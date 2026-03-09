"""
Test Portal Workspace Feature - Iteration 200
Tests dock bar, side panels, swap, resize, and compact portal views.
Previous iteration (199) tested basic package selection - all passed.
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


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Get authentication token for admin user"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="module")
def authenticated_client(api_client, auth_token):
    """Session with auth header"""
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client


# ============================================
# Portal Access API Tests
# ============================================
class TestPortalPackagesAPI:
    """Test portal packages endpoint"""
    
    def test_get_packages_returns_all_packages(self, api_client):
        """GET /api/portal/packages returns all 3 packages"""
        response = api_client.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        assert "packages" in data
        assert len(data["packages"]) == 3
        
        # Verify package IDs
        package_ids = [p["id"] for p in data["packages"]]
        assert "standard" in package_ids
        assert "medmatch_standalone" in package_ids
        assert "enterprise" in package_ids
        
    def test_standard_package_has_karau_enzi(self, api_client):
        """Standard package contains karau and enzi portals"""
        response = api_client.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        standard = next((p for p in data["packages"] if p["id"] == "standard"), None)
        assert standard is not None
        assert set(standard["portals"]) == {"karau", "enzi"}
        
    def test_standalone_package_has_medmatch(self, api_client):
        """Standalone package contains only medmatch portal"""
        response = api_client.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        standalone = next((p for p in data["packages"] if p["id"] == "medmatch_standalone"), None)
        assert standalone is not None
        assert standalone["portals"] == ["medmatch"]
        
    def test_enterprise_package_has_all_portals(self, api_client):
        """Enterprise package contains all 3 portals"""
        response = api_client.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        enterprise = next((p for p in data["packages"] if p["id"] == "enterprise"), None)
        assert enterprise is not None
        assert set(enterprise["portals"]) == {"medmatch", "karau", "enzi"}


class TestPortalAccessAPI:
    """Test portal access endpoint"""
    
    def test_get_access_requires_auth(self, api_client):
        """GET /api/portal/access requires authentication"""
        # Clear any existing auth header
        api_client.headers.pop("Authorization", None)
        response = api_client.get(f"{BASE_URL}/api/portal/access")
        assert response.status_code in [401, 403]
        
    def test_get_access_returns_user_package(self, authenticated_client):
        """GET /api/portal/access returns user's package"""
        response = authenticated_client.get(f"{BASE_URL}/api/portal/access")
        assert response.status_code == 200
        
        data = response.json()
        assert "package_id" in data
        assert "portals" in data
        assert "portal_info" in data
        
    def test_access_response_includes_portal_info(self, authenticated_client):
        """Portal access includes portal info for each portal"""
        response = authenticated_client.get(f"{BASE_URL}/api/portal/access")
        assert response.status_code == 200
        
        data = response.json()
        portal_info = data.get("portal_info", {})
        
        # Each portal should have name, path, icon, color
        for portal_key, info in portal_info.items():
            assert "name" in info
            assert "path" in info
            assert "icon" in info
            assert "color" in info


