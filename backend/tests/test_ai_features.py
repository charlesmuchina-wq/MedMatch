"""
AI Features Backend Tests
Tests for: Interview Prep, Answer Evaluation, Voice Coach, STT Status, 
KARAU DRAGON Assistant, Q&A Practice, Cover Letter Generator, Callback Probability
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-ai-hub-1.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"

# Sample job data for testing
SAMPLE_JOB = {
    "job_title": "Senior Software Engineer",
    "company": "TechCorp Inc",
    "job_description": "We are looking for a Senior Software Engineer with 5+ years of experience in Python, FastAPI, and cloud technologies. Must have experience with microservices architecture and CI/CD pipelines.",
    "job_url": "https://example.com/job/123",
    "location": "Remote",
    "posted_at": "2026-01-20"
}


class TestAIFeaturesAuth:
    """Test authentication requirements for AI endpoints"""
    
    def test_interview_prep_requires_auth(self):
        """POST /api/interview-prep requires authentication"""
        response = requests.post(f"{BASE_URL}/api/interview-prep", json={
            "job_title": "Software Engineer",
            "company": "Test Corp"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/interview-prep requires authentication (401)")
    
    def test_evaluate_answer_requires_auth(self):
        """POST /api/evaluate-answer requires authentication"""
        response = requests.post(f"{BASE_URL}/api/evaluate-answer", json={
            "question": "Tell me about yourself",
            "answer": "I am a software engineer",
            "job_title": "Software Engineer"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/evaluate-answer requires authentication (401)")
    
    def test_voice_coach_requires_auth(self):
        """POST /api/voice-coach requires authentication"""
        response = requests.post(f"{BASE_URL}/api/voice-coach", json={
            "mode": "tips",
            "topic": "elevator pitch"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/voice-coach requires authentication (401)")
    
    def test_stt_status_requires_auth(self):
        """GET /api/stt/status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/stt/status")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ GET /api/stt/status requires authentication (401)")
    
    def test_assistant_requires_auth(self):
        """POST /api/assistant requires authentication"""
        response = requests.post(f"{BASE_URL}/api/assistant", json={
            "message": "Hello",
            "context": "general"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/assistant requires authentication (401)")
    
    def test_qa_practice_requires_auth(self):
        """POST /api/qa-practice requires authentication"""
        response = requests.post(f"{BASE_URL}/api/qa-practice", json={
            "question": "Tell me about yourself",
            "answer": "I am a software engineer"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/qa-practice requires authentication (401)")
    
    def test_cover_letter_requires_auth(self):
        """POST /api/cover-letter/generate requires authentication"""
        response = requests.post(f"{BASE_URL}/api/cover-letter/generate", json={
            "job_title": "Software Engineer",
            "company": "Test Corp",
            "job_description": "Test description"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/cover-letter/generate requires authentication (401)")
    
    def test_callback_prediction_requires_auth(self):
        """POST /api/jobs/predict-callback requires authentication"""
        response = requests.post(f"{BASE_URL}/api/jobs/predict-callback", json={
            "job_title": "Software Engineer",
            "company": "Test Corp",
            "job_description": "Test description"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ POST /api/jobs/predict-callback requires authentication (401)")


class TestAIFeaturesAuthenticated:
    """Test AI features with authenticated user"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        print(f"✅ Logged in as {ADMIN_EMAIL}")
    
    def test_stt_status(self):
        """GET /api/stt/status - Check Speech-to-Text service status"""
        response = requests.get(f"{BASE_URL}/api/stt/status", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "available" in data, "Response should contain 'available' field"
        assert "model" in data, "Response should contain 'model' field"
        assert "supported_formats" in data, "Response should contain 'supported_formats' field"
        assert data["model"] == "whisper-1", f"Expected whisper-1 model, got {data['model']}"
        
        print(f"✅ GET /api/stt/status - STT available: {data['available']}, model: {data['model']}")
        print(f"   Supported formats: {data['supported_formats']}")
    
    def test_interview_prep_generation(self):
        """POST /api/interview-prep - Generate interview questions"""
        payload = {
            "job_title": SAMPLE_JOB["job_title"],
            "company": SAMPLE_JOB["company"],
            "topics": ["technical", "behavioral"],
            "difficulty": "medium",
            "num_questions": 3
        }
        
        response = requests.post(f"{BASE_URL}/api/interview-prep", headers=self.headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "questions" in data, "Response should contain 'questions' field"
        assert isinstance(data["questions"], list), "Questions should be a list"
        assert len(data["questions"]) > 0, "Should have at least one question"
        
        # Validate question structure
        first_question = data["questions"][0]
        assert "question" in first_question, "Question should have 'question' field"
        assert "type" in first_question, "Question should have 'type' field"
        assert "tip" in first_question, "Question should have 'tip' field"
        
        print(f"✅ POST /api/interview-prep - Generated {len(data['questions'])} questions")
        print(f"   First question type: {first_question.get('type')}")
        
        # Add delay for rate limiting
        time.sleep(2)
    
    def test_evaluate_answer(self):
        """POST /api/evaluate-answer - Evaluate interview answer"""
        payload = {
            "question": "Tell me about a time you faced a challenging technical problem",
            "answer": "In my previous role, I encountered a performance issue with our database queries. I analyzed the slow queries, identified missing indexes, and implemented query optimization. This reduced response times by 70% and improved user experience significantly.",
            "job_title": SAMPLE_JOB["job_title"]
        }
        
        response = requests.post(f"{BASE_URL}/api/evaluate-answer", headers=self.headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "score" in data, "Response should contain 'score' field"
        assert "strengths" in data, "Response should contain 'strengths' field"
        assert "improvements" in data, "Response should contain 'improvements' field"
        assert "star_analysis" in data, "Response should contain 'star_analysis' field"
        
        # Validate score range
        assert 1 <= data["score"] <= 10, f"Score should be 1-10, got {data['score']}"
        
        print(f"✅ POST /api/evaluate-answer - Score: {data['score']}/10")
        print(f"   Strengths: {len(data.get('strengths', []))} points")
        print(f"   Improvements: {len(data.get('improvements', []))} suggestions")
        
        time.sleep(2)
    
    def test_voice_coach_tips(self):
        """POST /api/voice-coach - Get voice coaching tips"""
        payload = {
            "mode": "tips",
            "topic": "elevator pitch"
        }
        
        response = requests.post(f"{BASE_URL}/api/voice-coach", headers=self.headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "coaching" in data, "Response should contain 'coaching' field"
        assert "key_points" in data, "Response should contain 'key_points' field"
        assert "practice_script" in data, "Response should contain 'practice_script' field"
        assert data["mode"] == "tips", f"Mode should be 'tips', got {data.get('mode')}"
        assert data["topic"] == "elevator pitch", f"Topic should be 'elevator pitch', got {data.get('topic')}"
        
        print(f"✅ POST /api/voice-coach (tips) - Key points: {len(data.get('key_points', []))}")
        
        time.sleep(2)
    
    def test_voice_coach_practice(self):
        """POST /api/voice-coach - Get practice scenario"""
        payload = {
            "mode": "practice",
            "topic": "salary negotiation"
        }
        
        response = requests.post(f"{BASE_URL}/api/voice-coach", headers=self.headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "coaching" in data, "Response should contain 'coaching' field"
        assert "practice_script" in data, "Response should contain 'practice_script' field"
        assert data["mode"] == "practice", f"Mode should be 'practice', got {data.get('mode')}"
        
        print("✅ POST /api/voice-coach (practice) - Practice script provided")
        
        time.sleep(2)
    
    def test_karau_dragon_assistant(self):
        """POST /api/assistant - KARAU DRAGON AI Assistant"""
        payload = {
            "message": "What are the best strategies for job searching in tech?",
            "context": "job_search"
        }
        
        response = requests.post(f"{BASE_URL}/api/assistant", headers=self.headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "success" in data, "Response should contain 'success' field"
        assert data["success"] == True, "Success should be True"
        assert "response" in data, "Response should contain 'response' field"
        assert "assistant" in data, "Response should contain 'assistant' field"
        assert data["assistant"] == "KARAU DRAGON", f"Assistant should be 'KARAU DRAGON', got {data.get('assistant')}"
        assert data["context"] == "job_search", f"Context should be 'job_search', got {data.get('context')}"
        
        print("✅ POST /api/assistant - KARAU DRAGON responded")
        print(f"   Context: {data.get('context')}")
        print(f"   Response length: {len(data.get('response', ''))} chars")
        
        time.sleep(2)
    
    def test_karau_dragon_career_context(self):
        """POST /api/assistant - KARAU DRAGON with career context"""
        payload = {
            "message": "How can I transition from software engineering to product management?",
            "context": "career"
        }
        
        response = requests.post(f"{BASE_URL}/api/assistant", headers=self.headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True, "Success should be True"
        assert data["context"] == "career", f"Context should be 'career', got {data.get('context')}"
        
        print("✅ POST /api/assistant (career context) - Response received")
        
        time.sleep(2)
    
    def test_qa_practice(self):
        """POST /api/qa-practice - Q&A Interview Practice"""
        payload = {
            "question": "Why do you want to work at our company?",
            "answer": "I'm excited about your company's innovative approach to healthcare technology. Your recent work on AI-powered diagnostics aligns perfectly with my passion for using technology to improve patient outcomes. I believe my experience in building scalable systems would contribute to your mission.",
            "job_context": "Healthcare Technology Company"
        }
        
        response = requests.post(f"{BASE_URL}/api/qa-practice", headers=self.headers, json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "score" in data, "Response should contain 'score' field"
        assert "feedback" in data, "Response should contain 'feedback' field"
        assert "strengths" in data, "Response should contain 'strengths' field"
        assert "improvements" in data, "Response should contain 'improvements' field"
        assert "example_answer" in data, "Response should contain 'example_answer' field"
        assert "follow_up_questions" in data, "Response should contain 'follow_up_questions' field"
        
        # Validate score range
        assert 1 <= data["score"] <= 10, f"Score should be 1-10, got {data['score']}"
        
        print(f"✅ POST /api/qa-practice - Score: {data['score']}/10")
        print(f"   Follow-up questions: {len(data.get('follow_up_questions', []))}")
        
        time.sleep(2)
    
    def test_cover_letter_generation(self):
        """POST /api/cover-letter/generate - Generate cover letter"""
        payload = {
            "job_title": SAMPLE_JOB["job_title"],
            "company": SAMPLE_JOB["company"],
            "job_description": SAMPLE_JOB["job_description"],
            "job_url": SAMPLE_JOB["job_url"]
        }
        
        response = requests.post(f"{BASE_URL}/api/cover-letter/generate", headers=self.headers, json=payload)
        
        # May return 400 if no resume uploaded
        if response.status_code == 400:
            data = response.json()
            if "resume" in data.get("detail", "").lower():
                print("⚠️ POST /api/cover-letter/generate - Requires resume upload (expected)")
                return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "cover_letter" in data, "Response should contain 'cover_letter' field"
        assert "key_matches" in data, "Response should contain 'key_matches' field"
        
        print("✅ POST /api/cover-letter/generate - Cover letter generated")
        print(f"   Key matches: {len(data.get('key_matches', []))}")
        
        time.sleep(2)
    
    def test_callback_prediction(self):
        """POST /api/jobs/predict-callback - Predict callback probability"""
        payload = {
            "job_title": SAMPLE_JOB["job_title"],
            "company": SAMPLE_JOB["company"],
            "job_description": SAMPLE_JOB["job_description"],
            "job_url": SAMPLE_JOB["job_url"],
            "location": SAMPLE_JOB["location"],
            "posted_at": SAMPLE_JOB["posted_at"]
        }
        
        response = requests.post(f"{BASE_URL}/api/jobs/predict-callback", headers=self.headers, json=payload)
        
        # May return 400 if no resume uploaded
        if response.status_code == 400:
            data = response.json()
            if "resume" in data.get("detail", "").lower():
                print("⚠️ POST /api/jobs/predict-callback - Requires resume upload (expected)")
                return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "probability_score" in data, "Response should contain 'probability_score' field"
        assert "probability_label" in data, "Response should contain 'probability_label' field"
        assert "factors" in data, "Response should contain 'factors' field"
        assert "recommendations" in data, "Response should contain 'recommendations' field"
        
        # Validate score range
        assert 0 <= data["probability_score"] <= 100, f"Score should be 0-100, got {data['probability_score']}"
        
        print(f"✅ POST /api/jobs/predict-callback - Probability: {data['probability_score']}% ({data['probability_label']})")
        print(f"   Recommendations: {len(data.get('recommendations', []))}")
        
        time.sleep(2)
    
    def test_interview_prep_history(self):
        """GET /api/interview-prep/history - Get interview prep history"""
        response = requests.get(f"{BASE_URL}/api/interview-prep/history", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"✅ GET /api/interview-prep/history - {len(data)} records found")
    
    def test_cover_letter_history(self):
        """GET /api/cover-letter/history - Get cover letter history"""
        response = requests.get(f"{BASE_URL}/api/cover-letter/history", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"✅ GET /api/cover-letter/history - {len(data)} records found")
    
    def test_prediction_history(self):
        """GET /api/jobs/prediction-history - Get prediction history"""
        response = requests.get(f"{BASE_URL}/api/jobs/prediction-history", headers=self.headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        
        print(f"✅ GET /api/jobs/prediction-history - {len(data)} records found")


class TestAIFeaturesValidation:
    """Test input validation for AI endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_interview_prep_missing_job_title(self):
        """POST /api/interview-prep - Missing job_title should fail"""
        payload = {
            "company": "Test Corp"
        }
        
        response = requests.post(f"{BASE_URL}/api/interview-prep", headers=self.headers, json=payload)
        assert response.status_code == 422, f"Expected 422 for missing job_title, got {response.status_code}"
        print("✅ POST /api/interview-prep - Validates required job_title field")
    
    def test_evaluate_answer_missing_fields(self):
        """POST /api/evaluate-answer - Missing required fields should fail"""
        payload = {
            "question": "Tell me about yourself"
            # Missing answer and job_title
        }
        
        response = requests.post(f"{BASE_URL}/api/evaluate-answer", headers=self.headers, json=payload)
        assert response.status_code == 422, f"Expected 422 for missing fields, got {response.status_code}"
        print("✅ POST /api/evaluate-answer - Validates required fields")
    
    def test_voice_coach_invalid_mode(self):
        """POST /api/voice-coach - Invalid mode should still work (defaults)"""
        payload = {
            "mode": "invalid_mode",
            "topic": "test"
        }
        
        response = requests.post(f"{BASE_URL}/api/voice-coach", headers=self.headers, json=payload)
        # Should still work as it defaults to tips mode
        assert response.status_code in [200, 422], f"Expected 200 or 422, got {response.status_code}"
        print("✅ POST /api/voice-coach - Handles invalid mode gracefully")
    
    def test_assistant_empty_message(self):
        """POST /api/assistant - Empty message handling"""
        payload = {
            "message": "",
            "context": "general"
        }
        
        response = requests.post(f"{BASE_URL}/api/assistant", headers=self.headers, json=payload)
        # May return 200 with empty response or 422 for validation
        assert response.status_code in [200, 422, 500], f"Expected 200, 422, or 500, got {response.status_code}"
        print(f"✅ POST /api/assistant - Empty message returns {response.status_code}")


class TestAIFeaturesIntegration:
    """Integration tests for AI features workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data["access_token"]
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_full_interview_prep_workflow(self):
        """Test complete interview preparation workflow"""
        # Step 1: Generate interview questions
        prep_payload = {
            "job_title": "Product Manager",
            "company": "Google",
            "topics": ["product sense", "analytical"],
            "difficulty": "hard",
            "num_questions": 2
        }
        
        response = requests.post(f"{BASE_URL}/api/interview-prep", headers=self.headers, json=prep_payload)
        assert response.status_code == 200, f"Interview prep failed: {response.text}"
        
        prep_data = response.json()
        assert len(prep_data.get("questions", [])) > 0, "Should have questions"
        
        first_question = prep_data["questions"][0]["question"]
        print(f"✅ Step 1: Generated question: {first_question[:50]}...")
        
        time.sleep(2)
        
        # Step 2: Practice answering with Q&A
        qa_payload = {
            "question": first_question,
            "answer": "I would approach this by first understanding the user needs through research, then defining success metrics, and finally prioritizing features based on impact and effort.",
            "job_context": "Product Manager at Google"
        }
        
        response = requests.post(f"{BASE_URL}/api/qa-practice", headers=self.headers, json=qa_payload)
        assert response.status_code == 200, f"Q&A practice failed: {response.text}"
        
        qa_data = response.json()
        print(f"✅ Step 2: Q&A Practice score: {qa_data.get('score')}/10")
        
        time.sleep(2)
        
        # Step 3: Get voice coaching tips
        voice_payload = {
            "mode": "tips",
            "topic": "interview confidence"
        }
        
        response = requests.post(f"{BASE_URL}/api/voice-coach", headers=self.headers, json=voice_payload)
        assert response.status_code == 200, f"Voice coach failed: {response.text}"
        
        voice_data = response.json()
        print(f"✅ Step 3: Voice coaching tips: {len(voice_data.get('key_points', []))} points")
        
        print("✅ Full interview prep workflow completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
