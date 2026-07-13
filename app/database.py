from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import AsyncGenerator
from app.config import get_settings


Base = declarative_base()


settings = get_settings()


def _get_engine():

    return create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10, 
    )


engine = _get_engine()


async def init_db():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,

    )

    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()