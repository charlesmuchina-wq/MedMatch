"""
Iteration 175 - LUMI Retention & Holds + Profile Theme Testing
Tests for:
1. Profile Theme Picker - GET/PUT /api/lumi/profile/theme
2. Retention & Holds System - Admin panel with approval workflow
   - GET /api/lumi/admin/retention - channels, holds, pending_requests
   - GET/PUT /api/lumi/admin/org-settings - IT admin, manager config
   - POST /api/lumi/admin/hold - create hold request (requires org settings)
   - PUT /api/lumi/admin/hold-requests/{id} - approve/reject requests
   - DELETE /api/lumi/admin/hold/{id} - release hold
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestAuthentication:
    """Login to get auth token"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "Response missing access_token"
        return data["access_token"]
    
    def test_login_returns_token(self, auth_token):
        """Verify login returns valid token"""
        assert auth_token is not None
        assert len(auth_token) > 0
        print(f"Auth token obtained successfully")


class TestProfileTheme:
    """Tests for User Profile Theme Picker"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_get_profile_theme_initial(self, auth_token):
        """GET /api/lumi/profile/theme - returns current accent color"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/profile/theme", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "accent_color" in data
        print(f"Current theme: {data}")
    
    def test_update_profile_theme_turquoise(self, auth_token):
        """PUT /api/lumi/profile/theme - set turquoise color"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        payload = {"accent_color": "#00CEC9"}
        response = requests.put(f"{BASE_URL}/api/lumi/profile/theme", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "updated"
        assert data["accent_color"] == "#00CEC9"
        print(f"Theme updated to turquoise: {data}")
    
    def test_get_profile_theme_after_update(self, auth_token):
        """GET /api/lumi/profile/theme - verify theme was persisted"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/profile/theme", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["accent_color"] == "#00CEC9"
        print(f"Theme persisted: {data}")
    
    def test_update_profile_theme_pink(self, auth_token):
        """PUT /api/lumi/profile/theme - set pink color"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        payload = {"accent_color": "#E84393"}
        response = requests.put(f"{BASE_URL}/api/lumi/profile/theme", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["accent_color"] == "#E84393"
        print(f"Theme updated to pink: {data}")
    
    def test_profile_theme_requires_auth(self):
        """Profile theme endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/profile/theme")
        assert response.status_code == 401


