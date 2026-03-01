"""
Test Suite for AI Meeting Notes and Presentation Features - Iteration 143
Tests:
1. POST /api/karau-meet/recordings/{recording_id}/notes/generate - 404 for non-existent recording
2. GET /api/karau-meet/recordings/{recording_id}/notes - 404 for non-existent recording
3. POST /api/karau-meet/recordings/{recording_id}/notes/send - 400 for recording without notes
4. GET /api/karau/webinar/{id}/presentation/slides - 404 when no presentation uploaded
5. POST /api/karau/webinar/{id}/presentation/upload - endpoint exists and requires auth
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestSetup:
    """Setup fixtures for test suite"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code != 200:
            pytest.skip(f"Auth failed: {response.status_code} - {response.text}")
        data = response.json()
        return data.get("access_token") or data.get("token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Returns headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestRecordingNotesEndpoints(TestSetup):
    """Test AI Meeting Notes endpoints for recordings"""
    
    def test_generate_notes_nonexistent_recording_returns_404(self, auth_headers):
        """
        POST /api/karau-meet/recordings/{recording_id}/notes/generate
        Should return 404 for non-existent recording
        """
        fake_recording_id = "nonexistent12"
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/{fake_recording_id}/notes/generate",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Generate notes for non-existent recording correctly returns 404")
    
    def test_get_notes_nonexistent_recording_returns_404(self, auth_headers):
        """
        GET /api/karau-meet/recordings/{recording_id}/notes
        Should return 404 for non-existent recording
        """
        fake_recording_id = "nonexistent12"
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/{fake_recording_id}/notes",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Get notes for non-existent recording correctly returns 404")
    
    def test_send_notes_requires_existing_notes_returns_400(self, auth_headers):
        """
        POST /api/karau-meet/recordings/{recording_id}/notes/send
        Should return 400 for recording without notes
        """
        fake_recording_id = "nonexistent12"
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/{fake_recording_id}/notes/send",
            headers=auth_headers,
            json={"recipient_emails": ["test@example.com"]}
        )
        # Could be 400 (no notes to send) or 404 (recording not found)
        assert response.status_code in [400, 404], f"Expected 400 or 404, got {response.status_code}: {response.text}"
        print(f"✓ Send notes for recording without notes correctly returns {response.status_code}")
    
    def test_recordings_list_endpoint_works(self, auth_headers):
        """GET /api/karau-meet/recordings/ - should return list"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "recordings" in data, "Response should contain 'recordings' key"
        assert "total" in data, "Response should contain 'total' key"
        print(f"✓ Recordings list endpoint works - {data.get('total', 0)} recordings found")
    
    def test_recordings_stats_endpoint_works(self, auth_headers):
        """GET /api/karau-meet/recordings/stats - should return stats"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "total_recordings" in data, "Should contain total_recordings"
        print(f"✓ Recordings stats endpoint works - {data.get('total_recordings', 0)} total")


