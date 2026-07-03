import asyncio
from uuid import UUID
from backend.database.connection import init_db, async_session_factory
from backend.database.repositories.scheme_repository import SchemeRepository
from backend.utils.sanitizer import clean_text

async def test():
    await init_db()
    async with async_session_factory() as session:
        repo = SchemeRepository(session)
        schemes = await repo.list_all()
        for idx, s in enumerate(schemes):
            print(f"{idx+1}. Name: {s.name} | Category: {s.category} | State: {s.state}")

if __name__ == "__main__":
    asyncio.run(test())
