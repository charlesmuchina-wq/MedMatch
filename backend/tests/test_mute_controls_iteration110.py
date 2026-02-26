"""
Test Iteration 110: Mute Controls and Active Speaker Features
Tests WebSocket message handlers for mute_participant, mute_all, pass_mic
Also verifies lobby endpoints still work correctly from previous iteration
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestAuthentication:
    """Auth endpoint tests"""
    
    def test_admin_login_success(self):
        """Verify admin can login and receive access_token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "access_token not in response"
        print(f"SUCCESS: Admin login returns 200 with access_token")
        return data["access_token"]


class TestLobbyEndpoints:
    """Lobby/Waiting Room API tests (regression from iteration 109)"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Auth failed")
    
    @pytest.fixture
    def test_meeting(self, auth_token):
        """Create a test meeting for lobby tests"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_MuteControl_Meeting"}
        )
        if response.status_code == 200:
            return response.json()
        pytest.skip("Could not create meeting")
    
    def test_lobby_join_guest(self, test_meeting):
        """Guest can join waiting room"""
        meeting_id = test_meeting.get("meeting_id")
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"guest_name": "TEST_Guest", "guest_email": "test@guest.com", "is_guest": True}
        )
        assert response.status_code == 200, f"Lobby join failed: {response.text}"
        data = response.json()
        assert data.get("status") in ["waiting", "admitted"]
        print(f"SUCCESS: Guest joined lobby with status={data.get('status')}")
    
    def test_lobby_join_authenticated(self, auth_token, test_meeting):
        """Authenticated user/host joins lobby (auto-admitted)"""
        meeting_id = test_meeting.get("meeting_id")
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join-auth",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Auth lobby join failed: {response.text}"
        data = response.json()
        # Host should be auto-admitted
        assert data.get("status") == "admitted", f"Host not auto-admitted: {data}"
        print(f"SUCCESS: Host auto-admitted to lobby")
    
    def test_lobby_status_poll(self, test_meeting):
        """Poll admission status"""
        meeting_id = test_meeting.get("meeting_id")
        # First join as guest
        join_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"guest_name": "TEST_Poller", "is_guest": True}
        )
        user_id = join_res.json().get("user_id")
        
        # Poll status
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/status?user_id={user_id}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"SUCCESS: Lobby status poll returns {data.get('status')}")
    
    def test_lobby_waiting_list(self, auth_token, test_meeting):
        """Host can view waiting list"""
        meeting_id = test_meeting.get("meeting_id")
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/waiting",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "waiting" in data
        assert "count" in data
        print(f"SUCCESS: Host can view waiting list, count={data.get('count')}")
    
    def test_lobby_admit_guest(self, auth_token, test_meeting):
        """Host can admit a guest"""
        meeting_id = test_meeting.get("meeting_id")
        # First add a guest to waiting room
        join_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"guest_name": "TEST_ToAdmit", "is_guest": True}
        )
        guest_user_id = join_res.json().get("user_id")
        
        # Host admits the guest
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/admit",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"user_id": guest_user_id}
        )
        assert response.status_code == 200
        print(f"SUCCESS: Host admitted guest {guest_user_id}")
    
    def test_lobby_deny_guest(self, auth_token, test_meeting):
        """Host can deny a guest"""
        meeting_id = test_meeting.get("meeting_id")
        # Add guest
        join_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"guest_name": "TEST_ToDeny", "is_guest": True}
        )
        guest_user_id = join_res.json().get("user_id")
        
        # Host denies
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/deny",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"user_id": guest_user_id}
        )
        assert response.status_code == 200
        print(f"SUCCESS: Host denied guest {guest_user_id}")
    
    def test_lobby_admit_all(self, auth_token, test_meeting):
        """Host can admit all waiting guests"""
        meeting_id = test_meeting.get("meeting_id")
        # Add some guests
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"guest_name": "TEST_AdmitAll1", "is_guest": True}
        )
        requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/join",
            json={"guest_name": "TEST_AdmitAll2", "is_guest": True}
        )
        
        # Admit all
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/lobby/admit-all",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"SUCCESS: Host admitted all waiting guests")
    
    def test_waiting_room_toggle(self, auth_token, test_meeting):
        """Host can toggle waiting room on/off"""
        meeting_id = test_meeting.get("meeting_id")
        
        # Disable waiting room
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/settings/waiting-room?enabled=false",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("waiting_room_enabled") == False
        print(f"SUCCESS: Waiting room disabled")
        
        # Re-enable
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/settings/waiting-room?enabled=true",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print(f"SUCCESS: Waiting room re-enabled")


