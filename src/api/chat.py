from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from llm.client import get_llm_client


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: list[dict[str, Any]]  # The ranked organizations


async def handle_chat(request: ChatRequest) -> str:
    """Handle a chat request using the provided context."""
    client = get_llm_client()

    # Build the system prompt with the context
    context_str = "You are the GSoC Pathfinder AI Assistant.\n"
    context_str += "The user has provided their CV and the matching engine has found the following top organizations for them:\n\n"

    for org in request.context:
        score = org.get("score", {}).get("total", 0) * 100
        context_str += f"- {org.get('canonical_name')} (Score: {score:.1f}%)\n"
        context_str += f"  Category: {org.get('category')}\n"
        techs = ", ".join(org.get("matched_technologies", []))
        context_str += f"  Matched Tech: {techs}\n"
        context_str += f"  Description: {org.get('description', '')[:200]}...\n\n"

    context_str += "Answer the user's questions about these organizations. Be concise, helpful, and use markdown formatting."

    langchain_msgs = [SystemMessage(content=context_str)]

    for msg in request.messages:
        if msg.role == "user":
            langchain_msgs.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_msgs.append(AIMessage(content=msg.content))

    response = await client.chat_model.ainvoke(langchain_msgs)
    return response.content
