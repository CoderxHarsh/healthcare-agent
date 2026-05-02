"""
Automated Data Training Pipeline
=================================
One-command script to ingest local medical data into the vector store.

Usage:
    python train_model.py --mode ingest       # Process and embed documents
    python train_model.py --mode test         # Test retrieval quality
    python train_model.py --mode stats        # Show knowledge base stats
"""

import sys
import os
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))


def ingest_documents():
    """Ingest documents into vector store."""
    print("\n" + "="*70)
    print("📥 INGESTING DOCUMENTS INTO VECTOR STORE")
    print("="*70)
    
    try:
        from backend.rag.ingestion import ingest_all_documents
        from backend.rag.vector_store import get_collection_stats
        
        print("\n⏳ Processing documents...")
        print("   This may take a few minutes for large batches...")
        
        # Run ingestion
        ingest_all_documents()
        
        # Show results
        stats = get_collection_stats()
        print(f"\n{'='*70}")
        print(f"✅ Ingestion Complete!")
        print(f"   Total chunks: {stats.get('total_chunks', 0)}")
        print(f"   Collection: healthcare_knowledge")
        print(f"{'='*70}\n")
        
        return stats.get('total_chunks', 0)
        
    except Exception as e:
        print(f"❌ Ingestion error: {e}")
        import traceback
        traceback.print_exc()
        return 0


def test_retrieval():
    """Test the knowledge base with sample queries."""
    print("\n" + "="*70)
    print("🧪 TESTING RETRIEVAL QUALITY")
    print("="*70)
    
    try:
        from backend.rag.retriever import retrieve
        from backend.rag.vector_store import get_collection_stats
        
        stats = get_collection_stats()
        if stats.get('total_chunks', 0) == 0:
            print("⚠️  Knowledge base is empty. Run crawl + ingest first.")
            return
        
        test_queries = [
            "Type 2 diabetes symptoms and treatment",
            "How to manage high blood pressure",
            "Mental health support and resources",
            "Exercise benefits for cardiovascular health",
            "Medication side effects and interactions",
            "Weight loss strategies and nutrition",
        ]
        
        print(f"\nKnowledge Base Stats:")
        print(f"  Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  Total sources: {stats.get('total_sources', 0)}")
        
        print(f"\nTesting {len(test_queries)} queries...\n")
        
        for query in test_queries:
            results = retrieve(query, n_results=2)
            print(f"Q: {query}")
            if results:
                for i, result in enumerate(results, 1):
                    source = result.get('source', 'Unknown')[:40]
                    score = result.get('score', 0)
                    text = result.get('text', '')[:100]
                    print(f"  {i}. [{score:.2f}] {source}: {text}...")
            else:
                print("  ❌ No results found")
            print()
        
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"❌ Test error: {e}")


def show_stats():
    """Show knowledge base statistics."""
    print("\n" + "="*70)
    print("📊 KNOWLEDGE BASE STATISTICS")
    print("="*70 + "\n")
    
    try:
        from backend.rag.vector_store import get_collection_stats
        
        stats = get_collection_stats()
        print(f"Total chunks indexed: {stats.get('total_chunks', 0)}")
        print(f"Total sources: {stats.get('total_sources', 0)}")
        print(f"Collection name: healthcare_knowledge")
        
        if 'top_sources' in stats:
            print(f"\nTop sources by chunk count:")
            for source, count in stats.get('top_sources', [])[:5]:
                print(f"  • {source}: {count} chunks")
        
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"❌ Stats error: {e}")


# ============================================
# MAIN ENTRY POINT
# ============================================

def main():
    parser = argparse.ArgumentParser(description="ML Model Data Training Pipeline")
    parser.add_argument(
        "--mode",
        choices=["ingest", "test", "stats"],
        default="ingest",
        help="Training mode: ingest (process), test, or stats"
    )
    
    args = parser.parse_args()
    
    print("\n🚀 HEALTH CARE AI - DATA TRAINING PIPELINE")
    print("=========================================\n")
    
    try:
        if args.mode == "ingest":
            print("Step 1: Ingesting documents into vector store...")
            ingest_documents()
            print("Step 2: Testing retrieval...")
            test_retrieval()
        
        elif args.mode == "test":
            test_retrieval()
        
        elif args.mode == "stats":
            show_stats()
        
        print("✅ TRAINING COMPLETE!\n")
        
    except KeyboardInterrupt:
        print("\n⚠️ Training interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
