"""
Credly OAuth Integration Tests
Tests for Credly digital badge import functionality.
Endpoints: /credly/auth, /credly/callback, /credly/status, /credly/sync, /credly/disconnect, /credly/badges, /credly/supported-issuers
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER_EMAIL = "credlytest@test.com"
TEST_USER_PASSWORD = "Test123!"


class TestCredlyIntegration:
    """Credly OAuth integration tests"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Shared requests session"""
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    @pytest.fixture(scope="class")
    def auth_token(self, api_client):
        """Get authentication token for test user"""
        # First try to register the user (may already exist)
        register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": "Credly Test User",
            "role": "job_seeker"
        })
        
        # Login to get token
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            return data.get("token") or data.get("access_token")
        
        pytest.skip(f"Authentication failed: {login_response.status_code} - {login_response.text}")
    
    @pytest.fixture(scope="class")
    def authenticated_client(self, api_client, auth_token):
        """Session with auth header"""
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        return api_client
    
    # ============== Credly Auth Endpoint Tests ==============
    
    def test_credly_auth_returns_auth_url_and_state(self, authenticated_client):
        """Test GET /api/credentials/credly/auth returns auth_url and state"""
        response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/auth")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "auth_url" in data, "Response should contain auth_url"
        assert "state" in data, "Response should contain state"
        assert "message" in data, "Response should contain message"
        
        # Verify auth_url format
        assert "credly.com" in data["auth_url"], "auth_url should point to Credly"
        assert "oauth" in data["auth_url"], "auth_url should be OAuth endpoint"
        
        # Verify state is a valid UUID format
        assert len(data["state"]) == 36, "State should be a UUID"
        
        print(f"✓ Credly auth endpoint returned auth_url and state: {data['state'][:8]}...")
    
    def test_credly_auth_requires_authentication(self):
        """Test that /api/credentials/credly/auth requires authentication"""
        # Use a fresh session without auth
        fresh_session = requests.Session()
        fresh_session.headers.update({"Content-Type": "application/json"})
        response = fresh_session.get(f"{BASE_URL}/api/credentials/credly/auth")
        
        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"
        print("✓ Credly auth endpoint requires authentication")
    
    # ============== Credly Callback Tests ==============
    
    def test_credly_callback_with_demo_code(self, authenticated_client):
        """Test GET /api/credentials/credly/callback with demo code imports badges"""
        # First get auth to create state
        auth_response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/auth")
        assert auth_response.status_code == 200
        state = auth_response.json()["state"]
        
        # Call callback with demo code
        callback_response = authenticated_client.get(
            f"{BASE_URL}/api/credentials/credly/callback",
            params={"code": "demo_code", "state": state}
        )
        
        assert callback_response.status_code == 200, f"Expected 200, got {callback_response.status_code}: {callback_response.text}"
        
        data = callback_response.json()
        assert data.get("success") == True, "Callback should return success=True"
        assert "imported_count" in data, "Response should contain imported_count"
        assert "total_badges" in data, "Response should contain total_badges"
        assert data.get("simulated") == True, "Demo mode should set simulated=True"
        
        # Verify badges were imported (demo mode returns 5 badges)
        assert data["total_badges"] == 5, f"Expected 5 demo badges, got {data['total_badges']}"
        
        print(f"✓ Credly callback imported {data['imported_count']} badges (simulated mode)")
    
    def test_credly_callback_missing_code(self, authenticated_client):
        """Test callback fails without authorization code"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/credentials/credly/callback",
            params={"state": "some_state"}
        )
        
        assert response.status_code == 400, f"Expected 400 without code, got {response.status_code}"
        print("✓ Credly callback correctly rejects missing code")
    
    def test_credly_callback_invalid_state(self, authenticated_client):
        """Test callback fails with invalid state"""
        response = authenticated_client.get(
            f"{BASE_URL}/api/credentials/credly/callback",
            params={"code": "demo_code", "state": "invalid_state_token"}
        )
        
        assert response.status_code == 400, f"Expected 400 with invalid state, got {response.status_code}"
        print("✓ Credly callback correctly rejects invalid state")
    
    # ============== Credly Status Tests ==============
    
    def test_credly_status_shows_connected(self, authenticated_client):
        """Test GET /api/credentials/credly/status shows connection status"""
        response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "connected" in data, "Response should contain connected field"
        assert "message" in data, "Response should contain message"
        
        # After callback test, should be connected
        if data["connected"]:
            assert "connected_at" in data, "Connected status should include connected_at"
            print(f"✓ Credly status: Connected (simulated={data.get('simulated', False)})")
        else:
            print("✓ Credly status: Not connected")
    
    # ============== Credly Badges List Tests ==============
    
    def test_credly_badges_returns_imported_badges(self, authenticated_client):
        """Test GET /api/credentials/credly/badges returns imported badges"""
        response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/badges")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "badges" in data, "Response should contain badges array"
        assert "total" in data, "Response should contain total count"
        
        badges = data["badges"]
        if len(badges) > 0:
            # Verify badge structure
            badge = badges[0]
            assert "credential_name" in badge, "Badge should have credential_name"
            assert "source" in badge, "Badge should have source"
            assert badge["source"] == "credly", "Badge source should be 'credly'"
            
            # Check for Credly-specific fields
            assert "badge_image_url" in badge or "badge_url" in badge, "Badge should have image or URL"
            
            print(f"✓ Credly badges endpoint returned {len(badges)} badges")
            for b in badges[:3]:
                print(f"  - {b.get('credential_name', 'Unknown')}")
        else:
            print("✓ Credly badges endpoint returned empty list (no badges imported)")
    
    # ============== Credly Sync Tests ==============
    
    def test_credly_sync_badges(self, authenticated_client):
        """Test POST /api/credentials/credly/sync syncs badges"""
        response = authenticated_client.post(f"{BASE_URL}/api/credentials/credly/sync")
        
        # May fail if not connected
        if response.status_code == 400:
            data = response.json()
            assert "Not connected" in data.get("detail", ""), "Should indicate not connected"
            print("✓ Credly sync correctly requires connection first")
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Sync should return success=True"
        assert "imported_count" in data, "Response should contain imported_count"
        assert "updated_count" in data, "Response should contain updated_count"
        assert "total_badges" in data, "Response should contain total_badges"
        
        print(f"✓ Credly sync: {data['imported_count']} new, {data['updated_count']} updated")
    
    # ============== Credly Disconnect Tests ==============
    
    def test_credly_disconnect(self, authenticated_client):
        """Test DELETE /api/credentials/credly/disconnect removes connection"""
        response = authenticated_client.delete(f"{BASE_URL}/api/credentials/credly/disconnect")
        
        # May return 404 if not connected
        if response.status_code == 404:
            print("✓ Credly disconnect: No connection to remove")
            return
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("success") == True, "Disconnect should return success=True"
        
        # Verify disconnected
        status_response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/status")
        status_data = status_response.json()
        assert status_data.get("connected") == False, "Should be disconnected after disconnect"
        
        print("✓ Credly disconnected successfully")
    
    # ============== Supported Issuers Tests ==============
    
    def test_supported_issuers_returns_list(self, authenticated_client):
        """Test GET /api/credentials/credly/supported-issuers returns issuer list"""
        response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/supported-issuers")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "issuers" in data, "Response should contain issuers array"
        assert "total" in data, "Response should contain total count"
        
        issuers = data["issuers"]
        assert len(issuers) > 0, "Should have at least one issuer"
        
        # Verify issuer structure
        issuer = issuers[0]
        assert "name" in issuer, "Issuer should have name"
        assert "badges" in issuer, "Issuer should have badges list"
        
        # Check for expected issuers
        issuer_names = [i["name"] for i in issuers]
        expected_issuers = ["Amazon Web Services", "Microsoft", "Google Cloud", "Cisco", "CompTIA"]
        for expected in expected_issuers:
            assert expected in issuer_names, f"Expected issuer '{expected}' not found"
        
        print(f"✓ Supported issuers: {len(issuers)} issuers returned")
        print(f"  Includes: {', '.join(issuer_names[:5])}...")
    
    # ============== My Credentials with Credly Source Tests ==============
    
    def test_my_credentials_includes_credly_badges(self, authenticated_client):
        """Test GET /api/credentials/my-credentials includes Credly badges with source='credly'"""
        # First ensure we have badges by connecting
        auth_response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/auth")
        if auth_response.status_code == 200:
            state = auth_response.json()["state"]
            authenticated_client.get(
                f"{BASE_URL}/api/credentials/credly/callback",
                params={"code": "demo_code", "state": state}
            )
        
        # Get all credentials
        response = authenticated_client.get(f"{BASE_URL}/api/credentials/my-credentials")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "credentials" in data, "Response should contain credentials array"
        
        credentials = data["credentials"]
        credly_creds = [c for c in credentials if c.get("source") == "credly"]
        
        if len(credly_creds) > 0:
            # Verify Credly credential structure
            cred = credly_creds[0]
            assert cred.get("source") == "credly", "Source should be 'credly'"
            assert "credential_name" in cred, "Should have credential_name"
            assert "issuing_authority" in cred, "Should have issuing_authority"
            assert "status" in cred, "Should have status"
            
            # Check for Credly-specific fields
            assert "badge_image_url" in cred or "badge_url" in cred, "Should have badge image or URL"
            
            print(f"✓ My credentials includes {len(credly_creds)} Credly badges")
            for c in credly_creds[:3]:
                print(f"  - {c.get('credential_name')} ({c.get('issuing_authority')})")
        else:
            print("✓ My credentials endpoint works (no Credly badges currently)")


class TestCredlyFullFlow:
    """End-to-end Credly OAuth flow test"""
    
    @pytest.fixture(scope="class")
    def api_client(self):
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        return session
    
    @pytest.fixture(scope="class")
    def auth_token(self, api_client):
        # Create a fresh test user for full flow
        test_email = f"credlyflow_{int(time.time())}@test.com"
        
        register_response = api_client.post(f"{BASE_URL}/api/auth/register", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD,
            "name": "Credly Flow Test User",
            "role": "job_seeker"
        })
        
        login_response = api_client.post(f"{BASE_URL}/api/auth/login", json={
            "email": test_email,
            "password": TEST_USER_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            return data.get("token") or data.get("access_token")
        
        pytest.skip(f"Authentication failed: {login_response.status_code}")
    
    @pytest.fixture(scope="class")
    def authenticated_client(self, api_client, auth_token):
        api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
        return api_client
    
    def test_full_credly_oauth_flow(self, authenticated_client):
        """Test complete Credly OAuth flow: auth -> callback -> status -> badges -> sync -> disconnect"""
        
        # Step 1: Check initial status (should be disconnected)
        status_response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/status")
        assert status_response.status_code == 200
        assert status_response.json().get("connected") == False
        print("Step 1: Initial status - Not connected ✓")
        
        # Step 2: Initiate OAuth
        auth_response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/auth")
        assert auth_response.status_code == 200
        auth_data = auth_response.json()
        assert "auth_url" in auth_data
        assert "state" in auth_data
        state = auth_data["state"]
        print(f"Step 2: OAuth initiated - State: {state[:8]}... ✓")
        
        # Step 3: Simulate callback (demo mode)
        callback_response = authenticated_client.get(
            f"{BASE_URL}/api/credentials/credly/callback",
            params={"code": "demo_code", "state": state}
        )
        assert callback_response.status_code == 200
        callback_data = callback_response.json()
        assert callback_data.get("success") == True
        imported_count = callback_data.get("imported_count", 0)
        print(f"Step 3: Callback processed - Imported {imported_count} badges ✓")
        
        # Step 4: Verify connected status
        status_response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data.get("connected") == True
        print(f"Step 4: Status verified - Connected (simulated={status_data.get('simulated')}) ✓")
        
        # Step 5: Get badges
        badges_response = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/badges")
        assert badges_response.status_code == 200
        badges_data = badges_response.json()
        assert len(badges_data.get("badges", [])) > 0
        print(f"Step 5: Badges retrieved - {len(badges_data['badges'])} badges ✓")
        
        # Step 6: Sync badges
        sync_response = authenticated_client.post(f"{BASE_URL}/api/credentials/credly/sync")
        assert sync_response.status_code == 200
        sync_data = sync_response.json()
        assert sync_data.get("success") == True
        print(f"Step 6: Sync completed - {sync_data.get('updated_count', 0)} updated ✓")
        
        # Step 7: Verify in my-credentials
        creds_response = authenticated_client.get(f"{BASE_URL}/api/credentials/my-credentials")
        assert creds_response.status_code == 200
        creds_data = creds_response.json()
        credly_creds = [c for c in creds_data.get("credentials", []) if c.get("source") == "credly"]
        assert len(credly_creds) > 0
        print(f"Step 7: My credentials includes {len(credly_creds)} Credly badges ✓")
        
        # Step 8: Disconnect
        disconnect_response = authenticated_client.delete(f"{BASE_URL}/api/credentials/credly/disconnect")
        assert disconnect_response.status_code == 200
        assert disconnect_response.json().get("success") == True
        print("Step 8: Disconnected successfully ✓")
        
        # Step 9: Verify disconnected
        final_status = authenticated_client.get(f"{BASE_URL}/api/credentials/credly/status")
        assert final_status.status_code == 200
        assert final_status.json().get("connected") == False
        print("Step 9: Final status - Not connected ✓")
        
        print("\n✓ Full Credly OAuth flow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
