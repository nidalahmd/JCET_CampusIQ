from app.core.config import get_settings
from app.core.database import Base
from app import models  # noqa: F401


def test_database_configuration_uses_psycopg() -> None:
    assert get_settings().database_url.startswith("postgresql+psycopg://")


def test_required_models_are_registered() -> None:
    required_tables = {
        "users",
        "documents",
        "document_chunks",
        "conversations",
        "messages",
        "message_sources",
        "feedback",
        "questions",
        "audit_logs",
    }

    assert required_tables.issubset(Base.metadata.tables)