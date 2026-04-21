"""
Database Initialization Script
==============================
Creates all database tables defined in models.py.
Run once on initial setup to initialize the PostgreSQL database schema.
"""

# asyncio - Async runtime for running async database operations
import asyncio
# requests - HTTP client (imported but may be unused)
import requests
# Database engine and models - For table creation
from .database import engine, Base

async def init_tables():
    """Create all SQLAlchemy ORM model tables in PostgreSQL"""
    print("🔄 Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    asyncio.run(init_tables())
