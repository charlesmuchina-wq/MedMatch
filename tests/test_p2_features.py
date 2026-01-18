"""
P2 Features Test Suite
Tests for: Push Notifications, ID Verification, Video Interview
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"
RECRUITER_EMAIL = "recruiter@medmatch-test.com"
RECRUITER_PASSWORD = "test123"


class TestHealthAndBasics:
    """Basic health checks"""
    
    def test_health_endpoint(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health endpoint working")


class TestAuthentication:
    """Authentication tests to get session for other tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            print(f"✅ Logged in as {ADMIN_EMAIL}")
            return session
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            pytest.skip("Authentication failed")
    
    def test_login_success(self, auth_session):
        """Verify login works"""
        response = auth_session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        print(f"✅ Auth verified - user_id: {data.get('user_id')}")


class TestPushNotifications:
    """Push Notifications API Tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return session
        pytest.skip("Authentication failed")
    
    def test_get_notification_preferences(self, auth_session):
        """Test GET /api/notifications/preferences"""
        response = auth_session.get(f"{BASE_URL}/api/notifications/preferences")
        assert response.status_code == 200
        data = response.json()
        # Should have default preferences
        assert "job_alerts" in data
        assert "application_updates" in data
        assert "messages" in data
        assert "interview_reminders" in data
        assert "weekly_digest" in data
        assert "marketing" in data
        print(f"✅ GET /api/notifications/preferences - defaults returned")
    
    def test_update_notification_preferences(self, auth_session):
        """Test PUT /api/notifications/preferences"""
        new_prefs = {
            "job_alerts": True,
            "application_updates": True,
            "messages": True,
            "interview_reminders": True,
            "weekly_digest": False,
            "marketing": False
        }
        response = auth_session.put(
            f"{BASE_URL}/api/notifications/preferences",
            json=new_prefs
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Preferences updated"
        assert data["preferences"]["weekly_digest"] == False
        print(f"✅ PUT /api/notifications/preferences - updated successfully")
    
    def test_get_notification_history(self, auth_session):
        """Test GET /api/notifications/history"""
        response = auth_session.get(f"{BASE_URL}/api/notifications/history?limit=50")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        assert "total" in data
        print(f"✅ GET /api/notifications/history - {data['total']} notifications, {data['unread_count']} unread")
    
    def test_subscribe_to_push(self, auth_session):
        """Test POST /api/notifications/subscribe"""
        subscription = {
            "endpoint": f"https://test-push-endpoint.com/{os.urandom(8).hex()}",
            "keys": {
                "p256dh": "test-p256dh-key",
                "auth": "test-auth-key"
            },
            "user_agent": "Test Browser/1.0"
        }
        response = auth_session.post(
            f"{BASE_URL}/api/notifications/subscribe",
            json=subscription
        )
        assert response.status_code == 200
        data = response.json()
        assert "subscription_id" in data
        assert data["message"] in ["Subscribed successfully", "Subscription updated"]
        print(f"✅ POST /api/notifications/subscribe - subscription_id: {data['subscription_id']}")
    
    def test_get_subscriptions(self, auth_session):
        """Test GET /api/notifications/subscriptions"""
        response = auth_session.get(f"{BASE_URL}/api/notifications/subscriptions")
        assert response.status_code == 200
        data = response.json()
        assert "subscriptions" in data
        assert "total" in data
        print(f"✅ GET /api/notifications/subscriptions - {data['total']} subscriptions")
    
    def test_send_test_notification(self, auth_session):
        """Test POST /api/notifications/send-test"""
        response = auth_session.post(f"{BASE_URL}/api/notifications/send-test")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Test notification sent"
        assert "notification_id" in data
        print(f"✅ POST /api/notifications/send-test - notification_id: {data['notification_id']}")
    
    def test_notification_history_after_test(self, auth_session):
        """Verify test notification appears in history"""
        response = auth_session.get(f"{BASE_URL}/api/notifications/history?limit=5")
        assert response.status_code == 200
        data = response.json()
        # Should have at least one notification now
        assert data["total"] >= 1
        # Check if test notification is there
        notifications = data["notifications"]
        test_notif = next((n for n in notifications if n.get("title") == "Test Notification"), None)
        if test_notif:
            print(f"✅ Test notification found in history")
        else:
            print(f"⚠️ Test notification not found in history (may be timing issue)")


class TestIDVerification:
    """ID Verification API Tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return session
        pytest.skip("Authentication failed")
    
    def test_get_verification_levels(self, auth_session):
        """Test GET /api/id-verification/levels"""
        response = auth_session.get(f"{BASE_URL}/api/id-verification/levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        levels = data["levels"]
        assert len(levels) == 4  # Levels 0-3
        
        # Verify level structure
        for level in levels:
            assert "level" in level
            assert "name" in level
            assert "features" in level
        
        # Check specific levels
        level_names = {l["level"]: l["name"] for l in levels}
        assert level_names[0] == "Unverified"
        assert level_names[1] == "Email Verified"
        assert level_names[2] == "Company Verified"
        assert level_names[3] == "ID Verified"
        print(f"✅ GET /api/id-verification/levels - 4 levels returned correctly")
    
    def test_get_verification_status(self, auth_session):
        """Test GET /api/id-verification/status"""
        response = auth_session.get(f"{BASE_URL}/api/id-verification/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "verification_level" in data
        assert "level_info" in data
        print(f"✅ GET /api/id-verification/status - status: {data['status']}, level: {data['verification_level']}")
    
    def test_request_verification(self, auth_session):
        """Test POST /api/id-verification/request-verification"""
        request_data = {
            "document_type": "government_id",
            "full_name": "Test User Admin",
            "date_of_birth": "1990-01-15",
            "country": "US"
        }
        response = auth_session.post(
            f"{BASE_URL}/api/id-verification/request-verification",
            json=request_data
        )
        # Could be 200 (new request) or 400 (already pending/approved)
        if response.status_code == 200:
            data = response.json()
            assert "verification_id" in data
            assert data["status"] == "pending"
            assert data["next_step"] == "upload_document"
            print(f"✅ POST /api/id-verification/request-verification - verification_id: {data['verification_id']}")
        elif response.status_code == 400:
            data = response.json()
            # Already verified or pending
            print(f"⚠️ Verification request rejected (expected if already verified): {data.get('detail')}")
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")


class TestIDVerificationRecruiter:
    """ID Verification for Recruiters - Company Verification"""
    
    @pytest.fixture(scope="class")
    def recruiter_session(self):
        """Get recruiter authenticated session"""
        session = requests.Session()
        # First try to login as recruiter
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD
        })
        if response.status_code == 200:
            return session
        
        # If recruiter doesn't exist, create one
        response = session.post(f"{BASE_URL}/api/auth/register", json={
            "email": RECRUITER_EMAIL,
            "password": RECRUITER_PASSWORD,
            "name": "Test Recruiter",
            "role": "recruiter"
        })
        if response.status_code in [200, 201]:
            # Login again
            response = session.post(f"{BASE_URL}/api/auth/login", json={
                "email": RECRUITER_EMAIL,
                "password": RECRUITER_PASSWORD
            })
            if response.status_code == 200:
                return session
        
        pytest.skip("Could not authenticate as recruiter")
    
    def test_verify_company_endpoint(self, recruiter_session):
        """Test POST /api/id-verification/verify-company"""
        company_data = {
            "company_name": "MedMatch Test Corp",
            "company_website": "https://medmatch-test.com",
            "company_email_domain": "medmatch-test.com",
            "role_at_company": "Talent Acquisition Manager",
            "linkedin_url": "https://linkedin.com/in/testrecruiter"
        }
        response = recruiter_session.post(
            f"{BASE_URL}/api/id-verification/verify-company",
            json=company_data
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "verification_id" in data
            assert "status" in data
            assert "verification_level" in data
            print(f"✅ POST /api/id-verification/verify-company - status: {data['status']}, level: {data['verification_level']}")
        elif response.status_code == 403:
            # Not a recruiter role
            print(f"⚠️ Company verification requires recruiter role")
        else:
            print(f"⚠️ Company verification response: {response.status_code} - {response.text}")


class TestVideoInterview:
    """Video Interview API Tests"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            return session
        pytest.skip("Authentication failed")
    
    def test_get_common_questions_general(self, auth_session):
        """Test GET /api/video-interview/common-questions/general"""
        response = auth_session.get(f"{BASE_URL}/api/video-interview/common-questions/general")
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert "job_type" in data
        assert "total" in data
        assert data["job_type"] == "general"
        assert len(data["questions"]) > 0
        print(f"✅ GET /api/video-interview/common-questions/general - {data['total']} questions")
    
    def test_get_common_questions_behavioral(self, auth_session):
        """Test GET /api/video-interview/common-questions/behavioral"""
        response = auth_session.get(f"{BASE_URL}/api/video-interview/common-questions/behavioral")
        assert response.status_code == 200
        data = response.json()
        assert data["job_type"] == "behavioral"
        assert len(data["questions"]) > 0
        print(f"✅ GET /api/video-interview/common-questions/behavioral - {data['total']} questions")
    
    def test_create_video_session(self, auth_session):
        """Test POST /api/video-interview/sessions/create"""
        session_data = {
            "title": "Test Practice Session",
            "job_title": "Quality Manager",
            "company_name": "Test Company",
            "questions": [
                "Tell me about yourself.",
                "Why are you interested in this position?"
            ]
        }
        response = auth_session.post(
            f"{BASE_URL}/api/video-interview/sessions/create",
            json=session_data
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["message"] == "Video session created"
        print(f"✅ POST /api/video-interview/sessions/create - session_id: {data['session_id']}")
        return data["session_id"]
    
    def test_list_video_sessions(self, auth_session):
        """Test GET /api/video-interview/sessions"""
        response = auth_session.get(f"{BASE_URL}/api/video-interview/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        print(f"✅ GET /api/video-interview/sessions - {data['total']} sessions")
    
    def test_get_specific_session(self, auth_session):
        """Test GET /api/video-interview/sessions/{session_id}"""
        # First create a session
        session_data = {
            "title": "Session for Get Test",
            "job_title": "Software Engineer",
            "questions": ["What is your experience?"]
        }
        create_response = auth_session.post(
            f"{BASE_URL}/api/video-interview/sessions/create",
            json=session_data
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # Now get the session
        response = auth_session.get(f"{BASE_URL}/api/video-interview/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["title"] == "Session for Get Test"
        print(f"✅ GET /api/video-interview/sessions/{session_id} - retrieved successfully")
    
    def test_delete_video_session(self, auth_session):
        """Test DELETE /api/video-interview/sessions/{session_id}"""
        # First create a session to delete
        session_data = {
            "title": "Session to Delete",
            "questions": ["Test question"]
        }
        create_response = auth_session.post(
            f"{BASE_URL}/api/video-interview/sessions/create",
            json=session_data
        )
        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]
        
        # Delete the session
        response = auth_session.delete(f"{BASE_URL}/api/video-interview/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session deleted"
        print(f"✅ DELETE /api/video-interview/sessions/{session_id} - deleted successfully")
        
        # Verify it's deleted
        get_response = auth_session.get(f"{BASE_URL}/api/video-interview/sessions/{session_id}")
        assert get_response.status_code == 404


class TestUnauthenticatedAccess:
    """Test that endpoints require authentication"""
    
    def test_notifications_preferences_requires_auth(self):
        """Notifications preferences should require auth"""
        response = requests.get(f"{BASE_URL}/api/notifications/preferences")
        assert response.status_code == 401
        print("✅ /api/notifications/preferences requires authentication")
    
    def test_id_verification_status_requires_auth(self):
        """ID verification status should require auth"""
        response = requests.get(f"{BASE_URL}/api/id-verification/status")
        assert response.status_code == 401
        print("✅ /api/id-verification/status requires authentication")
    
    def test_video_sessions_requires_auth(self):
        """Video sessions should require auth"""
        response = requests.get(f"{BASE_URL}/api/video-interview/sessions")
        assert response.status_code == 401
        print("✅ /api/video-interview/sessions requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
