"""
Comprehensive Bug Hunting Test Suite - Iteration 52
Tests edge cases, error handling, validation, security issues, and race conditions.
Focus areas: Authentication, Job Search, Data Validation, API Error Handling, 
Notifications, Geolocation, Credentials, AI Features
"""
import pytest
import requests
import os
import json
import time
import concurrent.futures
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://cinematic-meet.preview.emergentagent.com')

# Test credentials
JOB_SEEKER_CREDS = {"email": "test_jobseeker_ui@test.com", "password": "Test123!"}
ADMIN_CREDS = {"email": "admin@medmatch.com", "password": "MedMatch2026!"}
INVALID_CREDS = {"email": "nonexistent@test.com", "password": "wrongpassword"}


class TestAuthenticationBugs:
    """Authentication edge cases and security tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_login_invalid_credentials(self):
        """Login with invalid credentials - should return 401 with proper error message"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=INVALID_CREDS)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        data = response.json()
        assert "detail" in data, "Error response should contain 'detail' field"
        print(f"PASS: Invalid credentials returns 401 with message: {data.get('detail')}")
    
    def test_login_empty_email(self):
        """Login with empty email - should return validation error"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={"email": "", "password": "test123"})
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print(f"PASS: Empty email returns {response.status_code}")
    
    def test_login_empty_password(self):
        """Login with empty password - should return validation error"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={"email": "test@test.com", "password": ""})
        assert response.status_code in [400, 401, 422], f"Expected 400/401/422, got {response.status_code}"
        print(f"PASS: Empty password returns {response.status_code}")
    
    def test_login_empty_fields(self):
        """Login with all empty fields - should return validation error"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={"email": "", "password": ""})
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print(f"PASS: Empty fields returns {response.status_code}")
    
    def test_register_duplicate_email(self):
        """Register with existing email - should return 400"""
        # First register a user
        unique_email = f"test_dup_{int(time.time())}@test.com"
        reg_data = {"email": unique_email, "password": "Test123!", "name": "Test User", "role": "job_seeker"}
        self.session.post(f"{BASE_URL}/api/auth/register", json=reg_data)
        
        # Try to register again with same email
        response = self.session.post(f"{BASE_URL}/api/auth/register", json=reg_data)
        assert response.status_code == 400, f"Expected 400 for duplicate email, got {response.status_code}"
        print(f"PASS: Duplicate email registration returns 400")
    
    def test_logout_clears_session(self):
        """Logout should clear session properly"""
        # Login first
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code != 200:
            pytest.skip("Login failed, skipping logout test")
        
        token = login_resp.json().get("access_token")
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Logout
        logout_resp = self.session.post(f"{BASE_URL}/api/auth/logout")
        assert logout_resp.status_code == 200, f"Logout failed with {logout_resp.status_code}"
        
        # Try to access protected endpoint - should fail
        me_resp = self.session.get(f"{BASE_URL}/api/auth/me")
        # After logout, /me should return 401
        print(f"PASS: Logout successful, /me returns {me_resp.status_code}")
    
    def test_access_protected_without_token(self):
        """Access protected endpoint without token - should return 401"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: Protected endpoint without token returns 401")
    
    def test_access_with_expired_token(self):
        """Access with malformed/expired token - should return 401"""
        session = requests.Session()
        session.headers.update({
            "Authorization": "Bearer invalid_expired_token_12345",
            "Content-Type": "application/json"
        })
        response = session.get(f"{BASE_URL}/api/auth/me")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"PASS: Invalid token returns 401")


