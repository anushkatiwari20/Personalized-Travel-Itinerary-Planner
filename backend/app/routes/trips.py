"""Trip and itinerary routes."""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.schemas.schemas import (
    CreateTripRequest,
    DayItinerary,
    ItineraryResponse,
    MessageResponse,
    RegenerateRequest,
    TripResponse,
    UpdateTripRequest,
)
from app.services.ai import get_ai_orchestrator
from app.services.history import get_history_service
from app.services.trip import get_itinerary_service, get_trip_service
from app.utils.auth import get_current_user_id
from app.utils.errors import AIGenerationError, NotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trips", tags=["Trips"])


# ---------- Trips (CRUD) ----------
@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(req: CreateTripRequest, user_id: str = Depends(get_current_user_id)):
    return get_trip_service().create(user_id, req)


@router.get("", response_model=list[TripResponse])
def list_trips(user_id: str = Depends(get_current_user_id)):
    return get_trip_service().list(user_id)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: str, user_id: str = Depends(get_current_user_id)):
    return get_trip_service().get(user_id, trip_id)


@router.patch("/{trip_id}", response_model=TripResponse)
def update_trip(trip_id: str, req: UpdateTripRequest, user_id: str = Depends(get_current_user_id)):
    return get_trip_service().update(user_id, trip_id, req)


@router.delete("/{trip_id}", response_model=MessageResponse)
def delete_trip(trip_id: str, user_id: str = Depends(get_current_user_id)):
    get_trip_service().delete(user_id, trip_id)
    return MessageResponse(message="Trip deleted")


# ---------- Itinerary generation ----------
@router.post("/{trip_id}/generate", response_model=ItineraryResponse)
async def generate_itinerary(trip_id: str, user_id: str = Depends(get_current_user_id)):
    """Generate a day-by-day itinerary for a trip using the configured AI provider."""
    return await get_itinerary_service().generate(user_id, trip_id)


@router.post("/{trip_id}/regenerate", response_model=ItineraryResponse)
async def regenerate_itinerary(trip_id: str, req: RegenerateRequest, user_id: str = Depends(get_current_user_id)):
    """Regenerate the whole plan or a single day, optionally with feedback / a new vibe."""
    return await get_itinerary_service().regenerate(user_id, trip_id, req)


@router.get("/{trip_id}/itinerary", response_model=ItineraryResponse)
def get_itinerary(trip_id: str, user_id: str = Depends(get_current_user_id)):
    return get_itinerary_service().get(user_id, trip_id)


# ---------- Share & export ----------
@router.get("/{trip_id}/export", response_class=PlainTextResponse)
def export_itinerary(trip_id: str, user_id: str = Depends(get_current_user_id)):
    """Export the itinerary as Markdown (downloadable)."""
    md = get_itinerary_service().export_markdown(user_id, trip_id)
    return PlainTextResponse(
        content=md,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="itinerary-{trip_id[:8]}.md"'},
    )
