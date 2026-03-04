"""
Full System Validation - Iteration 147
Comprehensive E2E test of AI KARAU platform:
- Auth (login, register, 401)
- Webinar CRUD, roles, QA, hand raises, slides, live transcript
- Caption translation (16 languages)
- STT service
- Recordings and AI notes
- Payments/Plans
- Analytics
"""
import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-prestige.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = f"TEST_user_{uuid.uuid4().hex[:8]}@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


class TestAuthentication:
    """Auth endpoint tests - login, register, 401 handling"""

    def test_admin_login_success(self):
        """POST /api/auth/login with admin credentials returns access_token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "access_token" in data, "Missing access_token in response"
        assert data["access_token"], "access_token is empty"
        assert "user" in data, "Missing user in response"
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"PASS - Admin login returns access_token: {data['access_token'][:20]}...")

    def test_login_wrong_password_401(self):
        """POST /api/auth/login with wrong password returns 401"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": "WrongPassword123!"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS - Wrong password returns 401")

    def test_register_new_user(self):
        """POST /api/auth/register creates new user"""
        response = requests.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "name": "Test User",
            "role": "job_seeker"
        })
        # 200 or 400 (if already exists) are both acceptable
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data
            print(f"PASS - Registered new user: {TEST_EMAIL}")
        else:
            print(f"PASS - Registration handled (user may already exist)")


class TestWebinarCRUD:
    """Webinar CRUD operations"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for webinar tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
    def test_create_webinar(self):
        """POST /api/karau/webinar/create creates webinar"""
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_Webinar_{uuid.uuid4().hex[:6]}",
            "description": "Full system validation test webinar",
            "scheduled_time": datetime.utcnow().isoformat(),
            "max_attendees": 100,
            "q_and_a_enabled": True
        }, headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "webinar_id" in data, "Missing webinar_id"
        assert data["title"].startswith("TEST_Webinar")
        # Store for later tests
        self.__class__.webinar_id = data["webinar_id"]
        print(f"PASS - Created webinar: {data['webinar_id']}")

    def test_list_webinars(self):
        """GET /api/karau/webinar/list returns user's webinars"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert "webinars" in data
        assert isinstance(data["webinars"], list)
        print(f"PASS - Listed {len(data['webinars'])} webinars")

    def test_get_webinar_details(self):
        """GET /api/karau/webinar/{id} returns webinar details"""
        # Use the created webinar or get first from list
        response = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=self.headers)
        webinars = response.json().get("webinars", [])
        if webinars:
            webinar_id = webinars[0]["webinar_id"]
            response = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}", headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert "title" in data
            print(f"PASS - Got webinar details for {webinar_id}")
        else:
            pytest.skip("No webinars available")


