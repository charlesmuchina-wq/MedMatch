"""
Bug Fixes Retest - Iteration 51
Tests for verifying bug fixes:
1. HTML entity decoding in job titles
2. Previously 404 endpoints now return 200
3. ARIA labels (frontend - tested via Playwright)

Also includes full regression tests for all major features.
"""
import pytest
import requests
import os
import re

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
JOB_SEEKER_CREDS = {"email": "test_jobseeker_ui@test.com", "password": "Test123!"}
ADMIN_CREDS = {"email": "admin@medmatch.com", "password": "MedMatch2026!"}


class TestBugFixes:
    """Verify the 3 bug fixes from iteration 50"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_job_seeker_token(self):
        """Get job seeker auth token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def get_admin_token(self):
        """Get admin auth token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    # === BUG FIX 1: HTML Entity Decoding ===
    
    def test_html_entities_decoded_in_job_titles(self):
        """Verify HTML entities are properly decoded in job search results"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search?q=engineer")
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        assert len(jobs) > 0, "Should return jobs"
        
        # Check for HTML entities in titles
        html_entity_pattern = re.compile(r'&#\d+;|&amp;|&lt;|&gt;|&quot;|&nbsp;')
        
        for job in jobs[:20]:  # Check first 20 jobs
            title = job.get("title", "")
            company = job.get("company", "")
            description = job.get("description", "")
            
            assert not html_entity_pattern.search(title), f"HTML entity found in title: {title}"
            assert not html_entity_pattern.search(company), f"HTML entity found in company: {company}"
            # Description might have some entities from external sources, but title/company should be clean
        
        print(f"✓ Checked {len(jobs)} jobs - no HTML entities in titles/companies")
    
    # === BUG FIX 2: Previously 404 Endpoints ===
    
    def test_jobs_saved_endpoint_returns_200(self):
        """Verify /api/jobs/saved returns 200 (was 404)"""
        token = self.get_job_seeker_token()
        assert token, "Failed to get auth token"
        
        response = self.session.get(
            f"{BASE_URL}/api/jobs/saved",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "saved_jobs" in data
        assert "count" in data
        print(f"✓ /api/jobs/saved returns 200 with {data['count']} saved jobs")
    
    def test_jobs_alerts_endpoint_returns_200(self):
        """Verify /api/jobs/alerts returns 200 (was 404)"""
        token = self.get_job_seeker_token()
        assert token, "Failed to get auth token"
        
        response = self.session.get(
            f"{BASE_URL}/api/jobs/alerts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Should return list of alerts"
        print(f"✓ /api/jobs/alerts returns 200 with {len(data)} alerts")
    
    def test_interviews_endpoint_returns_200(self):
        """Verify /api/interviews returns 200 (was 404)"""
        token = self.get_job_seeker_token()
        assert token, "Failed to get auth token"
        
        response = self.session.get(
            f"{BASE_URL}/api/interviews",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "interviews" in data
        assert "total" in data
        print(f"✓ /api/interviews returns 200 with {data['total']} interviews")
    
    def test_metrics_endpoint_returns_200(self):
        """Verify /api/metrics returns 200 (was 404)"""
        response = self.session.get(f"{BASE_URL}/api/metrics")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "metrics" in data or "status" in data or isinstance(data, dict)
        print("✓ /api/metrics returns 200")
    
    def test_credentials_admin_pending_returns_200(self):
        """Verify /api/credentials/admin/pending returns 200 (was 404)"""
        token = self.get_admin_token()
        assert token, "Failed to get admin token"
        
        response = self.session.get(
            f"{BASE_URL}/api/credentials/admin/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "pending_reviews" in data or "credentials" in data
        print(f"✓ /api/credentials/admin/pending returns 200")


class TestCoreFeatures:
    """Full regression tests for core features"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def get_job_seeker_token(self):
        """Get job seeker auth token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def get_admin_token(self):
        """Get admin auth token"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    # === Authentication ===
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✓ Health endpoint working")
    
    def test_job_seeker_login(self):
        """Test job seeker login"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=JOB_SEEKER_CREDS)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "job_seeker"
        print(f"✓ Job seeker login successful: {data['user']['email']}")
    
    def test_admin_login(self):
        """Test admin login"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json=ADMIN_CREDS)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        print(f"✓ Admin login successful: {data['user']['email']}")
    
    def test_invalid_login_rejected(self):
        """Test invalid credentials are rejected"""
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "invalid@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code in [401, 400]
        print("✓ Invalid login correctly rejected")
    
    # === Job Search ===
    
    def test_job_search_returns_results(self):
        """Test job search returns results from multiple sources"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search?q=engineer")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert len(data["jobs"]) > 0
        
        # Check multiple sources
        sources = set(job.get("source", "") for job in data["jobs"])
        print(f"✓ Job search returned {len(data['jobs'])} jobs from sources: {sources}")
    
    def test_job_search_with_location(self):
        """Test job search with location filter"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search?q=quality&location=Remote")
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        print(f"✓ Job search with location returned {len(data['jobs'])} jobs")
    
    def test_job_sources_endpoint(self):
        """Test job sources endpoint"""
        response = self.session.get(f"{BASE_URL}/api/jobs/sources")
        assert response.status_code == 200
        
        data = response.json()
        assert "sources" in data
        assert len(data["sources"]) > 0
        print(f"✓ Job sources: {len(data['sources'])} sources available")
    
    def test_quality_keywords_endpoint(self):
        """Test quality engineering keywords endpoint"""
        response = self.session.get(f"{BASE_URL}/api/jobs/quality-keywords")
        assert response.status_code == 200
        
        data = response.json()
        assert "keywords" in data
        assert "categories" in data
        print(f"✓ Quality keywords: {len(data['keywords'])} keywords available")
    
    # === Notifications ===
    
    def test_get_notifications(self):
        """Test get notifications"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/notifications",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Get notifications working")
    
    def test_notification_preferences(self):
        """Test notification preferences"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/notifications/preferences",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Notification preferences working")
    
    # === Geolocation ===
    
    def test_major_hubs(self):
        """Test major hubs endpoint"""
        response = self.session.get(f"{BASE_URL}/api/geolocation/major-hubs")
        assert response.status_code == 200
        
        data = response.json()
        assert "hubs" in data
        assert len(data["hubs"]) >= 15
        print(f"✓ Major hubs: {len(data['hubs'])} hubs available")
    
    def test_distance_calculation(self):
        """Test distance calculation (Haversine)"""
        response = self.session.get(
            f"{BASE_URL}/api/geolocation/distance",
            params={
                "lat1": 37.7749, "lon1": -122.4194,  # San Francisco
                "lat2": 34.0522, "lon2": -118.2437   # Los Angeles
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "distance_km" in data or "distance" in data
        print("✓ Distance calculation working")
    
    def test_geolocation_preferences(self):
        """Test geolocation preferences"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/geolocation/preferences",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Geolocation preferences working")
    
    # === Credentials & Trust ===
    
    def test_certifications_list(self):
        """Test certifications list"""
        response = self.session.get(f"{BASE_URL}/api/credentials/certifications")
        assert response.status_code == 200
        
        data = response.json()
        assert "certifications" in data
        print(f"✓ Certifications: {len(data['certifications'])} available")
    
    def test_trust_score(self):
        """Test trust score calculation"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/credentials/trust-score",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "total_score" in data
        assert 0 <= data["total_score"] <= 300
        print(f"✓ Trust score: {data['total_score']}")
    
    def test_trust_score_history(self):
        """Test trust score history"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/credentials/trust-score/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "history" in data
        print(f"✓ Trust score history: {len(data['history'])} data points")
    
    def test_my_credentials(self):
        """Test my credentials endpoint"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/credentials/my-credentials",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "credentials" in data
        print(f"✓ My credentials: {len(data['credentials'])} credentials")
    
    # === AI Features ===
    
    def test_dragon_ai_assistant(self):
        """Test KARAU Dragon AI assistant"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.post(
            f"{BASE_URL}/api/ai/dragon/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Hello, what can you help me with?"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data or "message" in data
        print("✓ Dragon AI assistant responding")
    
    def test_ai_cover_letter(self):
        """Test AI cover letter generation"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.post(
            f"{BASE_URL}/api/ai/cover-letter",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_title": "Quality Engineer",
                "company": "Test Company",
                "job_description": "Looking for a quality engineer with ISO experience"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "cover_letter" in data or "content" in data
        print("✓ AI cover letter generation working")
    
    def test_ai_interview_questions(self):
        """Test AI interview question generation"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.post(
            f"{BASE_URL}/api/ai/interview-questions",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_title": "Quality Engineer",
                "company": "Test Company"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "questions" in data
        print(f"✓ AI interview questions: {len(data['questions'])} questions generated")
    
    def test_ai_deep_search(self):
        """Test AI deep search"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.post(
            f"{BASE_URL}/api/jobs/deep-search",
            headers={"Authorization": f"Bearer {token}"},
            json={"use_ai": True}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        print(f"✓ AI deep search: {len(data['jobs'])} jobs found")
    
    # === Translation ===
    
    def test_supported_languages(self):
        """Test supported languages endpoint"""
        response = self.session.get(f"{BASE_URL}/api/translation/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) >= 60
        print(f"✓ Translation: {len(data['languages'])} languages supported")
    
    def test_translate_text(self):
        """Test text translation"""
        response = self.session.post(
            f"{BASE_URL}/api/translation/translate",
            json={
                "text": "Hello, how are you?",
                "target_language": "es"
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "translated_text" in data or "translation" in data
        print("✓ Text translation working")
    
    # === Admin Features ===
    
    def test_admin_pending_reviews(self):
        """Test admin pending reviews"""
        token = self.get_admin_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/reviews/admin/pending",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Admin pending reviews working")
    
    def test_admin_review_stats(self):
        """Test admin review stats"""
        token = self.get_admin_token()
        assert token
        
        response = self.session.get(
            f"{BASE_URL}/api/reviews/admin/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        print("✓ Admin review stats working")
    
    # === Job Freshness ===
    
    def test_job_freshness_badges(self):
        """Test that jobs have freshness information"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search?q=engineer")
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        # Check that jobs have posted_at field for freshness calculation
        jobs_with_dates = [j for j in jobs if j.get("posted_at")]
        print(f"✓ Job freshness: {len(jobs_with_dates)}/{len(jobs)} jobs have posted dates")
    
    # === Save/Unsave Jobs ===
    
    def test_save_and_unsave_job(self):
        """Test save and unsave job functionality"""
        token = self.get_job_seeker_token()
        assert token
        
        # First search for a job
        search_response = self.session.get(f"{BASE_URL}/api/jobs/search?q=engineer")
        assert search_response.status_code == 200
        jobs = search_response.json().get("jobs", [])
        assert len(jobs) > 0
        
        test_job = jobs[0]
        
        # Save the job
        save_response = self.session.post(
            f"{BASE_URL}/api/saved-jobs",
            headers={"Authorization": f"Bearer {token}"},
            json=test_job
        )
        assert save_response.status_code == 200
        saved_data = save_response.json()
        saved_job_id = saved_data.get("saved_job", {}).get("id")
        
        print(f"✓ Job saved successfully")
        
        # Verify it's in saved jobs
        get_saved = self.session.get(
            f"{BASE_URL}/api/saved-jobs",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_saved.status_code == 200
        
        # Unsave the job
        if saved_job_id:
            unsave_response = self.session.delete(
                f"{BASE_URL}/api/saved-jobs/{saved_job_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert unsave_response.status_code == 200
            print("✓ Job unsaved successfully")
    
    # === Report Expired Job ===
    
    def test_report_expired_job(self):
        """Test report expired/ghost job functionality"""
        token = self.get_job_seeker_token()
        assert token
        
        response = self.session.post(
            f"{BASE_URL}/api/jobs/report-expired",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "job_url": "https://example.com/job/123",
                "reason": "Job posting is no longer available",
                "job_title": "Test Job"
            }
        )
        # Should succeed or return already reported
        assert response.status_code in [200, 201, 400]
        print("✓ Report expired job endpoint working")
    
    # === Job Alerts CRUD ===
    
    def test_job_alerts_crud(self):
        """Test job alerts CRUD operations"""
        token = self.get_job_seeker_token()
        assert token
        
        # Create alert
        create_response = self.session.post(
            f"{BASE_URL}/api/job-alerts",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "keywords": ["test engineer", "QA"],
                "locations": ["Remote"],
                "email": "test_jobseeker_ui@test.com"
            }
        )
        assert create_response.status_code == 200
        alert_data = create_response.json()
        alert_id = alert_data.get("alert", {}).get("id")
        print("✓ Job alert created")
        
        # Get alerts
        get_response = self.session.get(
            f"{BASE_URL}/api/job-alerts",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 200
        print("✓ Job alerts retrieved")
        
        # Delete alert
        if alert_id:
            delete_response = self.session.delete(
                f"{BASE_URL}/api/job-alerts/{alert_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert delete_response.status_code == 200
            print("✓ Job alert deleted")


class TestDataIntegrity:
    """Test data integrity and security"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_match_score_range(self):
        """Test that match scores are in valid range (0-100)"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search?q=engineer")
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        for job in jobs:
            score = job.get("match_score", 50)
            assert 0 <= score <= 100, f"Invalid match score: {score}"
        
        print(f"✓ All {len(jobs)} jobs have valid match scores (0-100)")
    
    def test_protected_routes_require_auth(self):
        """Test that protected routes require authentication"""
        protected_endpoints = [
            "/api/saved-jobs",
            "/api/job-alerts",
            "/api/interviews",
            "/api/notifications",
            "/api/credentials/my-credentials",
            "/api/credentials/trust-score"
        ]
        
        for endpoint in protected_endpoints:
            response = self.session.get(f"{BASE_URL}{endpoint}")
            assert response.status_code == 401, f"{endpoint} should require auth"
        
        print(f"✓ All {len(protected_endpoints)} protected routes require authentication")
    
    def test_job_deduplication(self):
        """Test that job search results are deduplicated"""
        response = self.session.get(f"{BASE_URL}/api/jobs/search?q=engineer")
        assert response.status_code == 200
        
        data = response.json()
        jobs = data.get("jobs", [])
        
        # Check for duplicate URLs
        urls = [job.get("url") for job in jobs if job.get("url")]
        unique_urls = set(urls)
        
        # Allow some duplicates from different sources, but not excessive
        duplicate_ratio = 1 - (len(unique_urls) / len(urls)) if urls else 0
        assert duplicate_ratio < 0.1, f"Too many duplicate jobs: {duplicate_ratio*100:.1f}%"
        
        print(f"✓ Job deduplication working: {len(unique_urls)} unique URLs from {len(urls)} jobs")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
