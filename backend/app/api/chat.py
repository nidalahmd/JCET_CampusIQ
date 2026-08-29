import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.entities import Conversation, Document, Message, MessageSource, User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationItem,
    MessageItem,
    SourceItem,
)
from app.services.rag import execute_chat

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def send_chat_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    result = execute_chat(
        user_id=current_user.id,
        prompt=payload.prompt,
        conversation_id=payload.conversation_id,
        db=db,
    )
    return ChatResponse(**result)


@router.get("/conversations", response_model=list[ConversationItem])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationItem]:
    stmt = (
        select(
            Conversation,
            func.count(Message.id).label("msg_count"),
        )
        .outerjoin(Message, Conversation.id == Message.conversation_id)
        .where(Conversation.user_id == current_user.id)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
    )
    results = db.execute(stmt).all()

    items: list[ConversationItem] = []
    for conv, count in results:
        items.append(
            ConversationItem(
                id=str(conv.id),
                title=conv.title or "New Conversation",
                created_at=conv.created_at.isoformat(),
                updated_at=conv.updated_at.isoformat(),
                message_count=count or 0,
            )
        )
    return items


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationDetail:
    conv = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = db.scalars(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    message_items: list[MessageItem] = []
    for msg in messages:
        # Load sources for assistant messages
        sources_list: list[SourceItem] = []
        if msg.role.value == "assistant":
            raw_sources = db.execute(
                select(MessageSource, Document.title)
                .join(Document, MessageSource.document_id == Document.id)
                .where(MessageSource.message_id == msg.id)
            ).all()

            for s_row, doc_title in raw_sources:
                sources_list.append(
                    SourceItem(
                        document_id=str(s_row.document_id),
                        chunk_id=str(s_row.chunk_id),
                        document_title=doc_title,
                        section_title=None,
                        page_number=s_row.page_number,
                        source_excerpt=s_row.source_excerpt or "",
                        relevance_score=s_row.relevance_score or 0.0,
                    )
                )

        message_items.append(
            MessageItem(
                id=str(msg.id),
                role=msg.role.value,
                content=msg.content,
                created_at=msg.created_at.isoformat(),
                latency_ms=msg.latency_ms,
                sources=sources_list,
            )
        )

    return ConversationDetail(
        id=str(conv.id),
        title=conv.title or "Conversation",
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=message_items,
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    conv = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    db.delete(conv)
    db.commit()
