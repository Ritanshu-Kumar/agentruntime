from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.infrastructure.db.session import create_database_engine

router = APIRouter(tags=["health"])

_engine = None


def get_database_engine():
    global _engine

    if _engine is None:
        _engine = create_database_engine(
            get_settings().database_url
        )

    return _engine


@router.get("/ready")
def readiness() -> dict[str, str]:
    try:
        with get_database_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is unavailable",
        ) from exc

    return {
        "status": "ready",
        "database": "ok",
    }