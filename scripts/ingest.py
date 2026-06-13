"""Full data ingestion CLI for Neo4j and Qdrant."""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from ingestion.parser import parse_directory
from ingestion.normalizer import DataNormalizer
from ingestion.validator import DataValidator
from ingestion.neo4j_loader import Neo4jLoader
from ingestion.qdrant_loader import QdrantLoader
from graph.client import get_neo4j_client, close_neo4j_client
from graph.schema import setup_schema
from vector.collections import VectorCollections
from llm.client import get_llm_client
from qdrant_client import AsyncQdrantClient
from config.settings import get_settings

async def main():
    print("=== GSoC Pathfinder Data Ingestion ===")
    
    settings = get_settings()
    data_dir = Path(__file__).parent.parent / "Data"
    config_dir = src_dir / "config"
    
    print("\n1. Parsing and Normalizing JSON Data...")
    raw_years = parse_directory(data_dir)
    normalizer = DataNormalizer(config_dir)
    validator = DataValidator()
    
    # Collect all projects across years
    all_projects = []
    for year_data in raw_years:
        profiles = normalizer.process_year_data(year_data)
        validator.add_profiles(profiles)
        for p in profiles:
            all_projects.extend(p.projects)
            
    organizations = validator.get_organizations()
    print(f"   Prepared {len(organizations)} unique organizations for ingestion.")
    print(f"   Prepared {len(all_projects)} projects for vector embeddings.")
    
    print("\n2. Initializing Neo4j and Qdrant Connections...")
    try:
        neo4j_client = await get_neo4j_client()
        qdrant_client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
        llm_client = get_llm_client()
    except Exception as e:
        print(f"\n[!] Failed to connect to databases. Is Docker running?")
        print(f"Error: {e}")
        return
        
    print("\n3. Setting up Schemas...")
    await setup_schema(neo4j_client)
    
    vector_collections = VectorCollections(qdrant_client)
    await vector_collections.setup_collections()
    
    print("\n4. Loading Data into Neo4j (Graph)...")
    graph_loader = Neo4jLoader(neo4j_client)
    await graph_loader.load_organizations(organizations)
    
    print("\n5. Loading Data into Qdrant (Vector Store)...")
    print("   (This will take time as it requests embeddings from the LLM)")
    vector_loader = QdrantLoader(qdrant_client, llm_client)
    await vector_loader.load_organizations(organizations)
    await vector_loader.load_projects(all_projects)
    
    # Close connection
    await close_neo4j_client()
    print("\n=== Ingestion Complete! ===")

if __name__ == "__main__":
    asyncio.run(main())
