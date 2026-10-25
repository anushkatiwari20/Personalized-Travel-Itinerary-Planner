"""Repository layer — all CRUD goes through here.

Two implementations:
  * SupabaseRepository  — production (uses the service-role client)
  * MemoryRepository    — automatic fallback when Supabase isn't configured,
                          so the API can be run and tested locally.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class BaseRepository:
    """Interface every repository implements."""

    # ---- users ----
    def create_user(self, email: str, name: str, password_hash: str) -> dict: ...
    def get_user_by_email(self, email: str) -> Optional[dict]: ...
    def get_user(self, user_id: str) -> Optional[dict]: ...

    # ---- trips ----
    def create_trip(self, data: dict) -> dict: ...
    def list_trips(self, user_id: str) -> list[dict]: ...
    def get_trip(self, trip_id: str, user_id: str) -> Optional[dict]: ...
    def update_trip(self, trip_id: str, user_id: str, data: dict) -> Optional[dict]: ...
    def delete_trip(self, trip_id: str, user_id: str) -> bool: ...

    # ---- itineraries ----
    def upsert_itinerary(self, data: dict) -> dict: ...
    def get_itinerary(self, trip_id: str, user_id: str) -> Optional[dict]: ...
    def itinerary_trip_ids(self, user_id: str) -> set[str]: ...

    # ---- preferences ----
    def get_preferences(self, user_id: str) -> Optional[dict]: ...
    def upsert_preferences(self, user_id: str, data: dict) -> dict: ...

    # ---- saved places ----
    def add_saved_place(self, data: dict) -> dict: ...
    def list_saved_places(self, user_id: str) -> list[dict]: ...
    def delete_saved_place(self, place_id: str, user_id: str) -> bool: ...

    # ---- history ----
    def add_history(self, user_id: str, action: str, trip_id: Optional[str], details: dict) -> dict: ...
    def list_history(self, user_id: str, limit: int = 50) -> list[dict]: ...


# ======================================================================
# Supabase implementation
# ======================================================================
class SupabaseRepository(BaseRepository):
    def __init__(self):
        from app.db.database import get_database

        self.db = get_database().get_service_client()

    @staticmethod
    def _one(res) -> Optional[dict]:
        return res.data[0] if res.data else None

    # users
    def create_user(self, email, name, password_hash):
        res = self.db.table("users").insert({"email": email, "name": name, "password_hash": password_hash}).execute()
        return self._one(res)

    def get_user_by_email(self, email):
        return self._one(self.db.table("users").select("*").eq("email", email).limit(1).execute())

    def get_user(self, user_id):
        return self._one(self.db.table("users").select("*").eq("id", user_id).limit(1).execute())

    # trips
    def create_trip(self, data):
        return self._one(self.db.table("trips").insert(data).execute())

    def list_trips(self, user_id):
        return self.db.table("trips").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data or []

    def get_trip(self, trip_id, user_id):
        return self._one(self.db.table("trips").select("*").eq("id", trip_id).eq("user_id", user_id).limit(1).execute())

    def update_trip(self, trip_id, user_id, data):
        return self._one(self.db.table("trips").update(data).eq("id", trip_id).eq("user_id", user_id).execute())

    def delete_trip(self, trip_id, user_id):
        res = self.db.table("trips").delete().eq("id", trip_id).eq("user_id", user_id).execute()
        return bool(res.data)

    # itineraries
    def upsert_itinerary(self, data):
        existing = self.get_itinerary(data["trip_id"], data["user_id"])
        if existing:
            data["version"] = int(existing.get("version", 1)) + 1
            return self._one(self.db.table("itineraries").update(data).eq("id", existing["id"]).execute())
        return self._one(self.db.table("itineraries").insert(data).execute())

    def get_itinerary(self, trip_id, user_id):
        return self._one(
            self.db.table("itineraries").select("*").eq("trip_id", trip_id).eq("user_id", user_id).limit(1).execute()
        )

    def itinerary_trip_ids(self, user_id):
        rows = self.db.table("itineraries").select("trip_id").eq("user_id", user_id).execute().data or []
        return {r["trip_id"] for r in rows}

    # preferences
    def get_preferences(self, user_id):
        return self._one(self.db.table("preferences").select("*").eq("user_id", user_id).limit(1).execute())

    def upsert_preferences(self, user_id, data):
        data = {**data, "user_id": user_id}
        return self._one(self.db.table("preferences").upsert(data, on_conflict="user_id").execute())

    # saved places
    def add_saved_place(self, data):
        return self._one(self.db.table("saved_places").insert(data).execute())

    def list_saved_places(self, user_id):
        return self.db.table("saved_places").select("*").eq("user_id", user_id).order("created_at", desc=True).execute().data or []

    def delete_saved_place(self, place_id, user_id):
        res = self.db.table("saved_places").delete().eq("id", place_id).eq("user_id", user_id).execute()
        return bool(res.data)

    # history
    def add_history(self, user_id, action, trip_id, details):
        return self._one(
            self.db.table("history").insert({"user_id": user_id, "action": action, "trip_id": trip_id, "details": details}).execute()
        )

    def list_history(self, user_id, limit=50):
        return (
            self.db.table("history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute().data
            or []
        )


# ======================================================================
# In-memory implementation (local dev / tests)
# ======================================================================
class MemoryRepository(BaseRepository):
    def __init__(self):
        self.users: dict[str, dict] = {}
        self.trips: dict[str, dict] = {}
        self.itineraries: dict[str, dict] = {}
        self.preferences: dict[str, dict] = {}
        self.saved_places: dict[str, dict] = {}
        self.history: list[dict] = []
        logger.warning("Using IN-MEMORY repository — data will be lost on restart. Configure Supabase for persistence.")

    @staticmethod
    def _row(data: dict) -> dict:
        return {"id": str(uuid.uuid4()), "created_at": _now(), "updated_at": _now(), **data}

    # users
    def create_user(self, email, name, password_hash):
        row = self._row({"email": email, "name": name, "password_hash": password_hash})
        self.users[row["id"]] = row
        return row

    def get_user_by_email(self, email):
        return next((u for u in self.users.values() if u["email"] == email), None)

    def get_user(self, user_id):
        return self.users.get(user_id)

    # trips
    def create_trip(self, data):
        row = self._row(data)
        self.trips[row["id"]] = row
        return row

    def list_trips(self, user_id):
        rows = [t for t in self.trips.values() if t["user_id"] == user_id]
        return sorted(rows, key=lambda r: r["created_at"], reverse=True)

    def get_trip(self, trip_id, user_id):
        t = self.trips.get(trip_id)
        return t if t and t["user_id"] == user_id else None

    def update_trip(self, trip_id, user_id, data):
        t = self.get_trip(trip_id, user_id)
        if not t:
            return None
        t.update(data)
        t["updated_at"] = _now()
        return t

    def delete_trip(self, trip_id, user_id):
        if self.get_trip(trip_id, user_id):
            del self.trips[trip_id]
            self.itineraries = {k: v for k, v in self.itineraries.items() if v["trip_id"] != trip_id}
            return True
        return False

    # itineraries
    def upsert_itinerary(self, data):
        existing = self.get_itinerary(data["trip_id"], data["user_id"])
        if existing:
            existing.update(data)
            existing["version"] = int(existing.get("version", 1)) + 1
            existing["updated_at"] = _now()
            return existing
        row = self._row({**data, "version": 1})
        self.itineraries[row["id"]] = row
        return row

    def get_itinerary(self, trip_id, user_id):
        return next((i for i in self.itineraries.values() if i["trip_id"] == trip_id and i["user_id"] == user_id), None)

    def itinerary_trip_ids(self, user_id):
        return {i["trip_id"] for i in self.itineraries.values() if i["user_id"] == user_id}

    # preferences
    def get_preferences(self, user_id):
        return self.preferences.get(user_id)

    def upsert_preferences(self, user_id, data):
        row = self.preferences.get(user_id) or self._row({"user_id": user_id})
        row.update(data)
        self.preferences[user_id] = row
        return row

    # saved places
    def add_saved_place(self, data):
        row = self._row(data)
        self.saved_places[row["id"]] = row
        return row

    def list_saved_places(self, user_id):
        return sorted([p for p in self.saved_places.values() if p["user_id"] == user_id], key=lambda r: r["created_at"], reverse=True)

    def delete_saved_place(self, place_id, user_id):
        p = self.saved_places.get(place_id)
        if p and p["user_id"] == user_id:
            del self.saved_places[place_id]
            return True
        return False

    # history
    def add_history(self, user_id, action, trip_id, details):
        row = self._row({"user_id": user_id, "action": action, "trip_id": trip_id, "details": details})
        self.history.append(row)
        return row

    def list_history(self, user_id, limit=50):
        rows = [h for h in self.history if h["user_id"] == user_id]
        return sorted(rows, key=lambda r: r["created_at"], reverse=True)[:limit]


_repo: Optional[BaseRepository] = None


def get_repository() -> BaseRepository:
    """Return the configured repository (Supabase if configured, else in-memory)."""
    global _repo
    if _repo is None:
        if get_settings().supabase_configured:
            try:
                _repo = SupabaseRepository()
                logger.info("Repository: Supabase")
            except Exception as e:  # pragma: no cover
                logger.error(f"Supabase init failed ({e}); falling back to in-memory repository")
                _repo = MemoryRepository()
        else:
            _repo = MemoryRepository()
    return _repo
