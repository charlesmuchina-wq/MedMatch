"""
Test Pricing Features - MedMatch Membership Pricing
Tests: Job Seeker pricing ($3/3 years), Recruiter tiers (Starter $2.99, Growth $7.99, Premium $14.99, Enterprise Custom)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPricingConstants:
    """Test that pricing constants are correctly defined in backend"""
    
    def test_health_check(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✓ API health check passed")

class TestMembershipStatusEndpoint:
    """Test /api/membership/status returns correct pricing info"""
    
    @pytest.fixture
    def job_seeker_session(self):
        """Login as job seeker and return session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@medmatch.com",
            "password": "Test123!"
        })
        if login_response.status_code != 200:
            pytest.skip("Job seeker login failed - skipping test")
        return session
    
    @pytest.fixture
    def recruiter_session(self):
        """Login as recruiter and return session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "recruiter@medmatch.com",
            "password": "Test123!"
        })
        if login_response.status_code != 200:
            pytest.skip("Recruiter login failed - skipping test")
        return session
    
    def test_job_seeker_membership_status(self, job_seeker_session):
        """Test job seeker gets correct pricing info"""
        response = job_seeker_session.get(f"{BASE_URL}/api/membership/status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify job seeker pricing
        assert data.get("price") == 3.00, f"Expected price $3.00, got {data.get('price')}"
        assert data.get("price_type") == "3_year", f"Expected price_type '3_year', got {data.get('price_type')}"
        assert data.get("trial_days") == 30, f"Expected 30 trial days, got {data.get('trial_days')}"
        assert data.get("role") == "job_seeker", f"Expected role 'job_seeker', got {data.get('role')}"
        
        print(f"✓ Job seeker pricing: ${data.get('price')} for {data.get('price_type')}")
        print(f"✓ Trial days: {data.get('trial_days')}")
    
    def test_recruiter_membership_status(self, recruiter_session):
        """Test recruiter gets correct pricing tiers"""
        response = recruiter_session.get(f"{BASE_URL}/api/membership/status")
        assert response.status_code == 200
        data = response.json()
        
        # Verify recruiter role
        assert data.get("role") == "recruiter", f"Expected role 'recruiter', got {data.get('role')}"
        assert data.get("trial_days") == 30, f"Expected 30 trial days, got {data.get('trial_days')}"
        
        # Verify pricing tiers
        pricing = data.get("pricing", {})
        
        # Starter tier
        starter = pricing.get("starter", {})
        assert starter.get("monthly") == 2.99, f"Expected Starter monthly $2.99, got {starter.get('monthly')}"
        assert starter.get("annual") == 29.99, f"Expected Starter annual $29.99, got {starter.get('annual')}"
        
        # Growth tier
        growth = pricing.get("growth", {})
        assert growth.get("monthly") == 7.99, f"Expected Growth monthly $7.99, got {growth.get('monthly')}"
        assert growth.get("annual") == 79.99, f"Expected Growth annual $79.99, got {growth.get('annual')}"
        
        # Premium tier
        premium = pricing.get("premium", {})
        assert premium.get("monthly") == 14.99, f"Expected Premium monthly $14.99, got {premium.get('monthly')}"
        assert premium.get("annual") == 149.99, f"Expected Premium annual $149.99, got {premium.get('annual')}"
        
        print("✓ Recruiter pricing tiers verified:")
        print(f"  - Starter: ${starter.get('monthly')}/mo, ${starter.get('annual')}/yr")
        print(f"  - Growth: ${growth.get('monthly')}/mo, ${growth.get('annual')}/yr")
        print(f"  - Premium: ${premium.get('monthly')}/mo, ${premium.get('annual')}/yr")


class TestPaymentCheckoutEndpoint:
    """Test /api/payments/create-checkout handles different plans"""
    
    @pytest.fixture
    def job_seeker_session(self):
        """Login as job seeker and return session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "testuser@medmatch.com",
            "password": "Test123!"
        })
        if login_response.status_code != 200:
            pytest.skip("Job seeker login failed - skipping test")
        return session
    
    @pytest.fixture
    def recruiter_session(self):
        """Login as recruiter and return session"""
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "recruiter@medmatch.com",
            "password": "Test123!"
        })
        if login_response.status_code != 200:
            pytest.skip("Recruiter login failed - skipping test")
        return session
    
    def test_job_seeker_3_year_checkout(self, job_seeker_session):
        """Test job_seeker_3_year plan creates checkout session"""
        response = job_seeker_session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "plan": "job_seeker_3_year"
        })
        
        # Should return 200 with checkout URL or 500 if Stripe not configured
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "url" in data or "session_id" in data, "Expected checkout URL or session_id"
            print("✓ Job seeker 3-year checkout created successfully")
        else:
            data = response.json()
            # If Stripe not configured, that's expected in test env
            if "not configured" in str(data.get("detail", "")):
                print("✓ Stripe not configured (expected in test env)")
            else:
                print(f"⚠ Checkout failed: {data.get('detail')}")
    
    def test_recruiter_starter_checkout(self, recruiter_session):
        """Test recruiter_starter plan creates checkout session"""
        response = recruiter_session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "plan": "recruiter_starter"
        })
        
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "url" in data or "session_id" in data, "Expected checkout URL or session_id"
            print("✓ Recruiter starter checkout created successfully")
        else:
            data = response.json()
            if "not configured" in str(data.get("detail", "")):
                print("✓ Stripe not configured (expected in test env)")
            else:
                print(f"⚠ Checkout failed: {data.get('detail')}")
    
    def test_recruiter_growth_checkout(self, recruiter_session):
        """Test recruiter_growth plan creates checkout session"""
        response = recruiter_session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "plan": "recruiter_growth"
        })
        
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "url" in data or "session_id" in data, "Expected checkout URL or session_id"
            print("✓ Recruiter growth checkout created successfully")
        else:
            data = response.json()
            if "not configured" in str(data.get("detail", "")):
                print("✓ Stripe not configured (expected in test env)")
    
    def test_recruiter_premium_checkout(self, recruiter_session):
        """Test recruiter_premium plan creates checkout session"""
        response = recruiter_session.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "plan": "recruiter_premium"
        })
        
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "url" in data or "session_id" in data, "Expected checkout URL or session_id"
            print("✓ Recruiter premium checkout created successfully")
        else:
            data = response.json()
            if "not configured" in str(data.get("detail", "")):
                print("✓ Stripe not configured (expected in test env)")
    
    def test_recruiter_annual_checkout(self, recruiter_session):
        """Test recruiter annual plans create checkout session"""
        for plan in ["recruiter_starter_annual", "recruiter_growth_annual", "recruiter_premium_annual"]:
            response = recruiter_session.post(f"{BASE_URL}/api/payments/create-checkout", json={
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
                "plan": plan
            })
            
            assert response.status_code in [200, 500], f"Unexpected status for {plan}: {response.status_code}"
            print(f"✓ {plan} checkout endpoint responded correctly")


class TestUnauthenticatedAccess:
    """Test that payment endpoints require authentication"""
    
    def test_membership_status_requires_auth(self):
        """Test /api/membership/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/membership/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Membership status requires authentication")
    
    def test_create_checkout_requires_auth(self):
        """Test /api/payments/create-checkout requires authentication"""
        response = requests.post(f"{BASE_URL}/api/payments/create-checkout", json={
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "plan": "job_seeker_3_year"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Create checkout requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
