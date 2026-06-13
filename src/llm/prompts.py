"""Prompt templates for LLM interactions."""

from langchain_core.prompts import PromptTemplate

# Prompt for extracting structured profile from CV
CV_EXTRACTION_PROMPT = PromptTemplate.from_template("""
You are an expert tech recruiter and technical screener.
Extract a structured profile from the following Curriculum Vitae (CV) text.

CV Text:
----------------
{cv_text}
----------------

Extract the following information:
1. "skills": A list of specific technologies, frameworks, and programming languages the person knows. Be specific (e.g. "React", "Python", "Kubernetes", "C++").
2. "topics_of_interest": A list of high-level domains the person is interested in or has worked on (e.g. "Machine Learning", "Web Development", "Compilers", "Robotics").
3. "experience_level": A single string classifying their level: "student", "junior", "mid", or "senior".
4. "languages": A subset of skills that are strictly programming languages.
5. "preferred_categories": Any specific industry or software categories they might fit into.
6. "summary": A 2-3 sentence summary of their technical profile.

Format the output EXACTLY as a JSON object matching this schema. Do not include markdown code blocks or any other text.
{{
  "skills": ["..."],
  "topics_of_interest": ["..."],
  "experience_level": "...",
  "languages": ["..."],
  "preferred_categories": ["..."],
  "summary": "..."
}}
""")

# Prompt for generating the final explanation for an organization match
EXPLANATION_PROMPT = PromptTemplate.from_template("""
You are an AI assistant helping a developer find the perfect Google Summer of Code (GSoC) organization.

You need to write a short, compelling explanation of WHY this organization is a good fit for this developer.

Developer Profile Summary:
{user_summary}

Matched Skills: {matched_skills}
Matched Interests: {matched_topics}

Organization Details:
Name: {org_name}
Description: {org_description}

Write a 2-3 sentence explanation directly addressing the developer (e.g., "This organization is a great fit for you because...").
Focus on how their specific skills and interests align with the organization's work. Keep it encouraging and concise.
""")
