"""
Migration script to add medication-related tables and columns.
Run this once to update the database schema.

Usage: python migrate_medications.py
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# Convert SQLAlchemy URL to asyncpg format
ASYNCPG_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")


async def migrate():
    try:
        conn = await asyncpg.connect(ASYNCPG_URL)
        print("✅ Connected to database")

        # --- 1. Add google_refresh_token to users table ---
        token_migration = [
            ("google_refresh_token", "TEXT"),
        ]

        print("\n📦 Migrating users table...")
        for column_name, column_type in token_migration:
            try:
                query = f"ALTER TABLE users ADD COLUMN {column_name} {column_type};"
                await conn.execute(query)
                print(f"  ✅ Added: {column_name}")
            except asyncpg.exceptions.DuplicateColumnError:
                print(f"  ⏭️  Already exists: {column_name}")
            except Exception as e:
                print(f"  ❌ Error adding {column_name}: {str(e)}")

        # --- 2. Create medications table ---
        print("\n📦 Creating medications table...")
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS medications (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    name VARCHAR NOT NULL,
                    dosage VARCHAR,
                    frequency VARCHAR NOT NULL,
                    time_of_day VARCHAR,
                    start_date DATE,
                    end_date DATE,
                    notes TEXT,
                    gcal_event_id VARCHAR,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            print("  ✅ medications table created")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

        # --- 3. Create medication_logs table ---
        print("\n📦 Creating medication_logs table...")
        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS medication_logs (
                    id SERIAL PRIMARY KEY,
                    medication_id INTEGER NOT NULL REFERENCES medications(id),
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    scheduled_date DATE NOT NULL,
                    status VARCHAR NOT NULL,
                    logged_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            print("  ✅ medication_logs table created")
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")

        # --- 4. Create indexes for performance ---
        print("\n📦 Creating indexes...")
        indexes = [
            ("idx_medications_user_id", "medications", "user_id"),
            ("idx_medication_logs_user_id", "medication_logs", "user_id"),
            ("idx_medication_logs_med_id", "medication_logs", "medication_id"),
            ("idx_medication_logs_date", "medication_logs", "scheduled_date"),
        ]
        for idx_name, table, column in indexes:
            try:
                await conn.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column});")
                print(f"  ✅ Index: {idx_name}")
            except Exception as e:
                print(f"  ❌ Error creating {idx_name}: {str(e)}")

        await conn.close()
        print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"❌ Connection error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(migrate())
