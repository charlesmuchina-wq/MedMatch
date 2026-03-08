"""
ENZI AI, Automation & Notifications API Tests - Iteration 191

Tests for new features:
- AI Auto-Reply Suggestions (POST /api/lumi/ai/auto-reply/suggestions)
- AI Conversation Summarize (POST /api/lumi/ai/summarize)
- Scheduled Messages CRUD (POST/GET/DELETE /api/lumi/automation/schedule)
- Webhooks for Bots (POST/GET/DELETE /api/lumi/automation/webhooks)
- Auto-Responders (POST/GET/DELETE /api/lumi/automation/auto-responders)
- Notification Preferences (GET/PUT prefs, DND, keywords)
"""
import pytest
import requests
import os
import uuid
from datetime import datetime, timedelta, timezone

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthSetup:
    """Authentication setup for tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    @pytest.fixture(scope="class")
    def test_channel_id(self, auth_headers):
        """Get or create a test channel"""
        # Get existing channels
        res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        if res.status_code == 200:
            channels = res.json().get("my_channels", [])
            if channels:
                return channels[0]["id"]
        
        # Create a new channel if none exist
        res = requests.post(f"{BASE_URL}/api/lumi/channels", 
            headers=auth_headers,
            json={"name": f"TEST_automation_{uuid.uuid4().hex[:6]}", "channel_type": "public"})
        if res.status_code in [200, 201]:
            return res.json().get("id")
        
        pytest.skip("No channels available for testing")


class TestAIAutoReplySuggestions(TestAuthSetup):
    """Tests for AI Auto-Reply Suggestions endpoint"""
    
    def test_auto_reply_suggestions_urgent(self, auth_headers, test_channel_id):
        """Test auto-reply suggestions for urgent bucket"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/auto-reply/suggestions",
            headers=auth_headers,
            json={
                "message_id": str(uuid.uuid4()),
                "channel_id": test_channel_id,
                "message_content": "This is extremely urgent, we need help now!",
                "bucket_category": "urgent"
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "suggestions" in data, "Missing suggestions in response"
        assert "category" in data, "Missing category in response"
        assert data["category"] == "urgent"
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) > 0, "No suggestions returned"
        print(f"AI Auto-Reply Suggestions (urgent): {data['suggestions']}")
    
    def test_auto_reply_suggestions_action_required(self, auth_headers, test_channel_id):
        """Test auto-reply suggestions for action_required bucket"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/auto-reply/suggestions",
            headers=auth_headers,
            json={
                "message_id": str(uuid.uuid4()),
                "channel_id": test_channel_id,
                "message_content": "Please review this document and approve",
                "bucket_category": "action_required"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "action_required"
        assert len(data["suggestions"]) > 0
        print(f"AI Auto-Reply Suggestions (action_required): {data['suggestions']}")
    
    def test_auto_reply_suggestions_meeting_request(self, auth_headers, test_channel_id):
        """Test auto-reply suggestions for meeting_request bucket"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/auto-reply/suggestions",
            headers=auth_headers,
            json={
                "message_id": str(uuid.uuid4()),
                "channel_id": test_channel_id,
                "message_content": "Can we schedule a meeting for tomorrow at 2pm?",
                "bucket_category": "meeting_request"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "meeting_request"
        assert len(data["suggestions"]) > 0
        print(f"AI Auto-Reply Suggestions (meeting_request): {data['suggestions']}")
    
    def test_auto_reply_suggestions_fyi(self, auth_headers, test_channel_id):
        """Test auto-reply suggestions for fyi bucket (default)"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/auto-reply/suggestions",
            headers=auth_headers,
            json={
                "message_id": str(uuid.uuid4()),
                "channel_id": test_channel_id,
                "message_content": "Just wanted to share this article with you",
                "bucket_category": "fyi"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "fyi"
        assert len(data["suggestions"]) > 0
        print(f"AI Auto-Reply Suggestions (fyi): {data['suggestions']}")
    
    def test_auto_reply_suggestions_no_bucket(self, auth_headers, test_channel_id):
        """Test auto-reply suggestions without bucket category (should use default)"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/auto-reply/suggestions",
            headers=auth_headers,
            json={
                "message_id": str(uuid.uuid4()),
                "channel_id": test_channel_id,
                "message_content": "Hello, how are you?"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) > 0
    
    def test_auto_reply_suggestions_unauthorized(self, test_channel_id):
        """Test auto-reply suggestions without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/auto-reply/suggestions",
            json={
                "message_id": str(uuid.uuid4()),
                "channel_id": test_channel_id,
                "message_content": "Test message"
            })
        assert response.status_code == 401


class TestAISummarize(TestAuthSetup):
    """Tests for AI Conversation Summarize endpoint"""
    
    def test_summarize_conversation(self, auth_headers, test_channel_id):
        """Test summarizing conversation in a channel"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/summarize",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "message_count": 50
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "summary" in data, "Missing summary in response"
        assert "message_count" in data, "Missing message_count in response"
        print(f"AI Summary ({data['message_count']} messages): {data['summary'][:200]}...")
    
    def test_summarize_empty_channel(self, auth_headers):
        """Test summarizing an empty/non-existent channel"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/summarize",
            headers=auth_headers,
            json={
                "channel_id": "non_existent_channel_id",
                "message_count": 50
            })
        
        assert response.status_code == 200  # Should return empty summary
        data = response.json()
        assert data["message_count"] == 0 or "No messages" in data.get("summary", "")
    
    def test_summarize_unauthorized(self, test_channel_id):
        """Test summarize without auth returns 401"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/summarize",
            json={"channel_id": test_channel_id})
        assert response.status_code == 401


