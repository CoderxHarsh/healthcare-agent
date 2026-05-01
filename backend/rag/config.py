"""
RAG Pipeline Configuration
===========================
Central config for all RAG components — paths, model names, chunking settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Load env
env_path = find_dotenv() or Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────
ROOT_DIR = Path(__file__).parent.parent.parent          # d:/Projects/HealthCareAGENT
DATA_DIR = ROOT_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"                  # Drop PDFs / TXTs here
CHROMA_DIR = DATA_DIR / "chroma_db"                    # Persisted vector store

# Create dirs if missing
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────
# Embedding model
# ─────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = "gemini-embedding-2"          # Google's latest embedding model
EMBEDDING_TASK_TYPE = "retrieval_document"             # For indexing docs

# ─────────────────────────────────────────────
# ChromaDB collection
# ─────────────────────────────────────────────
CHROMA_COLLECTION_NAME = "healthcare_knowledge"

# ─────────────────────────────────────────────
# Chunking settings
# ─────────────────────────────────────────────
CHUNK_SIZE = 800          # characters per chunk
CHUNK_OVERLAP = 150       # overlap to preserve context across boundaries

# ─────────────────────────────────────────────
# Retrieval settings
# ─────────────────────────────────────────────
TOP_K_RESULTS = 4         # how many chunks to retrieve per query
MIN_RELEVANCE_SCORE = 0.3 # minimum cosine similarity to include a chunk
