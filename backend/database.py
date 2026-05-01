"""
Database Configuration for HealthCare AI
=========================================
Manages async PostgreSQL connection pool, session management,
and ORM base configuration using SQLAlchemy 2.0.
"""

# SQLAlchemy async - Async database engine and session factory
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# SQLAlchemy ORM - Session management and base model
from sqlalchemy.orm import sessionmaker, DeclarativeBase
# os - Environment variable access for database URL
import os
# python-dotenv - Load .env configuration file
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Fix Neon + asyncpg SSL issue
# Strip query parameters from URL - asyncpg handles SSL via connect_args
if DATABASE_URL and "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

# Ensure correct protocol for asyncpg
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,          # Neon has connection limits on free tier (5 simultaneous connections)
    max_overflow=2,       # Allow up to 2 extra connections beyond pool_size if needed (5+2=7 max)
    pool_timeout=30,      # Wait up to 30s for a connection from the pool
    pool_recycle=300,     # Recycle connections every 5 min — matches Neon's idle timeout
    pool_pre_ping=True,   # Test connection health before use; auto-reconnects closed/stale connections
    connect_args={
        "ssl": True,      # For asyncpg: use True instead of "require"
        "timeout": 10,
        "command_timeout": 10,
    }
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models"""
    pass

async def get_db():
    """Dependency for FastAPI routes - provides database session to endpoints"""
    async with AsyncSessionLocal() as session:
        yield session

async def disconnect_db():
    """Close all database connections gracefully"""
    await engine.dispose()
    print("✅ Database disconnected successfully")