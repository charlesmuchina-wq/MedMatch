"""
Test AI Intelligence Features - Iteration 149
Tests for Agentic AI, Voice Commands, Sentiment Analysis, and Predictive Scheduling

Endpoints under test:
- POST /api/karau-features/ai-agent/research - AI researches topic
- POST /api/karau-features/ai-agent/assign-action - Assign action item
- GET /api/karau-features/ai-agent/actions/{meeting_id} - Get action items
- POST /api/karau-features/voice-command/execute - Parse voice commands
- POST /api/karau-features/sentiment/analyze - Analyze sentiment
- GET /api/karau-features/sentiment/dashboard/{meeting_id} - Engagement dashboard
- POST /api/karau-features/scheduling/predict - Predict optimal schedule
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
TEST_MEETING_ID = "test-meet-2"

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@medmatch.com",
        "password": "Swampdrainer2026!"
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json().get("access_token")

@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Build auth headers"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestAIAgentResearch:
    """Test AI Agent Research endpoint"""
    
    def test_research_topic_success(self, auth_headers):
        """AI researches a topic and returns structured results with follow-up suggestions"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/ai-agent/research",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "topic": "quantum computing applications in healthcare",
                "context": "We are discussing AI innovations"
            }
        )
        assert response.status_code == 200, f"Research failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "research" in data, "Missing 'research' field"
        assert "topic" in data, "Missing 'topic' field"
        assert "follow_up_suggestions" in data, "Missing 'follow_up_suggestions' field"
        
        # Verify research content is not empty
        assert len(data["research"]) > 50, "Research response too short"
        assert data["topic"] == "quantum computing applications in healthcare"
        
        # Verify follow-up suggestions
        assert isinstance(data["follow_up_suggestions"], list), "follow_up_suggestions should be list"
        assert len(data["follow_up_suggestions"]) > 0, "Should have follow-up suggestions"
        print(f"Research returned {len(data['research'])} chars with {len(data['follow_up_suggestions'])} follow-ups")
    
    def test_research_requires_auth(self):
        """Research endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/ai-agent/research",
            json={"meeting_id": TEST_MEETING_ID, "topic": "test"}
        )
        assert response.status_code in [401, 403], "Should require auth"


class TestAIAgentActions:
    """Test AI Agent Action Items"""
    
    def test_assign_action_item(self, auth_headers):
        """Assigns action item to participant"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/ai-agent/assign-action",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "action_item": "Review the quarterly report and provide feedback",
                "assignee": "John Doe",
                "due_date": "2026-02-15"
            }
        )
        assert response.status_code == 200, f"Assign action failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") is True, "Should return success"
        assert "action" in data, "Missing 'action' field"
        
        action = data["action"]
        assert action.get("action_item") == "Review the quarterly report and provide feedback"
        assert action.get("assignee") == "John Doe"
        assert action.get("status") == "pending"
        assert "action_id" in action, "Missing action_id"
        assert "created_at" in action, "Missing created_at"
        print(f"Action item assigned: {action['action_id']}")
    
    def test_get_action_items(self, auth_headers):
        """Returns action items list for meeting"""
        response = requests.get(
            f"{BASE_URL}/api/karau-features/ai-agent/actions/{TEST_MEETING_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get actions failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "action_items" in data, "Missing 'action_items' field"
        assert isinstance(data["action_items"], list), "action_items should be list"
        print(f"Found {len(data['action_items'])} action items")
    
    def test_actions_requires_auth(self):
        """Actions endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-features/ai-agent/actions/{TEST_MEETING_ID}")
        assert response.status_code in [401, 403], "Should require auth"


class TestVoiceCommands:
    """Test Voice Command parsing"""
    
    def test_parse_mute_all_command(self, auth_headers):
        """Parses 'mute everyone' to {action: 'mute_all'}"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/voice-command/execute",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "command_text": "mute everyone"
            }
        )
        assert response.status_code == 200, f"Voice command failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "command" in data, "Missing 'command' field"
        assert "original_text" in data, "Missing 'original_text' field"
        assert "executed" in data, "Missing 'executed' field"
        
        cmd = data["command"]
        assert cmd.get("action") == "mute_all", f"Expected mute_all, got {cmd.get('action')}"
        print(f"Parsed 'mute everyone' -> {cmd}")
    
    def test_parse_start_recording_command(self, auth_headers):
        """Parses 'start recording' correctly"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/voice-command/execute",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "command_text": "start recording"
            }
        )
        assert response.status_code == 200, f"Voice command failed: {response.text}"
        data = response.json()
        
        cmd = data["command"]
        assert cmd.get("action") == "start_recording", f"Expected start_recording, got {cmd.get('action')}"
        assert data.get("executed") is True
        print(f"Parsed 'start recording' -> {cmd}")
    
    def test_parse_summarize_command(self, auth_headers):
        """Parses 'summarize last 5 minutes' correctly"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/voice-command/execute",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "command_text": "summarize last 5 minutes"
            }
        )
        assert response.status_code == 200, f"Voice command failed: {response.text}"
        data = response.json()
        
        cmd = data["command"]
        assert cmd.get("action") == "summarize", f"Expected summarize, got {cmd.get('action')}"
        assert "params" in cmd, "Missing params for summarize"
        assert cmd["params"].get("minutes") == 5 or "5" in str(cmd["params"]), "Should include minutes param"
        print(f"Parsed 'summarize last 5 minutes' -> {cmd}")
    
    def test_voice_command_requires_auth(self):
        """Voice command requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/voice-command/execute",
            json={"meeting_id": TEST_MEETING_ID, "command_text": "test"}
        )
        assert response.status_code in [401, 403], "Should require auth"


class TestSentimentAnalysis:
    """Test Sentiment Analysis endpoints"""
    
    def test_analyze_positive_sentiment(self, auth_headers):
        """Returns sentiment, engagement_level, energy, key_emotion for positive text"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/sentiment/analyze",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "text": "This is absolutely fantastic! I'm so excited about our progress and the team has done an amazing job. Let's celebrate our wins!",
                "speaker": "Alice"
            }
        )
        assert response.status_code == 200, f"Sentiment analysis failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "sentiment" in data, "Missing 'sentiment' field"
        assert "engagement_level" in data, "Missing 'engagement_level' field"
        assert "energy" in data, "Missing 'energy' field"
        assert "key_emotion" in data, "Missing 'key_emotion' field"
        
        # Verify positive sentiment detected
        assert data["sentiment"] in ["positive", "excited"], f"Expected positive/excited, got {data['sentiment']}"
        assert data["engagement_level"] >= 7, "High engagement text should have high engagement_level"
        print(f"Positive sentiment result: {data}")
    
    def test_analyze_negative_sentiment(self, auth_headers):
        """Returns appropriate sentiment for negative text"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/sentiment/analyze",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "text": "I'm really frustrated with these delays. We keep missing deadlines and nothing is working as expected.",
                "speaker": "Bob"
            }
        )
        assert response.status_code == 200, f"Sentiment analysis failed: {response.text}"
        data = response.json()
        
        assert data["sentiment"] in ["negative", "frustrated"], f"Expected negative, got {data['sentiment']}"
        assert "key_emotion" in data
        print(f"Negative sentiment result: {data}")
    
    def test_analyze_confused_sentiment(self, auth_headers):
        """Returns appropriate sentiment for confused text"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/sentiment/analyze",
            headers=auth_headers,
            json={
                "meeting_id": TEST_MEETING_ID,
                "text": "I'm not sure I understand. Can you explain that again? What exactly does this mean? I'm a bit lost here.",
                "speaker": "Charlie"
            }
        )
        assert response.status_code == 200, f"Sentiment analysis failed: {response.text}"
        data = response.json()
        
        assert data["sentiment"] in ["confused", "neutral"], f"Expected confused/neutral, got {data['sentiment']}"
        print(f"Confused sentiment result: {data}")
    
    def test_sentiment_requires_auth(self):
        """Sentiment analysis requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/sentiment/analyze",
            json={"meeting_id": TEST_MEETING_ID, "text": "test", "speaker": "Test"}
        )
        assert response.status_code in [401, 403], "Should require auth"


class TestSentimentDashboard:
    """Test Sentiment Dashboard endpoint"""
    
    def test_get_dashboard(self, auth_headers):
        """Returns engagement_score, dominant_energy, sentiment_breakdown, alerts"""
        response = requests.get(
            f"{BASE_URL}/api/karau-features/sentiment/dashboard/{TEST_MEETING_ID}",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "engagement_score" in data, "Missing 'engagement_score' field"
        assert "dominant_energy" in data, "Missing 'dominant_energy' field"
        assert "sentiment_breakdown" in data, "Missing 'sentiment_breakdown' field"
        assert "alerts" in data, "Missing 'alerts' field"
        
        # Verify types
        assert isinstance(data["alerts"], list), "alerts should be list"
        assert data["dominant_energy"] in ["high", "medium", "low"], f"Unexpected energy: {data['dominant_energy']}"
        print(f"Dashboard: engagement={data['engagement_score']}, energy={data['dominant_energy']}, alerts={len(data['alerts'])}")
    
    def test_dashboard_requires_auth(self):
        """Dashboard requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-features/sentiment/dashboard/{TEST_MEETING_ID}")
        assert response.status_code in [401, 403], "Should require auth"


