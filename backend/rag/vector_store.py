"""
RAG Vector Store (PostgreSQL + pgvector)
========================================
Synchronous SQLAlchemy connection to Neon PostgreSQL for vector search.
Handles storing and retrieving KnowledgeChunks with user access control.
"""

import os
from typing import List, Dict, Any, Optional
from sqlalchemy import create_engine, select, func, or_
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv, find_dotenv

from .config import TOP_K_RESULTS, MIN_RELEVANCE_SCORE
from ..models import KnowledgeChunk

# Load .env
env_path = find_dotenv() or os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set.")

# Convert asyncpg URL to standard psycopg2 URL for synchronous operations
if "+asyncpg" in DATABASE_URL:
    SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")
else:
    SYNC_DATABASE_URL = DATABASE_URL

# psycopg2 uses ?sslmode=require, not ?ssl=require (asyncpg format)
SYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("?ssl=require", "?sslmode=require")

# We use a synchronous engine here to avoid blocking the FastAPI async event loop
engine = create_engine(SYNC_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def add_chunks(
    embeddings: List[List[float]],
    documents: List[str],
    metadatas: List[Dict[str, Any]],
    user_id: Optional[int] = None
) -> None:
    """
    Insert chunks into the PostgreSQL vector store.
    """
    with SessionLocal() as session:
        chunks_to_add = []
        for i in range(len(documents)):
            meta = metadatas[i]
            chunk = KnowledgeChunk(
                user_id=user_id,
                text=documents[i],
                source=meta.get("source", "Unknown"),
                page=meta.get("page"),
                chunk_index=meta.get("chunk_index"),
                embedding=embeddings[i]
            )
            chunks_to_add.append(chunk)
        
        if chunks_to_add:
            session.add_all(chunks_to_add)
            session.commit()


def query_chunks(
    query_embedding: List[float],
    n_results: int = TOP_K_RESULTS,
    user_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Find the most similar chunks to a query embedding.
    Ensures privacy by filtering by user_id.
    """
    with SessionLocal() as session:
        filters = []
        if user_id is not None:
            # User can see global (None) + their own
            filters.append(or_(KnowledgeChunk.user_id.is_(None), KnowledgeChunk.user_id == user_id))
        else:
            # Guest or Admin can only see global
            filters.append(KnowledgeChunk.user_id.is_(None))
            
        # Using pgvector's cosine_distance <=> operator
        stmt = select(
            KnowledgeChunk, 
            KnowledgeChunk.embedding.cosine_distance(query_embedding).label("distance")
        )
        
        if filters:
            stmt = stmt.where(*filters)
            
        stmt = stmt.order_by("distance").limit(n_results)
        results = session.execute(stmt).all()
        
        chunks = []
        for row in results:
            chunk = row.KnowledgeChunk
            dist = row.distance
            
            # Cosine distance to similarity (1 - dist)
            score = 1 - dist
            if score >= MIN_RELEVANCE_SCORE:
                chunks.append({
                    "text": chunk.text,
                    "source": chunk.source,
                    "page": chunk.page,
                    "score": round(score, 3),
                    "user_id": chunk.user_id
                })
                
        return chunks


def get_collection_stats() -> Dict[str, Any]:
    """Return basic stats about the vector store."""
    try:
        with SessionLocal() as session:
            count = session.query(func.count(KnowledgeChunk.id)).scalar()
            return {
                "total_chunks": count,
                "collection_name": "KnowledgeChunk (pgvector)",
                "persist_path": "PostgreSQL DB"
            }
    except Exception:
        # Tables might not be created yet during startup checks
        return {
            "total_chunks": 0,
            "collection_name": "KnowledgeChunk (pgvector)",
            "persist_path": "PostgreSQL DB"
        }


def delete_chunks_by_source(source_name: str, user_id: Optional[int] = None) -> int:
    """Remove chunks for a specific file and user."""
    with SessionLocal() as session:
        stmt = session.query(KnowledgeChunk).where(KnowledgeChunk.source == source_name)
        if user_id is not None:
            stmt = stmt.where(KnowledgeChunk.user_id == user_id)
        else:
            stmt = stmt.where(KnowledgeChunk.user_id.is_(None))
            
        chunks = stmt.all()
        count = len(chunks)
        for chunk in chunks:
            session.delete(chunk)
        session.commit()
        return count
