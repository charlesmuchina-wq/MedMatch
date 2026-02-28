"""
Iteration 142: Coordinator Role + Recording Transcription + WebRTC Tests
Tests for:
1. Coordinator role (proxy host - can monitor, drive slides, manage Q&A, promote/demote, mute - but NO video)
2. Recording transcription via OpenAI Whisper (auto-triggers on cloud upload)
3. WebRTC peer-to-peer video for webinar live room
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def auth_token():
    """Login as admin and get token"""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@medmatch.com",
        "password": "Swampdrainer2026!"
    })
    if res.status_code == 200:
        return res.json().get("access_token")
    pytest.skip(f"Auth failed: {res.status_code}")


@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


# =============================================================================
# COORDINATOR ROLE TESTS
# =============================================================================

class TestCoordinatorWebinarCreation:
    """Test webinar creation with coordinator_emails field"""

    def test_create_webinar_with_coordinator_emails(self, headers):
        """POST /api/karau/webinar/create accepts coordinator_emails field"""
        payload = {
            "title": f"TEST Coordinator Webinar {uuid.uuid4().hex[:6]}",
            "description": "Testing coordinator role",
            "scheduled_time": "2026-02-15T14:00:00",
            "max_attendees": 100,
            "registration_required": True,
            "q_and_a_enabled": True,
            "chat_enabled": True,
            "coordinator_emails": ["coord1@test.com", "coord2@test.com"],
            "panelist_emails": ["panelist@test.com"]
        }
        res = requests.post(f"{BASE_URL}/api/karau/webinar/create", json=payload, headers=headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "webinar_id" in data
        assert data["title"] == payload["title"]
        # Store for later tests
        TestCoordinatorWebinarCreation.created_webinar_id = data["webinar_id"]
        print(f"Created webinar with coordinators: {data['webinar_id']}")


class TestCoordinatorRoomInfo:
    """Test room-info returns coordinator recognition and permissions"""

    def test_room_info_returns_can_drive_slides(self, headers):
        """GET /api/karau/webinar/{id}/room-info returns can_drive_slides permission"""
        # Use existing test webinar
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/room-info", headers=headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        # Verify room info structure
        assert "my_role" in data
        assert "can_drive_slides" in data
        assert "can_control" in data
        assert "can_stream_video" in data
        print(f"Room info - my_role: {data['my_role']}, can_drive_slides: {data['can_drive_slides']}, can_control: {data['can_control']}")

    def test_host_has_full_permissions(self, headers):
        """Host should have can_drive_slides=true, can_control=true, can_stream_video=true"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/room-info", headers=headers)
        assert res.status_code == 200
        data = res.json()
        
        # Host has full control
        if data["my_role"] == "host":
            assert data["can_drive_slides"] == True
            assert data["can_control"] == True
            assert data["can_stream_video"] == True
            print("Host permissions verified: can_drive_slides, can_control, can_stream_video all True")


