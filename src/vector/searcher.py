"""Vector search operations for the agent."""

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from llm.client import LLMClient
from vector.collections import VectorCollections


class VectorSearcher:
    """Performs semantic search against Qdrant collections."""

    def __init__(self, client: AsyncQdrantClient, llm_client: LLMClient):
        self.client = client
        self.llm_client = llm_client

    async def search_organizations(
        self, query: str, limit: int = 10, required_years: list[int] | None = None
    ) -> list[dict]:
        """Search for organizations semantically similar to the query (CV text)."""

        # Embed the query
        query_vector = await self.llm_client.get_single_embedding(query)

        # Build filter if required_years provided
        query_filter = None
        if required_years:
            # Match any of the required years
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="years_active", match=models.MatchAny(any=required_years)
                    )
                ]
            )

        # Search
        response = await self.client.query_points(
            collection_name=VectorCollections.ORG_COLLECTION,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

        # Format results
        formatted_results = []
        for scored_point in response.points:
            data = scored_point.payload.copy()
            data["similarity_score"] = scored_point.score
            formatted_results.append(data)

        return formatted_results

    async def search_projects(
        self, query: str, limit: int = 10, org_name: str | None = None
    ) -> list[dict]:
        """Search for specific projects."""
        query_vector = await self.llm_client.get_single_embedding(query)

        query_filter = None
        if org_name:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="org_canonical_name", match=models.MatchValue(value=org_name)
                    )
                ]
            )

        response = await self.client.query_points(
            collection_name=VectorCollections.PROJECT_COLLECTION,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
        )

        formatted_results = []
        for scored_point in response.points:
            data = scored_point.payload.copy()
            data["similarity_score"] = scored_point.score
            formatted_results.append(data)

        return formatted_results
