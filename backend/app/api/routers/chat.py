from __future__ import annotations

import json

try:
    import httpx  # type: ignore
except Exception:  # pragma: no cover
    httpx = None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import consume_credits, get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.chat import AgentReply, ChatCompletionRequest, ChatCompletionResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _openrouter_chat(messages: list[dict]) -> str:
    if httpx is None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="httpx dependency not installed")
    if not settings.openrouter_api_key:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Chat requires OPENROUTER_API_KEY.",
        )

    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "temperature": 0.2,
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=60) as client:
        resp = client.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

    if resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="LLM provider error")

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Malformed LLM response")


@router.get("/agents")
def list_agents():
    return {
        "agents": [
            {"id": "researcher", "name": "Research Agent"},
            {"id": "chemist", "name": "Chemistry Agent"},
            {"id": "critic", "name": "Critic/Verifier"},
        ]
    }


@router.post("/completions", response_model=ChatCompletionResponse)
def chat_completions(
    payload: ChatCompletionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    credits = 5 if payload.agent_mode == "multi" else 2
    consume_credits(db=db, user=user, endpoint="chat.completions", credits=credits, request_payload=json.dumps(payload.model_dump()))

    base_messages = [m.model_dump() for m in payload.messages]

    if payload.agent_mode == "single":
        content = _openrouter_chat(base_messages)
        return ChatCompletionResponse(replies=[AgentReply(agent="assistant", content=content)], combined=content)

    agents = [
        ("researcher", "You are a research agent. Provide relevant papers, key findings, and citations when possible."),
        ("chemist", "You are a chemistry expert. Provide mechanistic explanations and safety considerations."),
        ("critic", "You are a critical reviewer. Identify assumptions, missing controls, and potential errors."),
    ]

    replies: list[AgentReply] = []
    for agent_id, system_prompt in agents:
        messages = [{"role": "system", "content": system_prompt}, *base_messages]
        replies.append(AgentReply(agent=agent_id, content=_openrouter_chat(messages)))

    combined = "\n\n".join([f"### {r.agent}\n{r.content}" for r in replies])
    return ChatCompletionResponse(replies=replies, combined=combined)
