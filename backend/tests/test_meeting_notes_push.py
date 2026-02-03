"""
Test Meeting Notes and Push Notification Features
Tests: Meeting Notes CRUD, AI Summary, Export, Push Service Integration
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "MedMatch2026!"


class TestMeetingNotesAPI:
    """Meeting Notes API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping authenticated tests")
        
        self.user = login_response.json()
        yield
    
    def test_meeting_notes_status(self):
        """Test GET /api/meeting-notes/status returns service status"""
        response = self.session.get(f"{BASE_URL}/api/meeting-notes/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "available" in data, "Response should contain 'available' field"
        assert data["available"] == True, "Service should be available"
        assert "features" in data, "Response should contain 'features' field"
        
        features = data["features"]
        assert features.get("transcription") == True, "Transcription should be enabled"
        assert features.get("summarization") == True, "Summarization should be enabled"
        assert features.get("action_items") == True, "Action items should be enabled"
        
        print(f"✅ Meeting notes status: available={data['available']}, features={features}")
    
    def test_create_meeting(self):
        """Test POST /api/meeting-notes/create creates a new meeting"""
        meeting_data = {
            "title": "TEST_Interview with Acme Corp",
            "meeting_type": "interview",
            "company": "Acme Corp",
            "position": "Software Engineer"
        }
        
        response = self.session.post(
            f"{BASE_URL}/api/meeting-notes/create",
            json=meeting_data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "meeting" in data, "Response should contain 'meeting' field"
        
        meeting = data["meeting"]
        assert meeting["title"] == meeting_data["title"], "Title should match"
        assert meeting["meeting_type"] == meeting_data["meeting_type"], "Meeting type should match"
        assert meeting["company"] == meeting_data["company"], "Company should match"
        assert meeting["status"] == "draft", "Initial status should be 'draft'"
        assert "id" in meeting, "Meeting should have an ID"
        
        # Store meeting ID for cleanup
        self.created_meeting_id = meeting["id"]
        
        print(f"✅ Created meeting: {meeting['id']} - {meeting['title']}")
        
        return meeting["id"]
    
    def test_list_meetings(self):
        """Test GET /api/meeting-notes/list returns user's meetings"""
        response = self.session.get(f"{BASE_URL}/api/meeting-notes/list")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "meetings" in data, "Response should contain 'meetings' field"
        assert "total" in data, "Response should contain 'total' field"
        assert isinstance(data["meetings"], list), "Meetings should be a list"
        
        print(f"✅ Listed {data['total']} meetings")
    
    def test_get_meeting_details(self):
        """Test GET /api/meeting-notes/{id} returns meeting details"""
        # First create a meeting
        meeting_id = self.test_create_meeting()
        
        response = self.session.get(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["id"] == meeting_id, "Meeting ID should match"
        assert "title" in data, "Response should contain 'title'"
        assert "status" in data, "Response should contain 'status'"
        
        print(f"✅ Got meeting details: {data['title']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
    
    def test_update_meeting(self):
        """Test PUT /api/meeting-notes/{id} updates meeting"""
        # First create a meeting
        meeting_id = self.test_create_meeting()
        
        update_data = {
            "title": "TEST_Updated Interview Title",
            "status": "recording"
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/meeting-notes/{meeting_id}",
            json=update_data
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify update
        get_response = self.session.get(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
        updated_meeting = get_response.json()
        
        assert updated_meeting["title"] == update_data["title"], "Title should be updated"
        assert updated_meeting["status"] == update_data["status"], "Status should be updated"
        
        print(f"✅ Updated meeting: {updated_meeting['title']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
    
    def test_delete_meeting(self):
        """Test DELETE /api/meeting-notes/{id} deletes meeting"""
        # First create a meeting
        meeting_id = self.test_create_meeting()
        
        response = self.session.delete(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify deletion
        get_response = self.session.get(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
        assert get_response.status_code == 404, "Meeting should not exist after deletion"
        
        print(f"✅ Deleted meeting: {meeting_id}")
    
    def test_meeting_stats(self):
        """Test GET /api/meeting-notes/stats/overview returns statistics"""
        response = self.session.get(f"{BASE_URL}/api/meeting-notes/stats/overview")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total_meetings" in data, "Response should contain 'total_meetings'"
        assert "completed_meetings" in data, "Response should contain 'completed_meetings'"
        assert "total_words_transcribed" in data, "Response should contain 'total_words_transcribed'"
        assert "meetings_by_type" in data, "Response should contain 'meetings_by_type'"
        
        print(f"✅ Meeting stats: total={data['total_meetings']}, completed={data['completed_meetings']}")
    
    def test_export_meeting_markdown(self):
        """Test GET /api/meeting-notes/{id}/export exports in markdown format"""
        # First create a meeting with some content
        meeting_id = self.test_create_meeting()
        
        response = self.session.get(
            f"{BASE_URL}/api/meeting-notes/{meeting_id}/export",
            params={"format": "markdown"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["format"] == "markdown", "Format should be markdown"
        assert "content" in data, "Response should contain 'content'"
        assert "filename" in data, "Response should contain 'filename'"
        assert data["filename"].endswith(".md"), "Filename should end with .md"
        
        print(f"✅ Exported meeting as markdown: {data['filename']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
    
    def test_export_meeting_json(self):
        """Test GET /api/meeting-notes/{id}/export exports in JSON format"""
        # First create a meeting
        meeting_id = self.test_create_meeting()
        
        response = self.session.get(
            f"{BASE_URL}/api/meeting-notes/{meeting_id}/export",
            params={"format": "json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data["format"] == "json", "Format should be json"
        assert "content" in data, "Response should contain 'content'"
        assert "filename" in data, "Response should contain 'filename'"
        assert data["filename"].endswith(".json"), "Filename should end with .json"
        
        print(f"✅ Exported meeting as JSON: {data['filename']}")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
    
    def test_generate_summary_requires_transcript(self):
        """Test POST /api/meeting-notes/{id}/generate-summary requires transcript"""
        # Create a meeting without transcript
        meeting_id = self.test_create_meeting()
        
        response = self.session.post(f"{BASE_URL}/api/meeting-notes/{meeting_id}/generate-summary")
        
        # Should fail because no transcript
        assert response.status_code == 400, f"Expected 400 (no transcript), got {response.status_code}"
        
        print("✅ Generate summary correctly requires transcript")
        
        # Cleanup
        self.session.delete(f"{BASE_URL}/api/meeting-notes/{meeting_id}")
    
    def test_meeting_notes_auth_required(self):
        """Test that meeting notes endpoints require authentication"""
        # Create a new session without auth
        unauth_session = requests.Session()
        
        response = unauth_session.get(f"{BASE_URL}/api/meeting-notes/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        response = unauth_session.get(f"{BASE_URL}/api/meeting-notes/list")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        print("✅ Meeting notes endpoints require authentication")


class TestWebPushAPI:
    """Web Push Notification API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping authenticated tests")
        
        self.user = login_response.json()
        yield
    
    def test_vapid_public_key(self):
        """Test GET /api/webpush/vapid-public-key returns VAPID key"""
        response = self.session.get(f"{BASE_URL}/api/webpush/vapid-public-key")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "publicKey" in data, "Response should contain 'publicKey'"
        assert data["configured"] == True, "Push should be configured"
        assert len(data["publicKey"]) > 20, "Public key should be a valid length"
        
        print(f"✅ VAPID public key available: {data['publicKey'][:30]}...")
    
    def test_push_status(self):
        """Test GET /api/webpush/status returns push status"""
        response = self.session.get(f"{BASE_URL}/api/webpush/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "configured" in data, "Response should contain 'configured'"
        assert "active_subscriptions" in data, "Response should contain 'active_subscriptions'"
        
        print(f"✅ Push status: configured={data['configured']}, subscriptions={data['active_subscriptions']}")
    
    def test_job_match_notification_endpoint(self):
        """Test POST /api/webpush/notify/job-match endpoint exists"""
        # This will fail to send (no subscription) but should return proper response
        response = self.session.post(
            f"{BASE_URL}/api/webpush/notify/job-match",
            json={
                "job_title": "Test Software Engineer",
                "company": "Test Company",
                "match_score": 85,
                "job_id": "test_job_123"
            }
        )
        
        # Should return 200 even if no subscriptions (graceful handling)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Will show no subscriptions but endpoint works
        assert "success" in data or "sent" in data, "Response should indicate result"
        
        print(f"✅ Job match notification endpoint works: {data}")
    
    def test_interview_reminder_notification_endpoint(self):
        """Test POST /api/webpush/notify/interview-reminder endpoint"""
        response = self.session.post(
            f"{BASE_URL}/api/webpush/notify/interview-reminder",
            json={
                "company": "Test Company",
                "position": "Software Engineer",
                "time": "Tomorrow at 2:00 PM"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        print("✅ Interview reminder notification endpoint works")
    
    def test_application_update_notification_endpoint(self):
        """Test POST /api/webpush/notify/application-update endpoint"""
        response = self.session.post(
            f"{BASE_URL}/api/webpush/notify/application-update",
            json={
                "company": "Test Company",
                "status": "shortlisted"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        print("✅ Application update notification endpoint works")
    
    def test_message_notification_endpoint(self):
        """Test POST /api/webpush/notify/message endpoint"""
        response = self.session.post(
            f"{BASE_URL}/api/webpush/notify/message",
            json={
                "sender_name": "Test Recruiter",
                "preview": "Hi, I saw your profile and wanted to reach out..."
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        print("✅ Message notification endpoint works")
    
    def test_webpush_auth_required(self):
        """Test that webpush endpoints require authentication"""
        unauth_session = requests.Session()
        
        response = unauth_session.get(f"{BASE_URL}/api/webpush/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        response = unauth_session.post(
            f"{BASE_URL}/api/webpush/notify/job-match",
            json={"job_title": "Test", "company": "Test", "match_score": 80}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        print("✅ Webpush endpoints require authentication")


class TestPushServiceIntegration:
    """Test Push Service utility integration with messages and recruiter routes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping authenticated tests")
        
        self.user = login_response.json()
        yield
    
    def test_messages_route_exists(self):
        """Test that messages route is accessible"""
        response = self.session.get(f"{BASE_URL}/api/messages/conversations")
        
        # Should return 200 (empty list is fine)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        print("✅ Messages route accessible")
    
    def test_messages_unread_count(self):
        """Test GET /api/messages/unread-count endpoint"""
        response = self.session.get(f"{BASE_URL}/api/messages/unread-count")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "unread_count" in data, "Response should contain 'unread_count'"
        
        print(f"✅ Unread count: {data['unread_count']}")


class TestPayPalDocumentation:
    """Test PayPal integration documentation exists"""
    
    def test_paypal_doc_exists(self):
        """Test that PayPal integration documentation exists"""
        doc_path = "/app/docs/PAYPAL_INTEGRATION.md"
        assert os.path.exists(doc_path), f"PayPal documentation should exist at {doc_path}"
        
        with open(doc_path, 'r') as f:
            content = f.read()
        
        # Check for key sections
        assert "PayPal" in content, "Doc should mention PayPal"
        assert "PAYPAL_CLIENT_ID" in content, "Doc should mention client ID"
        assert "webhook" in content.lower(), "Doc should mention webhooks"
        assert "sandbox" in content.lower(), "Doc should mention sandbox testing"
        
        print("✅ PayPal integration documentation exists and contains required sections")


class TestNavigationMeetingNotes:
    """Test that Meeting Notes appears in navigation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        
        if login_response.status_code != 200:
            pytest.skip("Authentication failed - skipping authenticated tests")
        
        yield
    
    def test_meeting_notes_route_registered(self):
        """Test that meeting-notes route is registered in backend"""
        # Test the status endpoint to confirm route is registered
        response = self.session.get(f"{BASE_URL}/api/meeting-notes/status")
        
        # Should not be 404 (route not found)
        assert response.status_code != 404, "Meeting notes route should be registered"
        
        print("✅ Meeting notes route is registered in backend")


# Cleanup function to remove test data
def cleanup_test_meetings():
    """Remove all TEST_ prefixed meetings"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    
    login_response = session.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if login_response.status_code == 200:
        list_response = session.get(f"{BASE_URL}/api/meeting-notes/list")
        if list_response.status_code == 200:
            meetings = list_response.json().get("meetings", [])
            for meeting in meetings:
                if meeting.get("title", "").startswith("TEST_"):
                    session.delete(f"{BASE_URL}/api/meeting-notes/{meeting['id']}")
                    print(f"Cleaned up: {meeting['id']}")


if __name__ == "__main__":
    # Run cleanup first
    cleanup_test_meetings()
    
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
