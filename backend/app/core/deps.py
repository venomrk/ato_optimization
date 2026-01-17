from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.models import UsageLog, User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.scalar(select(User).where(User.email == email))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    return user


PLAN_MONTHLY_CREDITS = {
    "free": 100,
    "premium": 10_000,
}


def ensure_credits_fresh(user: User) -> None:
    now = datetime.now(tz=timezone.utc)
    if user.credits_reset_at and now >= user.credits_reset_at:
        monthly = PLAN_MONTHLY_CREDITS.get(user.plan)
        if monthly is not None:
            user.credits_balance = monthly
            user.credits_reset_at = now + timedelta(days=30)


def consume_credits(db: Session, user: User, endpoint: str, credits: int = 1, request_payload: str | None = None) -> None:
    ensure_credits_fresh(user)

    if user.plan in ("enterprise",):
        return

    if user.credits_balance < credits:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Out of credits. Upgrade your plan to continue.",
        )

    user.credits_balance -= credits
    db.add(
        UsageLog(
            user_id=user.id,
            endpoint=endpoint,
            credits_used=credits,
            request_payload=request_payload,
        )
    )
    db.add(user)
    db.commit()
