"""Explore, saved places, preferences and history routes."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.repository import get_repository
from app.schemas.schemas import (
    DestinationResponse,
    HistoryResponse,
    MessageResponse,
    PreferencesRequest,
    PreferencesResponse,
    SavedPlaceResponse,
    SavePlaceRequest,
)
from app.services import explore as explore_service
from app.services.history import get_history_service
from app.utils.auth import get_current_user_id

# ---------- Explore ----------
explore_router = APIRouter(prefix="/explore", tags=["Explore"])


@explore_router.get("/vibes", response_model=list[str])
def vibes():
    return explore_service.VIBES


@explore_router.get("/destinations", response_model=list[DestinationResponse])
def destinations(vibe: Optional[str] = Query(default=None), q: Optional[str] = Query(default=None)):
    return explore_service.list_destinations(vibe, q)


@explore_router.get("/destinations/{slug}", response_model=DestinationResponse)
def destination(slug: str):
    d = explore_service.get_destination(slug)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination not found")
    return d


# ---------- Saved places ----------
saved_router = APIRouter(prefix="/saved-places", tags=["Saved Places"])


@saved_router.get("", response_model=list[SavedPlaceResponse])
def list_saved(user_id: str = Depends(get_current_user_id)):
    return get_repository().list_saved_places(user_id)


@saved_router.post("", response_model=SavedPlaceResponse, status_code=status.HTTP_201_CREATED)
def save_place(req: SavePlaceRequest, user_id: str = Depends(get_current_user_id)):
    data = {**req.model_dump(), "user_id": user_id}
    row = get_repository().add_saved_place(data)
    get_history_service().record(user_id, "place_saved", req.trip_id, {"name": req.name})
    return row


@saved_router.delete("/{place_id}", response_model=MessageResponse)
def delete_saved(place_id: str, user_id: str = Depends(get_current_user_id)):
    if not get_repository().delete_saved_place(place_id, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved place not found")
    return MessageResponse(message="Removed")


# ---------- Preferences ----------
prefs_router = APIRouter(prefix="/preferences", tags=["Preferences"])


@prefs_router.get("", response_model=PreferencesResponse)
def get_prefs(user_id: str = Depends(get_current_user_id)):
    row = get_repository().get_preferences(user_id) or {}
    return PreferencesResponse(user_id=user_id, **{k: v for k, v in row.items() if k in PreferencesResponse.model_fields and k != "user_id" and v is not None})


@prefs_router.put("", response_model=PreferencesResponse)
def set_prefs(req: PreferencesRequest, user_id: str = Depends(get_current_user_id)):
    data = {k: v for k, v in req.model_dump().items() if v is not None}
    row = get_repository().upsert_preferences(user_id, data) or {}
    return PreferencesResponse(user_id=user_id, **{k: v for k, v in row.items() if k in PreferencesResponse.model_fields and k != "user_id" and v is not None})


# ---------- History ----------
history_router = APIRouter(prefix="/history", tags=["History"])


@history_router.get("", response_model=list[HistoryResponse])
def list_history(limit: int = Query(default=50, ge=1, le=200), user_id: str = Depends(get_current_user_id)):
    rows = get_history_service().list(user_id, limit)
    for r in rows:
        r["details"] = r.get("details") or {}
    return rows
