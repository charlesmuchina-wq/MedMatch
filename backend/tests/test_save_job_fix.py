"""
Test Save Job Fix - Alias Routes
Tests the fix for save job functionality with composite IDs (e.g., remotive_12345)
and standard UUIDs via the new alias routes:
- POST /api/jobs/save (alias for /api/saved-jobs)
- DELETE /api/jobs/saved/{job_id} (alias for /api/saved-jobs/{job_id})
- GET /api/jobs/saved (alias for /api/saved-jobs)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_USER = {
    "email": "test_jobseeker_ui@test.com",
    "password": "Test123!"
}


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token for test user"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=TEST_USER,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code != 200:
        pytest.skip(f"Authentication failed: {response.status_code}")
    return response.json().get("access_token")


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestSaveJobAliasRoutes:
    """Test the new alias routes for save job functionality"""
    
    def test_save_job_composite_id(self, auth_headers):
        """Test saving a job with composite ID (e.g., remotive_12345)"""
        job_data = {
            "id": f"remotive_test_{uuid.uuid4().hex[:8]}",
            "title": "Test Engineer - Composite ID",
            "company": "Test Company",
            "location": "Remote",
            "description": "Test job with composite ID",
            "url": f"https://example.com/job/{uuid.uuid4().hex[:8]}",
            "source": "Remotive"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/save",
            json=job_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("message") == "Job saved"
        assert "saved_job" in data
        assert data["saved_job"]["job"]["id"] == job_data["id"]
        
        # Store for cleanup
        self.__class__.saved_job_id_composite = data["saved_job"]["id"]
    
    def test_save_job_standard_uuid(self, auth_headers):
        """Test saving a job with standard UUID"""
        job_data = {
            "id": str(uuid.uuid4()),
            "title": "Test Engineer - UUID",
            "company": "Tech Corp",
            "location": "New York",
            "description": "Test job with standard UUID",
            "url": f"https://example.com/job/{uuid.uuid4().hex[:8]}",
            "source": "LinkedIn"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/save",
            json=job_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("message") == "Job saved"
        assert "saved_job" in data
        
        # Store for cleanup
        self.__class__.saved_job_id_uuid = data["saved_job"]["id"]
    
    def test_get_saved_jobs_alias(self, auth_headers):
        """Test getting saved jobs via alias route /api/jobs/saved"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/saved",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "saved_jobs" in data
        assert "count" in data
        assert isinstance(data["saved_jobs"], list)
        assert data["count"] >= 0
    
    def test_get_saved_jobs_original(self, auth_headers):
        """Test getting saved jobs via original route /api/saved-jobs"""
        response = requests.get(
            f"{BASE_URL}/api/saved-jobs",
            headers=auth_headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "saved_jobs" in data
        assert "count" in data
    
    def test_delete_saved_job_alias(self, auth_headers):
        """Test deleting a saved job via alias route /api/jobs/saved/{id}"""
        # First save a job to delete
        job_data = {
            "id": f"delete_test_{uuid.uuid4().hex[:8]}",
            "title": "Job to Delete",
            "company": "Delete Corp",
            "location": "Remote",
            "description": "This job will be deleted",
            "url": f"https://example.com/job/delete_{uuid.uuid4().hex[:8]}",
            "source": "Test"
        }
        
        save_response = requests.post(
            f"{BASE_URL}/api/jobs/save",
            json=job_data,
            headers=auth_headers
        )
        assert save_response.status_code == 200
        saved_job_id = save_response.json()["saved_job"]["id"]
        
        # Delete via alias route
        delete_response = requests.delete(
            f"{BASE_URL}/api/jobs/saved/{saved_job_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        data = delete_response.json()
        assert data.get("message") == "Job removed from saved"
    
    def test_delete_saved_job_original(self, auth_headers):
        """Test deleting a saved job via original route /api/saved-jobs/{id}"""
        # First save a job to delete
        job_data = {
            "id": f"delete_orig_{uuid.uuid4().hex[:8]}",
            "title": "Job to Delete Original",
            "company": "Delete Corp",
            "location": "Remote",
            "description": "This job will be deleted via original route",
            "url": f"https://example.com/job/delete_orig_{uuid.uuid4().hex[:8]}",
            "source": "Test"
        }
        
        save_response = requests.post(
            f"{BASE_URL}/api/saved-jobs",
            json=job_data,
            headers=auth_headers
        )
        assert save_response.status_code == 200
        saved_job_id = save_response.json()["saved_job"]["id"]
        
        # Delete via original route
        delete_response = requests.delete(
            f"{BASE_URL}/api/saved-jobs/{saved_job_id}",
            headers=auth_headers
        )
        
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
    
    def test_save_job_without_auth(self):
        """Test that saving a job without auth returns 401"""
        job_data = {
            "id": "no_auth_test",
            "title": "No Auth Test",
            "company": "Test",
            "location": "Remote"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/jobs/save",
            json=job_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
    
    def test_delete_nonexistent_job(self, auth_headers):
        """Test deleting a non-existent saved job returns 404"""
        fake_id = str(uuid.uuid4())
        
        response = requests.delete(
            f"{BASE_URL}/api/jobs/saved/{fake_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"


class TestJobSearchReturnsResults:
    """Test that job search returns results from multiple sources"""
    
    def test_job_search_returns_jobs(self):
        """Test that job search returns jobs"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"q": "engineer", "location": "Remote"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        # Should return some jobs
        assert len(data["jobs"]) > 0, "Expected at least one job result"
    
    def test_job_search_has_required_fields(self):
        """Test that job search results have required fields"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"q": "developer", "location": "Remote"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data["jobs"]) > 0:
            job = data["jobs"][0]
            # Check required fields
            assert "id" in job, "Job should have id"
            assert "title" in job, "Job should have title"
            assert "company" in job, "Job should have company"
            assert "source" in job, "Job should have source"


# Cleanup fixture
@pytest.fixture(scope="module", autouse=True)
def cleanup(auth_token):
    """Cleanup test data after all tests"""
    yield
    # Cleanup is handled by individual tests
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
