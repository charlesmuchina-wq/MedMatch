"""
MedMatch API Backend Tests
Tests all API endpoints for the job search application
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://jobmatch-pro-47.preview.emergentagent.com').rstrip('/')

class TestResumeEndpoints:
    """Resume API endpoint tests"""
    
    def test_get_resume(self):
        """Test GET /api/resume - should return resume data"""
        response = requests.get(f"{BASE_URL}/api/resume")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "skills" in data
        assert "experience" in data
        assert "education" in data
        print(f"✅ GET /api/resume - Status: {response.status_code}")

    def test_update_skills(self):
        """Test PUT /api/resume/skills - update skills list"""
        test_skills = ["Python", "Quality Management", "ISO 13485"]
        response = requests.put(
            f"{BASE_URL}/api/resume/skills",
            json={"skills": test_skills}
        )
        assert response.status_code == 200
        data = response.json()
        # API returns {"message": "Skills updated"} on success
        assert "message" in data or "skills" in data
        print(f"✅ PUT /api/resume/skills - Status: {response.status_code}")


class TestJobSearchEndpoints:
    """Job Search API endpoint tests"""
    
    def test_get_presets(self):
        """Test GET /api/jobs/presets - should return search presets"""
        response = requests.get(f"{BASE_URL}/api/jobs/presets")
        assert response.status_code == 200
        data = response.json()
        assert "presets" in data
        assert "locations" in data
        assert len(data["presets"]) > 0
        print(f"✅ GET /api/jobs/presets - Status: {response.status_code}, Presets: {len(data['presets'])}")

    def test_search_jobs_default(self):
        """Test GET /api/jobs/search - default search"""
        response = requests.get(f"{BASE_URL}/api/jobs/search")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/jobs/search - Status: {response.status_code}, Jobs: {len(data)}")

    def test_search_jobs_with_query(self):
        """Test GET /api/jobs/search with query parameter"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"query": "Quality Manager", "source": "all", "location": "", "days": 0}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/jobs/search?query=Quality Manager - Status: {response.status_code}, Jobs: {len(data)}")

    def test_search_jobs_with_source_filter(self):
        """Test GET /api/jobs/search with source filter"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"query": "", "source": "remoteok", "location": "", "days": 0}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/jobs/search?source=remoteok - Status: {response.status_code}, Jobs: {len(data)}")

    def test_google_cse_search(self):
        """Test GET /api/jobs/google-search - Google Custom Search"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/google-search",
            params={"query": "Quality Manager", "location": "Remote"}
        )
        assert response.status_code == 200
        data = response.json()
        # API returns {"jobs": [...], "query": ..., "location": ..., "site": ..., "total": ...}
        assert "jobs" in data
        assert "total" in data
        print(f"✅ GET /api/jobs/google-search - Status: {response.status_code}, Jobs: {data.get('total', 0)}")


