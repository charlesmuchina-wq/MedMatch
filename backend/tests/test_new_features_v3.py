"""
Test Suite for New Features - Iteration 49
Tests: Job Sources, Notifications, Geolocation, Job Verification APIs
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "test_jobseeker_ui@test.com"
TEST_PASSWORD = "Test123!"


class TestHealthAndBasics:
    """Basic health and connectivity tests"""
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check passed: {data}")
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        print(f"✅ Status check passed: {data['mongodb']['status']}")


class TestAuthentication:
    """Authentication tests to get token for protected endpoints"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")  # Fixed: use access_token
            print(f"✅ Login successful, got token")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            pytest.skip("Authentication failed - skipping authenticated tests")
    
    def test_login(self, auth_token):
        """Verify login works"""
        assert auth_token is not None
        print(f"✅ Auth token obtained")


class TestJobSources:
    """Test Job Sources API - Multi-board integration"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("access_token")  # Fixed: use access_token
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_job_search_returns_results(self, auth_headers):
        """Test job search returns results from multiple sources"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"q": "engineer"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        print(f"✅ Job search returned {len(data.get('jobs', []))} jobs")
    
    def test_job_search_with_location(self, auth_headers):
        """Test job search with location filter"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"q": "quality", "location": "remote"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Job search with location returned {len(data.get('jobs', []))} jobs")
    
    def test_job_sources_endpoint(self, auth_headers):
        """Test GET /api/jobs/sources returns available sources"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/sources",
            headers=auth_headers
        )
        # This endpoint may or may not exist - check
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Job sources endpoint returned: {data}")
        elif response.status_code == 404:
            print(f"⚠️ Job sources endpoint not found (404) - may need to be added")
        else:
            print(f"⚠️ Job sources endpoint returned: {response.status_code}")


