# API Reference

Base URL: `http://localhost:8000/api` (local) · `https://<render-service>.onrender.com/api` (prod)
Interactive docs: `/docs` (Swagger) · `/redoc`

All endpoints except `/auth/*`, `/explore/*` and `/health` require `Authorization: Bearer <access_token>`.
Errors return `{"detail": "message"}` with an appropriate HTTP status (401, 404, 409, 422, 502).

## Health
| Method | Path | Response |
|---|---|---|
| GET | `/health` (also `/api/health`) | `{status, environment, ai_provider, database}` |

## Auth
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/auth/register` | `{email, password(≥8), name(≥2)}` | `TokenResponse` (201) |
| POST | `/auth/login` | `{email, password}` | `TokenResponse` |
| GET | `/auth/me` | — | `{id, email, name, created_at}` |

`TokenResponse = {access_token, token_type:"bearer", user_id, name, email}` — tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES`.

## Trips
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/trips` | `CreateTripRequest` | `TripResponse` (201) |
| GET | `/trips` | — | `TripResponse[]` |
| GET | `/trips/{trip_id}` | — | `TripResponse` |
| PATCH | `/trips/{trip_id}` | partial `CreateTripRequest` + `status` | `TripResponse` |
| DELETE | `/trips/{trip_id}` | — | `{message}` (cascades itinerary) |

```jsonc
// CreateTripRequest
{
  "destination": "Hyderabad",
  "start_date": "2026-03-03",
  "end_date": "2026-03-07",
  "travel_style": "adventure",      // relaxed|adventure|luxury|budget|cultural|romantic|family
  "interests": ["food", "history"],
  "group_size": 1,
  "pace": "moderate",               // relaxed|moderate|fast
  "budget_per_day": 2000,           // INR per person
  "dietary_restrictions": ["Vegetarian"],
  "mobility_concerns": null,
  "notes": null
}
// TripResponse adds: id, user_id, status (draft|generated), duration_days, has_itinerary, created_at, updated_at
```

## Itineraries
| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/trips/{trip_id}/generate` | — | `ItineraryResponse` |
| POST | `/trips/{trip_id}/regenerate` | `{day?, feedback?, travel_style?, pace?}` | `ItineraryResponse` (version +1) |
| GET | `/trips/{trip_id}/itinerary` | — | `ItineraryResponse` |
| GET | `/trips/{trip_id}/export` | — | `text/markdown` download |

```jsonc
// ItineraryResponse
{
  "id": "...", "trip_id": "...", "user_id": "...",
  "destination": "Hyderabad", "duration_days": 5,
  "total_estimated_cost": 21000, "summary": "...",
  "ai_provider": "groq", "version": 1,
  "itinerary_days": [
    {
      "day": 1, "date": "2026-03-03", "title": "Old City heritage",
      "morning": "Charminar - Explore the historic monument and Laad Bazaar (Time: 120 minutes, Cost: ₹20)",
      "afternoon": "Salar Jung Museum - ... (Time: 180 minutes, Cost: ₹50)",
      "evening": "Chowmahalla Palace - ... (Time: 150 minutes, Cost: ₹80)",
      "dining": [{"name": "Cafe Bahar", "description": "Iconic biryani", "cost": "₹300-₹500 per meal"}],
      "stay": "Stay in the Old City area ...",
      "transit": "Use the Hyderabad Metro (₹20-₹60 per ride) ...",
      "daily_cost": 1250, "notes": "..."
    }
  ]
}
```

`regenerate` with `day: 2` replaces only day 2 and keeps the rest; `feedback` and `travel_style` steer the model ("vibe-based personalisation").

## Explore
| Method | Path | Query | Response |
|---|---|---|---|
| GET | `/explore/vibes` | — | `["all","beach","mountain",...]` |
| GET | `/explore/destinations` | `vibe?`, `q?` | `DestinationResponse[]` |
| GET | `/explore/destinations/{slug}` | — | `DestinationResponse` |

`DestinationResponse = {slug, name, country, vibes[], rating, reviews, budget_level(1-3), avg_budget_per_day, best_time, overview, highlights[], image_url}`

## Saved places
| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/saved-places` | — | `SavedPlaceResponse[]` |
| POST | `/saved-places` | `{name, description?, category?, time_slot?, destination?, trip_id?, image_url?}` | `SavedPlaceResponse` (201) |
| DELETE | `/saved-places/{id}` | — | `{message}` |

## Preferences
| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/preferences` | — | `{user_id, travel_style, interests, pace, budget_per_day, dietary_restrictions, currency}` |
| PUT | `/preferences` | any subset of the above | same |

Preferences are also auto-updated every time a trip is created.

## History
| Method | Path | Query | Response |
|---|---|---|---|
| GET | `/history` | `limit` (1–200) | `[{id, user_id, trip_id, action, details, created_at}]` |

Actions: `trip_created`, `trip_updated`, `trip_deleted`, `itinerary_generated`, `itinerary_regenerated`, `place_saved`, `exported`.

## curl smoke test
```bash
B=http://localhost:8000/api
TOKEN=$(curl -s -X POST $B/auth/register -H 'Content-Type: application/json' \
  -d '{"email":"demo@example.com","password":"password123","name":"Demo User"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
TRIP=$(curl -s -X POST $B/trips -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"destination":"Goa","start_date":"2026-12-20","end_date":"2026-12-22","travel_style":"relaxed","interests":["beaches","food"],"group_size":2,"pace":"relaxed","budget_per_day":3000}' | python -c "import sys,json;print(json.load(sys.stdin)['id'])")
curl -s -X POST $B/trips/$TRIP/generate -H "Authorization: Bearer $TOKEN" | python -m json.tool | head -40
```
