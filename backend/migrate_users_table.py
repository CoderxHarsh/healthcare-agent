"""
Database Migration: Add Onboarding Columns to Users Table
=========================================================
Adds health profile fields (age, weight, height, etc.) to users table.
Run once during database setup to add missing columns.

Usage: python migrate_users_table.py
"""

# asyncio - Async runtime for database operations
import asyncio
# asyncpg - PostgreSQL async driver for direct database access
import asyncpg
# os - Environment variable access
import os
# python-dotenv - Load .env configuration
from .dotenv import load_dotenv

async def migrate():
    """Add missing health profile columns to the users table"""
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set in .env")
        return
    
    # Parse connection string
    # postgresql+asyncpg://user:password@host/dbname?ssl=require
    print("🔄 Connecting to database...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://"))
        
        print("✅ Connected!")
        
        # List of missing columns to add
        migrations = [
            ("age", "INTEGER"),
            ("gender", "VARCHAR"),
            ("height_cm", "FLOAT"),
            ("weight_kg", "FLOAT"),
            ("health_conditions", "TEXT"),
            ("medications", "TEXT"),
            ("allergies", "TEXT"),
            ("fitness_level", "VARCHAR"),
            ("health_goals", "TEXT"),
            ("onboarded_at", "TIMESTAMP WITH TIME ZONE"),
        ]
        
        for column_name, column_type in migrations:
            try:
                query = f"ALTER TABLE users ADD COLUMN {column_name} {column_type};"
                print(f"🔄 Adding column: {column_name} ({column_type})...")
                await conn.execute(query)
                print(f"✅ Added: {column_name}")
            except asyncpg.exceptions.DuplicateColumnError:
                print(f"⏭️  Column already exists: {column_name}")
            except Exception as e:
                print(f"❌ Error adding {column_name}: {str(e)}")
        
        await conn.close()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(migrate())
