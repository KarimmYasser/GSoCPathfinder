"""Node 4: Generate natural language explanations and finalize scores."""

from langchain_core.messages import HumanMessage

from agent.state import AgentState
from llm.client import get_llm_client
from llm.prompts import EXPLANATION_PROMPT
from scoring.factors import ScoringFactors
from scoring.weights import load_weights
from models import MatchResult

async def explainer_node(state: AgentState) -> dict:
    """Generates explanations for the top ranked organizations and adds Factor 7."""
    print("Agent Node: Generating LLM explanations for top matches...")
    
    orgs = state["ranked_organizations"]
    profile = state["user_profile"]
    
    if not orgs or not profile:
        return {"match_result": None}
        
    client = get_llm_client()
    weights = load_weights()
    
    user_summary = f"{profile.experience_level} developer with skills in {', '.join(profile.skills)}. Interests: {', '.join(profile.topics_of_interest)}"
    
    for org in orgs:
        prompt = EXPLANATION_PROMPT.format(
            user_summary=user_summary,
            matched_skills=", ".join(org.matched_technologies),
            matched_topics=", ".join(org.matched_topics),
            org_name=org.canonical_name,
            org_description=org.description
        )
        
        try:
            response = await client.chat_model.ainvoke([HumanMessage(content=prompt)])
            explanation = response.content.strip()
            org.explanation = explanation
            
            # For this prototype, we simulate the LLM relevance score from 1-10 
            # based on how many skills/topics matched, since extracting a hard number 
            # out of the LLM along with the text requires structured output parsing.
            # Ideally, this would be a separate LLM call or a parallel tool call.
            llm_score_raw = min(10, 5 + len(org.matched_technologies) + len(org.matched_topics))
            org.score.llm_relevance = ScoringFactors.f7_llm_relevance(llm_score_raw)
            
            # Recalculate total with LLM score included
            org.score.total += (org.score.llm_relevance * weights.llm_relevance)
            
        except Exception as e:
            print(f"   Warning: Failed to generate explanation for {org.canonical_name}. Error: {e}")
            org.explanation = "Matched based on algorithm, but AI explanation generation failed."
            org.score.llm_relevance = 0.0

    # Re-sort just in case Factor 7 changed the top order
    orgs.sort(key=lambda x: x.score.total, reverse=True)
    
    # Update ranks
    for i, org in enumerate(orgs):
        org.rank = i + 1
        
    # Serialize final result
    result = MatchResult(
        user_profile=profile,
        rankings=orgs,
        total_orgs_evaluated=len(orgs),
        weights_used=weights.model_dump()
    )
    
    return {
        "ranked_organizations": orgs,
        "match_result": result.model_dump()
    }
