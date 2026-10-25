"""Prompt templates — the prompt-engineering layer between FastAPI and the LLM."""

from typing import List, Optional

SYSTEM_PROMPT = """You are an expert travel planner with deep local knowledge of destinations worldwide.
Your job is to produce realistic, well-paced, budget-aware day-by-day itineraries.

Rules you always follow:
- Group each day's activities geographically so the traveler never backtracks across the city.
- Respect the requested pace, travel style, budget, dietary restrictions and mobility needs.
- Give concrete place names, realistic durations and estimated costs in Indian Rupees (INR, ₹).
- Keep the plan practical with accurate timing and costs.
- Output ONLY valid JSON. No markdown fences, no commentary before or after the JSON.

You provide day-by-day itineraries with specific recommendations."""


JSON_FORMAT_INSTRUCTIONS = """Return a JSON object with EXACTLY this structure:
{
  "summary": "2-3 sentence overview of the whole trip",
  "total_estimated_cost": <number, INR, for the whole group for the whole trip>,
  "itinerary_days": [
    {
      "day": 1,
      "date": "YYYY-MM-DD",
      "title": "short theme for the day",
      "morning": "Place - what to do (Time: N minutes, Cost: ₹X)",
      "afternoon": "Place - what to do (Time: N minutes, Cost: ₹X)",
      "evening": "Place - what to do (Time: N minutes, Cost: ₹X)",
      "dining": [
        {"name": "Restaurant", "description": "cuisine / why", "cost": "₹X-₹Y per meal"}
      ],
      "stay": "Neighbourhood / hotel suggestion and why it is convenient",
      "transit": "How to get around today, with approximate fares",
      "daily_cost": <number, INR, per person>,
      "notes": "optional tips"
    }
  ]
}"""


def build_itinerary_prompt(
    destination: str,
    start_date: str,
    end_date: str,
    travel_style: str,
    interests: List[str],
    group_size: int,
    pace: str,
    budget_per_day: float,
    dietary_restrictions: Optional[List[str]] = None,
    mobility_concerns: Optional[str] = None,
    notes: Optional[str] = None,
    duration_days: int = 1,
) -> str:
    """Build the user prompt for itinerary generation."""

    dietary_info = (
        f"Dietary restrictions: {', '.join(dietary_restrictions)}" if dietary_restrictions else ""
    )
    mobility_info = f"Mobility considerations: {mobility_concerns}" if mobility_concerns else ""
    extra_notes = f"Additional traveler notes: {notes}" if notes else ""

    interests_str = ", ".join(interests) if interests else "general sightseeing"
    pace_description = {
        "relaxed": "one or two main activities per day with plenty of rest",
        "moderate": "two to three main activities per day with some downtime",
        "fast": "three to four main activities per day, constantly exploring",
    }.get(pace, "moderate pace")

    style_description = {
        "relaxed": "slow mornings, scenic spots, cafes, minimal rushing",
        "adventure": "outdoor activities, treks, water sports, adrenaline",
        "luxury": "premium stays, fine dining, private experiences",
        "budget": "hostels/guesthouses, street food, free attractions, public transport",
        "cultural": "heritage sites, museums, local traditions, markets",
        "romantic": "sunset spots, intimate dinners, scenic walks",
        "family": "kid-friendly attractions, short distances, early evenings",
    }.get(travel_style, travel_style)

    prompt = f"""Create a detailed {destination} itinerary from {start_date} to {end_date} ({duration_days} day(s)).

Traveler profile:
- Travel style: {travel_style} ({style_description})
- Interests: {interests_str}
- Group size: {group_size}
- Pace: {pace} ({pace_description})
- Budget: ₹{budget_per_day:.0f} per person per day
{dietary_info}
{mobility_info}
{extra_notes}

Requirements:
- Produce exactly {duration_days} day(s), numbered 1..{duration_days}, with the correct calendar date for each.
- Order the stops within each day to minimise travel time (cluster nearby locations).
- Keep every day's cost at or under the daily budget where possible and state the per-person daily cost.
- Include 2-3 dining options per day that respect the dietary restrictions.
- Suggest where to stay and how to get around.

{JSON_FORMAT_INSTRUCTIONS}"""

    # Collapse blank lines left by empty optional sections
    return "\n".join(line for line in prompt.splitlines() if line.strip() != "" or line == "")


def build_regenerate_prompt(
    base_prompt: str,
    previous_itinerary_json: str,
    feedback: Optional[str],
    day: Optional[int],
) -> str:
    """Build a prompt that refines a previous itinerary (vibe-based personalisation)."""

    scope = f"Regenerate ONLY day {day}; keep all other days identical." if day else "Regenerate the full itinerary."
    fb = f"Traveler feedback to incorporate: {feedback}" if feedback else "Make it noticeably different and better."
    return f"""{base_prompt}

Here is the previous itinerary (JSON):
{previous_itinerary_json}

{scope}
{fb}
Preserve the traveler's context and return the complete JSON object in the same structure."""


def build_recommendation_prompt(destination: str, interests: List[str], travel_style: str) -> str:
    """Prompt for destination/activity recommendations (Explore)."""
    return f"""Suggest 6 must-do experiences in {destination} for a traveler who likes {', '.join(interests) or 'sightseeing'} with a {travel_style} travel style.
Return ONLY a JSON array of objects: [{{"name": "...", "category": "attraction|dining|activity", "description": "...", "best_time": "morning|afternoon|evening", "cost": "₹X"}}]"""