class TestScheduledMessages(TestAuthSetup):
    """Tests for Scheduled Messages CRUD"""
    
    def test_schedule_message_create(self, auth_headers, test_channel_id):
        """Test creating a scheduled message"""
        future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/lumi/automation/schedule",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "content": f"TEST_scheduled_message_{uuid.uuid4().hex[:6]}",
                "scheduled_at": future_time
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Missing id in response"
        assert data["status"] == "scheduled"
        assert "scheduled_at" in data
        print(f"Scheduled message created: {data['id']} at {data['scheduled_at']}")
        return data["id"]
    
    def test_schedule_message_list(self, auth_headers):
        """Test listing pending scheduled messages"""
        response = requests.get(f"{BASE_URL}/api/lumi/automation/schedule",
            headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "scheduled" in data
        assert "count" in data
        assert isinstance(data["scheduled"], list)
        print(f"Scheduled messages count: {data['count']}")
    
    def test_schedule_message_cancel(self, auth_headers, test_channel_id):
        """Test cancelling a scheduled message"""
        # First create a message
        future_time = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        create_res = requests.post(f"{BASE_URL}/api/lumi/automation/schedule",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "content": f"TEST_to_cancel_{uuid.uuid4().hex[:6]}",
                "scheduled_at": future_time
            })
        assert create_res.status_code == 200
        msg_id = create_res.json()["id"]
        
        # Now cancel it
        response = requests.delete(f"{BASE_URL}/api/lumi/automation/schedule/{msg_id}",
            headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["status"] == "cancelled"
        print(f"Scheduled message cancelled: {msg_id}")
    
    def test_schedule_message_past_time(self, auth_headers, test_channel_id):
        """Test scheduling a message for past time should fail"""
        past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        
        response = requests.post(f"{BASE_URL}/api/lumi/automation/schedule",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "content": "This should fail",
                "scheduled_at": past_time
            })
        
        assert response.status_code == 400, "Past time scheduling should be rejected"
    
    def test_schedule_message_cancel_nonexistent(self, auth_headers):
        """Test cancelling a non-existent message should fail"""
        response = requests.delete(f"{BASE_URL}/api/lumi/automation/schedule/nonexistent_id",
            headers=auth_headers)
        assert response.status_code == 404


