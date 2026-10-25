"""Trip & itinerary services (business logic)."""

import json
import logging
from datetime import date
from typing import Any, Optional

from app.db.repository import BaseRepository, get_repository
from app.prompts.templates import SYSTEM_PROMPT, build_itinerary_prompt, build_regenerate_prompt
from app.schemas.schemas import CreateTripRequest, RegenerateRequest, UpdateTripRequest
from app.services.ai import AIOrchestrator, get_ai_orchestrator
from app.services.history import HistoryService, get_history_service
from app.utils.errors import AIGenerationError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)


def _duration(start: Any, end: Any) -> int:
    s = date.fromisoformat(str(start)) if not isinstance(start, date) else start
    e = date.fromisoformat(str(end)) if not isinstance(end, date) else end
    return (e - s).days + 1


def _serialize_trip(row: dict, has_itinerary: bool = False) -> dict:
    row = dict(row)
    row["duration_days"] = _duration(row["start_date"], row["end_date"])
    row["has_itinerary"] = has_itinerary
    row["budget_per_day"] = float(row.get("budget_per_day") or 0)
    row["interests"] = row.get("interests") or []
    row["dietary_restrictions"] = row.get("dietary_restrictions") or []
    return row


# ======================================================================
class TripService:
    def __init__(self, repo: BaseRepository, history: HistoryService):
        self.repo = repo
        self.history = history

    def create(self, user_id: str, req: CreateTripRequest) -> dict:
        data = req.model_dump()
        data["start_date"] = req.start_date.isoformat()
        data["end_date"] = req.end_date.isoformat()
        data["user_id"] = user_id
        data["status"] = "draft"
        row = self.repo.create_trip(data)
        if not row:
            raise ValidationError("Could not create trip")
        self.history.record(user_id, "trip_created", row["id"], {"destination": row["destination"]})
        # keep user preferences in sync with the latest trip builder inputs
        self.repo.upsert_preferences(
            user_id,
            {
                "travel_style": req.travel_style,
                "interests": req.interests,
                "pace": req.pace,
                "budget_per_day": req.budget_per_day,
                "dietary_restrictions": req.dietary_restrictions,
            },
        )
        return _serialize_trip(row)

    def list(self, user_id: str) -> list[dict]:
        with_itin = self.repo.itinerary_trip_ids(user_id)
        return [_serialize_trip(t, t["id"] in with_itin) for t in self.repo.list_trips(user_id)]

    def get(self, user_id: str, trip_id: str) -> dict:
        row = self.repo.get_trip(trip_id, user_id)
        if not row:
            raise NotFoundError("Trip not found")
        return _serialize_trip(row, self.repo.get_itinerary(trip_id, user_id) is not None)

    def update(self, user_id: str, trip_id: str, req: UpdateTripRequest) -> dict:
        data = {k: v for k, v in req.model_dump().items() if v is not None}
        for k in ("start_date", "end_date"):
            if k in data:
                data[k] = data[k].isoformat()
        row = self.repo.update_trip(trip_id, user_id, data)
        if not row:
            raise NotFoundError("Trip not found")
        self.history.record(user_id, "trip_updated", trip_id, {"fields": list(data.keys())})
        return _serialize_trip(row, self.repo.get_itinerary(trip_id, user_id) is not None)

    def delete(self, user_id: str, trip_id: str) -> None:
        trip = self.repo.get_trip(trip_id, user_id)
        if not trip:
            raise NotFoundError("Trip not found")
        self.repo.delete_trip(trip_id, user_id)
        self.history.record(user_id, "trip_deleted", None, {"destination": trip["destination"]})