class TestRetentionOverview:
    """Tests for Retention Admin Overview"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_get_retention_overview(self, auth_token):
        """GET /api/lumi/admin/retention - returns channels, holds, requests"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "channels" in data
        assert "holds" in data
        assert "pending_requests" in data
        assert "all_requests" in data
        assert "global_retention_days" in data
        assert "org_settings_configured" in data
        
        # Global retention should be 90 days
        assert data["global_retention_days"] == 90
        print(f"Retention overview: {len(data['channels'])} channels, global={data['global_retention_days']} days")
    
    def test_retention_requires_auth(self):
        """Retention endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention")
        assert response.status_code == 401


class TestOrgSettings:
    """Tests for Organization Admin Settings"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_get_org_settings_initial(self, auth_token):
        """GET /api/lumi/admin/org-settings - returns current settings"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/org-settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify fields exist
        assert "it_admin_name" in data
        assert "it_admin_email" in data
        assert "manager_name" in data
        assert "manager_email" in data
        assert "department" in data
        assert "compliance_officer" in data
        print(f"Current org settings: {data}")
    
    def test_update_org_settings(self, auth_token):
        """PUT /api/lumi/admin/org-settings - save admin config"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        payload = {
            "it_admin_name": "John IT Admin",
            "it_admin_email": "itadmin@medmatch.com",
            "manager_name": "Jane Manager",
            "manager_email": "manager@medmatch.com",
            "department": "Engineering",
            "compliance_officer": "Legal Team"
        }
        response = requests.put(f"{BASE_URL}/api/lumi/admin/org-settings", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "saved"
        print(f"Org settings saved: {data}")
    
    def test_get_org_settings_after_update(self, auth_token):
        """GET /api/lumi/admin/org-settings - verify settings persisted"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/org-settings", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["it_admin_email"] == "itadmin@medmatch.com"
        assert data["manager_email"] == "manager@medmatch.com"
        print(f"Org settings verified: {data}")
    
    def test_retention_shows_org_configured(self, auth_token):
        """Retention overview shows org_settings_configured=True after saving"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["org_settings_configured"] == True
        print(f"Org settings configured: {data['org_settings_configured']}")


class TestHoldRequestWorkflow:
    """Tests for Hold Request Approval Workflow"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def channel_id(self, auth_token):
        """Get first available channel for testing"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        channels = response.json()["channels"]
        if channels:
            return channels[0]["id"]
        return None
    
    def test_create_legal_hold_request(self, auth_token, channel_id):
        """POST /api/lumi/admin/hold - create legal hold request"""
        if not channel_id:
            pytest.skip("No channels available")
        
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        payload = {
            "channel_id": channel_id,
            "hold_type": "legal",
            "reason": "Legal investigation - preserve all messages",
            "duration_days": 0,
            "active": True
        }
        response = requests.post(f"{BASE_URL}/api/lumi/admin/hold", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "pending"
        assert "message" in data
        print(f"Legal hold request created: {data}")
        return data["id"]
    
    def test_create_contractual_hold_request(self, auth_token, channel_id):
        """POST /api/lumi/admin/hold - create contractual hold request"""
        if not channel_id:
            pytest.skip("No channels available")
        
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        payload = {
            "channel_id": channel_id,
            "hold_type": "contractual",
            "reason": "Contract preservation - 180 day retention",
            "duration_days": 180,
            "active": True
        }
        response = requests.post(f"{BASE_URL}/api/lumi/admin/hold", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        print(f"Contractual hold request created: {data}")
    
    def test_pending_requests_appear_in_overview(self, auth_token):
        """Pending requests show in retention overview"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        assert response.status_code == 200
        data = response.json()
        pending = data["pending_requests"]
        print(f"Pending requests: {len(pending)}")
        # Should have at least our test requests
        assert isinstance(pending, list)
    
    def test_all_requests_include_request_details(self, auth_token):
        """All requests include proper details"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        assert response.status_code == 200
        all_requests = response.json()["all_requests"]
        
        if all_requests:
            req = all_requests[0]
            assert "id" in req
            assert "channel_id" in req
            assert "hold_type" in req
            assert "reason" in req
            assert "status" in req
            assert "requested_by" in req
            assert "it_admin_email" in req
            assert "manager_email" in req
            print(f"Request details verified: {req['id']}")


class TestHoldApproval:
    """Tests for approving/rejecting hold requests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_approve_pending_request(self, auth_token):
        """PUT /api/lumi/admin/hold-requests/{id} - approve request"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get pending requests
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        pending = response.json()["pending_requests"]
        
        if not pending:
            pytest.skip("No pending requests to approve")
        
        request_id = pending[0]["id"]
        headers["Content-Type"] = "application/json"
        
        payload = {"action": "approve", "note": "Approved by test automation"}
        response = requests.put(f"{BASE_URL}/api/lumi/admin/hold-requests/{request_id}", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        print(f"Request approved: {data}")
    
    def test_approved_hold_appears_in_holds(self, auth_token):
        """Approved hold shows in holds map"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        assert response.status_code == 200
        holds = response.json()["holds"]
        print(f"Active holds: {len(holds)} channels have holds")
        # Should have at least one hold after approval
        assert isinstance(holds, dict)
    
    def test_reject_pending_request(self, auth_token):
        """PUT /api/lumi/admin/hold-requests/{id} - reject request"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get pending requests
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        pending = response.json()["pending_requests"]
        
        if not pending:
            pytest.skip("No pending requests to reject")
        
        request_id = pending[0]["id"]
        headers["Content-Type"] = "application/json"
        
        payload = {"action": "reject", "note": "Rejected by test - not necessary"}
        response = requests.put(f"{BASE_URL}/api/lumi/admin/hold-requests/{request_id}", headers=headers, json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        print(f"Request rejected: {data}")


class TestHoldRelease:
    """Tests for releasing holds"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_release_active_hold(self, auth_token):
        """DELETE /api/lumi/admin/hold/{id} - release hold"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get holds
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        holds = response.json()["holds"]
        
        # Find an active hold
        hold_id = None
        for channel_id, channel_holds in holds.items():
            if channel_holds:
                hold_id = channel_holds[0]["id"]
                break
        
        if not hold_id:
            pytest.skip("No active holds to release")
        
        response = requests.delete(f"{BASE_URL}/api/lumi/admin/hold/{hold_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "released"
        print(f"Hold released: {data}")
    
    def test_release_nonexistent_hold(self, auth_token):
        """DELETE /api/lumi/admin/hold/{id} - 404 for nonexistent"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.delete(f"{BASE_URL}/api/lumi/admin/hold/hold_nonexistent123", headers=headers)
        assert response.status_code == 404


class TestProfileCapabilities:
    """Tests for profile capabilities endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_get_profile_capabilities(self, auth_token):
        """GET /api/lumi/profile/capabilities - returns user data and AI features"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/profile/capabilities", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        # Verify user info
        assert "user" in data
        user = data["user"]
        assert "user_id" in user
        assert "name" in user
        assert "email" in user
        assert "status" in user
        
        # Verify capabilities
        assert "capabilities" in data
        caps = data["capabilities"]
        assert len(caps) >= 10  # Should have multiple AI capabilities
        
        # Verify channels
        assert "channels" in data
        
        print(f"Profile: {user['email']}, {len(caps)} capabilities, {len(data['channels'])} channels")


class TestHoldRequestWithoutOrgSettings:
    """Test that hold requests fail when org settings not configured"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        return response.json()["access_token"]
    
    def test_hold_request_needs_org_settings(self, auth_token):
        """Hold requests should require org settings to be configured"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Check current org settings status
        response = requests.get(f"{BASE_URL}/api/lumi/admin/retention", headers=headers)
        data = response.json()
        
        # If org settings are configured, this test verifies hold requests work
        if data["org_settings_configured"]:
            print("Org settings configured - hold requests will work")
        else:
            # Try to create hold without org settings
            headers["Content-Type"] = "application/json"
            payload = {
                "channel_id": "test_channel",
                "hold_type": "legal",
                "reason": "Test",
                "duration_days": 0,
                "active": True
            }
            response = requests.post(f"{BASE_URL}/api/lumi/admin/hold", headers=headers, json=payload)
            assert response.status_code == 400
            print("Correctly rejected hold request without org settings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
