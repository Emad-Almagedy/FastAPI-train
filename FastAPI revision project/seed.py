import asyncio
from database import AsyncSessionLocal
import models
from auth import hash_password


async def create_admin():
    async with AsyncSessionLocal() as db:

        admin = models.User(
            username="admin",
            email="admin@example.com",
            hashed_password=hash_password("admin123"),
            is_admin=True
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        print("✅ Admin created successfully")


if __name__ == "__main__":
    asyncio.run(create_admin())