"""
Translation Health Monitor API Tests
Tests the new health-monitor endpoint and related translation QA features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-intelligence.preview.emergentagent.com').rstrip('/')


class TestLogin:
    """Test login functionality to get auth token"""
    
    def test_admin_login(self):
        """Login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        # Store token for other tests
        TestLogin.access_token = data["access_token"]
        print(f"Login successful, token: {data['access_token'][:20]}...")


class TestTranslationHealthMonitor:
    """Test Translation Health Monitor endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Ensure we have auth token"""
        if not hasattr(TestLogin, 'access_token'):
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "admin@medmatch.com",
                "password": "Swampdrainer2026!"
            })
            if login_response.status_code == 200:
                TestLogin.access_token = login_response.json()["access_token"]
            else:
                pytest.skip("Could not get auth token")
        
        self.headers = {"Authorization": f"Bearer {TestLogin.access_token}"}
    
    def test_health_monitor_endpoint_exists(self):
        """Test that health-monitor endpoint exists and returns 200"""
        response = requests.get(
            f"{BASE_URL}/api/translation-qa/health-monitor",
            headers=self.headers
        )
        assert response.status_code == 200, f"Health monitor returned {response.status_code}: {response.text}"
        print("Health monitor endpoint returns 200 OK")
    
    def test_health_monitor_returns_overall_status(self):
        """Test that health-monitor returns overall_status field"""
        response = requests.get(
            f"{BASE_URL}/api/translation-qa/health-monitor",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data, f"Missing overall_status. Keys: {data.keys()}"
        assert data["overall_status"] in ["healthy", "warning", "critical"], f"Invalid status: {data['overall_status']}"
        print(f"Overall status: {data['overall_status']}")
    
    def test_health_monitor_returns_summary(self):
        """Test that health-monitor returns summary with required fields"""
        response = requests.get(
            f"{BASE_URL}/api/translation-qa/health-monitor",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data, "Missing summary field"
        summary = data["summary"]
        
        # Check required summary fields
        assert "total_languages" in summary, "Missing total_languages in summary"
        assert "translatable_keys" in summary, "Missing translatable_keys in summary"
        assert "average_coverage" in summary, "Missing average_coverage in summary"
        assert "healthy" in summary, "Missing healthy count in summary"
        assert "warning" in summary, "Missing warning count in summary"
        
        print(f"Summary: {summary['total_languages']} languages, {summary['average_coverage']}% avg coverage")
        print(f"Status counts - Healthy: {summary['healthy']}, Warning: {summary['warning']}")
    
    def test_health_monitor_returns_languages_array(self):
        """Test that health-monitor returns languages array"""
        response = requests.get(
            f"{BASE_URL}/api/translation-qa/health-monitor",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "languages" in data, "Missing languages field"
        assert isinstance(data["languages"], list), "languages should be an array"
        assert len(data["languages"]) > 0, "languages array should not be empty"
        
        # Check first language entry structure
        first_lang = data["languages"][0]
        assert "language" in first_lang, "Missing language code"
        assert "coverage" in first_lang, "Missing coverage"
        assert "status" in first_lang, "Missing status"
        
        print(f"Found {len(data['languages'])} languages")
        print(f"Sample language: {first_lang['language']} - {first_lang['coverage']}% - {first_lang['status']}")
    
    def test_health_monitor_returns_alerts(self):
        """Test that health-monitor returns alerts array"""
        response = requests.get(
            f"{BASE_URL}/api/translation-qa/health-monitor",
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "alerts" in data, "Missing alerts field"
        assert isinstance(data["alerts"], list), "alerts should be an array"
        
        print(f"Found {len(data['alerts'])} alerts")
        if data["alerts"]:
            print(f"Sample alert: {data['alerts'][0].get('message', 'N/A')}")


class TestLinkedInStatus:
    """Test LinkedIn status endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not hasattr(TestLogin, 'access_token'):
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "admin@medmatch.com",
                "password": "Swampdrainer2026!"
            })
            if login_response.status_code == 200:
                TestLogin.access_token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {TestLogin.access_token}"}
    
    def test_linkedin_status_endpoint(self):
        """Test LinkedIn status returns integration_configured"""
        response = requests.get(
            f"{BASE_URL}/api/linkedin/status",
            headers=self.headers
        )
        assert response.status_code == 200, f"LinkedIn status failed: {response.text}"
        data = response.json()
        assert "integration_configured" in data, "Missing integration_configured"
        print(f"LinkedIn integration_configured: {data['integration_configured']}")


class TestORCIDConfig:
    """Test ORCID config endpoint"""
    
    def test_orcid_config_endpoint(self):
        """Test ORCID config returns configured status"""
        response = requests.get(f"{BASE_URL}/api/auth/orcid/config")
        assert response.status_code == 200, f"ORCID config failed: {response.text}"
        data = response.json()
        assert "configured" in data, "Missing configured field"
        print(f"ORCID configured: {data['configured']}")


class TestPayPalCreate:
    """Test PayPal create payment endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        if not hasattr(TestLogin, 'access_token'):
            login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
                "email": "admin@medmatch.com",
                "password": "Swampdrainer2026!"
            })
            if login_response.status_code == 200:
                TestLogin.access_token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {TestLogin.access_token}"}
    
    def test_paypal_create_endpoint_exists(self):
        """Test PayPal create endpoint exists (may return error due to sandbox config)"""
        response = requests.post(
            f"{BASE_URL}/api/payments/paypal/create",
            headers=self.headers,
            json={
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
                "plan": "lifetime"
            }
        )
        # Endpoint should exist - may return 500 if PayPal not configured or 200 if working
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        print(f"PayPal create endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"PayPal response: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
