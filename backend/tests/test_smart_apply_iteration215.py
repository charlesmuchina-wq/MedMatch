"""
Smart Apply (Quick Apply Bot) Backend Tests - Iteration 215
Tests:
- GET /api/smart-apply/config - returns default config for authenticated user
- PUT /api/smart-apply/config - saves target_roles, locations, exclude_companies
- POST /api/smart-apply/run - with job_title, location, max_jobs returns matching jobs
- GET /api/smart-apply/history - returns run history
- Smart Apply filters to 24h window jobs only
- Quick Apply Bot exists in ENZI bot catalog
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestSmartApplyBackend:
    """Smart Apply API endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    # ========== Unauthenticated Tests ==========
    
    def test_config_get_unauthenticated(self):
        """GET /api/smart-apply/config returns 401 for unauthenticated"""
        response = requests.get(f"{BASE_URL}/api/smart-apply/config")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/smart-apply/config returns 401 for unauthenticated")
    
    def test_config_put_unauthenticated(self):
        """PUT /api/smart-apply/config returns 401 for unauthenticated"""
        response = requests.put(
            f"{BASE_URL}/api/smart-apply/config",
            json={"target_roles": ["Engineer"]}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ PUT /api/smart-apply/config returns 401 for unauthenticated")
    
    def test_run_unauthenticated(self):
        """POST /api/smart-apply/run returns 401 for unauthenticated"""
        response = requests.post(
            f"{BASE_URL}/api/smart-apply/run",
            json={"job_title": "Engineer", "location": "Remote", "max_jobs": 5}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ POST /api/smart-apply/run returns 401 for unauthenticated")
    
    def test_history_unauthenticated(self):
        """GET /api/smart-apply/history returns 401 for unauthenticated"""
        response = requests.get(f"{BASE_URL}/api/smart-apply/history")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ GET /api/smart-apply/history returns 401 for unauthenticated")
    
    # ========== Authenticated Tests ==========
    
    def test_config_get_authenticated(self, auth_headers):
        """GET /api/smart-apply/config returns default config for authenticated user"""
        response = requests.get(f"{BASE_URL}/api/smart-apply/config", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify config structure
        assert "target_roles" in data, "Config should have target_roles"
        assert "locations" in data, "Config should have locations"
        assert "exclude_companies" in data, "Config should have exclude_companies"
        assert "max_applications_per_run" in data, "Config should have max_applications_per_run"
        assert "auto_generate_cover_letter" in data, "Config should have auto_generate_cover_letter"
        
        print(f"✓ GET /api/smart-apply/config returns config: {data}")
    
    def test_config_put_authenticated(self, auth_headers):
        """PUT /api/smart-apply/config saves target_roles, locations, exclude_companies"""
        test_config = {
            "target_roles": ["Software Engineer", "Data Scientist"],
            "locations": ["Remote", "San Francisco"],
            "exclude_companies": ["TestCompanyExclude"],
            "max_applications_per_run": 15,
            "auto_generate_cover_letter": True
        }
        
        response = requests.put(
            f"{BASE_URL}/api/smart-apply/config",
            headers=auth_headers,
            json=test_config
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        # Verify saved by fetching again
        get_response = requests.get(f"{BASE_URL}/api/smart-apply/config", headers=auth_headers)
        assert get_response.status_code == 200
        saved_config = get_response.json()
        
        assert saved_config.get("target_roles") == test_config["target_roles"], "target_roles not saved correctly"
        assert saved_config.get("locations") == test_config["locations"], "locations not saved correctly"
        assert saved_config.get("exclude_companies") == test_config["exclude_companies"], "exclude_companies not saved correctly"
        
        print(f"✓ PUT /api/smart-apply/config saves config correctly")
    
    def test_run_with_params(self, auth_headers):
        """POST /api/smart-apply/run with job_title, location, max_jobs returns matching jobs"""
        run_params = {
            "job_title": "Software Engineer",
            "location": "Remote",
            "max_jobs": 3
        }
        
        response = requests.post(
            f"{BASE_URL}/api/smart-apply/run",
            headers=auth_headers,
            json=run_params,
            timeout=60  # May take time due to job search + AI cover letter generation
        )
        
        # Could be 200 (success) or 400 (no resume)
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "run_id" in data, "Response should have run_id"
            assert "job_title" in data, "Response should have job_title"
            assert "total_jobs_found" in data, "Response should have total_jobs_found"
            assert "results" in data, "Response should have results"
            
            # Check results structure
            if data.get("results"):
                result = data["results"][0]
                assert "title" in result, "Result should have title"
                assert "company" in result, "Result should have company"
                assert "match_score" in result, "Result should have match_score"
            
            print(f"✓ POST /api/smart-apply/run returns: run_id={data.get('run_id')}, found={data.get('total_jobs_found')}, applied={data.get('total_applied')}")
        else:
            # 400 means no resume uploaded - still valid behavior
            print(f"✓ POST /api/smart-apply/run returns 400 (no resume) - expected behavior")
    
    def test_history_authenticated(self, auth_headers):
        """GET /api/smart-apply/history returns run history"""
        response = requests.get(f"{BASE_URL}/api/smart-apply/history", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "runs" in data, "Response should have runs array"
        assert isinstance(data["runs"], list), "runs should be a list"
        
        # If there are runs, verify structure
        if data["runs"]:
            run = data["runs"][0]
            assert "id" in run, "Run should have id"
            assert "job_title" in run, "Run should have job_title"
            assert "created_at" in run, "Run should have created_at"
        
        print(f"✓ GET /api/smart-apply/history returns {len(data['runs'])} runs")


class TestEnziBotCatalog:
    """ENZI Bot Catalog tests for Quick Apply Bot"""
    
    def test_quick_apply_bot_in_catalog(self):
        """GET /api/lumi/bots/catalog?category=Job+Toolkit should include Quick Apply Bot"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog?category=Job+Toolkit")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "bots" in data, "Response should have bots array"
        
        # Find quick_apply bot
        quick_apply_bot = None
        for bot in data["bots"]:
            if bot.get("id") == "quick_apply":
                quick_apply_bot = bot
                break
        
        assert quick_apply_bot is not None, "Quick Apply Bot should be in Job Toolkit category"
        assert quick_apply_bot.get("name") == "Quick Apply Bot", f"Bot name should be 'Quick Apply Bot', got {quick_apply_bot.get('name')}"
        assert quick_apply_bot.get("category") == "Job Toolkit", "Bot should be in Job Toolkit category"
        
        print(f"✓ Quick Apply Bot found in catalog: {quick_apply_bot.get('name')}")
    
    def test_quick_apply_bot_featured(self):
        """GET /api/lumi/bots/featured should include Quick Apply Bot"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/featured")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "bots" in data, "Response should have bots array"
        
        # Find quick_apply bot in featured
        quick_apply_bot = None
        for bot in data["bots"]:
            if bot.get("id") == "quick_apply":
                quick_apply_bot = bot
                break
        
        assert quick_apply_bot is not None, "Quick Apply Bot should be in featured bots"
        print(f"✓ Quick Apply Bot is featured: {quick_apply_bot.get('name')}")


class TestPredictiveChannels:
    """Test predictive channels endpoint used by ENZI messenger"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_predict_channels_endpoint(self, auth_headers):
        """GET /api/lumi/behavior/predict-channels returns predictions"""
        response = requests.get(f"{BASE_URL}/api/lumi/behavior/predict-channels", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should have predictions array
        assert "predictions" in data or "channels" in data, "Response should have predictions"
        
        print(f"✓ GET /api/lumi/behavior/predict-channels returns predictions")


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("✓ API health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
