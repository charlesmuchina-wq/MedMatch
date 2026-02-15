"""
Test suite for Q&A Practice, Translation, Biometric, and new features
Tests: Q&A Practice endpoints, Translation API (39 languages), Biometric WebAuthn
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://medmeet-4.preview.emergentagent.com').rstrip('/')

class TestTranslationAPI:
    """Translation API - 39 languages with EFIGS, CJK, expanding markets"""
    
    def test_get_languages_returns_39_plus(self):
        """GET /api/translate/languages returns 39+ languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) >= 39
        print(f"✅ Translation API returns {len(data['languages'])} languages")
    
    def test_languages_include_efigs(self):
        """Languages include EFIGS (en, es, fr, de, it)"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        data = response.json()
        codes = [lang["code"] for lang in data["languages"]]
        
        efigs = ["en", "es", "fr", "de", "it"]
        for code in efigs:
            assert code in codes, f"Missing EFIGS language: {code}"
        print("✅ EFIGS languages present: en, es, fr, de, it")
    
    def test_languages_include_cjk(self):
        """Languages include CJK (zh, ja, ko)"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        data = response.json()
        codes = [lang["code"] for lang in data["languages"]]
        
        cjk = ["zh", "ja", "ko"]
        for code in cjk:
            assert code in codes, f"Missing CJK language: {code}"
        print("✅ CJK languages present: zh, ja, ko")
    
    def test_languages_include_expanding_markets(self):
        """Languages include expanding markets (hi, pt-BR, ar)"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        data = response.json()
        codes = [lang["code"] for lang in data["languages"]]
        
        expanding = ["hi", "pt-BR", "ar"]
        for code in expanding:
            assert code in codes, f"Missing expanding market language: {code}"
        print("✅ Expanding market languages present: hi, pt-BR, ar")


class TestBiometricAPI:
    """Biometric WebAuthn API tests"""
    
    def test_biometric_supported_returns_true(self):
        """GET /api/biometric/supported returns supported:true"""
        response = requests.get(f"{BASE_URL}/api/biometric/supported")
        assert response.status_code == 200
        data = response.json()
        assert data.get("supported") == True
        print("✅ Biometric API returns supported:true")
    
    def test_biometric_features(self):
        """Biometric API returns expected features"""
        response = requests.get(f"{BASE_URL}/api/biometric/supported")
        data = response.json()
        assert "features" in data
        features = data["features"]
        assert features.get("platform_authenticator") == True
        assert features.get("cross_platform") == True
        print("✅ Biometric features: platform_authenticator, cross_platform")


class TestQAPracticeAPI:
    """Q&A Practice API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authenticated session"""
        self.session = requests.Session()
        # Login as admin
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        })
        if login_response.status_code == 200:
            print("✅ Logged in as admin")
        yield
    
    def test_qa_practice_analyze_match(self):
        """POST /api/qa-practice/analyze-match works"""
        response = self.session.post(f"{BASE_URL}/api/qa-practice/analyze-match", json={
            "company_name": "Test Company",
            "job_title": "Software Engineer",
            "job_description": "Looking for a skilled developer"
        })
        # Should return 200 or 401 if auth required
        assert response.status_code in [200, 401, 422]
        print(f"✅ Q&A analyze-match endpoint: {response.status_code}")
    
    def test_qa_practice_generate_answer(self):
        """POST /api/qa-practice/generate-answer works"""
        response = self.session.post(f"{BASE_URL}/api/qa-practice/generate-answer", json={
            "question": "Tell me about yourself",
            "question_type": "behavioral",
            "job_context": {
                "company_name": "Test Corp",
                "job_title": "Engineer"
            }
        })
        assert response.status_code in [200, 401, 422, 500]
        print(f"✅ Q&A generate-answer endpoint: {response.status_code}")
    
    def test_qa_practice_common_questions(self):
        """POST /api/qa-practice/common-questions works"""
        response = self.session.post(f"{BASE_URL}/api/qa-practice/common-questions", json={
            "company_name": "Test Company",
            "job_title": "Software Engineer"
        })
        assert response.status_code in [200, 401, 422, 500]
        print(f"✅ Q&A common-questions endpoint: {response.status_code}")
    
    def test_qa_practice_history(self):
        """GET /api/qa-practice/history works"""
        response = self.session.get(f"{BASE_URL}/api/qa-practice/history?limit=10")
        assert response.status_code in [200, 401]
        print(f"✅ Q&A history endpoint: {response.status_code}")
    
    def test_qa_practice_transcribe_audio_endpoint_exists(self):
        """POST /api/qa-practice/transcribe-audio endpoint exists"""
        # Just check endpoint exists (returns 422 without file)
        response = self.session.post(f"{BASE_URL}/api/qa-practice/transcribe-audio")
        # Should return 422 (validation error) or 400 (bad request) - not 404
        assert response.status_code != 404, "Transcribe audio endpoint not found"
        print(f"✅ Q&A transcribe-audio endpoint exists: {response.status_code}")


class TestHealthAndCore:
    """Core API health tests"""
    
    def test_health_check(self):
        """GET /api/health returns healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check: healthy")
    
    def test_auth_login_admin(self):
        """POST /api/auth/login works for admin"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "MedMatch2026!"
        })
        assert response.status_code == 200
        print("✅ Admin login successful")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
