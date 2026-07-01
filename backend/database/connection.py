"""
LabhArth AI — Database Connection
===================================
Async SQLAlchemy engine and session factory for PostgreSQL (Neon).
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.utils.config import get_settings

settings = get_settings()

# Async engine — configured for Neon PostgreSQL
db_url = settings.database_url
connect_args = {}

# Clean sslmode from connection url and pass to asyncpg connect_args
if "sslmode=" in db_url:
    if "?sslmode=" in db_url:
        db_url = db_url.split("?sslmode=")[0]
    elif "&sslmode=" in db_url:
        parts = db_url.split("&")
        db_url = "&".join([p for p in parts if not p.startswith("sslmode=")])
    connect_args["ssl"] = True
elif "neon.tech" in db_url:
    # Force SSL for Neon hosts by default
    connect_args["ssl"] = True

# Disable prepared statement cache for compatibility with Neon connection pooler
connect_args["statement_cache_size"] = 0

engine = create_async_engine(
    db_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.app_debug,
    pool_pre_ping=True,
    connect_args=connect_args,
)

# Session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
    """
    Dependency that yields an async database session.
    Usage in FastAPI routes:
        session: AsyncSession = Depends(get_db_session)
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database — create tables if they don't exist."""
    from backend.models.db_models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database engine connections."""
    await engine.dispose()
