import os
import shutil
import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.config import get_settings
from app.core.database import get_db
from app.models.entities import Document, DocumentChunk, ProcessingStatus, User
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentUpdate,
)
from app.services.ingestion import ingest_document_sync

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}


def _map_doc_response(doc: Document, chunks_count: int = 0) -> DocumentResponse:
    return DocumentResponse(
        id=doc.id,
        title=doc.title,
        file_name=doc.file_name,
        file_type=doc.file_type,
        storage_path=doc.storage_path,
        category=doc.category,
        department=doc.department,
        academic_year=doc.academic_year,
        processing_status=doc.processing_status,
        version=doc.version,
        uploaded_by=doc.uploaded_by,
        chunks_count=chunks_count,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str | None = Form(None),
    department: str | None = Form(None),
    academic_year: str | None = Form(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    settings = get_settings()
    upload_dir = Path(settings.upload_directory)
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = file.filename or "uploaded_document"
    file_ext = Path(original_name).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    doc_id = uuid.uuid4()
    saved_filename = f"{doc_id}{file_ext}"
    destination_path = upload_dir / saved_filename

    with destination_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_type = file_ext.lstrip(".")
    document = Document(
        id=doc_id,
        title=title.strip(),
        file_name=original_name,
        file_type=file_type,
        storage_path=str(destination_path),
        category=category.strip() if category else None,
        department=department.strip() if department else None,
        academic_year=academic_year.strip() if academic_year else None,
        processing_status=ProcessingStatus.UPLOADED,
        version=1,
        uploaded_by=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Queue asynchronous background ingestion
    background_tasks.add_task(ingest_document_sync, document.id)

    return _map_doc_response(document, chunks_count=0)


@router.get("", response_model=DocumentListResponse)
def list_documents(
    category: str | None = Query(None),
    department: str | None = Query(None),
    academic_year: str | None = Query(None),
    status_filter: ProcessingStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentListResponse:
    query = select(Document)

    if category:
        query = query.where(Document.category == category)
    if department:
        query = query.where(Document.department == department)
    if academic_year:
        query = query.where(Document.academic_year == academic_year)
    if status_filter:
        query = query.where(Document.processing_status == status_filter)

    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    docs = db.scalars(query.order_by(Document.created_at.desc()).offset(skip).limit(limit)).all()

    # Query chunk counts in batch
    doc_ids = [d.id for d in docs]
    chunk_counts: dict[uuid.UUID, int] = {}
    if doc_ids:
        counts = db.execute(
            select(DocumentChunk.document_id, func.count(DocumentChunk.id))
            .where(DocumentChunk.document_id.in_(doc_ids))
            .group_by(DocumentChunk.document_id)
        ).all()
        chunk_counts = {doc_id: count for doc_id, count in counts}

    items = [_map_doc_response(d, chunk_counts.get(d.id, 0)) for d in docs]
    return DocumentListResponse(items=items, total=total)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    doc = db.scalar(select(Document).where(Document.id == document_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunk_count = db.scalar(select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc.id)) or 0
    return _map_doc_response(doc, chunk_count)


@router.get("/{document_id}/chunks", response_model=list[DocumentChunkResponse])
def get_document_chunks(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DocumentChunkResponse]:
    doc = db.scalar(select(Document).where(Document.id == document_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    chunks = db.scalars(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
    ).all()

    return [
        DocumentChunkResponse(
            id=c.id,
            document_id=c.document_id,
            chunk_index=c.chunk_index,
            content=c.content,
            token_count=c.token_count,
            page_number=c.page_number,
            section_title=c.section_title,
            chunk_metadata=c.chunk_metadata,
            has_embedding=c.embedding is not None,
            created_at=c.created_at,
        )
        for c in chunks
    ]


@router.post("/{document_id}/process", response_model=DocumentResponse)
def process_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    doc = db.scalar(select(Document).where(Document.id == document_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    doc.processing_status = ProcessingStatus.PROCESSING
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(ingest_document_sync, doc.id)
    return _map_doc_response(doc, chunks_count=0)


@router.post("/{document_id}/reindex", response_model=DocumentResponse)
def reindex_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    doc = db.scalar(select(Document).where(Document.id == document_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    doc.version += 1
    doc.processing_status = ProcessingStatus.PROCESSING
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(ingest_document_sync, doc.id)
    return _map_doc_response(doc, chunks_count=0)


@router.post("/{document_id}/archive", response_model=DocumentResponse)
def archive_document(
    document_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    doc = db.scalar(select(Document).where(Document.id == document_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    doc.processing_status = ProcessingStatus.ARCHIVED
    db.add(doc)
    db.commit()
    db.refresh(doc)

    chunk_count = db.scalar(select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc.id)) or 0
    return _map_doc_response(doc, chunk_count)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> None:
    doc = db.scalar(select(Document).where(Document.id == document_id))
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Remove storage file if exists
    try:
        file_path = Path(doc.storage_path)
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass

    db.delete(doc)
    db.commit()
