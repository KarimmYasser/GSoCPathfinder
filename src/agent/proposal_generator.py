from langchain_core.messages import HumanMessage, SystemMessage

from llm.client import get_llm_client


async def generate_proposal(cv_text: str, org_name: str, org_desc: str) -> str:
    """Generate a GSoC proposal draft using the user's CV and organization info."""
    client = get_llm_client()

    sys_prompt = (
        "You are an expert technical writer and open-source contributor. "
        "Your task is to write a high-quality Google Summer of Code (GSoC) proposal draft. "
        "Use markdown formatting. Include sections for: Introduction, Project Goals, "
        "Implementation Plan, Timeline, and Why I am a Good Fit."
    )

    user_prompt = (
        f"Organization: {org_name}\n"
        f"Description: {org_desc}\n\n"
        f"My CV/Background:\n{cv_text}\n\n"
        "Please draft a compelling GSoC proposal tailored to this organization based on my skills."
    )

    messages = [SystemMessage(content=sys_prompt), HumanMessage(content=user_prompt)]

    response = await client.chat_model.ainvoke(messages)
    return response.content
