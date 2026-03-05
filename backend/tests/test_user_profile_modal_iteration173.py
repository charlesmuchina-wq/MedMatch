"""
Test User Profile Modal - Iteration 173
Tests for LUMI User Profile Modal features:
- GET /api/lumi/profile/capabilities
- PUT /api/lumi/profile/notification-prefs
- PUT /api/lumi/presence (status update)
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')
if not BASE_URL:
    raise ValueError("REACT_APP_BACKEND_URL not set")

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestUserProfileModal:
    """Tests for User Profile Modal API endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data or "token" in data
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    # ==================== Profile Capabilities Endpoint ====================
    
    def test_get_profile_capabilities(self, headers):
        """Test GET /api/lumi/profile/capabilities returns user info and capabilities"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        
        # Verify user info
        assert "user" in data
        user = data["user"]
        assert "user_id" in user
        assert "email" in user
        assert user["email"] == TEST_EMAIL
        assert "name" in user
        assert "role" in user
        assert "status" in user
        assert "messages_sent" in user
        
        # Verify capabilities list
        assert "capabilities" in data
        caps = data["capabilities"]
        assert isinstance(caps, list)
        assert len(caps) == 15, f"Expected 15 capabilities, got {len(caps)}"
        
        # Verify capability structure
        for cap in caps:
            assert "id" in cap
            assert "name" in cap
            assert "description" in cap
            assert "category" in cap
        
        # Verify expected categories exist
        categories = set(cap["category"] for cap in caps)
        expected_categories = {
            "Productivity AI", "Actionable Intelligence", 
            "Graph Intelligence", "Advanced Collaboration",
            "Communication", "Navigation", "Core"
        }
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"
        
        # Verify channels returned
        assert "channels" in data
        assert isinstance(data["channels"], list)
        
        # Verify dm_count
        assert "dm_count" in data
        assert isinstance(data["dm_count"], int)
        
        # Verify notification_preferences
        assert "notification_preferences" in data
        
        print(f"Profile capabilities: user={user['email']}, capabilities={len(caps)}, channels={len(data['channels'])}")
    
    def test_capabilities_requires_auth(self):
        """Test that profile/capabilities endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities")
        assert response.status_code == 401
    
    def test_capabilities_with_invalid_token(self):
        """Test that profile/capabilities rejects invalid token"""
        headers = {"Authorization": "Bearer invalid_token_xyz"}
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        assert response.status_code == 401
    
    # ==================== Notification Preferences Endpoint ====================
    
    def test_update_notification_prefs(self, headers):
        """Test PUT /api/lumi/profile/notification-prefs updates preferences"""
        # First get user's channels
        profile_res = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        assert profile_res.status_code == 200
        channels = profile_res.json().get("channels", [])
        
        if not channels:
            pytest.skip("No channels available to test notification prefs")
        
        test_channel_id = channels[0]["id"]
        
        # Test setting to mentions only
        response = requests.put(
            f"{BASE_URL}/api/lumi/profile/notification-prefs",
            headers=headers,
            json={"channel_id": test_channel_id, "mute": False, "level": "mentions"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("status") == "updated"
        assert data.get("channel_id") == test_channel_id
        assert data.get("level") == "mentions"
        assert data.get("mute") == False
        
        # Test setting to none (muted)
        response2 = requests.put(
            f"{BASE_URL}/api/lumi/profile/notification-prefs",
            headers=headers,
            json={"channel_id": test_channel_id, "mute": True, "level": "none"}
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2.get("level") == "none"
        assert data2.get("mute") == True
        
        # Test setting back to all
        response3 = requests.put(
            f"{BASE_URL}/api/lumi/profile/notification-prefs",
            headers=headers,
            json={"channel_id": test_channel_id, "mute": False, "level": "all"}
        )
        assert response3.status_code == 200
        data3 = response3.json()
        assert data3.get("level") == "all"
        
        print(f"Notification preferences updated for channel {test_channel_id}")
    
    def test_notification_prefs_requires_auth(self):
        """Test that notification-prefs endpoint requires authentication"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/profile/notification-prefs",
            json={"channel_id": "test", "mute": False, "level": "all"}
        )
        assert response.status_code == 401
    
    # ==================== Presence/Status Update ====================
    
    def test_update_presence_available(self, headers):
        """Test PUT /api/lumi/presence with 'available' status"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers,
            json={"status": "available"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert data.get("status") == "available"
        print("Status updated to: available")
    
    def test_update_presence_busy(self, headers):
        """Test PUT /api/lumi/presence with 'busy' status"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers,
            json={"status": "busy"}
        )
        assert response.status_code == 200
        assert response.json().get("status") == "busy"
        print("Status updated to: busy")
    
    def test_update_presence_in_meeting(self, headers):
        """Test PUT /api/lumi/presence with 'in_meeting' status"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers,
            json={"status": "in_meeting"}
        )
        assert response.status_code == 200
        assert response.json().get("status") == "in_meeting"
        print("Status updated to: in_meeting")
    
    def test_update_presence_ooo(self, headers):
        """Test PUT /api/lumi/presence with 'ooo' (out of office) status"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers,
            json={"status": "ooo"}
        )
        assert response.status_code == 200
        assert response.json().get("status") == "ooo"
        print("Status updated to: ooo")
    
    def test_update_presence_vacation(self, headers):
        """Test PUT /api/lumi/presence with 'vacation' status"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers,
            json={"status": "vacation"}
        )
        assert response.status_code == 200
        assert response.json().get("status") == "vacation"
        print("Status updated to: vacation")
    
    def test_update_presence_invalid_status(self, headers):
        """Test PUT /api/lumi/presence rejects invalid status"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers,
            json={"status": "invalid_status"}
        )
        assert response.status_code == 400
        print("Invalid status correctly rejected")
    
    def test_presence_requires_auth(self):
        """Test that presence endpoint requires authentication"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            json={"status": "available"}
        )
        assert response.status_code == 401
    
    # ==================== Verify Presence Persists in Profile ====================
    
    def test_status_persists_in_profile(self, headers):
        """Test that status change persists and shows in profile capabilities"""
        # Set status to busy
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers,
            json={"status": "busy"}
        )
        assert response.status_code == 200
        
        # Verify it shows in profile
        profile_res = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        assert profile_res.status_code == 200
        user_status = profile_res.json()["user"]["status"]
        assert user_status == "busy", f"Expected busy, got {user_status}"
        
        # Reset to available
        requests.put(f"{BASE_URL}/api/lumi/presence", headers=headers, json={"status": "available"})
        print("Status persistence verified")
    
    # ==================== Verify Notification Prefs Persist ====================
    
    def test_notification_prefs_persist(self, headers):
        """Test that notification preferences persist and show in profile"""
        profile_res = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        assert profile_res.status_code == 200
        channels = profile_res.json().get("channels", [])
        
        if not channels:
            pytest.skip("No channels to test")
        
        test_channel_id = channels[0]["id"]
        
        # Set to mentions
        requests.put(
            f"{BASE_URL}/api/lumi/profile/notification-prefs",
            headers=headers,
            json={"channel_id": test_channel_id, "mute": False, "level": "mentions"}
        )
        
        # Verify in profile
        profile_res2 = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        prefs = profile_res2.json().get("notification_preferences", {})
        assert test_channel_id in prefs, "Notification prefs not found in profile"
        assert prefs[test_channel_id].get("level") == "mentions"
        
        # Reset
        requests.put(
            f"{BASE_URL}/api/lumi/profile/notification-prefs",
            headers=headers,
            json={"channel_id": test_channel_id, "mute": False, "level": "all"}
        )
        print("Notification preferences persistence verified")


