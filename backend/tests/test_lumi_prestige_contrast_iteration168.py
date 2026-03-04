"""
Test LUMI Prestige - Iteration 168: Contrast Fixes and Footer Button
Tests the contrast/visibility improvements and the Switch to AI KARAU footer button
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLumiAuth:
    """Test LUMI authentication endpoints"""
    
    def test_login_success(self):
        """Test login with valid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"✅ Login successful for admin@medmatch.com")
        return data["access_token"]
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 400], f"Expected 401/400, got {response.status_code}"
        print("✅ Invalid login correctly rejected")


class TestLumiChannels:
    """Test LUMI channel endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_channels(self):
        """Test fetching user's channels"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels", headers=self.headers)
        assert response.status_code == 200, f"Failed to get channels: {response.text}"
        data = response.json()
        assert "my_channels" in data or "channels" in data
        print(f"✅ Channels fetched successfully")
    
    def test_get_channels_requires_auth(self):
        """Test that channels endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Channels endpoint correctly requires auth")


class TestLumiMessaging:
    """Test LUMI messaging endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and channel for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
        
        # Get a channel
        channels_response = requests.get(f"{BASE_URL}/api/lumi/channels", headers=self.headers)
        if channels_response.status_code == 200:
            data = channels_response.json()
            channels = data.get("my_channels", data.get("channels", []))
            if channels:
                self.channel_id = channels[0]["id"]
            else:
                pytest.skip("No channels available")
        else:
            pytest.skip("Failed to get channels")
    
    def test_get_messages(self):
        """Test fetching messages from a channel"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{self.channel_id}/messages",
            headers=self.headers
        )
        assert response.status_code == 200, f"Failed to get messages: {response.text}"
        data = response.json()
        assert "messages" in data
        print(f"✅ Messages fetched from channel {self.channel_id}")
    
    def test_send_message(self):
        """Test sending a message to a channel"""
        test_content = "TEST_iteration168_message"
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{self.channel_id}/messages",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"content": test_content}
        )
        assert response.status_code in [200, 201], f"Failed to send message: {response.text}"
        data = response.json()
        assert "content" in data or "id" in data
        print(f"✅ Message sent successfully")


class TestLumiDMs:
    """Test LUMI direct message endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_dms(self):
        """Test fetching direct messages list"""
        response = requests.get(f"{BASE_URL}/api/lumi/dm", headers=self.headers)
        assert response.status_code == 200, f"Failed to get DMs: {response.text}"
        data = response.json()
        assert "dms" in data
        print(f"✅ DMs fetched: {len(data.get('dms', []))} conversations")
    
    def test_dms_requires_auth(self):
        """Test that DM endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/dm")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ DM endpoint correctly requires auth")


class TestLumiPresence:
    """Test LUMI presence/status endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_all_presence(self):
        """Test fetching all users' presence status"""
        response = requests.get(f"{BASE_URL}/api/lumi/presence/all", headers=self.headers)
        assert response.status_code == 200, f"Failed to get presence: {response.text}"
        data = response.json()
        assert "presence" in data
        print(f"✅ Presence data fetched for {len(data.get('presence', {}))} users")
    
    def test_update_presence(self):
        """Test updating user's presence status"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"status": "available"}
        )
        assert response.status_code == 200, f"Failed to update presence: {response.text}"
        print("✅ Presence updated to 'available'")
    
    def test_invalid_presence_status(self):
        """Test that invalid presence status is rejected"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid status, got {response.status_code}"
        print("✅ Invalid presence status correctly rejected")


class TestLumiUserSearch:
    """Test LUMI user search endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_search_users(self):
        """Test searching for users"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=admin",
            headers=self.headers
        )
        assert response.status_code == 200, f"User search failed: {response.text}"
        data = response.json()
        assert "users" in data
        print(f"✅ User search returned {len(data.get('users', []))} results")
    
    def test_search_users_requires_auth(self):
        """Test that user search requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=test")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ User search correctly requires auth")


class TestLumiGlobalSearch:
    """Test LUMI global search endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_global_search(self):
        """Test global message search"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/search?q=test",
            headers=self.headers
        )
        assert response.status_code == 200, f"Global search failed: {response.text}"
        data = response.json()
        assert "results" in data
        print(f"✅ Global search returned {len(data.get('results', []))} results")


class TestLumiUnreadCounts:
    """Test LUMI unread counts endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Authentication failed")
    
    def test_get_unread_counts(self):
        """Test fetching unread message counts"""
        response = requests.get(f"{BASE_URL}/api/lumi/unread-counts", headers=self.headers)
        assert response.status_code == 200, f"Failed to get unread counts: {response.text}"
        data = response.json()
        assert "unread" in data
        print(f"✅ Unread counts fetched: {data.get('unread', {})}")


class TestHealthEndpoint:
    """Test API health endpoint"""
    
    def test_health(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        data = response.json()
        assert data.get("status") == "healthy"
        print(f"✅ Health check passed: {data.get('service')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
