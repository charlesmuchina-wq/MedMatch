"""
Test Share Meeting Feature - Backend API Tests
Tests for guest join page, share functionality, and public meeting info endpoint
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestShareMeetingFeature:
    """Test suite for Share Meeting feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def test_meeting(self, auth_token):
        """Create a test meeting for the test suite"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_Share_Meeting_Test"}
        )
        assert response.status_code == 200, f"Failed to create meeting: {response.text}"
        return response.json()
    
    # ============================================
    # Public /info Endpoint Tests (No Auth)
    # ============================================
    
    def test_public_info_endpoint_no_auth(self, test_meeting):
        """Test GET /api/karau-meet/meetings/{id}/info returns meeting info without auth"""
        meeting_id = test_meeting["meeting_id"]
        
        # Request WITHOUT authorization header
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/info")
        
        assert response.status_code == 200, f"Public info endpoint failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "meeting_id" in data
        assert "title" in data
        assert "status" in data
        assert "host_name" in data
        
        # Verify values
        assert data["meeting_id"] == meeting_id
        assert data["title"] == "TEST_Share_Meeting_Test"
        assert data["status"] in ["waiting", "active", "ended"]
        assert len(data["host_name"]) > 0
        print(f"✓ Public info endpoint returned: {data}")
    
    def test_public_info_invalid_meeting_returns_404(self):
        """Test GET /api/karau-meet/meetings/{invalid_id}/info returns 404"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/INVALID_XYZ_123/info")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        print("✓ Invalid meeting ID correctly returns 404")
    
    # ============================================
    # Guest Join Endpoint Tests
    # ============================================
    
    def test_guest_join_with_name(self, test_meeting):
        """Test POST /api/karau-meet/meetings/{id}/join-guest with guest name"""
        meeting_id = test_meeting["meeting_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join-guest",
            json={"guest_name": "John Test Guest"}
        )
        
        assert response.status_code == 200, f"Guest join failed: {response.text}"
        data = response.json()
        
        # Verify required fields
        assert "guest_user_id" in data
        assert "guest_name" in data
        assert "meeting" in data
        assert "ice_servers" in data
        
        # Verify values
        assert data["guest_name"] == "John Test Guest"
        assert data["guest_user_id"].startswith("guest_")
        assert len(data["ice_servers"]) > 0
        
        print(f"✓ Guest join successful with ID: {data['guest_user_id']}")
    
    def test_guest_join_with_empty_name_defaults_to_guest(self, test_meeting):
        """Test guest join with empty name defaults to 'Guest'"""
        meeting_id = test_meeting["meeting_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join-guest",
            json={"guest_name": ""}
        )
        
        assert response.status_code == 200, f"Guest join failed: {response.text}"
        data = response.json()
        
        # Should default to "Guest" when empty name provided
        assert data["guest_name"] == "Guest"
        print("✓ Empty guest name correctly defaults to 'Guest'")
    
    def test_guest_join_invalid_meeting_returns_404(self):
        """Test guest join with invalid meeting ID returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/INVALID_MEETING_XYZ/join-guest",
            json={"guest_name": "Test Guest"}
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Guest join with invalid meeting correctly returns 404")
    
    def test_guest_join_returns_ice_servers(self, test_meeting):
        """Test that guest join response includes ICE servers for WebRTC"""
        meeting_id = test_meeting["meeting_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join-guest",
            json={"guest_name": "ICE Test Guest"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "ice_servers" in data
        assert isinstance(data["ice_servers"], list)
        assert len(data["ice_servers"]) > 0
        
        # Verify ICE server structure
        for server in data["ice_servers"]:
            assert "urls" in server
            assert "stun:" in server["urls"] or "turn:" in server["urls"]
        
        print(f"✓ Guest join returns {len(data['ice_servers'])} ICE servers")
    
    # ============================================
    # Meeting Create with Share Tests
    # ============================================
    
    def test_create_meeting_returns_join_url(self, auth_token):
        """Test that creating a meeting returns a join_url for sharing"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_Create_and_Share_Meeting"}
        )
        
        assert response.status_code == 200, f"Create meeting failed: {response.text}"
        data = response.json()
        
        assert "meeting_id" in data
        assert "join_url" in data
        
        # Verify join_url format
        assert f"/karau-meet/join/{data['meeting_id']}" in data["join_url"]
        
        print(f"✓ Meeting created with join URL: {data['join_url']}")
    
    # ============================================
    # Authenticated Meeting Endpoints Tests
    # ============================================
    
    def test_authenticated_meeting_details(self, auth_token, test_meeting):
        """Test GET /api/karau-meet/meetings/{id} (authenticated)"""
        meeting_id = test_meeting["meeting_id"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting" in data
        assert "ice_servers" in data
        assert "participants" in data
        
        print("✓ Authenticated meeting details endpoint works")
    
    def test_get_user_meetings(self, auth_token):
        """Test GET /api/karau-meet/meetings returns user's meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "meetings" in data
        assert isinstance(data["meetings"], list)
        
        # Should have at least the test meetings we created
        assert len(data["meetings"]) > 0
        
        print(f"✓ User has {len(data['meetings'])} meetings")


class TestShareMeetingDataFlow:
    """Test the complete data flow for share meeting feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    def test_complete_share_flow(self, auth_token):
        """Test complete flow: Create meeting -> Get info -> Guest join"""
        # Step 1: Create meeting as host
        create_response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_Complete_Share_Flow"}
        )
        assert create_response.status_code == 200
        meeting = create_response.json()
        meeting_id = meeting["meeting_id"]
        print(f"Step 1: Created meeting {meeting_id}")
        
        # Step 2: Get public info (simulating guest visiting share link)
        info_response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/info"
        )
        assert info_response.status_code == 200
        info = info_response.json()
        assert info["title"] == "TEST_Complete_Share_Flow"
        print(f"Step 2: Got meeting info - title: {info['title']}")
        
        # Step 3: Guest joins the meeting
        join_response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join-guest",
            json={"guest_name": "Flow Test Guest"}
        )
        assert join_response.status_code == 200
        join_data = join_response.json()
        assert join_data["guest_name"] == "Flow Test Guest"
        assert "guest_user_id" in join_data
        print(f"Step 3: Guest joined with ID: {join_data['guest_user_id']}")
        
        # Step 4: Verify guest appears in participants
        participants_response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/participants",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert participants_response.status_code == 200
        participants = participants_response.json()["participants"]
        
        guest_found = any(p["user_name"] == "Flow Test Guest" for p in participants)
        assert guest_found, "Guest should appear in participants list"
        print(f"Step 4: Verified guest in participants list ({len(participants)} total)")
        
        print("✓ Complete share flow test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
