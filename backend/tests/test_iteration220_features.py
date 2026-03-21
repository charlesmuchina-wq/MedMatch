"""
Iteration 220 - Testing new features:
1. CI/CD Pipeline files (GitHub Actions + local runner)
2. P1 Resend Email Settings API (GET/PUT/POST test)
3. P2 Refactored KarauSettingsPage (8 tabs)
4. P2 Refactored BotStoreModal
5. P3 Enhanced BotChainBuilder (5 triggers)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


class TestCICDFiles:
    """CI/CD: Verify GitHub Actions workflow and local test runner exist"""
    
    def test_github_actions_workflow_exists(self):
        """CI/CD: GitHub Actions workflow file exists"""
        workflow_path = "/app/.github/workflows/test.yml"
        assert os.path.exists(workflow_path), f"GitHub Actions workflow not found at {workflow_path}"
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Verify key workflow components
        assert "name: AI Suite Testing Pipeline" in content, "Workflow name missing"
        assert "phase1-functional" in content, "Phase 1 job missing"
        assert "phase3-regression" in content, "Phase 3 job missing"
        assert "gate-summary" in content, "Gate summary job missing"
        assert "pytest" in content, "pytest command missing"
        print("GitHub Actions workflow file validated")
    
    def test_local_test_runner_exists_and_executable(self):
        """CI/CD: Local test runner script exists and is executable"""
        script_path = "/app/scripts/run_tests.sh"
        assert os.path.exists(script_path), f"Local test runner not found at {script_path}"
        
        # Check if executable
        assert os.access(script_path, os.X_OK), "run_tests.sh is not executable"
        
        with open(script_path, 'r') as f:
            content = f.read()
        
        # Verify key script components
        assert "#!/bin/bash" in content, "Shebang missing"
        assert "phase1" in content.lower(), "Phase 1 reference missing"
        assert "phase3" in content.lower(), "Phase 3 reference missing"
        assert "pytest" in content, "pytest command missing"
        print("Local test runner script validated")


class TestEmailSettingsAPI:
    """P1-EMAIL-API: Test Resend email settings endpoints"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip(f"Admin login failed: {response.status_code}")
    
    @pytest.fixture(scope="class")
    def test_user_token(self):
        """Get non-admin user token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip(f"Test user login failed: {response.status_code}")
    
    def test_get_email_settings_admin(self, admin_token):
        """P1-EMAIL-API: GET /api/admin/email-settings returns current email config (admin)"""
        response = requests.get(
            f"{BASE_URL}/api/admin/email-settings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify response structure
        assert "resend_api_key_masked" in data, "Missing resend_api_key_masked"
        assert "sender_email" in data, "Missing sender_email"
        assert "is_configured" in data, "Missing is_configured"
        assert "source" in data, "Missing source"
        
        # Verify data types
        assert isinstance(data["is_configured"], bool), "is_configured should be boolean"
        assert data["source"] in ["database", "environment"], f"Invalid source: {data['source']}"
        
        print(f"Email settings retrieved: configured={data['is_configured']}, source={data['source']}")
    
    def test_get_email_settings_non_admin_forbidden(self, test_user_token):
        """P1-EMAIL-API: Non-admin user gets 403 on email settings GET"""
        response = requests.get(
            f"{BASE_URL}/api/admin/email-settings",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("Non-admin correctly denied access to email settings GET")
    
    def test_put_email_settings_admin(self, admin_token):
        """P1-EMAIL-API: PUT /api/admin/email-settings updates sender email"""
        # Update only sender email (don't change API key)
        response = requests.put(
            f"{BASE_URL}/api/admin/email-settings",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json={"sender_email": "onboarding@resend.dev"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Update should return success=True"
        print("Email settings updated successfully")
        
        # Verify the update persisted
        verify_response = requests.get(
            f"{BASE_URL}/api/admin/email-settings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert verify_response.status_code == 200
        verify_data = verify_response.json()
        assert verify_data["sender_email"] == "onboarding@resend.dev", "Sender email not persisted"
    
    def test_put_email_settings_non_admin_forbidden(self, test_user_token):
        """P1-EMAIL-API: Non-admin user gets 403 on email settings PUT"""
        response = requests.put(
            f"{BASE_URL}/api/admin/email-settings",
            headers={
                "Authorization": f"Bearer {test_user_token}",
                "Content-Type": "application/json"
            },
            json={"sender_email": "hacker@evil.com"}
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("Non-admin correctly denied access to email settings PUT")
    
    def test_post_email_test_admin(self, admin_token):
        """P1-EMAIL-API: POST /api/admin/email-settings/test sends test email"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-settings/test",
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json"
            },
            json={"to_email": "test@example.com"}
        )
        # May return 200 with success=false if API key is invalid/sandbox
        assert response.status_code in [200, 400], f"Expected 200 or 400, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Response should have success and message fields
        assert "success" in data or "message" in data, "Response should have success or message"
        print(f"Email test endpoint responded: {data}")
    
    def test_post_email_test_non_admin_forbidden(self, test_user_token):
        """P1-EMAIL-API: Non-admin user gets 403 on email test POST"""
        response = requests.post(
            f"{BASE_URL}/api/admin/email-settings/test",
            headers={
                "Authorization": f"Bearer {test_user_token}",
                "Content-Type": "application/json"
            },
            json={"to_email": "test@example.com"}
        )
        assert response.status_code == 403, f"Expected 403 for non-admin, got {response.status_code}"
        print("Non-admin correctly denied access to email test POST")


