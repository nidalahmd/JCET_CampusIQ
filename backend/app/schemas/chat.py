import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SourceItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    chunk_id: str
    document_title: str
    section_title: str | None = None
    page_number: int | None = None
    source_excerpt: str
    relevance_score: float = 0.0


class MessageItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    created_at: str
    latency_ms: int | None = None
    sources: list[SourceItem] = Field(default_factory=list)


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=2000)
    conversation_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: MessageItem
    sources: list[SourceItem] = Field(default_factory=list)
    latency_ms: int = 0


class ConversationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str | None = None
    created_at: str
    updated_at: str
    message_count: int = 0


class ConversationDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str | None = None
    created_at: str
    updated_at: str
    messages: list[MessageItem]
