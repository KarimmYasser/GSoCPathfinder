"""Node 2B: Semantic search using Qdrant vector store."""

from langchain_core.runnables import RunnableConfig
from agent.state import AgentState
from vector.searcher import VectorSearcher
from llm.client import get_llm_client
from qdrant_client import AsyncQdrantClient
from config.settings import get_settings

async def vector_search_node(state: AgentState, config: RunnableConfig = None) -> dict:
    """Searches Qdrant using the raw CV text for semantic similarity."""
    print("Agent Node: Performing Semantic Vector Search...")
    callback = config.get("configurable", {}).get("progress_callback") if config else None
    if callback:
        await callback("info", "Querying Qdrant Vector Store...")
    
    cv_text = state["raw_cv_text"]
    if not cv_text:
        return {"vector_results": []}
        
    settings = get_settings()
    llm_client = get_llm_client()
    qdrant_client = AsyncQdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)
    
    searcher = VectorSearcher(qdrant_client, llm_client)
    limit = settings.top_n_results * 5
    
    results = await searcher.search_organizations(cv_text, limit=limit)
    print(f"   Vector search returned {len(results)} candidate organizations.")
    if callback:
        await callback("info", f"Vector search complete. Found {len(results)} candidate organizations.")
    
    return {"vector_results": results}