class TestMeetingEndpoints:
    """Meeting CRUD endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get admin auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Auth failed")
    
    def test_create_meeting(self, auth_token):
        """Create a new meeting"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_Iteration110_Meeting"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "meeting_id" in data
        print(f"SUCCESS: Meeting created with ID={data.get('meeting_id')}")
        return data
    
    def test_get_meeting_info(self, auth_token):
        """Get public meeting info"""
        # Create meeting first
        create_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_InfoCheck"}
        )
        meeting_id = create_res.json().get("meeting_id")
        
        # Get public info (no auth required)
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/info")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "host_name" in data
        print(f"SUCCESS: Meeting info retrieved: {data.get('title')}")
    
    def test_get_meeting_info_not_found(self):
        """Invalid meeting returns 404"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/meetings/INVALID_TEST_ID/info")
        assert response.status_code == 404
        print(f"SUCCESS: Invalid meeting returns 404")
    
    def test_join_meeting(self, auth_token):
        """Join an existing meeting"""
        # Create meeting
        create_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_JoinTest"}
        )
        meeting_id = create_res.json().get("meeting_id")
        
        # Join meeting
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"video_enabled": True, "audio_enabled": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert "ice_servers" in data
        print(f"SUCCESS: Joined meeting with ICE servers")
    
    def test_join_meeting_as_guest(self, auth_token):
        """Join meeting as guest (no auth)"""
        # Create meeting first
        create_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_GuestJoin"}
        )
        meeting_id = create_res.json().get("meeting_id")
        
        # Join as guest
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/join-guest",
            json={"guest_name": "TEST_GuestUser", "video_enabled": True, "audio_enabled": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert "guest_user_id" in data
        print(f"SUCCESS: Guest joined with ID={data.get('guest_user_id')}")
    
    def test_get_my_meetings(self, auth_token):
        """Get user's meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "meetings" in data
        print(f"SUCCESS: Retrieved {len(data.get('meetings', []))} meetings")


class TestWebSocketSignalingHandlers:
    """Tests to verify WebSocket message type handlers exist in code
    Note: These verify code structure, not runtime WebSocket behavior
    """
    
    def test_verify_mute_participant_handler_exists(self):
        """Verify mute_participant handler is defined in webrtc_signaling.py"""
        import inspect
        from pathlib import Path
        
        signaling_file = Path("/app/backend/services/karau_meet/webrtc_signaling.py")
        content = signaling_file.read_text()
        
        # Check for mute_participant handler
        assert 'message_type == "mute_participant"' in content, "mute_participant handler not found"
        assert 'force_mute' in content, "force_mute action not found"
        print("SUCCESS: mute_participant WebSocket handler exists in code")
    
    def test_verify_mute_all_handler_exists(self):
        """Verify mute_all handler is defined in webrtc_signaling.py"""
        from pathlib import Path
        
        signaling_file = Path("/app/backend/services/karau_meet/webrtc_signaling.py")
        content = signaling_file.read_text()
        
        # Check for mute_all handler
        assert 'message_type == "mute_all"' in content, "mute_all handler not found"
        assert 'broadcast_to_meeting' in content, "broadcast function not used"
        print("SUCCESS: mute_all WebSocket handler exists in code")
    
    def test_verify_pass_mic_handler_exists(self):
        """Verify pass_mic handler is defined in webrtc_signaling.py"""
        from pathlib import Path
        
        signaling_file = Path("/app/backend/services/karau_meet/webrtc_signaling.py")
        content = signaling_file.read_text()
        
        # Check for pass_mic handler
        assert 'message_type == "pass_mic"' in content, "pass_mic handler not found"
        assert '"action": "pass_mic"' in content, "pass_mic action message not found"
        print("SUCCESS: pass_mic WebSocket handler exists in code")
    
    def test_verify_host_only_checks(self):
        """Verify mute controls are host-only"""
        from pathlib import Path
        
        signaling_file = Path("/app/backend/services/karau_meet/webrtc_signaling.py")
        content = signaling_file.read_text()
        
        # All mute controls should check is_host
        assert 'and is_host' in content, "is_host check not found for mute controls"
        print("SUCCESS: Host-only checks exist for mute controls")


