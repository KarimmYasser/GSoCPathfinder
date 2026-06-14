"""Qdrant collection schemas and initialization."""

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from config.settings import get_settings


class VectorCollections:
    """Manages Qdrant collections."""

    ORG_COLLECTION = "gsoc_organizations"
    PROJECT_COLLECTION = "gsoc_projects"

    def __init__(self, client: AsyncQdrantClient):
        self.client = client
        self.settings = get_settings()

    async def setup_collections(self):
        """Create Qdrant collections if they don't exist."""
        collections = await self.client.get_collections()
        existing = [c.name for c in collections.collections]

        dim = self.settings.embed_dimension

        if self.ORG_COLLECTION not in existing:
            print(f"Creating collection: {self.ORG_COLLECTION}")
            await self.client.create_collection(
                collection_name=self.ORG_COLLECTION,
                vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )
            # Create payload index for fast filtering
            await self.client.create_payload_index(
                collection_name=self.ORG_COLLECTION,
                field_name="years_active",
                field_schema=models.PayloadSchemaType.INTEGER,
            )

        if self.PROJECT_COLLECTION not in existing:
            print(f"Creating collection: {self.PROJECT_COLLECTION}")
            await self.client.create_collection(
                collection_name=self.PROJECT_COLLECTION,
                vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )
            # Payload indices
            await self.client.create_payload_index(
                collection_name=self.PROJECT_COLLECTION,
                field_name="year",
                field_schema=models.PayloadSchemaType.INTEGER,
            )
            await self.client.create_payload_index(
                collection_name=self.PROJECT_COLLECTION,
                field_name="org_canonical_name",
                field_schema=models.PayloadSchemaType.KEYWORD,
            )

        print("Vector collections setup complete.")
