# tests/conftest.py

import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from backend.infrastructure.persistence.models.base import BaseORM

@pytest_asyncio.fixture(scope="function")
async def engine() -> AsyncEngine:
    dsn = os.getenv("POSTGRES_DSN", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")
    engine = create_async_engine(dsn, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(engine: AsyncEngine) -> AsyncSession:
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()
