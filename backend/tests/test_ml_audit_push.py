"""
Test suite for new features:
1. ML Data Collection endpoints
2. Admin Audit Logging endpoints
3. Expo Push Notification endpoints
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"


class TestMLDataCollection:
    """ML Data Collection API tests"""
    
    def test_ml_data_status(self):
        """Test ML data collector status endpoint"""
        response = requests.get(f"{BASE_URL}/api/ml-data/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["active", "not_initialized", "error"]
        assert "buffer_size" in data
        assert "flush_interval_seconds" in data
        print(f"ML Data Status: {data['status']}, Buffer: {data['buffer_size']}")
    
    def test_ml_data_test_event(self):
        """Test logging a test event"""
        response = requests.post(f"{BASE_URL}/api/ml-data/test-event")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "buffer_size" in data
        print(f"Test event logged, buffer size: {data['buffer_size']}")
    
    def test_ml_data_flush(self):
        """Test flushing the event buffer"""
        # First log some events
        requests.post(f"{BASE_URL}/api/ml-data/test-event")
        requests.post(f"{BASE_URL}/api/ml-data/test-event")
        
        # Then flush
        response = requests.post(f"{BASE_URL}/api/ml-data/flush")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "events_flushed" in data
        print(f"Events flushed: {data['events_flushed']}")
    
    def test_ml_data_event_stats(self):
        """Test getting event statistics"""
        response = requests.get(f"{BASE_URL}/api/ml-data/events/stats")
        assert response.status_code == 200
        data = response.json()
        assert "time_period_hours" in data
        assert "event_breakdown" in data
        assert "total_events" in data
        print(f"Total events in last 24h: {data['total_events']}")
    
    def test_ml_data_event_types(self):
        """Test getting available event types"""
        response = requests.get(f"{BASE_URL}/api/ml-data/event-types")
        assert response.status_code == 200
        data = response.json()
        assert "event_types" in data
        assert "severities" in data
        assert len(data["event_types"]) > 0
        print(f"Available event types: {len(data['event_types'])}")


class TestAdminAuditLogging:
    """Admin Audit Logging API tests - requires authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Admin login failed")
    
    def test_audit_status(self):
        """Test audit logging service status"""
        response = requests.get(
            f"{BASE_URL}/api/admin-audit/status",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "total_logs" in data
        assert "supported_actions" in data
        assert "target_types" in data
        print(f"Audit status: {data['status']}, Total logs: {data['total_logs']}")
    
    def test_audit_log_creation(self):
        """Test creating an audit log entry"""
        log_entry = {
            "action": "settings_update",
            "target_type": "system",
            "target_id": "test_123",
            "details": {"test": True, "timestamp": time.time()}
        }
        response = requests.post(
            f"{BASE_URL}/api/admin-audit/log",
            headers=self.headers,
            json=log_entry
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "log_entry" in data
        assert data["log_entry"]["action"] == "settings_update"
        print(f"Audit log created: {data['log_entry']['id']}")
    
    def test_audit_logs_retrieval(self):
        """Test retrieving audit logs"""
        response = requests.get(
            f"{BASE_URL}/api/admin-audit/logs?limit=10",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert "page" in data
        print(f"Retrieved {len(data['logs'])} logs, total: {data['total']}")
    
    def test_audit_unauthorized_access(self):
        """Test that unauthenticated requests are rejected"""
        response = requests.get(f"{BASE_URL}/api/admin-audit/status")
        assert response.status_code == 401
        print("Unauthorized access correctly rejected")


class TestExpoPushNotifications:
    """Expo Push Notification API tests - requires authentication"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Admin login failed")
    
    def test_expo_subscribe(self):
        """Test registering an Expo push token"""
        subscription = {
            "expo_token": f"ExponentPushToken[TEST_{int(time.time())}]",
            "device_name": "Test Device",
            "platform": "ios"
        }
        response = requests.post(
            f"{BASE_URL}/api/webpush/expo/subscribe",
            headers=self.headers,
            json=subscription
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "token_id" in data or "message" in data
        print(f"Expo token registered: {data.get('token_id', 'updated')}")
    
    def test_expo_status(self):
        """Test getting Expo push status"""
        response = requests.get(
            f"{BASE_URL}/api/webpush/expo/status",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "enabled" in data
        assert "devices" in data
        print(f"Expo push enabled: {data['enabled']}, devices: {data['devices']}")
    
    def test_expo_unauthorized_access(self):
        """Test that unauthenticated requests are rejected"""
        response = requests.get(f"{BASE_URL}/api/webpush/expo/status")
        assert response.status_code == 401
        print("Unauthorized access correctly rejected")


class TestWebPushNotifications:
    """Web Push Notification API tests"""
    
    def test_vapid_public_key(self):
        """Test getting VAPID public key"""
        response = requests.get(f"{BASE_URL}/api/webpush/vapid-public-key")
        assert response.status_code == 200
        data = response.json()
        assert "publicKey" in data
        assert data["configured"] == True
        print(f"VAPID key configured: {data['configured']}")


class TestRateLimiting:
    """Test rate limiting behavior"""
    
    def test_rate_limit_status(self):
        """Test rate limit status endpoint"""
        response = requests.get(f"{BASE_URL}/api/rate-limit/status")
        assert response.status_code == 200
        data = response.json()
        assert "tier" in data
        assert "limits" in data
        print(f"Rate limit tier: {data['tier']}")
    
    def test_rate_limit_tiers(self):
        """Test getting rate limit tiers"""
        response = requests.get(f"{BASE_URL}/api/rate-limit/tiers")
        assert response.status_code == 200
        data = response.json()
        assert "anonymous" in data
        assert "authenticated" in data
        print(f"Available tiers: {list(data.keys())}")


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "ai_supervisor" in data
        print(f"Health: {data['status']}, AI Supervisor: {data['ai_supervisor']}")
    
    def test_system_status(self):
        """Test system status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "mongodb" in data
        assert "cache" in data
        print(f"System status: {data['status']}, MongoDB: {data['mongodb']['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
