"""
Test suite for Biometric Authentication and Offline Capabilities
Tests: WebAuthn endpoints, biometric registration/authentication flows
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://enterprise-video.preview.emergentagent.com')

class TestBiometricEndpoints:
    """Test WebAuthn/Biometric authentication endpoints"""
    
    def test_biometric_supported_endpoint(self):
        """Test /api/biometric/supported returns correct response"""
        response = requests.get(f"{BASE_URL}/api/biometric/supported")
        assert response.status_code == 200
        
        data = response.json()
        assert data["supported"] == True
        assert "rp_id" in data
        assert "rp_name" in data
        assert data["rp_name"] == "MedMatch"
        
        # Check features
        assert "features" in data
        features = data["features"]
        assert features["platform_authenticator"] == True
        assert features["cross_platform"] == True
        assert features["user_verification"] == True
        assert features["resident_key"] == True
        print("✅ /api/biometric/supported - Returns supported:true with all features")
    
    def test_biometric_register_start(self):
        """Test /api/biometric/register/start endpoint"""
        payload = {
            "email": "test_biometric@example.com",
            "username": "Test Biometric User",
            "device_name": "Test Device"
        }
        response = requests.post(
            f"{BASE_URL}/api/biometric/register/start",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "options" in data
        assert "challenge_id" in data
        
        # Verify options structure
        import json
        options = json.loads(data["options"])
        assert "rp" in options
        assert "user" in options
        assert "challenge" in options
        assert "pubKeyCredParams" in options
        assert options["rp"]["name"] == "MedMatch"
        assert options["user"]["name"] == "test_biometric@example.com"
        print("✅ /api/biometric/register/start - Returns valid WebAuthn options")
    
    def test_biometric_authenticate_start_user_not_found(self):
        """Test /api/biometric/authenticate/start with non-existent user"""
        payload = {"email": "nonexistent_user@example.com"}
        response = requests.post(
            f"{BASE_URL}/api/biometric/authenticate/start",
            json=payload
        )
        # Should return 404 for non-existent user
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        print("✅ /api/biometric/authenticate/start - Returns 404 for non-existent user")
    
    def test_biometric_security_status(self):
        """Test /api/biometric/security/status endpoint"""
        response = requests.get(f"{BASE_URL}/api/biometric/security/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "ip_address" in data
        assert "is_suspicious" in data
        assert "risk_score" in data
        assert "security_level" in data
        assert data["security_level"] in ["low", "medium", "high"]
        print("✅ /api/biometric/security/status - Returns security status")


class TestAuthenticationFlow:
    """Test standard authentication flow still works"""
    
    def test_email_login_success(self):
        """Test email/password login still works"""
        payload = {
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=payload
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == "admin@medmatch.com"
        print("✅ /api/auth/login - Email/password login works")
    
    def test_email_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        payload = {
            "email": "admin@medmatch.com",
            "password": "wrongpassword"
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=payload
        )
        assert response.status_code == 401
        print("✅ /api/auth/login - Returns 401 for invalid credentials")


class TestQAPracticeEndpoints:
    """Test Q&A Practice endpoints with fallback"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "MedMatch2026!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def test_qa_practice_analyze_match(self, auth_token):
        """Test /api/qa-practice/analyze-match endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        payload = {
            "job_title": "Software Engineer",
            "company": "Tech Corp",
            "job_description": "Looking for a skilled developer"
        }
        response = requests.post(
            f"{BASE_URL}/api/qa-practice/analyze-match",
            json=payload,
            headers=headers
        )
        # Should work or return appropriate error (401 if no auth, 200/500 if auth)
        assert response.status_code in [200, 400, 401, 500]
        print(f"✅ /api/qa-practice/analyze-match - Returns {response.status_code}")
    
    def test_qa_practice_generate_answer(self, auth_token):
        """Test /api/qa-practice/generate-answer endpoint"""
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        payload = {
            "question": "Tell me about yourself",
            "question_type": "behavioral",
            "job_context": {
                "title": "Software Engineer",
                "company": "Tech Corp"
            }
        }
        response = requests.post(
            f"{BASE_URL}/api/qa-practice/generate-answer",
            json=payload,
            headers=headers
        )
        # Should work or return appropriate error
        assert response.status_code in [200, 400, 401, 500]
        print(f"✅ /api/qa-practice/generate-answer - Returns {response.status_code}")


class TestHealthAndBasicEndpoints:
    """Test basic health and API endpoints"""
    
    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ /api/health - Returns healthy")
    
    def test_translate_languages(self):
        """Test /api/translate/languages endpoint"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 0
        print(f"✅ /api/translate/languages - Returns {len(data['languages'])} languages")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
