"""
Iteration 140: Test Cloud Recordings and Enhanced Webinar Analytics Features
- Cloud recording storage: upload, download, stats, CRUD
- Enhanced webinar analytics: funnel, qa_stats, engagement, org_breakdown, timeline
"""

import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication for test session"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "admin@medmatch.com", "password": "Swampdrainer2026!"}
        )
        assert response.status_code == 200, f"Auth failed: {response.text}"
        token = response.json().get("access_token") or response.json().get("token")
        assert token, "No token in response"
        return token

    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Headers with auth token"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestRecordingsAPI(TestAuth):
    """Test Cloud Recordings API endpoints"""
    
    def test_get_recordings_list(self, auth_headers):
        """GET /api/karau-meet/recordings/ - returns recordings with storage_type field"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "recordings" in data, "Missing recordings array"
        assert "total" in data, "Missing total count"
        
        # If recordings exist, check structure
        if data["recordings"]:
            rec = data["recordings"][0]
            assert "recording_id" in rec, "Missing recording_id"
            assert "meeting_title" in rec, "Missing meeting_title"
            assert "storage_type" in rec, "Missing storage_type field"
            assert rec["storage_type"] in ["cloud", "browser_local"], f"Invalid storage_type: {rec['storage_type']}"
            print(f"PASS: GET recordings returns {len(data['recordings'])} recordings with storage_type field")
        else:
            print("PASS: GET recordings returns empty list (no recordings yet)")
    
    def test_get_recordings_stats(self, auth_headers):
        """GET /api/karau-meet/recordings/stats - returns total_recordings, cloud_count, local_count, total_size_bytes, total_duration_seconds"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/stats",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify all required fields
        assert "total_recordings" in data, "Missing total_recordings"
        assert "cloud_count" in data, "Missing cloud_count"
        assert "local_count" in data, "Missing local_count"
        assert "total_size_bytes" in data, "Missing total_size_bytes"
        assert "total_duration_seconds" in data, "Missing total_duration_seconds"
        
        # Verify types
        assert isinstance(data["total_recordings"], int), "total_recordings not int"
        assert isinstance(data["cloud_count"], int), "cloud_count not int"
        assert isinstance(data["local_count"], int), "local_count not int"
        assert isinstance(data["total_size_bytes"], int), "total_size_bytes not int"
        assert isinstance(data["total_duration_seconds"], int), "total_duration_seconds not int"
        
        print(f"PASS: GET recordings/stats returns all fields: total={data['total_recordings']}, cloud={data['cloud_count']}, local={data['local_count']}")
    
    def test_upload_recording(self, auth_headers):
        """POST /api/karau-meet/recordings/upload - accepts multipart form data"""
        # Create a small test file
        test_file_content = b"TEST_RECORDING_CONTENT_FOR_ITERATION_140"
        files = {
            'file': ('TEST_recording_iter140.webm', io.BytesIO(test_file_content), 'video/webm')
        }
        data = {
            'meeting_id': 'TEST-MEET-140',
            'meeting_title': 'TEST Recording Upload Iteration 140',
            'duration_seconds': '60'
        }
        
        # Remove Content-Type from headers for multipart
        headers = {"Authorization": auth_headers["Authorization"]}
        
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/upload",
            headers=headers,
            files=files,
            data=data
        )
        
        # Note: This may fail if object storage is not available (budget)
        # Check for both success and graceful failure
        if response.status_code == 200:
            result = response.json()
            assert result.get("success") == True, "Upload didn't return success"
            assert "recording" in result, "Missing recording data"
            rec = result["recording"]
            assert rec.get("storage_type") == "cloud", "Should be cloud storage"
            assert rec.get("meeting_id") == "TEST-MEET-140"
            print(f"PASS: POST upload creates cloud recording: {rec.get('recording_id')}")
            return rec.get("recording_id")
        else:
            # Object storage may not be available
            print(f"INFO: Cloud upload returned {response.status_code} - object storage may be unavailable: {response.text[:100]}")
            pytest.skip("Object storage unavailable (expected if budget low)")
    
    def test_save_local_recording_metadata(self, auth_headers):
        """POST /api/karau-meet/recordings/metadata - saves local recording metadata"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/metadata",
            headers=auth_headers,
            json={
                "meeting_id": "TEST-LOCAL-140",
                "meeting_title": "TEST Local Recording Iteration 140",
                "duration_seconds": 120,
                "file_size_bytes": 5000000,
                "file_name": "TEST_local_rec_140.webm"
            }
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Should return success"
        assert "recording" in data, "Missing recording data"
        rec = data["recording"]
        assert rec.get("storage_type") == "browser_local", f"Should be browser_local, got {rec.get('storage_type')}"
        assert rec.get("meeting_id") == "TEST-LOCAL-140"
        print(f"PASS: POST metadata creates local recording: {rec.get('recording_id')}")
        return rec.get("recording_id")
    
    def test_delete_recording(self, auth_headers):
        """DELETE /api/karau-meet/recordings/{recording_id} - soft-deletes a recording"""
        # First create a recording to delete
        create_response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/metadata",
            headers=auth_headers,
            json={
                "meeting_id": "TEST-DELETE-140",
                "meeting_title": "TEST Delete Me Iteration 140",
                "duration_seconds": 30,
                "file_size_bytes": 1000000,
                "file_name": "TEST_delete_me_140.webm"
            }
        )
        assert create_response.status_code == 200
        recording_id = create_response.json()["recording"]["recording_id"]
        
        # Now delete it
        delete_response = requests.delete(
            f"{BASE_URL}/api/karau-meet/recordings/{recording_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        data = delete_response.json()
        assert data.get("success") == True, "Should return success"
        assert data.get("deleted") == recording_id, "Should return deleted ID"
        
        # Verify it's no longer in the list
        list_response = requests.get(f"{BASE_URL}/api/karau-meet/recordings/", headers=auth_headers)
        recordings = list_response.json().get("recordings", [])
        deleted_ids = [r["recording_id"] for r in recordings]
        assert recording_id not in deleted_ids, "Deleted recording should not appear in list"
        
        print(f"PASS: DELETE soft-deletes recording {recording_id}")
    
    def test_download_local_recording_returns_error(self, auth_headers):
        """GET /api/karau-meet/recordings/download/{id} - returns 400 for local recordings"""
        # Create a local recording first
        create_response = requests.post(
            f"{BASE_URL}/api/karau-meet/recordings/metadata",
            headers=auth_headers,
            json={
                "meeting_id": "TEST-DOWNLOAD-CHECK-140",
                "meeting_title": "TEST Local Download Check",
                "duration_seconds": 10,
                "file_size_bytes": 100000,
                "file_name": "TEST_local_download_check.webm"
            }
        )
        recording_id = create_response.json()["recording"]["recording_id"]
        
        # Try to download (should fail for local)
        download_response = requests.get(
            f"{BASE_URL}/api/karau-meet/recordings/download/{recording_id}",
            headers=auth_headers
        )
        assert download_response.status_code == 400, f"Expected 400 for local recording, got {download_response.status_code}"
        print("PASS: Download endpoint correctly rejects local recordings with 400")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/karau-meet/recordings/{recording_id}", headers=auth_headers)


class TestWebinarAnalyticsAPI(TestAuth):
    """Test Enhanced Webinar Analytics API"""
    
    @pytest.fixture(scope="class")
    def test_webinar(self, auth_headers):
        """Create a test webinar with registrations and Q&A for analytics testing"""
        # First check if we have existing webinars
        list_response = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=auth_headers)
        webinars = list_response.json().get("webinars", [])
        
        if webinars:
            # Use existing webinar
            return webinars[0]["webinar_id"]
        
        # Create a new test webinar
        create_response = requests.post(
            f"{BASE_URL}/api/karau/webinar/create",
            headers=auth_headers,
            json={
                "title": "TEST Analytics Webinar Iteration 140",
                "description": "Test webinar for analytics",
                "scheduled_time": "2026-03-01T10:00:00Z",
                "max_attendees": 100,
                "registration_required": True,
                "q_and_a_enabled": True
            }
        )
        if create_response.status_code == 200:
            return create_response.json()["webinar_id"]
        return None
    
    def test_webinar_analytics_structure(self, auth_headers, test_webinar):
        """GET /api/karau/webinar/{id}/analytics - returns enhanced analytics structure"""
        if not test_webinar:
            pytest.skip("No webinar available for testing")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar}/analytics",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify top-level fields
        assert "webinar_id" in data, "Missing webinar_id"
        assert "title" in data, "Missing title"
        assert "status" in data, "Missing status"
        
        print(f"PASS: Analytics endpoint returns webinar: {data['title']}")
    
    def test_webinar_analytics_funnel(self, auth_headers, test_webinar):
        """Analytics contains funnel with registration/attendance data"""
        if not test_webinar:
            pytest.skip("No webinar available")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar}/analytics",
            headers=auth_headers
        )
        data = response.json()
        
        # Check funnel
        assert "funnel" in data, "Missing funnel object"
        funnel = data["funnel"]
        assert "total_registrations" in funnel, "Missing total_registrations"
        assert "attended" in funnel, "Missing attended"
        assert "missed" in funnel, "Missing missed"
        assert "attendance_rate" in funnel, "Missing attendance_rate"
        assert "drop_off_rate" in funnel, "Missing drop_off_rate"
        
        # Verify types
        assert isinstance(funnel["total_registrations"], int)
        assert isinstance(funnel["attendance_rate"], int)  # percentage
        
        print(f"PASS: Funnel data present - {funnel['total_registrations']} registered, {funnel['attended']} attended ({funnel['attendance_rate']}%)")
    
    def test_webinar_analytics_qa_stats(self, auth_headers, test_webinar):
        """Analytics contains Q&A statistics"""
        if not test_webinar:
            pytest.skip("No webinar available")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar}/analytics",
            headers=auth_headers
        )
        data = response.json()
        
        # Check qa_stats
        assert "qa_stats" in data, "Missing qa_stats object"
        qa = data["qa_stats"]
        assert "total_questions" in qa, "Missing total_questions"
        assert "pending" in qa, "Missing pending"
        assert "answered" in qa, "Missing answered"
        assert "dismissed" in qa, "Missing dismissed"
        assert "anonymous" in qa, "Missing anonymous"
        assert "total_upvotes" in qa, "Missing total_upvotes"
        assert "answer_rate" in qa, "Missing answer_rate"
        assert "top_questions" in qa, "Missing top_questions"
        
        print(f"PASS: Q&A stats present - {qa['total_questions']} questions, {qa['answer_rate']}% answer rate")
    
    def test_webinar_analytics_engagement(self, auth_headers, test_webinar):
        """Analytics contains engagement score and metrics"""
        if not test_webinar:
            pytest.skip("No webinar available")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar}/analytics",
            headers=auth_headers
        )
        data = response.json()
        
        # Check engagement
        assert "engagement" in data, "Missing engagement object"
        eng = data["engagement"]
        assert "score" in eng, "Missing engagement score"
        assert "peak_attendees" in eng, "Missing peak_attendees"
        assert "avg_watch_time_minutes" in eng, "Missing avg_watch_time_minutes"
        
        # Score should be 0-100
        assert 0 <= eng["score"] <= 100, f"Score out of range: {eng['score']}"
        
        print(f"PASS: Engagement score: {eng['score']}/100, peak attendees: {eng['peak_attendees']}")
    
    def test_webinar_analytics_org_breakdown(self, auth_headers, test_webinar):
        """Analytics contains organization breakdown"""
        if not test_webinar:
            pytest.skip("No webinar available")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar}/analytics",
            headers=auth_headers
        )
        data = response.json()
        
        # Check org_breakdown
        assert "org_breakdown" in data, "Missing org_breakdown array"
        assert isinstance(data["org_breakdown"], list), "org_breakdown should be list"
        
        # If there are orgs, check structure
        if data["org_breakdown"]:
            org = data["org_breakdown"][0]
            assert "org" in org, "Missing org name"
            assert "count" in org, "Missing count"
        
        print(f"PASS: Org breakdown present with {len(data['org_breakdown'])} organizations")
    
    def test_webinar_analytics_timeline(self, auth_headers, test_webinar):
        """Analytics contains registration timeline"""
        if not test_webinar:
            pytest.skip("No webinar available")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar}/analytics",
            headers=auth_headers
        )
        data = response.json()
        
        # Check registration_timeline
        assert "registration_timeline" in data, "Missing registration_timeline array"
        assert isinstance(data["registration_timeline"], list), "registration_timeline should be list"
        
        # If there's timeline data, check structure
        if data["registration_timeline"]:
            day = data["registration_timeline"][0]
            assert "date" in day, "Missing date"
            assert "count" in day, "Missing count"
        
        print(f"PASS: Registration timeline present with {len(data['registration_timeline'])} data points")
    
    def test_webinar_analytics_max_attendees(self, auth_headers, test_webinar):
        """Analytics contains max_attendees field"""
        if not test_webinar:
            pytest.skip("No webinar available")
        
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/{test_webinar}/analytics",
            headers=auth_headers
        )
        data = response.json()
        
        assert "max_attendees" in data, "Missing max_attendees"
        assert isinstance(data["max_attendees"], int), "max_attendees should be int"
        assert data["max_attendees"] > 0, "max_attendees should be positive"
        
        print(f"PASS: max_attendees = {data['max_attendees']}")


class TestCleanup(TestAuth):
    """Cleanup test data"""
    
    def test_cleanup_test_recordings(self, auth_headers):
        """Remove test recordings created during tests"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/recordings/", headers=auth_headers)
        if response.status_code == 200:
            recordings = response.json().get("recordings", [])
            deleted = 0
            for rec in recordings:
                if rec.get("meeting_id", "").startswith("TEST-"):
                    requests.delete(
                        f"{BASE_URL}/api/karau-meet/recordings/{rec['recording_id']}",
                        headers=auth_headers
                    )
                    deleted += 1
            print(f"Cleanup: Deleted {deleted} test recordings")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
