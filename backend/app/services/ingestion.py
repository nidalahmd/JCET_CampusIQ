import logging
import uuid
from pathlib import Path

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models.entities import Document, DocumentChunk, ProcessingStatus
from app.services.chunker import chunk_document
from app.services.embedding import get_embedding_service
from app.services.parsers import parse_document

logger = logging.getLogger("campusiq.ingestion")


def ingest_document_sync(document_id: uuid.UUID) -> bool:
    """Synchronous ingestion execution for background task or direct pipeline."""
    with SessionLocal() as db:
        doc = db.scalar(select(Document).where(Document.id == document_id))
        if not doc:
            logger.error(f"Document {document_id} not found for ingestion.")
            return False

        try:
            # 1. Update status to PROCESSING
            doc.processing_status = ProcessingStatus.PROCESSING
            db.add(doc)
            db.commit()
            db.refresh(doc)

            file_path = Path(doc.storage_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Document file not found on disk at: {doc.storage_path}")

            # 2. Parse document
            parsed_doc = parse_document(file_path, doc.file_type)

            # 3. Header-aware chunking
            chunks = chunk_document(parsed_doc)

            # 4. Generate embeddings
            embedding_service = get_embedding_service()
            chunk_texts = [c.content for c in chunks]
            embeddings = embedding_service.embed_batch(chunk_texts) if chunk_texts else []

            # 5. Clear prior chunks for this document (idempotent for reindex)
            db.execute(delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))

            # 6. Insert new chunks
            for idx, (chunk_item, emb_vector) in enumerate(zip(chunks, embeddings)):
                db_chunk = DocumentChunk(
                    document_id=doc.id,
                    chunk_index=idx,
                    content=chunk_item.content,
                    token_count=chunk_item.token_count,
                    page_number=chunk_item.page_number,
                    section_title=chunk_item.section_title,
                    chunk_metadata=chunk_item.metadata,
                    embedding=emb_vector,
                )
                db.add(db_chunk)

            # 7. Update status to PROCESSED
            doc.processing_status = ProcessingStatus.PROCESSED
            db.add(doc)
            db.commit()
            logger.info(f"Successfully processed document {doc.id} ({len(chunks)} chunks).")
            return True

        except Exception as exc:
            db.rollback()
            logger.exception(f"Ingestion failed for document {document_id}: {exc}")
            # Mark document as FAILED
            try:
                doc_failed = db.scalar(select(Document).where(Document.id == document_id))
                if doc_failed:
                    doc_failed.processing_status = ProcessingStatus.FAILED
                    db.add(doc_failed)
                    db.commit()
            except Exception:
                pass
            return False
