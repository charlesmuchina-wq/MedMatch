"""
Test E2EE (End-to-End Encryption) APIs - Batch B
- Key management: publish, retrieve, status
- E2EE enable/disable for users
- DM channel E2EE status
- Integration with existing features
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://karau-enzi-nexus.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture(scope="module")
def admin_token():
    """Get admin auth token"""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def admin_user(admin_token):
    """Get admin user info"""
    res = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    return res.json()


@pytest.fixture(scope="module")
def test_token():
    """Get test user auth token"""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if res.status_code != 200:
        pytest.skip(f"Test user login failed: {res.text}")
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def test_user(test_token):
    """Get test user info"""
    res = requests.get(f"{BASE_URL}/api/auth/me", headers={"Authorization": f"Bearer {test_token}"})
    if res.status_code != 200:
        pytest.skip("Test user auth failed")
    return res.json()


class TestE2EEKeyStatus:
    """Tests for E2EE key status endpoint - GET /api/lumi/e2ee/keys/status/me"""

    def test_get_e2ee_status_authenticated(self, admin_token):
        """Test that authenticated user can check their E2EE status"""
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/status/me",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        # Response should have enabled and has_public_key fields
        assert "enabled" in data, "Response should have 'enabled' field"
        assert "has_public_key" in data, "Response should have 'has_public_key' field"
        assert isinstance(data["enabled"], bool), "'enabled' should be boolean"
        assert isinstance(data["has_public_key"], bool), "'has_public_key' should be boolean"
        print(f"Admin E2EE status: enabled={data['enabled']}, has_public_key={data['has_public_key']}")

    def test_get_e2ee_status_unauthenticated(self):
        """Test that unauthenticated request returns 401"""
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/status/me")
        assert res.status_code == 401, f"Expected 401, got {res.status_code}"


class TestE2EEKeyPublish:
    """Tests for E2EE key publish endpoint - POST /api/lumi/e2ee/keys/publish"""

    def test_publish_public_key(self, admin_token, admin_user):
        """Test publishing a public key"""
        # Sample JWK format public key
        sample_public_key = '{"kty":"EC","crv":"P-256","x":"test_x_coordinate_base64","y":"test_y_coordinate_base64"}'
        
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/keys/publish",
                           headers={"Authorization": f"Bearer {admin_token}",
                                   "Content-Type": "application/json"},
                           json={"public_key": sample_public_key})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("status") == "published", f"Expected 'published' status, got {data}"
        assert "user_id" in data, "Response should contain user_id"
        print(f"Published key for user: {data['user_id']}")

    def test_publish_key_unauthenticated(self):
        """Test that unauthenticated request returns 401"""
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/keys/publish",
                           headers={"Content-Type": "application/json"},
                           json={"public_key": "test"})
        assert res.status_code == 401


class TestE2EEKeyRetrieval:
    """Tests for E2EE key retrieval endpoint - GET /api/lumi/e2ee/keys/{user_id}"""

    def test_get_public_key_existing_user(self, admin_token, admin_user):
        """Test retrieving a user's public key"""
        user_id = admin_user.get("user_id")
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/{user_id}",
                          headers={"Authorization": f"Bearer {admin_token}"})
        # If key exists, should return 200; if not, 404
        assert res.status_code in [200, 404], f"Expected 200 or 404, got {res.status_code}"
        if res.status_code == 200:
            data = res.json()
            assert "user_id" in data
            assert "public_key" in data
            print(f"Retrieved key for user {user_id}")
        else:
            print(f"No key published yet for user {user_id}")

    def test_get_public_key_nonexistent_user(self, admin_token):
        """Test retrieving key for nonexistent user returns 404"""
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/nonexistent_user_12345",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 404, f"Expected 404, got {res.status_code}"

    def test_get_public_key_unauthenticated(self):
        """Test that unauthenticated request returns 401"""
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/some_user_id")
        assert res.status_code == 401


class TestE2EEEnableDisable:
    """Tests for E2EE enable/disable endpoints"""

    def test_enable_e2ee(self, admin_token):
        """Test POST /api/lumi/e2ee/enable - enables E2EE for user"""
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/enable",
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("status") == "enabled", f"Expected 'enabled' status, got {data}"
        assert "message" in data
        print(f"E2EE enabled: {data['message']}")

    def test_enable_e2ee_unauthenticated(self):
        """Test that unauthenticated request returns 401"""
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/enable")
        assert res.status_code == 401

    def test_disable_e2ee(self, admin_token):
        """Test POST /api/lumi/e2ee/disable - disables E2EE and removes keys"""
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/disable",
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("status") == "disabled", f"Expected 'disabled' status, got {data}"
        assert "message" in data
        print(f"E2EE disabled: {data['message']}")

        # Re-enable for further tests
        requests.post(f"{BASE_URL}/api/lumi/e2ee/enable",
                     headers={"Authorization": f"Bearer {admin_token}"})

    def test_disable_e2ee_unauthenticated(self):
        """Test that unauthenticated request returns 401"""
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/disable")
        assert res.status_code == 401


