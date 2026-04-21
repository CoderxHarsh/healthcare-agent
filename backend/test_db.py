"""
Database Connection Test
========================
Verifies successful connection to PostgreSQL database.
Quick validation that DATABASE_URL is configured correctly.

Run from: python test_db.py
"""

# asyncio - Async runtime for async database operations
import asyncio
# Database engine - SQLAlchemy async engine for PostgreSQL
from .database import engine

async def test():
    """Test connection to PostgreSQL database"""
    async with engine.connect() as conn:
        print("✅ Connected to Neon PostgreSQL successfully!")

asyncio.run(test())