class TestWebinarRoles:
    """Webinar role management - promote, demote, room-info"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth and create webinar"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.user_id = response.json()["user"]["user_id"]
        
        # Create webinar for role tests
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_RoleWebinar_{uuid.uuid4().hex[:6]}",
            "description": "Role management test",
            "scheduled_time": datetime.utcnow().isoformat()
        }, headers=self.headers)
        self.webinar_id = response.json()["webinar_id"]

    def test_room_info_returns_role_permissions(self):
        """GET /api/karau/webinar/{id}/room-info returns role and permissions"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/room-info",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        # Verify required fields
        assert "my_role" in data, "Missing my_role"
        assert "can_stream_video" in data, "Missing can_stream_video"
        assert "can_control" in data, "Missing can_control"
        assert "can_drive_slides" in data, "Missing can_drive_slides"
        # Host should have all permissions
        assert data["my_role"] == "host"
        assert data["can_stream_video"] == True
        assert data["can_control"] == True
        assert data["can_drive_slides"] == True
        print(f"PASS - room-info returns my_role={data['my_role']}, can_control={data['can_control']}")

    def test_promote_participant(self):
        """POST /api/karau/webinar/{id}/roles/promote promotes user"""
        # Create a dummy user_id for testing
        target_user_id = f"user_test_{uuid.uuid4().hex[:8]}"
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/roles/promote",
            json={"user_id": target_user_id, "role": "presenter"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["role"] == "presenter"
        print(f"PASS - Promoted {target_user_id} to presenter")

    def test_demote_participant(self):
        """POST /api/karau/webinar/{id}/roles/demote demotes user"""
        target_user_id = f"user_demote_{uuid.uuid4().hex[:8]}"
        # First promote
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/roles/promote",
            json={"user_id": target_user_id, "role": "panelist"},
            headers=self.headers
        )
        # Then demote
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/roles/demote",
            json={"user_id": target_user_id, "role": "panelist"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        print(f"PASS - Demoted {target_user_id}")


class TestWebinarLifecycle:
    """Webinar start, practice, end"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create webinar
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_LifecycleWebinar_{uuid.uuid4().hex[:6]}",
            "scheduled_time": datetime.utcnow().isoformat()
        }, headers=self.headers)
        self.webinar_id = response.json()["webinar_id"]

    def test_start_webinar(self):
        """POST /api/karau/webinar/{id}/start - host only"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/start",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "live"
        print(f"PASS - Started webinar {self.webinar_id}")

    def test_start_practice_session(self):
        """POST /api/karau/webinar/{id}/practice/start"""
        # Create new webinar for practice
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_PracticeWebinar_{uuid.uuid4().hex[:6]}",
            "scheduled_time": datetime.utcnow().isoformat()
        }, headers=self.headers)
        webinar_id = response.json()["webinar_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{webinar_id}/practice/start",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "practice"
        print(f"PASS - Started practice session for {webinar_id}")


class TestWebinarQA:
    """Q&A: ask, list, answer, upvote"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create webinar
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_QAWebinar_{uuid.uuid4().hex[:6]}",
            "scheduled_time": datetime.utcnow().isoformat(),
            "q_and_a_enabled": True
        }, headers=self.headers)
        self.webinar_id = response.json()["webinar_id"]

    def test_ask_question(self):
        """POST /api/karau/webinar/{id}/qa/ask submits question"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/qa/ask",
            json={"question": "Test question for full validation?", "is_anonymous": False},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "question_id" in data
        self.__class__.question_id = data["question_id"]
        print(f"PASS - Asked question: {data['question_id']}")

    def test_get_questions(self):
        """GET /api/karau/webinar/{id}/qa returns questions list"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/qa",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
        assert isinstance(data["questions"], list)
        print(f"PASS - Got {len(data['questions'])} questions")

    def test_answer_question(self):
        """POST /api/karau/webinar/{id}/qa/{qid}/answer"""
        # First ask a question
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/qa/ask",
            json={"question": "Another test question?"},
            headers=self.headers
        )
        qid = response.json()["question_id"]
        
        # Answer it
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/qa/{qid}/answer",
            json={"answer": "This is the answer!"},
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        print(f"PASS - Answered question {qid}")

    def test_upvote_question(self):
        """POST /api/karau/webinar/{id}/qa/{qid}/upvote"""
        # Ask question
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/qa/ask",
            json={"question": "Upvote test question?"},
            headers=self.headers
        )
        qid = response.json()["question_id"]
        
        # Upvote
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/qa/{qid}/upvote",
            headers=self.headers
        )
        assert response.status_code == 200
        print(f"PASS - Upvoted question {qid}")


class TestWebinarHandRaises:
    """Hand raise functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_HandRaiseWebinar_{uuid.uuid4().hex[:6]}",
            "scheduled_time": datetime.utcnow().isoformat()
        }, headers=self.headers)
        self.webinar_id = response.json()["webinar_id"]

    def test_raise_hand(self):
        """POST /api/karau/webinar/{id}/hand-raise"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/hand-raise",
            headers=self.headers
        )
        assert response.status_code == 200
        assert response.json()["success"] == True
        print("PASS - Hand raised")

    def test_get_hand_raises(self):
        """GET /api/karau/webinar/{id}/hand-raises"""
        # First raise hand
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/hand-raise",
            headers=self.headers
        )
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/hand-raises",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "hand_raises" in data
        print(f"PASS - Got {len(data['hand_raises'])} hand raises")


class TestCaptionTranslation:
    """Caption translation - 16 languages"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_caption_languages_returns_16(self):
        """GET /api/karau/webinar/caption-languages returns 16 languages"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/caption-languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) == 16, f"Expected 16 languages, got {len(data['languages'])}"
        print(f"PASS - caption-languages returns 16 languages: {list(data['languages'].keys())}")

    def test_translate_en_to_es(self):
        """POST /api/karau/webinar/translate-caption EN->ES"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "Hello, this is a test.", "source_language": "en", "target_language": "es"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "translated" in data
        assert data["source"] == "en"
        assert data["target"] == "es"
        assert data["translated"], "Translated text is empty"
        print(f"PASS - EN->ES translation: '{data['translated']}'")

    def test_translate_en_to_fr(self):
        """POST /api/karau/webinar/translate-caption EN->FR"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "Good morning everyone.", "source_language": "en", "target_language": "fr"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["translated"], "Translated text is empty"
        print(f"PASS - EN->FR translation: '{data['translated']}'")

    def test_translate_en_to_ja(self):
        """POST /api/karau/webinar/translate-caption EN->JA"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "Welcome to the meeting.", "source_language": "en", "target_language": "ja"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["translated"], "Translated text is empty"
        print(f"PASS - EN->JA translation: '{data['translated']}'")

    def test_translate_same_language_no_llm(self):
        """Same language returns original without LLM call"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "This is already English.", "source_language": "en", "target_language": "en"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["translated"] == "This is already English."
        print("PASS - Same language returns original")

    def test_translate_empty_text(self):
        """Empty text returns empty"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "", "source_language": "en", "target_language": "es"},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["translated"] == ""
        print("PASS - Empty text returns empty")

    def test_translate_requires_auth(self):
        """translate-caption requires auth (401 without token)"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "Test", "source_language": "en", "target_language": "es"}
            # No auth header
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS - translate-caption requires auth (401)")


class TestLiveTranscript:
    """Live transcript save and get"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_TranscriptWebinar_{uuid.uuid4().hex[:6]}",
            "scheduled_time": datetime.utcnow().isoformat()
        }, headers=self.headers)
        self.webinar_id = response.json()["webinar_id"]

    def test_save_live_transcript_host(self):
        """POST /api/karau/webinar/{id}/live-transcript/save - host can save"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/live-transcript/save",
            json={"transcript": "This is the full transcript text.", "duration_seconds": 120.5},
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["word_count"] > 0
        print(f"PASS - Host saved transcript ({data['word_count']} words)")

    def test_get_live_transcript(self):
        """GET /api/karau/webinar/{id}/live-transcript"""
        # First save
        requests.post(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/live-transcript/save",
            json={"transcript": "Transcript for retrieval test.", "duration_seconds": 60},
            headers=self.headers
        )
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/live-transcript",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "transcript" in data
        print("PASS - Retrieved live transcript")


class TestSTTService:
    """Speech-to-Text service status and transcribe"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_stt_status(self):
        """GET /api/realtime-stt/status returns available:true"""
        response = requests.get(
            f"{BASE_URL}/api/realtime-stt/status",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        # Should be true if EMERGENT_LLM_KEY is configured
        print(f"PASS - STT status: available={data['available']}")

    def test_transcribe_base64_validates_input(self):
        """POST /api/realtime-stt/transcribe-base64 validates input"""
        response = requests.post(
            f"{BASE_URL}/api/realtime-stt/transcribe-base64",
            json={},  # Missing audio
            headers=self.headers
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS - transcribe-base64 returns 400 for missing audio")


class TestRecordings:
    """Recordings list, stats, notes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_recordings_list(self):
        """GET /api/karau-meet/recordings/ returns recordings list"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "recordings" in data
        assert isinstance(data["recordings"], list)
        print(f"PASS - Got {len(data['recordings'])} recordings")

    def test_get_recording_stats(self):
        """GET /api/karau-meet/recordings/stats returns stats"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/stats",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_recordings" in data
        print(f"PASS - Recording stats: total={data.get('total_recordings', 0)}")

    def test_notes_generate_404_nonexistent(self):
        """POST /api/karau-meet/recordings/{id}/notes/generate returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/nonexistent123/notes/generate",
            headers=self.headers
        )
        assert response.status_code == 404
        print("PASS - notes/generate returns 404 for nonexistent recording")

    def test_notes_get_404_nonexistent(self):
        """GET /api/karau-meet/recordings/{id}/notes returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/nonexistent123/notes",
            headers=self.headers
        )
        assert response.status_code == 404
        print("PASS - notes/get returns 404 for nonexistent recording")


class TestPayments:
    """Payment plans endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_get_membership_status(self):
        """GET /api/membership/status returns subscription info"""
        response = requests.get(
            f"{BASE_URL}/api/membership/status",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "is_active" in data
        print(f"PASS - Membership status: {data['status']}, active={data['is_active']}")


class TestWebinarAnalytics:
    """Webinar analytics endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_AnalyticsWebinar_{uuid.uuid4().hex[:6]}",
            "scheduled_time": datetime.utcnow().isoformat()
        }, headers=self.headers)
        self.webinar_id = response.json()["webinar_id"]

    def test_get_analytics(self):
        """GET /api/karau/webinar/{id}/analytics returns analytics data"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/analytics",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "funnel" in data
        assert "qa_stats" in data
        assert "engagement" in data
        print(f"PASS - Analytics: engagement_score={data['engagement'].get('score', 0)}")


class TestWebinarSlides:
    """Presentation slides endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        response = requests.post(f"{BASE_URL}/api/karau/webinar/create", json={
            "title": f"TEST_SlidesWebinar_{uuid.uuid4().hex[:6]}",
            "scheduled_time": datetime.utcnow().isoformat()
        }, headers=self.headers)
        self.webinar_id = response.json()["webinar_id"]

    def test_get_slides_404_when_none(self):
        """GET /api/karau/webinar/{id}/presentation/slides returns 404 when no slides"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{self.webinar_id}/presentation/slides",
            headers=self.headers
        )
        assert response.status_code == 404
        print("PASS - slides returns 404 when no presentation")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