class TestCapabilitiesContent:
    """Test that all 15 LUMI capabilities are returned correctly"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token") or response.json().get("token")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}"}
    
    def test_all_capability_ids_present(self, headers):
        """Verify all 15 capability IDs are present"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        assert response.status_code == 200
        
        caps = response.json()["capabilities"]
        cap_ids = {cap["id"] for cap in caps}
        
        expected_ids = {
            "sentiment", "tasks", "reports",
            "ask_ai", "decision_cards", "anomaly_alerts",
            "knowledge_graph", "bottleneck_detection", "what_if",
            "smart_notifications", "translation", "command_bar",
            "threading", "file_sharing", "reactions"
        }
        
        for expected_id in expected_ids:
            assert expected_id in cap_ids, f"Missing capability: {expected_id}"
        
        print(f"All {len(expected_ids)} capabilities verified")
    
    def test_productivity_ai_capabilities(self, headers):
        """Verify Productivity AI category has correct capabilities"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        caps = response.json()["capabilities"]
        
        productivity_ai = [c for c in caps if c["category"] == "Productivity AI"]
        assert len(productivity_ai) == 3
        
        ids = {c["id"] for c in productivity_ai}
        assert ids == {"sentiment", "tasks", "reports"}
        print("Productivity AI capabilities verified: sentiment, tasks, reports")
    
    def test_actionable_intelligence_capabilities(self, headers):
        """Verify Actionable Intelligence category"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        caps = response.json()["capabilities"]
        
        actionable = [c for c in caps if c["category"] == "Actionable Intelligence"]
        assert len(actionable) == 3
        
        ids = {c["id"] for c in actionable}
        assert ids == {"ask_ai", "decision_cards", "anomaly_alerts"}
        print("Actionable Intelligence capabilities verified")
    
    def test_graph_intelligence_capabilities(self, headers):
        """Verify Graph Intelligence category"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        caps = response.json()["capabilities"]
        
        graph = [c for c in caps if c["category"] == "Graph Intelligence"]
        assert len(graph) == 2
        
        ids = {c["id"] for c in graph}
        assert ids == {"knowledge_graph", "bottleneck_detection"}
        print("Graph Intelligence capabilities verified")
    
    def test_core_capabilities(self, headers):
        """Verify Core category capabilities"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        caps = response.json()["capabilities"]
        
        core = [c for c in caps if c["category"] == "Core"]
        assert len(core) == 3
        
        ids = {c["id"] for c in core}
        assert ids == {"threading", "file_sharing", "reactions"}
        print("Core capabilities verified: threading, file_sharing, reactions")
