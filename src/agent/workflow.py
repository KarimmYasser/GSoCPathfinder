"""LangGraph workflow definition for the Matching Agent."""

from langgraph.graph import END, START, StateGraph

from agent.nodes.explainer import explainer_node
from agent.nodes.extractor import extract_profile_node
from agent.nodes.graph_querier import query_graph_node
from agent.nodes.merger import merger_node
from agent.nodes.vector_searcher import vector_search_node
from agent.state import AgentState


def create_matching_workflow() -> StateGraph:
    """Build the LangGraph execution graph."""

    # Initialize the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("extractor", extract_profile_node)
    workflow.add_node("graph_querier", query_graph_node)
    workflow.add_node("vector_searcher", vector_search_node)
    workflow.add_node("merger", merger_node)
    workflow.add_node("explainer", explainer_node)

    # Define edges
    # START -> extractor
    workflow.add_edge(START, "extractor")

    # extractor -> parallel (graph_querier, vector_searcher)
    workflow.add_edge("extractor", "graph_querier")
    workflow.add_edge("extractor", "vector_searcher")

    # parallel (graph, vector) -> merger
    # Both must finish before merger starts
    workflow.add_edge(["graph_querier", "vector_searcher"], "merger")

    # merger -> explainer
    workflow.add_edge("merger", "explainer")

    # explainer -> END
    workflow.add_edge("explainer", END)

    return workflow.compile()
