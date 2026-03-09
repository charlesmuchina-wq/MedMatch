"""
ENZI Batch C - Payments & Behavioral Modeling Tests (Iteration 197)
Tests Stripe payments (via emergentintegrations) and behavioral modeling endpoints.

Features tested:
- GET /api/lumi/payments/packages - returns 4 premium packages
- POST /api/lumi/payments/checkout - creates Stripe checkout session
- GET /api/lumi/payments/my-subscription - returns user subscription status
- GET /api/lumi/payments/history - returns payment transactions
- GET /api/lumi/payments/status/{session_id} - polls payment status
- GET /api/lumi/behavior/context-triggers - returns context-aware triggers
- GET /api/lumi/behavior/smart-suggestions - returns personalized suggestions
- GET /api/lumi/behavior/usage-insights - returns engagement score and stats
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestAuthentication:
    """Test authentication for Batch C tests"""
    
    def test_admin_login(self):
        """Test login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        print(f"PASS: Admin login successful, user_id: {data['user'].get('user_id')}")


@pytest.fixture(scope="class")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.text}")
    return response.json().get("access_token")


@pytest.fixture
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


class TestPaymentsPackages:
    """Test premium packages endpoint"""
    
    def test_get_packages_returns_4_packages(self, auth_headers):
        """GET /api/lumi/payments/packages returns 4 premium packages"""
        response = requests.get(f"{BASE_URL}/api/lumi/payments/packages", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "packages" in data, "No 'packages' key in response"
        packages = data["packages"]
        assert len(packages) == 4, f"Expected 4 packages, got {len(packages)}"
        
        # Verify expected package IDs
        package_ids = [p["id"] for p in packages]
        assert "pro_monthly" in package_ids, "Missing pro_monthly package"
        assert "pro_yearly" in package_ids, "Missing pro_yearly package"
        assert "team_monthly" in package_ids, "Missing team_monthly package"
        assert "enterprise" in package_ids, "Missing enterprise package"
        
        # Verify packages have required fields
        for pkg in packages:
            assert "id" in pkg, f"Package missing 'id': {pkg}"
            assert "name" in pkg, f"Package missing 'name': {pkg}"
            assert "amount" in pkg, f"Package missing 'amount': {pkg}"
            assert "currency" in pkg, f"Package missing 'currency': {pkg}"
            assert "features" in pkg, f"Package missing 'features': {pkg}"
            assert isinstance(pkg["features"], list), f"Features should be a list: {pkg['features']}"
            assert len(pkg["features"]) > 0, f"Package {pkg['id']} should have features"
        
        print(f"PASS: Got {len(packages)} packages: {package_ids}")
    
    def test_packages_have_correct_pricing(self, auth_headers):
        """Verify package pricing"""
        response = requests.get(f"{BASE_URL}/api/lumi/payments/packages", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        packages = {p["id"]: p for p in data["packages"]}
        
        # Check pricing
        assert packages["pro_monthly"]["amount"] == 9.99, "Pro monthly should be $9.99"
        assert packages["pro_yearly"]["amount"] == 99.99, "Pro yearly should be $99.99"
        assert packages["team_monthly"]["amount"] == 29.99, "Team monthly should be $29.99"
        assert packages["enterprise"]["amount"] == 99.99, "Enterprise should be $99.99"
        
        print("PASS: All packages have correct pricing")


class TestPaymentsCheckout:
    """Test Stripe checkout endpoint"""
    
    def test_checkout_creates_stripe_session(self, auth_headers):
        """POST /api/lumi/payments/checkout creates Stripe checkout session"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/payments/checkout",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "package_id": "pro_monthly",
                "origin_url": "https://ai-karau.preview.emergentagent.com"
            }
        )
        assert response.status_code == 200, f"Checkout failed: {response.text}"
        data = response.json()
        
        assert "url" in data, "No 'url' in response"
        assert "session_id" in data, "No 'session_id' in response"
        assert data["url"].startswith("https://checkout.stripe.com"), f"Invalid checkout URL: {data['url']}"
        assert len(data["session_id"]) > 0, "Empty session_id"
        
        print(f"PASS: Checkout session created, URL starts with Stripe checkout")
        return data["session_id"]
    
    def test_checkout_requires_valid_package(self, auth_headers):
        """POST /api/lumi/payments/checkout requires valid package_id"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/payments/checkout",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "package_id": "invalid_package",
                "origin_url": "https://ai-karau.preview.emergentagent.com"
            }
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "No error detail in response"
        print(f"PASS: Invalid package returns 400 - {data['detail']}")
    
    def test_checkout_requires_auth(self):
        """POST /api/lumi/payments/checkout requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/payments/checkout",
            headers={"Content-Type": "application/json"},
            json={
                "package_id": "pro_monthly",
                "origin_url": "https://ai-karau.preview.emergentagent.com"
            }
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Unauthenticated checkout returns 401")


class TestPaymentsSubscription:
    """Test subscription status endpoint"""
    
    def test_get_subscription_status(self, auth_headers):
        """GET /api/lumi/payments/my-subscription returns subscription status"""
        response = requests.get(f"{BASE_URL}/api/lumi/payments/my-subscription", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Required fields in subscription status
        assert "is_premium" in data, "No 'is_premium' in response"
        assert "package_id" in data, "No 'package_id' in response"
        assert "package_name" in data, "No 'package_name' in response"
        assert "features" in data, "No 'features' in response"
        assert "premium_since" in data, "No 'premium_since' in response"
        
        assert isinstance(data["is_premium"], bool), "is_premium should be boolean"
        assert isinstance(data["features"], list), "features should be a list"
        
        print(f"PASS: Subscription status - is_premium: {data['is_premium']}, package: {data['package_name']}")
    
    def test_subscription_requires_auth(self):
        """GET /api/lumi/payments/my-subscription requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/payments/my-subscription")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Unauthenticated subscription check returns 401")


