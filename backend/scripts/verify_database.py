import sys
import os
from pathlib import Path

from sqlalchemy import text

backend_root = Path(__file__).resolve().parents[1]
os.chdir(backend_root)
sys.path.insert(0, str(backend_root))

from app.core.database import engine

REQUIRED_TABLES = {
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


def main() -> int:
    try:
        with engine.connect() as connection:
            tables = set(
                connection.execute(
                    text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
                ).scalars()
            )
            extension_enabled = connection.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
            ).scalar()
            embedding_is_vector = connection.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
                    "WHERE table_schema = 'public' AND table_name = 'document_chunks' "
                    "AND column_name = 'embedding' AND udt_name = 'vector')"
                )
            ).scalar()
    except Exception as error:
        message = str(error).lower()
        category = "dns" if "translate host name" in message else "connection_or_authentication"
        print("database=unavailable")
        print(f"error_category={category}")
        return 1

    print("database=connected")
    print(f"tables_complete={REQUIRED_TABLES.issubset(tables)}")
    print(f"pgvector_enabled={bool(extension_enabled)}")
    print(f"embedding_vector_type={bool(embedding_is_vector)}")
    return 0 if REQUIRED_TABLES.issubset(tables) and extension_enabled and embedding_is_vector else 1


if __name__ == "__main__":
    raise SystemExit(main())