"""
Payment Routes
Handles: Stripe payments, PayPal payments, membership management
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import os
import logging

from utils.database import db
from routes.auth import get_current_user, check_membership_status

router = APIRouter(prefix="/payments", tags=["Payments"])

STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')
LIFETIME_PRICE = 1.00
TRIAL_DAYS = 15

# ============== Models ==============

class CreateCheckoutRequest(BaseModel):
    success_url: str
    cancel_url: str
    plan: str = "lifetime"

# ============== Stripe Routes ==============

@router.post("/create-checkout")
async def create_checkout_session(checkout_request: CreateCheckoutRequest, request: Request):
    """Create a Stripe checkout session for membership"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'MedMatch Lifetime Membership',
                        'description': 'Unlimited access to all job search features',
                    },
                    'unit_amount': int(LIFETIME_PRICE * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=checkout_request.success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=checkout_request.cancel_url,
            customer_email=user['email'],
            metadata={
                'user_id': user['user_id'],
                'plan': checkout_request.plan
            }
        )
        
        return {"session_id": session.id, "url": session.url}
        
    except Exception as e:
        logging.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@router.get("/status/{session_id}")
async def get_payment_status(session_id: str, request: Request):
    """Get payment status from Stripe"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Update user membership
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "membership_status": "active",
                    "membership_activated_at": datetime.now(timezone.utc).isoformat(),
                    "payment_session_id": session_id
                }}
            )
            
            return {
                "status": "success",
                "message": "Payment successful! Your membership is now active.",
                "membership_status": "active"
            }
        else:
            return {
                "status": session.payment_status,
                "message": "Payment is being processed"
            }
            
    except Exception as e:
        logging.error(f"Payment status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to check payment status")

@router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        
        # In production, verify webhook signature
        event = stripe.Event.construct_from(
            values=eval(payload.decode()),
            key=stripe.api_key
        )
        
        if event.type == 'checkout.session.completed':
            session = event.data.object
            user_id = session.metadata.get('user_id')
            
            if user_id:
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": {
                        "membership_status": "active",
                        "membership_activated_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
        
        return {"received": True}
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============== PayPal Routes ==============

@router.post("/paypal/create")
async def create_paypal_payment(checkout_request: CreateCheckoutRequest, request: Request):
    """Create a PayPal payment"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    paypal_client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
    paypal_secret = os.environ.get('PAYPAL_SECRET', '')
    
    if not paypal_client_id or not paypal_secret:
        raise HTTPException(status_code=500, detail="PayPal not configured")
    
    # Determine amount based on plan
    amount = "1.00" if checkout_request.plan == "lifetime" else "1.00"
    
    try:
        import paypalrestsdk
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),
            "client_id": paypal_client_id,
            "client_secret": paypal_secret
        })
        
        # Create payment
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": checkout_request.success_url,
                "cancel_url": checkout_request.cancel_url
            },
            "transactions": [{
                "amount": {
                    "total": amount,
                    "currency": "USD"
                },
                "description": "MedMatch Lifetime Membership"
            }]
        })
        
        if payment.create():
            # Find approval URL
            for link in payment.links:
                if link.rel == "approval_url":
                    return {
                        "payment_id": payment.id,
                        "approval_url": link.href
                    }
            raise HTTPException(status_code=500, detail="PayPal approval URL not found")
        else:
            logging.error(f"PayPal payment creation failed: {payment.error}")
            raise HTTPException(status_code=500, detail=f"PayPal error: {payment.error}")
            
    except ImportError:
        raise HTTPException(status_code=500, detail="PayPal SDK not installed")
    except Exception as e:
        logging.error(f"PayPal error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/paypal/execute")
async def execute_paypal_payment(request: Request):
    """Execute PayPal payment after user approval"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    payment_id = body.get("payment_id")
    payer_id = body.get("payer_id")
    
    if not payment_id or not payer_id:
        raise HTTPException(status_code=400, detail="Missing payment_id or payer_id")
    
    paypal_client_id = os.environ.get('PAYPAL_CLIENT_ID', '')
    paypal_secret = os.environ.get('PAYPAL_SECRET', '')
    
    if not paypal_client_id or not paypal_secret:
        raise HTTPException(status_code=500, detail="PayPal not configured")
    
    try:
        import paypalrestsdk
        
        paypalrestsdk.configure({
            "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),
            "client_id": paypal_client_id,
            "client_secret": paypal_secret
        })
        
        payment = paypalrestsdk.Payment.find(payment_id)
        
        if payment.execute({"payer_id": payer_id}):
            # Payment successful - update user membership
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": {
                    "membership_status": "lifetime",
                    "membership_updated": datetime.now(timezone.utc).isoformat(),
                    "payment_method": "paypal",
                    "paypal_payment_id": payment_id
                }}
            )
            return {
                "success": True,
                "payment_id": payment_id,
                "message": "Payment successful! Welcome to MedMatch Lifetime Membership."
            }
        else:
            logging.error(f"PayPal execution failed: {payment.error}")
            raise HTTPException(status_code=500, detail=f"PayPal error: {payment.error}")
            
    except Exception as e:
        logging.error(f"PayPal execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============== Membership Routes ==============

membership_router = APIRouter(prefix="/membership", tags=["Membership"])

@membership_router.get("/status")
async def get_membership_status(request: Request):
    """Get current membership status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    status = check_membership_status(user)
    
    # Calculate days remaining for trial
    days_remaining = None
    if status == "trial" and user.get("trial_ends_at"):
        try:
            trial_end = datetime.fromisoformat(user["trial_ends_at"].replace('Z', '+00:00'))
            days_remaining = (trial_end - datetime.now(timezone.utc)).days
        except:
            pass
    
    return {
        "status": status,
        "is_active": status in ["active", "trial"],
        "trial_ends_at": user.get("trial_ends_at"),
        "days_remaining": days_remaining,
        "price": LIFETIME_PRICE
    }

@membership_router.get("/check-access/{feature}")
async def check_feature_access(feature: str, request: Request):
    """Check if user has access to a specific feature"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Admin bypass
    if user.get("is_admin") or user.get("email") == "admin@medmatch.com":
        return {"has_access": True, "reason": "admin"}
    
    # Recruiters have free access
    if user.get("role") == "recruiter":
        return {"has_access": True, "reason": "recruiter"}
    
    status = check_membership_status(user)
    
    # Free features
    free_features = ["resume", "job_search", "saved_jobs", "applications"]
    if feature in free_features:
        return {"has_access": True, "reason": "free_feature"}
    
    # Premium features require active membership
    if status in ["active", "trial"]:
        return {"has_access": True, "reason": status}
    
    return {
        "has_access": False,
        "reason": "membership_required",
        "message": "Upgrade to access this feature"
    }