class TestWebhooks(TestAuthSetup):
    """Tests for Webhook system"""
    
    @pytest.fixture(scope="class")
    def created_webhook(self, auth_headers, test_channel_id):
        """Create a webhook for testing"""
        response = requests.post(f"{BASE_URL}/api/lumi/automation/webhooks",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "name": f"TEST_webhook_{uuid.uuid4().hex[:6]}",
                "events": ["message"]
            })
        assert response.status_code == 200
        return response.json()
    
    def test_webhook_create(self, auth_headers, test_channel_id):
        """Test creating a webhook"""
        response = requests.post(f"{BASE_URL}/api/lumi/automation/webhooks",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "name": f"TEST_webhook_{uuid.uuid4().hex[:6]}",
                "events": ["message", "member_join"]
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Missing id in response"
        assert "token" in data, "Missing token in response"
        assert "url" in data, "Missing url in response"
        assert "events" in data
        print(f"Webhook created: {data['id']}, URL: {data['url']}")
    
    def test_webhook_list(self, auth_headers):
        """Test listing webhooks"""
        response = requests.get(f"{BASE_URL}/api/lumi/automation/webhooks",
            headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "webhooks" in data
        assert "count" in data
        print(f"Webhooks count: {data['count']}")
    
    def test_webhook_send_message(self, created_webhook):
        """Test sending a message via webhook (no auth required)"""
        webhook_id = created_webhook["id"]
        
        response = requests.post(f"{BASE_URL}/api/lumi/automation/webhooks/{webhook_id}/send",
            json={
                "content": f"TEST_webhook_message_{uuid.uuid4().hex[:6]}",
                "username": "Test Bot"
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["status"] == "sent"
        assert "message_id" in data
        print(f"Webhook message sent: {data['message_id']}")
    
    def test_webhook_send_message_invalid(self):
        """Test sending to non-existent webhook"""
        response = requests.post(f"{BASE_URL}/api/lumi/automation/webhooks/nonexistent_id/send",
            json={"content": "Test"})
        assert response.status_code == 404
    
    def test_webhook_send_empty_message(self, created_webhook):
        """Test sending empty message via webhook should fail"""
        webhook_id = created_webhook["id"]
        response = requests.post(f"{BASE_URL}/api/lumi/automation/webhooks/{webhook_id}/send",
            json={})
        assert response.status_code == 400
    
    def test_webhook_delete(self, auth_headers, test_channel_id):
        """Test deleting a webhook"""
        # Create one to delete
        create_res = requests.post(f"{BASE_URL}/api/lumi/automation/webhooks",
            headers=auth_headers,
            json={"channel_id": test_channel_id, "name": "to_delete"})
        webhook_id = create_res.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/lumi/automation/webhooks/{webhook_id}",
            headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


class TestAutoResponders(TestAuthSetup):
    """Tests for Auto-Responders"""
    
    def test_auto_responder_create(self, auth_headers, test_channel_id):
        """Test creating an auto-responder"""
        response = requests.post(f"{BASE_URL}/api/lumi/automation/auto-responders",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "trigger": "hello",
                "response": "Hi there! How can I help you?",
                "is_active": True
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["status"] == "created"
        print(f"Auto-responder created: {data['id']}")
        return data["id"]
    
    def test_auto_responder_list(self, auth_headers):
        """Test listing auto-responders"""
        response = requests.get(f"{BASE_URL}/api/lumi/automation/auto-responders",
            headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "auto_responders" in data
        assert "count" in data
        print(f"Auto-responders count: {data['count']}")
    
    def test_auto_responder_delete(self, auth_headers, test_channel_id):
        """Test deleting an auto-responder"""
        # Create one to delete
        create_res = requests.post(f"{BASE_URL}/api/lumi/automation/auto-responders",
            headers=auth_headers,
            json={"channel_id": test_channel_id, "trigger": "bye", "response": "Goodbye!"})
        responder_id = create_res.json()["id"]
        
        # Delete it
        response = requests.delete(f"{BASE_URL}/api/lumi/automation/auto-responders/{responder_id}",
            headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"


class TestNotificationPreferences(TestAuthSetup):
    """Tests for Notification Preferences"""
    
    def test_get_notification_preferences(self, auth_headers):
        """Test getting notification preferences"""
        response = requests.get(f"{BASE_URL}/api/lumi/notifications/preferences",
            headers=auth_headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "dnd" in data or "channel_prefs" in data or "keyword_alerts" in data
        print(f"Notification preferences: {data}")
    
    def test_set_channel_notification_level(self, auth_headers, test_channel_id):
        """Test setting per-channel notification level"""
        response = requests.put(f"{BASE_URL}/api/lumi/notifications/channel",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "level": "mentions"
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["status"] == "updated"
        assert data["level"] == "mentions"
        print(f"Channel notification set: {test_channel_id} -> mentions")
    
    def test_set_channel_notification_invalid_level(self, auth_headers, test_channel_id):
        """Test setting invalid notification level"""
        response = requests.put(f"{BASE_URL}/api/lumi/notifications/channel",
            headers=auth_headers,
            json={
                "channel_id": test_channel_id,
                "level": "invalid_level"
            })
        assert response.status_code == 400
    
    def test_toggle_dnd_on(self, auth_headers):
        """Test enabling Do Not Disturb"""
        response = requests.put(f"{BASE_URL}/api/lumi/notifications/dnd",
            headers=auth_headers,
            json={
                "enabled": True,
                "start_time": "22:00",
                "end_time": "08:00",
                "timezone": "UTC"
            })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["status"] == "updated"
        assert data["dnd"]["enabled"] == True
        print(f"DND enabled: {data['dnd']}")
    
    def test_toggle_dnd_off(self, auth_headers):
        """Test disabling Do Not Disturb"""
        response = requests.put(f"{BASE_URL}/api/lumi/notifications/dnd",
            headers=auth_headers,
            json={"enabled": False})
        
        assert response.status_code == 200
        data = response.json()
        assert data["dnd"]["enabled"] == False
    
    def test_add_keyword_alert(self, auth_headers):
        """Test adding a keyword alert"""
        test_keyword = f"TEST_keyword_{uuid.uuid4().hex[:6]}"
        
        response = requests.post(f"{BASE_URL}/api/lumi/notifications/keywords",
            headers=auth_headers,
            json={"keyword": test_keyword})
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["status"] == "added"
        print(f"Keyword alert added: {test_keyword}")
        return test_keyword
    
    def test_remove_keyword_alert(self, auth_headers):
        """Test removing a keyword alert"""
        # First add one
        test_keyword = f"test_remove_{uuid.uuid4().hex[:6]}"
        requests.post(f"{BASE_URL}/api/lumi/notifications/keywords",
            headers=auth_headers,
            json={"keyword": test_keyword})
        
        # Now remove it
        response = requests.delete(f"{BASE_URL}/api/lumi/notifications/keywords/{test_keyword}",
            headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "removed"


class TestEndpointHealth:
    """Quick health checks for all endpoints"""
    
    def test_all_endpoints_reachable(self):
        """Verify all new endpoints exist and are reachable"""
        endpoints = [
            ("POST", "/api/lumi/ai/auto-reply/suggestions"),
            ("POST", "/api/lumi/ai/summarize"),
            ("POST", "/api/lumi/automation/schedule"),
            ("GET", "/api/lumi/automation/schedule"),
            ("POST", "/api/lumi/automation/webhooks"),
            ("GET", "/api/lumi/automation/webhooks"),
            ("POST", "/api/lumi/automation/auto-responders"),
            ("GET", "/api/lumi/automation/auto-responders"),
            ("GET", "/api/lumi/notifications/preferences"),
            ("PUT", "/api/lumi/notifications/channel"),
            ("PUT", "/api/lumi/notifications/dnd"),
            ("POST", "/api/lumi/notifications/keywords"),
        ]
        
        for method, endpoint in endpoints:
            url = f"{BASE_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json={})
            elif method == "PUT":
                response = requests.put(url, json={})
            
            # 401 means endpoint exists but requires auth (expected)
            # 422 means endpoint exists but request validation failed (expected for empty body)
            assert response.status_code in [200, 401, 422, 400], \
                f"{method} {endpoint} returned unexpected {response.status_code}"
            print(f"{method} {endpoint} -> {response.status_code} (reachable)")