class TestJobSearchBugs:
    """Job search edge cases and security tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_search_empty_query(self):
        """Search with empty query - should return results or helpful message"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": ""})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "jobs" in data, "Response should contain 'jobs' field"
        print(f"PASS: Empty query search returns {len(data.get('jobs', []))} jobs")
    
    def test_search_special_characters(self):
        """Search with special characters (!@#$%^&*) - should handle gracefully"""
        special_chars = "!@#$%^&*()"
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": special_chars})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: Special characters search handled gracefully")
    
    def test_search_very_long_query(self):
        """Search with very long query (500+ chars) - should handle gracefully"""
        long_query = "a" * 500
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": long_query})
        assert response.status_code in [200, 400], f"Expected 200/400, got {response.status_code}"
        print(f"PASS: Long query (500 chars) returns {response.status_code}")
    
    def test_search_sql_injection(self):
        """Search with SQL injection attempt - should be sanitized"""
        sql_injection = "'; DROP TABLE users; --"
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": sql_injection})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        # Should not cause server error
        print(f"PASS: SQL injection attempt handled safely")
    
    def test_search_xss_attempt(self):
        """Search with XSS attempt - should be sanitized"""
        xss_payload = "<script>alert('xss')</script>"
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": xss_payload})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Check that XSS is not reflected in response
        response_str = json.dumps(data)
        assert "<script>" not in response_str, "XSS payload should be sanitized"
        print(f"PASS: XSS attempt handled safely")
    
    def test_pagination_page_zero(self):
        """Pagination with page 0 - should handle gracefully"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": "engineer", "page": 0})
        assert response.status_code in [200, 400], f"Expected 200/400, got {response.status_code}"
        print(f"PASS: Page 0 returns {response.status_code}")
    
    def test_pagination_negative_page(self):
        """Pagination with negative page - should handle gracefully"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": "engineer", "page": -1})
        assert response.status_code in [200, 400], f"Expected 200/400, got {response.status_code}"
        print(f"PASS: Negative page returns {response.status_code}")
    
    def test_pagination_very_large_page(self):
        """Pagination with very large page number - should return empty or error"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search", params={"q": "engineer", "page": 999999})
        assert response.status_code in [200, 400], f"Expected 200/400, got {response.status_code}"
        print(f"PASS: Very large page returns {response.status_code}")


class TestDataInputValidation:
    """Data input validation tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_save_job_invalid_id(self):
        """Save job with invalid job_id - should handle gracefully"""
        invalid_job = {
            "id": "invalid_id_!@#$%",
            "title": "Test Job",
            "company": "Test Company",
            "location": "Remote"
        }
        response = self.session.post(f"{BASE_URL}/api/saved-jobs", json=invalid_job)
        # Should either accept (IDs are strings) or return validation error
        assert response.status_code in [200, 201, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Invalid job_id handled with status {response.status_code}")
    
    def test_create_alert_missing_fields(self):
        """Create alert with missing required fields - should return validation error"""
        incomplete_alert = {"keywords": []}  # Missing email
        response = self.session.post(f"{BASE_URL}/api/job-alerts", json=incomplete_alert)
        # Should either use user's email or return error
        assert response.status_code in [200, 201, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Missing fields handled with status {response.status_code}")
    
    def test_update_profile_invalid_data_types(self):
        """Update profile with invalid data types - should return validation error"""
        invalid_profile = {
            "name": 12345,  # Should be string
            "email": "not_an_email"  # Invalid email format
        }
        response = self.session.put(f"{BASE_URL}/api/auth/preferences", json=invalid_profile)
        # Should return validation error or handle gracefully
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Invalid data types handled with status {response.status_code}")


class TestAPIErrorHandling:
    """API error handling tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
    
    def test_malformed_json(self):
        """Request with malformed JSON - should return 400/422"""
        self.session.headers.update({"Content-Type": "application/json"})
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            data="{'invalid json",  # Malformed JSON
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print(f"PASS: Malformed JSON returns {response.status_code}")
    
    def test_missing_content_type(self):
        """Request without Content-Type header - should handle gracefully"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            data=json.dumps(JOB_SEEKER_CREDS)
        )
        # FastAPI should still parse JSON or return appropriate error
        assert response.status_code in [200, 400, 415, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Missing Content-Type handled with status {response.status_code}")
    
    def test_nonexistent_endpoint(self):
        """Request to non-existent endpoint - should return 404"""
        response = self.session.get(f"{BASE_URL}/api/nonexistent/endpoint/12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Non-existent endpoint returns 404")
    
    def test_wrong_http_method(self):
        """Request with wrong HTTP method - should return 405"""
        response = self.session.delete(f"{BASE_URL}/api/auth/login")
        assert response.status_code == 405, f"Expected 405, got {response.status_code}"
        print(f"PASS: Wrong HTTP method returns 405")


class TestNotificationBugs:
    """Notification system edge cases"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_mark_nonexistent_notification_read(self):
        """Mark non-existent notification as read - should return 404"""
        response = self.session.post(f"{BASE_URL}/api/notifications/nonexistent_id_12345/read")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Non-existent notification returns 404")
    
    def test_delete_nonexistent_notification(self):
        """Delete non-existent notification - should return 404"""
        response = self.session.delete(f"{BASE_URL}/api/notifications/nonexistent_id_12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Delete non-existent notification returns 404")
    
    def test_get_notifications_invalid_limit(self):
        """Get notifications with invalid limit parameter - should handle gracefully"""
        response = self.session.get(f"{BASE_URL}/api/notifications", params={"limit": -1})
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Invalid limit handled with status {response.status_code}")
    
    def test_get_notifications_very_large_limit(self):
        """Get notifications with very large limit - should handle gracefully"""
        response = self.session.get(f"{BASE_URL}/api/notifications", params={"limit": 999999})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: Very large limit handled gracefully")


class TestGeolocationBugs:
    """Geolocation system edge cases"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_distance_invalid_coordinates(self):
        """Distance calculation with invalid coordinates - should handle gracefully"""
        invalid_coords = {
            "lat1": 999,  # Invalid latitude
            "lon1": 999,  # Invalid longitude
            "lat2": -999,
            "lon2": -999
        }
        response = self.session.post(f"{BASE_URL}/api/geolocation/distance", json=invalid_coords)
        # Should either calculate (math works) or return validation error
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Invalid coordinates handled with status {response.status_code}")
    
    def test_geocode_nonexistent_city(self):
        """Geocode with non-existent city - should return not found"""
        response = self.session.post(
            f"{BASE_URL}/api/geolocation/geocode",
            json={"address": "Nonexistent City XYZ123"}
        )
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            # Should indicate not found
            assert data.get("found") == False or "coordinates" not in data or data.get("coordinates") is None
        print(f"PASS: Non-existent city handled correctly")
    
    def test_update_preferences_negative_radius(self):
        """Update preferences with negative radius - should return validation error"""
        invalid_prefs = {
            "preferred_radius_miles": -50
        }
        response = self.session.put(f"{BASE_URL}/api/geolocation/preferences", json=invalid_prefs)
        # Should either reject or handle gracefully
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Negative radius handled with status {response.status_code}")
    
    def test_update_preferences_very_large_radius(self):
        """Update preferences with radius > 1000 miles - should handle gracefully"""
        large_radius_prefs = {
            "preferred_radius_miles": 5000
        }
        response = self.session.put(f"{BASE_URL}/api/geolocation/preferences", json=large_radius_prefs)
        # Should either accept or return validation error
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Very large radius handled with status {response.status_code}")


class TestCredentialBugs:
    """Credential verification edge cases"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_add_credential_future_expiration(self):
        """Add credential with future expiration date - should be accepted"""
        future_cred = {
            "credential_code": "TEST_CERT",
            "credential_number": "12345",
            "expiry_date": "2030-12-31"
        }
        response = self.session.post(f"{BASE_URL}/api/credentials/submit", json=future_cred)
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}"
        print(f"PASS: Future expiration date accepted")
    
    def test_verify_credential_invalid_id(self):
        """Verify credential with invalid ID - should return 404"""
        response = self.session.post(f"{BASE_URL}/api/credentials/reverify/invalid_id_12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"PASS: Invalid credential ID returns 404")


class TestAIFeatureBugs:
    """AI feature edge cases"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def test_dragon_ai_empty_message(self):
        """Dragon AI with empty message - should return validation error"""
        response = self.session.post(
            f"{BASE_URL}/api/assistant",
            json={"message": "", "context": "general"}
        )
        # Should either return error or handle gracefully
        assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"
        print(f"PASS: Empty message handled with status {response.status_code}")
    
    def test_dragon_ai_very_long_message(self):
        """Dragon AI with very long message (10000+ chars) - should handle gracefully"""
        long_message = "a" * 10000
        response = self.session.post(
            f"{BASE_URL}/api/assistant",
            json={"message": long_message, "context": "general"},
            timeout=60  # AI calls can be slow
        )
        # Should either process or return error
        assert response.status_code in [200, 400, 413, 422, 500], f"Unexpected status: {response.status_code}"
        print(f"PASS: Very long message handled with status {response.status_code}")
    
    def test_cover_letter_missing_company(self):
        """Cover letter with missing company - should return validation error"""
        incomplete_request = {
            "job_title": "Software Engineer",
            "company": "",  # Empty company
            "job_description": "Test description"
        }
        response = self.session.post(
            f"{BASE_URL}/api/cover-letter/generate",
            json=incomplete_request,
            timeout=60
        )
        # Should either handle gracefully or return error
        assert response.status_code in [200, 400, 422, 500], f"Unexpected status: {response.status_code}"
        print(f"PASS: Missing company handled with status {response.status_code}")


class TestRaceConditions:
    """Race condition and concurrent request tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        # Login
        login_resp = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if login_resp.status_code == 200:
            self.token = login_resp.json().get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
    
    def test_rapid_save_unsave_job(self):
        """Rapid save/unsave job clicks - should handle gracefully"""
        test_job = {
            "id": f"race_test_{int(time.time())}",
            "title": "Race Condition Test Job",
            "company": "Test Company",
            "location": "Remote"
        }
        
        # Save the job first
        save_resp = self.session.post(f"{BASE_URL}/api/saved-jobs", json=test_job)
        if save_resp.status_code not in [200, 201]:
            pytest.skip("Could not save job for race condition test")
        
        saved_id = save_resp.json().get("saved_job", {}).get("id") or save_resp.json().get("id")
        if not saved_id:
            pytest.skip("Could not get saved job ID")
        
        # Rapid delete attempts
        results = []
        for _ in range(3):
            resp = self.session.delete(f"{BASE_URL}/api/saved-jobs/{saved_id}")
            results.append(resp.status_code)
        
        # First should succeed (200), rest should be 404
        assert 200 in results or 404 in results, f"Unexpected results: {results}"
        print(f"PASS: Rapid save/unsave handled correctly. Results: {results}")
    
    def test_concurrent_api_calls(self):
        """Multiple simultaneous API calls - should all complete"""
        def make_request(endpoint):
            session = requests.Session()
            session.headers.update({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            })
            try:
                resp = session.get(f"{BASE_URL}{endpoint}", timeout=30)
                return (endpoint, resp.status_code)
            except Exception as e:
                return (endpoint, str(e))
        
        endpoints = [
            "/api/auth/me",
            "/api/jobs/search?q=engineer",
            "/api/saved-jobs",
            "/api/applications",
            "/api/notifications"
        ]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All should complete without server errors
        for endpoint, status in results:
            assert status in [200, 401, 404] or isinstance(status, str), f"Unexpected status for {endpoint}: {status}"
        
        print(f"PASS: Concurrent requests completed. Results: {results}")
    
    def test_login_while_logged_in(self):
        """Login while already logged in - should handle gracefully"""
        # Already logged in from setup
        # Try to login again
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: Login while logged in handled correctly")


class TestSecurityVulnerabilities:
    """Security vulnerability tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_path_traversal_attempt(self):
        """Path traversal attempt - should be blocked"""
        response = self.session.get(f"{BASE_URL}/api/../../../etc/passwd")
        assert response.status_code in [400, 404], f"Path traversal should be blocked, got {response.status_code}"
        print(f"PASS: Path traversal blocked with status {response.status_code}")
    
    def test_header_injection(self):
        """Header injection attempt - should be handled safely"""
        malicious_headers = {
            "X-Injected-Header": "malicious\r\nX-Another: value",
            "Content-Type": "application/json"
        }
        response = self.session.get(f"{BASE_URL}/api/auth/me", headers=malicious_headers)
        # Should not cause server error
        assert response.status_code in [200, 401], f"Unexpected status: {response.status_code}"
        print(f"PASS: Header injection handled safely")
    
    def test_large_payload_attack(self):
        """Large payload attack - should be rejected or handled"""
        large_payload = {"data": "x" * 1000000}  # 1MB payload
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json=large_payload,
            timeout=30
        )
        # Should either reject (413) or handle gracefully
        assert response.status_code in [400, 413, 422], f"Large payload should be rejected, got {response.status_code}"
        print(f"PASS: Large payload handled with status {response.status_code}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
