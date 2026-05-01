"""
RAG Retriever
==============
Query interface for the vector store.
Called by the chatbot to fetch relevant knowledge chunks before building the LLM prompt.
"""

import logging
from typing import List, Dict, Any, Optional

from .embedder import embed_query
from .vector_store import query_chunks, get_collection_stats
from .config import TOP_K_RESULTS

logger = logging.getLogger(__name__)


def retrieve(query: str, n_results: int = TOP_K_RESULTS, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant knowledge chunks for a user query.

    Args:
        query:    The user's message / question.
        n_results: Max chunks to return (default from config).
        user_id: Optional user ID to filter by.

    Returns:
        List of dicts: [{text, source, page, score}, ...]
        Empty list if nothing relevant is found or store is empty.
    """
    try:
        stats = get_collection_stats()
        if stats["total_chunks"] == 0:
            return []   # Store is empty — skip silently

        query_vector = embed_query(query)
        chunks = query_chunks(query_vector, n_results=n_results, user_id=user_id)
        return chunks

    except Exception as e:
        logger.warning(f"RAG retrieval failed (non-fatal): {e}")
        return []


def format_rag_context(chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks into a context block for injection into the LLM prompt.

    Args:
        chunks: Output of retrieve()

    Returns:
        Formatted string block, or empty string if no chunks.
    """
    if not chunks:
        return ""

    lines = [
        "\n\n--- KNOWLEDGE BASE (retrieved context) ---",
        "Use the following excerpts from trusted medical documents to answer the user's question.",
        "Cite the source name when referencing specific facts.\n",
    ]

    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "Unknown")
        page = chunk.get("page", "")
        score = chunk.get("score", 0)
        text = chunk.get("text", "")

        page_label = f", page {page}" if page else ""
        lines.append(f"[{i}] Source: {source}{page_label} (relevance: {score:.2f})")
        lines.append(text)
        lines.append("")

    lines.append("--- END KNOWLEDGE BASE ---\n")
    return "\n".join(lines)
