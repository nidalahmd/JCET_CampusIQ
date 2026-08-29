"""Create Phase 1 database schema.

Revision ID: 0001_initial_schema
Revises:
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    bind = op.get_bind()
    user_role_type = sa.dialects.postgresql.ENUM("student", "admin", name="user_role")
    proc_status_type = sa.dialects.postgresql.ENUM("UPLOADED", "PROCESSING", "PROCESSED", "FAILED", "ARCHIVED", name="processing_status")
    msg_role_type = sa.dialects.postgresql.ENUM("user", "assistant", name="message_role")
    fb_rating_type = sa.dialects.postgresql.ENUM("positive", "negative", name="feedback_rating")

    for enum in (user_role_type, proc_status_type, msg_role_type, fb_rating_type):
        enum.create(bind, checkfirst=True)

    user_role = sa.dialects.postgresql.ENUM("student", "admin", name="user_role", create_type=False)
    processing_status = sa.dialects.postgresql.ENUM("UPLOADED", "PROCESSING", "PROCESSED", "FAILED", "ARCHIVED", name="processing_status", create_type=False)
    message_role = sa.dialects.postgresql.ENUM("user", "assistant", name="message_role", create_type=False)
    feedback_rating = sa.dialects.postgresql.ENUM("positive", "negative", name="feedback_rating", create_type=False)

    uuid = sa.dialects.postgresql.UUID(as_uuid=True)
    op.create_table("users", sa.Column("id", uuid, primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("email", sa.String(320), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", user_role, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("documents", sa.Column("id", uuid, primary_key=True), sa.Column("title", sa.String(500), nullable=False), sa.Column("file_name", sa.String(500), nullable=False), sa.Column("file_type", sa.String(100), nullable=False), sa.Column("storage_path", sa.String(1000), nullable=False), sa.Column("category", sa.String(150)), sa.Column("department", sa.String(200)), sa.Column("academic_year", sa.String(20)), sa.Column("processing_status", processing_status, nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("uploaded_by", uuid, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("conversations", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("title", sa.String(500)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("document_chunks", sa.Column("id", uuid, primary_key=True), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("version_id", uuid, sa.ForeignKey("documents.id", ondelete="SET NULL")), sa.Column("chunk_index", sa.Integer, nullable=False), sa.Column("content", sa.Text, nullable=False), sa.Column("token_count", sa.Integer), sa.Column("page_number", sa.Integer), sa.Column("section_title", sa.String(500)), sa.Column("metadata", sa.JSON), sa.Column("embedding", Vector(1536)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_table("messages", sa.Column("id", uuid, primary_key=True), sa.Column("conversation_id", uuid, sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False), sa.Column("role", message_role, nullable=False), sa.Column("content", sa.Text, nullable=False), sa.Column("retrieval_metadata", sa.JSON), sa.Column("latency_ms", sa.Integer), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("message_sources", sa.Column("id", uuid, primary_key=True), sa.Column("message_id", uuid, sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False), sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False), sa.Column("chunk_id", uuid, sa.ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False), sa.Column("relevance_score", sa.Float), sa.Column("page_number", sa.Integer), sa.Column("source_excerpt", sa.Text))
    op.create_table("feedback", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("message_id", uuid, sa.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False), sa.Column("rating", feedback_rating, nullable=False), sa.Column("comment", sa.Text), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("questions", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("message_id", uuid, sa.ForeignKey("messages.id", ondelete="SET NULL")), sa.Column("category", sa.String(150)), sa.Column("intent", sa.String(150)), sa.Column("resolved", sa.Boolean, nullable=False), sa.Column("retrieval_score", sa.Float), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("audit_logs", sa.Column("id", uuid, primary_key=True), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("action", sa.String(200), nullable=False), sa.Column("resource_type", sa.String(100), nullable=False), sa.Column("resource_id", uuid), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))


def downgrade() -> None:
    for table in ("audit_logs", "questions", "feedback", "message_sources", "messages", "document_chunks", "conversations", "documents", "users"):
        op.drop_table(table)
    for name in ("feedback_rating", "message_role", "processing_status", "user_role"):
        sa.dialects.postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
