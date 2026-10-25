"""Database connection and initialization."""

import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)


class Database:
    """Supabase database client wrapper."""

    def __init__(self):
        """Initialize Supabase client."""
        from supabase import Client, create_client

        settings = get_settings()
        if not settings.supabase_configured:
            raise RuntimeError("Supabase is not configured (SUPABASE_URL / keys missing)")

        anon_key = settings.supabase_key or settings.supabase_service_role_key
        service_key = settings.supabase_service_role_key or settings.supabase_key

        self.client: Client = create_client(settings.supabase_url, anon_key)
        self.service_client: Client = create_client(settings.supabase_url, service_key)
        logger.info("Supabase clients initialized")

    def get_client(self):
        """Get Supabase client."""
        return self.client

    def get_service_client(self):
        """Get service role client for admin operations."""
        return self.service_client


_db: Optional[Database] = None


def get_database() -> Database:
    global _db
    if _db is None:
        _db = Database()
    return _db
