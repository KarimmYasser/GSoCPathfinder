from langchain_core.messages import HumanMessage, SystemMessage

from llm.client import get_llm_client


async def optimize_cv(cv_text: str, org_name: str, org_desc: str) -> str:
    """Generate a Learning Roadmap to bridge the gap between CV and Org."""
    client = get_llm_client()

    sys_prompt = (
        "You are an expert technical mentor for Google Summer of Code. "
        "Your task is to analyze the gap between a student's current CV and their 'Dream Organization', "
        "and generate a personalized Learning Roadmap.\n"
        "Use markdown. Include sections for:\n"
        "1. Gap Analysis (What the student lacks)\n"
        "2. Short-term Roadmap (1-3 months)\n"
        "3. Long-term Roadmap (3-6 months)\n"
        "4. Recommended Projects/Contributions to start with."
    )

    user_prompt = (
        f"Target Organization: {org_name}\n"
        f"Organization Description: {org_desc}\n\n"
        f"My Current CV/Background:\n{cv_text}\n\n"
        "Please provide a learning roadmap to help me become a 100% match for this organization."
    )

    messages = [SystemMessage(content=sys_prompt), HumanMessage(content=user_prompt)]

    response = await client.chat_model.ainvoke(messages)
    return response.content