class TestPaymentsHistory:
    """Test payment history endpoint"""
    
    def test_get_payment_history(self, auth_headers):
        """GET /api/lumi/payments/history returns transaction history"""
        response = requests.get(f"{BASE_URL}/api/lumi/payments/history", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "transactions" in data, "No 'transactions' in response"
        assert "count" in data, "No 'count' in response"
        assert isinstance(data["transactions"], list), "transactions should be a list"
        assert isinstance(data["count"], int), "count should be an integer"
        
        # If there are transactions, verify structure
        if data["count"] > 0:
            tx = data["transactions"][0]
            expected_fields = ["session_id", "user_id", "package_id", "amount", "payment_status", "created_at"]
            for field in expected_fields:
                assert field in tx, f"Transaction missing '{field}'"
        
        print(f"PASS: Payment history - {data['count']} transactions")
    
    def test_history_requires_auth(self):
        """GET /api/lumi/payments/history requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/payments/history")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Unauthenticated history request returns 401")


class TestPaymentsStatus:
    """Test payment status polling endpoint"""
    
    def test_poll_payment_status(self, auth_headers):
        """GET /api/lumi/payments/status/{session_id} polls payment status"""
        # First create a checkout session to get a session_id
        checkout_response = requests.post(
            f"{BASE_URL}/api/lumi/payments/checkout",
            headers={**auth_headers, "Content-Type": "application/json"},
            json={
                "package_id": "pro_monthly",
                "origin_url": "https://ai-karau.preview.emergentagent.com"
            }
        )
        assert checkout_response.status_code == 200, f"Checkout failed: {checkout_response.text}"
        session_id = checkout_response.json()["session_id"]
        
        # Poll the status
        response = requests.get(f"{BASE_URL}/api/lumi/payments/status/{session_id}", headers=auth_headers)
        assert response.status_code == 200, f"Status check failed: {response.text}"
        data = response.json()
        
        assert "status" in data, "No 'status' in response"
        assert "payment_status" in data, "No 'payment_status' in response"
        # Initial status should be 'open' or 'unpaid'
        assert data["status"] in ["open", "complete", "expired"], f"Unexpected status: {data['status']}"
        
        print(f"PASS: Payment status polling - status: {data['status']}, payment_status: {data['payment_status']}")
    
    def test_status_requires_auth(self):
        """GET /api/lumi/payments/status/{session_id} requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/payments/status/fake_session_id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Unauthenticated status check returns 401")


class TestBehavioralContextTriggers:
    """Test context-aware triggers endpoint"""
    
    def test_get_context_triggers(self, auth_headers):
        """GET /api/lumi/behavior/context-triggers returns context triggers"""
        response = requests.get(f"{BASE_URL}/api/lumi/behavior/context-triggers", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "triggers" in data, "No 'triggers' in response"
        assert "count" in data, "No 'count' in response"
        assert isinstance(data["triggers"], list), "triggers should be a list"
        assert isinstance(data["count"], int), "count should be an integer"
        assert data["count"] == len(data["triggers"]), "count should match triggers length"
        
        # Verify trigger structure if any exist
        for trigger in data["triggers"]:
            assert "trigger_id" in trigger, f"Trigger missing 'trigger_id': {trigger}"
            assert "type" in trigger, f"Trigger missing 'type': {trigger}"
            assert "title" in trigger, f"Trigger missing 'title': {trigger}"
            assert "message" in trigger, f"Trigger missing 'message': {trigger}"
            assert "priority" in trigger, f"Trigger missing 'priority': {trigger}"
            assert trigger["priority"] in ["low", "medium", "high"], f"Invalid priority: {trigger['priority']}"
        
        # Log trigger types found
        trigger_types = [t["type"] for t in data["triggers"]]
        print(f"PASS: Context triggers - {data['count']} triggers, types: {trigger_types}")
    
    def test_triggers_require_auth(self):
        """GET /api/lumi/behavior/context-triggers requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/behavior/context-triggers")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Unauthenticated triggers request returns 401")


class TestBehavioralSmartSuggestions:
    """Test smart suggestions endpoint"""
    
    def test_get_smart_suggestions(self, auth_headers):
        """GET /api/lumi/behavior/smart-suggestions returns personalized suggestions"""
        response = requests.get(f"{BASE_URL}/api/lumi/behavior/smart-suggestions", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "suggestions" in data, "No 'suggestions' in response"
        assert "count" in data, "No 'count' in response"
        assert isinstance(data["suggestions"], list), "suggestions should be a list"
        assert isinstance(data["count"], int), "count should be an integer"
        
        # Verify suggestion structure if any exist
        for suggestion in data["suggestions"]:
            assert "id" in suggestion, f"Suggestion missing 'id': {suggestion}"
            assert "type" in suggestion, f"Suggestion missing 'type': {suggestion}"
            assert "title" in suggestion, f"Suggestion missing 'title': {suggestion}"
            assert "description" in suggestion, f"Suggestion missing 'description': {suggestion}"
            assert "action" in suggestion, f"Suggestion missing 'action': {suggestion}"
        
        # Log suggestion types
        suggestion_types = [s["type"] for s in data["suggestions"]]
        print(f"PASS: Smart suggestions - {data['count']} suggestions, types: {suggestion_types}")
    
    def test_suggestions_with_channel_id(self, auth_headers):
        """GET /api/lumi/behavior/smart-suggestions?channel_id=xxx filters by channel"""
        # First get channels to have a valid channel_id
        ch_response = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        if ch_response.status_code == 200:
            channels = ch_response.json().get("my_channels", [])
            if channels:
                channel_id = channels[0]["id"]
                response = requests.get(
                    f"{BASE_URL}/api/lumi/behavior/smart-suggestions?channel_id={channel_id}",
                    headers=auth_headers
                )
                assert response.status_code == 200, f"Failed: {response.text}"
                data = response.json()
                assert "suggestions" in data
                print(f"PASS: Smart suggestions with channel_id filter returned {data['count']} suggestions")
                return
        
        # If no channels, just check the endpoint without filter
        print("PASS: Smart suggestions channel filter test skipped (no channels)")
    
    def test_suggestions_require_auth(self):
        """GET /api/lumi/behavior/smart-suggestions requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/behavior/smart-suggestions")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Unauthenticated suggestions request returns 401")


class TestBehavioralUsageInsights:
    """Test usage insights endpoint"""
    
    def test_get_usage_insights(self, auth_headers):
        """GET /api/lumi/behavior/usage-insights returns engagement score and stats"""
        response = requests.get(f"{BASE_URL}/api/lumi/behavior/usage-insights", headers=auth_headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Required fields
        assert "period" in data, "No 'period' in response"
        assert "messages_sent" in data, "No 'messages_sent' in response"
        assert "active_channels" in data, "No 'active_channels' in response"
        assert "meetings_attended" in data, "No 'meetings_attended' in response"
        assert "peak_hours" in data, "No 'peak_hours' in response"
        assert "engagement_score" in data, "No 'engagement_score' in response"
        assert "insights" in data, "No 'insights' in response"
        
        # Type checks
        assert data["period"] == "last_7_days", f"Unexpected period: {data['period']}"
        assert isinstance(data["messages_sent"], int), "messages_sent should be int"
        assert isinstance(data["active_channels"], int), "active_channels should be int"
        assert isinstance(data["meetings_attended"], int), "meetings_attended should be int"
        assert isinstance(data["peak_hours"], list), "peak_hours should be list"
        assert isinstance(data["engagement_score"], int), "engagement_score should be int"
        assert isinstance(data["insights"], list), "insights should be list"
        
        # engagement_score should be 0-100
        assert 0 <= data["engagement_score"] <= 100, f"Engagement score out of range: {data['engagement_score']}"
        
        print(f"PASS: Usage insights - messages: {data['messages_sent']}, channels: {data['active_channels']}, meetings: {data['meetings_attended']}, engagement: {data['engagement_score']}/100")
    
    def test_insights_require_auth(self):
        """GET /api/lumi/behavior/usage-insights requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/behavior/usage-insights")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Unauthenticated insights request returns 401")


class TestExistingAPIsStillWork:
    """Verify existing APIs from previous iterations still work"""
    
    def test_channels_api(self, auth_headers):
        """GET /api/lumi/channels still works"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        assert response.status_code == 200, f"Channels API failed: {response.text}"
        data = response.json()
        assert "my_channels" in data or "discover" in data
        print("PASS: Channels API still works")
    
    def test_dm_api(self, auth_headers):
        """GET /api/lumi/dm still works"""
        response = requests.get(f"{BASE_URL}/api/lumi/dm", headers=auth_headers)
        assert response.status_code == 200, f"DM API failed: {response.text}"
        data = response.json()
        assert "dms" in data
        print("PASS: DM API still works")
    
    def test_bot_store_api(self, auth_headers):
        """GET /api/lumi/bots/catalog (browse available bots) still works"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", headers=auth_headers)
        assert response.status_code == 200, f"Bot Store API failed: {response.text}"
        data = response.json()
        assert "bots" in data
        print("PASS: Bot Store API still works")
    
    def test_meeting_history_api(self, auth_headers):
        """GET /api/lumi/meetings/history still works"""
        response = requests.get(f"{BASE_URL}/api/lumi/meetings/history", headers=auth_headers)
        assert response.status_code == 200, f"Meeting History API failed: {response.text}"
        data = response.json()
        assert "meetings" in data
        print("PASS: Meeting History API still works")
    
    def test_e2ee_status_api(self, auth_headers):
        """GET /api/lumi/e2ee/keys/status/me still works"""
        response = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/status/me", headers=auth_headers)
        assert response.status_code == 200, f"E2EE API failed: {response.text}"
        data = response.json()
        assert "enabled" in data
        print("PASS: E2EE status API still works")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
