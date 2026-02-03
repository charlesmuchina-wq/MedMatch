"""
Interview Prep Feature Tests
Tests for: AI Generate Questions, From Job Description, Paste Questions, AI Answer Generation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "MedMatch2026!"


class TestInterviewPrepEndpoints:
    """Test Interview Prep API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get auth token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("token") or data.get("access_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                print("Logged in successfully")
            else:
                # Try cookie-based auth
                print("Using cookie-based auth")
        else:
            pytest.skip(f"Authentication failed: {login_response.status_code}")
    
    def test_interview_prep_generate_questions(self):
        """Test /api/interview-prep endpoint - AI Generate Questions"""
        response = self.session.post(f"{BASE_URL}/api/interview-prep", json={
            "job_title": "Software Engineer",
            "company": "Google",
            "difficulty": "medium",
            "num_questions": 5,
            "topics": ["Python", "JavaScript", "React"]
        })
        
        print(f"Interview Prep Response Status: {response.status_code}")
        
        # Check status code
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        # Check response data
        data = response.json()
        assert "questions" in data, "Response should contain 'questions' field"
        assert len(data["questions"]) > 0, "Should generate at least one question"
        
        # Verify question structure
        first_question = data["questions"][0]
        assert "question" in first_question, "Question should have 'question' field"
        assert "type" in first_question, "Question should have 'type' field"
        
        print(f"Generated {len(data['questions'])} questions")
        print(f"First question: {first_question.get('question', '')[:100]}...")
    
    def test_interview_prep_with_job_description(self):
        """Test /api/interview-prep with job description context"""
        job_description = """
        We are looking for a Senior Software Engineer to join our team.
        Requirements:
        - 5+ years of experience in software development
        - Strong proficiency in Python, JavaScript, and React
        - Experience with cloud platforms (AWS, GCP)
        """
        
        response = self.session.post(f"{BASE_URL}/api/interview-prep", json={
            "job_title": "Senior Software Engineer",
            "company": "Tech Company",
            "difficulty": "hard",
            "num_questions": 5,
            "topics": ["Python", "AWS"],
            "job_description": job_description,
            "resume_skills": ["Python", "JavaScript", "React", "AWS"]
        })
        
        print(f"Interview Prep with JD Response Status: {response.status_code}")
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert "questions" in data, "Response should contain 'questions' field"
        print(f"Generated {len(data.get('questions', []))} questions from JD")
    
    def test_assistant_endpoint_for_answer_generation(self):
        """Test /api/assistant endpoint - AI Answer Generation"""
        response = self.session.post(f"{BASE_URL}/api/assistant", json={
            "message": "Generate a strong interview answer for: Tell me about a time you led a cross-functional team. The position is Product Manager at Amazon.",
            "context": "interview"
        })
        
        print(f"Assistant Response Status: {response.status_code}")
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert "response" in data, "Response should contain 'response' field"
        assert len(data["response"]) > 50, "Answer should be substantial"
        
        print(f"Generated answer length: {len(data['response'])} characters")
    
    def test_qa_practice_endpoint(self):
        """Test /api/qa-practice endpoint - Mock Interview Feedback"""
        response = self.session.post(f"{BASE_URL}/api/qa-practice", json={
            "question": "Tell me about a time you faced a challenging technical problem.",
            "answer": "In my previous role, I encountered a performance issue with our database queries. I analyzed the slow queries, identified missing indexes, and implemented query optimization. This reduced response times by 60%.",
            "job_context": "Software Engineer at Google"
        })
        
        print(f"QA Practice Response Status: {response.status_code}")
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert "score" in data, "Response should contain 'score' field"
        assert "feedback" in data, "Response should contain 'feedback' field"
        
        print(f"Score: {data.get('score')}/10")
        print(f"Feedback: {data.get('feedback', '')[:100]}...")
    
    def test_export_interview_prep_html(self):
        """Test /api/export/interview-prep-html endpoint - PDF Export"""
        response = self.session.post(f"{BASE_URL}/api/export/interview-prep-html", json={
            "job_title": "Software Engineer",
            "company": "Google",
            "questions": {
                "behavioral": [
                    {"question": "Tell me about yourself", "tip": "Keep it professional"}
                ],
                "technical": [
                    {"question": "Explain REST APIs", "tip": "Be specific"}
                ]
            },
            "applicant_name": "Test User"
        })
        
        print(f"Export HTML Response Status: {response.status_code}")
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert "html" in data, "Response should contain 'html' field"
        assert "Interview Preparation" in data["html"], "HTML should contain title"
        
        print("PDF export HTML generated successfully")
    
    def test_interview_prep_history(self):
        """Test /api/interview-prep/history endpoint"""
        response = self.session.get(f"{BASE_URL}/api/interview-prep/history")
        
        print(f"Interview Prep History Response Status: {response.status_code}")
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"Found {len(data)} interview prep history items")


class TestCompanyResearch:
    """Test Company Research functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("token") or data.get("access_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_company_research_via_assistant(self):
        """Test company research using /api/assistant endpoint"""
        response = self.session.post(f"{BASE_URL}/api/assistant", json={
            "message": "Provide interview preparation research for Google. Include: company culture, recent news, interview tips, common interview questions, and what they look for in candidates.",
            "context": "career"
        })
        
        print(f"Company Research Response Status: {response.status_code}")
        
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        
        data = response.json()
        assert "response" in data, "Response should contain 'response' field"
        assert len(data["response"]) > 100, "Research should be substantial"
        
        print(f"Company research length: {len(data['response'])} characters")


class TestAuthenticationRequired:
    """Test that endpoints require authentication"""
    
    def test_interview_prep_requires_auth(self):
        """Test that /api/interview-prep requires authentication"""
        response = requests.post(f"{BASE_URL}/api/interview-prep", json={
            "job_title": "Test",
            "company": "Test"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Interview prep endpoint correctly requires authentication")
    
    def test_assistant_requires_auth(self):
        """Test that /api/assistant requires authentication"""
        response = requests.post(f"{BASE_URL}/api/assistant", json={
            "message": "Test",
            "context": "general"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("Assistant endpoint correctly requires authentication")
    
    def test_qa_practice_requires_auth(self):
        """Test that /api/qa-practice requires authentication"""
        response = requests.post(f"{BASE_URL}/api/qa-practice", json={
            "question": "Test",
            "answer": "Test"
        })
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("QA practice endpoint correctly requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
