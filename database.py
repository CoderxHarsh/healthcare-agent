from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=5,          # Neon has connection limits on free tier 5 users can connect simultaneously
    max_overflow=2,       #allow up to 2 (5+2=7) additional connections beyond the pool_size if needed
    pool_timeout=30,      #8th user in line
    pool_recycle=1800,    # Recycle connections every 30 min
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