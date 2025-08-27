"""
Simple database connection management for PostgreSQL.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from app.core.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
)

# Create session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables and seed with default data"""
    from app.database.models import Base
    from app.database.seed import seed_database
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed database with default user
    async with AsyncSessionLocal() as session:
        try:
            await seed_database(session)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise


async def close_db():
    """Close database engine"""
    await engine.dispose()