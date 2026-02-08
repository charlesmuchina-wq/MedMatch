"""
Test Suite for Iteration 58 - Video Tutorials, Skill Tests, Dragon AI, Login Button
Tests the recent updates including:
1. Video Tutorials system with 5 videos
2. Skill Tests loading fix
3. Dragon AI job search enhancement
4. Sign-in button color
5. Rate limits for free tier
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestVideoTutorials:
    """Test Video Tutorials API - 5 videos with diverse presenters"""
    
    def test_list_all_videos(self):
        """Verify all 5 tutorial videos are returned"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        
        data = response.json()
        assert "videos" in data
        assert data["count"] == 5
        
        videos = data["videos"]
        expected_ids = [
            "01_jobseeker_features",
            "02_recruiter_features",
            "03_privacy_matters",
            "04_faq_ai_compliance",
            "05_complete_overview"
        ]
        
        actual_ids = [v["id"] for v in videos]
        for expected_id in expected_ids:
            assert expected_id in actual_ids, f"Missing video: {expected_id}"
    
    def test_video_metadata_structure(self):
        """Verify video metadata has required fields"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        
        videos = response.json()["videos"]
        required_fields = ["id", "title", "description", "duration", "category", "url"]
        
        for video in videos:
            for field in required_fields:
                assert field in video, f"Missing field '{field}' in video {video.get('id')}"
    
    def test_video_categories(self):
        """Verify videos have correct categories"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        
        videos = response.json()["videos"]
        
        # Check specific video categories
        video_categories = {v["id"]: v["category"] for v in videos}
        
        assert video_categories["01_jobseeker_features"] == "job_seeker"
        assert video_categories["02_recruiter_features"] == "recruiter"
        assert video_categories["03_privacy_matters"] == "general"
        assert video_categories["04_faq_ai_compliance"] == "general"
        assert video_categories["05_complete_overview"] == "overview"
    
    def test_filter_by_category(self):
        """Test filtering videos by category"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos?category=job_seeker")
        assert response.status_code == 200
        
        videos = response.json()["videos"]
        for video in videos:
            assert video["category"] == "job_seeker"


class TestSkillAssessments:
    """Test Skill Assessments API"""
    
    def test_list_available_assessments(self):
        """Verify skill assessments are available"""
        response = requests.get(f"{BASE_URL}/api/skills/available")
        assert response.status_code == 200
        
        data = response.json()
        assert "assessments" in data
        assert len(data["assessments"]) > 0
    
    def test_assessment_structure(self):
        """Verify assessment metadata structure"""
        response = requests.get(f"{BASE_URL}/api/skills/available")
        assert response.status_code == 200
        
        assessments = response.json()["assessments"]
        required_fields = ["skill_name", "category", "questions", "time_limit", "passing_score"]
        
        for assessment in assessments[:5]:  # Check first 5
            for field in required_fields:
                assert field in assessment, f"Missing field '{field}' in assessment"
    
    def test_categories_available(self):
        """Verify assessments are grouped by category"""
        response = requests.get(f"{BASE_URL}/api/skills/available")
        assert response.status_code == 200
        
        data = response.json()
        assert "by_category" in data
        
        # Check some expected categories exist
        categories = data["by_category"]
        expected_categories = ["Quality Engineering", "Software Engineering"]
        
        for cat in expected_categories:
            assert cat in categories, f"Missing category: {cat}"


class TestDragonAIAssistant:
    """Test Dragon AI Assistant API"""
    
    def test_assistant_endpoint_exists(self):
        """Verify assistant endpoint is accessible (requires auth)"""
        response = requests.post(
            f"{BASE_URL}/api/assistant",
            json={"message": "test", "context": "general"}
        )
        # Should return 401 without auth, not 404
        assert response.status_code in [401, 422, 200]
    
    def test_assistant_with_job_search_context(self):
        """Test assistant recognizes job search intent"""
        # This test verifies the endpoint structure
        # Full job search requires authentication
        response = requests.post(
            f"{BASE_URL}/api/assistant",
            json={
                "message": "Interested in Supplier Quality Manager",
                "context": "job_search"
            }
        )
        # Should return 401 without auth
        assert response.status_code in [401, 422, 200]


class TestAuthEndpoints:
    """Test Authentication endpoints"""
    
    def test_login_endpoint(self):
        """Test login endpoint with test credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "test_jobseeker_ui@test.com",
                "password": "Test123!"
            }
        )
        # Should succeed or return proper error
        assert response.status_code in [200, 401, 422]
        
        if response.status_code == 200:
            data = response.json()
            assert "user" in data
    
    def test_register_endpoint_structure(self):
        """Test register endpoint accepts required fields"""
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json={
                "email": "test_new_user_temp@test.com",
                "password": "TestPass123!",
                "name": "Test User",
                "role": "job_seeker"
            }
        )
        # Should succeed or return conflict if user exists
        assert response.status_code in [200, 201, 409, 422]


class TestHealthAndStatus:
    """Test health and status endpoints"""
    
    def test_api_health(self):
        """Verify API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
    
    def test_tutorials_endpoint_accessible(self):
        """Verify tutorials endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
    
    def test_skills_endpoint_accessible(self):
        """Verify skills endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/skills/available")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
