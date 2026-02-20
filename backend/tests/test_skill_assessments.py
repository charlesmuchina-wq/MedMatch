"""
Skill Assessments API Tests
Tests: Available assessments, Start assessment, Submit assessment, Badges
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestSkillAssessmentsAPI:
    """Test Skill Assessment endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_session(self):
        """Get authenticated session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Login
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            if token:
                session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip(f"Authentication failed: {response.status_code}")
        
        return session

    def test_get_available_assessments(self, auth_session):
        """Test GET /api/skills/available - Get list of all available assessments"""
        response = auth_session.get(f"{BASE_URL}/api/skills/available")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "assessments" in data, "Response should contain 'assessments' key"
        assert "by_category" in data, "Response should contain 'by_category' key"
        
        # Verify assessments structure
        if data["assessments"]:
            assessment = data["assessments"][0]
            assert "skill_name" in assessment
            assert "category" in assessment
            assert "questions" in assessment
            assert "time_limit" in assessment
            assert "passing_score" in assessment
            assert "badge_icon" in assessment
            assert "badge_color" in assessment
        
        # Verify categories structure
        categories = data["by_category"]
        assert len(categories) > 0, "Should have at least one category"
        
        print(f"Available assessments: {len(data['assessments'])}")
        print(f"Categories: {list(categories.keys())}")

    def test_get_skill_categories(self, auth_session):
        """Test GET /api/skills/categories - Get skill categories"""
        response = auth_session.get(f"{BASE_URL}/api/skills/categories")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "categories" in data
        assert "total_categories" in data
        assert data["total_categories"] > 0
        
        print(f"Total categories: {data['total_categories']}")

    def test_get_my_badges(self, auth_session):
        """Test GET /api/skills/my-badges - Get user's earned badges"""
        response = auth_session.get(f"{BASE_URL}/api/skills/my-badges")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "badges" in data
        assert "total" in data
        
        print(f"User has {data['total']} badges")

    def test_start_assessment(self, auth_session):
        """Test POST /api/skills/start - Start a skill assessment
        
        NOTE: This endpoint generates AI questions which takes 20-40 seconds.
        The fix being tested is that loading feedback is shown during this time.
        """
        # Use Python skill for testing as it's a common one
        skill_name = "Python"
        
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={
                "skill_name": skill_name,
                "difficulty": "intermediate"
            },
            timeout=60  # Long timeout for AI generation
        )
        
        # Could be 200 (success) or 400 (cooldown period)
        if response.status_code == 400:
            data = response.json()
            if "24 hours" in str(data.get("detail", "")):
                pytest.skip("Assessment on cooldown - recently failed")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "assessment_id" in data, "Should return assessment_id"
        assert "skill_name" in data, "Should return skill_name"
        assert "questions" in data, "Should return questions"
        assert "time_limit" in data, "Should return time_limit"
        assert "total_questions" in data, "Should return total_questions"
        
        # Verify questions structure (should not include answers)
        questions = data["questions"]
        assert len(questions) > 0, "Should have at least one question"
        
        for q in questions:
            assert "index" in q, "Question should have index"
            assert "question" in q, "Question should have question text"
            assert "options" in q, "Question should have options"
            assert "correct_answer" not in q, "Question should NOT expose correct answer"
        
        print(f"Assessment started: {data['assessment_id']}")
        print(f"Total questions: {data['total_questions']}")
        print(f"Time limit: {data['time_limit']} minutes")
        
        # Store assessment_id for submit test
        auth_session.assessment_id = data["assessment_id"]
        auth_session.questions = data["questions"]
        return data

    def test_submit_assessment(self, auth_session):
        """Test POST /api/skills/submit - Submit completed assessment"""
        # Need to have started an assessment first
        if not hasattr(auth_session, 'assessment_id'):
            # Start an assessment first
            start_response = auth_session.post(
                f"{BASE_URL}/api/skills/start",
                json={"skill_name": "Communication", "difficulty": "beginner"},
                timeout=60
            )
            
            if start_response.status_code == 400:
                pytest.skip("Cannot start assessment - on cooldown")
            
            if start_response.status_code != 200:
                pytest.skip("Could not start assessment for submit test")
            
            data = start_response.json()
            auth_session.assessment_id = data["assessment_id"]
            auth_session.questions = data["questions"]
        
        # Submit answers (answer first option for all questions)
        answers = []
        for q in auth_session.questions:
            answers.append({
                "question_index": q["index"],
                "answer": q["options"][0]  # Select first option
            })
        
        response = auth_session.post(
            f"{BASE_URL}/api/skills/submit",
            json={
                "assessment_id": auth_session.assessment_id,
                "answers": answers
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "passed" in data, "Should return passed status"
        assert "score" in data, "Should return score"
        assert "correct_count" in data, "Should return correct_count"
        assert "total_questions" in data, "Should return total_questions"
        assert "passing_score" in data, "Should return passing_score"
        assert "message" in data, "Should return message"
        
        print(f"Assessment result: {'PASSED' if data['passed'] else 'FAILED'}")
        print(f"Score: {data['score']}%")
        print(f"Correct: {data['correct_count']}/{data['total_questions']}")

    def test_get_assessment_history(self, auth_session):
        """Test GET /api/skills/history - Get user's assessment history"""
        response = auth_session.get(f"{BASE_URL}/api/skills/history")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "history" in data
        
        print(f"Assessment history entries: {len(data['history'])}")

    def test_get_skill_leaderboard(self, auth_session):
        """Test GET /api/skills/leaderboard/{skill_name} - Get leaderboard"""
        response = auth_session.get(f"{BASE_URL}/api/skills/leaderboard/Python")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "skill_name" in data
        assert "leaderboard" in data
        
        print(f"Leaderboard for Python: {len(data['leaderboard'])} entries")

    def test_verify_badge_endpoint(self, auth_session):
        """Test GET /api/skills/verify/{user_id}/{skill_name} - Public verification"""
        # This is a public endpoint - test with a non-existent user
        response = auth_session.get(f"{BASE_URL}/api/skills/verify/test_user_123/Python")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Should return verified: false for non-existent badge
        assert "verified" in data

    def test_start_invalid_skill(self, auth_session):
        """Test POST /api/skills/start with invalid skill name"""
        response = auth_session.post(
            f"{BASE_URL}/api/skills/start",
            json={
                "skill_name": "NonExistentSkill123",
                "difficulty": "intermediate"
            }
        )
        
        assert response.status_code == 400, f"Expected 400 for invalid skill, got {response.status_code}"
        
        data = response.json()
        assert "Assessment not available" in str(data.get("detail", ""))

    def test_submit_invalid_assessment(self, auth_session):
        """Test POST /api/skills/submit with invalid assessment ID"""
        response = auth_session.post(
            f"{BASE_URL}/api/skills/submit",
            json={
                "assessment_id": "invalid_assessment_id_123",
                "answers": []
            }
        )
        
        assert response.status_code == 404, f"Expected 404 for invalid assessment, got {response.status_code}"

    def test_unauthenticated_access(self):
        """Test that protected endpoints require authentication"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Test my-badges without auth
        response = session.get(f"{BASE_URL}/api/skills/my-badges")
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        
        # Test start without auth
        response = session.post(
            f"{BASE_URL}/api/skills/start",
            json={"skill_name": "Python", "difficulty": "intermediate"}
        )
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
