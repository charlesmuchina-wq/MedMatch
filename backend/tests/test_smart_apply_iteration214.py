"""
Smart Apply Backend Tests - Iteration 214
Tests for Quick Apply Bot backend endpoints:
- GET /api/smart-apply/config - Get user's Smart Apply preferences
- PUT /api/smart-apply/config - Save preferences  
- POST /api/smart-apply/run - Run smart apply with job search
- GET /api/smart-apply/history - Get run history
- Authentication checks (401 for unauthenticated)
- ENZI Bot Catalog check for quick_apply bot
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSmartApplyAuthentication:
    """Test authentication requirements for Smart Apply endpoints"""
    
    def test_smart_apply_config_requires_auth(self):
        """GET /api/smart-apply/config should return 401 for unauthenticated users"""
        response = requests.get(f"{BASE_URL}/api/smart-apply/config")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/smart-apply/config returns 401 for unauthenticated users")
    
    def test_smart_apply_history_requires_auth(self):
        """GET /api/smart-apply/history should return 401 for unauthenticated users"""
        response = requests.get(f"{BASE_URL}/api/smart-apply/history")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: GET /api/smart-apply/history returns 401 for unauthenticated users")
    
    def test_smart_apply_run_requires_auth(self):
        """POST /api/smart-apply/run should return 401 for unauthenticated users"""
        response = requests.post(
            f"{BASE_URL}/api/smart-apply/run",
            json={"job_title": "Test", "location": "Remote", "max_jobs": 5}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: POST /api/smart-apply/run returns 401 for unauthenticated users")
    
    def test_smart_apply_config_put_requires_auth(self):
        """PUT /api/smart-apply/config should return 401 for unauthenticated users"""
        response = requests.put(
            f"{BASE_URL}/api/smart-apply/config",
            json={"target_roles": ["Engineer"], "locations": ["Remote"]}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: PUT /api/smart-apply/config returns 401 for unauthenticated users")


class TestSmartApplyConfig:
    """Test Smart Apply config endpoints with authenticated user"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_get_smart_apply_config(self, auth_token):
        """GET /api/smart-apply/config returns config for authenticated user"""
        response = requests.get(
            f"{BASE_URL}/api/smart-apply/config",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Verify config structure
        assert "target_roles" in data or "user_id" in data, "Config should have target_roles or user_id"
        assert "locations" in data, "Config should have locations"
        assert "auto_generate_cover_letter" in data, "Config should have auto_generate_cover_letter"
        print(f"PASS: GET /api/smart-apply/config returns config: {list(data.keys())}")
    
    def test_put_smart_apply_config(self, auth_token):
        """PUT /api/smart-apply/config saves preferences"""
        config_data = {
            "target_roles": ["Software Engineer", "Backend Developer"],
            "locations": ["Remote", "San Francisco"],
            "exclude_companies": ["BadCompany Inc"],
            "auto_generate_cover_letter": True,
            "max_applications_per_run": 15
        }
        response = requests.put(
            f"{BASE_URL}/api/smart-apply/config",
            headers={"Authorization": f"Bearer {auth_token}"},
            json=config_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "message" in data or data.get("message") == "Config saved", "Should return success message"
        print("PASS: PUT /api/smart-apply/config saves preferences")
        
        # Verify the config was saved by fetching it again
        verify_response = requests.get(
            f"{BASE_URL}/api/smart-apply/config",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert verify_response.status_code == 200
        saved_config = verify_response.json()
        assert "Software Engineer" in saved_config.get("target_roles", []) or saved_config.get("target_roles") == config_data["target_roles"]
        print("PASS: Verified config was persisted correctly")


class TestSmartApplyRun:
    """Test Smart Apply run endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_smart_apply_run_accepts_params(self, auth_token):
        """POST /api/smart-apply/run accepts job_title, location, max_jobs params"""
        # Note: This may take a while as it performs actual job search
        response = requests.post(
            f"{BASE_URL}/api/smart-apply/run",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"job_title": "Software Engineer", "location": "Remote", "max_jobs": 2},
            timeout=120  # Allow up to 2 minutes for job search + AI cover letter generation
        )
        # Should either succeed (200) or fail with 400 if no resume
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "run_id" in data, "Response should contain run_id"
            assert "results" in data, "Response should contain results"
            assert "total_applied" in data or "total_jobs_found" in data, "Response should contain totals"
            print(f"PASS: POST /api/smart-apply/run completed - found {data.get('total_jobs_found', 0)} jobs, applied to {data.get('total_applied', 0)}")
        else:
            # 400 is acceptable if user has no resume
            data = response.json()
            assert "resume" in data.get("detail", "").lower() or "upload" in data.get("detail", "").lower(), \
                f"400 should be about missing resume, got: {data}"
            print("PASS: POST /api/smart-apply/run correctly requires resume (400 returned)")


class TestSmartApplyHistory:
    """Test Smart Apply history endpoint"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        if response.status_code != 200:
            pytest.skip(f"Authentication failed: {response.status_code}")
        return response.json().get("access_token")
    
    def test_get_smart_apply_history(self, auth_token):
        """GET /api/smart-apply/history returns run history"""
        response = requests.get(
            f"{BASE_URL}/api/smart-apply/history",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "runs" in data, "Response should contain runs array"
        assert isinstance(data["runs"], list), "Runs should be a list"
        print(f"PASS: GET /api/smart-apply/history returns {len(data['runs'])} runs")


class TestEnziBotCatalog:
    """Test that Quick Apply Bot exists in ENZI bot catalog"""
    
    def test_quick_apply_bot_in_catalog(self):
        """GET /api/lumi/bots/catalog should include quick_apply bot in Job Toolkit category"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog?category=Job+Toolkit")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "bots" in data, "Response should contain bots array"
        
        # Find quick_apply bot
        quick_apply_bot = next((b for b in data["bots"] if b["id"] == "quick_apply"), None)
        assert quick_apply_bot is not None, "quick_apply bot should exist in Job Toolkit category"
        assert quick_apply_bot["name"] == "Quick Apply Bot", "Bot name should be 'Quick Apply Bot'"
        assert quick_apply_bot["category"] == "Job Toolkit", "Bot should be in Job Toolkit category"
        assert quick_apply_bot.get("featured") == True, "quick_apply should be featured"
        print(f"PASS: Quick Apply Bot found in ENZI bot catalog - rating: {quick_apply_bot.get('rating')}, installs: {quick_apply_bot.get('install_count')}")
    
    def test_quick_apply_bot_in_featured(self):
        """GET /api/lumi/bots/featured should include quick_apply bot"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/featured")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        # Check if quick_apply is in featured bots
        quick_apply_bot = next((b for b in data.get("bots", []) if b["id"] == "quick_apply"), None)
        assert quick_apply_bot is not None, "quick_apply bot should be in featured bots"
        print("PASS: Quick Apply Bot is in featured bots")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
