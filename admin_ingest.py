"""
Admin RAG Ingestion Script
==========================
Run this script to ingest all documents inside data/documents/ 
into the global (admin) vector store. This data will be accessible to ALL users.
"""
import sys
from pathlib import Path
import argparse

# Ensure we can import the backend package
sys.path.append(str(Path(__file__).parent))

from backend.rag.ingestion import ingest_all_documents
from backend.rag.vector_store import get_collection_stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest global documents for all users.")
    parser.add_argument("--force", action="store_true", help="Force re-ingest all documents")
    args = parser.parse_args()

    print("🚀 Starting Admin RAG Ingestion (Global Documents)...")
    results = ingest_all_documents(force=args.force)
    
    stats = get_collection_stats()
    
    print("\n✅ Ingestion Complete. Summary:")
    if not results:
        print("  (No files found or all files failed)")
    for file, count in results.items():
        print(f"  - {file}: {count} chunks")
        
    print(f"\n📊 Total Chunks in DB: {stats['total_chunks']}")