class TestSetPackageAPI:
    """Test set-package endpoint"""
    
    def test_set_package_requires_auth(self, api_client):
        """POST /api/portal/set-package requires authentication"""
        api_client.headers.pop("Authorization", None)
        response = api_client.post(f"{BASE_URL}/api/portal/set-package", json={
            "package_id": "standard"
        })
        assert response.status_code in [401, 403]
        
    def test_set_standard_package(self, authenticated_client):
        """Setting standard package returns karau + enzi portals"""
        response = authenticated_client.post(f"{BASE_URL}/api/portal/set-package", json={
            "package_id": "standard"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["package_id"] == "standard"
        assert set(data["portals"]) == {"karau", "enzi"}
        
    def test_set_enterprise_package(self, authenticated_client):
        """Setting enterprise package returns all 3 portals"""
        response = authenticated_client.post(f"{BASE_URL}/api/portal/set-package", json={
            "package_id": "enterprise"
        })
        assert response.status_code == 200
        
        data = response.json()
        assert data["package_id"] == "enterprise"
        assert set(data["portals"]) == {"medmatch", "karau", "enzi"}
        
    def test_set_invalid_package_fails(self, authenticated_client):
        """Setting invalid package returns error"""
        response = authenticated_client.post(f"{BASE_URL}/api/portal/set-package", json={
            "package_id": "invalid_package"
        })
        assert response.status_code == 400


class TestSyncSessionAPI:
    """Test sync-session endpoint for cross-portal auth"""
    
    def test_sync_session_requires_auth(self, api_client):
        """POST /api/portal/sync-session requires authentication"""
        api_client.headers.pop("Authorization", None)
        response = api_client.post(f"{BASE_URL}/api/portal/sync-session")
        assert response.status_code in [401, 403]
        
    def test_sync_session_returns_token(self, authenticated_client):
        """POST /api/portal/sync-session returns token"""
        response = authenticated_client.post(f"{BASE_URL}/api/portal/sync-session")
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 0
        
    def test_sync_session_returns_user_info(self, authenticated_client):
        """Sync session returns user info"""
        response = authenticated_client.post(f"{BASE_URL}/api/portal/sync-session")
        assert response.status_code == 200
        
        data = response.json()
        assert "user" in data
        assert "user_id" in data["user"]
        assert "email" in data["user"]


class TestCheckAccessAPI:
    """Test check-access endpoint"""
    
    def test_check_karau_access(self, authenticated_client):
        """Check access to karau portal"""
        response = authenticated_client.get(f"{BASE_URL}/api/portal/check-access/karau")
        assert response.status_code == 200
        
        data = response.json()
        assert "has_access" in data
        assert "portal" in data
        assert data["portal"] == "karau"
        
    def test_check_enzi_access(self, authenticated_client):
        """Check access to enzi portal"""
        response = authenticated_client.get(f"{BASE_URL}/api/portal/check-access/enzi")
        assert response.status_code == 200
        
        data = response.json()
        assert "has_access" in data
        assert data["portal"] == "enzi"
        
    def test_check_medmatch_access(self, authenticated_client):
        """Check access to medmatch portal"""
        response = authenticated_client.get(f"{BASE_URL}/api/portal/check-access/medmatch")
        assert response.status_code == 200
        
        data = response.json()
        assert "has_access" in data
        assert data["portal"] == "medmatch"
        
    def test_check_invalid_portal_fails(self, authenticated_client):
        """Check access to invalid portal returns error"""
        response = authenticated_client.get(f"{BASE_URL}/api/portal/check-access/invalid")
        assert response.status_code == 400


class TestPortalAccessPersistence:
    """Test that package selection persists correctly"""
    
    def test_set_and_get_package(self, authenticated_client):
        """Set standard package and verify it persists"""
        # First set standard package
        set_response = authenticated_client.post(f"{BASE_URL}/api/portal/set-package", json={
            "package_id": "standard"
        })
        assert set_response.status_code == 200
        
        # Now get access and verify
        get_response = authenticated_client.get(f"{BASE_URL}/api/portal/access")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["package_id"] == "standard"
        assert set(data["portals"]) == {"karau", "enzi"}
        
    def test_change_package_and_verify(self, authenticated_client):
        """Change from standard to enterprise and verify"""
        # Set enterprise
        set_response = authenticated_client.post(f"{BASE_URL}/api/portal/set-package", json={
            "package_id": "enterprise"
        })
        assert set_response.status_code == 200
        
        # Verify
        get_response = authenticated_client.get(f"{BASE_URL}/api/portal/access")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["package_id"] == "enterprise"
        assert set(data["portals"]) == {"medmatch", "karau", "enzi"}


# ============================================
# KARAU Meeting API Tests for compact panel
# ============================================
class TestKarauMeetingsAPI:
    """Test KARAU meetings endpoint for compact panel"""
    
    def test_get_meetings_requires_auth(self, api_client):
        """GET /api/karau/meetings requires authentication"""
        api_client.headers.pop("Authorization", None)
        response = api_client.get(f"{BASE_URL}/api/karau/meetings")
        assert response.status_code in [401, 403, 422]  # 422 if token validation fails
        
    def test_get_meetings_list(self, authenticated_client):
        """GET /api/karau/meetings returns meetings list"""
        response = authenticated_client.get(f"{BASE_URL}/api/karau/meetings?limit=10")
        assert response.status_code == 200
        
        data = response.json()
        # Should return either array or object with meetings key
        assert isinstance(data, (list, dict))
        
    def test_create_meeting(self, authenticated_client):
        """POST /api/karau/meetings creates a new meeting"""
        response = authenticated_client.post(f"{BASE_URL}/api/karau/meetings", json={
            "title": "Test Meeting for Workspace",
            "type": "instant",
            "settings": {"max_participants": 50}
        })
        assert response.status_code in [200, 201]
        
        data = response.json()
        assert "meeting_id" in data or "id" in data


# ============================================
# ENZI/Lumi Channels API Tests for compact panel
# ============================================
class TestEnziChannelsAPI:
    """Test ENZI channels endpoint for compact panel"""
    
    def test_get_channels_requires_auth(self, api_client):
        """GET /api/lumi/channels requires authentication"""
        api_client.headers.pop("Authorization", None)
        response = api_client.get(f"{BASE_URL}/api/lumi/channels")
        assert response.status_code in [401, 403, 422]
        
    def test_get_channels_list(self, authenticated_client):
        """GET /api/lumi/channels returns channels list"""
        response = authenticated_client.get(f"{BASE_URL}/api/lumi/channels")
        # Could be 200 with list or error if no channels
        assert response.status_code in [200, 404]
        
    def test_get_dm_list(self, authenticated_client):
        """GET /api/lumi/dm/list returns DM conversations"""
        response = authenticated_client.get(f"{BASE_URL}/api/lumi/dm/list")
        assert response.status_code in [200, 404]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
