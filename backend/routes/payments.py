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
RECRUITER_MONTHLY_PRICE = 5.00
JOB_SEEKER_TRIAL_DAYS = 15
RECRUITER_TRIAL_DAYS = 30

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
        
        is_recruiter = user.get('role') == 'recruiter'
        plan = checkout_request.plan
        
        # Determine pricing based on plan type
        if plan == 'recruiter_monthly' or (is_recruiter and plan != 'lifetime'):
            # Recruiter monthly subscription - $5/month
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'MedMatch Recruiter Pro',
                            'description': 'Post unlimited jobs, access candidate database, ATS tools',
                        },
                        'unit_amount': int(RECRUITER_MONTHLY_PRICE * 100),
                        'recurring': {
                            'interval': 'month',
                        },
                    },
                    'quantity': 1,
                }],
                mode='subscription',
                subscription_data={
                    'trial_period_days': RECRUITER_TRIAL_DAYS,
                },
                success_url=checkout_request.success_url + ('&' if '?' in checkout_request.success_url else '?') + 'session_id={CHECKOUT_SESSION_ID}',
                cancel_url=checkout_request.cancel_url,
                customer_email=user['email'],
                metadata={
                    'user_id': user['user_id'],
                    'plan': 'recruiter_monthly',
                    'role': 'recruiter'
                }
            )
        else:
            # Job seeker lifetime membership - $1 one-time
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
                success_url=checkout_request.success_url + ('&' if '?' in checkout_request.success_url else '?') + 'session_id={CHECKOUT_SESSION_ID}',
                cancel_url=checkout_request.cancel_url,
                customer_email=user['email'],
                metadata={
                    'user_id': user['user_id'],
                    'plan': 'lifetime',
                    'role': 'job_seeker'
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
        
        # Check if it's a subscription (recruiter) or one-time payment (job seeker)
        is_subscription = session.mode == 'subscription'
        is_paid = session.payment_status == 'paid' or (is_subscription and session.status == 'complete')
        
        if is_paid:
            # Determine plan type from metadata
            plan = session.metadata.get('plan', 'lifetime')
            role = session.metadata.get('role', 'job_seeker')
            
            update_data = {
                "membership_status": "active",
                "membership_activated_at": datetime.now(timezone.utc).isoformat(),
                "payment_session_id": session_id
            }
            
            if is_subscription:
                # Recruiter subscription
                update_data["subscription_id"] = session.subscription
                update_data["subscription_plan"] = "recruiter_monthly"
                update_data["subscription_status"] = "active"
                # Trial ends in 30 days
                update_data["trial_ends_at"] = (datetime.now(timezone.utc) + timedelta(days=RECRUITER_TRIAL_DAYS)).isoformat()
            else:
                # Job seeker lifetime
                update_data["membership_plan"] = "lifetime"
            
            # Update user membership
            await db.users.update_one(
                {"user_id": user["user_id"]},
                {"$set": update_data}
            )
            
            return {
                "status": "success",
                "message": "Payment successful! Your membership is now active.",
                "membership_status": "active",
                "plan": plan
            }
        else:
            return {
                "status": session.payment_status or session.status,
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
    is_recruiter = user.get("role") == "recruiter"
    
    # Calculate days remaining for trial
    days_remaining = None
    if status == "trial" and user.get("trial_ends_at"):
        try:
            trial_end = datetime.fromisoformat(user["trial_ends_at"].replace('Z', '+00:00'))
            days_remaining = (trial_end - datetime.now(timezone.utc)).days
        except:
            pass
    
    response = {
        "status": status,
        "is_active": status in ["active", "trial"],
        "trial_ends_at": user.get("trial_ends_at"),
        "days_remaining": days_remaining,
        "role": user.get("role", "job_seeker"),
    }
    
    # Add role-specific pricing
    if is_recruiter:
        response["price"] = RECRUITER_MONTHLY_PRICE
        response["price_type"] = "monthly"
        response["trial_days"] = RECRUITER_TRIAL_DAYS
        response["plan"] = user.get("subscription_plan", "recruiter_monthly")
        response["subscription_status"] = user.get("subscription_status")
    else:
        response["price"] = LIFETIME_PRICE
        response["price_type"] = "lifetime"
        response["trial_days"] = JOB_SEEKER_TRIAL_DAYS
        response["plan"] = user.get("membership_plan", "lifetime")
    
    return response

@membership_router.get("/check-access/{feature}")
async def check_feature_access(feature: str, request: Request):
    """Check if user has access to a specific feature"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Admin bypass
    if user.get("is_admin") or user.get("email") == "admin@medmatch.com":
        return {"has_access": True, "reason": "admin"}
    
    status = check_membership_status(user)
    is_recruiter = user.get("role") == "recruiter"
    
    # Check recruiter-specific access
    if is_recruiter:
        # Basic recruiter features are free during trial or with active subscription
        free_recruiter_features = ["post_job", "view_applications"]
        premium_recruiter_features = ["candidate_search", "ats", "messaging", "analytics"]
        
        if feature in free_recruiter_features:
            return {"has_access": True, "reason": "free_recruiter_feature"}
        
        if feature in premium_recruiter_features:
            if status in ["active", "trial"]:
                return {"has_access": True, "reason": status}
            return {
                "has_access": False,
                "reason": "subscription_required",
                "message": "Upgrade to Recruiter Pro to access this feature"
            }
    
    # Job seeker features
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