class TestNotifications:
    """Test Notification Center APIs"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_get_notifications(self, auth_headers):
        """Test GET /api/notifications returns notifications list"""
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            params={"limit": 20},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        print(f"✅ Notifications: {len(data['notifications'])} total, {data['unread_count']} unread")
    
    def test_get_notification_preferences(self, auth_headers):
        """Test GET /api/notifications/preferences"""
        response = requests.get(
            f"{BASE_URL}/api/notifications/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Notification preferences: {data}")
    
    def test_update_notification_preferences(self, auth_headers):
        """Test PUT /api/notifications/preferences"""
        preferences = {
            "email_enabled": True,
            "push_enabled": True,
            "in_app_enabled": True,
            "job_match_threshold": 85,
            "digest_frequency": "daily",
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00"
        }
        response = requests.put(
            f"{BASE_URL}/api/notifications/preferences",
            json=preferences,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✅ Updated notification preferences: {data['message']}")
    
    def test_create_test_notification(self, auth_headers):
        """Test POST /api/notifications/test creates a test notification"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/test",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data or "title" in data
        print(f"✅ Test notification created: {data.get('title', data)}")
    
    def test_mark_notification_read(self, auth_headers):
        """Test marking a notification as read"""
        # First get notifications
        response = requests.get(
            f"{BASE_URL}/api/notifications",
            params={"limit": 5},
            headers=auth_headers
        )
        if response.status_code == 200:
            notifications = response.json().get("notifications", [])
            if notifications:
                notif_id = notifications[0].get("id")
                # Mark as read
                read_response = requests.post(
                    f"{BASE_URL}/api/notifications/{notif_id}/read",
                    headers=auth_headers
                )
                assert read_response.status_code == 200
                print(f"✅ Marked notification {notif_id} as read")
            else:
                print("⚠️ No notifications to mark as read")
        else:
            print(f"⚠️ Could not get notifications: {response.status_code}")
    
    def test_mark_all_notifications_read(self, auth_headers):
        """Test POST /api/notifications/read-all"""
        response = requests.post(
            f"{BASE_URL}/api/notifications/read-all",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Mark all read: {data}")


class TestGeolocation:
    """Test Geolocation APIs - Location preferences and distance calculations"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_get_geolocation_preferences(self, auth_headers):
        """Test GET /api/geolocation/preferences"""
        response = requests.get(
            f"{BASE_URL}/api/geolocation/preferences",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Geolocation preferences: {data}")
    
    def test_update_geolocation_preferences(self, auth_headers):
        """Test PUT /api/geolocation/preferences"""
        preferences = {
            "home_lat": 37.7749,
            "home_lon": -122.4194,
            "home_address": "San Francisco, CA",
            "preferred_radius_miles": 25,
            "commute_preference": "driving",
            "location_alerts_enabled": True,
            "preferred_work_types": ["remote", "hybrid", "onsite"]
        }
        response = requests.put(
            f"{BASE_URL}/api/geolocation/preferences",
            json=preferences,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("success") == True
        print(f"✅ Updated geolocation preferences: {data}")
    
    def test_calculate_distance(self, auth_headers):
        """Test POST /api/geolocation/distance - Haversine calculation"""
        # San Francisco to Los Angeles
        distance_data = {
            "lat1": 37.7749,
            "lon1": -122.4194,
            "lat2": 34.0522,
            "lon2": -118.2437
        }
        response = requests.post(
            f"{BASE_URL}/api/geolocation/distance",
            json=distance_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "distance_miles" in data
        assert "distance_km" in data
        assert "commute_estimate" in data
        # SF to LA is about 380 miles
        assert 350 < data["distance_miles"] < 420
        print(f"✅ Distance calculation: {data['distance_miles']} miles, {data['distance_km']} km")
        print(f"   Commute estimate: {data['commute_estimate']}")
    
    def test_get_major_hubs(self, auth_headers):
        """Test GET /api/geolocation/hubs returns 15 major hubs"""
        response = requests.get(
            f"{BASE_URL}/api/geolocation/hubs",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "hubs" in data
        assert "total" in data
        assert data["total"] == 15, f"Expected 15 hubs, got {data['total']}"
        print(f"✅ Major hubs: {data['total']} hubs returned")
        for hub in data["hubs"][:5]:
            print(f"   - {hub['name']}: ({hub['lat']}, {hub['lon']})")
    
    def test_get_nearest_hub(self, auth_headers):
        """Test GET /api/geolocation/nearest-hub"""
        response = requests.get(
            f"{BASE_URL}/api/geolocation/nearest-hub",
            params={"lat": 37.7749, "lon": -122.4194},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "distance_miles" in data
        print(f"✅ Nearest hub to SF: {data['name']} ({data['distance_miles']} miles)")
    
    def test_geocode_address(self, auth_headers):
        """Test POST /api/geolocation/geocode"""
        response = requests.post(
            f"{BASE_URL}/api/geolocation/geocode",
            json={"address": "Boston"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "found" in data
        if data["found"]:
            assert "coordinates" in data
            print(f"✅ Geocoded Boston: {data['coordinates']}")
        else:
            print(f"⚠️ Geocoding returned: {data}")
    
    def test_commute_estimate(self, auth_headers):
        """Test GET /api/geolocation/commute-estimate"""
        response = requests.get(
            f"{BASE_URL}/api/geolocation/commute-estimate",
            params={"distance_miles": 25, "mode": "driving"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "minutes" in data or "time" in data or "estimate" in data
        print(f"✅ Commute estimate for 25 miles: {data}")
    
    def test_radius_settings(self, auth_headers):
        """Test GET /api/geolocation/radius-settings"""
        response = requests.get(
            f"{BASE_URL}/api/geolocation/radius-settings",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "defaults" in data
        print(f"✅ Radius settings: {data['defaults']}")


class TestJobVerification:
    """Test Job Verification/Liveness APIs - Ghost job detection"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_report_expired_job(self, auth_headers):
        """Test POST /api/jobs/verify/report - Report ghost job"""
        report_data = {
            "job_id": "test_job_123",
            "reason": "expired"
        }
        response = requests.post(
            f"{BASE_URL}/api/jobs/verify/report",
            json=report_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data or "message" in data or "report_count" in data
        print(f"✅ Job report submitted: {data}")
    
    def test_get_job_verification_status(self, auth_headers):
        """Test GET /api/jobs/verify/{job_id}"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/verify/test_job_123",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Job verification status: {data}")
    
    def test_verify_job_url(self, auth_headers):
        """Test POST /api/jobs/verify/{job_id} with URL"""
        response = requests.post(
            f"{BASE_URL}/api/jobs/verify/test_job_456",
            params={"url": "https://example.com/job/123"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Job URL verification: {data}")
    
    def test_check_url_status(self, auth_headers):
        """Test GET /api/jobs/verify/check-url"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/verify/check-url",
            params={"url": "https://www.google.com"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_alive" in data
        print(f"✅ URL check: {data}")


class TestJobFreshness:
    """Test job freshness badges in search results"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get auth headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        if response.status_code == 200:
            token = response.json().get("token")
            return {"Authorization": f"Bearer {token}"}
        pytest.skip("Authentication failed")
    
    def test_jobs_have_freshness_data(self, auth_headers):
        """Test that job search results include freshness information"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/search",
            params={"q": "engineer"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("jobs", [])
        
        if jobs:
            # Check if jobs have freshness data
            jobs_with_freshness = [j for j in jobs if j.get("freshness") or j.get("posted_at")]
            print(f"✅ Jobs with freshness data: {len(jobs_with_freshness)}/{len(jobs)}")
            
            # Sample a job
            sample_job = jobs[0]
            print(f"   Sample job: {sample_job.get('title', 'N/A')}")
            print(f"   Posted at: {sample_job.get('posted_at', 'N/A')}")
            print(f"   Freshness: {sample_job.get('freshness', 'N/A')}")
        else:
            print("⚠️ No jobs returned to check freshness")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
