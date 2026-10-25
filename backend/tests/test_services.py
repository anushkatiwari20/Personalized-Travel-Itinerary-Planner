"""Service-level functional tests (Activity 7.1 / 7.2).

Runs WITHOUT Supabase or an AI key (uses the in-memory repository and the
offline template provider), so it works anywhere:

    cd backend
    python -m pytest tests/ -q        # with pytest
    python tests/test_services.py     # plain python
"""

import asyncio
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("AI_PROVIDER", "template")

from app.db.repository import MemoryRepository  # noqa: E402
from app.schemas.schemas import CreateTripRequest, RegenerateRequest  # noqa: E402
from app.services.ai import AIOrchestrator, TemplateProvider, parse_json_response  # noqa: E402
from app.services.history import HistoryService  # noqa: E402
from app.services.trip import ItineraryService, TripService  # noqa: E402
from app.utils.auth import create_access_token, decode_token, hash_password, verify_password  # noqa: E402


def _services():
    repo = MemoryRepository()
    hist = HistoryService(repo)
    return repo, hist, TripService(repo, hist), ItineraryService(repo, hist, AIOrchestrator(TemplateProvider()))


def test_password_and_jwt():
    h = hash_password("secret123")
    assert verify_password("secret123", h) and not verify_password("wrong", h)
    tok = create_access_token("user-1", {"email": "a@b.com"})
    assert decode_token(tok)["sub"] == "user-1"


def test_parse_json_response():
    assert parse_json_response('```json\n{"a": 1}\n```') == {"a": 1}
    assert parse_json_response('Here you go: {"a": [1,2]} thanks') == {"a": [1, 2]}


def test_trip_lifecycle_and_db_updates():
    repo, hist, trips, itins = _services()
    user = repo.create_user("test@example.com", "Test User", hash_password("password1"))
    uid = user["id"]

    start = date.today() + timedelta(days=10)
    req = CreateTripRequest(
        destination="Hyderabad",
        start_date=start,
        end_date=start + timedelta(days=2),
        travel_style="adventure",
        interests=["food", "history"],
        group_size=2,
        pace="moderate",
        budget_per_day=2000,
    )
    trip = trips.create(uid, req)
    assert trip["duration_days"] == 3 and trip["status"] == "draft"
    assert repo.get_preferences(uid)["travel_style"] == "adventure"  # preferences synced

    itin = asyncio.run(itins.generate(uid, trip["id"]))
    assert len(itin["itinerary_days"]) == 3
    assert itin["itinerary_days"][0]["date"] == start.isoformat()
    assert itin["total_estimated_cost"] > 0
    assert repo.get_trip(trip["id"], uid)["status"] == "generated"  # DB updated

    # regenerate only day 2 with feedback
    day2_before = itin["itinerary_days"][1]["title"]
    itin2 = asyncio.run(itins.regenerate(uid, trip["id"], RegenerateRequest(day=2, feedback="more food", travel_style="relaxed")))
    assert itin2["version"] == 2
    assert itin2["itinerary_days"][1]["title"] != day2_before
    assert itin2["itinerary_days"][0]["title"] == itin["itinerary_days"][0]["title"]  # day 1 untouched

    md = itins.export_markdown(uid, trip["id"])
    assert md.startswith("# Hyderabad") and "## Day 3" in md

    repo.add_saved_place({"user_id": uid, "trip_id": trip["id"], "name": "Charminar", "category": "attraction"})
    assert len(repo.list_saved_places(uid)) == 1

    actions = [h["action"] for h in hist.list(uid)]
    assert {"trip_created", "itinerary_generated", "itinerary_regenerated", "exported"} <= set(actions)

    trips.delete(uid, trip["id"])
    assert trips.list(uid) == [] and repo.get_itinerary(trip["id"], uid) is None  # cascade


if __name__ == "__main__":
    test_password_and_jwt()
    test_parse_json_response()
    test_trip_lifecycle_and_db_updates()
    print("ALL SERVICE TESTS PASSED")
