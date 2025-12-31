from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Transform database URL for async driver if needed
# Railway and some providers use postgresql:// which loads psycopg2 (sync)
# We need postgresql+asyncpg:// for async SQLAlchemy
database_url = settings.database_url
if database_url.startswith("postgresql://") and not database_url.startswith("postgresql+asyncpg://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    logger.info("Transformed database URL to use asyncpg driver")
elif database_url.startswith("postgresql+asyncpg://"):
    logger.debug("Database URL already uses asyncpg driver")
else:
    logger.debug(f"Database URL scheme: {database_url.split('://')[0] if '://' in database_url else 'unknown'}")

# Create async engine with proper pool settings
engine = create_async_engine(
    database_url,
    echo=settings.environment == "development",
    future=True,
    # Connection pool settings
    pool_size=10,  # Number of connections to maintain in the pool
    max_overflow=20,  # Additional connections beyond pool_size
    pool_pre_ping=True,  # Test connections before using them (handles stale connections)
    pool_recycle=3600,  # Recycle connections after 1 hour (prevents stale connections)
    pool_timeout=30,  # Timeout for getting connection from pool
    # Use NullPool for SQLite, regular pool for PostgreSQL
    poolclass=None if "postgresql" in database_url.lower() else NullPool,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.
    
    Note: In production, use Alembic migrations instead of this function.
    This is useful for development/testing or initial setup.
    """
    try:
        # Import all models to ensure they're registered with Base
        from app.database import models  # noqa: F401
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

