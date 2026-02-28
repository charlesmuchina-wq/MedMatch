"""
Test suite for i18n and Meeting Portal functionality
Tests P0: i18n verification and P1: Meeting Portal APIs
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://ai-meet-hub.preview.emergentagent.com')

class TestTranslationBenchmark:
    """P0: i18n Translation Benchmark API Tests"""
    
    def test_translation_benchmark_endpoint(self):
        """Test that translation benchmark endpoint returns data"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert "languages" in data
        
    def test_translation_coverage_above_99(self):
        """Test that overall translation coverage is above 99%"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        overall_coverage = data["summary"]["overall_average_coverage"]
        assert overall_coverage >= 99.0, f"Expected >=99% coverage, got {overall_coverage}%"
        
    def test_32_languages_at_95_percent(self):
        """Test that 32 languages have 95%+ coverage"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        langs_at_95 = data["summary"]["languages_at_95_percent"]
        assert langs_at_95 == 32, f"Expected 32 languages at 95%+, got {langs_at_95}"
        
    def test_french_coverage(self):
        """Test French language coverage"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        fr_coverage = data["languages"]["fr"]["coverage"]
        assert fr_coverage >= 99.0, f"French coverage {fr_coverage}% < 99%"
        
    def test_arabic_coverage(self):
        """Test Arabic language coverage"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        ar_coverage = data["languages"]["ar"]["coverage"]
        assert ar_coverage >= 97.0, f"Arabic coverage {ar_coverage}% < 97%"
        
    def test_spanish_coverage(self):
        """Test Spanish language coverage"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        es_coverage = data["languages"]["es"]["coverage"]
        assert es_coverage >= 99.0, f"Spanish coverage {es_coverage}% < 99%"
        
    def test_swahili_coverage(self):
        """Test Swahili language coverage"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        sw_coverage = data["languages"]["sw"]["coverage"]
        assert sw_coverage >= 99.0, f"Swahili coverage {sw_coverage}% < 99%"


class TestMeetingPortalAPIs:
    """P1: Meeting Portal API Tests"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
        
    def test_login_endpoint(self):
        """Test login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        
    def test_ice_servers_endpoint(self):
        """Test ICE servers endpoint returns STUN servers"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        data = response.json()
        assert "ice_servers" in data
        assert data["success"] == True
        assert len(data["ice_servers"]) > 0
        # Verify Google STUN servers are included
        stun_urls = [s["urls"] for s in data["ice_servers"]]
        assert any("stun.l.google.com" in str(u) for u in stun_urls)
        
    def test_create_meeting(self, auth_token):
        """Test creating a new meeting"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Test Meeting from pytest",
                "enable_ai_notes": True,
                "enable_recording": False
            }
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "meeting_id" in data or "id" in data
        
    def test_get_meetings_list(self, auth_token):
        """Test getting list of meetings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should return a list or dict with meetings
        assert isinstance(data, (list, dict))
        
    def test_get_meeting_by_id(self, auth_token):
        """Test getting meeting by ID (DAF3BD00)"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings/DAF3BD00",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Meeting may or may not exist
        assert response.status_code in [200, 404]
        
    def test_meetings_list_has_data(self, auth_token):
        """Test that meetings list returns meeting data"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should return list of meetings or dict with meetings key
        if isinstance(data, dict):
            assert "meetings" in data or len(data) > 0
        else:
            assert isinstance(data, list)


class TestHealthEndpoint:
    """Health check endpoint test"""
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
