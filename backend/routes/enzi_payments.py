"""
ENZI Premium - Stripe Payment Gateway
Subscription tiers for premium ENZI features
Uses emergentintegrations Stripe Checkout
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone
import os
import uuid

from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, CheckoutSessionRequest, CheckoutSessionResponse, CheckoutStatusResponse
)
from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/payments", tags=["ENZI Payments"])

PREMIUM_PACKAGES = {
    "pro_monthly": {"name": "ENZI Pro", "amount": 9.99, "currency": "usd", "period": "monthly",
                    "features": ["Unlimited E2EE", "Priority Support", "Custom Bots", "Advanced AI"]},
    "pro_yearly": {"name": "ENZI Pro (Annual)", "amount": 99.99, "currency": "usd", "period": "yearly",
                   "features": ["Unlimited E2EE", "Priority Support", "Custom Bots", "Advanced AI", "2 Months Free"]},
    "team_monthly": {"name": "ENZI Team", "amount": 29.99, "currency": "usd", "period": "monthly",
                     "features": ["Everything in Pro", "Team Analytics", "Admin Dashboard", "SSO Management", "Up to 50 members"]},
    "enterprise": {"name": "ENZI Enterprise", "amount": 99.99, "currency": "usd", "period": "monthly",
                   "features": ["Everything in Team", "Unlimited Members", "Dedicated Support", "Custom Integrations", "SLA"]},
}


class CheckoutRequest(BaseModel):
    package_id: str
    origin_url: str


@router.get("/packages")
async def get_packages():
    """Get available ENZI premium packages"""
    return {"packages": [{"id": k, **v} for k, v in PREMIUM_PACKAGES.items()]}


@router.post("/checkout")
async def create_checkout(req: CheckoutRequest, request: Request):
    """Create Stripe checkout session for ENZI premium"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if req.package_id not in PREMIUM_PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")

    pkg = PREMIUM_PACKAGES[req.package_id]
    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")

    host_url = str(request.base_url).rstrip("/")
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe = StripeCheckout(api_key=api_key, webhook_url=webhook_url)

    success_url = f"{req.origin_url}/lumi?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{req.origin_url}/lumi?payment=cancelled"

    metadata = {"user_id": user["user_id"], "email": user["email"],
                "package_id": req.package_id, "package_name": pkg["name"]}

    checkout_req = CheckoutSessionRequest(
        amount=float(pkg["amount"]), currency=pkg["currency"],
        success_url=success_url, cancel_url=cancel_url, metadata=metadata
    )
    session: CheckoutSessionResponse = await stripe.create_checkout_session(checkout_req)

    await db.payment_transactions.insert_one({
        "id": str(uuid.uuid4()), "session_id": session.session_id,
        "user_id": user["user_id"], "email": user["email"],
        "package_id": req.package_id, "package_name": pkg["name"],
        "amount": pkg["amount"], "currency": pkg["currency"],
        "payment_status": "pending", "status": "initiated",
        "metadata": metadata, "created_at": datetime.now(timezone.utc).isoformat()
    })

    return {"url": session.url, "session_id": session.session_id}


@router.get("/status/{session_id}")
async def check_payment_status(session_id: str, request: Request):
    """Poll payment status and update transaction"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    api_key = os.environ.get("STRIPE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Payment system not configured")

    host_url = str(request.base_url).rstrip("/")
    stripe = StripeCheckout(api_key=api_key, webhook_url=f"{host_url}/api/webhook/stripe")
    status: CheckoutStatusResponse = await stripe.get_checkout_status(session_id)

    tx = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if tx and tx.get("payment_status") != "paid" and status.payment_status == "paid":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "paid", "status": "completed",
                      "completed_at": datetime.now(timezone.utc).isoformat()}}
        )
        await db.users.update_one(
            {"user_id": tx["user_id"]},
            {"$set": {"premium": True, "premium_package": tx["package_id"],
                      "premium_since": datetime.now(timezone.utc).isoformat()}}
        )
    elif tx and status.status == "expired":
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {"payment_status": "expired", "status": "expired"}}
        )

    return {"status": status.status, "payment_status": status.payment_status,
            "amount_total": status.amount_total, "currency": status.currency}


@router.get("/my-subscription")
async def get_subscription(request: Request):
    """Get user's subscription status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    u = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0, "password_hash": 0})
    pkg = PREMIUM_PACKAGES.get(u.get("premium_package"), {})

    return {
        "is_premium": u.get("premium", False),
        "package_id": u.get("premium_package"),
        "package_name": pkg.get("name", "Free"),
        "features": pkg.get("features", []),
        "premium_since": u.get("premium_since")
    }


@router.get("/history")
async def get_payment_history(request: Request):
    """Get payment history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    txs = await db.payment_transactions.find(
        {"user_id": user["user_id"]}, {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)

    return {"transactions": txs, "count": len(txs)}