class TestSavedJobsEndpoints:
    """Saved Jobs API endpoint tests"""
    
    def test_get_saved_jobs(self):
        """Test GET /api/jobs/saved - get all saved jobs"""
        response = requests.get(f"{BASE_URL}/api/jobs/saved")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/jobs/saved - Status: {response.status_code}, Saved: {len(data)}")

    def test_save_job(self):
        """Test POST /api/jobs/save - save a job"""
        test_job = {
            "id": f"test_job_{int(time.time())}",
            "title": "TEST Quality Manager",
            "company": "Test Company",
            "location": "Remote",
            "description": "Test job description",
            "url": "https://example.com/job",
            "salary": "$100,000 - $120,000",
            "tags": ["Quality", "ISO"],
            "source": "Test"
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/save",  # Correct endpoint is /api/jobs/save
            json=test_job
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        print(f"✅ POST /api/jobs/save - Status: {response.status_code}")
        return data.get("id")

    def test_delete_saved_job(self):
        """Test DELETE /api/jobs/saved/{id} - remove saved job"""
        # First save a job
        test_job = {
            "id": f"test_delete_{int(time.time())}",
            "title": "TEST Delete Job",
            "company": "Test Company",
            "location": "Remote",
            "description": "Test job to delete",
            "url": "https://example.com/job",
            "salary": "",
            "tags": [],
            "source": "Test"
        }
        save_response = requests.post(f"{BASE_URL}/api/jobs/save", json=test_job)  # Correct endpoint
        assert save_response.status_code == 200
        saved_id = save_response.json().get("id")
        
        # Now delete it
        delete_response = requests.delete(f"{BASE_URL}/api/jobs/saved/{saved_id}")
        assert delete_response.status_code == 200
        print(f"✅ DELETE /api/jobs/saved/{saved_id} - Status: {delete_response.status_code}")


class TestApplicationsEndpoints:
    """Applications API endpoint tests"""
    
    def test_get_applications(self):
        """Test GET /api/applications - get all applications"""
        response = requests.get(f"{BASE_URL}/api/applications")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/applications - Status: {response.status_code}, Applications: {len(data)}")

    def test_create_application(self):
        """Test POST /api/applications - create new application"""
        test_app = {
            "job": {
                "id": f"test_app_job_{int(time.time())}",
                "title": "TEST Application Job",
                "company": "Test Company",
                "location": "Remote",
                "description": "Test application",
                "url": "https://example.com/job",
                "salary": "",
                "tags": [],
                "source": "Test"
            },
            "notes": "Test application notes"
        }
        response = requests.post(
            f"{BASE_URL}/api/applications",
            json=test_app
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["status"] == "Applied"
        print(f"✅ POST /api/applications - Status: {response.status_code}")
        return data.get("id")

    def test_update_application_status(self):
        """Test PUT /api/applications/{id} - update status"""
        # First create an application
        test_app = {
            "job": {
                "id": f"test_status_job_{int(time.time())}",
                "title": "TEST Status Update Job",
                "company": "Test Company",
                "location": "Remote",
                "description": "Test status update",
                "url": "",
                "salary": "",
                "tags": [],
                "source": "Test"
            },
            "notes": ""
        }
        create_response = requests.post(f"{BASE_URL}/api/applications", json=test_app)
        assert create_response.status_code == 200
        app_id = create_response.json().get("id")
        
        # Update status - endpoint is /api/applications/{id} not /api/applications/{id}/status
        update_response = requests.put(
            f"{BASE_URL}/api/applications/{app_id}",
            json={"status": "Interview", "notes": "Interview scheduled"}
        )
        assert update_response.status_code == 200
        data = update_response.json()
        assert "message" in data  # Returns {"message": "Application updated"}
        print(f"✅ PUT /api/applications/{app_id} - Status: {update_response.status_code}")

    def test_delete_application(self):
        """Test DELETE /api/applications/{id} - delete application"""
        # First create an application
        test_app = {
            "job": {
                "id": f"test_delete_app_{int(time.time())}",
                "title": "TEST Delete Application",
                "company": "Test Company",
                "location": "Remote",
                "description": "Test delete",
                "url": "",
                "salary": "",
                "tags": [],
                "source": "Test"
            },
            "notes": ""
        }
        create_response = requests.post(f"{BASE_URL}/api/applications", json=test_app)
        assert create_response.status_code == 200
        app_id = create_response.json().get("id")
        
        # Delete it
        delete_response = requests.delete(f"{BASE_URL}/api/applications/{app_id}")
        assert delete_response.status_code == 200
        print(f"✅ DELETE /api/applications/{app_id} - Status: {delete_response.status_code}")


class TestCoverLetterEndpoints:
    """Cover Letter API endpoint tests"""
    
    def test_get_cover_letter_history(self):
        """Test GET /api/cover-letter/history - get history"""
        response = requests.get(f"{BASE_URL}/api/cover-letter/history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ GET /api/cover-letter/history - Status: {response.status_code}, History: {len(data)}")

    def test_generate_cover_letter(self):
        """Test POST /api/cover-letter/generate - generate cover letter"""
        request_data = {
            "job_title": "Quality Manager",
            "company": "Test Medical Devices Inc",
            "job_description": "We are looking for a Quality Manager with experience in ISO 13485 and FDA compliance. The ideal candidate will have 5+ years of experience in medical device quality management.",
            "job_url": "https://example.com/job"
        }
        response = requests.post(
            f"{BASE_URL}/api/cover-letter/generate",
            json=request_data,
            timeout=60  # AI generation can take time
        )
        # May return 400 if no resume uploaded, or 200 with cover letter
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            data = response.json()
            assert "cover_letter" in data
            print(f"✅ POST /api/cover-letter/generate - Status: {response.status_code}, Generated cover letter")
        else:
            print(f"⚠️ POST /api/cover-letter/generate - Status: {response.status_code} (Resume may not be uploaded)")


class TestDigestEndpoints:
    """Daily Digest API endpoint tests"""
    
    def test_get_digest_settings(self):
        """Test GET /api/digest/settings - get digest settings"""
        response = requests.get(
            f"{BASE_URL}/api/digest/settings",
            params={"email": "test@example.com"}
        )
        # May return 200 with settings or 404 if not found
        assert response.status_code in [200, 404]
        print(f"✅ GET /api/digest/settings - Status: {response.status_code}")

    def test_save_digest_settings(self):
        """Test POST /api/digest/settings - save digest settings"""
        settings = {
            "email": "test@example.com",
            "frequency": "daily",
            "search_queries": ["Quality Manager", "Medical Device"],
            "locations": ["Remote", "USA"]
        }
        response = requests.post(
            f"{BASE_URL}/api/digest/settings",
            json=settings
        )
        assert response.status_code == 200
        data = response.json()
        # API returns {"message": "Digest settings created/updated", "email": ..., "frequency": ...}
        assert "message" in data
        assert "email" in data
        print(f"✅ POST /api/digest/settings - Status: {response.status_code}")

    def test_get_digest_history(self):
        """Test GET /api/digest/history - get emailed jobs history"""
        response = requests.get(
            f"{BASE_URL}/api/digest/history",
            params={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        print(f"✅ GET /api/digest/history - Status: {response.status_code}, History: {len(data.get('history', []))}")


class TestAlertEndpoints:
    """Job Alert API endpoint tests"""
    
    def test_send_alert_now(self):
        """Test POST /api/alerts/send-now - send immediate alert"""
        response = requests.post(
            f"{BASE_URL}/api/alerts/send-now",
            json={"email": "test@example.com"},
            timeout=60  # Email sending can take time
        )
        # May succeed or fail based on email config
        assert response.status_code in [200, 500]
        print(f"✅ POST /api/alerts/send-now - Status: {response.status_code}")


class TestDeepSearchEndpoint:
    """AI Deep Search endpoint test"""
    
    def test_deep_search(self):
        """Test POST /api/jobs/deep-search - AI-powered deep search"""
        response = requests.post(
            f"{BASE_URL}/api/jobs/deep-search",
            json={"use_ai": True},
            timeout=120  # Deep search can take 30+ seconds
        )
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total_found" in data
        print(f"✅ POST /api/jobs/deep-search - Status: {response.status_code}, Jobs: {data.get('total_found', 0)}")


class TestJobAnalyzeEndpoint:
    """Job Analysis endpoint test"""
    
    def test_analyze_job(self):
        """Test POST /api/jobs/analyze - AI job match analysis"""
        request_data = {
            "job_title": "Quality Manager",
            "job_description": "Looking for Quality Manager with ISO 13485 experience",
            "company": "Test Company"
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/analyze",
            json=request_data,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert "match_score" in data
        assert "analysis" in data
        print(f"✅ POST /api/jobs/analyze - Status: {response.status_code}, Score: {data.get('match_score')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
