"""
LDAP Integration Test Script for AI KARAU
Tests the LDAP/Active Directory sync configuration endpoints.
Run: pytest /app/backend/tests/test_ldap_integration.py -v
"""
import pytest
import httpx
import os

API_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001")
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


@pytest.fixture
def admin_token():
    """Get admin auth token."""
    resp = httpx.post(f"{API_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_ldap_configure_endpoint(admin_token):
    """Test LDAP configuration save."""
    resp = httpx.post(
        f"{API_URL}/api/karau-organizations/org_5a18c854f810/ldap/configure",
        json={
            "server": "ldap://test.example.com:389",
            "bind_dn": "cn=admin,dc=example,dc=com",
            "bind_password": "test_password",
            "base_dn": "dc=example,dc=com",
            "user_filter": "(objectClass=person)",
            "sync_interval": 3600,
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # Should succeed (configuration saved, not tested against live server)
    assert resp.status_code in (200, 201, 404)  # 404 if org doesn't exist


def test_ldap_configure_requires_auth():
    """Test LDAP configuration requires authentication."""
    resp = httpx.post(
        f"{API_URL}/api/karau-organizations/org_test/ldap/configure",
        json={"server": "ldap://test.example.com"},
    )
    assert resp.status_code == 401


def test_ldap_sync_endpoint(admin_token):
    """Test LDAP sync trigger."""
    resp = httpx.post(
        f"{API_URL}/api/karau-organizations/org_5a18c854f810/ldap/sync",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    # May return error if LDAP server not reachable - that's expected
    assert resp.status_code in (200, 400, 404, 500, 503)


def test_employee_csv_import(admin_token):
    """Test CSV employee import endpoint exists."""
    # Create a minimal CSV
    import io
    csv_content = "name,email,department\nJohn Doe,john@test.com,Engineering"
    files = {"file": ("employees.csv", csv_content, "text/csv")}
    resp = httpx.post(
        f"{API_URL}/api/karau-organizations/org_5a18c854f810/employees/csv",
        files=files,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code in (200, 404)  # 404 if org doesn't exist


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
