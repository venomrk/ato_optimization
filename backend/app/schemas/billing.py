from __future__ import annotations

from pydantic import BaseModel, Field


class PlanOut(BaseModel):
    id: str
    name: str
    monthly_credits: int | None


class CheckoutSessionRequest(BaseModel):
    plan: str = Field(pattern="^(premium)$")


class CheckoutSessionResponse(BaseModel):
    url: str
