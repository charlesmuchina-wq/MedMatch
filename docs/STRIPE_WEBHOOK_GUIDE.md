# Stripe Webhook Configuration Guide for MedMatch

## Overview
Webhooks allow Stripe to notify your application about events in real-time, such as successful payments, subscription changes, and failed charges.

## Prerequisites
- Stripe account with API keys configured in `/app/backend/.env`
- MedMatch application deployed to a publicly accessible URL

## Step 1: Access Stripe Dashboard

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Log in to your Stripe account
3. Navigate to **Developers** → **Webhooks**

## Step 2: Add Webhook Endpoint

### For Production
1. Click **"Add endpoint"**
2. Enter your webhook URL:
   ```
   https://immersive-karau.preview.emergentagent.com/api/payments/webhook/stripe
   ```
3. Select events to listen to (see Step 3)
4. Click **"Add endpoint"**

### For Testing/Development
1. Click **"Add endpoint"**
2. For local development, use [Stripe CLI](https://stripe.com/docs/stripe-cli) or a tunnel service like ngrok
3. Example with ngrok:
   ```bash
   ngrok http 8001
   # Use the generated URL: https://xxxx.ngrok.io/api/payments/webhook
   ```

## Step 3: Select Webhook Events

Select these events for MedMatch functionality:

### Payment Events
- `payment_intent.succeeded` - Payment completed successfully
- `payment_intent.payment_failed` - Payment failed
- `charge.succeeded` - Charge was successful
- `charge.failed` - Charge failed
- `charge.refunded` - Charge was refunded

### Subscription Events (Recruiter Plan)
- `customer.subscription.created` - New subscription started
- `customer.subscription.updated` - Subscription modified
- `customer.subscription.deleted` - Subscription cancelled
- `customer.subscription.trial_will_end` - Trial ending soon (3 days notice)
- `customer.subscription.paused` - Subscription paused

### Invoice Events
- `invoice.paid` - Invoice payment successful
- `invoice.payment_failed` - Invoice payment failed
- `invoice.upcoming` - Invoice will be created soon

### Customer Events
- `customer.created` - New customer created
- `customer.updated` - Customer info updated

## Step 4: Get Webhook Signing Secret

1. After creating the webhook, click on it to view details
2. Click **"Reveal"** under **Signing secret**
3. Copy the secret (starts with `whsec_`)
4. Add to your environment:

```bash
# Add to /app/backend/.env
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

## Step 5: Verify Backend Configuration

The MedMatch backend already has webhook handling at `/app/backend/routes/payments.py`:

```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle specific events
    if event["type"] == "payment_intent.succeeded":
        # Handle successful payment
        pass
    elif event["type"] == "customer.subscription.created":
        # Handle new subscription
        pass
    # ... more handlers
    
    return {"status": "success"}
```

## Step 6: Test Webhooks

### Using Stripe CLI (Recommended for Development)
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to local server
stripe listen --forward-to localhost:8001/api/payments/webhook

# In another terminal, trigger test events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

### Using Stripe Dashboard
1. Go to **Developers** → **Webhooks**
2. Click on your endpoint
3. Click **"Send test webhook"**
4. Select an event type and click **"Send test webhook"**

## Step 7: Monitor Webhook Delivery

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click on your endpoint
3. View **"Webhook attempts"** to see:
   - Successful deliveries (200 response)
   - Failed attempts (with error details)
   - Pending retries

## Webhook Event Handling Reference

### Payment Success Handler
```python
async def handle_payment_success(event):
    payment_intent = event["data"]["object"]
    user_id = payment_intent["metadata"].get("user_id")
    plan_type = payment_intent["metadata"].get("plan_type")
    
    # Update user membership
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {
            "membership_status": "active",
            "plan_type": plan_type,
            "payment_date": datetime.now(timezone.utc).isoformat()
        }}
    )
```

### Subscription Created Handler
```python
async def handle_subscription_created(event):
    subscription = event["data"]["object"]
    customer_id = subscription["customer"]
    
    # Find user by Stripe customer ID
    user = await db.users.find_one({"stripe_customer_id": customer_id})
    
    if user:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {
                "subscription_id": subscription["id"],
                "subscription_status": subscription["status"],
                "current_period_end": subscription["current_period_end"]
            }}
        )
```

### Subscription Cancelled Handler
```python
async def handle_subscription_cancelled(event):
    subscription = event["data"]["object"]
    customer_id = subscription["customer"]
    
    user = await db.users.find_one({"stripe_customer_id": customer_id})
    
    if user:
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {
                "subscription_status": "cancelled",
                "membership_status": "inactive",
                "cancelled_at": datetime.now(timezone.utc).isoformat()
            }}
        )
```

## Environment Variables Summary

Add these to `/app/backend/.env`:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_your_live_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_signing_secret

# For testing (use test keys)
# STRIPE_SECRET_KEY=sk_test_your_test_secret_key
# STRIPE_PUBLISHABLE_KEY=pk_test_your_test_publishable_key
# STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret
```

## Troubleshooting

### Common Issues

1. **"Invalid signature" error**
   - Verify `STRIPE_WEBHOOK_SECRET` is correct
   - Ensure you're using the signing secret from the specific webhook endpoint
   - Check that the raw request body is being used (not parsed JSON)

2. **Webhook not received**
   - Verify the endpoint URL is publicly accessible
   - Check firewall/security rules allow Stripe IPs
   - Ensure SSL certificate is valid (HTTPS required for production)

3. **Events arriving out of order**
   - Webhooks may arrive out of order
   - Use `event.created` timestamp for ordering
   - Implement idempotency using `event.id`

4. **Duplicate events**
   - Stripe may retry failed webhooks
   - Store processed `event.id` values and skip duplicates

### Stripe IP Addresses
For firewall configuration, allow Stripe webhook IPs:
- See: https://stripe.com/docs/ips

## Security Best Practices

1. **Always verify signatures** - Never process webhooks without signature verification
2. **Use HTTPS** - Required for production webhooks
3. **Respond quickly** - Return 200 within 30 seconds, process async if needed
4. **Handle retries** - Stripe retries failed webhooks for up to 3 days
5. **Log events** - Keep audit trail of all webhook events
6. **Test thoroughly** - Use Stripe CLI to test all event types

## Production Checklist

- [ ] Webhook endpoint URL configured in Stripe Dashboard
- [ ] `STRIPE_WEBHOOK_SECRET` added to production environment
- [ ] All relevant event types selected
- [ ] Signature verification enabled in webhook handler
- [ ] Error handling and logging implemented
- [ ] Webhook delivery tested and confirmed
- [ ] Monitoring/alerting set up for failed webhooks

## Support

- Stripe Webhooks Documentation: https://stripe.com/docs/webhooks
- Stripe CLI: https://stripe.com/docs/stripe-cli
- Stripe Support: https://support.stripe.com/