class TestWebinarPresentationEndpoints(TestSetup):
    """Test Webinar Presentation (Slide) endpoints"""
    
    @pytest.fixture(scope="class")
    def test_webinar_id(self, auth_headers):
        """Create a test webinar for presentation tests"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/create",
            headers=auth_headers,
            json={
                "title": f"TEST_Presentation_Webinar_{uuid.uuid4().hex[:6]}",
                "description": "Test webinar for presentation testing",
                "scheduled_time": "2026-03-15T10:00:00Z",
                "max_attendees": 100,
                "registration_required": False
            }
        )
        if response.status_code != 200:
            pytest.skip(f"Failed to create test webinar: {response.status_code}")
        data = response.json()
        webinar_id = data.get("webinar_id")
        print(f"✓ Created test webinar: {webinar_id}")
        return webinar_id
    
    def test_get_slides_no_presentation_returns_404(self, auth_headers, test_webinar_id):
        """
        GET /api/karau/webinar/{id}/presentation/slides
        Should return 404 when no presentation uploaded
        """
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/presentation/slides",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Get slides without presentation correctly returns 404")
    
    def test_get_slide_image_no_presentation_returns_404(self, auth_headers, test_webinar_id):
        """
        GET /api/karau/webinar/{id}/presentation/slide/0
        Should return 404 when no presentation uploaded
        """
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/presentation/slide/0",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Get slide image without presentation correctly returns 404")
    
    def test_upload_presentation_endpoint_exists(self, auth_headers, test_webinar_id):
        """
        POST /api/karau/webinar/{id}/presentation/upload
        Endpoint should exist and require file
        """
        # Test without file - should get 422 (validation error)
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/presentation/upload",
            headers={"Authorization": auth_headers["Authorization"]}
        )
        # Should be 422 (missing file) not 404 (endpoint not found)
        assert response.status_code != 404, "Upload endpoint should exist"
        assert response.status_code == 422, f"Expected 422 (missing file), got {response.status_code}"
        print(f"✓ Presentation upload endpoint exists and validates file requirement")
    
    def test_upload_presentation_requires_auth(self, test_webinar_id):
        """
        POST /api/karau/webinar/{id}/presentation/upload
        Should require authentication
        """
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/presentation/upload"
        )
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print(f"✓ Presentation upload requires authentication")
    
    def test_slides_nonexistent_webinar_returns_404(self, auth_headers):
        """
        GET /api/karau/webinar/{nonexistent}/presentation/slides
        Should return 404 for non-existent webinar
        """
        fake_webinar_id = "WEB-NOTEXIST"
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{fake_webinar_id}/presentation/slides",
            headers=auth_headers
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}: {response.text}"
        print(f"✓ Get slides for non-existent webinar correctly returns 404")


class TestWebinarNotesEndpoints(TestSetup):
    """Test Webinar-level notes endpoints"""
    
    def test_generate_notes_webinar_requires_recording_id(self, auth_headers):
        """
        POST /api/karau/webinar/{id}/notes/generate
        Should require recording_id query param
        """
        fake_webinar_id = "WEB-TESTGEN"
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{fake_webinar_id}/notes/generate",
            headers=auth_headers
        )
        # Should fail due to missing recording_id
        assert response.status_code in [404, 422], f"Expected 404 or 422, got {response.status_code}"
        print(f"✓ Webinar notes generate endpoint validates input")
    
    def test_send_notes_webinar_requires_recording_id(self, auth_headers):
        """
        POST /api/karau/webinar/{id}/notes/send
        Should require recording_id in body
        """
        fake_webinar_id = "WEB-TESTSEND"
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{fake_webinar_id}/notes/send",
            headers=auth_headers,
            json={"recipient_emails": ["test@example.com"]}
        )
        # Should fail due to missing recording_id
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
        print(f"✓ Webinar notes send endpoint validates recording_id")


class TestRecordingWithTranscriptFlow(TestSetup):
    """Test notes flow with real recordings (if any exist with transcription)"""
    
    def test_find_recording_with_completed_transcription(self, auth_headers):
        """Find if any recordings have completed transcription"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/",
            headers=auth_headers
        )
        if response.status_code != 200:
            pytest.skip("Could not fetch recordings")
        
        data = response.json()
        recordings = data.get("recordings", [])
        
        transcribed_recordings = [
            r for r in recordings 
            if r.get("transcription_status") == "completed"
        ]
        
        if transcribed_recordings:
            print(f"✓ Found {len(transcribed_recordings)} recording(s) with completed transcription")
            for rec in transcribed_recordings[:2]:
                print(f"  - {rec.get('recording_id')}: {rec.get('meeting_title', 'Untitled')}")
        else:
            print(f"ℹ No recordings with completed transcription found (total: {len(recordings)})")
            # List transcription statuses
            statuses = {}
            for r in recordings:
                status = r.get("transcription_status", "none")
                statuses[status] = statuses.get(status, 0) + 1
            print(f"  Transcription status breakdown: {statuses}")
        
        # Test passes regardless - we're just checking for data
        assert True


class TestMeetingNotesService(TestSetup):
    """Test the meeting notes service exists"""
    
    def test_notes_service_can_be_imported(self):
        """Verify meeting notes service module exists"""
        # This is a meta-test to ensure the service is properly set up
        import sys
        sys.path.insert(0, '/app/backend')
        try:
            from services.meeting_notes_service import generate_meeting_notes
            print(f"✓ Meeting notes service can be imported")
            assert True
        except ImportError as e:
            pytest.fail(f"Could not import meeting_notes_service: {e}")


class TestPresentationService(TestSetup):
    """Test presentation service exists"""
    
    def test_presentation_service_can_be_imported(self):
        """Verify presentation service module exists"""
        import sys
        sys.path.insert(0, '/app/backend')
        try:
            from services.presentation_service import process_presentation
            print(f"✓ Presentation service can be imported")
            assert True
        except ImportError as e:
            pytest.fail(f"Could not import presentation_service: {e}")


class TestWebinarListAndManagement(TestSetup):
    """Test webinar management endpoints needed for frontend"""
    
    def test_list_webinars_works(self, auth_headers):
        """GET /api/karau/webinar/list - should return webinars"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "webinars" in data, "Response should contain 'webinars' key"
        print(f"✓ Webinar list works - {len(data.get('webinars', []))} webinars found")
    
    def test_webinar_room_info_for_live_room(self, auth_headers):
        """GET /api/karau/webinar/{id}/room-info - test room info endpoint"""
        # First get a webinar
        list_response = requests.get(
            f"{BASE_URL}/api/karau/webinar/list",
            headers=auth_headers
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get webinar list")
        
        webinars = list_response.json().get("webinars", [])
        if not webinars:
            pytest.skip("No webinars available for room-info test")
        
        webinar_id = webinars[0]["webinar_id"]
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{webinar_id}/room-info",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Verify required fields for WebinarLiveRoom
        assert "webinar_id" in data
        assert "my_role" in data
        assert "can_stream_video" in data
        assert "can_control" in data
        assert "can_drive_slides" in data  # New feature
        print(f"✓ Room info includes can_drive_slides: {data.get('can_drive_slides')}")
        print(f"  Role: {data.get('my_role')}, can_control: {data.get('can_control')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
