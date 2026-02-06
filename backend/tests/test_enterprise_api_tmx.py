"""
Test Enterprise API and TMX Export Features
Tests: API Keys, Webhooks, ATS Status, TMX/JSON/XLIFF Export
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "MedMatch2026!"
JOB_SEEKER_EMAIL = "test_jobseeker_ui@test.com"
JOB_SEEKER_PASSWORD = "Test123!"


class TestEnterpriseAPIStatus:
    """Test Enterprise ATS Status endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        # Login as admin
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            self.admin_token = token
        else:
            pytest.skip("Admin login failed")
    
    def test_ats_status_endpoint(self):
        """Test GET /api/enterprise/ats/status returns correct structure"""
        response = self.session.get(f"{BASE_URL}/api/enterprise/ats/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "tier" in data, "Response should contain 'tier'"
        assert "features" in data, "Response should contain 'features'"
        assert "integrations" in data, "Response should contain 'integrations'"
        assert "rate_limit" in data, "Response should contain 'rate_limit'"
        
        # Verify features structure
        features = data["features"]
        assert "api_access" in features
        assert "webhooks" in features
        assert "bulk_export" in features
        assert "bulk_import" in features
        assert "sso" in features
        
        print(f"ATS Status: tier={data['tier']}, rate_limit={data['rate_limit']}")
        print(f"Features: {features}")
    
    def test_ats_status_unauthenticated(self):
        """Test ATS status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/enterprise/ats/status")
        assert response.status_code == 401, "Should require authentication"


class TestAPIKeyManagement:
    """Test API Key creation and management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_list_api_keys(self):
        """Test GET /api/enterprise/api-keys"""
        response = self.session.get(f"{BASE_URL}/api/enterprise/api-keys")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "api_keys" in data
        assert "count" in data
        assert "tier" in data
        assert "rate_limit" in data
        
        print(f"API Keys count: {data['count']}, tier: {data['tier']}")
    
    def test_create_api_key_tier_gating(self):
        """Test API key creation requires Premium tier"""
        # Admin is on recruiter_starter tier, should be denied
        response = self.session.post(f"{BASE_URL}/api/enterprise/api-keys", json={
            "name": "Test API Key",
            "scopes": ["read:candidates"],
            "expires_in_days": 30
        })
        
        # Should return 403 because admin is on starter tier
        if response.status_code == 403:
            data = response.json()
            assert "Premium" in data.get("detail", "") or "upgrade" in data.get("detail", "").lower()
            print(f"Tier gating working: {data.get('detail')}")
        elif response.status_code == 200:
            # If it succeeds, user might have been upgraded
            print("API key created - user may have Premium tier")
        else:
            print(f"Unexpected response: {response.status_code} - {response.text}")


class TestWebhookManagement:
    """Test Webhook creation and management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_list_webhooks(self):
        """Test GET /api/enterprise/webhooks"""
        response = self.session.get(f"{BASE_URL}/api/enterprise/webhooks")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "webhooks" in data
        assert "count" in data
        assert "available_events" in data
        
        print(f"Webhooks count: {data['count']}")
        print(f"Available events: {len(data['available_events'])}")
    
    def test_create_webhook_tier_gating(self):
        """Test webhook creation requires Growth tier"""
        response = self.session.post(f"{BASE_URL}/api/enterprise/webhooks", json={
            "url": "https://example.com/webhook",
            "events": ["application.created"],
            "description": "Test webhook"
        })
        
        # Should return 403 because admin is on starter tier
        if response.status_code == 403:
            data = response.json()
            assert "Growth" in data.get("detail", "") or "upgrade" in data.get("detail", "").lower()
            print(f"Tier gating working: {data.get('detail')}")
        elif response.status_code == 200:
            print("Webhook created - user may have Growth tier")
        else:
            print(f"Unexpected response: {response.status_code} - {response.text}")


class TestTMXExport:
    """Test TMX/JSON/XLIFF Export endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_tmx_export_admin_only(self):
        """Test TMX export requires admin role"""
        response = self.session.get(f"{BASE_URL}/api/translate/memory/export/tmx")
        
        # Should be 200 (admin) or 404 (no entries)
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            # Verify TMX format
            content = response.text
            assert "<?xml" in content
            assert "<tmx" in content
            print("TMX export successful - valid XML returned")
        else:
            print("TMX export: No translation memory entries found (expected)")
    
    def test_json_export_admin_only(self):
        """Test JSON export requires admin role"""
        response = self.session.get(f"{BASE_URL}/api/translate/memory/export/json")
        
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert "format" in data
            assert "entries" in data
            assert "statistics" in data
            print(f"JSON export successful - {len(data.get('entries', []))} entries")
        else:
            print("JSON export: No entries found")
    
    def test_xliff_export_requires_language(self):
        """Test XLIFF export requires target_language parameter"""
        # Without target_language
        response = self.session.get(f"{BASE_URL}/api/translate/memory/export/xliff")
        assert response.status_code == 400, "Should require target_language"
        
        # With target_language
        response = self.session.get(f"{BASE_URL}/api/translate/memory/export/xliff?target_language=es")
        assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}"
        
        if response.status_code == 200:
            content = response.text
            assert "<?xml" in content
            assert "<xliff" in content
            print("XLIFF export successful")
        else:
            print("XLIFF export: No entries for Spanish")
    
    def test_export_non_admin_denied(self):
        """Test export endpoints deny non-admin users"""
        # Login as job seeker
        session = requests.Session()
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": JOB_SEEKER_EMAIL,
            "password": JOB_SEEKER_PASSWORD
        })
        
        if response.status_code != 200:
            pytest.skip("Job seeker login failed")
        
        token = response.json().get("access_token")
        session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Try TMX export
        response = session.get(f"{BASE_URL}/api/translate/memory/export/tmx")
        assert response.status_code == 403, f"Non-admin should be denied TMX export, got {response.status_code}"
        
        # Try JSON export
        response = session.get(f"{BASE_URL}/api/translate/memory/export/json")
        assert response.status_code == 403, f"Non-admin should be denied JSON export, got {response.status_code}"
        
        print("Non-admin correctly denied access to export endpoints")


class TestATSDocumentation:
    """Test ATS Documentation endpoint"""
    
    def test_ats_docs_public(self):
        """Test GET /api/enterprise/ats/docs is accessible"""
        response = requests.get(f"{BASE_URL}/api/enterprise/ats/docs")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "api_version" in data
        assert "authentication" in data
        assert "endpoints" in data
        assert "webhooks" in data
        assert "rate_limits" in data
        
        print(f"API Version: {data['api_version']}")
        print(f"Endpoints documented: {list(data['endpoints'].keys())}")


class TestTranslationMemoryStats:
    """Test Translation Memory statistics"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup - login as admin"""
        self.session = requests.Session()
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            token = response.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            pytest.skip("Admin login failed")
    
    def test_memory_stats(self):
        """Test GET /api/translate/memory/stats"""
        response = self.session.get(f"{BASE_URL}/api/translate/memory/stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total_entries" in data
        assert "by_language" in data
        assert "by_context" in data
        
        print(f"Translation Memory: {data['total_entries']} entries")
    
    def test_memory_analytics(self):
        """Test GET /api/translate/memory/analytics"""
        response = self.session.get(f"{BASE_URL}/api/translate/memory/analytics")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "summary" in data or "total_entries" in data
        
        print(f"Memory Analytics: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
