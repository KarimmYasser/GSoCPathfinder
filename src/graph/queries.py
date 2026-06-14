"""Cypher queries for the LangGraph agent."""

from graph.client import Neo4jClient


class GraphQueries:
    """Library of Cypher queries for the matching engine."""

    def __init__(self, client: Neo4jClient):
        self.client = client

    async def find_orgs_by_skills(self, skills: list[str], limit: int = 20) -> list[dict]:
        """Find organizations that use the given technologies."""
        query = """
        UNWIND $skills AS skill
        MATCH (o:Organization)-[:HAS_PROFILE]->(op:OrgProfile)-[:USES]->(t:Technology)
        WHERE toLower(t.name) CONTAINS toLower(skill)
        
        WITH o, count(DISTINCT t) as matched_skills_count, collect(DISTINCT t.name) as matched_skills
        ORDER BY matched_skills_count DESC
        LIMIT $limit
        
        RETURN o.canonical_name AS canonical_name,
               o.description AS description,
               o.years_active AS years_active,
               matched_skills_count,
               matched_skills
        """
        return await self.client.execute_query(query, {"skills": skills, "limit": limit})

    async def find_orgs_by_topics(self, topics: list[str], limit: int = 20) -> list[dict]:
        """Find organizations focused on specific topics."""
        query = """
        UNWIND $topics AS topic_word
        MATCH (o:Organization)-[:HAS_PROFILE]->(op:OrgProfile)-[:FOCUSES_ON]->(t:Topic)
        WHERE toLower(t.name) CONTAINS toLower(topic_word)
        
        WITH o, count(DISTINCT t) as matched_topics_count, collect(DISTINCT t.name) as matched_topics
        ORDER BY matched_topics_count DESC
        LIMIT $limit
        
        RETURN o.canonical_name AS canonical_name,
               o.description AS description,
               o.years_active AS years_active,
               matched_topics_count,
               matched_topics
        """
        return await self.client.execute_query(query, {"topics": topics, "limit": limit})

    async def get_org_details(self, canonical_name: str) -> dict | None:
        """Get full details for an organization, including its most recent profile."""
        query = """
        MATCH (o:Organization {canonical_name: $name})
        OPTIONAL MATCH (o)-[:HAS_PROFILE]->(op:OrgProfile)
        WITH o, op ORDER BY op.year DESC
        WITH o, collect(op) AS profiles
        
        LET latest = profiles[0]
        
        OPTIONAL MATCH (latest)-[:USES]->(t:Technology)
        WITH o, latest, profiles, collect(t.name) AS technologies
        
        OPTIONAL MATCH (latest)-[:FOCUSES_ON]->(top:Topic)
        WITH o, latest, profiles, technologies, collect(top.name) AS topics
        
        RETURN o.canonical_name AS canonical_name,
               o.description AS description,
               o.url AS url,
               o.years_active AS years_active,
               latest.num_projects AS recent_projects,
               technologies,
               topics
        """
        results = await self.client.execute_query(query, {"name": canonical_name})
        return results[0] if results else None
