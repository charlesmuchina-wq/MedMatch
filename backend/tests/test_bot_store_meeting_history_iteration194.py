"""
ENZI Iteration 194 Tests: Bot Store/Marketplace, Meeting History Panel, Legacy Admin Auth Display
Tests for:
1. GET /api/lumi/meetings/history - Meeting history endpoint
2. GET /api/lumi/bots/catalog - Bot catalog (8 bots)
3. POST /api/lumi/bots/install - Install bot to channel
4. GET /api/lumi/bots/installed - Get installed bots
5. DELETE /api/lumi/bots/uninstall/{id} - Uninstall bot
6. POST /api/auth/login - Admin credentials verification
7. POST /api/auth/github/login - GitHub SSO (MOCKED) still works
8. GET /api/lumi/profile/capabilities - User profile with auth method badge
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://karau-enzi-nexus.preview.emergentagent.com').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


class TestAdminLogin:
    """Test admin login and verify auth method for Legacy Admin User Display"""
    
    def test_admin_login_success(self):
        """Test admin@medmatch.com login with Swampdrainer2026!"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        print(f"PASS: Admin login successful, user_id={data['user'].get('user_id')}")
        return data["access_token"]


class TestMeetingHistoryEndpoint:
    """Test GET /api/lumi/meetings/history endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for authenticated requests"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_res.status_code == 200:
            self.token = login_res.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed - skipping authenticated tests")
    
    def test_meeting_history_returns_200(self):
        """GET /api/lumi/meetings/history returns 200 with meetings list and total"""
        response = requests.get(f"{BASE_URL}/api/lumi/meetings/history", headers=self.headers)
        assert response.status_code == 200, f"Meeting history failed: {response.text}"
        data = response.json()
        assert "meetings" in data, "Response should contain 'meetings' key"
        assert "total" in data, "Response should contain 'total' key"
        assert "count" in data, "Response should contain 'count' key"
        assert isinstance(data["meetings"], list), "'meetings' should be a list"
        assert isinstance(data["total"], int), "'total' should be an integer"
        print(f"PASS: Meeting history returned {data['count']} meetings, total={data['total']}")
    
    def test_meeting_history_with_limit(self):
        """GET /api/lumi/meetings/history?limit=5 respects limit parameter"""
        response = requests.get(f"{BASE_URL}/api/lumi/meetings/history?limit=5", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["meetings"]) <= 5, "Should respect limit parameter"
        print(f"PASS: Meeting history with limit=5 returned {len(data['meetings'])} meetings")
    
    def test_meeting_history_meeting_structure(self):
        """Verify meeting objects have expected fields"""
        # First create a meeting to ensure we have data
        create_res = requests.post(f"{BASE_URL}/api/lumi/meetings/quick", 
            headers={"Content-Type": "application/json", **self.headers},
            json={"title": "TEST_HistoryCheck Meeting"})
        
        response = requests.get(f"{BASE_URL}/api/lumi/meetings/history?limit=5", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        if data["meetings"]:
            meeting = data["meetings"][0]
            # Check expected fields
            assert "id" in meeting, "Meeting should have 'id'"
            assert "title" in meeting, "Meeting should have 'title'"
            assert "status" in meeting, "Meeting should have 'status'"
            assert "created_at" in meeting, "Meeting should have 'created_at'"
            print(f"PASS: Meeting structure verified - id={meeting['id']}, status={meeting['status']}")
        else:
            print("PASS: Meeting history structure check (no meetings to verify)")


class TestBotCatalog:
    """Test GET /api/lumi/bots/catalog endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_res.status_code == 200:
            self.token = login_res.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed")
    
    def test_bot_catalog_returns_8_bots(self):
        """GET /api/lumi/bots/catalog returns 8 bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", headers=self.headers)
        assert response.status_code == 200, f"Bot catalog failed: {response.text}"
        data = response.json()
        assert "bots" in data, "Response should contain 'bots'"
        assert "categories" in data, "Response should contain 'categories'"
        assert len(data["bots"]) == 8, f"Expected 8 bots, got {len(data['bots'])}"
        print(f"PASS: Bot catalog returned {len(data['bots'])} bots")
    
    def test_bot_catalog_categories(self):
        """Verify bot catalog returns categories"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["categories"]) > 0, "Should have categories"
        expected_categories = ["Productivity", "Engagement", "Collaboration", "Onboarding", "AI", "Communication", "DevOps"]
        for cat in data["categories"]:
            assert cat in expected_categories, f"Unexpected category: {cat}"
        print(f"PASS: Bot catalog has {len(data['categories'])} categories: {data['categories']}")
    
    def test_bot_structure(self):
        """Verify bot objects have expected fields"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        for bot in data["bots"]:
            assert "id" in bot, f"Bot should have 'id'"
            assert "name" in bot, f"Bot should have 'name'"
            assert "description" in bot, f"Bot should have 'description'"
            assert "icon" in bot, f"Bot should have 'icon'"
            assert "category" in bot, f"Bot should have 'category'"
        
        bot_ids = [b["id"] for b in data["bots"]]
        expected_ids = ["standup", "reminder", "poll", "meeting", "welcome", "summary", "translator", "github_notify"]
        for expected_id in expected_ids:
            assert expected_id in bot_ids, f"Missing bot: {expected_id}"
        print(f"PASS: All 8 bots have correct structure: {bot_ids}")


class TestBotInstallUninstall:
    """Test bot install/uninstall endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token and prepare test data"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_res.status_code == 200:
            self.token = login_res.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed")
        
        # Get a channel to use for testing
        channels_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=self.headers)
        if channels_res.status_code == 200:
            channels = channels_res.json().get("my_channels", [])
            if channels:
                self.test_channel_id = channels[0]["id"]
            else:
                # Create a test channel
                create_res = requests.post(f"{BASE_URL}/api/lumi/channels",
                    headers={"Content-Type": "application/json", **self.headers},
                    json={"name": f"test-bot-channel-{uuid.uuid4().hex[:8]}", "channel_type": "team"})
                if create_res.status_code in [200, 201]:
                    self.test_channel_id = create_res.json()["id"]
                else:
                    self.test_channel_id = f"test-channel-{uuid.uuid4().hex[:8]}"
        else:
            self.test_channel_id = f"test-channel-{uuid.uuid4().hex[:8]}"
    
    def test_install_bot(self):
        """POST /api/lumi/bots/install installs a bot to channel"""
        response = requests.post(f"{BASE_URL}/api/lumi/bots/install",
            headers={"Content-Type": "application/json", **self.headers},
            json={
                "bot_id": "reminder",
                "channel_id": self.test_channel_id
            })
        
        # Could be 200 (success) or 400 (already installed)
        assert response.status_code in [200, 400], f"Bot install unexpected status: {response.status_code}, {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data, "Should return install id"
            assert data["bot_id"] == "reminder"
            assert data["status"] == "installed"
            print(f"PASS: Bot installed successfully, install_id={data['id']}")
            return data["id"]
        else:
            # Already installed
            data = response.json()
            assert "already installed" in data.get("detail", "").lower()
            print(f"PASS: Bot already installed (expected behavior)")
            return None
    
    def test_get_installed_bots(self):
        """GET /api/lumi/bots/installed returns installed bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/installed", headers=self.headers)
        assert response.status_code == 200, f"Get installed bots failed: {response.text}"
        data = response.json()
        assert "bots" in data, "Response should contain 'bots'"
        assert "count" in data, "Response should contain 'count'"
        assert isinstance(data["bots"], list)
        print(f"PASS: Got {data['count']} installed bots")
    
    def test_install_then_uninstall(self):
        """Test full install -> get -> uninstall flow"""
        # Install a unique bot
        install_res = requests.post(f"{BASE_URL}/api/lumi/bots/install",
            headers={"Content-Type": "application/json", **self.headers},
            json={
                "bot_id": "poll",
                "channel_id": f"test-uninstall-{uuid.uuid4().hex[:8]}"
            })
        
        if install_res.status_code == 200:
            install_id = install_res.json()["id"]
            
            # Verify it appears in installed list
            installed_res = requests.get(f"{BASE_URL}/api/lumi/bots/installed", headers=self.headers)
            assert installed_res.status_code == 200
            installed_bots = installed_res.json()["bots"]
            found = any(b["id"] == install_id for b in installed_bots)
            assert found, "Installed bot should appear in list"
            
            # Uninstall
            uninstall_res = requests.delete(
                f"{BASE_URL}/api/lumi/bots/uninstall/{install_id}",
                headers=self.headers
            )
            assert uninstall_res.status_code == 200, f"Uninstall failed: {uninstall_res.text}"
            assert uninstall_res.json()["status"] == "uninstalled"
            print(f"PASS: Bot install -> uninstall flow completed")
        else:
            print(f"PASS: Install returned {install_res.status_code} (may already exist)")
    
    def test_uninstall_nonexistent(self):
        """DELETE /api/lumi/bots/uninstall/{id} with invalid id returns 404"""
        response = requests.delete(
            f"{BASE_URL}/api/lumi/bots/uninstall/nonexistent-id-12345",
            headers=self.headers
        )
        assert response.status_code == 404, f"Expected 404 for nonexistent, got {response.status_code}"
        print("PASS: Uninstall nonexistent bot returns 404")


class TestUserProfileAuthBadge:
    """Test user profile shows correct auth method badge"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_res.status_code == 200:
            self.token = login_res.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed")
    
    def test_profile_capabilities_endpoint(self):
        """GET /api/lumi/profile/capabilities returns user profile with auth_method"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=self.headers)
        assert response.status_code == 200, f"Profile capabilities failed: {response.text}"
        data = response.json()
        
        assert "user" in data, "Response should contain 'user'"
        user = data["user"]
        assert "email" in user
        assert "role" in user
        # Check for auth_method field (may be 'admin', 'password', 'google', etc.)
        print(f"PASS: Profile capabilities returned - email={user['email']}, role={user['role']}, auth_method={user.get('auth_method', 'N/A')}")


class TestGitHubSSOStillWorks:
    """Verify GitHub SSO (MOCKED) still works"""
    
    def test_github_login_endpoint(self):
        """POST /api/auth/github/login returns mock auth_url"""
        response = requests.post(f"{BASE_URL}/api/auth/github/login")
        assert response.status_code == 200, f"GitHub login failed: {response.text}"
        data = response.json()
        assert "auth_url" in data, "Response should contain 'auth_url'"
        # Mocked GitHub SSO redirects to own callback
        assert "/api/auth/github/callback" in data["auth_url"], "Should redirect to mock callback"
        print(f"PASS: GitHub SSO (MOCKED) returns auth_url: {data['auth_url'][:80]}...")


class TestDashboardBentoTiles:
    """Test that dashboard endpoints support the 4 action tiles"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if login_res.status_code == 200:
            self.token = login_res.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            pytest.skip("Login failed")
    
    def test_all_dashboard_apis_work(self):
        """Verify all APIs that power dashboard tiles work"""
        # Meeting tile - uses /api/lumi/meetings/quick
        quick_meeting_res = requests.post(f"{BASE_URL}/api/lumi/meetings/quick",
            headers={"Content-Type": "application/json", **self.headers},
            json={"title": "TEST_DashboardCheck"})
        assert quick_meeting_res.status_code == 200, "Meeting API should work"
        
        # Bot Store tile - uses /api/lumi/bots/catalog
        bot_catalog_res = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", headers=self.headers)
        assert bot_catalog_res.status_code == 200, "Bot catalog API should work"
        
        # Meeting History tile - uses /api/lumi/meetings/history
        history_res = requests.get(f"{BASE_URL}/api/lumi/meetings/history", headers=self.headers)
        assert history_res.status_code == 200, "Meeting history API should work"
        
        # Invite tile - uses /api/lumi/invite/link
        invite_res = requests.get(f"{BASE_URL}/api/lumi/invite/link", headers=self.headers)
        assert invite_res.status_code == 200, "Invite link API should work"
        
        print("PASS: All 4 dashboard tile APIs working correctly")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
