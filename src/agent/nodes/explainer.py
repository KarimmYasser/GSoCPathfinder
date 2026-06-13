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
    is_advanced = state.get("advanced", False)
    
    if not orgs or not profile:
        return {"match_result": None}
        
    client = get_llm_client()
    weights = load_weights()
    
    # We will need the Neo4j client to fetch projects if in advanced mode
    client_neo4j = None
    if is_advanced:
        try:
            from graph.client import get_neo4j_client
            client_neo4j = await get_neo4j_client()
        except Exception as e:
            print(f"   [Advanced Mode] Failed to load Neo4j client: {e}")
    
    user_summary = f"{profile.experience_level} developer with skills in {', '.join(profile.skills)}. Interests: {', '.join(profile.topics_of_interest)}"
    
    for org in orgs:
        # Advanced Mode: Fetch GSoC project context from Neo4j
        project_list_str = ""
        if is_advanced and client_neo4j:
            try:
                project_query = """
                MATCH (o:Organization)-[:HAS_PROFILE]->(y:YearProfile)-[:ACCEPTED_PROJECT]->(p:Project)
                WHERE o.canonical_name = $org_name
                RETURN p.title AS title, p.description AS description
                LIMIT 5
                """
                records = await client_neo4j.execute_query(project_query, {"org_name": org.canonical_name})
                if records:
                    project_list_str = "\n".join([f"- Project: {r['title']}\n  Description: {r['description']}" for r in records])
            except Exception as e:
                print(f"   [Advanced Mode] Warning: Failed to query projects for {org.canonical_name}: {e}")

        if is_advanced and project_list_str:
            print(f"   [Advanced Mode] Running deep reasoning matching and project alignment for {org.canonical_name}...")
            prompt = f"""
You are an expert GSoC mentor for the organization '{org.canonical_name}'.
You are evaluating a student with the following profile:
- Experience Level: {profile.experience_level}
- Extracted Skills: {', '.join(profile.skills)}
- Interests/Topics: {', '.join(profile.topics_of_interest)}

Here is a list of recent GSoC projects accepted by '{org.canonical_name}':
{project_list_str}

Please perform a deep, high-reasoning match analysis:
1. Identify the single best-matching project from the list above for this student. If none match well, state why.
2. Write a detailed matching narrative (2-3 paragraphs) explaining why they are a strong candidate, pointing out how their skills overlap with the recommended project.
3. Perform a gap analysis: list the exact programming languages, tools, or concepts they still need to learn or master to be fully competitive for this organization.
4. Provide a critique of this match: what are the potential risks or weaknesses in their application?
5. Assign a final match score on a scale from 0 to 100 on how suitable this candidate is (0 = completely incompatible, 100 = perfect match).

Format your output exactly as follows (use these headers):

### MATCH JUSTIFICATION
[Your detailed narrative paragraphs here...]

### RECOMMENDED CONTRIBUTOR PROJECT
- **Project Title:** [Title of the best matched project]
- **Alignment:** [Why this project fits their skills...]

### RECOMMENDATION SCORE
[A single integer number between 0 and 100, e.g. 85]
"""
        else:
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
            
            # Extract recommendation score if in advanced mode
            llm_score_raw = None
            if is_advanced and "### RECOMMENDATION SCORE" in explanation:
                parts = explanation.split("### RECOMMENDATION SCORE")
                explanation_body = parts[0].strip()
                score_str = parts[1].strip()
                
                # Parse the score number
                import re
                match = re.search(r'\b\d{1,3}\b', score_str)
                if match:
                    val = int(match.group())
                    llm_score_raw = min(10.0, max(0.0, val / 10.0))
                    print(f"   [Advanced Mode] Parsed LLM recommendation score: {val}/100 ({llm_score_raw:.2f}/10)")
                
                org.explanation = explanation_body
            else:
                org.explanation = explanation
            
            if llm_score_raw is None:
                llm_score_raw = min(10, 5 + len(org.matched_technologies) + len(org.matched_topics))
                
            org.score.llm_relevance = ScoringFactors.f7_llm_relevance(llm_score_raw)
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
