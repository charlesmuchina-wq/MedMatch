"""
Test Lobby/Waiting Room Features for AI KARAU Meeting Platform
Tests:
  - Guest lobby join
  - Authenticated user lobby join  
  - Host auto-admission
  - Host admit/deny guests
  - Admit-all functionality
  - Waiting room toggle
  - Lobby status polling
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"

class TestLobbyAuthentication:
    """Authentication tests for lobby endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth tokens for testing"""
        # Admin login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        self.admin_token = data.get("access_token")
        self.admin_user_id = data.get("user", {}).get("user_id")
        assert self.admin_token, "No access_token returned"
        
    def test_admin_login(self):
        """Verify admin login returns access_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✓ Admin login successful, token received")


class TestLobbyGuestJoin:
    """Test guest joining the lobby"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Create a meeting first"""
        # Admin login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        data = response.json()
        self.admin_token = data.get("access_token")
        self.admin_user_id = data.get("user", {}).get("user_id")
        
        # Create meeting
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"title": "TEST_Lobby_Guest_Meeting"}
        )
        assert response.status_code == 200
        self.meeting_id = response.json()["meeting_id"]
        print(f"✓ Meeting created: {self.meeting_id}")
    
    def test_guest_join_lobby(self):
        """POST /api/karau-meet/meetings/{id}/lobby/join - Guest join puts user in waiting state"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={
                "guest_name": "Test Guest",
                "guest_email": "guest@test.com",
                "is_guest": True
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "user_id" in data
        assert data["status"] == "waiting", f"Expected 'waiting', got '{data['status']}'"
        assert data.get("require_admission") == True
        print(f"✓ Guest placed in waiting status: {data['user_id']}")
        
        # Store for next test
        self.guest_user_id = data["user_id"]
        return data
    
    def test_guest_lobby_status_poll(self):
        """GET /api/karau-meet/meetings/{id}/lobby/status - Check guest status"""
        # First join as guest
        join_response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "Poll Test Guest", "is_guest": True}
        )
        guest_user_id = join_response.json()["user_id"]
        
        # Poll status
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/status",
            params={"user_id": guest_user_id}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "admitted" in data
        assert data["status"] == "waiting"
        assert data["admitted"] == False
        print(f"✓ Guest status poll working: status={data['status']}, admitted={data['admitted']}")


class TestLobbyAuthenticatedJoin:
    """Test authenticated user joining lobby"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Admin login and create meeting
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        data = response.json()
        self.admin_token = data.get("access_token")
        self.admin_user_id = data.get("user", {}).get("user_id")
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"title": "TEST_Auth_Lobby_Meeting"}
        )
        self.meeting_id = response.json()["meeting_id"]
    
    def test_host_auto_admitted(self):
        """POST /api/karau-meet/meetings/{id}/lobby/join-auth - Host auto-admitted"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join-auth",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Host should be auto-admitted
        assert data["status"] == "admitted", f"Host not auto-admitted: {data['status']}"
        assert data.get("is_host") == True
        print(f"✓ Host auto-admitted: status={data['status']}, is_host={data['is_host']}")
    
    def test_non_host_placed_in_waiting(self):
        """POST /api/karau-meet/meetings/{id}/lobby/join-auth - Non-host goes to waiting"""
        # Login as test user (not host)
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Test user not available")
        
        test_token = response.json().get("access_token")
        
        # Join lobby as non-host
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join-auth",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Non-host should be in waiting
        assert data["status"] == "waiting", f"Non-host not in waiting: {data['status']}"
        assert data.get("is_host") == False
        print(f"✓ Non-host placed in waiting: status={data['status']}, is_host={data['is_host']}")


class TestLobbyHostControls:
    """Test host controls for admitting/denying users"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Admin login
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        data = response.json()
        self.admin_token = data.get("access_token")
        
        # Create meeting
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"title": "TEST_Host_Controls_Meeting"}
        )
        self.meeting_id = response.json()["meeting_id"]
        print(f"✓ Meeting created: {self.meeting_id}")
    
    def test_host_admit_guest(self):
        """POST /api/karau-meet/meetings/{id}/lobby/admit - Host admits guest"""
        # First add a guest to waiting room
        join_response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "Admit Test Guest", "is_guest": True}
        )
        guest_user_id = join_response.json()["user_id"]
        
        # Host admits guest
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/admit",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"user_id": guest_user_id}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True or data.get("admitted") == True
        print(f"✓ Guest admitted by host: {guest_user_id}")
        
        # Verify guest status is now admitted
        status_response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/status",
            params={"user_id": guest_user_id}
        )
        status_data = status_response.json()
        assert status_data["status"] == "admitted" or status_data["admitted"] == True
        print(f"✓ Guest status verified as admitted")
    
    def test_host_deny_guest(self):
        """POST /api/karau-meet/meetings/{id}/lobby/deny - Host denies guest"""
        # Add guest
        join_response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "Deny Test Guest", "is_guest": True}
        )
        guest_user_id = join_response.json()["user_id"]
        
        # Host denies guest
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/deny",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"user_id": guest_user_id}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True or data.get("rejected") == True
        print(f"✓ Guest denied by host: {guest_user_id}")
        
        # Verify guest status is rejected
        status_response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/status",
            params={"user_id": guest_user_id}
        )
        status_data = status_response.json()
        assert status_data["status"] == "rejected" or status_data["rejected"] == True
        print(f"✓ Guest status verified as rejected")
    
    def test_host_get_waiting_list(self):
        """GET /api/karau-meet/meetings/{id}/lobby/waiting - Host views waiting list"""
        # Add multiple guests
        for i in range(3):
            requests.post(
                f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
                json={"guest_name": f"Waiting Guest {i+1}", "is_guest": True}
            )
        
        # Host gets waiting list
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/waiting",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "waiting" in data
        assert "count" in data
        assert data["count"] >= 3
        print(f"✓ Waiting list retrieved: {data['count']} guests waiting")
    
    def test_host_admit_all(self):
        """POST /api/karau-meet/meetings/{id}/lobby/admit-all - Host admits all waiting guests"""
        # Create fresh meeting for this test
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"title": "TEST_Admit_All_Meeting"}
        )
        meeting_id = response.json()["meeting_id"]
        
        # Add multiple guests
        guest_ids = []
        for i in range(3):
            join_resp = requests.post(
                f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
                json={"guest_name": f"Admit All Guest {i+1}", "is_guest": True}
            )
            guest_ids.append(join_resp.json()["user_id"])
        
        # Host admits all
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/admit-all",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "admitted" in data
        assert data["admitted"] >= 3
        print(f"✓ Admit-all: {data['admitted']} guests admitted")
        
        # Verify all guests are admitted
        for guest_id in guest_ids:
            status_resp = requests.get(
                f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/status",
                params={"user_id": guest_id}
            )
            assert status_resp.json()["admitted"] == True
        print(f"✓ All {len(guest_ids)} guests verified as admitted")


