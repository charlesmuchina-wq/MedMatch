# PayPal Integration Guide for MedMatch

## Overview
This guide provides step-by-step instructions to integrate PayPal payments into MedMatch alongside the existing Stripe integration.

## Prerequisites
- PayPal Business Account
- PayPal Developer Account (developer.paypal.com)

## Step 1: Create PayPal App

1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/)
2. Log in with your PayPal Business account
3. Click "Apps & Credentials"
4. Click "Create App"
5. Enter app name: `MedMatch Payments`
6. Select "Merchant" as the app type
7. Click "Create App"

## Step 2: Get API Credentials

### Sandbox (Testing)
1. In the app dashboard, ensure "Sandbox" is selected
2. Copy the **Client ID** and **Secret**
3. Add to `/app/backend/.env`:
   ```
   PAYPAL_CLIENT_ID=<your-sandbox-client-id>
   PAYPAL_CLIENT_SECRET=<your-sandbox-secret>
   PAYPAL_MODE=sandbox
   ```

### Live (Production)
1. Switch to "Live" in the app dashboard
2. Copy the **Client ID** and **Secret**
3. Update `.env` for production:
   ```
   PAYPAL_CLIENT_ID=<your-live-client-id>
   PAYPAL_CLIENT_SECRET=<your-live-secret>
   PAYPAL_MODE=live
   ```

## Step 3: Configure Webhooks

1. In the PayPal Developer Dashboard, go to your app
2. Scroll to "Webhooks" section
3. Click "Add Webhook"
4. Enter Webhook URL: `https://your-domain.com/api/payments/paypal-webhook`
5. Select events to track:
   - `PAYMENT.SALE.COMPLETED`
   - `BILLING.SUBSCRIPTION.CREATED`
   - `BILLING.SUBSCRIPTION.CANCELLED`
   - `BILLING.SUBSCRIPTION.SUSPENDED`
   - `BILLING.SUBSCRIPTION.PAYMENT.FAILED`
6. Copy the **Webhook ID** and add to `.env`:
   ```
   PAYPAL_WEBHOOK_ID=<your-webhook-id>
   ```

## Step 4: Create Subscription Plans in PayPal

### Job Seeker Plan ($1 Lifetime)
1. Go to PayPal Dashboard > Products & Plans
2. Create Product: "MedMatch Job Seeker"
3. Create Plan with:
   - Name: "Lifetime Access"
   - Price: $1.00
   - Billing Cycle: One-time

### Recruiter Plan ($5/month)
1. Create Product: "MedMatch Recruiter"
2. Create Plan with:
   - Name: "Monthly Subscription"
   - Price: $5.00
   - Billing Cycle: Monthly
   - Trial: 30 days free

## Step 5: Backend Implementation

The backend route at `/app/backend/routes/payments.py` should be updated to include PayPal:

```python
# Add to payments.py

from paypalrestsdk import Api, Payment, BillingPlan, BillingAgreement

# Initialize PayPal
paypal_api = Api({
    'mode': os.environ.get('PAYPAL_MODE', 'sandbox'),
    'client_id': os.environ.get('PAYPAL_CLIENT_ID'),
    'client_secret': os.environ.get('PAYPAL_CLIENT_SECRET')
})

@router.post("/paypal/create-order")
async def create_paypal_order(request: Request):
    """Create PayPal order for one-time payment"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    plan_type = body.get("plan_type", "job_seeker")
    
    amount = "1.00" if plan_type == "job_seeker" else "5.00"
    
    payment = Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": f"{FRONTEND_URL}/payment/success",
            "cancel_url": f"{FRONTEND_URL}/payment/cancel"
        },
        "transactions": [{
            "amount": {
                "total": amount,
                "currency": "USD"
            },
            "description": f"MedMatch {plan_type.replace('_', ' ').title()} Membership"
        }]
    })
    
    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return {"approval_url": link.href, "payment_id": payment.id}
    
    raise HTTPException(status_code=500, detail="PayPal order creation failed")

@router.post("/paypal/execute-payment")
async def execute_paypal_payment(request: Request):
    """Execute PayPal payment after user approval"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    body = await request.json()
    payment_id = body.get("payment_id")
    payer_id = body.get("payer_id")
    
    payment = Payment.find(payment_id)
    
    if payment.execute({"payer_id": payer_id}):
        # Update user membership
        await update_user_membership(user["user_id"], payment)
        return {"success": True, "message": "Payment successful"}
    
    raise HTTPException(status_code=500, detail="Payment execution failed")

@router.post("/paypal-webhook")
async def paypal_webhook(request: Request):
    """Handle PayPal webhooks"""
    body = await request.json()
    event_type = body.get("event_type")
    
    # Verify webhook signature (recommended)
    # ...
    
    if event_type == "PAYMENT.SALE.COMPLETED":
        # Handle successful payment
        pass
    elif event_type == "BILLING.SUBSCRIPTION.CANCELLED":
        # Handle subscription cancellation
        pass
    
    return {"status": "received"}
```

## Step 6: Frontend Integration

Add PayPal button to the pricing page:

```jsx
// In PricingPage.jsx or MembershipPage.jsx

import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";

const PayPalPaymentButton = ({ planType, onSuccess }) => (
  <PayPalScriptProvider options={{ 
    "client-id": process.env.REACT_APP_PAYPAL_CLIENT_ID 
  }}>
    <PayPalButtons
      createOrder={async () => {
        const response = await apiClient.post('/api/payments/paypal/create-order', {
          plan_type: planType
        });
        return response.data.payment_id;
      }}
      onApprove={async (data) => {
        const response = await apiClient.post('/api/payments/paypal/execute-payment', {
          payment_id: data.orderID,
          payer_id: data.payerID
        });
        if (response.data.success) {
          onSuccess();
        }
      }}
      onError={(err) => {
        console.error('PayPal error:', err);
        toast.error('Payment failed');
      }}
    />
  </PayPalScriptProvider>
);
```

## Step 7: Install Dependencies

```bash
# Backend
pip install paypalrestsdk

# Frontend
yarn add @paypal/react-paypal-js
```

## Step 8: Environment Variables Summary

Add to `/app/backend/.env`:
```
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_MODE=sandbox  # or 'live' for production
PAYPAL_WEBHOOK_ID=your_webhook_id
```

Add to `/app/frontend/.env`:
```
REACT_APP_PAYPAL_CLIENT_ID=your_client_id
```

## Testing

### Sandbox Testing
1. Use PayPal sandbox test accounts
2. Go to developer.paypal.com > Sandbox > Accounts
3. Create test buyer and seller accounts
4. Use test buyer credentials to complete payments

### Test Card Numbers (PayPal Sandbox)
- Email: Any sandbox buyer email
- Password: Sandbox account password

## Troubleshooting

### Common Issues

1. **"INSTRUMENT_DECLINED"**
   - The test buyer account has insufficient funds
   - Use a different sandbox buyer account

2. **Webhook not received**
   - Verify webhook URL is publicly accessible
   - Check webhook events are selected
   - Verify SSL certificate is valid

3. **"PAYEE_ACCOUNT_INVALID"**
   - Ensure PayPal Business account is verified
   - Check that the account can receive payments

## Security Considerations

1. Never expose `PAYPAL_CLIENT_SECRET` to frontend
2. Always verify webhook signatures
3. Use HTTPS in production
4. Validate payment amounts server-side
5. Log all payment events for audit trail

## Support

- PayPal Developer Documentation: https://developer.paypal.com/docs/
- PayPal Technical Support: https://developer.paypal.com/support/
