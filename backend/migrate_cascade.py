"""
Migration: Add ON DELETE CASCADE to foreign keys
-------------------------------------------------
Fixes: "update or delete on table 'users' violates foreign key constraint 
        'medications_user_id_fkey' on table 'medications' (SQLSTATE 23503)"

Run once:  python migrate_cascade.py
"""
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Foreign keys that need CASCADE: (table, constraint_name, column, references)
FK_UPDATES = [
    ("health_logs",     "health_logs_user_id_fkey",       "user_id",       "users(id)"),
    ("medications",     "medications_user_id_fkey",       "user_id",       "users(id)"),
    ("medication_logs", "medication_logs_medication_id_fkey", "medication_id", "medications(id)"),
    ("medication_logs", "medication_logs_user_id_fkey",   "user_id",       "users(id)"),
]


async def migrate():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        for table, constraint, column, references in FK_UPDATES:
            print(f"  [FIX] {table}.{column} -> {references} ON DELETE CASCADE")
            # Drop existing constraint
            await conn.execute(text(
                f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}"
            ))
            # Re-add with CASCADE
            await conn.execute(text(
                f"ALTER TABLE {table} ADD CONSTRAINT {constraint} "
                f"FOREIGN KEY ({column}) REFERENCES {references} ON DELETE CASCADE"
            ))
    
    await engine.dispose()
    print("\n[OK] All foreign keys updated with ON DELETE CASCADE!")


if __name__ == "__main__":
    asyncio.run(migrate())