class TestWaitingRoomSettings:
    """Test waiting room enable/disable"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        data = response.json()
        self.admin_token = data.get("access_token")
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"title": "TEST_WR_Settings_Meeting"}
        )
        self.meeting_id = response.json()["meeting_id"]
    
    def test_toggle_waiting_room_off(self):
        """PUT /api/karau-meet/meetings/{id}/settings/waiting-room?enabled=false"""
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/settings/waiting-room",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            params={"enabled": "false"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("waiting_room_enabled") == False
        print(f"✓ Waiting room disabled")
        
        # Verify guest can join directly when WR disabled
        join_response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "Direct Join Guest", "is_guest": True}
        )
        join_data = join_response.json()
        # When WR is disabled, guest should be auto-admitted
        assert join_data["status"] == "admitted"
        print(f"✓ Guest auto-admitted when waiting room disabled")
    
    def test_toggle_waiting_room_on(self):
        """PUT /api/karau-meet/meetings/{id}/settings/waiting-room?enabled=true"""
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/settings/waiting-room",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            params={"enabled": "true"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data.get("success") == True
        assert data.get("waiting_room_enabled") == True
        print(f"✓ Waiting room enabled")


class TestMeetingInfo:
    """Test public meeting info endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        data = response.json()
        self.admin_token = data.get("access_token")
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"title": "TEST_Info_Meeting"}
        )
        self.meeting_id = response.json()["meeting_id"]
    
    def test_get_meeting_info_public(self):
        """GET /api/karau-meet/meetings/{id}/info - Public endpoint for lobby"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/info"
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "meeting_id" in data
        assert "title" in data
        assert "host_name" in data
        assert "status" in data
        assert data["meeting_id"] == self.meeting_id
        print(f"✓ Public meeting info: title={data['title']}, host={data['host_name']}")
    
    def test_meeting_info_not_found(self):
        """GET /api/karau-meet/meetings/{invalid_id}/info - Returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/INVALID123/info"
        )
        assert response.status_code == 404
        print(f"✓ Invalid meeting ID returns 404")


class TestNonHostRestrictions:
    """Test that non-hosts cannot perform host actions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Admin creates meeting
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        data = response.json()
        self.admin_token = data.get("access_token")
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            json={"title": "TEST_Restrictions_Meeting"}
        )
        self.meeting_id = response.json()["meeting_id"]
        
        # Get test user token
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            self.test_token = response.json().get("access_token")
        else:
            self.test_token = None
    
    def test_non_host_cannot_view_waiting_list(self):
        """Non-host cannot GET waiting list"""
        if not self.test_token:
            pytest.skip("Test user not available")
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/waiting",
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        assert response.status_code == 403
        print(f"✓ Non-host blocked from viewing waiting list (403)")
    
    def test_non_host_cannot_admit(self):
        """Non-host cannot admit guests"""
        if not self.test_token:
            pytest.skip("Test user not available")
        
        # Add a guest first
        join_resp = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "Block Test Guest", "is_guest": True}
        )
        guest_id = join_resp.json()["user_id"]
        
        # Try to admit as non-host
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/admit",
            headers={"Authorization": f"Bearer {self.test_token}"},
            json={"user_id": guest_id}
        )
        assert response.status_code == 403
        print(f"✓ Non-host blocked from admitting (403)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
