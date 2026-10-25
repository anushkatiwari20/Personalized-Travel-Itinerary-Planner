"""FastAPI application entry point.

Run locally:   uvicorn app.main:app --reload
Production:    gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes.auth import router as auth_router
from app.routes.misc import explore_router, history_router, prefs_router, saved_router
from app.routes.trips import router as trips_router
from app.utils.errors import AppError

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting Travel Planner API [{settings.environment}] — AI provider: {settings.ai_provider}")
    logger.info(f"Supabase configured: {settings.supabase_configured}")
    yield
    logger.info("Shutting down")


app = FastAPI(
    title="Personalized Travel Itinerary Planner API",
    description="AI-powered day-by-day travel itineraries. React + FastAPI + Supabase.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/", tags=["Health"])
def root():
    return {"name": "Personalized Travel Itinerary Planner API", "status": "ok", "docs": "/docs"}


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "ai_provider": settings.ai_provider,
        "database": "supabase" if settings.supabase_configured else "in-memory",
    }


# All feature routes live under /api  (frontend uses VITE_API_URL=https://<backend>/api)
API_PREFIX = "/api"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(trips_router, prefix=API_PREFIX)
app.include_router(explore_router, prefix=API_PREFIX)
app.include_router(saved_router, prefix=API_PREFIX)
app.include_router(prefs_router, prefix=API_PREFIX)
app.include_router(history_router, prefix=API_PREFIX)