# ======================================================================
class ItineraryService:
    def __init__(self, repo: BaseRepository, history: HistoryService, ai: AIOrchestrator):
        self.repo = repo
        self.history = history
        self.ai = ai

    def _prompt_for(self, trip: dict, overrides: Optional[dict] = None) -> str:
        o = overrides or {}
        return build_itinerary_prompt(
            destination=trip["destination"],
            start_date=str(trip["start_date"]),
            end_date=str(trip["end_date"]),
            travel_style=o.get("travel_style") or trip["travel_style"],
            interests=trip.get("interests") or [],
            group_size=int(trip.get("group_size") or 1),
            pace=o.get("pace") or trip["pace"],
            budget_per_day=float(trip.get("budget_per_day") or 0),
            dietary_restrictions=trip.get("dietary_restrictions") or [],
            mobility_concerns=trip.get("mobility_concerns"),
            notes=trip.get("notes"),
            duration_days=_duration(trip["start_date"], trip["end_date"]),
        )

    @staticmethod
    def _normalize(result: dict, trip: dict) -> dict:
        """Route & time optimisation / sanity pass on the model output."""
        days = result.get("itinerary_days") or []
        duration = _duration(trip["start_date"], trip["end_date"])
        start = date.fromisoformat(str(trip["start_date"]))
        normalized = []
        for i in range(duration):
            d = days[i] if i < len(days) else {}
            day_date = date.fromordinal(start.toordinal() + i).isoformat()
            dining = d.get("dining") or []
            if isinstance(dining, str):
                dining = [{"name": dining}]
            normalized.append(
                {
                    "day": i + 1,
                    "date": day_date,
                    "title": d.get("title") or f"Day {i + 1}",
                    "morning": str(d.get("morning") or "Free morning — explore at your own pace."),
                    "afternoon": str(d.get("afternoon") or "Free afternoon."),
                    "evening": str(d.get("evening") or "Free evening."),
                    "dining": dining,
                    "stay": d.get("stay"),
                    "transit": d.get("transit"),
                    "daily_cost": float(d.get("daily_cost") or 0),
                    "notes": d.get("notes"),
                }
            )
        total = result.get("total_estimated_cost")
        if not total:
            total = sum(x["daily_cost"] for x in normalized) * int(trip.get("group_size") or 1)
        return {
            "summary": result.get("summary"),
            "total_estimated_cost": float(total),
            "itinerary_days": normalized,
        }

    async def generate(self, user_id: str, trip_id: str) -> dict:
        trip = self.repo.get_trip(trip_id, user_id)
        if not trip:
            raise NotFoundError("Trip not found")
        prompt = self._prompt_for(trip)
        result = await self.ai.generate_json(SYSTEM_PROMPT, prompt)
        return self._save(user_id, trip, result, "itinerary_generated")

    async def regenerate(self, user_id: str, trip_id: str, req: RegenerateRequest) -> dict:
        trip = self.repo.get_trip(trip_id, user_id)
        if not trip:
            raise NotFoundError("Trip not found")
        previous = self.repo.get_itinerary(trip_id, user_id)
        overrides = {"travel_style": req.travel_style, "pace": req.pace}
        base_prompt = self._prompt_for(trip, overrides)
        if previous:
            prev_json = json.dumps(
                {"summary": previous.get("summary"), "itinerary_days": previous.get("itinerary_days")}
            )[:12000]
            prompt = build_regenerate_prompt(base_prompt, prev_json, req.feedback, req.day)
        else:
            prompt = base_prompt
        result = await self.ai.generate_json(SYSTEM_PROMPT, prompt)
        normalized = self._normalize(result, trip)
        # If only one day was requested, splice it into the previous plan.
        if previous and req.day:
            prev_days = previous.get("itinerary_days") or []
            idx = req.day - 1
            if 0 <= idx < len(prev_days) and idx < len(normalized["itinerary_days"]):
                prev_days[idx] = normalized["itinerary_days"][idx]
                normalized["itinerary_days"] = prev_days
                normalized["total_estimated_cost"] = sum(float(d.get("daily_cost") or 0) for d in prev_days) * int(
                    trip.get("group_size") or 1
                )
        return self._save(
            user_id, trip, normalized, "itinerary_regenerated", {"day": req.day, "feedback": req.feedback}, already_normalized=True
        )

    def _save(self, user_id, trip, result, action, extra=None, already_normalized=False) -> dict:
        normalized = result if already_normalized else self._normalize(result, trip)
        row = self.repo.upsert_itinerary(
            {
                "trip_id": trip["id"],
                "user_id": user_id,
                "destination": trip["destination"],
                "duration_days": len(normalized["itinerary_days"]),
                "total_estimated_cost": normalized["total_estimated_cost"],
                "itinerary_days": normalized["itinerary_days"],
                "summary": normalized.get("summary"),
                "ai_provider": self.ai.provider_name,
            }
        )
        self.repo.update_trip(trip["id"], user_id, {"status": "generated"})
        self.history.record(user_id, action, trip["id"], {"destination": trip["destination"], **(extra or {})})
        return self._serialize(row)

    def get(self, user_id: str, trip_id: str) -> dict:
        row = self.repo.get_itinerary(trip_id, user_id)
        if not row:
            raise NotFoundError("No itinerary generated for this trip yet")
        return self._serialize(row)

    @staticmethod
    def _serialize(row: dict) -> dict:
        row = dict(row)
        row["total_estimated_cost"] = float(row.get("total_estimated_cost") or 0)
        row["itinerary_days"] = row.get("itinerary_days") or []
        return row

    def export_markdown(self, user_id: str, trip_id: str) -> str:
        trip = self.repo.get_trip(trip_id, user_id)
        itin = self.repo.get_itinerary(trip_id, user_id)
        if not trip or not itin:
            raise NotFoundError("Itinerary not found")
        lines = [
            f"# {trip['destination']} — Travel Itinerary",
            "",
            f"**Dates:** {trip['start_date']} → {trip['end_date']}  ",
            f"**Travellers:** {trip.get('group_size', 1)}  ",
            f"**Style / pace:** {trip['travel_style']} / {trip['pace']}  ",
            f"**Budget:** ₹{float(trip.get('budget_per_day') or 0):.0f} per person per day  ",
            f"**Estimated total:** ₹{float(itin.get('total_estimated_cost') or 0):,.0f}",
            "",
        ]
        if itin.get("summary"):
            lines += [itin["summary"], ""]
        for d in itin.get("itinerary_days") or []:
            lines += [f"## Day {d['day']} — {d.get('date', '')} {('· ' + d['title']) if d.get('title') else ''}", ""]
            lines += [f"- **Morning:** {d.get('morning', '')}", f"- **Afternoon:** {d.get('afternoon', '')}", f"- **Evening:** {d.get('evening', '')}"]
            if d.get("dining"):
                lines.append("- **Dining:**")
                for m in d["dining"]:
                    if isinstance(m, dict):
                        lines.append(f"  - {m.get('name', '')} — {m.get('description', '')} ({m.get('cost', '')})")
                    else:
                        lines.append(f"  - {m}")
            if d.get("stay"):
                lines.append(f"- **Stay:** {d['stay']}")
            if d.get("transit"):
                lines.append(f"- **Transit:** {d['transit']}")
            lines += [f"- **Daily cost (per person):** ₹{float(d.get('daily_cost') or 0):,.0f}", ""]
        self.history.record(user_id, "exported", trip_id, {"format": "markdown"})
        return "\n".join(lines)


# ---------- factories ----------
def get_trip_service() -> TripService:
    return TripService(get_repository(), get_history_service())


def get_itinerary_service() -> ItineraryService:
    return ItineraryService(get_repository(), get_history_service(), get_ai_orchestrator())
