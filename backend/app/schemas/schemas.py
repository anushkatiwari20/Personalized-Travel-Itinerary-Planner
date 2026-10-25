"""Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

# ============ Authentication Schemas ============


class UserRegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=2)


class UserLoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None


class UserResponse(BaseModel):
    """User response."""

    id: str
    email: str
    name: str
    created_at: Optional[datetime] = None


# ============ Trip Schemas ============

TRAVEL_STYLES = {"relaxed", "adventure", "luxury", "budget", "cultural", "romantic", "family"}
PACES = {"relaxed", "moderate", "fast"}


class CreateTripRequest(BaseModel):
    """Trip creation request (output of the 3-step trip builder)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    destination: str = Field(..., min_length=2, max_length=120)
    start_date: date
    end_date: date
    travel_style: str = "cultural"
    interests: List[str] = Field(default_factory=list)
    group_size: int = Field(default=1, ge=1, le=50)
    pace: str = "moderate"
    budget_per_day: float = Field(default=2000, ge=0)
    dietary_restrictions: List[str] = Field(default_factory=list)
    mobility_concerns: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("travel_style")
    @classmethod
    def _style(cls, v: str) -> str:
        v = v.lower()
        if v not in TRAVEL_STYLES:
            raise ValueError(f"travel_style must be one of {sorted(TRAVEL_STYLES)}")
        return v

    @field_validator("pace")
    @classmethod
    def _pace(cls, v: str) -> str:
        v = v.lower()
        if v not in PACES:
            raise ValueError(f"pace must be one of {sorted(PACES)}")
        return v

    @model_validator(mode="after")
    def _dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if (self.end_date - self.start_date).days > 30:
            raise ValueError("Trips longer than 30 days are not supported")
        return self


class UpdateTripRequest(BaseModel):
    """Partial trip update."""

    destination: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    travel_style: Optional[str] = None
    interests: Optional[List[str]] = None
    group_size: Optional[int] = None
    pace: Optional[str] = None
    budget_per_day: Optional[float] = None
    dietary_restrictions: Optional[List[str]] = None
    mobility_concerns: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class TripResponse(BaseModel):
    """Trip response."""

    id: str
    user_id: str
    destination: str
    start_date: date
    end_date: date
    travel_style: str
    interests: List[str] = []
    group_size: int = 1
    pace: str = "moderate"
    budget_per_day: float = 0
    dietary_restrictions: List[str] = []
    mobility_concerns: Optional[str] = None
    notes: Optional[str] = None
    status: str = "draft"
    duration_days: int = 1
    has_itinerary: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ============ Itinerary Schemas ============


class DiningOption(BaseModel):
    name: str
    description: Optional[str] = None
    cost: Optional[str] = None


class DayItinerary(BaseModel):
    """A single day in the itinerary."""

    day: int
    date: Optional[str] = None
    title: Optional[str] = None
    morning: str = ""
    afternoon: str = ""
    evening: str = ""
    dining: List[Any] = Field(default_factory=list)
    stay: Optional[str] = None
    transit: Optional[str] = None
    daily_cost: float = 0
    notes: Optional[str] = None


class ItineraryResponse(BaseModel):
    """Full itinerary response."""

    id: str
    trip_id: str
    user_id: str
    destination: str
    duration_days: int
    total_estimated_cost: float = 0
    itinerary_days: List[DayItinerary] = Field(default_factory=list)
    summary: Optional[str] = None
    ai_provider: Optional[str] = None
    version: int = 1
    created_at: Optional[datetime] = None


class RegenerateRequest(BaseModel):
    """Regenerate request — optionally only one day, with feedback."""

    day: Optional[int] = Field(default=None, ge=1)
    feedback: Optional[str] = None
    travel_style: Optional[str] = None
    pace: Optional[str] = None


# ============ Preferences ============


class PreferencesRequest(BaseModel):
    travel_style: Optional[str] = None
    interests: Optional[List[str]] = None
    pace: Optional[str] = None
    budget_per_day: Optional[float] = None
    dietary_restrictions: Optional[List[str]] = None
    currency: Optional[str] = None


class PreferencesResponse(BaseModel):
    user_id: str
    travel_style: str = "cultural"
    interests: List[str] = []
    pace: str = "moderate"
    budget_per_day: float = 2000
    dietary_restrictions: List[str] = []
    currency: str = "INR"


# ============ Saved Places ============


class SavePlaceRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    category: Optional[str] = "attraction"
    time_slot: Optional[str] = None
    destination: Optional[str] = None
    trip_id: Optional[str] = None
    image_url: Optional[str] = None


class SavedPlaceResponse(BaseModel):
    id: str
    user_id: str
    trip_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    time_slot: Optional[str] = None
    destination: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None


# ============ History ============


class HistoryResponse(BaseModel):
    id: str
    user_id: str
    trip_id: Optional[str] = None
    action: str
    details: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None


# ============ Explore ============


class DestinationResponse(BaseModel):
    slug: str
    name: str
    country: str
    vibes: List[str]
    rating: float
    reviews: int
    budget_level: int  # 1-3
    avg_budget_per_day: float
    best_time: str
    overview: str
    highlights: List[str]
    image_url: str


# ============ Generic ============


class MessageResponse(BaseModel):
    message: str
    success: bool = True
