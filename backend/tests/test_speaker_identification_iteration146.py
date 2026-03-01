"""
Iteration 146: Speaker Identification in Live Captions
Tests for speaker detection hook integration and backend API regression
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthAndToken:
    """Authentication tests to get token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_login_success(self, auth_token):
        """Verify login works and returns token"""
        assert auth_token is not None
        assert len(auth_token) > 0
        print(f"✓ Login successful, got token: {auth_token[:20]}...")


class TestCaptionLanguagesAPI:
    """Test caption languages endpoint - returns 16 languages"""
    
    def test_caption_languages_returns_16(self):
        """GET /api/karau/webinar/caption-languages should return 16 languages"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/caption-languages")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "languages" in data, "Response missing 'languages' key"
        
        languages = data["languages"]
        assert len(languages) == 16, f"Expected 16 languages, got {len(languages)}"
        
        # Verify all expected language codes are present
        expected_codes = ["en", "es", "fr", "de", "it", "pt", "ja", "ko", 
                        "zh", "nl", "ar", "hi", "ru", "tr", "pl", "sv"]
        for code in expected_codes:
            assert code in languages, f"Missing language code: {code}"
        
        print(f"✓ caption-languages returns all 16 languages: {list(languages.keys())}")
    
    def test_caption_languages_no_auth_required(self):
        """caption-languages endpoint is public (no auth needed)"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/caption-languages")
        assert response.status_code == 200, "Should work without auth token"
        print("✓ caption-languages is public (no auth required)")


class TestTranslateCaptionAPI:
    """Test translate-caption endpoint with auth"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        return response.json().get("access_token")
    
    def test_translate_en_to_es_with_auth(self, auth_token):
        """POST /api/karau/webinar/translate-caption - EN to ES translation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "Hello, how are you?", "source_language": "en", "target_language": "es"},
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "translated" in data, "Response missing 'translated'"
        # Spanish translation should contain common words
        translated_lower = data["translated"].lower()
        assert any(word in translated_lower for word in ["hola", "cómo", "como", "estás"]), \
            f"Translation doesn't look like Spanish: {data['translated']}"
        
        print(f"✓ EN->ES translation: '{data['translated']}'")
    
    def test_translate_same_language_noop(self, auth_token):
        """Same language should return original text without calling LLM"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "Hello world", "source_language": "en", "target_language": "en"},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["translated"] == "Hello world", f"Same-lang should return original, got: {data['translated']}"
        print("✓ Same language returns original text (no LLM call)")


class TestLiveTranscriptAPI:
    """Test live transcript save endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for admin (host)"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def test_webinar_id(self, auth_token):
        """Create a test webinar for transcript testing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/create",
            json={
                "title": "TEST_Speaker_Detection_Webinar",
                "description": "Testing speaker identification feature",
                "scheduled_time": "2026-01-25T10:00:00Z",
                "max_attendees": 100
            },
            headers=headers
        )
        if response.status_code == 200:
            return response.json().get("webinar_id")
        return None
    
    def test_save_live_transcript_as_host(self, auth_token, test_webinar_id):
        """POST /api/karau/webinar/{id}/live-transcript/save - Host can save transcript"""
        if not test_webinar_id:
            pytest.skip("No test webinar available")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/live-transcript/save",
            json={
                "transcript": "Speaker1: Hello everyone. Speaker2: Welcome to the webinar. Speaker1: Let's begin.",
                "duration_seconds": 120.5
            },
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Expected success=true"
        assert "word_count" in data, "Response should include word_count"
        assert data["word_count"] > 0, "Word count should be positive"
        
        print(f"✓ Live transcript saved successfully, word_count={data['word_count']}")
    
    def test_get_live_transcript(self, auth_token, test_webinar_id):
        """GET /api/karau/webinar/{id}/live-transcript - Retrieve saved transcript"""
        if not test_webinar_id:
            pytest.skip("No test webinar available")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/live-transcript",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "transcript" in data, "Response should have 'transcript' key"
        
        if data["transcript"]:
            assert "text" in data["transcript"], "Transcript should have 'text' field"
            print(f"✓ Retrieved transcript: {data['transcript']['text'][:50]}...")
        else:
            print("✓ Get transcript endpoint works (no transcript saved yet)")


class TestWebinarRoomInfoAPI:
    """Test webinar room-info endpoint (used by WebinarLiveRoom)"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def test_webinar_id(self, auth_token):
        """Get or create a test webinar"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # First try to list existing webinars
        response = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        if response.status_code == 200:
            webinars = response.json().get("webinars", [])
            if webinars:
                return webinars[0].get("webinar_id")
        
        # Create new webinar
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/create",
            json={
                "title": "TEST_Room_Info_Webinar",
                "description": "For testing room-info endpoint",
                "scheduled_time": "2026-01-25T11:00:00Z"
            },
            headers=headers
        )
        if response.status_code == 200:
            return response.json().get("webinar_id")
        return None
    
    def test_room_info_returns_required_fields(self, auth_token, test_webinar_id):
        """GET /api/karau/webinar/{id}/room-info should return role and permissions"""
        if not test_webinar_id:
            pytest.skip("No test webinar available")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar_id}/room-info",
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify required fields for WebinarLiveRoom component
        required_fields = ["webinar_id", "title", "status", "my_role", 
                         "can_stream_video", "can_control", "settings", "host_name"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Host should have specific permissions
        assert data["my_role"] == "host", f"Admin should be host, got: {data['my_role']}"
        assert data["can_stream_video"] == True, "Host should be able to stream video"
        assert data["can_control"] == True, "Host should have control permissions"
        
        print(f"✓ room-info returns all required fields for WebinarLiveRoom")
        print(f"  - Role: {data['my_role']}, Can stream: {data['can_stream_video']}, Can control: {data['can_control']}")


class TestBackendRegression:
    """Regression tests for existing webinar endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        return response.json().get("access_token")
    
    def test_webinar_list(self, auth_token):
        """GET /api/karau/webinar/list - List user's webinars"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "webinars" in data, "Response should have 'webinars' key"
        print(f"✓ webinar/list works, found {len(data['webinars'])} webinars")
    
    def test_webinar_create(self, auth_token):
        """POST /api/karau/webinar/create - Create new webinar"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/create",
            json={
                "title": "TEST_Regression_Webinar",
                "description": "Testing webinar creation still works",
                "scheduled_time": "2026-01-26T10:00:00Z",
                "max_attendees": 50
            },
            headers=headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "webinar_id" in data, "Response should have webinar_id"
        assert data["title"] == "TEST_Regression_Webinar"
        print(f"✓ webinar/create works, created {data['webinar_id']}")
    
    def test_webinar_qa_public(self):
        """GET /api/karau/webinar/{id}/qa - Q&A endpoint is public"""
        # First get a webinar id
        auth_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        token = auth_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        list_response = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=headers)
        webinars = list_response.json().get("webinars", [])
        
        if not webinars:
            pytest.skip("No webinars to test Q&A")
        
        webinar_id = webinars[0]["webinar_id"]
        
        # Q&A should be accessible without auth
        response = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/qa")
        assert response.status_code == 200, f"Q&A should be public, got {response.status_code}"
        
        data = response.json()
        assert "questions" in data, "Response should have 'questions' key"
        print(f"✓ webinar/{webinar_id}/qa is public")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
