from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: int
    email: EmailStr
    plan: str
    credits_balance: int
    credits_reset_at: datetime

    model_config = {"from_attributes": True}
