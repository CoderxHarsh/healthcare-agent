import asyncio
import requests
from database import engine, Base

async def init_tables():
    """Create all tables in the database"""
    print("🔄 Creating database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    asyncio.run(init_tables())
