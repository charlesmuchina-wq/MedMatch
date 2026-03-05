"""
Iteration 172 - SSO Implementation & LUMI Refactor Tests
Tests: Google SSO, Microsoft SSO placeholder, LUMI Login, LumiMessenger components
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestHealthCheck:
    """Basic health check - verify backend is accessible"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("✓ Health endpoint accessible")


class TestAuthLogin:
    """Test email/password login for LUMI"""
    
    def test_admin_login_success(self):
        """Test admin credentials: admin@medmatch.com / Swampdrainer2026!"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        assert data["user"]["email"] == "admin@medmatch.com"
        print(f"✓ Admin login successful: user_id={data['user'].get('user_id')}")
        return data["access_token"]
    
    def test_invalid_login_returns_401(self):
        """Test invalid credentials return 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "wrong@example.com", "password": "wrongpass"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Invalid login correctly returns 401")


class TestMicrosoftSSOPlaceholder:
    """Test Microsoft SSO placeholder returns 501"""
    
    def test_microsoft_login_returns_501(self):
        """POST /api/auth/microsoft/login should return 501 (not yet implemented)"""
        response = requests.post(f"{BASE_URL}/api/auth/microsoft/login")
        assert response.status_code == 501, f"Expected 501, got {response.status_code}"
        data = response.json()
        assert "Microsoft SSO is not yet configured" in data.get("detail", "")
        print("✓ Microsoft SSO placeholder returns 501 with correct message")


class TestGoogleSessionEndpoint:
    """Test Google session endpoint exists"""
    
    def test_google_session_endpoint_exists(self):
        """POST /api/auth/google/session should exist (returns 400 without session_id)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/session",
            json={}
        )
        # Should return 400 (missing session_id) not 404 (endpoint not found)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        data = response.json()
        assert "session_id" in str(data.get("detail", "")).lower(), f"Unexpected response: {data}"
        print("✓ Google session endpoint exists and validates input")
    
    def test_google_session_with_invalid_session_id(self):
        """POST /api/auth/google/session with invalid session_id"""
        response = requests.post(
            f"{BASE_URL}/api/auth/google/session",
            json={"session_id": "invalid_session_12345"}
        )
        # Should return 401 (invalid session) or 502 (auth service unavailable)
        assert response.status_code in [401, 502], f"Expected 401/502, got {response.status_code}: {response.text}"
        print(f"✓ Google session correctly validates session_id (status {response.status_code})")


class TestLumiChannelsAPI:
    """Test LUMI channels API - verify refactored components work"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for authenticated requests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code != 200:
            pytest.skip("Could not authenticate")
        return response.json()["access_token"]
    
    def test_channels_endpoint_requires_auth(self):
        """GET /api/lumi/channels requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Channels endpoint correctly requires auth")
    
    def test_channels_endpoint_with_auth(self, auth_token):
        """GET /api/lumi/channels with valid token"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Channels failed: {response.text}"
        data = response.json()
        assert "my_channels" in data or "discover" in data
        print(f"✓ Channels endpoint works: {len(data.get('my_channels', []))} channels")


class TestLumiMessaging:
    """Test LUMI messaging after login"""
    
    @pytest.fixture
    def auth_session(self):
        """Get auth token and seed channels if needed"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code != 200:
            pytest.skip("Could not authenticate")
        token = response.json()["access_token"]
        
        # Get or seed channels
        ch_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {token}"}
        )
        channels = ch_response.json() if ch_response.status_code == 200 else {}
        
        if not channels.get("my_channels"):
            # Seed channels
            requests.post(
                f"{BASE_URL}/api/lumi/seed",
                headers={"Authorization": f"Bearer {token}"}
            )
            ch_response = requests.get(
                f"{BASE_URL}/api/lumi/channels",
                headers={"Authorization": f"Bearer {token}"}
            )
            channels = ch_response.json()
        
        return {"token": token, "channels": channels}
    
    def test_send_message_in_channel(self, auth_session):
        """Test sending a message in a channel"""
        token = auth_session["token"]
        channels = auth_session["channels"].get("my_channels", [])
        
        if not channels:
            pytest.skip("No channels available")
        
        channel_id = channels[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"content": "TEST_iteration172_message"}
        )
        assert response.status_code in [200, 201], f"Send message failed: {response.text}"
        print(f"✓ Message sent in channel {channels[0]['name']}")


class TestLumiAIFeatures:
    """Test LUMI AI panel buttons - verify they're accessible"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code != 200:
            pytest.skip("Could not authenticate")
        return response.json()["access_token"]
    
    def test_ai_insights_endpoint(self, auth_token):
        """Test AI insights endpoint exists"""
        # Get a channel first
        ch_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if ch_response.status_code != 200:
            pytest.skip("Could not get channels")
        
        channels = ch_response.json().get("my_channels", [])
        if not channels:
            pytest.skip("No channels available")
        
        channel_id = channels[0]["id"]
        
        # Test AI summary endpoint
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/summary/{channel_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 200 or 404 (not 401/500)
        assert response.status_code in [200, 404], f"AI summary failed: {response.status_code}"
        print(f"✓ AI insights endpoint accessible (status {response.status_code})")
    
    def test_alerts_endpoint(self, auth_token):
        """Test alerts/anomalies endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/anomalies",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Anomalies failed: {response.text}"
        print("✓ Alerts endpoint accessible")
    
    def test_knowledge_graph_endpoint(self, auth_token):
        """Test knowledge graph endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/knowledge-graph",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Knowledge graph failed: {response.text}"
        print("✓ Knowledge graph endpoint accessible")
    
    def test_bottleneck_endpoint(self, auth_token):
        """Test bottleneck detection endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bottlenecks",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Bottlenecks failed: {response.text}"
        print("✓ Bottleneck endpoint accessible")
    
    def test_simulation_endpoint(self, auth_token):
        """Test what-if simulation endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/simulate",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={"scenario": "What if we delay the project by 2 weeks?"}
        )
        assert response.status_code == 200, f"Simulation failed: {response.text}"
        print("✓ Simulation endpoint accessible")
    
    def test_notifications_endpoint(self, auth_token):
        """Test smart notifications endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/notifications",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Notifications failed: {response.text}"
        print("✓ Notifications endpoint accessible")


class TestORCIDOAuth:
    """Test ORCID OAuth configuration"""
    
    def test_orcid_config(self):
        """Test ORCID config endpoint"""
        response = requests.get(f"{BASE_URL}/api/auth/orcid/config")
        assert response.status_code == 200, f"ORCID config failed: {response.text}"
        data = response.json()
        assert "configured" in data
        print(f"✓ ORCID config accessible (configured={data.get('configured')})")


class TestAppleAuth:
    """Test Apple Sign In configuration"""
    
    def test_apple_config(self):
        """Test Apple config endpoint"""
        response = requests.get(f"{BASE_URL}/api/auth/apple/config")
        assert response.status_code == 200, f"Apple config failed: {response.text}"
        data = response.json()
        assert "configured" in data
        print(f"✓ Apple config accessible (configured={data.get('configured')})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
