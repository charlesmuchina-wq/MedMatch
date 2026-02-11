"""
Payment Routes
Handles: Stripe payments, PayPal payments, membership management
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import os
import logging

from utils.database import db
from routes.auth import get_current_user, check_membership_status

router = APIRouter(prefix="/payments", tags=["Payments"])

STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# Job Seeker Pricing
JOB_SEEKER_3_YEAR_PRICE = 3.00  # $3 for 3 years premium
JOB_SEEKER_TRIAL_DAYS = 30

# Recruiter Pricing (monthly)
RECRUITER_STARTER_PRICE = 2.99
RECRUITER_GROWTH_PRICE = 7.99
RECRUITER_PREMIUM_PRICE = 14.99
RECRUITER_TRIAL_DAYS = 30

# Annual pricing (save 2 months)
RECRUITER_STARTER_ANNUAL = 29.99
RECRUITER_GROWTH_ANNUAL = 79.99
RECRUITER_PREMIUM_ANNUAL = 149.99

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
        
        plan = checkout_request.plan
        
        # Determine pricing based on plan type
        recruiter_plans = {
            'recruiter_starter': (RECRUITER_STARTER_PRICE, 'month', 'MedMatch Recruiter Starter', '5 job posts, basic candidate search'),
            'recruiter_starter_annual': (RECRUITER_STARTER_ANNUAL, 'year', 'MedMatch Recruiter Starter (Annual)', '5 job posts, basic candidate search - Save 2 months!'),
            'recruiter_growth': (RECRUITER_GROWTH_PRICE, 'month', 'MedMatch Recruiter Growth', '10 job posts, advanced search, blind screening, analytics'),
            'recruiter_growth_annual': (RECRUITER_GROWTH_ANNUAL, 'year', 'MedMatch Recruiter Growth (Annual)', '10 job posts, advanced search, blind screening, analytics - Save 2 months!'),
            'recruiter_premium': (RECRUITER_PREMIUM_PRICE, 'month', 'MedMatch Recruiter Premium', 'Unlimited posts, ATS integration, API access, dedicated support'),
            'recruiter_premium_annual': (RECRUITER_PREMIUM_ANNUAL, 'year', 'MedMatch Recruiter Premium (Annual)', 'Unlimited posts, ATS integration, API access, dedicated support - Save 2 months!'),
        }
        
        if plan in recruiter_plans:
            price, interval, name, description = recruiter_plans[plan]
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': name,
                            'description': description,
                        },
                        'unit_amount': int(price * 100),
                        'recurring': {
                            'interval': interval,
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
                    'plan': plan,
                    'role': 'recruiter'
                }
            )
        elif plan == 'job_seeker_3_year' or plan == 'premium_3_year':
            # Job seeker 3-year premium membership - $3 one-time
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'MedMatch Premium (3 Years)',
                            'description': 'Full access to all premium features for 3 years',
                        },
                        'unit_amount': int(JOB_SEEKER_3_YEAR_PRICE * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=checkout_request.success_url + ('&' if '?' in checkout_request.success_url else '?') + 'session_id={CHECKOUT_SESSION_ID}',
                cancel_url=checkout_request.cancel_url,
                customer_email=user['email'],
                metadata={
                    'user_id': user['user_id'],
                    'plan': 'premium_3_year',
                    'role': 'job_seeker'
                }
            )
        else:
            # Fallback - Job seeker 3-year premium
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'MedMatch Premium (3 Years)',
                            'description': 'Full access to all premium features for 3 years',
                        },
                        'unit_amount': int(JOB_SEEKER_3_YEAR_PRICE * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=checkout_request.success_url + ('&' if '?' in checkout_request.success_url else '?') + 'session_id={CHECKOUT_SESSION_ID}',
                cancel_url=checkout_request.cancel_url,
                customer_email=user['email'],
                metadata={
                    'user_id': user['user_id'],
                    'plan': 'premium_3_year',
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
            plan = session.metadata.get('plan', 'premium_3_year')
            
            update_data = {
                "membership_status": "active",
                "membership_activated_at": datetime.now(timezone.utc).isoformat(),
                "payment_session_id": session_id
            }
            
            if is_subscription:
                # Recruiter subscription
                update_data["subscription_id"] = session.subscription
                update_data["subscription_plan"] = plan
                update_data["subscription_status"] = "active"
                # Trial ends in 30 days
                update_data["trial_ends_at"] = (datetime.now(timezone.utc) + timedelta(days=RECRUITER_TRIAL_DAYS)).isoformat()
            else:
                # Job seeker 3-year premium
                update_data["membership_plan"] = "premium_3_year"
                # Set expiry to 3 years from now
                update_data["membership_expires_at"] = (datetime.now(timezone.utc) + timedelta(days=1095)).isoformat()
            
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
    """Handle Stripe webhooks for subscription events"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        payload = await request.body()
        sig_header = request.headers.get('stripe-signature')
        webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
        
        # Verify webhook signature if secret is configured
        if webhook_secret and sig_header:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except stripe.error.SignatureVerificationError:
                raise HTTPException(status_code=400, detail="Invalid signature")
        else:
            # Fallback for development
            import json
            event_data = json.loads(payload.decode())
            event = stripe.Event.construct_from(event_data, stripe.api_key)
        
        logging.info(f"Stripe webhook received: {event.type}")
        
        # Handle different event types
        if event.type == 'checkout.session.completed':
            session = event.data.object
            user_id = session.metadata.get('user_id')
            
            if user_id:
                update_data = {
                    "membership_status": "active",
                    "membership_activated_at": datetime.now(timezone.utc).isoformat()
                }
                
                # If subscription, store subscription ID
                if session.subscription:
                    update_data["subscription_id"] = session.subscription
                    update_data["subscription_status"] = "active"
                
                await db.users.update_one(
                    {"user_id": user_id},
                    {"$set": update_data}
                )
                logging.info(f"Updated membership for user {user_id}")
        
        elif event.type == 'customer.subscription.updated':
            subscription = event.data.object
            # Find user by subscription ID
            user = await db.users.find_one({"subscription_id": subscription.id})
            if user:
                status = subscription.status
                update_data = {
                    "subscription_status": status,
                    "membership_status": "active" if status in ["active", "trialing"] else "expired"
                }
                
                # Update trial end date if in trial
                if subscription.trial_end:
                    update_data["trial_ends_at"] = datetime.fromtimestamp(
                        subscription.trial_end, tz=timezone.utc
                    ).isoformat()
                
                # Update current period end
                if subscription.current_period_end:
                    update_data["subscription_period_end"] = datetime.fromtimestamp(
                        subscription.current_period_end, tz=timezone.utc
                    ).isoformat()
                
                await db.users.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": update_data}
                )
                logging.info(f"Subscription updated for user {user['user_id']}: {status}")
        
        elif event.type == 'customer.subscription.deleted':
            subscription = event.data.object
            user = await db.users.find_one({"subscription_id": subscription.id})
            if user:
                await db.users.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {
                        "subscription_status": "canceled",
                        "membership_status": "expired",
                        "subscription_canceled_at": datetime.now(timezone.utc).isoformat()
                    }}
                )
                logging.info(f"Subscription canceled for user {user['user_id']}")
        
        elif event.type == 'invoice.payment_succeeded':
            invoice = event.data.object
            if invoice.subscription:
                user = await db.users.find_one({"subscription_id": invoice.subscription})
                if user:
                    # Store payment record
                    payment_record = {
                        "user_id": user["user_id"],
                        "invoice_id": invoice.id,
                        "amount": invoice.amount_paid / 100,
                        "currency": invoice.currency,
                        "status": "paid",
                        "paid_at": datetime.now(timezone.utc).isoformat(),
                        "period_start": datetime.fromtimestamp(invoice.period_start, tz=timezone.utc).isoformat(),
                        "period_end": datetime.fromtimestamp(invoice.period_end, tz=timezone.utc).isoformat()
                    }
                    await db.payment_history.insert_one(payment_record)
                    logging.info(f"Payment recorded for user {user['user_id']}: ${invoice.amount_paid/100}")
        
        elif event.type == 'invoice.payment_failed':
            invoice = event.data.object
            if invoice.subscription:
                user = await db.users.find_one({"subscription_id": invoice.subscription})
                if user:
                    await db.users.update_one(
                        {"user_id": user["user_id"]},
                        {"$set": {
                            "subscription_status": "past_due",
                            "payment_failed_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    logging.warning(f"Payment failed for user {user['user_id']}")
        
        return {"received": True}
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============== Subscription Management Routes ==============

@router.get("/subscription")
async def get_subscription_details(request: Request):
    """Get current subscription details for recruiter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscription_id = user.get("subscription_id")
    
    if not subscription_id:
        return {
            "has_subscription": False,
            "message": "No active subscription"
        }
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Get customer info
        customer = stripe.Customer.retrieve(subscription.customer)
        
        # Get default payment method
        payment_method = None
        if subscription.default_payment_method:
            pm = stripe.PaymentMethod.retrieve(subscription.default_payment_method)
            if pm.card:
                payment_method = {
                    "brand": pm.card.brand,
                    "last4": pm.card.last4,
                    "exp_month": pm.card.exp_month,
                    "exp_year": pm.card.exp_year
                }
        
        # Access subscription data - use start_date and billing_cycle_anchor for trial periods
        start_date = subscription.start_date or subscription.created
        billing_cycle_anchor = subscription.billing_cycle_anchor
        trial_end = subscription.trial_end
        canceled_at = subscription.canceled_at
        
        return {
            "has_subscription": True,
            "subscription_id": subscription.id,
            "status": subscription.status,
            "plan": "Recruiter Pro",
            "price": RECRUITER_STARTER_PRICE,  # Default price, actual varies by plan
            "interval": "month",
            "current_period_start": datetime.fromtimestamp(start_date, tz=timezone.utc).isoformat() if start_date else None,
            "current_period_end": datetime.fromtimestamp(billing_cycle_anchor, tz=timezone.utc).isoformat() if billing_cycle_anchor else None,
            "trial_end": datetime.fromtimestamp(trial_end, tz=timezone.utc).isoformat() if trial_end else None,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": datetime.fromtimestamp(canceled_at, tz=timezone.utc).isoformat() if canceled_at else None,
            "payment_method": payment_method,
            "customer_email": customer.email
        }
        
    except Exception as e:
        logging.error(f"Error fetching subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscription details")

@router.post("/subscription/cancel")
async def cancel_subscription(request: Request):
    """Cancel recruiter subscription (at period end)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscription_id = user.get("subscription_id")
    
    if not subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        # Cancel at period end (user keeps access until subscription period ends)
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
        
        # Update user record
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {
                "subscription_status": "canceling",
                "subscription_cancel_requested_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "success": True,
            "message": "Subscription will be canceled at the end of the current billing period",
            "cancel_at": datetime.fromtimestamp(subscription.current_period_end, tz=timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"Error canceling subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

@router.post("/subscription/reactivate")
async def reactivate_subscription(request: Request):
    """Reactivate a subscription that was set to cancel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscription_id = user.get("subscription_id")
    
    if not subscription_id:
        raise HTTPException(status_code=400, detail="No subscription to reactivate")
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        # Reactivate subscription
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False
        )
        
        # Update user record
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {
                "subscription_status": subscription.status,
                "subscription_cancel_requested_at": None
            }}
        )
        
        return {
            "success": True,
            "message": "Subscription reactivated successfully",
            "status": subscription.status
        }
        
    except Exception as e:
        logging.error(f"Error reactivating subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to reactivate subscription")

@router.get("/billing-history")
async def get_billing_history(request: Request):
    """Get payment/billing history for user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get from local database
    payments = await db.payment_history.find(
        {"user_id": user["user_id"]}
    ).sort("paid_at", -1).limit(12).to_list(12)
    
    # Convert ObjectIds to strings
    for payment in payments:
        payment["_id"] = str(payment["_id"])
    
    # Also try to get from Stripe if we have subscription
    subscription_id = user.get("subscription_id")
    stripe_invoices = []
    
    if subscription_id and STRIPE_API_KEY:
        try:
            import stripe
            stripe.api_key = STRIPE_API_KEY
            
            invoices = stripe.Invoice.list(
                subscription=subscription_id,
                limit=12
            )
            
            for inv in invoices.data:
                stripe_invoices.append({
                    "invoice_id": inv.id,
                    "amount": inv.amount_paid / 100 if inv.amount_paid else inv.total / 100,
                    "currency": inv.currency,
                    "status": inv.status,
                    "paid_at": datetime.fromtimestamp(inv.status_transitions.paid_at, tz=timezone.utc).isoformat() if inv.status_transitions.paid_at else None,
                    "period_start": datetime.fromtimestamp(inv.period_start, tz=timezone.utc).isoformat(),
                    "period_end": datetime.fromtimestamp(inv.period_end, tz=timezone.utc).isoformat(),
                    "invoice_pdf": inv.invoice_pdf,
                    "hosted_invoice_url": inv.hosted_invoice_url
                })
        except Exception as e:
            logging.error(f"Error fetching Stripe invoices: {e}")
    
    return {
        "local_payments": payments,
        "stripe_invoices": stripe_invoices
    }

@router.post("/update-payment-method")
async def create_payment_method_session(request: Request):
    """Create a Stripe session to update payment method"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    subscription_id = user.get("subscription_id")
    
    if not subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")
    
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Payment system not configured")
    
    try:
        import stripe
        stripe.api_key = STRIPE_API_KEY
        
        # Get subscription to find customer
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Create billing portal session
        session = stripe.billing_portal.Session.create(
            customer=subscription.customer,
            return_url=f"{os.environ.get('FRONTEND_URL', 'https://global-audit-dash.preview.emergentagent.com')}/membership?updated=true"
        )
        
        return {
            "url": session.url
        }
        
    except Exception as e:
        logging.error(f"Error creating billing portal session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment update session")

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
        except Exception:
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
        response["pricing"] = {
            "starter": {"monthly": RECRUITER_STARTER_PRICE, "annual": RECRUITER_STARTER_ANNUAL},
            "growth": {"monthly": RECRUITER_GROWTH_PRICE, "annual": RECRUITER_GROWTH_ANNUAL},
            "premium": {"monthly": RECRUITER_PREMIUM_PRICE, "annual": RECRUITER_PREMIUM_ANNUAL}
        }
        response["trial_days"] = RECRUITER_TRIAL_DAYS
        response["plan"] = user.get("subscription_plan", "recruiter_starter")
        response["subscription_status"] = user.get("subscription_status")
    else:
        response["price"] = JOB_SEEKER_3_YEAR_PRICE
        response["price_type"] = "3_year"
        response["trial_days"] = JOB_SEEKER_TRIAL_DAYS
        response["plan"] = user.get("membership_plan", "free")
        response["membership_expires_at"] = user.get("membership_expires_at")
    
    return response

@membership_router.get("/check-access/{feature}")
async def check_feature_access(feature: str, request: Request):
    """Check if user has access to a specific feature"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Admin bypass - check all admin indicators
    is_admin = (
        user.get("is_admin") or 
        user.get("role") == "admin" or 
        user.get("email") == "admin@medmatch.com"
    )
    if is_admin:
        return {
            "has_access": True, 
            "reason": "admin",
            "role": "admin",
            "membership_status": "admin",
            "is_admin": True
        }
    
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