class TestPredictiveScheduling:
    """Test Predictive Scheduling endpoint"""
    
    def test_predict_schedule(self, auth_headers):
        """Returns suggestions array with day, time, reason"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/scheduling/predict",
            headers=auth_headers,
            json={
                "participants": ["alice@example.com", "bob@example.com"],
                "duration_minutes": 30,
                "meeting_type": "standup",
                "timezone": "UTC"
            }
        )
        assert response.status_code == 200, f"Scheduling predict failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "suggestions" in data, "Missing 'suggestions' field"
        assert isinstance(data["suggestions"], list), "suggestions should be list"
        assert len(data["suggestions"]) > 0, "Should have at least one suggestion"
        
        # Verify suggestion structure
        for suggestion in data["suggestions"]:
            assert "day" in suggestion, "Suggestion missing 'day'"
            assert "time" in suggestion, "Suggestion missing 'time'"
            assert "reason" in suggestion, "Suggestion missing 'reason'"
        
        print(f"Got {len(data['suggestions'])} scheduling suggestions")
        for s in data["suggestions"][:3]:
            print(f"  - {s['day']} at {s['time']}: {s['reason'][:50]}...")
    
    def test_scheduling_requires_auth(self):
        """Scheduling endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/scheduling/predict",
            json={"duration_minutes": 30}
        )
        assert response.status_code in [401, 403], "Should require auth"


