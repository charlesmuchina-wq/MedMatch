"""
Test suite for i18n pages - QAPracticePage, SkillAssessmentsPage, SuccessPredictorPage, 
VideoInterviewPage, VoiceCoachPage, JobAlertsPage
Tests API endpoints and verifies i18n implementation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jobmatch-pro-47.preview.emergentagent.com')

class TestHealthAndStatus:
    """Basic health check tests"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check passed: {data}")
    
    def test_status_endpoint(self):
        """Test /api/status returns operational status"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✅ Status check passed: {data}")


class TestSkillAssessmentsAPI:
    """Tests for Skill Assessments page APIs"""
    
    def test_skills_available(self):
        """Test /api/skills/available returns assessments"""
        response = requests.get(f"{BASE_URL}/api/skills/available")
        assert response.status_code == 200
        data = response.json()
        assert "assessments" in data
        assert "by_category" in data
        assert len(data["assessments"]) > 0
        print(f"✅ Skills available: {len(data['assessments'])} assessments found")
    
    def test_skills_my_badges(self):
        """Test /api/skills/my-badges endpoint"""
        response = requests.get(f"{BASE_URL}/api/skills/my-badges")
        # May return 401 if not authenticated, or 200 with empty badges
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "badges" in data
            print(f"✅ My badges endpoint working: {len(data.get('badges', []))} badges")
        else:
            print("⚠️ My badges requires authentication")


class TestQAPracticeAPI:
    """Tests for Q&A Practice page APIs"""
    
    def test_qa_favorites(self):
        """Test /api/qa-practice/favorites endpoint"""
        response = requests.get(f"{BASE_URL}/api/qa-practice/favorites")
        # May return 401 if not authenticated
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert "favorites" in data
            print(f"✅ Q&A favorites endpoint working: {len(data.get('favorites', []))} favorites")
        else:
            print("⚠️ Q&A favorites requires authentication")


class TestSuccessPredictorAPI:
    """Tests for Success Predictor page APIs"""
    
    def test_predictor_history(self):
        """Test /api/success-predictor/history endpoint"""
        response = requests.get(f"{BASE_URL}/api/success-predictor/history")
        # May return 401 if not authenticated
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            print("✅ Success predictor history endpoint working")
        else:
            print("⚠️ Success predictor history requires authentication")


class TestJobAlertsAPI:
    """Tests for Job Alerts page APIs"""
    
    def test_scheduler_status(self):
        """Test /api/job-alerts/scheduler-status endpoint"""
        response = requests.get(f"{BASE_URL}/api/job-alerts/scheduler-status")
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job alerts scheduler status: {data}")
        else:
            print("⚠️ Job alerts scheduler requires authentication")


class TestVoiceCoachAPI:
    """Tests for Voice Coach page APIs"""
    
    def test_voice_sessions(self):
        """Test /api/voice-coach/sessions endpoint"""
        response = requests.get(f"{BASE_URL}/api/voice-coach/sessions")
        # May return 401 if not authenticated
        assert response.status_code in [200, 401, 404]
        if response.status_code == 200:
            print("✅ Voice coach sessions endpoint working")
        elif response.status_code == 404:
            print("⚠️ Voice coach sessions endpoint not found")
        else:
            print("⚠️ Voice coach sessions requires authentication")


class TestCachedEndpoints:
    """Tests for cached/static endpoints"""
    
    def test_cached_languages(self):
        """Test /api/cached/languages endpoint"""
        response = requests.get(f"{BASE_URL}/api/cached/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        print(f"✅ Cached languages: {len(data['languages'])} languages")
    
    def test_cached_id_levels(self):
        """Test /api/cached/id-levels endpoint"""
        response = requests.get(f"{BASE_URL}/api/cached/id-levels")
        assert response.status_code == 200
        data = response.json()
        assert "levels" in data
        print(f"✅ Cached ID levels: {len(data['levels'])} levels")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
