from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from models import User
from sqlalchemy.sql import func

async def upsert_user(db: AsyncSession, google_sub: str, email: str, name: str, picture: str) -> User:
    # Upsert: insert or update last_login_at if user already exists
    stmt = insert(User).values(
        google_sub=google_sub,
        email=email,
        name=name,
        profile_picture_url=picture,
    ).on_conflict_do_update(
        index_elements=["google_sub"],
        set_={"last_login_at": func.now(), "email": email, "name": name, "profile_picture_url": picture}
    )
    #Execute the statement asynchronously
    await db.execute(stmt)
    #Commit the transaction to save it to the database
    await db.commit()

    # Fetch and return the user
    result = await db.execute(select(User).where(User.google_sub == google_sub))
    return result.scalar_one()