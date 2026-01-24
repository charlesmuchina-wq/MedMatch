"""
Interview Calendar API Tests
Tests: CRUD operations, AI preparation generation, stats, upcoming interviews
"""
import pytest
import requests
import os
import time
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Add delay between tests to avoid rate limiting
@pytest.fixture(autouse=True)
def rate_limit_delay():
    """Add delay between tests to avoid rate limiting"""
    yield
    time.sleep(1.5)  # Wait 1.5 seconds between tests

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "MedMatch2026!"


class TestInterviewCalendarAPI:
    """Interview Calendar endpoint tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login to get auth token
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("token") or data.get("access_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        yield
        
        # Cleanup: Delete test events
        try:
            events_response = self.session.get(f"{BASE_URL}/api/interview-calendar/events")
            if events_response.status_code == 200:
                events = events_response.json().get("events", [])
                for event in events:
                    if event.get("company", "").startswith("TEST_"):
                        self.session.delete(f"{BASE_URL}/api/interview-calendar/events/{event['id']}")
        except:
            pass
    
    # ============== Status Endpoint ==============
    
    def test_get_calendar_status(self):
        """Test GET /api/interview-calendar/status returns available=true with features"""
        response = self.session.get(f"{BASE_URL}/api/interview-calendar/status")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("available") == True, "Calendar should be available"
        assert "features" in data, "Response should include features"
        
        features = data.get("features", {})
        assert "ai_preparation" in features, "Features should include ai_preparation"
        assert "push_reminders" in features, "Features should include push_reminders"
        
        print(f"✓ Calendar status: available={data.get('available')}, features={features}")
    
    def test_status_requires_auth(self):
        """Test that status endpoint requires authentication"""
        session = requests.Session()
        response = session.get(f"{BASE_URL}/api/interview-calendar/status")
        
        assert response.status_code == 401, f"Expected 401 for unauthenticated request, got {response.status_code}"
        print("✓ Status endpoint correctly requires authentication")
    
    # ============== Events CRUD ==============
    
    def test_create_interview_event(self):
        """Test POST /api/interview-calendar/events creates interview event"""
        # Create event with future date
        future_date = (datetime.now() + timedelta(days=3)).isoformat()
        end_date = (datetime.now() + timedelta(days=3, hours=1)).isoformat()
        
        event_data = {
            "title": "Technical Interview",
            "company": "TEST_Google",
            "position": "Senior Software Engineer",
            "interview_type": "video",
            "start_time": future_date,
            "end_time": end_date,
            "location": "",
            "meeting_link": "https://meet.google.com/test-meeting",
            "notes": "Prepare for system design questions",
            "interviewer_name": "John Smith",
            "interviewer_email": "john@google.com"
        }
        
        response = self.session.post(f"{BASE_URL}/api/interview-calendar/events", json=event_data)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "event" in data, "Response should include event"
        
        event = data["event"]
        assert event.get("company") == "TEST_Google", "Company should match"
        assert event.get("position") == "Senior Software Engineer", "Position should match"
        assert event.get("interview_type") == "video", "Interview type should match"
        assert event.get("status") == "scheduled", "Status should be scheduled"
        assert "id" in event, "Event should have an ID"
        
        # Store event ID for later tests
        self.created_event_id = event["id"]
        
        print(f"✓ Created interview event: {event['id']} for {event['company']}")
        return event["id"]
    
    def test_get_all_events(self):
        """Test GET /api/interview-calendar/events returns user's interviews"""
        response = self.session.get(f"{BASE_URL}/api/interview-calendar/events")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "events" in data, "Response should include events array"
        assert "total" in data, "Response should include total count"
        assert isinstance(data["events"], list), "Events should be a list"
        
        print(f"✓ Retrieved {data['total']} interview events")
    
    def test_get_specific_event(self):
        """Test GET /api/interview-calendar/events/{id} returns specific interview"""
        # First create an event
        future_date = (datetime.now() + timedelta(days=5)).isoformat()
        end_date = (datetime.now() + timedelta(days=5, hours=1)).isoformat()
        
        create_response = self.session.post(f"{BASE_URL}/api/interview-calendar/events", json={
            "title": "Phone Screen",
            "company": "TEST_Amazon",
            "position": "Backend Developer",
            "interview_type": "phone",
            "start_time": future_date,
            "end_time": end_date
        })
        
        assert create_response.status_code == 200
        event_id = create_response.json()["event"]["id"]
        
        # Get specific event
        response = self.session.get(f"{BASE_URL}/api/interview-calendar/events/{event_id}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        event = response.json()
        assert event.get("id") == event_id, "Event ID should match"
        assert event.get("company") == "TEST_Amazon", "Company should match"
        assert event.get("position") == "Backend Developer", "Position should match"
        
        print(f"✓ Retrieved specific event: {event_id}")
    
    def test_get_nonexistent_event(self):
        """Test GET /api/interview-calendar/events/{id} returns 404 for nonexistent event"""
        response = self.session.get(f"{BASE_URL}/api/interview-calendar/events/nonexistent_event_123")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Correctly returns 404 for nonexistent event")
    
    def test_update_event_status(self):
        """Test PUT /api/interview-calendar/events/{id} updates event status"""
        # First create an event
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        end_date = (datetime.now() + timedelta(days=7, hours=1)).isoformat()
        
        create_response = self.session.post(f"{BASE_URL}/api/interview-calendar/events", json={
            "title": "Final Round",
            "company": "TEST_Microsoft",
            "position": "Full Stack Developer",
            "interview_type": "video",
            "start_time": future_date,
            "end_time": end_date
        })
        
        assert create_response.status_code == 200
        event_id = create_response.json()["event"]["id"]
        
        # Update status to completed
        update_response = self.session.put(f"{BASE_URL}/api/interview-calendar/events/{event_id}", json={
            "status": "completed"
        })
        
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}: {update_response.text}"
        
        # Verify update by getting the event
        get_response = self.session.get(f"{BASE_URL}/api/interview-calendar/events/{event_id}")
        assert get_response.status_code == 200
        
        updated_event = get_response.json()
        assert updated_event.get("status") == "completed", "Status should be updated to completed"
        
        print(f"✓ Updated event {event_id} status to completed")
    
    def test_delete_event(self):
        """Test DELETE /api/interview-calendar/events/{id} deletes event"""
        # First create an event
        future_date = (datetime.now() + timedelta(days=10)).isoformat()
        end_date = (datetime.now() + timedelta(days=10, hours=1)).isoformat()
        
        create_response = self.session.post(f"{BASE_URL}/api/interview-calendar/events", json={
            "title": "To Be Deleted",
            "company": "TEST_DeleteMe",
            "position": "Test Position",
            "interview_type": "in_person",
            "start_time": future_date,
            "end_time": end_date
        })
        
        assert create_response.status_code == 200
        event_id = create_response.json()["event"]["id"]
        
        # Delete the event
        delete_response = self.session.delete(f"{BASE_URL}/api/interview-calendar/events/{event_id}")
        
        assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}: {delete_response.text}"
        
        # Verify deletion by trying to get the event
        get_response = self.session.get(f"{BASE_URL}/api/interview-calendar/events/{event_id}")
        assert get_response.status_code == 404, "Deleted event should return 404"
        
        print(f"✓ Deleted event {event_id} and verified removal")
    
    # ============== AI Preparation ==============
    
    def test_generate_ai_preparation(self):
        """Test POST /api/interview-calendar/events/{id}/generate-preparation generates AI preparation"""
        # First create an event
        future_date = (datetime.now() + timedelta(days=4)).isoformat()
        end_date = (datetime.now() + timedelta(days=4, hours=1)).isoformat()
        
        create_response = self.session.post(f"{BASE_URL}/api/interview-calendar/events", json={
            "title": "AI Prep Test",
            "company": "TEST_Netflix",
            "position": "Data Engineer",
            "interview_type": "video",
            "start_time": future_date,
            "end_time": end_date,
            "notes": "Focus on data pipelines and ETL processes"
        })
        
        assert create_response.status_code == 200
        event_id = create_response.json()["event"]["id"]
        
        # Generate AI preparation
        prep_response = self.session.post(f"{BASE_URL}/api/interview-calendar/events/{event_id}/generate-preparation")
        
        assert prep_response.status_code == 200, f"Expected 200, got {prep_response.status_code}: {prep_response.text}"
        
        data = prep_response.json()
        assert data.get("success") == True, "Response should indicate success"
        assert "preparation" in data, "Response should include preparation"
        
        preparation = data["preparation"]
        assert "talking_points" in preparation, "Preparation should include talking_points"
        assert isinstance(preparation["talking_points"], list), "talking_points should be a list"
        assert len(preparation["talking_points"]) > 0, "talking_points should not be empty"
        
        # Check for other expected fields
        expected_fields = ["company_insights", "potential_questions", "tips"]
        for field in expected_fields:
            assert field in preparation, f"Preparation should include {field}"
        
        print(f"✓ Generated AI preparation with {len(preparation['talking_points'])} talking points")
        print(f"  - Company insights: {preparation.get('company_insights', '')[:100]}...")
        print(f"  - Potential questions: {len(preparation.get('potential_questions', []))} questions")
    
    # ============== Stats ==============
    
    def test_get_calendar_stats(self):
        """Test GET /api/interview-calendar/stats returns interview statistics"""
        response = self.session.get(f"{BASE_URL}/api/interview-calendar/stats")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Check required fields
        required_fields = ["total_interviews", "upcoming", "completed", "this_week"]
        for field in required_fields:
            assert field in data, f"Stats should include {field}"
            assert isinstance(data[field], int), f"{field} should be an integer"
        
        print(f"✓ Calendar stats: total={data['total_interviews']}, upcoming={data['upcoming']}, completed={data['completed']}, this_week={data['this_week']}")
    
    # ============== Upcoming Interviews ==============
    
    def test_get_upcoming_interviews(self):
        """Test GET /api/interview-calendar/upcoming returns upcoming interviews"""
        response = self.session.get(f"{BASE_URL}/api/interview-calendar/upcoming")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "events" in data, "Response should include events"
        assert "total" in data, "Response should include total"
        assert isinstance(data["events"], list), "Events should be a list"
        
        # Check that events have time_until field
        for event in data["events"]:
            assert "time_until" in event, "Each event should have time_until"
            assert "days" in event["time_until"], "time_until should include days"
            assert "hours" in event["time_until"], "time_until should include hours"
        
        print(f"✓ Retrieved {data['total']} upcoming interviews")
    
    def test_get_upcoming_with_days_param(self):
        """Test GET /api/interview-calendar/upcoming with days parameter"""
        response = self.session.get(f"{BASE_URL}/api/interview-calendar/upcoming?days=14")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "events" in data, "Response should include events"
        
        print(f"✓ Retrieved upcoming interviews for next 14 days: {data['total']} events")


