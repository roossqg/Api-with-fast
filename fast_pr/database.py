from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fast_pr.settings import Settings
import os

DATABASE_URL = Settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
