import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.entities import ProcessingStatus


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    token_count: int | None = None
    page_number: int | None = None
    section_title: str | None = None
    chunk_metadata: dict[str, Any] | None = None
    has_embedding: bool = False
    created_at: datetime


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    file_name: str
    file_type: str
    storage_path: str
    category: str | None = None
    department: str | None = None
    academic_year: str | None = None
    processing_status: ProcessingStatus
    version: int
    uploaded_by: uuid.UUID | None = None
    chunks_count: int = 0
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class DocumentUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    category: str | None = Field(None, max_length=150)
    department: str | None = Field(None, max_length=200)
    academic_year: str | None = Field(None, max_length=20)
