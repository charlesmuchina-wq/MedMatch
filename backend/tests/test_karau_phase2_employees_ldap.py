"""
Test KARAU Phase 2: Employee Directory with CSV Import, LDAP Integration, and Enhanced Management
Features: CSV upload, employee CRUD (delete/update/status), LDAP config/test/sync, employee stats
"""
import pytest
import requests
import os
import time
import io
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://realtime-simulations.preview.emergentagent.com')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
EXISTING_ORG_ID = "org_5a18c854f810"  # MedMatch Inc


class TestAuth:
    """Helper for authentication"""
    
    @staticmethod
    def get_admin_token():
        """Get admin auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token") or data.get("token")
        return None


@pytest.fixture(scope="module")
def admin_token():
    """Module-scoped admin token fixture"""
    token = TestAuth.get_admin_token()
    if not token:
        pytest.skip("Admin authentication failed - skipping tests")
    return token


@pytest.fixture(scope="module")
def headers(admin_token):
    """Headers with auth token"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}"
    }


@pytest.fixture(scope="module")
def auth_only_headers(admin_token):
    """Headers with just auth (for file uploads)"""
    return {
        "Authorization": f"Bearer {admin_token}"
    }


# ============= CSV UPLOAD TESTS =============

class TestCSVUpload:
    """Test CSV file upload for bulk employee import"""
    
    def test_csv_upload_basic(self, auth_only_headers):
        """POST /api/karau-meet/organizations/{id}/employees/csv-upload - Basic CSV upload"""
        timestamp = int(time.time())
        
        # Create a simple CSV
        csv_content = f"""email,first_name,last_name,department,title
TEST_csv1_{timestamp}@medmatch.com,CSV,User1,Engineering,Developer
TEST_csv2_{timestamp}@medmatch.com,CSV,User2,Marketing,Manager
TEST_csv3_{timestamp}@medmatch.com,CSV,User3,Sales,Representative
"""
        
        files = {
            'file': ('employees.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/csv-upload",
            headers=auth_only_headers,
            files=files
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "added" in data, "Response should contain 'added' count"
        assert data["added"] >= 0, "Added count should be >= 0"
        assert "errors" in data, "Response should contain 'errors' list"
        assert "detected_columns" in data, "Response should contain 'detected_columns'"
        
        # Verify column detection
        columns = data["detected_columns"]
        assert "email" in columns, "Should detect email column"
        
        print(f"✅ CSV upload: added {data['added']}, errors {data['error_count']}")
    
    def test_csv_upload_flexible_column_names(self, auth_only_headers):
        """CSV upload with flexible column names (Email Address, First Name, etc.)"""
        timestamp = int(time.time())
        
        # CSV with alternative column names
        csv_content = f"""Email Address,First Name,Last Name,Department,Job Title
TEST_flex1_{timestamp}@medmatch.com,Flexible,UserA,HR,Specialist
TEST_flex2_{timestamp}@medmatch.com,Flexible,UserB,IT,Admin
"""
        
        files = {
            'file': ('employees_flex.csv', csv_content, 'text/csv')
        }
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/csv-upload",
            headers=auth_only_headers,
            files=files
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Should detect columns even with alternative names
        columns = data["detected_columns"]
        assert "email" in columns, "Should detect email from 'Email Address'"
        
        print(f"✅ Flexible columns detected: {list(columns.keys())}")
    
    def test_csv_upload_handles_duplicate_emails(self, auth_only_headers):
        """CSV upload handles duplicate emails correctly"""
        timestamp = int(time.time())
        
        # First upload
        csv_content1 = f"""email,first_name,last_name,department,title
TEST_dup_{timestamp}@medmatch.com,Dup,User,Engineering,Developer
"""
        
        files1 = {'file': ('emp1.csv', csv_content1, 'text/csv')}
        response1 = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/csv-upload",
            headers=auth_only_headers,
            files=files1
        )
        assert response1.status_code == 200
        first_added = response1.json().get("added", 0)
        
        # Second upload with same email (duplicate)
        files2 = {'file': ('emp2.csv', csv_content1, 'text/csv')}
        response2 = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/csv-upload",
            headers=auth_only_headers,
            files=files2
        )
        assert response2.status_code == 200
        
        data = response2.json()
        # Should have error for duplicate
        if first_added > 0:
            assert data["error_count"] > 0 or data["added"] == 0, "Duplicate should be rejected"
            
        print(f"✅ Duplicate email handling: errors={data['error_count']}")
    
    def test_csv_upload_invalid_emails(self, auth_only_headers):
        """CSV upload handles invalid email addresses"""
        timestamp = int(time.time())
        
        csv_content = f"""email,first_name,last_name,department,title
invalid_no_at_sign,Bad,Email1,Test,Tester
also-invalid,Bad,Email2,Test,Tester
TEST_valid_{timestamp}@medmatch.com,Valid,Email,Test,Tester
"""
        
        files = {'file': ('invalid_emails.csv', csv_content, 'text/csv')}
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/csv-upload",
            headers=auth_only_headers,
            files=files
        )
        
        assert response.status_code == 200
        
        data = response.json()
        # Should have errors for invalid emails
        assert data["error_count"] >= 2, "Should reject at least 2 invalid emails"
        
        print(f"✅ Invalid email handling: {data['error_count']} errors, {data['added']} added")
    
    def test_csv_upload_non_csv_file_rejected(self, auth_only_headers):
        """CSV upload rejects non-CSV files"""
        files = {'file': ('test.txt', 'not a csv', 'text/plain')}
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/csv-upload",
            headers=auth_only_headers,
            files=files
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Non-CSV file rejected")
    
    def test_csv_upload_missing_email_column(self, auth_only_headers):
        """CSV upload requires email column"""
        csv_content = """first_name,last_name,department
John,Doe,Engineering
"""
        
        files = {'file': ('no_email.csv', csv_content, 'text/csv')}
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/csv-upload",
            headers=auth_only_headers,
            files=files
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        assert "email" in response.json().get("detail", "").lower()
        
        print("✅ Missing email column rejected")


