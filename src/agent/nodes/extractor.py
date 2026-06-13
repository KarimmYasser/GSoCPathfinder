"""Node 1: Extract structured profile from CV using LLM."""

import json
from langchain_core.messages import HumanMessage

from agent.state import AgentState
from llm.client import get_llm_client
from llm.prompts import CV_EXTRACTION_PROMPT
from models import UserProfile

async def extract_profile_node(state: AgentState) -> dict:
    """Extracts skills, experience, and topics from the raw CV."""
    print("Agent Node: Extracting profile from CV...")
    
    cv_text = state["raw_cv_text"]
    if not cv_text.strip():
        raise ValueError("Empty CV text provided.")
        
    client = get_llm_client()
    
    # We ask the model to output JSON. We force JSON mode if supported, 
    # but since we use LM Studio / various local models, we just parse it robustly.
    prompt = CV_EXTRACTION_PROMPT.format(cv_text=cv_text)
    
    response = await client.chat_model.ainvoke([HumanMessage(content=prompt)])
    content = response.content.strip()
    
    # Robust JSON parsing (sometimes models wrap in ```json ... ```)
    if content.startswith("```json"):
        content = content.replace("```json", "", 1)
        if content.endswith("```"):
            content = content[:-3]
    elif content.startswith("```"):
        content = content.replace("```", "", 1)
        if content.endswith("```"):
            content = content[:-3]
            
    try:
        parsed_data = json.loads(content.strip())
        # Provide the raw text to the model
        parsed_data["raw_cv_text"] = cv_text
        profile = UserProfile.model_validate(parsed_data)
        
    except json.JSONDecodeError:
        print("Warning: LLM did not output valid JSON. Falling back to empty profile.")
        # Fallback profile if the LLM fails completely
        profile = UserProfile(
            raw_cv_text=cv_text,
            skills=[],
            topics_of_interest=[],
            experience_level="unknown",
            languages=[],
            preferred_categories=[],
            summary="Failed to extract profile."
        )

    # Advanced Mode: Profile Refinement Loop
    if state.get("advanced") and len(profile.skills) > 0:
        print("   [Advanced Mode] Running iterative CV audit refinement loop...")
        refine_prompt = f"""
You are an expert CV auditor. We have parsed the following CV text:
---
{cv_text}
---
The initial extraction identified the following skills/technologies:
{profile.skills}

Your task is to audit the CV text and list any ADDITIONAL programming languages, databases, libraries, frameworks, cloud platforms, tools, or machine learning topics mentioned in the CV that were missed in the first pass.
Only output the new skills as a JSON list of strings (e.g. ["kubernetes", "redis"]). If no other skills were missed, output an empty list []. Do not explain anything. Output only valid JSON.
"""
        try:
            refine_response = await client.chat_model.ainvoke([HumanMessage(content=refine_prompt)])
            refine_content = refine_response.content.strip()
            
            # Clean up JSON formatting
            if refine_content.startswith("```json"):
                refine_content = refine_content.replace("```json", "", 1)
                if refine_content.endswith("```"):
                    refine_content = refine_content[:-3]
            elif refine_content.startswith("```"):
                refine_content = refine_content.replace("```", "", 1)
                if refine_content.endswith("```"):
                    refine_content = refine_content[:-3]
                    
            new_skills = json.loads(refine_content.strip())
            if isinstance(new_skills, list) and len(new_skills) > 0:
                print(f"   [Advanced Mode] Found {len(new_skills)} additional skills: {new_skills}")
                existing_skills_lower = {s.lower() for s in profile.skills}
                for skill in new_skills:
                    if skill.lower() not in existing_skills_lower:
                        profile.skills.append(skill)
                        existing_skills_lower.add(skill.lower())
        except Exception as e:
            print(f"   [Advanced Mode] Warning: Failed to refine profile extraction: {e}")

    print(f"   Extracted {len(profile.skills)} skills and {len(profile.topics_of_interest)} topics.")
    return {"user_profile": profile}
