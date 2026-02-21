"""
Test Suite for Bug Fixes - Iteration 68
Testing: Translation QA, RealTime STT, Skill Assessments, Video Tutorials Translation

Tests the following fixes:
1. Translation QA Dashboard page at /qa-dashboard
2. RealTime STT page at /realtime-stt
3. Skill Assessments page at /skill-assessments
4. Video Tutorials - Generate Audio button
5. POST /api/tutorials/translate/{video_id}?lang=es endpoint
6. GET /api/tutorials/translate/{video_id}/status?lang=es endpoint
7. GET /api/realtime-stt/status endpoint
8. GET /api/skills/available endpoint
9. GET /api/translation-qa/dashboard-summary endpoint
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://medmatch-translate.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "MedMatch2026!"


class TestAuthSetup:
    """Authentication setup for tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("token") or data.get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def auth_cookies(self):
        """Get authentication cookies"""
        session = requests.Session()
        response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            return session.cookies
        pytest.skip("Authentication failed - skipping authenticated tests")


class TestHealthEndpoints:
    """Test basic health endpoints"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "ai_supervisor" in data
        print(f"✅ API Health: {data['status']}, AI Supervisor: {data['ai_supervisor']}")
    
    def test_api_status(self):
        """Test API status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        print(f"✅ API Status: {data['status']}, MongoDB: {data['mongodb']['status']}")


class TestTranslationQADashboard:
    """Test Translation QA Dashboard endpoints - Issue #1"""
    
    def test_dashboard_summary_endpoint(self):
        """Test GET /api/translation-qa/dashboard-summary returns proper data"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/dashboard-summary")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "overall_score" in data, "Missing overall_score in response"
        assert "health" in data, "Missing health in response"
        assert "total_languages" in data, "Missing total_languages in response"
        assert "total_keys" in data, "Missing total_keys in response"
        assert "issues" in data, "Missing issues in response"
        assert "language_status" in data, "Missing language_status in response"
        
        # Verify data types
        assert isinstance(data["overall_score"], (int, float)), "overall_score should be numeric"
        assert isinstance(data["total_languages"], int), "total_languages should be int"
        
        print(f"✅ Translation QA Dashboard Summary:")
        print(f"   - Overall Score: {data['overall_score']}")
        print(f"   - Health: {data['health']}")
        print(f"   - Total Languages: {data['total_languages']}")
        print(f"   - Total Keys: {data['total_keys']}")
    
    def test_translation_qa_latest(self):
        """Test GET /api/translation-qa/latest returns QA results"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/latest")
        assert response.status_code == 200
        data = response.json()
        
        assert "run_id" in data, "Missing run_id"
        assert "status" in data, "Missing status"
        assert "languages" in data, "Missing languages"
        
        print(f"✅ Translation QA Latest: run_id={data['run_id']}, status={data['status']}")
    
    def test_translation_qa_score(self):
        """Test GET /api/translation-qa/score returns language scores"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/score")
        assert response.status_code == 200
        data = response.json()
        
        assert "overall_score" in data
        assert "language_scores" in data
        
        print(f"✅ Translation QA Score: {data['overall_score']}")


class TestRealTimeSTT:
    """Test Real-Time STT endpoints - Issue #2"""
    
    def test_stt_status_unauthenticated(self):
        """Test GET /api/realtime-stt/status returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/realtime-stt/status")
        # Should require authentication
        assert response.status_code == 401
        print("✅ STT Status correctly requires authentication")
    
    def test_stt_status_authenticated(self):
        """Test GET /api/realtime-stt/status returns available:true when authenticated"""
        # First login
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        # Now test STT status
        response = session.get(f"{BASE_URL}/api/realtime-stt/status")
        assert response.status_code == 200, f"STT status failed: {response.text}"
        data = response.json()
        
        assert "available" in data, "Missing 'available' field"
        assert "features" in data, "Missing 'features' field"
        assert "model" in data, "Missing 'model' field"
        
        print(f"✅ STT Status (authenticated):")
        print(f"   - Available: {data['available']}")
        print(f"   - Model: {data['model']}")
        print(f"   - Features: {list(data['features'].keys())}")


class TestSkillAssessments:
    """Test Skill Assessments endpoints - Issue #3"""
    
    def test_skills_available_endpoint(self):
        """Test GET /api/skills/available returns list of assessments"""
        response = requests.get(f"{BASE_URL}/api/skills/available")
        assert response.status_code == 200
        data = response.json()
        
        assert "assessments" in data, "Missing assessments in response"
        assert "by_category" in data, "Missing by_category in response"
        assert isinstance(data["assessments"], list), "assessments should be a list"
        assert len(data["assessments"]) > 0, "Should have at least one assessment"
        
        # Verify assessment structure
        first_assessment = data["assessments"][0]
        assert "skill_name" in first_assessment
        assert "category" in first_assessment
        assert "questions" in first_assessment
        assert "time_limit" in first_assessment
        assert "passing_score" in first_assessment
        assert "badge_icon" in first_assessment
        
        print(f"✅ Skills Available:")
        print(f"   - Total Assessments: {len(data['assessments'])}")
        print(f"   - Categories: {list(data['by_category'].keys())}")
    
    def test_skills_categories_endpoint(self):
        """Test GET /api/skills/categories returns categories"""
        response = requests.get(f"{BASE_URL}/api/skills/categories")
        assert response.status_code == 200
        data = response.json()
        
        assert "categories" in data
        assert "total_categories" in data
        
        print(f"✅ Skills Categories: {data['total_categories']} categories")