# ============= EMPLOYEE CRUD TESTS =============

class TestEmployeeCRUD:
    """Test employee CRUD operations (delete, update, status toggle)"""
    
    created_employee_id = None
    
    def test_delete_employee(self, headers):
        """DELETE /api/karau-meet/organizations/{id}/employees/{emp_id} - Delete employee"""
        # First create an employee to delete
        timestamp = int(time.time())
        create_response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees",
            headers=headers,
            json={
                "email": f"TEST_delete_{timestamp}@medmatch.com",
                "first_name": "Delete",
                "last_name": "Test",
                "department": "Test",
                "title": "Test Employee"
            }
        )
        
        assert create_response.status_code == 200, f"Failed to create employee: {create_response.text}"
        emp_id = create_response.json()["employee_id"]
        
        # Now delete
        delete_response = requests.delete(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/{emp_id}",
            headers=headers
        )
        
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        
        data = delete_response.json()
        assert data["success"] == True
        assert data["employee_id"] == emp_id
        
        # Verify deletion - employee should not appear in list
        list_response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees",
            headers=headers
        )
        employees = list_response.json().get("employees", [])
        emp_ids = [e["employee_id"] for e in employees]
        assert emp_id not in emp_ids, "Deleted employee should not appear in list"
        
        print(f"✅ Employee deleted: {emp_id}")
    
    def test_delete_employee_not_found(self, headers):
        """DELETE /api/karau-meet/organizations/{id}/employees/{emp_id} - 404 for invalid ID"""
        response = requests.delete(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/invalid_emp_id",
            headers=headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Delete invalid employee returns 404")
    
    def test_update_employee(self, headers):
        """PUT /api/karau-meet/organizations/{id}/employees/{emp_id} - Update employee details"""
        # First create an employee to update
        timestamp = int(time.time())
        create_response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees",
            headers=headers,
            json={
                "email": f"TEST_update_{timestamp}@medmatch.com",
                "first_name": "Update",
                "last_name": "Test",
                "department": "Original",
                "title": "Original Title"
            }
        )
        
        assert create_response.status_code == 200
        emp_id = create_response.json()["employee_id"]
        TestEmployeeCRUD.created_employee_id = emp_id
        
        # Now update
        update_response = requests.put(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/{emp_id}",
            headers=headers,
            json={
                "email": f"TEST_update_{timestamp}@medmatch.com",
                "first_name": "Updated",
                "last_name": "Employee",
                "department": "New Department",
                "title": "Senior Engineer"
            }
        )
        
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        data = update_response.json()
        assert data["success"] == True
        assert data["employee_id"] == emp_id
        
        print(f"✅ Employee updated: {emp_id}")
    
    def test_update_employee_not_found(self, headers):
        """PUT /api/karau-meet/organizations/{id}/employees/{emp_id} - 404 for invalid ID"""
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/invalid_emp_id",
            headers=headers,
            json={
                "email": "test@test.com",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Update invalid employee returns 404")
    
    def test_toggle_employee_status_to_inactive(self, headers):
        """PUT /api/karau-meet/organizations/{id}/employees/{emp_id}/status?status=inactive - Deactivate"""
        # First create an employee
        timestamp = int(time.time())
        create_response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees",
            headers=headers,
            json={
                "email": f"TEST_status_{timestamp}@medmatch.com",
                "first_name": "Status",
                "last_name": "Test",
                "department": "Test"
            }
        )
        
        assert create_response.status_code == 200
        emp_id = create_response.json()["employee_id"]
        
        # Toggle to inactive
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/{emp_id}/status",
            headers=headers,
            params={"status": "inactive"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "inactive"
        
        print(f"✅ Employee status toggled to inactive: {emp_id}")
    
    def test_toggle_employee_status_to_active(self, headers):
        """PUT /api/karau-meet/organizations/{id}/employees/{emp_id}/status?status=active - Reactivate"""
        # First create an employee and make inactive
        timestamp = int(time.time())
        create_response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees",
            headers=headers,
            json={
                "email": f"TEST_reactivate_{timestamp}@medmatch.com",
                "first_name": "Reactivate",
                "last_name": "Test",
                "department": "Test"
            }
        )
        
        assert create_response.status_code == 200
        emp_id = create_response.json()["employee_id"]
        
        # Make inactive first
        requests.put(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/{emp_id}/status",
            headers=headers,
            params={"status": "inactive"}
        )
        
        # Now reactivate
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/{emp_id}/status",
            headers=headers,
            params={"status": "active"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["status"] == "active"
        
        print(f"✅ Employee reactivated: {emp_id}")
    
    def test_toggle_status_invalid_status_value(self, headers):
        """PUT status with invalid status value returns 400"""
        # Use any employee ID (will validate status first)
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/any_id/status",
            headers=headers,
            params={"status": "invalid_status"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Invalid status value returns 400")


# ============= EMPLOYEE STATS TESTS =============

class TestEmployeeStats:
    """Test employee statistics endpoint"""
    
    def test_get_employee_stats(self, headers):
        """GET /api/karau-meet/organizations/{id}/employees/stats - Get stats"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/stats",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify structure
        assert "total" in data, "Stats should include 'total'"
        assert "active" in data, "Stats should include 'active'"
        assert "inactive" in data, "Stats should include 'inactive'"
        assert "departments" in data, "Stats should include 'departments' breakdown"
        assert "sources" in data, "Stats should include 'sources' breakdown"
        
        # Verify types
        assert isinstance(data["total"], int)
        assert isinstance(data["active"], int)
        assert isinstance(data["inactive"], int)
        assert isinstance(data["departments"], list)
        assert isinstance(data["sources"], dict)
        
        # Verify math
        assert data["total"] >= data["active"], "Total should be >= active"
        assert data["inactive"] >= 0, "Inactive should be >= 0"
        
        print(f"✅ Employee stats: total={data['total']}, active={data['active']}, inactive={data['inactive']}")
        print(f"   Departments: {len(data['departments'])}, Sources: {list(data['sources'].keys())}")
    
    def test_stats_includes_department_breakdown(self, headers):
        """Stats includes department breakdown with counts"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/stats",
            headers=headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        departments = data.get("departments", [])
        
        # Each department entry should have name and count
        for dept in departments:
            assert "department" in dept, "Department entry should have 'department' name"
            assert "count" in dept, "Department entry should have 'count'"
            assert dept["count"] > 0, "Department count should be > 0"
        
        print(f"✅ Department breakdown: {departments}")
    
    def test_stats_includes_source_breakdown(self, headers):
        """Stats includes source breakdown (manual, csv_import, ldap_sync)"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees/stats",
            headers=headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        sources = data.get("sources", {})
        
        # Sources should be a dict with counts
        assert isinstance(sources, dict)
        
        # Valid source keys
        valid_sources = {"manual", "csv_import", "ldap_sync", None}
        for source_key in sources.keys():
            # source_key can be None for old records
            assert source_key in valid_sources or source_key is None, f"Invalid source: {source_key}"
        
        print(f"✅ Source breakdown: {sources}")


# ============= LDAP CONFIGURATION TESTS =============

class TestLDAPConfig:
    """Test LDAP/Active Directory configuration endpoints"""
    
    def test_configure_ldap(self, headers):
        """POST /api/karau-meet/organizations/{id}/ldap/configure - Save LDAP config"""
        ldap_config = {
            "server_url": "ldap://test.ldap.example.com:389",
            "bind_dn": "cn=admin,dc=example,dc=com",
            "bind_password": "test_password_123",
            "base_dn": "ou=users,dc=example,dc=com",
            "user_filter": "(objectClass=person)",
            "email_attr": "mail",
            "first_name_attr": "givenName",
            "last_name_attr": "sn",
            "department_attr": "department",
            "title_attr": "title",
            "enabled": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/ldap/configure",
            headers=headers,
            json=ldap_config
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["success"] == True
        assert data["enabled"] == True
        
        print("✅ LDAP configuration saved")
    
    def test_get_ldap_config_masked_password(self, headers):
        """GET /api/karau-meet/organizations/{id}/ldap/config - Password should be masked"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/ldap/config",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "configured" in data
        
        if data["configured"]:
            config = data["config"]
            assert "bind_password" in config
            # Password should be masked (not the actual password)
            assert config["bind_password"] == "••••••••" or len(config["bind_password"]) == 0 or "*" in config["bind_password"] or "•" in config["bind_password"], \
                f"Password should be masked, got: {config['bind_password']}"
            assert "server_url" in config
            assert "bind_dn" in config
            assert "base_dn" in config
            
            print(f"✅ LDAP config retrieved with masked password: {config['bind_password']}")
        else:
            print("✅ LDAP not configured (expected for fresh orgs)")
    
    def test_get_ldap_config_not_configured(self, headers):
        """GET /api/karau-meet/organizations/{id}/ldap/config - Returns configured=false if not set"""
        # Create a new org without LDAP config
        timestamp = int(time.time())
        org_response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations",
            headers=headers,
            json={
                "name": f"TEST_NoLDAP_{timestamp}",
                "email_domains": [f"noldap{timestamp}.com"],
                "tier": "tier_1"
            }
        )
        
        if org_response.status_code != 200:
            pytest.skip("Could not create test org")
        
        new_org_id = org_response.json()["org_id"]
        
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{new_org_id}/ldap/config",
            headers=headers
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["configured"] == False
        
        print("✅ Unconfigured org returns configured=false")


# ============= LDAP TEST/SYNC TESTS =============

class TestLDAPOperations:
    """Test LDAP test connection and sync (will fail gracefully without real LDAP)"""
    
    def test_ldap_test_connection(self, headers):
        """POST /api/karau-meet/organizations/{id}/ldap/test - Test LDAP connection"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/ldap/test",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "success" in data
        assert "message" in data
        
        # Will likely fail since we don't have a real LDAP server
        # That's expected - just checking the endpoint works
        if data["success"]:
            print(f"✅ LDAP test succeeded: {data['message']}")
        else:
            print(f"✅ LDAP test failed (expected - no real LDAP): {data['message']}")
    
    def test_ldap_test_not_configured(self, headers):
        """POST /api/karau-meet/organizations/{id}/ldap/test - Returns error if not configured"""
        # Create org without LDAP config
        timestamp = int(time.time())
        org_response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations",
            headers=headers,
            json={
                "name": f"TEST_NoLDAPTest_{timestamp}",
                "email_domains": [f"noldaptest{timestamp}.com"],
                "tier": "tier_1"
            }
        )
        
        if org_response.status_code != 200:
            pytest.skip("Could not create test org")
        
        new_org_id = org_response.json()["org_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{new_org_id}/ldap/test",
            headers=headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ LDAP test on unconfigured org returns 400")
    
    def test_ldap_sync(self, headers):
        """POST /api/karau-meet/organizations/{id}/ldap/sync - Sync employees from LDAP"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/ldap/sync",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "success" in data
        
        # Will likely fail since we don't have a real LDAP server
        if data["success"]:
            assert "added" in data
            assert "updated" in data
            print(f"✅ LDAP sync succeeded: added={data.get('added')}, updated={data.get('updated')}")
        else:
            assert "message" in data
            print(f"✅ LDAP sync failed (expected - no real LDAP): {data['message']}")
    
    def test_ldap_sync_not_configured(self, headers):
        """POST /api/karau-meet/organizations/{id}/ldap/sync - Returns error if not configured"""
        # Create org without LDAP config
        timestamp = int(time.time())
        org_response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations",
            headers=headers,
            json={
                "name": f"TEST_NoLDAPSync_{timestamp}",
                "email_domains": [f"noldapsync{timestamp}.com"],
                "tier": "tier_1"
            }
        )
        
        if org_response.status_code != 200:
            pytest.skip("Could not create test org")
        
        new_org_id = org_response.json()["org_id"]
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/organizations/{new_org_id}/ldap/sync",
            headers=headers
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ LDAP sync on unconfigured org returns 400")


