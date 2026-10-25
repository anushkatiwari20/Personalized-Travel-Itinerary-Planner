# Personalized Travel Itinerary Planner

A full-stack, AI-powered web application that generates customized day-by-day travel itineraries based on user preferences, budget and travel style. Built with a **React** frontend, **FastAPI** backend and **Supabase** (Postgres) database, with **Groq** (default), Hugging Face or local Ollama as the generative-AI provider.

> Program: Generative AI with Google Cloud · Project: Personalized Travel Itinerary Planner

## Features

| Epic | Feature | Where |
|---|---|---|
| 3.1 | 3-step trip builder (Basics → Preferences → Logistics) with validation | `frontend/src/pages/CreateTrip.jsx`, `backend/app/schemas/schemas.py` |
| 3.2 | Prompt-structuring layer (role, constraints, pace, diet, mobility → JSON contract) | `backend/app/prompts/templates.py` |
| 3.3 | Destination recommendation engine + Explore page with vibe filters | `backend/app/services/explore.py`, `frontend/src/pages/Explore.jsx` |
| 4.1 | Daily itinerary builder (morning / afternoon / evening / dining / stay / transit) | `backend/app/services/ai.py`, `backend/app/services/trip.py` |
| 4.2 | Route & time optimisation (geographic clustering in prompt + normalisation pass) | `templates.py`, `trip.py::_normalize` |
| 4.3 | Vibe-based personalisation — regenerate whole plan or a single day with feedback / new vibe | `TripView.jsx`, `POST /trips/{id}/regenerate` |
| 5.1 | Trip save & management (CRUD, dashboard, history) | `routes/trips.py`, `Dashboard.jsx`, `TripHistory.jsx` |
| 5.2 | Share & export (Markdown download, Web Share / clipboard) | `GET /trips/{id}/export`, `TripView.jsx` |
| 5.3/5.4 | Env-driven configuration, production settings, tests | `config.py`, `.env.example`, `tests/` |
| 6 | Deploy backend → Render, frontend → Vercel | `render.yaml`, `frontend/vercel.json`, `DEPLOYMENT.md` |

Also: JWT auth (register / login), saved places (bookmark any activity), user preferences that persist between trips, a full activity history log.

## Project structure

```
PERSONALIZED TRAVEL ITINERARY PLANNER
├── backend/                 FastAPI application
│   ├── app/
│   │   ├── main.py          app factory, CORS, /api router mounting
│   │   ├── config.py        pydantic-settings (reads .env)
│   │   ├── routes/          auth.py · trips.py · misc.py (explore, saved, prefs, history)
│   │   ├── services/        ai.py · trip.py · history.py · explore.py
│   │   ├── schemas/         schemas.py (Pydantic request/response models)
│   │   ├── prompts/         templates.py (SYSTEM_PROMPT, build_itinerary_prompt …)
│   │   ├── db/              database.py (Supabase clients) · repository.py (CRUD)
│   │   └── utils/           auth.py (JWT, hashing) · errors.py
│   ├── tests/test_services.py
│   ├── requirements.txt
│   └── .env.example
├── database/schema.sql      6 tables + indexes + RLS (run in Supabase SQL editor)
├── frontend/                React 18 + Vite + framer-motion + lucide-react
│   └── src/
│       ├── pages/           Landing · Auth · Dashboard · CreateTrip · TripView · Explore · SavedPlaces · TripHistory
│       ├── components/      Sidebar · TopBar · Layout
│       ├── services/api.js  axios client (tripsAPI, authAPI, exploreAPI, savedAPI, historyAPI)
│       └── utils/           auth.js · placeImages.js
├── .gitignore
├── API.md · ARCHITECTURE.md · DEPLOYMENT.md · PROJECT_COMPLETION.md · SETUP.md
└── render.yaml
```

## Quick start

```bash
# 1. Database — paste database/schema.sql into Supabase SQL Editor and Run

# 2. Backend
cd backend
cp .env.example .env            # fill SUPABASE_*, SECRET_KEY, GROQ_API_KEY
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000/docs

# 3. Frontend
cd ../frontend
cp .env.example .env            # VITE_API_URL=http://localhost:8000/api
npm install
npm run dev                     # http://localhost:5173
```

No Supabase or AI key yet? The backend still runs: it falls back to an **in-memory store** and an **offline template itinerary** so every screen can be exercised. See `SETUP.md` for the full walkthrough and `DEPLOYMENT.md` for Render + Vercel.

## Tech stack

React 18 · Vite · React Router 7 · Framer Motion · Lucide · Axios · FastAPI · Pydantic v2 · PyJWT · supabase-py · Groq SDK · Gunicorn/Uvicorn · Supabase Postgres · Render · Vercel
