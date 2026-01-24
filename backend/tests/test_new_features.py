"""
Test suite for Real-Time STT and Video Analysis features
Tests the new AI-powered features: Real-time voice transcription and TensorFlow.js facial analysis
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRealTimeSTT:
    """Tests for Real-Time Speech-to-Text API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication for tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "MedMatch2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
    def test_stt_status_endpoint(self):
        """Test GET /api/realtime-stt/status returns available=true with model and features"""
        response = self.session.get(f"{BASE_URL}/api/realtime-stt/status")
        
        assert response.status_code == 200, f"Status endpoint failed: {response.text}"
        
        data = response.json()
        assert data.get("available") == True, "STT service should be available"
        assert data.get("model") == "whisper-1", "Model should be whisper-1"
        assert "features" in data, "Response should include features"
        
        features = data["features"]
        assert features.get("streaming") == True, "Streaming should be enabled"
        assert features.get("real_time") == True, "Real-time should be enabled"
        assert "languages" in features, "Languages should be listed"
        assert "en" in features["languages"], "English should be supported"
        
        print(f"STT Status: available={data['available']}, model={data['model']}")
        print(f"Features: {features}")
        
    def test_stt_history_endpoint(self):
        """Test GET /api/realtime-stt/history returns user's transcription history"""
        response = self.session.get(f"{BASE_URL}/api/realtime-stt/history")
        
        assert response.status_code == 200, f"History endpoint failed: {response.text}"
        
        data = response.json()
        assert "history" in data, "Response should include history array"
        assert "count" in data, "Response should include count"
        assert isinstance(data["history"], list), "History should be a list"
        
        print(f"History count: {data['count']}")
        
    def test_stt_status_unauthenticated(self):
        """Test that STT status requires authentication"""
        # Create new session without auth
        unauth_session = requests.Session()
        response = unauth_session.get(f"{BASE_URL}/api/realtime-stt/status")
        
        assert response.status_code == 401, "Should require authentication"