class TestE2EEDMStatus:
    """Tests for DM E2EE status endpoint - GET /api/lumi/e2ee/dm/{channel_id}/status"""

    def test_get_dm_e2ee_status_valid_channel(self, admin_token):
        """Test getting E2EE status for a DM channel"""
        # First get list of DMs
        res = requests.get(f"{BASE_URL}/api/lumi/dm",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Failed to get DMs: {res.text}"
        dms = res.json().get("dms", [])
        
        if len(dms) == 0:
            pytest.skip("No DM channels available to test E2EE status")
        
        # Test with first DM channel
        dm_channel_id = dms[0]["id"]
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/dm/{dm_channel_id}/status",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert "encrypted" in data, "Response should have 'encrypted' field"
        assert "my_key_published" in data, "Response should have 'my_key_published' field"
        assert "partner_key_available" in data, "Response should have 'partner_key_available' field"
        print(f"DM {dm_channel_id} E2EE status: encrypted={data['encrypted']}, my_key={data['my_key_published']}, partner_key={data['partner_key_available']}")

    def test_get_dm_e2ee_status_non_dm_channel(self, admin_token):
        """Test that non-DM channel returns 'Not a DM channel' status"""
        # Get regular channels
        res = requests.get(f"{BASE_URL}/api/lumi/channels",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        channels = res.json().get("my_channels", [])
        
        # Find a non-DM channel
        non_dm = next((ch for ch in channels if ch.get("channel_type") != "dm"), None)
        if not non_dm:
            pytest.skip("No non-DM channel available for test")
        
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/dm/{non_dm['id']}/status",
                          headers={"Authorization": f"Bearer {admin_token}"})
        # Should still return 200 but with encrypted=False and reason
        assert res.status_code == 200
        data = res.json()
        assert data.get("encrypted") == False
        print(f"Non-DM channel E2EE status: {data}")

    def test_get_dm_e2ee_status_unauthenticated(self):
        """Test that unauthenticated request returns 401"""
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/dm/some_channel_id/status")
        assert res.status_code == 401


class TestExistingFeaturesIntegration:
    """Tests to ensure existing features still work with E2EE integration"""

    def test_login_works(self):
        """Test that login works with admin credentials"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert res.status_code == 200, f"Login failed: {res.text}"
        data = res.json()
        assert "access_token" in data
        assert "user" in data
        print("Login successful")

    def test_channels_api_works(self, admin_token):
        """Test that channels API still works"""
        res = requests.get(f"{BASE_URL}/api/lumi/channels",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Channels API failed: {res.text}"
        data = res.json()
        assert "my_channels" in data or "discover" in data
        print(f"Channels loaded: {len(data.get('my_channels', []))} my_channels")

    def test_dm_api_works(self, admin_token):
        """Test that DM API still works"""
        res = requests.get(f"{BASE_URL}/api/lumi/dm",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"DM API failed: {res.text}"
        data = res.json()
        assert "dms" in data
        print(f"DMs loaded: {len(data.get('dms', []))}")

    def test_bot_store_works(self, admin_token):
        """Test that Bot Store API still works"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/catalog",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Bot Store failed: {res.text}"
        print("Bot Store API working")

    def test_meeting_history_works(self, admin_token):
        """Test that Meeting History API still works"""
        res = requests.get(f"{BASE_URL}/api/lumi/meetings/history",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Meeting History failed: {res.text}"
        print("Meeting History API working")

    def test_predictive_nav_works(self, admin_token):
        """Test that Predictive Navigation API still works"""
        res = requests.get(f"{BASE_URL}/api/lumi/predict/suggestions",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200, f"Predictions API failed: {res.text}"
        data = res.json()
        assert "channels" in data or "dms" in data
        print("Predictive Navigation API working")


class TestE2EEWorkflow:
    """Tests for complete E2EE workflow"""

    def test_full_e2ee_workflow(self, admin_token, admin_user):
        """Test complete E2EE enable/key-publish/status workflow"""
        # Step 1: Check initial status
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/status/me",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        initial_status = res.json()
        print(f"1. Initial status: {initial_status}")

        # Step 2: Enable E2EE
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/enable",
                           headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        print("2. E2EE enabled")

        # Step 3: Publish key
        test_key = '{"kty":"EC","crv":"P-256","x":"workflow_test_x","y":"workflow_test_y"}'
        res = requests.post(f"{BASE_URL}/api/lumi/e2ee/keys/publish",
                           headers={"Authorization": f"Bearer {admin_token}",
                                   "Content-Type": "application/json"},
                           json={"public_key": test_key})
        assert res.status_code == 200
        print("3. Key published")

        # Step 4: Verify status shows key published
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/status/me",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        final_status = res.json()
        assert final_status["has_public_key"] == True, "Expected has_public_key=True after publishing"
        print(f"4. Final status: {final_status}")

        # Step 5: Retrieve key to verify
        user_id = admin_user.get("user_id")
        res = requests.get(f"{BASE_URL}/api/lumi/e2ee/keys/{user_id}",
                          headers={"Authorization": f"Bearer {admin_token}"})
        assert res.status_code == 200
        key_data = res.json()
        assert key_data["public_key"] == test_key
        print(f"5. Retrieved key matches published key")

        print("Full E2EE workflow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
