"""Async Neo4j client for GSoC Pathfinder."""

from neo4j import AsyncDriver, AsyncGraphDatabase

from config.settings import get_settings


class Neo4jClient:
    """Async client for interacting with Neo4j."""

    def __init__(self):
        settings = get_settings()
        self.uri = settings.neo4j_uri
        self.user = settings.neo4j_user
        self.password = settings.neo4j_password
        self.driver: AsyncDriver | None = None

    async def connect(self):
        """Establish connection to Neo4j."""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connection
            await self.driver.verify_connectivity()

    async def close(self):
        """Close the database connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None

    async def execute_query(self, query: str, parameters: dict | None = None):
        """Execute a single query and return results."""
        if not self.driver:
            await self.connect()

        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()

    async def execute_write(self, query: str, parameters: dict | None = None):
        """Execute a write transaction."""
        if not self.driver:
            await self.connect()

        async def work(tx):
            result = await tx.run(query, parameters or {})
            return await result.data()

        async with self.driver.session() as session:
            return await session.execute_write(work)


# Global singleton instance (initialized when needed)
_client: Neo4jClient | None = None


async def get_neo4j_client() -> Neo4jClient:
    """Get or create the global Neo4j client."""
    global _client
    if _client is None:
        _client = Neo4jClient()
        await _client.connect()
    return _client


async def close_neo4j_client():
    """Close the global Neo4j client."""
    global _client
    if _client is not None:
        await _client.close()
        _client = None
