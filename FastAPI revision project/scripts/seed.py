import asyncio
from core import AsyncSessionLocal, hash_password
import models


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