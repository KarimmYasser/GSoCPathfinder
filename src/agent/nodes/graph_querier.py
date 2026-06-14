"""Node 2A: Query Neo4j for exact skill and topic matches."""

from langchain_core.runnables import RunnableConfig

from agent.state import AgentState
from config.settings import get_settings
from graph.client import get_neo4j_client
from graph.queries import GraphQueries


async def query_graph_node(state: AgentState, config: RunnableConfig = None) -> dict:
    """Queries Neo4j based on the extracted user profile."""
    print("Agent Node: Querying Knowledge Graph...")
    callback = config.get("configurable", {}).get("progress_callback") if config else None
    if callback:
        await callback("info", "Querying Neo4j Knowledge Graph...")

    profile = state["user_profile"]
    if not profile:
        return {"graph_results": []}

    settings = get_settings()
    client = await get_neo4j_client()
    queries = GraphQueries(client)
    # We fetch many candidates (e.g. 100) from the DB so that specialized orgs
    # (like API Dash with fewer total skills) aren't pushed out by generic orgs
    # (that happen to match many generic skills like Python/Java) before Jaccard
    # scoring can properly weigh them.
    limit = settings.top_n_results * 10
    # We query by both skills and topics, then merge results
    skill_results = []
    if profile.skills:
        skill_results = await queries.find_orgs_by_skills(profile.skills, limit=limit)

    topic_results = []
    if profile.topics_of_interest:
        topic_results = await queries.find_orgs_by_topics(profile.topics_of_interest, limit=limit)

    # Merge them into a single list of unique orgs with aggregated match counts
    org_map = {}

    for r in skill_results:
        name = r["canonical_name"]
        org_map[name] = r
        org_map[name]["matched_topics"] = []
        org_map[name]["matched_topics_count"] = 0

    for r in topic_results:
        name = r["canonical_name"]
        if name in org_map:
            org_map[name]["matched_topics"] = r["matched_topics"]
            org_map[name]["matched_topics_count"] = r["matched_topics_count"]
        else:
            org_map[name] = r
            org_map[name]["matched_skills"] = []
            org_map[name]["matched_skills_count"] = 0

    results = list(org_map.values())
    print(f"   Graph returned {len(results)} candidate organizations.")
    if callback:
        await callback(
            "info", f"Graph query complete. Found {len(results)} candidate organizations."
        )

    return {"graph_results": results}
