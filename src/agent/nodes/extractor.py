"""Node 1: Extract structured profile from CV using LLM."""

import json

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.state import AgentState
from llm.client import get_llm_client
from llm.prompts import CV_EXTRACTION_PROMPT
from models import UserProfile


async def extract_profile_node(state: AgentState, config: RunnableConfig = None) -> dict:
    """Extracts skills, experience, and topics from the raw CV."""
    print("Agent Node: Extracting profile from CV...")
    callback = config.get("configurable", {}).get("progress_callback") if config else None
    if callback:
        await callback("info", "Extracting profile from CV...")

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
            summary="Failed to extract profile.",
        )

    # Advanced Mode: Profile Refinement Loop
    if (state.get("advanced") or state.get("ultra")) and len(profile.skills) > 0:
        print("   [Advanced/Ultra Mode] Running iterative CV audit refinement loop...")
        if callback:
            await callback("info", "Auditing CV for additional skills...")
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
                print(
                    f"   [Advanced/Ultra Mode] Found {len(new_skills)} additional skills: {new_skills}"
                )
                existing_skills_lower = {s.lower() for s in profile.skills}
                for skill in new_skills:
                    if skill.lower() not in existing_skills_lower:
                        profile.skills.append(skill)
                        existing_skills_lower.add(skill.lower())
        except Exception as e:
            print(f"   [Advanced/Ultra Mode] Warning: Failed to refine profile extraction: {e}")

    # Ultra Mode: Skill Verification & Hallucination Elimination Loop
    if state.get("ultra") and len(profile.skills) > 0:
        print("   [Ultra Mode] Running CV skill verification and self-correction loop...")
        if callback:
            await callback("info", "Verifying skills against CV to eliminate hallucinations...")
        verify_prompt = f"""
You are a CV verification assistant. We extracted the following skills/technologies/concepts from the CV:
{profile.skills}

CV Text:
---
{cv_text}
---

For each skill, inspect the CV text and check if the candidate actually possesses or mentions this skill/technology/concept.
If a skill is a hallucination (not mentioned, or not related to the candidate's technical profile in the text), mark it as "remove".
Otherwise, provide a very short 1-sentence quote or context from the CV showing where it is mentioned.

Format your output as a single JSON object mapping each skill to either a quote/context string or the word "remove". Do not include markdown code blocks or explanations.
Example output format:
{{
  "python": "Used python for 3 years in college",
  "kubernetes": "remove"
}}
"""
        try:
            verify_response = await client.chat_model.ainvoke([HumanMessage(content=verify_prompt)])
            verify_content = verify_response.content.strip()

            # Clean up JSON formatting
            if verify_content.startswith("```json"):
                verify_content = verify_content.replace("```json", "", 1)
                if verify_content.endswith("```"):
                    verify_content = verify_content[:-3]
            elif verify_content.startswith("```"):
                verify_content = verify_content.replace("```", "", 1)
                if verify_content.endswith("```"):
                    verify_content = verify_content[:-3]

            verified_data = json.loads(verify_content.strip())
            if isinstance(verified_data, dict):
                verified_skills = []
                for skill in profile.skills:
                    val = verified_data.get(skill) or verified_data.get(skill.lower())
                    if val and str(val).strip().lower() != "remove":
                        verified_skills.append(skill)
                    else:
                        print(f"   [Ultra Mode] Removed unverified/hallucinated skill: {skill}")
                profile.skills = verified_skills
        except Exception as e:
            print(f"   [Ultra Mode] Warning: Failed to verify skills: {e}")

    print(
        f"   Extracted {len(profile.skills)} skills and {len(profile.topics_of_interest)} topics."
    )
    if callback:
        await callback(
            "info",
            f"Extracted {len(profile.skills)} skills and {len(profile.topics_of_interest)} topics.",
        )
    return {"user_profile": profile}