class TestFrontendComponents:
    """Tests to verify frontend components have required elements"""
    
    def test_meeting_panels_has_mute_all_button(self):
        """Verify ParticipantsPanel has Mute All button"""
        from pathlib import Path
        
        panels_file = Path("/app/frontend/src/components/KarauMeet/MeetingPanels.jsx")
        content = panels_file.read_text()
        
        assert 'data-testid="mute-all-btn"' in content, "Mute All button data-testid not found"
        assert 'onMuteAll' in content, "onMuteAll prop not found"
        print("SUCCESS: ParticipantsPanel has Mute All button with data-testid")
    
    def test_meeting_panels_has_mute_participant(self):
        """Verify ParticipantsPanel has mute participant dropdown"""
        from pathlib import Path
        
        panels_file = Path("/app/frontend/src/components/KarauMeet/MeetingPanels.jsx")
        content = panels_file.read_text()
        
        assert 'data-testid={`mute-participant-' in content, "Mute participant data-testid not found"
        assert 'onMuteParticipant' in content, "onMuteParticipant prop not found"
        print("SUCCESS: ParticipantsPanel has mute participant dropdown")
    
    def test_meeting_panels_has_pass_mic(self):
        """Verify ParticipantsPanel has pass mic option"""
        from pathlib import Path
        
        panels_file = Path("/app/frontend/src/components/KarauMeet/MeetingPanels.jsx")
        content = panels_file.read_text()
        
        assert 'data-testid={`pass-mic-' in content, "Pass mic data-testid not found"
        assert 'onPassMic' in content, "onPassMic prop not found"
        print("SUCCESS: ParticipantsPanel has pass mic option")
    
    def test_participant_grid_has_active_speaker_prop(self):
        """Verify ParticipantGrid passes activeSpeakerId"""
        from pathlib import Path
        
        grid_file = Path("/app/frontend/src/components/KarauMeet/ParticipantGrid.jsx")
        content = grid_file.read_text()
        
        assert 'activeSpeakerId' in content, "activeSpeakerId prop not found"
        assert 'isSpeaking' in content, "isSpeaking prop not found"
        print("SUCCESS: ParticipantGrid has activeSpeakerId prop")
    
    def test_video_participant_has_speaking_styles(self):
        """Verify VideoParticipant shows emerald ring when speaking"""
        from pathlib import Path
        
        grid_file = Path("/app/frontend/src/components/KarauMeet/ParticipantGrid.jsx")
        content = grid_file.read_text()
        
        assert 'ring-emerald-500' in content, "Emerald ring class not found"
        assert 'shadow-emerald' in content or 'shadow-lg shadow-emerald' in content, "Emerald shadow not found"
        print("SUCCESS: VideoParticipant has emerald ring/shadow for active speaker")
    
    def test_meeting_room_has_force_mute_handler(self):
        """Verify MeetingRoom handles force_mute host_action"""
        from pathlib import Path
        
        room_file = Path("/app/frontend/src/components/KarauMeet/MeetingRoom.jsx")
        content = room_file.read_text()
        
        assert "action === 'force_mute'" in content or 'action === "force_mute"' in content, "force_mute handler not found"
        print("SUCCESS: MeetingRoom handles force_mute host_action")
    
    def test_meeting_room_has_pass_mic_handler(self):
        """Verify MeetingRoom handles pass_mic host_action"""
        from pathlib import Path
        
        room_file = Path("/app/frontend/src/components/KarauMeet/MeetingRoom.jsx")
        content = room_file.read_text()
        
        assert "action === 'pass_mic'" in content or 'action === "pass_mic"' in content, "pass_mic handler not found"
        print("SUCCESS: MeetingRoom handles pass_mic host_action")
    
    def test_meeting_room_has_mute_functions(self):
        """Verify MeetingRoom has muteAll, muteParticipant, passMic functions"""
        from pathlib import Path
        
        room_file = Path("/app/frontend/src/components/KarauMeet/MeetingRoom.jsx")
        content = room_file.read_text()
        
        assert 'const muteAll' in content, "muteAll function not found"
        assert 'const muteParticipant' in content, "muteParticipant function not found"
        assert 'const passMic' in content, "passMic function not found"
        print("SUCCESS: MeetingRoom has muteAll, muteParticipant, passMic functions")
    
    def test_meeting_room_has_active_speaker_state(self):
        """Verify MeetingRoom has activeSpeakerId state"""
        from pathlib import Path
        
        room_file = Path("/app/frontend/src/components/KarauMeet/MeetingRoom.jsx")
        content = room_file.read_text()
        
        assert 'activeSpeakerId' in content, "activeSpeakerId state not found"
        assert 'setActiveSpeakerId' in content, "setActiveSpeakerId not found"
        print("SUCCESS: MeetingRoom has activeSpeakerId state")
    
    def test_meeting_lobby_renders(self):
        """Verify MeetingLobby component exists"""
        from pathlib import Path
        
        lobby_file = Path("/app/frontend/src/components/KarauMeet/MeetingLobby.jsx")
        assert lobby_file.exists(), "MeetingLobby.jsx not found"
        
        content = lobby_file.read_text()
        assert 'data-testid="meeting-lobby"' in content, "meeting-lobby data-testid not found"
        assert 'data-testid="lobby-join-btn"' in content, "Join button data-testid not found"
        print("SUCCESS: MeetingLobby component exists with proper data-testids")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
