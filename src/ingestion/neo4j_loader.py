"""Load normalized data into Neo4j."""

import json
from models import NormalizedOrganization
from graph.client import Neo4jClient

class Neo4jLoader:
    """Handles bulk ingestion of organizations, profiles, and projects into Neo4j."""
    
    def __init__(self, client: Neo4jClient):
        self.client = client
        
    async def load_organizations(self, organizations: list[NormalizedOrganization]):
        """Load the full object graph into Neo4j."""
        print(f"Loading {len(organizations)} organizations into Neo4j...")
        
        # We will use UNWIND batches for performance
        batch_size = 50
        
        for i in range(0, len(organizations), batch_size):
            batch = organizations[i:i+batch_size]
            await self._load_batch(batch)
            print(f"Loaded {min(i+batch_size, len(organizations))} / {len(organizations)}")
            
    async def _load_batch(self, batch: list[NormalizedOrganization]):
        """Execute the Cypher queries for a single batch."""
        
        # Prepare data structures for UNWIND
        orgs_data = []
        profiles_data = []
        projects_data = []
        
        for org in batch:
            orgs_data.append({
                "canonical_name": org.canonical_name,
                "aliases": org.aliases,
                "description": org.description,
                "url": org.url,
                "image_url": org.image_url,
                "years_active": org.years_active,
            })
            
            for profile in org.profiles:
                profiles_data.append({
                    "id": profile.id,
                    "canonical_name": profile.canonical_name,
                    "year": profile.year,
                    "description": profile.description,
                    "url": profile.url,
                    "category": profile.category,
                    "num_projects": profile.num_projects,
                    "topics": profile.topics,
                    "technologies": profile.technologies
                })
                
                for proj in profile.projects:
                    projects_data.append({
                        "id": proj.id,
                        "title": proj.title,
                        "short_description": proj.short_description,
                        "description_clean": proj.description_clean,
                        "student_name": proj.student_name,
                        "year": proj.year,
                        "profile_id": profile.id,
                        "technologies": proj.technologies
                    })

        # 1. Merge Organizations
        org_query = """
        UNWIND $batch AS org
        MERGE (o:Organization {canonical_name: org.canonical_name})
        SET o.aliases = org.aliases,
            o.description = org.description,
            o.url = org.url,
            o.image_url = org.image_url,
            o.years_active = org.years_active
        """
        await self.client.execute_write(org_query, {"batch": orgs_data})
        
        # 2. Merge Profiles and Link to Organization
        profile_query = """
        UNWIND $batch AS p
        MERGE (op:OrgProfile {id: p.id})
        SET op.year = p.year,
            op.description = p.description,
            op.url = p.url,
            op.category = p.category,
            op.num_projects = p.num_projects
            
        WITH op, p
        MATCH (o:Organization {canonical_name: p.canonical_name})
        MERGE (o)-[:HAS_PROFILE]->(op)
        
        WITH op, p
        UNWIND p.topics AS topic_name
        MERGE (t:Topic {name: topic_name})
        MERGE (op)-[:FOCUSES_ON]->(t)
        
        WITH op, p
        UNWIND p.technologies AS tech_name
        MERGE (tech:Technology {name: tech_name})
        MERGE (op)-[:USES]->(tech)
        """
        await self.client.execute_write(profile_query, {"batch": profiles_data})
        
        # 3. Merge Projects and Link to Profile
        # We split projects into sub-batches if it gets too large
        proj_batch_size = 500
        for j in range(0, len(projects_data), proj_batch_size):
            p_batch = projects_data[j:j+proj_batch_size]
            project_query = """
            UNWIND $batch AS proj
            MERGE (p:Project {id: proj.id})
            SET p.title = proj.title,
                p.short_description = proj.short_description,
                p.description = proj.description_clean,
                p.student_name = proj.student_name,
                p.year = proj.year
                
            WITH p, proj
            MATCH (op:OrgProfile {id: proj.profile_id})
            MERGE (op)-[:SPONSORED]->(p)
            
            WITH p, proj
            UNWIND proj.technologies AS tech_name
            MERGE (tech:Technology {name: tech_name})
            MERGE (p)-[:USES]->(tech)
            """
            await self.client.execute_write(project_query, {"batch": p_batch})
