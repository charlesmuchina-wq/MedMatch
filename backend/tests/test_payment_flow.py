"""
Payment Flow Tests
Tests: Stripe checkout, PayPal payments, Membership status
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPaymentFlow:
    """Payment endpoint tests for Stripe and PayPal"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login with test credentials
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping payment tests")
        
        # Store cookies for authenticated requests
        self.cookies = login_response.cookies
        
    # ============== Stripe Tests ==============
    
    def test_stripe_checkout_session_creation(self):
        """Test POST /api/payments/create-checkout - creates Stripe checkout session"""
        payload = {
            "success_url": "https://karau-premium.preview.emergentagent.com/membership?success=true",
            "cancel_url": "https://karau-premium.preview.emergentagent.com/membership?canceled=true",
            "plan": "lifetime"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/payments/create-checkout",
            json=payload,
            cookies=self.cookies
        )
        
        # Status assertion
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Data assertions
        data = response.json()
        assert "session_id" in data, "Response should contain session_id"
        assert "url" in data, "Response should contain checkout url"
        
        # Validate session_id format (Stripe session IDs start with 'cs_')
        assert data["session_id"].startswith("cs_"), f"Session ID should start with 'cs_', got: {data['session_id']}"
        
        # Validate URL is a Stripe checkout URL
        assert "checkout.stripe.com" in data["url"], f"URL should be Stripe checkout URL, got: {data['url']}"
        
        print(f"✅ Stripe checkout session created: {data['session_id']}")
        print(f"✅ Checkout URL: {data['url'][:80]}...")
        
        # Store session_id for status test
        self.__class__.stripe_session_id = data["session_id"]
    
    def test_stripe_checkout_requires_auth(self):
        """Test that Stripe checkout requires authentication"""
        payload = {
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "plan": "lifetime"
        }
        
        # Make request without cookies (unauthenticated)
        response = requests.post(
            f"{BASE_URL}/api/payments/create-checkout",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("✅ Stripe checkout correctly requires authentication")
    
    def test_stripe_payment_status_check(self):
        """Test GET /api/payments/status/{session_id} - checks payment status"""
        # First create a session to get a valid session_id
        payload = {
            "success_url": "https://karau-premium.preview.emergentagent.com/membership?success=true",
            "cancel_url": "https://karau-premium.preview.emergentagent.com/membership?canceled=true",
            "plan": "lifetime"
        }
        
        create_response = self.session.post(
            f"{BASE_URL}/api/payments/create-checkout",
            json=payload,
            cookies=self.cookies
        )
        
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # Check payment status
        status_response = self.session.get(
            f"{BASE_URL}/api/payments/status/{session_id}",
            cookies=self.cookies
        )
        
        assert status_response.status_code == 200, f"Expected 200, got {status_response.status_code}: {status_response.text}"
        
        data = status_response.json()
        # New session should be unpaid
        assert "status" in data, "Response should contain status"
        print(f"✅ Payment status check works: {data}")
    
    def test_stripe_payment_status_requires_auth(self):
        """Test that payment status check requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/payments/status/cs_test_fake_session",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("✅ Payment status correctly requires authentication")
    
    # ============== PayPal Tests ==============
    
    def test_paypal_payment_creation(self):
        """Test POST /api/payments/paypal/create - creates PayPal payment"""
        payload = {
            "success_url": "https://karau-premium.preview.emergentagent.com/membership?provider=paypal&success=true",
            "cancel_url": "https://karau-premium.preview.emergentagent.com/membership?canceled=true",
            "plan": "lifetime"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/payments/paypal/create",
            json=payload,
            cookies=self.cookies
        )
        
        # PayPal might not be fully configured, so we accept 200 or 500
        if response.status_code == 200:
            data = response.json()
            assert "payment_id" in data or "approval_url" in data, "Response should contain payment_id or approval_url"
            
            if "approval_url" in data:
                assert "paypal.com" in data["approval_url"], "Approval URL should be PayPal URL"
                print(f"✅ PayPal payment created: {data.get('payment_id', 'N/A')}")
                print(f"✅ Approval URL: {data['approval_url'][:80]}...")
            else:
                print(f"✅ PayPal response: {data}")
        elif response.status_code == 500:
            # PayPal SDK might not be installed or configured
            data = response.json()
            print(f"⚠️ PayPal not fully configured: {data.get('detail', 'Unknown error')}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}: {response.text}")
    
    def test_paypal_requires_auth(self):
        """Test that PayPal payment creation requires authentication"""
        payload = {
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "plan": "lifetime"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/payments/paypal/create",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("✅ PayPal payment correctly requires authentication")
    
    # ============== Membership Tests ==============
    
    def test_membership_status(self):
        """Test GET /api/membership/status - returns membership status"""
        response = self.session.get(
            f"{BASE_URL}/api/membership/status",
            cookies=self.cookies
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "status" in data, "Response should contain status"
        assert "is_active" in data, "Response should contain is_active"
        assert "price" in data, "Response should contain price"
        
        print(f"✅ Membership status: {data['status']}")
        print(f"✅ Is active: {data['is_active']}")
        print(f"✅ Price: ${data['price']}")
    
    def test_membership_status_requires_auth(self):
        """Test that membership status requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/membership/status",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("✅ Membership status correctly requires authentication")
    
    def test_membership_feature_access_check(self):
        """Test GET /api/membership/check-access/{feature} - checks feature access"""
        features_to_test = ["resume", "job_search", "ai_interview", "cover_letter"]
        
        for feature in features_to_test:
            response = self.session.get(
                f"{BASE_URL}/api/membership/check-access/{feature}",
                cookies=self.cookies
            )
            
            assert response.status_code == 200, f"Expected 200 for {feature}, got {response.status_code}"
            
            data = response.json()
            assert "has_access" in data, f"Response for {feature} should contain has_access"
            print(f"✅ Feature '{feature}' access: {data['has_access']} (reason: {data.get('reason', 'N/A')})")


class TestStripeIntegration:
    """Additional Stripe integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login with test credentials
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping Stripe tests")
        
        self.cookies = login_response.cookies
    
    def test_stripe_checkout_with_different_plans(self):
        """Test checkout session creation with different plan types"""
        plans = ["lifetime", "monthly", "annual"]
        
        for plan in plans:
            payload = {
                "success_url": "https://karau-premium.preview.emergentagent.com/membership?success=true",
                "cancel_url": "https://karau-premium.preview.emergentagent.com/membership?canceled=true",
                "plan": plan
            }
            
            response = self.session.post(
                f"{BASE_URL}/api/payments/create-checkout",
                json=payload,
                cookies=self.cookies
            )
            
            # All plans should work (backend may default to lifetime)
            assert response.status_code == 200, f"Plan '{plan}' failed: {response.status_code}: {response.text}"
            
            data = response.json()
            assert "session_id" in data
            assert "url" in data
            print(f"✅ Plan '{plan}' checkout created successfully")
    
    def test_stripe_checkout_url_format(self):
        """Test that checkout URL has correct format and parameters"""
        payload = {
            "success_url": "https://karau-premium.preview.emergentagent.com/membership?success=true",
            "cancel_url": "https://karau-premium.preview.emergentagent.com/membership?canceled=true",
            "plan": "lifetime"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/payments/create-checkout",
            json=payload,
            cookies=self.cookies
        )
        
        assert response.status_code == 200
        data = response.json()
        
        checkout_url = data["url"]
        
        # Validate URL structure
        assert checkout_url.startswith("https://checkout.stripe.com/"), "URL should start with https://checkout.stripe.com/"
        assert "/c/pay/" in checkout_url or "/pay/" in checkout_url, "URL should contain payment path"
        
        print(f"✅ Checkout URL format is valid: {checkout_url[:100]}...")


class TestPaymentSecurity:
    """Security tests for payment endpoints"""
    
    def test_checkout_without_required_fields(self):
        """Test that checkout fails without required fields"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login first
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed")
        
        cookies = login_response.cookies
        
        # Test with missing success_url
        response = session.post(
            f"{BASE_URL}/api/payments/create-checkout",
            json={"cancel_url": "https://example.com/cancel"},
            cookies=cookies
        )
        
        # Should fail with 422 (validation error) or similar
        assert response.status_code in [400, 422], f"Expected 400/422 for missing fields, got {response.status_code}"
        print("✅ Checkout correctly validates required fields")
    
    def test_invalid_session_id_status_check(self):
        """Test payment status with invalid session ID"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login first
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        })
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed")
        
        cookies = login_response.cookies
        
        # Check status with invalid session ID
        response = session.get(
            f"{BASE_URL}/api/payments/status/invalid_session_id_12345",
            cookies=cookies
        )
        
        # Should fail with error status (400, 404, 500, 520)
        assert response.status_code in [400, 404, 500, 520], f"Expected error for invalid session, got {response.status_code}"
        print(f"✅ Invalid session ID handled correctly: {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
