import math
from dataclasses import dataclass, field
from typing import Any

from app.services.parsers import ParsedDocument, ParsedSection

TARGET_CHUNK_SIZE = 650
TARGET_CHUNK_OVERLAP = 120


@dataclass
class DocumentChunkItem:
    chunk_index: int
    content: str
    token_count: int
    page_number: int | None = None
    section_title: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


def _estimate_tokens(text: str) -> int:
    # Standard heuristic: ~4 chars per token in English / technical text
    return max(1, math.ceil(len(text) / 4))


def chunk_section(
    section: ParsedSection,
    start_index: int,
    chunk_size: int = TARGET_CHUNK_SIZE,
    chunk_overlap: int = TARGET_CHUNK_OVERLAP,
) -> tuple[list[DocumentChunkItem], int]:
    text = section.content.strip()
    if not text:
        return [], start_index

    # If section is smaller than target chunk size, keep as single chunk
    if len(text) <= chunk_size:
        chunk = DocumentChunkItem(
            chunk_index=start_index,
            content=text,
            token_count=_estimate_tokens(text),
            page_number=section.page_number,
            section_title=section.section_title,
            metadata={
                "char_count": len(text),
                "page": section.page_number,
                "section": section.section_title,
                **section.metadata,
            },
        )
        return [chunk], start_index + 1

    # Split larger section while respecting sentence/paragraph boundaries
    chunks: list[DocumentChunkItem] = []
    current_idx = start_index
    step = chunk_size - chunk_overlap
    pos = 0

    while pos < len(text):
        end_pos = min(pos + chunk_size, len(text))
        chunk_text = text[pos:end_pos]

        # If not at the very end of the text, try finding a clean boundary (period, newline, question mark, semicolon)
        if end_pos < len(text):
            # Look for sentence boundary near the end
            last_break = max(
                chunk_text.rfind(". "),
                chunk_text.rfind(".\n"),
                chunk_text.rfind("\n\n"),
                chunk_text.rfind("\n"),
                chunk_text.rfind("; "),
            )
            if last_break > chunk_size // 2:
                # Include the punctuation mark
                actual_end = pos + last_break + (2 if chunk_text[last_break : last_break + 2] in (". ", ".\n", "\n\n", "; ") else 1)
                chunk_text = text[pos:actual_end]
                pos = actual_end - chunk_overlap
            else:
                pos += step
        else:
            pos = len(text)

        cleaned_chunk = chunk_text.strip()
        if cleaned_chunk:
            chunks.append(
                DocumentChunkItem(
                    chunk_index=current_idx,
                    content=cleaned_chunk,
                    token_count=_estimate_tokens(cleaned_chunk),
                    page_number=section.page_number,
                    section_title=section.section_title,
                    metadata={
                        "char_count": len(cleaned_chunk),
                        "page": section.page_number,
                        "section": section.section_title,
                        **section.metadata,
                    },
                )
            )
            current_idx += 1

    return chunks, current_idx


def chunk_document(
    parsed_doc: ParsedDocument,
    chunk_size: int = TARGET_CHUNK_SIZE,
    chunk_overlap: int = TARGET_CHUNK_OVERLAP,
) -> list[DocumentChunkItem]:
    all_chunks: list[DocumentChunkItem] = []
    current_index = 0

    for section in parsed_doc.sections:
        section_chunks, current_index = chunk_section(
            section,
            start_index=current_index,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        all_chunks.extend(section_chunks)

    return all_chunks
