"""Agent state definitions for LangGraph."""

from typing import TypedDict

from models import RankedOrganization, UserProfile


class AgentState(TypedDict, total=False):
    """The state passed between LangGraph nodes."""

    # Input
    raw_cv_text: str
    advanced: bool
    ultra: bool

    # Intermediate State
    user_profile: UserProfile | None
    graph_results: list[dict]
    vector_results: list[dict]

    # Final Output
    ranked_organizations: list[RankedOrganization]
    global_score_min: float  # Min score across ALL evaluated orgs (not just top-N)
    global_score_max: float  # Max score across ALL evaluated orgs
    match_result: dict | None  # The final MatchResult serialized
