import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import create_access_token
from app.main import app
from app.models.entities import (
    Conversation,
    Document,
    DocumentChunk,
    Message,
    MessageRole,
    MessageSource,
    ProcessingStatus,
    User,
    UserRole,
)
from app.services.embedding import get_embedding_service
from app.services.rag import (
    FALLBACK_UNKNOWN_MESSAGE,
    execute_chat,
    generate_grounded_answer,
    retrieve_context,
)

client = TestClient(app)


@pytest.fixture
def student_auth_token() -> str:
    """Fixture providing valid JWT for a student."""
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "test.student.rag@jcet.edu.in"))
        if not user:
            user = User(
                id=uuid.uuid4(),
                email="test.student.rag@jcet.edu.in",
                password_hash="$2b$12$eXAmPLeHaShEdPaSsWoRdFoRtEsTiNgPuRpOsEsOnLy12345678",
                name="RAG Test Student",
                role=UserRole.STUDENT,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return create_access_token({"sub": str(user.id), "role": user.role.value})


@pytest.fixture
def sample_jcet_doc() -> Document:
    """Fixture providing a processed JCET sample document with pgvector chunk."""
    with SessionLocal() as db:
        doc = db.scalar(select(Document).where(Document.title == "JCET Academic Test Document"))
        if not doc:
            doc = Document(
                id=uuid.uuid4(),
                title="JCET Academic Test Document",
                category="Academics",
                department="CSE",
                academic_year="2025-2026",
                file_name="jcet_academic_test.txt",
                file_type=".txt",
                storage_path="documents/jcet_academic_test.txt",
                processing_status=ProcessingStatus.PROCESSED,
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            content = "Students must maintain a minimum attendance of 75% in each course to be eligible to appear for the end semester examinations."
            embedder = get_embedding_service()
            emb = embedder.embed_text(content)

            chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=doc.id,
                chunk_index=0,
                content=content,
                page_number=1,
                section_title="Attendance Regulations",
                embedding=emb,
            )
            db.add(chunk)
            db.commit()

        return doc


def test_retrieve_context_finds_relevant_chunks(sample_jcet_doc: Document):
    """Test pgvector retrieval finds chunks related to attendance."""
    with SessionLocal() as db:
        chunks = retrieve_context("What is the minimum attendance requirement at JCET?", db, top_k=3)
        assert len(chunks) > 0
        assert any("attendance" in c.content.lower() for c in chunks)
        assert chunks[0].relevance_score >= 0.2


def test_unknown_query_returns_strict_refusal_phrase():
    """Test that out-of-domain query refuses to hallucinate facts."""
    with SessionLocal() as db:
        unrelated_query = "What is the tuition fee for the NASA Mars Astronaut Training at JCET?"
        chunks = retrieve_context(unrelated_query, db, top_k=2)
        answer = generate_grounded_answer(unrelated_query, chunks)
        assert answer == FALLBACK_UNKNOWN_MESSAGE


def test_execute_chat_persists_conversation_and_sources(sample_jcet_doc: Document):
    """Test execute_chat persists conversation, user message, assistant message, and message sources."""
    with SessionLocal() as db:
        student_user = db.scalar(select(User).where(User.email == "test.student.rag@jcet.edu.in"))
        if not student_user:
            student_user = User(
                id=uuid.uuid4(),
                email="test.student.rag@jcet.edu.in",
                password_hash="$2b$12$eXAmPLeHaShEdPaSsWoRdFoRtEsTiNgPuRpOsEsOnLy12345678",
                name="RAG Test Student",
                role=UserRole.STUDENT,
            )
            db.add(student_user)
            db.commit()
            db.refresh(student_user)

        res = execute_chat(
            user_id=student_user.id,
            prompt="What is the attendance requirement at JCET?",
            conversation_id=None,
            db=db,
        )

        assert "conversation_id" in res
        assert res["message"]["role"] == "assistant"
        assert len(res["message"]["content"]) > 0

        # Verify conversation in db
        conv_id = uuid.UUID(res["conversation_id"])
        conv = db.scalar(select(Conversation).where(Conversation.id == conv_id))
        assert conv is not None
        assert conv.user_id == student_user.id

        # Verify messages
        msgs = db.scalars(select(Message).where(Message.conversation_id == conv_id)).all()
        assert len(msgs) >= 2
        assert msgs[0].role == MessageRole.USER
        assert msgs[1].role == MessageRole.ASSISTANT


def test_api_chat_endpoint(student_auth_token: str, sample_jcet_doc: Document):
    """Test POST /api/chat endpoint."""
    res = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {student_auth_token}"},
        json={"prompt": "What is the minimum attendance requirement at JCET?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "conversation_id" in data
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert len(data["message"]["content"]) > 0


def test_api_conversation_history_endpoints(student_auth_token: str, sample_jcet_doc: Document):
    """Test conversation listing, retrieval, and deletion endpoints."""
    # 1. Create a conversation via chat
    chat_res = client.post(
        "/api/chat",
        headers={"Authorization": f"Bearer {student_auth_token}"},
        json={"prompt": "Tell me about JCET attendance policies."},
    )
    assert chat_res.status_code == 200
    conv_id = chat_res.json()["conversation_id"]

    # 2. List conversations
    list_res = client.get(
        "/api/chat/conversations",
        headers={"Authorization": f"Bearer {student_auth_token}"},
    )
    assert list_res.status_code == 200
    convs = list_res.json()
    assert any(c["id"] == conv_id for c in convs)

    # 3. Get single conversation detail
    detail_res = client.get(
        f"/api/chat/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {student_auth_token}"},
    )
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["messages"]) >= 2

    # 4. Delete conversation
    del_res = client.delete(
        f"/api/chat/conversations/{conv_id}",
        headers={"Authorization": f"Bearer {student_auth_token}"},
    )
    assert del_res.status_code == 204
