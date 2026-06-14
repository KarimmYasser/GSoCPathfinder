"""Neo4j schema definitions: Constraints and Indexes."""

from graph.client import Neo4jClient


async def setup_schema(client: Neo4jClient):
    """Create all necessary constraints and indexes."""

    statements = [
        # Constraints (ensure uniqueness and fast lookup)
        "CREATE CONSTRAINT IF NOT EXISTS FOR (o:Organization) REQUIRE o.canonical_name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (op:OrgProfile) REQUIRE op.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Project) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (top:Topic) REQUIRE top.name IS UNIQUE",
        # Indexes (fast text search)
        "CREATE INDEX IF NOT EXISTS FOR (o:Organization) ON (o.aliases)",
        "CREATE INDEX IF NOT EXISTS FOR (p:Project) ON (p.title)",
    ]

    print("Setting up Neo4j schema...")
    for statement in statements:
        try:
            await client.execute_query(statement)
            print(f"Executed: {statement.split('FOR')[0] if 'FOR' in statement else statement}")
        except Exception as e:
            print(f"Warning on schema setup: {e}")

    print("Schema setup complete.")
