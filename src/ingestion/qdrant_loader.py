"""Qdrant loader for bulk embedding and upserting."""

import uuid

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from config.settings import get_settings
from llm.client import LLMClient
from models import NormalizedOrganization, NormalizedProject
from vector.collections import VectorCollections


class QdrantLoader:
    """Handles embedding and upserting data into Qdrant."""

    def __init__(self, client: AsyncQdrantClient, llm_client: LLMClient):
        self.client = client
        self.llm_client = llm_client
        self.settings = get_settings()

    def _generate_uuid(self, string_id: str) -> str:
        """Qdrant requires UUIDs or integers for point IDs."""
        import hashlib

        m = hashlib.md5()
        m.update(string_id.encode("utf-8"))
        return str(uuid.UUID(m.hexdigest()))

    async def load_organizations(self, organizations: list[NormalizedOrganization]):
        """Embed and load organization profiles."""
        print(f"Embedding and loading {len(organizations)} organizations into Qdrant...")

        batch_size = self.settings.embed_batch_size

        for i in range(0, len(organizations), batch_size):
            batch = organizations[i : i + batch_size]

            # Prepare texts to embed
            # We embed a rich representation of the organization's latest profile
            texts = []
            for org in batch:
                latest = org.profiles[-1]
                techs = ", ".join(latest.technologies)
                topics = ", ".join(latest.topics)
                text = f"Organization: {org.canonical_name}\n"
                text += f"Description: {org.description}\n"
                text += f"Technologies: {techs}\n"
                text += f"Topics: {topics}\n"
                texts.append(text)

            # Get embeddings
            embeddings = await self.llm_client.get_embeddings(texts)

            # Prepare points
            points = []
            for org, vector in zip(batch, embeddings):
                latest = org.profiles[-1]
                point_id = self._generate_uuid(f"org_{org.canonical_name}")

                payload = {
                    "canonical_name": org.canonical_name,
                    "description": org.description,
                    "url": org.url,
                    "image_url": org.image_url,
                    "years_active": org.years_active,
                    "technologies": latest.technologies,
                    "topics": latest.topics,
                    "total_projects": org.total_projects,
                }

                points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))

            # Upsert batch
            await self.client.upsert(
                collection_name=VectorCollections.ORG_COLLECTION, points=points
            )
            print(f"Loaded orgs {min(i + batch_size, len(organizations))} / {len(organizations)}")

    async def load_projects(self, projects: list[NormalizedProject]):
        """Embed and load projects."""
        print(f"Embedding and loading {len(projects)} projects into Qdrant...")

        batch_size = self.settings.embed_batch_size

        for i in range(0, len(projects), batch_size):
            batch = projects[i : i + batch_size]

            texts = []
            for proj in batch:
                techs = ", ".join(proj.technologies)
                text = f"Project: {proj.title}\n"
                text += f"Organization: {proj.org_canonical_name}\n"
                text += f"Technologies: {techs}\n"
                text += f"Description: {proj.description_clean}\n"
                texts.append(text)

            embeddings = await self.llm_client.get_embeddings(texts)

            points = []
            for proj, vector in zip(batch, embeddings):
                point_id = self._generate_uuid(f"proj_{proj.id}")

                payload = {
                    "project_id": proj.id,
                    "title": proj.title,
                    "org_canonical_name": proj.org_canonical_name,
                    "year": proj.year,
                    "technologies": proj.technologies,
                    "is_ongoing": proj.is_ongoing,
                }

                points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))

            await self.client.upsert(
                collection_name=VectorCollections.PROJECT_COLLECTION, points=points
            )
            print(f"Loaded projects {min(i + batch_size, len(projects))} / {len(projects)}")
