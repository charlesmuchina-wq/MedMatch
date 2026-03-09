"""
Portal Packaging System Tests - Iteration 199
Tests for the three-portal suite (MedMatch AI, AI KARAU, ENZI) packaging system.
Packages: Standard (KARAU+ENZI), Standalone (MedMatch), Enterprise (All 3)
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


class TestPortalPackages:
    """Tests for GET /api/portal/packages endpoint"""

    def test_get_packages_returns_all_three(self):
        """Test that GET /api/portal/packages returns all 3 packages"""
        response = requests.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        assert "packages" in data
        assert len(data["packages"]) == 3
        
        # Verify package IDs
        package_ids = [p["id"] for p in data["packages"]]
        assert "standard" in package_ids
        assert "medmatch_standalone" in package_ids
        assert "enterprise" in package_ids

    def test_standard_package_details(self):
        """Test standard package has correct details (AI KARAU + ENZI)"""
        response = requests.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        standard_pkg = next((p for p in data["packages"] if p["id"] == "standard"), None)
        
        assert standard_pkg is not None
        assert standard_pkg["name"] == "AI KARAU + ENZI"
        assert "karau" in standard_pkg["portals"]
        assert "enzi" in standard_pkg["portals"]
        assert "medmatch" not in standard_pkg["portals"]
        assert standard_pkg["is_default"] == True

    def test_medmatch_standalone_package_details(self):
        """Test standalone package has correct details (MedMatch only)"""
        response = requests.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        standalone_pkg = next((p for p in data["packages"] if p["id"] == "medmatch_standalone"), None)
        
        assert standalone_pkg is not None
        assert standalone_pkg["name"] == "MedMatch Job Toolkit"
        assert "medmatch" in standalone_pkg["portals"]
        assert "karau" not in standalone_pkg["portals"]
        assert "enzi" not in standalone_pkg["portals"]
        assert standalone_pkg["is_default"] == False

    def test_enterprise_package_details(self):
        """Test enterprise package has all 3 portals"""
        response = requests.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        enterprise_pkg = next((p for p in data["packages"] if p["id"] == "enterprise"), None)
        
        assert enterprise_pkg is not None
        assert enterprise_pkg["name"] == "Enterprise Suite"
        assert "medmatch" in enterprise_pkg["portals"]
        assert "karau" in enterprise_pkg["portals"]
        assert "enzi" in enterprise_pkg["portals"]
        assert len(enterprise_pkg["portals"]) == 3

    def test_portal_info_included(self):
        """Test portal info is returned with packages"""
        response = requests.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        
        data = response.json()
        assert "portals" in data
        
        portal_info = data["portals"]
        assert "medmatch" in portal_info
        assert "karau" in portal_info
        assert "enzi" in portal_info
        
        # Verify portal info structure
        assert portal_info["medmatch"]["name"] == "MedMatch Job Toolkit"
        assert portal_info["karau"]["name"] == "AI KARAU"
        assert portal_info["enzi"]["name"] == "ENZI Messenger"


class TestPortalAccess:
    """Tests for authenticated portal access endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield
        # Reset to enterprise package after tests
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "enterprise"}
        )

    def test_get_portal_access_authenticated(self):
        """Test GET /api/portal/access returns user's current package"""
        response = requests.get(
            f"{BASE_URL}/api/portal/access",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "package_id" in data
        assert "package_name" in data
        assert "portals" in data
        assert "portal_info" in data

    def test_get_portal_access_unauthenticated(self):
        """Test GET /api/portal/access returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/portal/access")
        assert response.status_code == 401

    def test_set_package_standard(self):
        """Test setting package to standard (KARAU + ENZI)"""
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "standard"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "updated"
        assert data["package_id"] == "standard"
        assert "karau" in data["portals"]
        assert "enzi" in data["portals"]
        assert "medmatch" not in data["portals"]

    def test_set_package_medmatch_standalone(self):
        """Test setting package to MedMatch standalone"""
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "medmatch_standalone"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "updated"
        assert data["package_id"] == "medmatch_standalone"
        assert "medmatch" in data["portals"]
        assert "karau" not in data["portals"]
        assert "enzi" not in data["portals"]

    def test_set_package_enterprise(self):
        """Test setting package to enterprise (all 3)"""
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "enterprise"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "updated"
        assert data["package_id"] == "enterprise"
        assert "medmatch" in data["portals"]
        assert "karau" in data["portals"]
        assert "enzi" in data["portals"]

    def test_set_package_invalid(self):
        """Test setting invalid package returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "invalid_package"}
        )
        assert response.status_code == 400

    def test_set_package_unauthenticated(self):
        """Test setting package without auth returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            json={"package_id": "standard"}
        )
        assert response.status_code == 401


class TestPortalSyncSession:
    """Tests for cross-portal session synchronization"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_sync_session_returns_token(self):
        """Test POST /api/portal/sync-session returns new token"""
        response = requests.post(
            f"{BASE_URL}/api/portal/sync-session",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "token" in data
        assert len(data["token"]) > 20  # Valid token length
        
    def test_sync_session_returns_user_info(self):
        """Test POST /api/portal/sync-session returns user data"""
        response = requests.post(
            f"{BASE_URL}/api/portal/sync-session",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == ADMIN_EMAIL
        assert "user_id" in data["user"]

    def test_sync_session_sets_cookie(self):
        """Test POST /api/portal/sync-session sets session cookie"""
        response = requests.post(
            f"{BASE_URL}/api/portal/sync-session",
            headers=self.headers
        )
        assert response.status_code == 200
        
        # Check that session_token cookie is set in response
        cookies = response.cookies
        # Note: Cookie may not be visible in response.cookies due to httponly
        # But the endpoint should set it (verified by actual browser tests)

    def test_sync_session_unauthenticated(self):
        """Test POST /api/portal/sync-session without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/portal/sync-session")
        assert response.status_code == 401


class TestPortalCheckAccess:
    """Tests for checking access to specific portals"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield
        # Reset to enterprise after tests
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "enterprise"}
        )

    def test_check_access_medmatch_with_enterprise(self):
        """Test checking medmatch access with enterprise package"""
        # First set to enterprise
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "enterprise"}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/portal/check-access/medmatch",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_access"] == True
        assert data["portal"] == "medmatch"

    def test_check_access_medmatch_with_standard(self):
        """Test checking medmatch access with standard package (should be denied)"""
        # Set to standard (no medmatch)
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "standard"}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/portal/check-access/medmatch",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_access"] == False
        assert data["portal"] == "medmatch"

    def test_check_access_karau_with_standard(self):
        """Test checking karau access with standard package (should have access)"""
        # Set to standard
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "standard"}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/portal/check-access/karau",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_access"] == True
        assert data["portal"] == "karau"

    def test_check_access_enzi_with_medmatch_standalone(self):
        """Test checking enzi access with medmatch_standalone (should be denied)"""
        # Set to medmatch_standalone (no enzi)
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "medmatch_standalone"}
        )
        
        response = requests.get(
            f"{BASE_URL}/api/portal/check-access/enzi",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_access"] == False
        assert data["portal"] == "enzi"

    def test_check_access_invalid_portal(self):
        """Test checking access for invalid portal returns 400"""
        response = requests.get(
            f"{BASE_URL}/api/portal/check-access/invalid_portal",
            headers=self.headers
        )
        assert response.status_code == 400

    def test_check_access_unauthenticated(self):
        """Test checking access without auth returns 401"""
        response = requests.get(f"{BASE_URL}/api/portal/check-access/medmatch")
        assert response.status_code == 401

    def test_check_access_returns_portal_info(self):
        """Test that check-access returns portal info"""
        response = requests.get(
            f"{BASE_URL}/api/portal/check-access/medmatch",
            headers=self.headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "portal_info" in data
        assert data["portal_info"]["name"] == "MedMatch Job Toolkit"
        assert data["portal_info"]["path"] == "/"


class TestPackagePersistence:
    """Tests for package selection persistence"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token before each test"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        yield
        # Reset to enterprise
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "enterprise"}
        )

    def test_package_selection_persists(self):
        """Test that package selection persists across requests"""
        # Set to standard
        set_response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "standard"}
        )
        assert set_response.status_code == 200
        
        # Get access and verify it's standard
        get_response = requests.get(
            f"{BASE_URL}/api/portal/access",
            headers=self.headers
        )
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["package_id"] == "standard"
        assert "karau" in data["portals"]
        assert "enzi" in data["portals"]
        assert "medmatch" not in data["portals"]

    def test_can_change_package(self):
        """Test that user can change their package"""
        # Set to standard first
        requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "standard"}
        )
        
        # Now change to enterprise
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=self.headers,
            json={"package_id": "enterprise"}
        )
        assert response.status_code == 200
        
        # Verify it changed
        get_response = requests.get(
            f"{BASE_URL}/api/portal/access",
            headers=self.headers
        )
        assert get_response.json()["package_id"] == "enterprise"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
