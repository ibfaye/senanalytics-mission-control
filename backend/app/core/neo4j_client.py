"""
Neo4j Knowledge Graph Driver — real connection to the Neo4j graph database.
Replaces the in-memory KnowledgeGraph with persistent Neo4j storage.
"""

import logging
from typing import Optional, Any
from app.config import settings

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase, Driver
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    logger.warning("neo4j not installed. Install with: pip install neo4j")


class Neo4jConnection:
    """Neo4j driver wrapper with query helpers."""

    def __init__(self):
        self.driver: Optional[Driver] = None

    async def connect(self):
        """Create Neo4j driver connection."""
        if not NEO4J_AVAILABLE:
            logger.warning("[Neo4j] Driver not installed — using in-memory fallback")
            return

        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            # Verify connection
            self.driver.verify_connectivity()
            logger.info(f"[Neo4j] Connected to {settings.neo4j_uri}")
        except Exception as e:
            logger.error(f"[Neo4j] Connection failed: {e}")
            self.driver = None

    async def disconnect(self):
        """Close the driver."""
        if self.driver:
            self.driver.close()
            logger.info("[Neo4j] Driver closed")

    def run(self, cypher: str, **params) -> list[dict]:
        """Execute a Cypher query and return results as dicts."""
        if not self.driver:
            return []
        with self.driver.session() as session:
            result = session.run(cypher, **params)
            return [dict(r) for r in result]

    def run_single(self, cypher: str, **params) -> Optional[dict]:
        """Execute a Cypher query and return a single result."""
        if not self.driver:
            return None
        with self.driver.session() as session:
            result = session.run(cypher, **params)
            record = result.single()
            return dict(record) if record else None

    def execute(self, cypher: str, **params) -> Any:
        """Execute a Cypher statement (CREATE/MERGE/DELETE)."""
        if not self.driver:
            return None
        with self.driver.session() as session:
            return session.run(cypher, **params).consume()

    @property
    def is_connected(self) -> bool:
        return self.driver is not None


# Singleton
neo4j = Neo4jConnection()