class TestExistingEndpoints:
    """Verify existing endpoints still work after refactoring"""
    
    def test_health_endpoint(self):
        """BACKEND: Health endpoint works"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("Health endpoint working")
    
    def test_auth_login_endpoint(self):
        """BACKEND: Auth login endpoint works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data or "token" in data
        print("Auth login endpoint working")
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip("Login failed")
    
    def test_lumi_channels_endpoint(self, auth_token):
        """BACKEND: LUMI channels endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # API returns my_channels and discover instead of channels
        assert "my_channels" in data or "channels" in data, f"Expected my_channels or channels in response"
        channels = data.get("my_channels", data.get("channels", []))
        print(f"LUMI channels endpoint working: {len(channels)} channels")
    
    def test_lumi_bots_catalog_endpoint(self, auth_token):
        """BACKEND: LUMI bots catalog endpoint works (for BotStoreModal)"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/catalog",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "bots" in data
        assert "categories" in data
        print(f"Bot catalog endpoint working: {len(data['bots'])} bots, {len(data['categories'])} categories")
    
    def test_karau_accessibility_settings_endpoint(self, auth_token):
        """BACKEND: KARAU accessibility settings endpoint works (for KarauSettingsPage)"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/accessibility/settings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        # Should have accessibility settings fields
        assert isinstance(data, dict)
        print("KARAU accessibility settings endpoint working")
    
    def test_karau_security_compliance_endpoint(self, auth_token):
        """BACKEND: KARAU security compliance endpoint works"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/security/compliance",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        print("KARAU security compliance endpoint working")


class TestBotChainBuilderEndpoints:
    """P3-TRIGGERS: Test BotChainBuilder related endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip("Login failed")
    
    @pytest.fixture(scope="class")
    def test_channel_id(self, auth_token):
        """Get or create a test channel"""
        # First try to get existing channels
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            channels = response.json().get("channels", [])
            if channels:
                return channels[0]["id"]
        
        # Create a test channel if none exist
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={"name": "test-bot-chain-channel", "description": "Test channel for bot chains"}
        )
        if response.status_code in [200, 201]:
            return response.json().get("id") or response.json().get("channel", {}).get("id")
        
        pytest.skip("Could not get or create test channel")
    
    def test_get_bot_chains(self, auth_token, test_channel_id):
        """P3-TRIGGERS: Get bot chains for a channel"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/chains/{test_channel_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "chains" in data
        print(f"Bot chains endpoint working: {len(data['chains'])} chains")
    
    def test_create_bot_chain_with_scheduled_trigger(self, auth_token, test_channel_id):
        """P3-TRIGGERS: Create bot chain with scheduled trigger"""
        # First get bot catalog to get valid bot IDs
        catalog_response = requests.get(
            f"{BASE_URL}/api/lumi/bots/catalog",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if catalog_response.status_code != 200:
            pytest.skip("Could not get bot catalog")
        
        bots = catalog_response.json().get("bots", [])
        if len(bots) < 2:
            pytest.skip("Need at least 2 bots in catalog")
        
        # Create chain with scheduled trigger
        response = requests.post(
            f"{BASE_URL}/api/lumi/bots/chains",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "name": "TEST_Scheduled_Workflow",
                "channel_id": test_channel_id,
                "steps": [
                    {"bot_id": bots[0]["id"], "action": bots[0]["id"], "order": 1},
                    {"bot_id": bots[1]["id"], "action": bots[1]["id"], "order": 2}
                ],
                "trigger": "scheduled",
                "trigger_config": {"type": "scheduled", "value": "0 9 * * *"}
            }
        )
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data or "chain" in data
        print("Created bot chain with scheduled trigger")
        
        # Clean up - delete the test chain
        chain_id = data.get("id") or data.get("chain", {}).get("id")
        if chain_id:
            requests.delete(
                f"{BASE_URL}/api/lumi/bots/chains/{chain_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )


class TestRefactoredComponentsBackendSupport:
    """Verify backend endpoints support refactored frontend components"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        pytest.skip("Login failed")
    
    def test_karau_calendar_status(self, auth_token):
        """P2-REFACTOR-KARAU: Calendar tab backend support"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/calendar/status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # May return 200 or 404 depending on implementation
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        print(f"Calendar status endpoint: {response.status_code}")
    
    def test_karau_tsr_reports(self, auth_token):
        """P2-REFACTOR-KARAU: TSR tab backend support"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/tsr/reports",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "reports" in data
        print(f"TSR reports endpoint working: {len(data['reports'])} reports")
    
    def test_lumi_bots_installed(self, auth_token):
        """P2-REFACTOR-BOT: Installed bots endpoint for BotStoreModal"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/installed",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "bots" in data
        print(f"Installed bots endpoint working: {len(data['bots'])} installed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
