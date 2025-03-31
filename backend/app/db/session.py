from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import settings
from app.core.exceptions import DatabaseError

# Create async engine with connection pooling
engine = create_async_engine(
    settings.get_database_url(),
    poolclass=AsyncAdaptedQueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.ENVIRONMENT == "development",
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise DatabaseError(f"Database error: {str(e)}")
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database."""
    try:
        # Create database tables
        from app.db.base import Base

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        raise DatabaseError(f"Failed to initialize database: {str(e)}")


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()
