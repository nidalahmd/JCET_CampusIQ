import io
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models.entities import Document, DocumentChunk, ProcessingStatus, UserRole
from app.services.chunker import chunk_document
from app.services.embedding import get_embedding_service
from app.services.ingestion import ingest_document_sync
from app.services.parsers import parse_document, parse_markdown, parse_text


def test_embedding_service_dimensions_and_norm():
    service = get_embedding_service()
    text = "Jawaharlal College of Engineering and Technology academic regulations."
    vec = service.embed_text(text)

    assert len(vec) == 1536
    norm = sum(x * x for x in vec)
    assert abs(norm - 1.0) < 1e-4

    # Batch test
    batch = service.embed_batch(["First sentence.", "Second sentence with more words."])
    assert len(batch) == 2
    assert len(batch[0]) == 1536
    assert len(batch[1]) == 1536


def test_markdown_parser_and_chunker(tmp_path: Path):
    md_file = tmp_path / "sample_regulations.md"
    content = """# JCET Academic Regulations 2026

## Attendance Requirements
Students are required to maintain a minimum of 75% attendance in each course.
Condonation of attendance up to 10% may be granted on medical grounds by the Principal.

## Evaluation and Grading System
The evaluation consists of continuous assessment (40%) and end semester examinations (60%).
A student must secure a minimum of 40% in the end semester examination and 50% in total to pass.
"""
    md_file.write_text(content, encoding="utf-8")

    parsed = parse_document(md_file)
    assert len(parsed.sections) >= 2

    chunks = chunk_document(parsed)
    assert len(chunks) >= 2
    assert any("Attendance Requirements" in (c.section_title or "") for c in chunks)
    assert all(c.token_count > 0 for c in chunks)
    assert all("char_count" in c.metadata for c in chunks)


def test_document_ingestion_api_and_pipeline():
    client = TestClient(app)

    # 1. Register Admin User
    unique_suffix = uuid.uuid4().hex[:6]
    admin_payload = {
        "name": f"Admin Ingest {unique_suffix}",
        "email": f"admin_ingest_{unique_suffix}@jcet.ac.in",
        "password": "Password123!",
        "role": "admin",
    }
    reg_res = client.post("/api/auth/register", json=admin_payload)
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload Document
    doc_content = b"# JCET Placement Guidelines\n\n## Eligibility Criteria\nStudents with CGPA >= 7.0 and no active backlogs are eligible for Tier-1 campus placements.\n\n## Interview Conduct\nFormal dress code and valid identity cards are mandatory for all recruitment drives."
    file_tuple = ("placement_rules.md", io.BytesIO(doc_content), "text/markdown")

    upload_res = client.post(
        "/api/documents",
        headers=headers,
        data={
            "title": "JCET Placement Guidelines 2026",
            "category": "Placement",
            "department": "All Departments",
            "academic_year": "2025-2026",
        },
        files={"file": file_tuple},
    )
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    doc_id = uuid.UUID(doc_data["id"])
    assert doc_data["title"] == "JCET Placement Guidelines 2026"
    assert doc_data["category"] == "Placement"

    # 3. Synchronously Execute Ingestion
    ingest_success = ingest_document_sync(doc_id)
    assert ingest_success is True

    # 4. Verify Document Status is PROCESSED
    get_res = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["processing_status"] == "PROCESSED"
    assert get_res.json()["chunks_count"] >= 2

    # 5. Verify Chunks & Embeddings in PostgreSQL/pgvector
    chunks_res = client.get(f"/api/documents/{doc_id}/chunks", headers=headers)
    assert chunks_res.status_code == 200
    chunks = chunks_res.json()
    assert len(chunks) >= 2
    assert all(c["has_embedding"] is True for c in chunks)
    assert any("Eligibility Criteria" in (c["section_title"] or "") for c in chunks)

    # 6. Archive Document
    archive_res = client.post(f"/api/documents/{doc_id}/archive", headers=headers)
    assert archive_res.status_code == 200
    assert archive_res.json()["processing_status"] == "ARCHIVED"

    # 7. Delete Document
    del_res = client.delete(f"/api/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 204

    # Verify 404 after deletion
    get_del_res = client.get(f"/api/documents/{doc_id}", headers=headers)
    assert get_del_res.status_code == 404


def test_document_rbac_student_forbidden():
    client = TestClient(app)

    # Register Student
    unique_suffix = uuid.uuid4().hex[:6]
    student_payload = {
        "name": f"Student Doc {unique_suffix}",
        "email": f"student_doc_{unique_suffix}@jcet.ac.in",
        "password": "Password123!",
        "role": "student",
    }
    reg_res = client.post("/api/auth/register", json=student_payload)
    assert reg_res.status_code == 201
    student_token = reg_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # Attempt to upload document as student -> 403 Forbidden
    file_tuple = ("test.txt", io.BytesIO(b"Sample plain text"), "text/plain")
    upload_res = client.post(
        "/api/documents",
        headers=student_headers,
        data={"title": "Unauthorized Upload"},
        files={"file": file_tuple},
    )
    assert upload_res.status_code == 403

    # Student CAN list documents (read-only)
    list_res = client.get("/api/documents", headers=student_headers)
    assert list_res.status_code == 200
