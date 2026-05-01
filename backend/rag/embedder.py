"""
RAG Embedder
=============
Wraps Google's text-embedding-004 model for both indexing and querying.
Uses two task types:
  - retrieval_document  → for embedding chunks during ingestion
  - retrieval_query     → for embedding user queries at retrieval time
"""

from typing import List
from google import genai
from google.genai import types

from .config import GOOGLE_API_KEY, EMBEDDING_MODEL

if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is not set. Add it to your .env file.")

# One shared client instance
_client = genai.Client(api_key=GOOGLE_API_KEY)


def embed_documents(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of document chunks for storage in the vector store.
    Uses task_type='RETRIEVAL_DOCUMENT' — optimised for indexed text.

    Args:
        texts: List of chunk strings to embed.

    Returns:
        List of embedding vectors (list of floats).
    """
    embeddings = []
    for text in texts:
        response = _client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
        )
        embeddings.append(response.embeddings[0].values)
    return embeddings


def embed_query(query: str) -> List[float]:
    """
    Embed a single user query for similarity search.
    Uses task_type='RETRIEVAL_QUERY' — optimised for search queries.

    Args:
        query: The user's question string.

    Returns:
        Embedding vector (list of floats).
    """
    response = _client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=query,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return response.embeddings[0].values