class TestInterviewCalendarEdgeCases:
    """Edge case tests for Interview Calendar"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session with authentication"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Login
        login_response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        
        if login_response.status_code == 200:
            data = login_response.json()
            token = data.get("token") or data.get("access_token")
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        yield
    
    def test_create_event_missing_required_fields(self):
        """Test that creating event without required fields fails gracefully"""
        # Missing company and position
        response = self.session.post(f"{BASE_URL}/api/interview-calendar/events", json={
            "title": "Test",
            "interview_type": "video"
        })
        
        # Should either fail with 422 (validation error) or succeed with defaults
        assert response.status_code in [200, 422], f"Expected 200 or 422, got {response.status_code}"
        print(f"✓ Create event with missing fields handled: status {response.status_code}")
    
    def test_update_nonexistent_event(self):
        """Test updating nonexistent event returns 404"""
        response = self.session.put(f"{BASE_URL}/api/interview-calendar/events/nonexistent_123", json={
            "status": "completed"
        })
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Update nonexistent event correctly returns 404")
    
    def test_delete_nonexistent_event(self):
        """Test deleting nonexistent event returns 404"""
        response = self.session.delete(f"{BASE_URL}/api/interview-calendar/events/nonexistent_456")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Delete nonexistent event correctly returns 404")
    
    def test_generate_preparation_nonexistent_event(self):
        """Test generating preparation for nonexistent event returns 404"""
        response = self.session.post(f"{BASE_URL}/api/interview-calendar/events/nonexistent_789/generate-preparation")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Generate preparation for nonexistent event correctly returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
