from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.state import AgentState
from llm.client import get_llm_client
from llm.prompts import EXPLANATION_PROMPT
from scoring.factors import ScoringFactors
from scoring.weights import load_weights
from models import MatchResult

async def explainer_node(state: AgentState, config: RunnableConfig = None) -> dict:
    """Generates explanations for the top ranked organizations and adds Factor 7."""
    print("Agent Node: Generating LLM explanations for top matches...")
    callback = config.get("configurable", {}).get("progress_callback") if config else None
    if callback:
        await callback("info", "Generating AI justifications and recommendations...")
    
    orgs = state["ranked_organizations"]
    profile = state["user_profile"]
    is_advanced = state.get("advanced", False)
    is_ultra = state.get("ultra", False)
    
    if not orgs or not profile:
        return {"match_result": None}
        
    client = get_llm_client()
    weights = load_weights()
    
    # We will need the Neo4j client to fetch projects if in advanced or ultra mode
    client_neo4j = None
    if is_advanced or is_ultra:
        try:
            from graph.client import get_neo4j_client
            client_neo4j = await get_neo4j_client()
        except Exception as e:
            print(f"   [Advanced/Ultra Mode] Failed to load Neo4j client: {e}")
    
    user_summary = f"{profile.experience_level} developer with skills in {', '.join(profile.skills)}. Interests: {', '.join(profile.topics_of_interest)}"
    
    for org in orgs:
        # Advanced/Ultra Mode: Fetch GSoC project context from Neo4j
        project_list_str = ""
        if (is_advanced or is_ultra) and client_neo4j:
            try:
                project_query = """
                MATCH (o:Organization)-[:HAS_PROFILE]->(y:OrgProfile)-[:SPONSORED]->(p:Project)
                WHERE o.canonical_name = $org_name
                RETURN p.title AS title, p.description AS description
                LIMIT 5
                """
                records = await client_neo4j.execute_query(project_query, {"org_name": org.canonical_name})
                if records:
                    project_list_str = "\n".join([f"- Project: {r['title']}\n  Description: {r['description']}" for r in records])
            except Exception as e:
                print(f"   [Advanced/Ultra Mode] Warning: Failed to query projects for {org.canonical_name}: {e}")

        if is_ultra and project_list_str:
            print(f"   [Ultra Mode] Running multi-loop deep reasoning, critique, and proposal strategy for {org.canonical_name}...")
            
            # Loop 1: Project Alignment & Suitability
            if callback:
                await callback("info", f"[{org.canonical_name}] Loop 1: Best project matching...")
            prompt_suitability = f"""
You are an expert GSoC mentor for the organization '{org.canonical_name}'.
You are evaluating a student with the following profile:
- Experience Level: {profile.experience_level}
- Extracted Skills: {', '.join(profile.skills)}
- Interests/Topics: {', '.join(profile.topics_of_interest)}

Here is a list of recent GSoC projects accepted by '{org.canonical_name}':
{project_list_str}

Please identify the single best-matching project from the list for this student.
Explain in detail (1-2 paragraphs) why they are a strong candidate for this project and how their skills align.
Format your output exactly as:
### BEST MATCHING PROJECT
- **Project Title:** [Title of the best matched project]
- **Alignment Analysis:** [1-2 paragraphs explaining alignment...]
"""
            try:
                resp_suitability = await client.chat_model.ainvoke([HumanMessage(content=prompt_suitability)])
                suitability_txt = resp_suitability.content.strip()
            except Exception as e:
                suitability_txt = f"### BEST MATCHING PROJECT\n- **Project Title:** High-level match\n- **Alignment Analysis:** Algorithmic match (LLM failed: {e})"

            # Loop 2: Adversarial Critique
            if callback:
                await callback("info", f"[{org.canonical_name}] Loop 2: Reviewer risk & gap analysis...")
            prompt_critique = f"""
You are a highly critical, adversarial GSoC proposal reviewer for '{org.canonical_name}'.
You want to ensure only the highest quality students get accepted.
Review the candidate's profile:
- Skills: {', '.join(profile.skills)}
- Experience Level: {profile.experience_level}

And the best-matching project alignment:
{suitability_txt}

Identify all potential risks, weaknesses, and missing skills/prerequisites in this candidate's application.
Why would this candidate struggle? What important tools, concepts, or experience are they missing for this project?
Provide a detailed 1-2 paragraph critique.
Format your output exactly as:
### CRITIQUE & RISK ASSESSMENT
[Your detailed critique paragraphs...]
"""
            try:
                resp_critique = await client.chat_model.ainvoke([HumanMessage(content=prompt_critique)])
                critique_txt = resp_critique.content.strip()
            except Exception as e:
                critique_txt = f"### CRITIQUE & RISK ASSESSMENT\nCould not perform critique: {e}"

            # Loop 3: Actionable Roadmap & Proposal Strategy
            if callback:
                await callback("info", f"[{org.canonical_name}] Loop 3: Formulating proposal strategy...")
            prompt_strategy = f"""
You are a senior developer and advisor helping a GSoC applicant succeed.
You have the suitability analysis:
{suitability_txt}

And the critic's review of their weaknesses:
{critique_txt}

Draft a concrete, actionable proposal strategy and learning roadmap for the student.
What specific actions (e.g. learning specific libraries, contributing to particular parts of the repo, writing their proposal in a certain way) should they take to mitigate the critic's concerns and maximize their chances of acceptance?
Format your output exactly as:
### PROPOSAL STRATEGY & ROADMAP
[Your concrete recommendations...]
"""
            try:
                resp_strategy = await client.chat_model.ainvoke([HumanMessage(content=prompt_strategy)])
                strategy_txt = resp_strategy.content.strip()
            except Exception as e:
                strategy_txt = f"### PROPOSAL STRATEGY & ROADMAP\nCould not compile roadmap: {e}"

            # Loop 4: Synthesis & Final Recommendation Score
            if callback:
                await callback("info", f"[{org.canonical_name}] Loop 4: Synthesizing score and report...")
            prompt_synthesis = f"""
You are the Selection Committee Lead for '{org.canonical_name}' at GSoC.
You have reviewed all the materials for this candidate:
1. Suitability & Alignment:
{suitability_txt}

2. Critique & Weaknesses:
{critique_txt}

3. Strategy & Mitigation:
{strategy_txt}

Synthesize these into a final, unified presentation for the candidate's dashboard.
Then, assign a final suitability score on a scale from 0 to 100 (where 0 is completely incompatible and 100 is a perfect fit).

Format your output exactly as follows (use these headers):

### MATCH JUSTIFICATION
[Write a comprehensive synthesis of the match, summarizing the suitability, risks, and mitigation strategy in 2-3 polished paragraphs. Address the student directly: "You are a strong match because..."]

### RECOMMENDED CONTRIBUTOR PROJECT
{suitability_txt.replace('### BEST MATCHING PROJECT', '').strip()}

### MAINTAINER CRITIQUE & RISK ASSESSMENT
{critique_txt.replace('### CRITIQUE & RISK ASSESSMENT', '').strip()}

### ACTIONABLE PROPOSAL STRATEGY & ROADMAP
{strategy_txt.replace('### PROPOSAL STRATEGY & ROADMAP', '').strip()}

### RECOMMENDATION SCORE
[A single integer number between 0 and 100, e.g. 90]
"""
            try:
                resp_synthesis = await client.chat_model.ainvoke([HumanMessage(content=prompt_synthesis)])
                explanation = resp_synthesis.content.strip()
                if callback:
                    await callback("info", f"[{org.canonical_name}] Multi-loop analysis complete.")
            except Exception as e:
                print(f"   [Ultra Mode] Warning: Synthesis loop failed: {e}")
                explanation = f"### MATCH JUSTIFICATION\nFailed to synthesize reasoning: {e}\n\n### RECOMMENDATION SCORE\n70"

        elif is_advanced and project_list_str:
            print(f"   [Advanced Mode] Running deep reasoning matching and project alignment for {org.canonical_name}...")
            if callback:
                await callback("info", f"[{org.canonical_name}] Running deep project matching & gap analysis...")
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
            if callback:
                await callback("info", f"[{org.canonical_name}] Generating match explanation...")
            prompt = EXPLANATION_PROMPT.format(
                user_summary=user_summary,
                matched_skills=", ".join(org.matched_technologies),
                matched_topics=", ".join(org.matched_topics),
                org_name=org.canonical_name,
                org_description=org.description
            )
        
        try:
            if not (is_ultra and project_list_str):
                response = await client.chat_model.ainvoke([HumanMessage(content=prompt)])
                explanation = response.content.strip()
            
            # Extract recommendation score if in advanced or ultra mode
            llm_score_raw = None
            if (is_advanced or is_ultra) and "### RECOMMENDATION SCORE" in explanation:
                parts = explanation.split("### RECOMMENDATION SCORE")
                explanation_body = parts[0].strip()
                score_str = parts[1].strip()
                
                # Parse the score number
                import re
                match = re.search(r'\b\d{1,3}\b', score_str)
                if match:
                    val = int(match.group())
                    llm_score_raw = min(10.0, max(0.0, val / 10.0))
                    print(f"   [{'Ultra' if is_ultra else 'Advanced'} Mode] Parsed LLM recommendation score: {val}/100 ({llm_score_raw:.2f}/10)")
                
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
    
    # --- Pure Min-Max Normalization using global score range ---
    # global_score_min/max come from merger.py and represent the score range
    # across ALL evaluated orgs (not just this top-N batch).
    # This gives honest scores: e.g. 10th place isn't 0% just because it's last
    # in the batch — it's scored relative to every org that was evaluated.
    g_min = state.get("global_score_min", 0.0)
    g_max = state.get("global_score_max", 1.0)

    for org in orgs:
        if g_max == g_min:
            org.score.total = round(1.0, 4)
        else:
            org.score.total = round((org.score.total - g_min) / (g_max - g_min), 4)

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
    
    if callback:
        await callback("info", "All matches processed. Compiling results...")
        
    return {
        "ranked_organizations": orgs,
        "match_result": result.model_dump()
    }