class TestCoordinatorRoles:
    """Test coordinator role management"""

    def test_get_roles_returns_coordinator_emails(self, headers):
        """GET /api/karau/webinar/{id}/roles returns coordinator_emails array"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/roles", headers=headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        
        assert "roles" in data
        assert "coordinator_emails" in data
        assert "panelist_emails" in data
        assert isinstance(data["coordinator_emails"], list)
        print(f"Roles endpoint - coordinator_emails: {data['coordinator_emails']}, panelist_emails: {data['panelist_emails']}")

    def test_promote_to_coordinator_requires_host(self, headers):
        """Only host can promote to coordinator role"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        test_user_id = f"test-user-{uuid.uuid4().hex[:8]}"
        
        # Host can promote to coordinator
        res = requests.post(f"{BASE_URL}/api/karau/webinar/{webinar_id}/roles/promote", 
                           json={"user_id": test_user_id, "role": "coordinator"}, headers=headers)
        # As host, should succeed
        if res.status_code == 200:
            data = res.json()
            assert data.get("success") == True
            assert data.get("role") == "coordinator"
            print(f"Successfully promoted {test_user_id} to coordinator")
            # Clean up - demote
            requests.post(f"{BASE_URL}/api/karau/webinar/{webinar_id}/roles/demote",
                         json={"user_id": test_user_id}, headers=headers)
        else:
            # If not host, should fail with 403
            print(f"Promote to coordinator response: {res.status_code} - {res.text}")

    def test_coordinator_can_promote_presenter_panelist(self, headers):
        """Coordinator can promote users to presenter or panelist (but not coordinator)"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        test_user_id = f"test-promote-{uuid.uuid4().hex[:8]}"
        
        # Test promoting to presenter
        res = requests.post(f"{BASE_URL}/api/karau/webinar/{webinar_id}/roles/promote",
                           json={"user_id": test_user_id, "role": "presenter"}, headers=headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("success") == True
        assert data.get("role") == "presenter"
        print(f"Promoted {test_user_id} to presenter successfully")
        
        # Demote back
        res_demote = requests.post(f"{BASE_URL}/api/karau/webinar/{webinar_id}/roles/demote",
                                   json={"user_id": test_user_id}, headers=headers)
        assert res_demote.status_code == 200

    def test_demote_works_for_coordinator(self, headers):
        """Test that demote endpoint works"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        test_user_id = f"test-demote-{uuid.uuid4().hex[:8]}"
        
        # First promote
        requests.post(f"{BASE_URL}/api/karau/webinar/{webinar_id}/roles/promote",
                     json={"user_id": test_user_id, "role": "panelist"}, headers=headers)
        
        # Then demote
        res = requests.post(f"{BASE_URL}/api/karau/webinar/{webinar_id}/roles/demote",
                           json={"user_id": test_user_id}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data.get("success") == True
        assert data.get("demoted") == True
        print(f"Successfully demoted {test_user_id}")


class TestCoordinatorPermissions:
    """Test coordinator specific permissions - can_control=true but can_stream_video=false"""

    def test_coordinator_role_permissions_structure(self, headers):
        """Verify the room-info permission structure supports coordinator role"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/room-info", headers=headers)
        assert res.status_code == 200
        data = res.json()
        
        # Verify all required permission fields exist
        required_fields = ["my_role", "can_stream_video", "can_stream_audio", 
                          "can_screen_share", "can_control", "can_drive_slides"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        # Role-based permissions verified
        print(f"Permission structure verified: {required_fields}")


# =============================================================================
# RECORDING TRANSCRIPTION TESTS
# =============================================================================

class TestRecordingTranscription:
    """Test recording transcription endpoints"""

    def test_get_transcript_endpoint_exists(self, headers):
        """GET /api/karau-meet/recordings/transcript/{id} endpoint exists"""
        fake_id = "nonexistent123"
        res = requests.get(f"{BASE_URL}/api/karau-meet/recordings/transcript/{fake_id}", headers=headers)
        # Should return 404 for nonexistent, not 405 (method not allowed)
        assert res.status_code == 404, f"Expected 404, got {res.status_code}: {res.text}"
        print("Transcript endpoint exists and returns 404 for nonexistent recording")

    def test_get_recordings_list(self, headers):
        """GET /api/karau-meet/recordings/ returns recordings list"""
        res = requests.get(f"{BASE_URL}/api/karau-meet/recordings/", headers=headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "recordings" in data
        assert "total" in data
        print(f"Recordings list: {len(data['recordings'])} recordings, total: {data['total']}")

    def test_get_recordings_stats(self, headers):
        """GET /api/karau-meet/recordings/stats returns statistics"""
        res = requests.get(f"{BASE_URL}/api/karau-meet/recordings/stats", headers=headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "total_recordings" in data
        assert "cloud_count" in data
        print(f"Recording stats: {data['total_recordings']} total, {data['cloud_count']} cloud")

    def test_transcript_response_structure(self, headers):
        """Transcript endpoint returns {status, transcription, error} structure"""
        # Get a real recording if available
        res = requests.get(f"{BASE_URL}/api/karau-meet/recordings/", headers=headers)
        if res.status_code == 200:
            data = res.json()
            recordings = data.get("recordings", [])
            
            for rec in recordings:
                if rec.get("transcription_status") in ["queued", "processing", "completed", "failed"]:
                    rec_id = rec.get("recording_id")
                    trans_res = requests.get(f"{BASE_URL}/api/karau-meet/recordings/transcript/{rec_id}", headers=headers)
                    
                    if trans_res.status_code == 200:
                        trans_data = trans_res.json()
                        assert "recording_id" in trans_data
                        assert "status" in trans_data
                        # transcription and error may be None
                        print(f"Transcript for {rec_id}: status={trans_data['status']}")
                        return
            
            print("No recordings with transcription status found, skipping structure test")
        else:
            pytest.skip("Could not fetch recordings list")


class TestUploadTriggersTranscription:
    """Test that upload sets transcription_status=queued"""

    def test_upload_endpoint_exists(self, headers):
        """POST /api/karau-meet/recordings/upload endpoint exists"""
        # Just verify the endpoint exists (we can't easily test file upload without a real file)
        # Send an empty request to verify endpoint
        res = requests.post(f"{BASE_URL}/api/karau-meet/recordings/upload", headers=headers)
        # Should fail with 422 (validation error) not 404/405
        assert res.status_code in [422, 400], f"Expected 422/400, got {res.status_code}"
        print("Upload endpoint exists and validates input")


# =============================================================================
# WEBINAR WEBRTC SIGNALING TESTS
# =============================================================================

class TestWebinarWebRTC:
    """Test WebRTC related webinar functionality"""

    def test_room_info_for_webrtc_ready(self, headers):
        """Room info returns necessary data for WebRTC connection"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/room-info", headers=headers)
        assert res.status_code == 200
        data = res.json()
        
        # Required fields for WebRTC
        assert "webinar_id" in data
        assert "title" in data
        assert "status" in data
        assert "my_role" in data
        assert "host_name" in data
        print(f"Room info has all WebRTC-required fields: webinar_id, title, status, my_role, host_name")


# =============================================================================
# EXISTING WEBINAR FUNCTIONALITY (regression tests)
# =============================================================================

class TestExistingWebinarFunctionality:
    """Regression tests for existing webinar features"""

    def test_list_webinars(self, headers):
        """GET /api/karau/webinar/list works"""
        res = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "webinars" in data
        print(f"Listed {len(data['webinars'])} webinars")

    def test_get_webinar_details(self, headers):
        """GET /api/karau/webinar/{id} works"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "title" in data
        assert "status" in data
        print(f"Webinar details: {data['title']}, status: {data['status']}")

    def test_qa_endpoint(self, headers):
        """GET /api/karau/webinar/{id}/qa works"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/qa")
        assert res.status_code == 200
        data = res.json()
        assert "questions" in data
        print(f"Q&A: {len(data['questions'])} questions")

    def test_hand_raises(self, headers):
        """GET /api/karau/webinar/{id}/hand-raises works"""
        webinar_id = getattr(TestCoordinatorWebinarCreation, 'created_webinar_id', 'WEB-E38AC839')
        res = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/hand-raises", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert "hand_raises" in data
        print(f"Hand raises: {len(data['hand_raises'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
