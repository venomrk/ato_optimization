from __future__ import annotations

from datetime import datetime, timedelta, timezone

try:
    import stripe  # type: ignore
except Exception:  # pragma: no cover
    stripe = None

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import PLAN_MONTHLY_CREDITS, get_current_user
from app.db.models import User
from app.db.session import SessionLocal, get_db
from app.schemas.billing import CheckoutSessionRequest, CheckoutSessionResponse, PlanOut

router = APIRouter(prefix="/billing", tags=["billing"])


def _require_stripe() -> None:
    if stripe is None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Stripe dependency not installed")
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Stripe not configured")
    stripe.api_key = settings.stripe_secret_key


def _apply_plan(user: User, plan: str) -> None:
    now = datetime.now(tz=timezone.utc)
    user.plan = plan
    monthly = PLAN_MONTHLY_CREDITS.get(plan)
    if monthly is not None:
        user.credits_balance = monthly
        user.credits_reset_at = now + timedelta(days=30)


@router.get("/plans", response_model=list[PlanOut])
def plans():
    return [
        PlanOut(id="free", name="Free", monthly_credits=PLAN_MONTHLY_CREDITS["free"]),
        PlanOut(id="premium", name="Premium", monthly_credits=PLAN_MONTHLY_CREDITS["premium"]),
        PlanOut(id="enterprise", name="Enterprise", monthly_credits=None),
    ]


@router.post("/checkout-session", response_model=CheckoutSessionResponse)
def create_checkout_session(
    payload: CheckoutSessionRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _require_stripe()

    if payload.plan != "premium":
        raise HTTPException(status_code=400, detail="Unsupported plan")

    if not settings.stripe_premium_price_id:
        raise HTTPException(status_code=500, detail="Missing STRIPE_PREMIUM_PRICE_ID")

    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})
        user.stripe_customer_id = customer["id"]
        db.add(user)
        db.commit()

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=user.stripe_customer_id,
        line_items=[{"price": settings.stripe_premium_price_id, "quantity": 1}],
        success_url=settings.stripe_success_url,
        cancel_url=settings.stripe_cancel_url,
        metadata={"user_id": str(user.id), "plan": "premium"},
    )

    return CheckoutSessionResponse(url=session["url"])


@router.post("/portal-session")
def create_portal_session(user: User = Depends(get_current_user)):
    _require_stripe()

    if not user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer")

    portal = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=settings.frontend_url,
    )
    return {"url": portal["url"]}


@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str | None = Header(default=None)):
    _require_stripe()

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=500, detail="Missing STRIPE_WEBHOOK_SECRET")

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=stripe_signature, secret=settings.stripe_webhook_secret)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type")
    data_obj = (event.get("data") or {}).get("object") or {}

    db = SessionLocal()
    try:
        if event_type == "checkout.session.completed":
            user_id = (data_obj.get("metadata") or {}).get("user_id")
            subscription_id = data_obj.get("subscription")
            customer_id = data_obj.get("customer")

            if user_id:
                user = db.get(User, int(user_id))
            elif customer_id:
                user = db.scalar(select(User).where(User.stripe_customer_id == customer_id))
            else:
                user = None

            if user:
                user.stripe_customer_id = customer_id or user.stripe_customer_id
                user.stripe_subscription_id = subscription_id
                _apply_plan(user, "premium")
                db.add(user)
                db.commit()

        if event_type == "customer.subscription.deleted":
            customer_id = data_obj.get("customer")
            if customer_id:
                user = db.scalar(select(User).where(User.stripe_customer_id == customer_id))
                if user:
                    user.stripe_subscription_id = None
                    _apply_plan(user, "free")
                    db.add(user)
                    db.commit()

        if event_type == "invoice.payment_succeeded":
            customer_id = data_obj.get("customer")
            if customer_id:
                user = db.scalar(select(User).where(User.stripe_customer_id == customer_id))
                if user and user.plan in PLAN_MONTHLY_CREDITS:
                    _apply_plan(user, user.plan)
                    db.add(user)
                    db.commit()

    finally:
        db.close()

    return {"received": True}
