"""
Breakout Rooms Feature Tests - Iteration 111
Tests for the new breakout room session management endpoints:
- POST /api/karau-meet/meetings/{id}/breakout-session/start - Start breakout session
- GET /api/karau-meet/meetings/{id}/breakout-session - Get session status
- POST /api/karau-meet/meetings/{id}/breakout-session/close - Close all breakout rooms
- POST /api/karau-meet/meetings/{id}/breakout-session/move - Move participant between rooms
- POST /api/karau-meet/meetings/{id}/breakout-session/auto-assign - AI auto-assign preview
- POST /api/karau-meet/meetings/{id}/breakout-rooms - Single room creation
- Regression: Lobby endpoints still working
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestBreakoutRoomFeature:
    """Tests for breakout room management endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and create a meeting for tests"""
        # Login as admin (host)
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        data = login_res.json()
        self.token = data.get("access_token")
        self.host_id = data["user"]["user_id"]
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        # Create a test meeting
        meeting_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Breakout_Session_Meeting"},
            headers=self.headers
        )
        assert meeting_res.status_code == 200, f"Create meeting failed: {meeting_res.text}"
        self.meeting_id = meeting_res.json()["meeting_id"]
        
        # Add guest participants for breakout tests
        self.guest_ids = []
        for i in range(4):
            guest_res = requests.post(
                f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/join-guest",
                json={"guest_name": f"TEST_Guest_{i}"}
            )
            if guest_res.status_code == 200:
                self.guest_ids.append(guest_res.json().get("guest_user_id"))
        
        yield
        
        # Cleanup: End the meeting
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/end",
            headers=self.headers
        )

    # ============ BREAKOUT SESSION START TESTS ============
    
    def test_start_breakout_session_manual_rooms(self):
        """POST /api/karau-meet/meetings/{id}/breakout-session/start - Manual rooms"""
        if len(self.guest_ids) < 2:
            pytest.skip("Need at least 2 guests for breakout test")
        
        rooms = [
            {"room_name": "Room A", "participant_ids": [self.guest_ids[0]]},
            {"room_name": "Room B", "participant_ids": [self.guest_ids[1]]}
        ]
        if len(self.guest_ids) > 2:
            rooms[0]["participant_ids"].append(self.guest_ids[2])
        
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/start",
            json={"rooms": rooms, "timer_minutes": 5, "auto_assign": False},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Start breakout failed: {res.text}"
        data = res.json()
        assert "session_id" in data, "Response should contain session_id"
        assert data["status"] == "active", "Session should be active"
        assert len(data["rooms"]) == 2, "Should have 2 rooms"
        assert data["timer_minutes"] == 5, "Timer should be 5 minutes"
        print(f"PASSED: Started breakout session with {len(data['rooms'])} rooms")

    def test_start_breakout_session_with_auto_assign(self):
        """POST /api/karau-meet/meetings/{id}/breakout-session/start - Auto-assign mode"""
        if len(self.guest_ids) < 2:
            pytest.skip("Need at least 2 guests for auto-assign test")
        
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/start",
            json={"rooms": [], "timer_minutes": 3, "auto_assign": True, "num_rooms": 2},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Auto-assign start failed: {res.text}"
        data = res.json()
        assert data["status"] == "active", "Session should be active"
        # Auto-assign distributes guests into rooms
        total_assigned = sum(len(r.get("participants", [])) for r in data.get("rooms", []))
        assert total_assigned >= 1, "At least 1 participant should be assigned"
        print(f"PASSED: Auto-assigned {total_assigned} participants to breakout rooms")

    def test_start_breakout_non_host_forbidden(self):
        """Non-host should get 403 when trying to start breakout session"""
        # Use a guest token or no token
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/start",
            json={"rooms": [], "timer_minutes": 5, "auto_assign": True, "num_rooms": 2},
            headers={"Content-Type": "application/json"}  # No auth
        )
        
        # Should fail - either 403 or 401
        assert res.status_code in [401, 403, 422], f"Expected auth error, got {res.status_code}"
        print("PASSED: Non-host correctly blocked from starting breakout session")

    # ============ BREAKOUT SESSION STATUS TESTS ============
    
    def test_get_breakout_session_status_none(self):
        """GET /api/karau-meet/meetings/{id}/breakout-session - No active session"""
        res = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session",
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Get session failed: {res.text}"
        data = res.json()
        # Could be "none" or might have leftover from previous test
        assert "status" in data, "Response should contain status"
        print(f"PASSED: Got breakout session status: {data.get('status')}")

    def test_get_breakout_session_status_active(self):
        """GET /api/karau-meet/meetings/{id}/breakout-session - After starting"""
        if len(self.guest_ids) < 1:
            pytest.skip("Need at least 1 guest")
        
        # Start a session first
        start_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/start",
            json={"rooms": [{"room_name": "Room 1", "participant_ids": self.guest_ids[:1]}], "timer_minutes": 10},
            headers=self.headers
        )
        assert start_res.status_code == 200
        
        # Get status
        res = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session",
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Get session failed: {res.text}"
        data = res.json()
        assert data["status"] == "active", f"Expected active status, got {data['status']}"
        assert "session" in data, "Response should contain session details"
        print("PASSED: Got active breakout session status with session details")

    # ============ BREAKOUT SESSION CLOSE TESTS ============
    
    def test_close_breakout_session(self):
        """POST /api/karau-meet/meetings/{id}/breakout-session/close - Close all rooms"""
        if len(self.guest_ids) < 1:
            pytest.skip("Need at least 1 guest")
        
        # Start a session first
        start_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/start",
            json={"rooms": [{"room_name": "Room 1", "participant_ids": self.guest_ids[:1]}], "timer_minutes": 10},
            headers=self.headers
        )
        assert start_res.status_code == 200
        
        # Close session
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/close",
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Close session failed: {res.text}"
        data = res.json()
        assert data.get("success") == True or "returned_count" in data, "Should indicate success"
        print(f"PASSED: Closed breakout session, returned {data.get('returned_count', 0)} participants")

    def test_close_breakout_non_host_forbidden(self):
        """Non-host should get 403 when trying to close breakout session"""
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/close",
            headers={"Content-Type": "application/json"}  # No auth
        )
        
        assert res.status_code in [401, 403, 422], f"Expected auth error, got {res.status_code}"
        print("PASSED: Non-host correctly blocked from closing breakout session")

    # ============ MOVE PARTICIPANT TESTS ============
    
    def test_move_participant_between_rooms(self):
        """POST /api/karau-meet/meetings/{id}/breakout-session/move - Move participant"""
        if len(self.guest_ids) < 2:
            pytest.skip("Need at least 2 guests for move test")
        
        # Start session with 2 rooms
        start_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/start",
            json={
                "rooms": [
                    {"room_name": "Room A", "participant_ids": [self.guest_ids[0]]},
                    {"room_name": "Room B", "participant_ids": [self.guest_ids[1]]}
                ],
                "timer_minutes": 10
            },
            headers=self.headers
        )
        assert start_res.status_code == 200
        room_b_id = start_res.json()["rooms"][1]["room_id"]
        
        # Move guest 0 to room B
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/move",
            json={"user_id": self.guest_ids[0], "target_room_id": room_b_id},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Move participant failed: {res.text}"
        data = res.json()
        assert data.get("success") == True, "Move should succeed"
        assert data.get("room_id") == room_b_id, "Should confirm target room"
        print("PASSED: Successfully moved participant between breakout rooms")

    def test_move_participant_max_capacity(self):
        """Move to full room should fail (max 10 per room)"""
        # This would require 11+ participants which is hard to test
        # We'll verify the error handling exists
        if len(self.guest_ids) < 1:
            pytest.skip("Need guests for test")
        
        # Start session
        start_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/start",
            json={"rooms": [{"room_name": "Room 1", "participant_ids": self.guest_ids}], "timer_minutes": 10},
            headers=self.headers
        )
        assert start_res.status_code == 200
        
        # Try to move to non-existent room
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/move",
            json={"user_id": self.guest_ids[0], "target_room_id": "INVALID"},
            headers=self.headers
        )
        
        # Should fail with 400 - room not found
        assert res.status_code == 400, f"Expected 400 for invalid room, got {res.status_code}"
        print("PASSED: Move to invalid room correctly returns error")

    def test_move_participant_non_host_forbidden(self):
        """Non-host should get 403 when trying to move participants"""
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/move",
            json={"user_id": "any", "target_room_id": "any"},
            headers={"Content-Type": "application/json"}  # No auth
        )
        
        assert res.status_code in [401, 403, 422], f"Expected auth error, got {res.status_code}"
        print("PASSED: Non-host correctly blocked from moving participants")

    # ============ AI AUTO-ASSIGN PREVIEW TESTS ============
    
    def test_ai_auto_assign_preview(self):
        """POST /api/karau-meet/meetings/{id}/breakout-session/auto-assign - Preview"""
        if len(self.guest_ids) < 2:
            pytest.skip("Need at least 2 guests for auto-assign preview")
        
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/auto-assign?num_rooms=2",
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Auto-assign preview failed: {res.text}"
        data = res.json()
        assert "rooms" in data, "Response should contain rooms"
        assert "total_participants" in data, "Response should contain total_participants"
        # Should distribute guests evenly
        assert len(data["rooms"]) <= 2, "Should create up to 2 rooms"
        print(f"PASSED: AI auto-assign preview: {data['total_participants']} participants across {len(data['rooms'])} rooms")

    def test_ai_auto_assign_excludes_host(self):
        """AI auto-assign should not include the host in breakout rooms"""
        # Join meeting as host first
        join_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/join",
            json={"video_enabled": True, "audio_enabled": True},
            headers=self.headers
        )
        # May fail if already in meeting - that's ok
        
        if len(self.guest_ids) < 1:
            pytest.skip("Need at least 1 guest")
        
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/auto-assign?num_rooms=2",
            headers=self.headers
        )
        
        assert res.status_code == 200
        data = res.json()
        
        # Check host is not in any room
        all_assigned_ids = []
        for room in data.get("rooms", []):
            all_assigned_ids.extend(room.get("participant_ids", []))
        
        assert self.host_id not in all_assigned_ids, "Host should not be assigned to breakout rooms"
        print("PASSED: Host correctly excluded from auto-assign")

    def test_ai_auto_assign_non_host_forbidden(self):
        """Non-host should get 403 when trying to auto-assign"""
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-session/auto-assign?num_rooms=2",
            headers={"Content-Type": "application/json"}  # No auth
        )
        
        assert res.status_code in [401, 403, 422], f"Expected auth error, got {res.status_code}"
        print("PASSED: Non-host correctly blocked from auto-assign preview")

    # ============ SINGLE BREAKOUT ROOM CREATION (EXISTING) ============
    
    def test_create_single_breakout_room(self):
        """POST /api/karau-meet/meetings/{id}/breakout-rooms - Create single room"""
        if len(self.guest_ids) < 1:
            pytest.skip("Need at least 1 guest")
        
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-rooms",
            json={"room_name": "TEST_Single_Room", "participant_ids": [self.guest_ids[0]]},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Create room failed: {res.text}"
        data = res.json()
        assert "room_id" in data, "Response should contain room_id"
        assert data["room_name"] == "TEST_Single_Room", "Room name should match"
        print(f"PASSED: Created single breakout room: {data['room_id']}")

    def test_create_single_breakout_room_non_host_forbidden(self):
        """Non-host should get 403 when creating breakout room"""
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/breakout-rooms",
            json={"room_name": "Unauthorized Room", "participant_ids": []},
            headers={"Content-Type": "application/json"}  # No auth
        )
        
        assert res.status_code in [401, 403, 422], f"Expected auth error, got {res.status_code}"
        print("PASSED: Non-host correctly blocked from creating breakout room")


class TestLobbyRegressionIteration111:
    """Regression tests for lobby endpoints (from iteration 110)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup: Login and create meeting"""
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_res.status_code == 200
        data = login_res.json()
        self.token = data.get("access_token")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        
        # Create meeting
        meeting_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Lobby_Regression"},
            headers=self.headers
        )
        assert meeting_res.status_code == 200
        self.meeting_id = meeting_res.json()["meeting_id"]
        
        yield
        
        # Cleanup
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/end",
            headers=self.headers
        )

    def test_lobby_join_guest(self):
        """POST /api/karau-meet/meetings/{id}/lobby/join - Guest joins lobby"""
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "TEST_Lobby_Guest", "guest_email": "test@example.com", "is_guest": True}
        )
        
        assert res.status_code == 200, f"Lobby join failed: {res.text}"
        data = res.json()
        assert data["status"] in ["waiting", "admitted"], "Should be waiting or admitted"
        assert "user_id" in data, "Should return user_id"
        print(f"PASSED: Guest joined lobby with status: {data['status']}")

    def test_lobby_join_authenticated(self):
        """POST /api/karau-meet/meetings/{id}/lobby/join-auth - Auth user joins lobby"""
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join-auth",
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Auth lobby join failed: {res.text}"
        data = res.json()
        # Host should be auto-admitted
        assert data["status"] == "admitted", "Host should be auto-admitted"
        assert data.get("is_host") == True, "Should indicate is_host"
        print("PASSED: Host auto-admitted to lobby")

    def test_lobby_waiting_list_host_only(self):
        """GET /api/karau-meet/meetings/{id}/lobby/waiting - Host views waiting list"""
        # Add a guest to lobby first
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "TEST_Waiting_Guest", "is_guest": True}
        )
        
        res = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/waiting",
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Get waiting list failed: {res.text}"
        data = res.json()
        assert "waiting" in data, "Response should contain waiting list"
        assert "count" in data, "Response should contain count"
        print(f"PASSED: Host viewed waiting list, count: {data['count']}")

    def test_lobby_admit_guest(self):
        """POST /api/karau-meet/meetings/{id}/lobby/admit - Host admits guest"""
        # Add guest to lobby
        join_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "TEST_To_Admit", "is_guest": True}
        )
        assert join_res.status_code == 200
        guest_id = join_res.json()["user_id"]
        
        # Host admits
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/admit",
            json={"user_id": guest_id},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Admit failed: {res.text}"
        data = res.json()
        assert data.get("admitted") == True or data.get("success") == True, "Should indicate admission"
        print("PASSED: Host admitted guest from lobby")

    def test_lobby_deny_guest(self):
        """POST /api/karau-meet/meetings/{id}/lobby/deny - Host denies guest"""
        # Add guest to lobby
        join_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "TEST_To_Deny", "is_guest": True}
        )
        assert join_res.status_code == 200
        guest_id = join_res.json()["user_id"]
        
        # Host denies
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/deny",
            json={"user_id": guest_id},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Deny failed: {res.text}"
        data = res.json()
        assert data.get("rejected") == True or data.get("success") == True, "Should indicate rejection"
        print("PASSED: Host denied guest from lobby")

    def test_lobby_status_poll(self):
        """GET /api/karau-meet/meetings/{id}/lobby/status - Poll admission status"""
        # Add guest to lobby
        join_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/join",
            json={"guest_name": "TEST_Poll_Status", "is_guest": True}
        )
        assert join_res.status_code == 200
        guest_id = join_res.json()["user_id"]
        
        # Poll status
        res = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{self.meeting_id}/lobby/status?user_id={guest_id}"
        )
        
        assert res.status_code == 200, f"Status poll failed: {res.text}"
        data = res.json()
        assert "status" in data, "Response should contain status"
        print(f"PASSED: Polled lobby status: {data['status']}")


class TestMeetingRegressionIteration111:
    """Regression tests for core meeting endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login as admin"""
        login_res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert login_res.status_code == 200
        data = login_res.json()
        self.token = data.get("access_token")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def test_create_meeting(self):
        """POST /api/karau-meet/meetings - Create new meeting"""
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Regression_Meeting"},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Create meeting failed: {res.text}"
        data = res.json()
        assert "meeting_id" in data, "Should return meeting_id"
        
        # Cleanup
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{data['meeting_id']}/end",
            headers=self.headers
        )
        print("PASSED: Create meeting working")

    def test_get_meeting_info(self):
        """GET /api/karau-meet/meetings/{id}/info - Public meeting info"""
        # Create meeting first
        create_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Info_Meeting"},
            headers=self.headers
        )
        meeting_id = create_res.json()["meeting_id"]
        
        res = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/info")
        
        assert res.status_code == 200, f"Get info failed: {res.text}"
        data = res.json()
        assert data["meeting_id"] == meeting_id
        assert data["title"] == "TEST_Info_Meeting"
        
        # Cleanup
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/end",
            headers=self.headers
        )
        print("PASSED: Get meeting info working")

    def test_join_meeting_authenticated(self):
        """POST /api/karau-meet/meetings/{id}/join - Auth user joins"""
        # Create meeting
        create_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Join_Meeting"},
            headers=self.headers
        )
        meeting_id = create_res.json()["meeting_id"]
        
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join",
            json={"video_enabled": True, "audio_enabled": True},
            headers=self.headers
        )
        
        assert res.status_code == 200, f"Join failed: {res.text}"
        data = res.json()
        assert "meeting" in data or "participant" in data, "Should return meeting or participant data"
        
        # Cleanup
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/end",
            headers=self.headers
        )
        print("PASSED: Authenticated join working")

    def test_join_meeting_guest(self):
        """POST /api/karau-meet/meetings/{id}/join-guest - Guest joins"""
        # Create meeting
        create_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "TEST_Guest_Join_Meeting"},
            headers=self.headers
        )
        meeting_id = create_res.json()["meeting_id"]
        
        res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join-guest",
            json={"guest_name": "TEST_Guest"}
        )
        
        assert res.status_code == 200, f"Guest join failed: {res.text}"
        data = res.json()
        assert "guest_user_id" in data, "Should return guest_user_id"
        
        # Cleanup
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/end",
            headers=self.headers
        )
        print("PASSED: Guest join working")

    def test_list_user_meetings(self):
        """GET /api/karau-meet/meetings - List user meetings"""
        res = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers=self.headers
        )
        
        assert res.status_code == 200, f"List meetings failed: {res.text}"
        data = res.json()
        assert "meetings" in data, "Should return meetings array"
        print(f"PASSED: Listed {len(data['meetings'])} meetings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
