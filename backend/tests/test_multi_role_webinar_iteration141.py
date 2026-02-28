"""
Test Multi-Role Webinar System - Iteration 141
Tests: Role management, hand raise, practice session, room-info endpoints

Features:
- Role hierarchy: host > presenter > panelist > attendee
- Promote/demote users
- Hand raise for attendees
- Practice session (blocks attendees)
- Room info with permissions
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_WEBINAR_ID = "WEB-3F035EFF"


class TestMultiRoleWebinarSystem:
    """Tests for the new multi-role webinar features"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    # --- Room Info Tests ---
    
    def test_room_info_returns_role_permissions(self, auth_headers):
        """GET /api/karau/webinar/{id}/room-info returns my_role, permissions"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/room-info",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Room info failed: {response.text}"
        data = response.json()
        
        # Verify required fields
        assert "my_role" in data, "Missing my_role field"
        assert "can_stream_video" in data, "Missing can_stream_video field"
        assert "can_stream_audio" in data, "Missing can_stream_audio field"
        assert "can_screen_share" in data, "Missing can_screen_share field"
        assert "can_control" in data, "Missing can_control field"
        assert "practice_mode" in data, "Missing practice_mode field"
        assert "settings" in data, "Missing settings field"
        
        # Host should have full permissions
        assert data["my_role"] == "host", f"Expected host role, got {data['my_role']}"
        assert data["can_stream_video"] is True
        assert data["can_stream_audio"] is True
        assert data["can_screen_share"] is True
        assert data["can_control"] is True
        
        print(f"Room info: role={data['my_role']}, status={data.get('status')}, practice_mode={data['practice_mode']}")

    def test_room_info_returns_webinar_details(self, auth_headers):
        """Room info includes webinar_id, title, status, host_name"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/room-info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["webinar_id"] == TEST_WEBINAR_ID
        assert "title" in data and len(data["title"]) > 0
        assert "status" in data
        assert "host_name" in data
        
        print(f"Webinar: {data['title']} - Status: {data['status']}")

    # --- Roles Management Tests ---
    
    def test_get_webinar_roles(self, auth_headers):
        """GET /api/karau/webinar/{id}/roles returns host info and active_roles"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get roles failed: {response.text}"
        data = response.json()
        
        # Should have roles dict with host info
        assert "roles" in data, "Missing roles field"
        assert "host" in data["roles"], "Missing host in roles"
        assert "user_id" in data["roles"]["host"], "Missing user_id in host role"
        
        print(f"Roles response: {data}")

    def test_promote_user_to_presenter(self, auth_headers):
        """POST /api/karau/webinar/{id}/roles/promote promotes user to presenter"""
        test_user_id = "test_user_promote_presenter"
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/promote",
            headers=auth_headers,
            json={
                "user_id": test_user_id,
                "role": "presenter"
            }
        )
        assert response.status_code == 200, f"Promote failed: {response.text}"
        data = response.json()
        
        assert data["success"] is True
        assert data["user_id"] == test_user_id
        assert data["role"] == "presenter"
        
        print(f"Promoted {test_user_id} to presenter")
        
        # Clean up - demote the user
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/demote",
            headers=auth_headers,
            json={"user_id": test_user_id}
        )

    def test_promote_user_to_panelist(self, auth_headers):
        """POST /api/karau/webinar/{id}/roles/promote promotes user to panelist"""
        test_user_id = "test_user_promote_panelist"
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/promote",
            headers=auth_headers,
            json={
                "user_id": test_user_id,
                "role": "panelist"
            }
        )
        assert response.status_code == 200, f"Promote failed: {response.text}"
        data = response.json()
        
        assert data["success"] is True
        assert data["role"] == "panelist"
        
        print(f"Promoted {test_user_id} to panelist")
        
        # Clean up
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/demote",
            headers=auth_headers,
            json={"user_id": test_user_id}
        )

    def test_demote_user(self, auth_headers):
        """POST /api/karau/webinar/{id}/roles/demote demotes user back to attendee"""
        test_user_id = "test_user_demote"
        
        # First promote
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/promote",
            headers=auth_headers,
            json={"user_id": test_user_id, "role": "presenter"}
        )
        
        # Then demote
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/demote",
            headers=auth_headers,
            json={"user_id": test_user_id}
        )
        assert response.status_code == 200, f"Demote failed: {response.text}"
        data = response.json()
        
        assert data["success"] is True
        assert data["demoted"] is True
        
        print(f"Demoted {test_user_id} to attendee")

    def test_promote_invalid_role_fails(self, auth_headers):
        """Promoting with invalid role returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/promote",
            headers=auth_headers,
            json={
                "user_id": "test_user",
                "role": "invalid_role"
            }
        )
        assert response.status_code == 400, f"Expected 400 for invalid role, got {response.status_code}"
        print("Invalid role correctly rejected with 400")

    # --- Hand Raise Tests ---
    
    def test_hand_raise(self, auth_headers):
        """POST /api/karau/webinar/{id}/hand-raise adds user to hand_raises"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/hand-raise",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Hand raise failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        
        print("Hand raised successfully")

    def test_get_hand_raises(self, auth_headers):
        """GET /api/karau/webinar/{id}/hand-raises returns list of raised hands"""
        # First raise hand to ensure there's data
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/hand-raise",
            headers=auth_headers
        )
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/hand-raises",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get hand raises failed: {response.text}"
        data = response.json()
        
        assert "hand_raises" in data, "Missing hand_raises field"
        assert isinstance(data["hand_raises"], list)
        
        print(f"Hand raises count: {len(data['hand_raises'])}")

    def test_hand_lower(self, auth_headers):
        """POST /api/karau/webinar/{id}/hand-lower removes user from hand_raises"""
        # First raise hand
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/hand-raise",
            headers=auth_headers
        )
        
        # Then lower
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/hand-lower",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Hand lower failed: {response.text}"
        data = response.json()
        assert data["success"] is True
        
        print("Hand lowered successfully")

    # --- Practice Session Tests ---
    
    def test_start_practice_session(self, auth_headers):
        """POST /api/karau/webinar/{id}/practice/start starts practice session"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/practice/start",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Start practice failed: {response.text}"
        data = response.json()
        
        assert data["success"] is True
        assert data["status"] == "practice"
        
        print("Practice session started")

    def test_room_info_shows_practice_mode(self, auth_headers):
        """Room info shows practice_mode=True during practice"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/room-info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # After starting practice, practice_mode should be True
        assert data["practice_mode"] is True, "Expected practice_mode to be True"
        assert data["status"] == "practice", f"Expected status 'practice', got {data['status']}"
        
        print(f"Practice mode confirmed: {data['practice_mode']}, status: {data['status']}")

    def test_end_practice_session(self, auth_headers):
        """POST /api/karau/webinar/{id}/practice/end ends practice session"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/practice/end",
            headers=auth_headers
        )
        assert response.status_code == 200, f"End practice failed: {response.text}"
        data = response.json()
        
        assert data["success"] is True
        assert data["status"] == "scheduled"
        
        print("Practice session ended, status back to scheduled")

    def test_room_info_after_practice_ended(self, auth_headers):
        """Room info shows practice_mode=False after practice ends"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/room-info",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["practice_mode"] is False, "Expected practice_mode to be False after ending"
        assert data["status"] == "scheduled"
        
        print("Practice mode ended, status: scheduled")

    # --- Selective Unmute Test ---
    
    def test_unmute_user(self, auth_headers):
        """POST /api/karau/webinar/{id}/controls/unmute-user returns success"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/controls/unmute-user",
            headers=auth_headers,
            params={"target_user_id": "test_user_unmute"}
        )
        assert response.status_code == 200, f"Unmute user failed: {response.text}"
        data = response.json()
        
        assert data["success"] is True
        assert data["target_user_id"] == "test_user_unmute"
        assert data["action"] == "unmute_request"
        
        print("Selective unmute successful")

    # --- Edge Cases ---
    
    def test_room_info_nonexistent_webinar(self, auth_headers):
        """Room info returns 404 for nonexistent webinar"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/NONEXISTENT-ID/room-info",
            headers=auth_headers
        )
        assert response.status_code == 404
        print("Nonexistent webinar correctly returns 404")

    def test_promote_without_host_permission(self):
        """Non-host cannot promote users (test with different/no auth)"""
        # This would require a second user account to properly test
        # For now, test that unauthorized request fails
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}/roles/promote",
            headers={"Content-Type": "application/json"},
            json={"user_id": "test", "role": "presenter"}
        )
        # Should fail with 401 or 403
        assert response.status_code in [401, 403, 422], f"Expected auth error, got {response.status_code}"
        print("Unauthorized promote correctly rejected")


class TestWebinarListAndStatus:
    """Tests for webinar list and status badges"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

    def test_webinar_list_returns_status(self, auth_headers):
        """GET /api/karau/webinar/list includes status field"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"List failed: {response.text}"
        data = response.json()
        
        assert "webinars" in data
        if len(data["webinars"]) > 0:
            webinar = data["webinars"][0]
            assert "status" in webinar, "Missing status field in webinar"
            assert webinar["status"] in ["scheduled", "live", "practice", "ended"]
            print(f"Found {len(data['webinars'])} webinars with status field")
        else:
            print("No webinars found in list")

    def test_webinar_details_returns_status(self, auth_headers):
        """GET /api/karau/webinar/{id} includes status"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{TEST_WEBINAR_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        print(f"Webinar {TEST_WEBINAR_ID} status: {data['status']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
