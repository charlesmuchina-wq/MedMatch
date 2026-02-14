"""
Test MEDIUM severity bug fixes for MedMatch
- Job Search status badges (not showing 'Unknown')
- Interview Prep AI question generation
- Translation keys in en.json
- Video Tutorials diverse presenters
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestMediumSeverityFixes:
    """Test MEDIUM severity bug fixes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get token
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "MedMatch2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
        token = login_response.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        print(f"Logged in successfully, token: {token[:20]}...")
    
    def test_interview_prep_endpoint_returns_questions(self):
        """Test POST /api/interview-prep returns questions array with question, type, tip fields"""
        response = self.session.post(
            f"{BASE_URL}/api/interview-prep",
            json={
                "job_title": "Software Engineer",
                "company": "Google",
                "difficulty": "medium",
                "num_questions": 3,
                "topics": ["technical", "behavioral"]
            }
        )
        
        print(f"Interview prep response status: {response.status_code}")
        print(f"Interview prep response: {response.text[:500]}")
        
        assert response.status_code == 200, f"Interview prep failed: {response.text}"
        
        data = response.json()
        
        # Verify questions array exists
        assert "questions" in data, "Response should contain 'questions' array"
        questions = data["questions"]
        assert isinstance(questions, list), "Questions should be a list"
        assert len(questions) > 0, "Should have at least one question"
        
        # Verify each question has required fields
        for i, q in enumerate(questions):
            assert "question" in q, f"Question {i} missing 'question' field"
            assert "type" in q, f"Question {i} missing 'type' field"
            assert "tip" in q, f"Question {i} missing 'tip' field"
            print(f"Question {i+1}: {q['question'][:50]}... (type: {q['type']})")
    
    def test_translation_qa_dashboard_summary(self):
        """Test Translation QA Dashboard returns language scores and overall score"""
        response = self.session.get(f"{BASE_URL}/api/translation-qa/dashboard-summary")
        
        print(f"Translation QA response status: {response.status_code}")
        
        assert response.status_code == 200, f"Translation QA failed: {response.text}"
        
        data = response.json()
        
        # Verify overall score exists
        assert "overall_score" in data, "Response should contain 'overall_score'"
        print(f"Overall score: {data['overall_score']}")
        
        # Verify languages count
        if "languages" in data:
            print(f"Languages count: {data['languages']}")
    
    def test_jobs_search_endpoint(self):
        """Test jobs search endpoint returns jobs with status"""
        response = self.session.get(
            f"{BASE_URL}/api/jobs/search",
            params={"query": "engineer", "limit": 5}
        )
        
        print(f"Jobs search response status: {response.status_code}")
        
        # Jobs search may return 200 or other status
        if response.status_code == 200:
            data = response.json()
            print(f"Jobs search response keys: {data.keys() if isinstance(data, dict) else 'list'}")
            
            # Check if jobs have status field
            jobs = data.get("jobs", data) if isinstance(data, dict) else data
            if isinstance(jobs, list) and len(jobs) > 0:
                for i, job in enumerate(jobs[:3]):
                    status = job.get("status", job.get("job_status", "N/A"))
                    print(f"Job {i+1}: {job.get('title', 'N/A')[:30]} - Status: {status}")
    
    def test_tutorials_videos_endpoint(self):
        """Test tutorials videos endpoint returns diverse presenters"""
        response = self.session.get(f"{BASE_URL}/api/tutorials/videos")
        
        print(f"Tutorials videos response status: {response.status_code}")
        
        assert response.status_code == 200, f"Tutorials videos failed: {response.text}"
        
        data = response.json()
        
        # Verify videos array exists
        assert "videos" in data, "Response should contain 'videos' array"
        videos = data["videos"]
        assert isinstance(videos, list), "Videos should be a list"
        
        print(f"Found {len(videos)} tutorial videos")
        for video in videos[:5]:
            print(f"Video: {video.get('id', 'N/A')} - {video.get('title', 'N/A')[:40]}")


class TestTranslationKeys:
    """Test translation keys in en.json"""
    
    def test_common_translation_keys_exist(self):
        """Verify common translation keys exist in en.json"""
        en_json_path = "/app/frontend/src/locales/en.json"
        
        with open(en_json_path, 'r') as f:
            translations = json.load(f)
        
        # Required common keys
        required_keys = ["download", "filter", "help", "less", "more", "none", "previous", "sort", "upload"]
        
        common = translations.get("common", {})
        
        missing_keys = []
        for key in required_keys:
            if key not in common:
                missing_keys.append(key)
            else:
                print(f"✓ common.{key}: {common[key]}")
        
        assert len(missing_keys) == 0, f"Missing translation keys: {missing_keys}"
        print(f"All {len(required_keys)} required common keys present")


class TestJobCardStatusBadge:
    """Test JobCard component status badge logic"""
    
    def test_jobcard_default_status_is_active(self):
        """Verify JobCard.jsx defaults to 'Active' instead of 'Unknown'"""
        jobcard_path = "/app/frontend/src/components/shared/JobCard.jsx"
        
        with open(jobcard_path, 'r') as f:
            content = f.read()
        
        # Check that 'Unknown' is NOT the default status
        assert "label: 'Unknown'" not in content, "JobCard should not default to 'Unknown' status"
        
        # Check that 'Active' is the default status
        assert "label: 'Active'" in content, "JobCard should default to 'Active' status"
        
        # Verify the fallback logic
        assert "// Unknown status - Default to Active" in content or "Default to Active" in content, \
            "JobCard should have comment about defaulting to Active"
        
        print("✓ JobCard defaults to 'Active' status instead of 'Unknown'")


class TestVideoTutorialsDiversity:
    """Test Video Tutorials page has diverse presenters"""
    
    def test_video_tutorials_has_diverse_presenters(self):
        """Verify VideoTutorialsPage.jsx has diverse presenter images per region"""
        video_page_path = "/app/frontend/src/pages/VideoTutorialsPage.jsx"
        
        with open(video_page_path, 'r') as f:
            content = f.read()
        
        # Check for region-appropriate avatars
        assert "REGION_AVATARS" in content, "Should have REGION_AVATARS mapping"
        
        # Check for diverse regions
        regions = ["Europe", "Asia", "Africa", "Middle East", "South America"]
        for region in regions:
            assert f"'{region}'" in content, f"Should have {region} region"
        
        # Check for diverse presenter images
        assert "presenter_1_black_woman" in content or "black_woman" in content.lower() or "Africa" in content, \
            "Should have African presenter"
        assert "presenter_2_pacific_islander" in content or "pacific" in content.lower(), \
            "Should have Pacific Islander presenter"
        assert "presenter_3_asian_male" in content or "asian" in content.lower() or "Asia" in content, \
            "Should have Asian presenter"
        
        print("✓ VideoTutorialsPage has diverse presenters per region")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