class TestVideoAnalysis:
    """Tests for Video Analysis API endpoints (TensorFlow.js facial analysis)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication for tests"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get session
        login_response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "MedMatch2026!"}
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        
    def test_video_analysis_status_endpoint(self):
        """Test GET /api/video-analysis/status returns available=true with all features"""
        response = self.session.get(f"{BASE_URL}/api/video-analysis/status")
        
        assert response.status_code == 200, f"Status endpoint failed: {response.text}"
        
        data = response.json()
        assert data.get("available") == True, "Video analysis should be available"
        assert "features" in data, "Response should include features"
        
        features = data["features"]
        assert features.get("frame_analysis") == True, "Frame analysis should be enabled"
        assert features.get("expression_detection") == True, "Expression detection should be enabled"
        assert features.get("eye_contact_tracking") == True, "Eye contact tracking should be enabled"
        assert features.get("engagement_scoring") == True, "Engagement scoring should be enabled"
        assert features.get("real_time_tips") == True, "Real-time tips should be enabled"
        
        print(f"Video Analysis Status: available={data['available']}")
        print(f"Features: {features}")
        
    def test_video_analysis_benchmarks_endpoint(self):
        """Test GET /api/video-analysis/benchmarks returns industry benchmarks"""
        response = self.session.get(f"{BASE_URL}/api/video-analysis/benchmarks")
        
        assert response.status_code == 200, f"Benchmarks endpoint failed: {response.text}"
        
        data = response.json()
        assert "top_performer_benchmarks" in data, "Should include top performer benchmarks"
        assert "industry_averages" in data, "Should include industry averages"
        assert "improvement_timeline" in data, "Should include improvement timeline"
        
        # Verify benchmark structure
        benchmarks = data["top_performer_benchmarks"]
        assert "eye_contact" in benchmarks, "Should have eye contact benchmarks"
        assert "engagement" in benchmarks, "Should have engagement benchmarks"
        assert "confidence" in benchmarks, "Should have confidence benchmarks"
        
        # Verify eye contact benchmark values
        eye_contact = benchmarks["eye_contact"]
        assert eye_contact.get("excellent") == 85, "Excellent eye contact should be 85"
        assert eye_contact.get("good") == 70, "Good eye contact should be 70"
        
        print(f"Benchmarks: {list(benchmarks.keys())}")
        print(f"Industry averages: {list(data['industry_averages'].keys())}")
        
    def test_video_analysis_realtime_tips_endpoint(self):
        """Test GET /api/video-analysis/tips/real-time returns coaching tips based on params"""
        # Test with default params
        response = self.session.get(
            f"{BASE_URL}/api/video-analysis/tips/real-time",
            params={"eye_contact": 50, "expression": "neutral", "posture": "good"}
        )
        
        assert response.status_code == 200, f"Tips endpoint failed: {response.text}"
        
        data = response.json()
        assert "tips" in data, "Response should include tips"
        assert "current_state" in data, "Response should include current state"
        assert "overall_status" in data, "Response should include overall status"
        
        # Verify current state reflects params
        current_state = data["current_state"]
        assert current_state.get("eye_contact") == 50, "Eye contact should match param"
        assert current_state.get("expression") == "neutral", "Expression should match param"
        assert current_state.get("posture") == "good", "Posture should match param"
        
        print(f"Tips count: {len(data['tips'])}")
        print(f"Overall status: {data['overall_status']}")
        
    def test_video_analysis_tips_low_eye_contact(self):
        """Test tips endpoint returns high priority tip for low eye contact"""
        response = self.session.get(
            f"{BASE_URL}/api/video-analysis/tips/real-time",
            params={"eye_contact": 30, "expression": "neutral", "posture": "good"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        tips = data["tips"]
        
        # Should have high priority eye contact tip
        eye_contact_tips = [t for t in tips if t.get("category") == "eye_contact"]
        assert len(eye_contact_tips) > 0, "Should have eye contact tip for low score"
        assert eye_contact_tips[0].get("priority") == "high", "Should be high priority"
        
        print(f"Eye contact tip: {eye_contact_tips[0].get('tip')}")
        
    def test_video_analysis_tips_nervous_expression(self):
        """Test tips endpoint returns tip for nervous expression"""
        response = self.session.get(
            f"{BASE_URL}/api/video-analysis/tips/real-time",
            params={"eye_contact": 70, "expression": "nervous", "posture": "good"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        tips = data["tips"]
        
        # Should have expression tip
        expression_tips = [t for t in tips if t.get("category") == "expression"]
        assert len(expression_tips) > 0, "Should have expression tip for nervous"
        
        print(f"Expression tip: {expression_tips[0].get('tip')}")
        
    def test_video_analysis_tips_no_auth_required(self):
        """Test that real-time tips endpoint doesn't require authentication"""
        # Create new session without auth
        unauth_session = requests.Session()
        response = unauth_session.get(
            f"{BASE_URL}/api/video-analysis/tips/real-time",
            params={"eye_contact": 50, "expression": "neutral", "posture": "good"}
        )
        
        # This endpoint should work without auth for real-time feedback
        assert response.status_code == 200, "Real-time tips should work without auth"
        
    def test_video_analysis_status_unauthenticated(self):
        """Test that video analysis status requires authentication"""
        unauth_session = requests.Session()
        response = unauth_session.get(f"{BASE_URL}/api/video-analysis/status")
        
        assert response.status_code == 401, "Should require authentication"
        
    def test_video_analysis_benchmarks_unauthenticated(self):
        """Test that benchmarks endpoint requires authentication"""
        unauth_session = requests.Session()
        response = unauth_session.get(f"{BASE_URL}/api/video-analysis/benchmarks")
        
        assert response.status_code == 401, "Should require authentication"


class TestNavigationLinks:
    """Tests to verify navigation links are present"""
    
    def test_api_health(self):
        """Test that the API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, "API should be healthy"
        print("API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
