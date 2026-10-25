"""History service — records every meaningful user action."""

from typing import Optional

from app.db.repository import BaseRepository, get_repository


class HistoryService:
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    def record(self, user_id: str, action: str, trip_id: Optional[str] = None, details: Optional[dict] = None) -> dict:
        return self.repo.add_history(user_id, action, trip_id, details or {})

    def list(self, user_id: str, limit: int = 50) -> list[dict]:
        return self.repo.list_history(user_id, limit)


def get_history_service() -> HistoryService:
    return HistoryService(get_repository())
