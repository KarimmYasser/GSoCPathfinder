"""Node 3: Merge signals, score, and rank organizations."""

from langchain_core.runnables import RunnableConfig
from agent.state import AgentState
from scoring.ranker import MatchingEngine
from config.settings import get_settings

async def merger_node(state: AgentState, config: RunnableConfig = None) -> dict:
    """Merges graph and vector results, applying the 7 scoring factors."""
    print("Agent Node: Merging signals and ranking candidates...")
    callback = config.get("configurable", {}).get("progress_callback") if config else None
    if callback:
        await callback("info", "Merging vector/graph search signals and scoring candidates...")
    
    user_profile = state["user_profile"]
    graph_results = state["graph_results"]
    vector_results = state["vector_results"]
    
    if not user_profile:
        print("   No user profile. Skipping ranking.")
        return {"ranked_organizations": []}
        
    engine = MatchingEngine()
    
    # Ranks all merged organizations and sets f1-f6 scores
    ranked_orgs = engine.rank_organizations(
        user_profile, 
        vector_results, 
        graph_results
    )
    
    settings = get_settings()
    
    # We only keep the Top N for the final LLM explanation phase
    # (LLM calls are expensive, so we only explain the best ones)
    top_orgs = ranked_orgs[:settings.top_n_results]
    
    print(f"   Ranked {len(ranked_orgs)} total organizations. Keeping top {len(top_orgs)}.")
    if callback:
        await callback("info", f"Signal merging complete. Ranked {len(ranked_orgs)} total organizations. Evaluating top {len(top_orgs)} matches.")
    
    return {"ranked_organizations": top_orgs}
