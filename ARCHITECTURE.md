# Architecture

```
┌──────────┐      HTTPS/JSON       ┌──────────────────────┐        ┌───────────────────┐
│   User   │ ───────────────────▶  │  Frontend (Vercel)   │ ─────▶ │ Backend (Render)  │
│ browser  │ ◀───────────────────  │  React 18 + Vite     │ ◀───── │ FastAPI + Gunicorn│
└──────────┘                       │  react-router        │        └────────┬──────────┘
                                   │  framer-motion       │                 │
                                   │  axios (JWT bearer)  │     ┌───────────┼─────────────┐
                                   └──────────────────────┘     ▼           ▼             ▼
                                                        ┌──────────┐ ┌────────────┐ ┌─────────────┐
                                                        │ Supabase │ │  Groq AI   │ │ picsum /    │
                                                        │ Postgres │ │ (or HF /   │ │ Unsplash-   │
                                                        │ + RLS    │ │  Ollama)   │ │ style images│
                                                        └──────────┘ └────────────┘ └─────────────┘
```

## Request flow — "Generate Itinerary"

1. **CreateTrip.jsx** collects inputs in 3 steps and validates client-side.
2. `tripsAPI.create()` → `POST /api/trips` — **Pydantic** (`CreateTripRequest`) validates again: enum values, date order, ≤30 days, group size, budget ≥ 0.
3. **TripService.create** writes the `trips` row via the repository, syncs `preferences`, logs `trip_created` to `history`.
4. Frontend navigates to `/trips/:id` and calls `POST /api/trips/{id}/generate`.
5. **ItineraryService.generate** → `build_itinerary_prompt()` (prompts/templates.py) injects destination, dates, style, interests, pace, budget, diet, mobility into the structured prompt and attaches a strict JSON contract.
6. **AIOrchestrator.generate_json** sends `SYSTEM_PROMPT` + user prompt to the configured **LLMProvider** (`GroqProvider` / `HuggingFaceProvider` / `OllamaProvider` / `TemplateProvider`), parses the JSON (strips fences, retries once on invalid JSON).
7. **`_normalize`** — the route & time optimisation pass: forces exactly N days with correct dates, fills missing slots, coerces costs, recomputes totals.
8. Result is upserted into `itineraries` (version bump on regenerate), trip status → `generated`, history → `itinerary_generated`.
9. **TripView.jsx** renders day cards (morning / afternoon / evening / dining / stay / transit / daily cap), with Regenerate (whole or single day + feedback + vibe switch), Export (Markdown), Share, and Bookmark → `saved_places`.

## Backend layers

| Layer | Module | Responsibility |
|---|---|---|
| Routes | `app/routes/*` | HTTP contracts, auth dependency, status codes |
| Schemas | `app/schemas/schemas.py` | Pydantic v2 request/response validation |
| Services | `app/services/trip.py`, `history.py`, `explore.py` | Business logic, orchestration |
| AI | `app/services/ai.py` | Provider abstraction (`LLMProvider` ABC) + JSON parsing |
| Prompts | `app/prompts/templates.py` | Prompt engineering layer |
| Data | `app/db/repository.py`, `database.py` | CRUD; Supabase (service role) or in-memory fallback |
| Utils | `app/utils/auth.py`, `errors.py` | PBKDF2 hashing, JWT, typed exceptions → HTTP |
| Config | `app/config.py` | `pydantic-settings`, `.env`, CORS origins |

## Data model (Supabase)

```
users 1───∞ trips 1───1 itineraries
  │            │
  │            └───∞ saved_places (trip_id nullable)
  ├───1 preferences
  └───∞ history (trip_id nullable)
```
All FKs cascade on user delete; itineraries cascade on trip delete; RLS enabled with service-role-only policies (the backend is the only writer).

## Security
- Passwords: PBKDF2-SHA256, 200k iterations, per-user salt.
- JWT HS256 signed with `SECRET_KEY`; bearer header; 401 auto-logout in the axios interceptor.
- Supabase `service_role` key lives only on the server; the browser never talks to Supabase directly.
- CORS restricted to `FRONTEND_URL`, localhost, and `*.vercel.app`.

## Frontend structure
- `components/Layout.jsx` — protected shell (Sidebar + Outlet).
- `services/api.js` — single axios instance; `VITE_API_URL` switches local ↔ production.
- State: React hooks only (useState/useEffect); session in `localStorage`.
- Styling: hand-written CSS design tokens (`index.css`), Outfit + Inter fonts, framer-motion for transitions.

## Extensibility
- New AI provider → subclass `LLMProvider`, register in `get_ai_orchestrator()`.
- New export format → add a method next to `export_markdown` and a route in `routes/trips.py`.
- Real-time collaboration → Supabase Realtime on `itineraries`.
