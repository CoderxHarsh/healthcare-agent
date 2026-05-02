"""
RAG Document Ingestion
=======================
Loads documents from data/documents/, chunks them, embeds them,
and stores them in PostgreSQL using pgvector.

Supported file types:
  - PDF  (.pdf)   — via pypdf
  - Text (.txt)   — plain read
  - Markdown (.md)

Run this directly to index your documents:
    python -m backend.rag.ingestion

Or call ingest_all_documents() from anywhere in the app.
"""

import hashlib
import logging
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from .config import DOCUMENTS_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from .embedder import embed_documents
from .vector_store import add_chunks, delete_chunks_by_source, get_collection_stats

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Rate limit config (Gemini free tier = 100 req/min)
# ─────────────────────────────────────────────
BATCH_SIZE = 50          # safe batch size under free tier
BATCH_DELAY = 1.5        # seconds between batches (polite delay)
MAX_RETRIES = 5          # retry attempts on 429
BASE_BACKOFF = 45        # base wait time on 429 (Gemini suggests ~42s)


# ─────────────────────────────────────────────
# Text extraction
# ─────────────────────────────────────────────

def _extract_text_from_pdf(path: Path) -> List[Tuple[str, int]]:
    """
    Extract text from a PDF.
    Returns list of (page_text, page_number) tuples.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("Install pypdf: pip install pypdf")

    reader = PdfReader(str(path))
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append((text, i + 1))
    return pages


def _extract_text_from_txt(path: Path) -> List[Tuple[str, int]]:
    """Read a plain text or markdown file as a single 'page'."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return [(text, 1)]


def extract_text(path: Path) -> List[Tuple[str, int]]:
    """Dispatch to the right extractor based on file extension."""
    ext = path.suffix.lower()
    if ext == ".pdf":
        return _extract_text_from_pdf(path)
    elif ext in (".txt", ".md"):
        return _extract_text_from_txt(path)
    else:
        logger.warning(f"Unsupported file type: {path.name} — skipping.")
        return []


# ─────────────────────────────────────────────
# Chunking
# ─────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping character-level chunks.
    Tries to split at sentence boundaries ('. ') where possible.
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            search_start = start + int(chunk_size * 0.8)
            boundary = text.rfind(". ", search_start, end)
            if boundary != -1:
                end = boundary + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap if end - overlap > start else end

    return chunks


# ─────────────────────────────────────────────
# Chunk ID generation
# ─────────────────────────────────────────────

def make_chunk_id(source: str, page: int, chunk_index: int) -> str:
    """Create a deterministic, unique chunk ID."""
    raw = f"{source}__p{page}__c{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()


# ─────────────────────────────────────────────
# Rate-limit-aware embedding
# ─────────────────────────────────────────────

def _embed_with_retry(batch: List[str]) -> List:
    """
    Call embed_documents() with exponential backoff on 429 errors.
    Gemini free tier: 100 requests/min — retries after ~45s on rate limit.
    """
    for attempt in range(MAX_RETRIES):
        try:
            return embed_documents(batch)

        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                # Exponential backoff: 45s, 90s, 180s ...
                wait = BASE_BACKOFF * (2 ** attempt) + random.uniform(1, 5)
                logger.warning(
                    f"  ⏳ Rate limited (429). "
                    f"Waiting {wait:.0f}s before retry {attempt + 1}/{MAX_RETRIES}..."
                )
                time.sleep(wait)
            else:
                raise  # Not a rate-limit error — re-raise immediately

    raise RuntimeError(f"Embedding failed after {MAX_RETRIES} retries due to rate limiting.")


def _embed_all_chunks(texts: List[str]) -> List:
    """
    Embed all chunks in safe batches with delays between them.
    Prevents hitting Gemini free tier limit (100 req/min).
    """
    all_embeddings = []
    total_batches = -(-len(texts) // BATCH_SIZE)  # ceiling division

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        logger.info(f"  Embedding batch {batch_num} / {total_batches} ({len(batch)} chunks)")

        embeddings = _embed_with_retry(batch)
        all_embeddings.extend(embeddings)

        # Polite delay between batches — skip after last batch
        if batch_num < total_batches:
            time.sleep(BATCH_DELAY)

    return all_embeddings


# ─────────────────────────────────────────────
# Main ingestion functions
# ─────────────────────────────────────────────

def ingest_file(path: Path, force: bool = False, user_id: Optional[int] = None) -> int:
    """
    Ingest a single file into the vector store.

    Args:
        path:  Path to the document file.
        force: If True, delete existing chunks for this file first.
        user_id: Optional user ID to associate with the chunks (None = Global).

    Returns:
        Number of chunks indexed.
    """
    source_name = path.name
    logger.info(f"Ingesting: {source_name}")

    if force:
        removed = delete_chunks_by_source(source_name, user_id=user_id)
        if removed:
            logger.info(f"  Removed {removed} old chunks for '{source_name}'")

    # 1. Extract text pages
    pages = extract_text(path)
    if not pages:
        logger.warning(f"  No text extracted from {source_name}")
        return 0

    # 2. Build chunks with metadata
    all_chunk_ids: List[str] = []
    all_texts: List[str] = []
    all_metadatas: List[Dict[str, Any]] = []

    for page_text, page_num in pages:
        chunks = chunk_text(page_text)
        for i, chunk in enumerate(chunks):
            chunk_id = make_chunk_id(source_name, page_num, i)
            all_chunk_ids.append(chunk_id)
            all_texts.append(chunk)
            all_metadatas.append({
                "source": source_name,
                "page": page_num,
                "chunk_index": i,
            })

    if not all_texts:
        return 0

    # 3. Embed with rate-limit handling
    all_embeddings = _embed_all_chunks(all_texts)

    # 4. Upsert into PostgreSQL
    add_chunks(all_embeddings, all_texts, all_metadatas, user_id=user_id)
    logger.info(f"  ✅ Indexed {len(all_texts)} chunks from '{source_name}'")
    return len(all_texts)


def ingest_all_documents(force: bool = False) -> Dict[str, int]:
    """
    Ingest every supported document in data/documents/.

    Args:
        force: Re-ingest even if already present.

    Returns:
        Dict mapping filename → chunk count.
    """
    supported = {".pdf", ".txt", ".md"}
    files = [f for f in DOCUMENTS_DIR.iterdir() if f.suffix.lower() in supported]

    if not files:
        logger.warning(f"No documents found in {DOCUMENTS_DIR}. Drop PDFs/TXTs there and re-run.")
        return {}

    results = {}
    for file in files:
        try:
            count = ingest_file(file, force=force, user_id=None)
            results[file.name] = count
        except Exception as e:
            logger.error(f"Failed to ingest {file.name}: {e}")
            results[file.name] = 0

    stats = get_collection_stats()
    logger.info(f"\nTotal chunks in store: {stats['total_chunks']}")
    return results


# ─────────────────────────────────────────────
# CLI entrypoint
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    force_flag = "--force" in sys.argv
    print(f"\nStarting RAG ingestion (force={force_flag})")
    print(f"Documents directory: {DOCUMENTS_DIR}\n")

    results = ingest_all_documents(force=force_flag)

    if results:
        print("\nIngestion Summary:")
        for fname, count in results.items():
            status = "✅ OK  " if count > 0 else "⚠️  WARN"
            print(f"  {status}  {fname}: {count} chunks")
    else:
        print("No documents were ingested.")

    stats = get_collection_stats()
    print(f"\nVector store: {stats['total_chunks']} total chunks in '{stats['collection_name']}'")