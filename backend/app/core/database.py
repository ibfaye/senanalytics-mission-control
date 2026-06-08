"""
PostgreSQL Database Layer — asyncpg connection pool with query helpers.
Replaces in-memory stores with persistent PostgreSQL storage.
"""

import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Try to import asyncpg; fall back gracefully if not installed
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logger.warning("asyncpg not installed. Install with: pip install asyncpg")


class Database:
    """Async PostgreSQL connection pool."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Create connection pool."""
        if not ASYNCPG_AVAILABLE:
            logger.warning("[DB] asyncpg not available — using in-memory fallback")
            return

        try:
            self.pool = await asyncpg.create_pool(
                settings.database_url,
                min_size=2,
                max_size=10,
                command_timeout=30,
            )
            # Verify connection
            async with self.pool.acquire() as conn:
                version = await conn.fetchval("SELECT version()")
            logger.info(f"[DB] Connected to PostgreSQL: {version[:50]}...")
        except Exception as e:
            logger.error(f"[DB] PostgreSQL connection failed: {e}")
            self.pool = None

    async def disconnect(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("[DB] PostgreSQL pool closed")

    # ── Query helpers ──

    async def fetch(self, query: str, *args) -> list[dict]:
        """Execute a SELECT query and return rows as dicts."""
        if not self.pool:
            return []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(r) for r in rows]

    async def fetchrow(self, query: str, *args) -> Optional[dict]:
        """Execute a SELECT query and return a single row."""
        if not self.pool:
            return None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

    async def execute(self, query: str, *args) -> str:
        """Execute an INSERT/UPDATE/DELETE and return status."""
        if not self.pool:
            return "no_connection"
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *args)
            return result

    async def fetchval(self, query: str, *args) -> Any:
        """Execute a query and return a single value."""
        if not self.pool:
            return None
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    @property
    def is_connected(self) -> bool:
        return self.pool is not None


# Singleton
db = Database()