class TestVideoTutorials:
    """Test Video Tutorials endpoints - Issue #4"""
    
    def test_tutorials_videos_list(self):
        """Test GET /api/tutorials/videos returns video list"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        data = response.json()
        
        assert "videos" in data, "Missing videos in response"
        assert "count" in data, "Missing count in response"
        assert len(data["videos"]) > 0, "Should have at least one video"
        
        # Verify video structure
        first_video = data["videos"][0]
        assert "id" in first_video
        assert "title" in first_video
        assert "description" in first_video
        assert "duration" in first_video
        
        print(f"✅ Tutorial Videos: {data['count']} videos available")
        for v in data["videos"][:3]:
            print(f"   - {v['id']}: {v['title']}")
    
    def test_tutorials_translate_endpoint(self):
        """Test POST /api/tutorials/translate/{video_id}?lang=es returns 200 with job_id"""
        video_id = "01_jobseeker_features"
        lang = "es"
        
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/{video_id}?lang={lang}")
        assert response.status_code == 200, f"Translate endpoint failed: {response.text}"
        data = response.json()
        
        assert "job_id" in data, "Missing job_id in response"
        assert "status" in data, "Missing status in response"
        
        print(f"✅ Tutorial Translate Endpoint:")
        print(f"   - Job ID: {data['job_id']}")
        print(f"   - Status: {data['status']}")
    
    def test_tutorials_translate_status_endpoint(self):
        """Test GET /api/tutorials/translate/{video_id}/status?lang=es returns status"""
        video_id = "01_jobseeker_features"
        lang = "es"
        
        response = requests.get(f"{BASE_URL}/api/tutorials/translate/{video_id}/status?lang={lang}")
        assert response.status_code == 200, f"Translate status endpoint failed: {response.text}"
        data = response.json()
        
        assert "job_id" in data, "Missing job_id in response"
        assert "status" in data, "Missing status in response"
        
        print(f"✅ Tutorial Translate Status:")
        print(f"   - Job ID: {data['job_id']}")
        print(f"   - Status: {data['status']}")
    
    def test_tutorials_multilang_videos(self):
        """Test GET /api/tutorials/videos/multilang returns language options"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/multilang")
        assert response.status_code == 200
        data = response.json()
        
        assert "languages" in data or "tutorials" in data
        print(f"✅ Multilang Videos endpoint working")
    
    def test_tutorials_guide(self):
        """Test GET /api/tutorials/guide returns navigation guide"""
        response = requests.get(f"{BASE_URL}/api/tutorials/guide")
        # May return 404 if guide file doesn't exist, which is acceptable
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            print("✅ Tutorial Guide available")
        else:
            print("⚠️ Tutorial Guide file not found (acceptable)")


class TestMyBadges:
    """Test My Badges endpoint (requires auth)"""
    
    def test_my_badges_authenticated(self):
        """Test GET /api/skills/my-badges returns user badges"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/skills/my-badges")
        assert response.status_code == 200
        data = response.json()
        
        assert "badges" in data
        assert "total" in data
        
        print(f"✅ My Badges: {data['total']} badges earned")


class TestTranscriptionHistory:
    """Test Transcription History endpoint (requires auth)"""
    
    def test_transcription_history_authenticated(self):
        """Test GET /api/realtime-stt/history returns transcription history"""
        session = requests.Session()
        login_response = session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert login_response.status_code == 200
        
        response = session.get(f"{BASE_URL}/api/realtime-stt/history")
        assert response.status_code == 200
        data = response.json()
        
        assert "history" in data
        assert "count" in data
        
        print(f"✅ Transcription History: {data['count']} transcriptions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
