from __future__ import annotations

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str


class ChatCompletionRequest(BaseModel):
    messages: list[ChatMessage]
    agent_mode: str = Field(default="multi", description="single|multi")


class AgentReply(BaseModel):
    agent: str
    content: str


class ChatCompletionResponse(BaseModel):
    replies: list[AgentReply]
    combined: str
