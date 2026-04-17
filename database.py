from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,          # Neon has connection limits on free tier (5 simultaneous connections)
    max_overflow=2,       # Allow up to 2 extra connections beyond pool_size if needed (5+2=7 max)
    pool_timeout=30,      # Wait up to 30s for a connection from the pool
    pool_recycle=300,     # Recycle connections every 5 min — matches Neon's idle timeout
    pool_pre_ping=True,   # Test connection health before use; auto-reconnects closed/stale connections
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def disconnect_db():
    await engine.dispose()
    print("✅ Database disconnected successfully")