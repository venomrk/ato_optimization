from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def default_credit_reset_at() -> datetime:
    return utcnow() + timedelta(days=30)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True)

    plan: Mapped[str] = mapped_column(String(32), default="free")
    credits_balance: Mapped[int] = mapped_column(Integer, default=100)
    credits_reset_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=default_credit_reset_at)

    stripe_customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    usage_logs: Mapped[list[UsageLog]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    endpoint: Mapped[str] = mapped_column(String(128), nullable=False)
    credits_used: Mapped[int] = mapped_column(Integer, default=1)
    request_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="usage_logs")