class TestRegressionFeatures:
    """Regression tests for existing KARAU features"""
    
    def test_translate_caption(self, auth_headers):
        """Verify translate-caption still works"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=auth_headers,
            json={
                "text": "Hello, how are you?",
                "target_language": "es"
            }
        )
        assert response.status_code == 200, f"Translate failed: {response.text}"
        data = response.json()
        assert "translated" in data or "translated_text" in data or "translation" in data
        print(f"Translation regression: PASS")
    
    def test_caption_languages(self, auth_headers):
        """Verify caption-languages still works"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/caption-languages",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Caption languages failed: {response.text}"
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) >= 10, "Should have at least 10 languages"
        print(f"Caption languages regression: PASS ({len(data['languages'])} languages)")
    
    def test_recordings_notes(self, auth_headers):
        """Verify recording notes endpoint still works"""
        # Get a webinar first
        webinars_resp = requests.get(f"{BASE_URL}/api/karau/webinar/list", headers=auth_headers)
        if webinars_resp.status_code == 200 and webinars_resp.json().get("webinars"):
            webinar_id = webinars_resp.json()["webinars"][0].get("webinar_id", "test")
            response = requests.get(f"{BASE_URL}/api/karau/webinar/{webinar_id}/notes", headers=auth_headers)
            # Either 200 (notes exist) or 404 (no notes) is acceptable
            assert response.status_code in [200, 404], f"Notes endpoint error: {response.text}"
            print(f"Recording notes regression: PASS")
        else:
            print("Recording notes regression: SKIP (no webinars)")
    
    def test_webinar_list(self, auth_headers):
        """Verify webinar list still works"""
        response = requests.get(
            f"{BASE_URL}/api/karau/webinar/list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Webinar list failed: {response.text}"
        data = response.json()
        assert "webinars" in data
        print(f"Webinar list regression: PASS ({len(data['webinars'])} webinars)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
