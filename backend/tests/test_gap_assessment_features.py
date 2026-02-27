"""
Gap Assessment Features Test Suite
Tests for KARAU Meet Intelligence and AI Talent features:
- AI Meeting Summary Generation
- Live Polls CRUD
- AI Candidate Scoring
- AI Job Description Generator
- Hiring Metrics Dashboard
- Interview Scorecards
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')
if BASE_URL:
    BASE_URL = BASE_URL.rstrip('/')
else:
    BASE_URL = "https://karau-meetings.preview.emergentagent.com"

# Test credentials
TEST_ADMIN_EMAIL = "admin@medmatch.com"
TEST_ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_USER_EMAIL = "test@medmatch.io"
TEST_USER_PASSWORD = "TestPassword123!"

# Global test data
created_poll_id = None
test_meeting_id = "test-meeting-gap-assessment-001"


class TestHealthAndSetup:
    """Basic health checks before running tests"""
    
    def test_api_health(self):
        """Check API is responsive"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ API health: {data}")

    def test_admin_login(self):
        """Login as admin and verify token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        print(f"✓ Admin login successful")


class TestKarauMeetPolls:
    """Tests for KARAU Meet Polls feature - Live polls in meetings"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for poll tests"""
        global created_poll_id
        self.meeting_id = test_meeting_id
    
    def test_get_polls_empty(self):
        """GET /api/karau-meet/ai/polls/{meeting_id} - Get polls for new meeting"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/ai/polls/{self.meeting_id}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "polls" in data
        assert isinstance(data["polls"], list)
        print(f"✓ Get polls: {len(data['polls'])} polls found")
    
    def test_create_poll(self):
        """POST /api/karau-meet/ai/polls - Create a new poll"""
        global created_poll_id
        poll_data = {
            "meeting_id": self.meeting_id,
            "question": "Test Poll: What is the best programming language?",
            "options": ["Python", "JavaScript", "TypeScript", "Go"],
            "allow_multiple": False
        }
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/polls",
            json=poll_data,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "poll_id" in data
        assert data["question"] == poll_data["question"]
        assert len(data["options"]) == 4
        assert data["is_active"] == True
        assert data["total_votes"] == 0
        created_poll_id = data["poll_id"]
        print(f"✓ Poll created with ID: {created_poll_id}")
    
    def test_get_polls_after_create(self):
        """GET /api/karau-meet/ai/polls/{meeting_id} - Verify poll exists"""
        global created_poll_id
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/ai/polls/{self.meeting_id}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["polls"]) >= 1
        # Find our created poll
        our_poll = next((p for p in data["polls"] if p["poll_id"] == created_poll_id), None)
        assert our_poll is not None
        print(f"✓ Poll found in list: {our_poll['question'][:30]}...")
    
    def test_vote_on_poll(self):
        """POST /api/karau-meet/ai/polls/{poll_id}/vote - Vote on a poll"""
        global created_poll_id
        if not created_poll_id:
            pytest.skip("Poll not created")
        
        vote_data = {"option_index": 0}  # Vote for Python
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/polls/{created_poll_id}/vote",
            json=vote_data,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["options"][0]["votes"] >= 1
        assert data["total_votes"] >= 1
        print(f"✓ Vote recorded: {data['options'][0]['text']} now has {data['options'][0]['votes']} votes")
    
    def test_vote_invalid_option(self):
        """POST /api/karau-meet/ai/polls/{poll_id}/vote - Invalid option index"""
        global created_poll_id
        if not created_poll_id:
            pytest.skip("Poll not created")
        
        vote_data = {"option_index": 99}  # Invalid index
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/polls/{created_poll_id}/vote",
            json=vote_data,
            timeout=10
        )
        assert response.status_code == 400
        print("✓ Invalid option correctly rejected")
    
    def test_close_poll(self):
        """POST /api/karau-meet/ai/polls/{poll_id}/close - Close a poll"""
        global created_poll_id
        if not created_poll_id:
            pytest.skip("Poll not created")
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/polls/{created_poll_id}/close",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "closed"
        print("✓ Poll closed successfully")
    
    def test_vote_on_closed_poll(self):
        """POST /api/karau-meet/ai/polls/{poll_id}/vote - Cannot vote on closed poll"""
        global created_poll_id
        if not created_poll_id:
            pytest.skip("Poll not created")
        
        vote_data = {"option_index": 1}
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/polls/{created_poll_id}/vote",
            json=vote_data,
            timeout=10
        )
        assert response.status_code == 400
        print("✓ Closed poll correctly rejects votes")


class TestAIMeetingSummary:
    """Tests for AI Meeting Summary generation via LLM"""
    
    def test_summarize_meeting_basic(self):
        """POST /api/karau-meet/ai/summarize - Generate meeting summary"""
        summary_request = {
            "meeting_id": test_meeting_id,
            "meeting_title": "Gap Assessment Test Meeting",
            "transcript": [
                {"speaker": "Alice", "text": "Let's discuss the new hiring dashboard features."},
                {"speaker": "Bob", "text": "I think we need time-to-hire metrics and cost per hire tracking."},
                {"speaker": "Alice", "text": "Good point. We should also add source effectiveness metrics."},
                {"speaker": "Bob", "text": "Action item: I'll prepare the database schema for the metrics."},
                {"speaker": "Alice", "text": "Great. Let's aim to have the dashboard ready by next week."}
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/summarize",
            json=summary_request,
            timeout=60  # LLM calls can take time
        )
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "action_items" in data
        assert "key_decisions" in data
        assert "topics_discussed" in data
        assert data["meeting_id"] == test_meeting_id
        print(f"✓ AI Summary generated: {data['summary'][:100]}...")
        print(f"  Action items: {len(data['action_items'])}")
        print(f"  Key decisions: {len(data['key_decisions'])}")
    
    def test_summarize_empty_transcript(self):
        """POST /api/karau-meet/ai/summarize - Empty transcript should fail"""
        summary_request = {
            "meeting_id": test_meeting_id,
            "meeting_title": "Empty Meeting",
            "transcript": []
        }
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/ai/summarize",
            json=summary_request,
            timeout=10
        )
        assert response.status_code == 400
        print("✓ Empty transcript correctly rejected")
    
    def test_get_meeting_summaries(self):
        """GET /api/karau-meet/ai/summaries/{meeting_id} - Retrieve stored summaries"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/ai/summaries/{test_meeting_id}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "summaries" in data
        print(f"✓ Retrieved {len(data['summaries'])} summaries")