# ============= REGRESSION: PHASE 1 ENDPOINTS =============

class TestPhase1Regression:
    """Regression tests for Phase 1 endpoints"""
    
    def test_tier_info_still_works(self, headers):
        """GET /api/karau-meet/organizations/tiers/info - Still returns all tiers"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/organizations/tiers/info", headers=headers)
        
        assert response.status_code == 200
        assert "tiers" in response.json()
        
        print("✅ Tier info endpoint still working")
    
    def test_org_list_still_works(self, headers):
        """GET /api/karau-meet/organizations - Still lists orgs"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/organizations", headers=headers)
        
        assert response.status_code == 200
        assert "organizations" in response.json()
        
        print("✅ Org list endpoint still working")
    
    def test_room_endpoints_still_work(self, headers):
        """Room CRUD endpoints still work"""
        # List rooms
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/rooms",
            headers=headers
        )
        
        assert response.status_code == 200
        assert "rooms" in response.json()
        
        print("✅ Room endpoints still working")
    
    def test_branding_endpoint_still_works(self):
        """GET /api/karau-meet/organizations/branding/by-domain - Still returns branding"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/branding/by-domain",
            params={"email": "test@medmatch.com"}
        )
        
        assert response.status_code == 200
        
        print("✅ Branding endpoint still working")
    
    def test_employee_search_still_works(self, headers):
        """GET /api/karau-meet/organizations/{id}/employees?search= - Last name search still works"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/organizations/{EXISTING_ORG_ID}/employees",
            headers=headers,
            params={"search": "Smith"}
        )
        
        assert response.status_code == 200
        assert "employees" in response.json()
        
        print("✅ Employee search still working")


# ============= CLEANUP =============

@pytest.fixture(scope="module", autouse=True)
def cleanup(headers):
    """Cleanup TEST_ prefixed data after all tests"""
    yield
    
    print("\n🧹 Test cleanup: TEST_ prefixed data created during testing")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
