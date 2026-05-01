import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()

url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg://", "postgresql://")

async def check():
    conn = await asyncpg.connect(url)
    rows = await conn.fetch("SELECT id, email, google_refresh_token FROM users")
    for r in rows:
        token = r["google_refresh_token"]
        if token:
            status = f"STORED ({len(token)} chars)"
        else:
            status = "NULL -- NEEDS RE-LOGIN"
        print(f"  User {r['id']}: {r['email']} -> {status}")
    await conn.close()

asyncio.run(check())