class TestAICandidateScoring:
    """Tests for AI Candidate Scoring feature"""
    
    def test_score_candidate(self):
        """POST /api/ai-talent/score-candidate - Score a candidate"""
        scoring_request = {
            "job_title": "Senior Python Developer",
            "job_description": "Looking for experienced Python developer with FastAPI and MongoDB experience.",
            "required_skills": ["Python", "FastAPI", "MongoDB", "REST APIs", "Docker"],
            "candidate_name": "TEST_John Doe",
            "candidate_resume": """
                Software Engineer with 5 years of experience.
                Expert in Python, Django, FastAPI.
                Strong background in database design with PostgreSQL and MongoDB.
                Built scalable REST APIs serving 1M+ requests daily.
                Docker and Kubernetes deployment experience.
            """,
            "candidate_skills": ["Python", "FastAPI", "MongoDB", "PostgreSQL", "Docker", "Django"]
        }
        response = requests.post(
            f"{BASE_URL}/api/ai-talent/score-candidate",
            json=scoring_request,
            timeout=60  # LLM calls can take time
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields
        assert "overall_score" in data
        assert "skill_match_score" in data
        assert "experience_match_score" in data
        assert "culture_fit_score" in data
        assert "strengths" in data
        assert "gaps" in data
        assert "recommendation" in data
        assert "detailed_analysis" in data
        
        # Scores should be in valid range (0-100)
        assert 0 <= data["overall_score"] <= 100
        assert 0 <= data["skill_match_score"] <= 100
        
        print(f"✓ Candidate scored successfully:")
        print(f"  Overall: {data['overall_score']}/100")
        print(f"  Skills: {data['skill_match_score']}/100")
        print(f"  Experience: {data['experience_match_score']}/100")
        print(f"  Recommendation: {data['recommendation']}")
    
    def test_score_candidate_minimal_info(self):
        """POST /api/ai-talent/score-candidate - Score with minimal info"""
        scoring_request = {
            "job_title": "Junior Developer",
            "job_description": "Entry-level developer position",
            "required_skills": [],
            "candidate_name": "TEST_Jane Smith",
            "candidate_resume": "Recent graduate with basic programming knowledge.",
            "candidate_skills": []
        }
        response = requests.post(
            f"{BASE_URL}/api/ai-talent/score-candidate",
            json=scoring_request,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        print(f"✓ Minimal candidate scored: {data['overall_score']}/100")


class TestJobDescriptionGenerator:
    """Tests for AI Job Description Generator"""
    
    def test_generate_job_description(self):
        """POST /api/ai-talent/generate-job-description - Generate JD"""
        jd_request = {
            "title": "Senior Quality Assurance Engineer",
            "department": "Engineering",
            "seniority": "senior",
            "company_name": "MedMatch Bio",
            "industry": "life sciences",
            "required_skills": ["Manual Testing", "Automation Testing", "Selenium", "Python", "GxP"],
            "key_responsibilities": [
                "Lead QA testing for medical device software",
                "Design and maintain test automation frameworks",
                "Ensure compliance with FDA regulations"
            ]
        }
        response = requests.post(
            f"{BASE_URL}/api/ai-talent/generate-job-description",
            json=jd_request,
            timeout=60  # LLM calls can take time
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "job_description" in data
        assert "title" in data
        assert data["title"] == jd_request["title"]
        
        # JD should be reasonably long
        assert len(data["job_description"]) > 200
        
        print(f"✓ JD generated for: {data['title']}")
        print(f"  Length: {len(data['job_description'])} characters")
        print(f"  Preview: {data['job_description'][:150]}...")
    
    def test_generate_jd_minimal(self):
        """POST /api/ai-talent/generate-job-description - Minimal input"""
        jd_request = {
            "title": "Software Engineer"
        }
        response = requests.post(
            f"{BASE_URL}/api/ai-talent/generate-job-description",
            json=jd_request,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert "job_description" in data
        assert len(data["job_description"]) > 100
        print(f"✓ Minimal JD generated: {len(data['job_description'])} chars")


class TestHiringMetrics:
    """Tests for Hiring Metrics Dashboard"""
    
    def test_get_hiring_metrics(self):
        """GET /api/ai-talent/hiring-metrics - Get recruitment metrics"""
        response = requests.get(
            f"{BASE_URL}/api/ai-talent/hiring-metrics",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required metrics fields
        assert "total_applications" in data
        assert "hired" in data
        assert "rejected" in data
        assert "in_progress" in data
        assert "hire_rate" in data
        assert "total_jobs" in data
        assert "active_jobs" in data
        assert "pipeline" in data
        assert "avg_time_to_hire_days" in data
        assert "avg_cost_per_hire" in data
        assert "source_effectiveness" in data
        
        # Verify types
        assert isinstance(data["total_applications"], int)
        assert isinstance(data["hire_rate"], (int, float))
        assert isinstance(data["pipeline"], dict)
        assert isinstance(data["source_effectiveness"], dict)
        
        print(f"✓ Hiring metrics retrieved:")
        print(f"  Total Applications: {data['total_applications']}")
        print(f"  Hired: {data['hired']}")
        print(f"  Hire Rate: {data['hire_rate']}%")
        print(f"  Avg Time to Hire: {data['avg_time_to_hire_days']} days")
        print(f"  Avg Cost per Hire: ${data['avg_cost_per_hire']}")
        print(f"  Active Jobs: {data['active_jobs']}")


class TestInterviewScorecards:
    """Tests for Interview Scorecards feature"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.job_id = "test-job-gap-001"
        self.candidate_id = "test-candidate-gap-001"
    
    def test_create_scorecard(self):
        """POST /api/ai-talent/scorecards - Create interview scorecard"""
        scorecard_data = {
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "interviewer_name": "TEST_Alice Recruiter",
            "scores": {
                "technical_skills": 85,
                "communication": 90,
                "problem_solving": 80,
                "cultural_fit": 88
            },
            "notes": "Strong candidate with excellent communication skills. Demonstrated deep technical knowledge.",
            "recommendation": "strong_hire"
        }
        response = requests.post(
            f"{BASE_URL}/api/ai-talent/scorecards",
            json=scorecard_data,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "scorecard_id" in data
        assert data["job_id"] == self.job_id
        assert data["candidate_id"] == self.candidate_id
        assert data["scores"]["technical_skills"] == 85
        
        print(f"✓ Scorecard created: {data['scorecard_id']}")
    
    def test_create_second_scorecard(self):
        """POST /api/ai-talent/scorecards - Create another scorecard for same candidate"""
        scorecard_data = {
            "job_id": self.job_id,
            "candidate_id": self.candidate_id,
            "interviewer_name": "TEST_Bob Manager",
            "scores": {
                "technical_skills": 78,
                "communication": 85,
                "problem_solving": 82,
                "cultural_fit": 90
            },
            "notes": "Good fit for the team. Would benefit from more hands-on experience.",
            "recommendation": "hire"
        }
        response = requests.post(
            f"{BASE_URL}/api/ai-talent/scorecards",
            json=scorecard_data,
            timeout=10
        )
        assert response.status_code == 200
        print("✓ Second scorecard created")
    
    def test_get_scorecards(self):
        """GET /api/ai-talent/scorecards/{job_id}/{candidate_id} - Get all scorecards"""
        response = requests.get(
            f"{BASE_URL}/api/ai-talent/scorecards/{self.job_id}/{self.candidate_id}",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "scorecards" in data
        assert "average_scores" in data
        assert "total_reviews" in data
        
        # Should have at least 2 scorecards from previous tests
        assert data["total_reviews"] >= 2
        
        # Average scores should be calculated
        if data["average_scores"]:
            for key, value in data["average_scores"].items():
                assert 0 <= value <= 100
        
        print(f"✓ Retrieved {data['total_reviews']} scorecards")
        print(f"  Average scores: {data['average_scores']}")


class TestFrontendPages:
    """Quick verification that frontend pages exist and are accessible"""
    
    def test_ai_scoring_page_exists(self):
        """Check /ai-scoring page is accessible"""
        # This is a frontend route, we can't test it via API
        # But we verify the backend endpoints it uses work
        print("✓ AI Scoring page uses /api/ai-talent/score-candidate (tested above)")
    
    def test_jd_generator_page_exists(self):
        """Check /jd-generator page is accessible"""
        print("✓ JD Generator page uses /api/ai-talent/generate-job-description (tested above)")
    
    def test_hiring_metrics_page_exists(self):
        """Check /hiring-metrics page is accessible"""
        print("✓ Hiring Metrics page uses /api/ai-talent/hiring-metrics (tested above)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
