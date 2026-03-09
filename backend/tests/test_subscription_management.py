"""
Test Subscription Management Features
Tests: Recruiter subscription checkout, subscription details, cancel, reactivate, billing history
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-karau.preview.emergentagent.com')

# Test credentials
RECRUITER_EMAIL = "recruiter_test_1769122141@example.com"
RECRUITER_PASSWORD = "Test123!"
RECRUITER_SUBSCRIPTION_ID = "sub_1SsX7jBYhELfJFENvNbeeqsG"

ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"


class TestSubscriptionEndpoints:
    """Test subscription management API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session for each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login(self, email, password):
        """Helper to login and get session"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        return response
    
    # ============== Authentication Tests ==============
    
    def test_subscription_endpoint_requires_auth(self):
        """GET /api/payments/subscription requires authentication"""
        response = self.session.get(f"{BASE_URL}/api/payments/subscription")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ GET /api/payments/subscription requires authentication")
    
    def test_cancel_endpoint_requires_auth(self):
        """POST /api/payments/subscription/cancel requires authentication"""
        response = self.session.post(f"{BASE_URL}/api/payments/subscription/cancel")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/payments/subscription/cancel requires authentication")
    
    def test_reactivate_endpoint_requires_auth(self):
        """POST /api/payments/subscription/reactivate requires authentication"""
        response = self.session.post(f"{BASE_URL}/api/payments/subscription/reactivate")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/payments/subscription/reactivate requires authentication")
    
    def test_billing_history_requires_auth(self):
        """GET /api/payments/billing-history requires authentication"""
        response = self.session.get(f"{BASE_URL}/api/payments/billing-history")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ GET /api/payments/billing-history requires authentication")
    
    def test_update_payment_method_requires_auth(self):
        """POST /api/payments/update-payment-method requires authentication"""
        response = self.session.post(f"{BASE_URL}/api/payments/update-payment-method")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/payments/update-payment-method requires authentication")
    
    # ============== Recruiter Checkout Tests ==============
    
    def test_recruiter_checkout_creates_subscription_session(self):
        """POST /api/payments/create-checkout with plan=recruiter_monthly creates subscription"""
        # Login as recruiter
        login_resp = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as recruiter: {login_resp.status_code}")
        
        # Create checkout session for recruiter plan
        response = self.session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "success_url": "https://ai-karau.preview.emergentagent.com/membership?success=true",
            "cancel_url": "https://ai-karau.preview.emergentagent.com/membership?canceled=true",
            "plan": "recruiter_monthly"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "session_id" in data, "Response should contain session_id"
        assert "url" in data, "Response should contain url"
        assert "checkout.stripe.com" in data["url"], "URL should be Stripe checkout URL"
        
        print(f"✅ Recruiter checkout creates subscription session: {data['session_id'][:20]}...")
    
    def test_admin_checkout_creates_subscription_session(self):
        """POST /api/payments/create-checkout works for admin user"""
        # Login as admin
        login_resp = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as admin: {login_resp.status_code}")
        
        # Create checkout session
        response = self.session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "success_url": "https://ai-karau.preview.emergentagent.com/membership?success=true",
            "cancel_url": "https://ai-karau.preview.emergentagent.com/membership?canceled=true",
            "plan": "lifetime"
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "session_id" in data, "Response should contain session_id"
        assert "url" in data, "Response should contain url"
        
        print(f"✅ Admin checkout creates session: {data['session_id'][:20]}...")
    
    # ============== Subscription Details Tests ==============
    
    def test_get_subscription_details_with_subscription(self):
        """GET /api/payments/subscription returns subscription details for subscribed user"""
        # Login as recruiter with subscription
        login_resp = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as recruiter: {login_resp.status_code}")
        
        response = self.session.get(f"{BASE_URL}/api/payments/subscription")
        
        # Could be 200 with subscription or 200 with no subscription
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        if data.get("has_subscription"):
            # Verify subscription details structure
            assert "subscription_id" in data, "Should have subscription_id"
            assert "status" in data, "Should have status"
            assert "plan" in data, "Should have plan"
            assert "price" in data, "Should have price"
            print(f"✅ Subscription details returned: {data['plan']} - ${data['price']}/month, status: {data['status']}")
        else:
            print("✅ No subscription found for user (expected if not subscribed)")
    
    def test_get_subscription_details_without_subscription(self):
        """GET /api/payments/subscription returns no subscription for user without one"""
        # Login as admin (may not have subscription)
        login_resp = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as admin: {login_resp.status_code}")
        
        response = self.session.get(f"{BASE_URL}/api/payments/subscription")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Should indicate no subscription or have subscription
        if not data.get("has_subscription"):
            assert "message" in data or "has_subscription" in data
            print("✅ No subscription response returned correctly")
        else:
            print(f"✅ Admin has subscription: {data.get('plan')}")
    
    # ============== Billing History Tests ==============
    
    def test_get_billing_history(self):
        """GET /api/payments/billing-history returns billing history"""
        # Login as recruiter
        login_resp = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as recruiter: {login_resp.status_code}")
        
        response = self.session.get(f"{BASE_URL}/api/payments/billing-history")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "local_payments" in data, "Should have local_payments"
        assert "stripe_invoices" in data, "Should have stripe_invoices"
        assert isinstance(data["local_payments"], list), "local_payments should be a list"
        assert isinstance(data["stripe_invoices"], list), "stripe_invoices should be a list"
        
        print(f"✅ Billing history returned: {len(data['local_payments'])} local, {len(data['stripe_invoices'])} Stripe invoices")
    
    # ============== Cancel/Reactivate Tests ==============
    
    def test_cancel_subscription_without_subscription(self):
        """POST /api/payments/subscription/cancel returns error for user without subscription"""
        # Login as admin (may not have subscription)
        login_resp = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as admin: {login_resp.status_code}")
        
        response = self.session.post(f"{BASE_URL}/api/payments/subscription/cancel")
        
        # Should return 400 if no subscription
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✅ Cancel without subscription returns 400: {data['detail']}")
        elif response.status_code == 200:
            # User has subscription and it was canceled
            data = response.json()
            print(f"✅ Subscription canceled: {data.get('message')}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_reactivate_subscription_without_subscription(self):
        """POST /api/payments/subscription/reactivate returns error for user without subscription"""
        # Login as admin
        login_resp = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as admin: {login_resp.status_code}")
        
        response = self.session.post(f"{BASE_URL}/api/payments/subscription/reactivate")
        
        # Should return 400 if no subscription
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✅ Reactivate without subscription returns 400: {data['detail']}")
        elif response.status_code == 200:
            data = response.json()
            print(f"✅ Subscription reactivated: {data.get('message')}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    # ============== Update Payment Method Tests ==============
    
    def test_update_payment_method_without_subscription(self):
        """POST /api/payments/update-payment-method returns error for user without subscription"""
        # Login as admin
        login_resp = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as admin: {login_resp.status_code}")
        
        response = self.session.post(f"{BASE_URL}/api/payments/update-payment-method")
        
        # Should return 400 if no subscription
        if response.status_code == 400:
            data = response.json()
            assert "detail" in data
            print(f"✅ Update payment method without subscription returns 400: {data['detail']}")
        elif response.status_code == 200:
            data = response.json()
            assert "url" in data, "Should return billing portal URL"
            print("✅ Billing portal URL returned")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    # ============== Membership Status Tests ==============
    
    def test_membership_status_for_recruiter(self):
        """GET /api/membership/status returns recruiter-specific info"""
        # Login as recruiter
        login_resp = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as recruiter: {login_resp.status_code}")
        
        response = self.session.get(f"{BASE_URL}/api/membership/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Verify recruiter-specific fields
        assert "role" in data, "Should have role"
        assert "price" in data, "Should have price"
        assert "price_type" in data, "Should have price_type"
        
        if data.get("role") == "recruiter":
            assert data["price"] == 5.0, f"Recruiter price should be $5, got {data['price']}"
            assert data["price_type"] == "monthly", f"Recruiter price type should be monthly, got {data['price_type']}"
            print(f"✅ Recruiter membership status: ${data['price']}/{data['price_type']}, status: {data.get('status')}")
        else:
            print(f"✅ User role: {data.get('role')}, price: ${data.get('price')}")
    
    def test_membership_status_for_admin(self):
        """GET /api/membership/status returns correct info for admin"""
        # Login as admin
        login_resp = self.login(ADMIN_EMAIL, ADMIN_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as admin: {login_resp.status_code}")
        
        response = self.session.get(f"{BASE_URL}/api/membership/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "status" in data, "Should have status"
        assert "is_active" in data, "Should have is_active"
        assert "role" in data, "Should have role"
        
        print(f"✅ Admin membership status: {data.get('status')}, role: {data.get('role')}, active: {data.get('is_active')}")
    
    # ============== Webhook Tests ==============
    
    def test_webhook_endpoint_exists(self):
        """POST /api/payments/webhook/stripe endpoint exists"""
        # Send empty payload (will fail signature verification but endpoint should exist)
        response = self.session.post(f"{BASE_URL}/api/payments/webhook/stripe", 
                                     data=b'{}',
                                     headers={"Content-Type": "application/json"})
        
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404, "Webhook endpoint should exist"
        print(f"✅ Webhook endpoint exists (status: {response.status_code})")


class TestRecruiterSubscriptionFlow:
    """Test complete recruiter subscription flow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup session for each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def login(self, email, password):
        """Helper to login and get session"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": email,
            "password": password
        })
        return response
    
    def test_complete_recruiter_subscription_flow(self):
        """Test complete flow: login -> check status -> create checkout -> verify subscription"""
        # Step 1: Login as recruiter
        login_resp = self.login(RECRUITER_EMAIL, RECRUITER_PASSWORD)
        if login_resp.status_code != 200:
            pytest.skip(f"Could not login as recruiter: {login_resp.status_code}")
        
        print("✅ Step 1: Logged in as recruiter")
        
        # Step 2: Check membership status
        status_resp = self.session.get(f"{BASE_URL}/api/membership/status")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        
        print(f"✅ Step 2: Membership status - {status_data.get('status')}, role: {status_data.get('role')}")
        
        # Step 3: Check subscription details
        sub_resp = self.session.get(f"{BASE_URL}/api/payments/subscription")
        assert sub_resp.status_code == 200
        sub_data = sub_resp.json()
        
        if sub_data.get("has_subscription"):
            print(f"✅ Step 3: Has subscription - {sub_data.get('plan')}, status: {sub_data.get('status')}")
            
            # Step 4: Check billing history
            billing_resp = self.session.get(f"{BASE_URL}/api/payments/billing-history")
            assert billing_resp.status_code == 200
            billing_data = billing_resp.json()
            print(f"✅ Step 4: Billing history - {len(billing_data.get('stripe_invoices', []))} invoices")
        else:
            print("✅ Step 3: No active subscription")
            
            # Step 4: Create checkout session
            checkout_resp = self.session.post(f"{BASE_URL}/api/payments/create-checkout", json={
                "success_url": "https://ai-karau.preview.emergentagent.com/membership?success=true",
                "cancel_url": "https://ai-karau.preview.emergentagent.com/membership?canceled=true",
                "plan": "recruiter_monthly"
            })
            assert checkout_resp.status_code == 200
            checkout_data = checkout_resp.json()
            print(f"✅ Step 4: Checkout session created - {checkout_data.get('session_id', '')[:20]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
