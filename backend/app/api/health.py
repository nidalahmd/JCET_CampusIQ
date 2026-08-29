from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "campusiq-api"}


@router.get("/db")
def database_health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        extension = db.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'")).scalar_one_or_none()
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail={"status": "unavailable", "database": "unavailable"}) from error
    return {"status": "ok", "database": "connected", "pgvector": "enabled" if extension else "missing"}
