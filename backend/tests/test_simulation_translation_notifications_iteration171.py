"""
Iteration 171 Tests - What-If Simulations, Message Translation, Smart Notifications, Enhanced Thread Panel
Tests new LUMI features:
1. What-If Simulations (POST /lumi/ai/simulate)
2. Message Translation (POST /lumi/ai/translate)
3. Smart Notifications (GET /lumi/ai/notifications)
4. Enhanced Thread Panel features
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_health_check(self):
        """Test health endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        assert response.status_code == 200
        print("✅ Health check passed")
    
    def test_auth_login(self):
        """Test login with admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        }, timeout=10)
        assert response.status_code == 200
        data = response.json()
        # API returns access_token instead of token
        assert "access_token" in data or "token" in data
        assert "user" in data
        token = data.get("access_token") or data.get("token")
        print(f"✅ Login successful for user: {data['user'].get('email')}")
        return token


@pytest.fixture(scope="class")
def auth_token():
    """Get authentication token for tests"""
    response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@medmatch.com",
        "password": "Swampdrainer2026!"
    }, timeout=10)
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token") or data.get("token")
    pytest.skip("Authentication failed - skipping authenticated tests")


@pytest.fixture(scope="class")
def auth_headers(auth_token):
    """Get headers with auth token"""
    return {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }


class TestWhatIfSimulation:
    """Tests for What-If Simulation feature (POST /lumi/ai/simulate)"""
    
    def test_simulate_endpoint_exists(self, auth_headers):
        """Test that simulate endpoint exists and accepts POST"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/simulate",
            headers=auth_headers,
            json={"scenario": "What if we add 2 more team members?"},
            timeout=60
        )
        # Should return 200 with simulation results
        assert response.status_code == 200
        print(f"✅ Simulate endpoint returned status {response.status_code}")
    
    def test_simulate_returns_structured_response(self, auth_headers):
        """Test that simulation returns expected fields"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/simulate",
            headers=auth_headers,
            json={"scenario": "What if we delay the project deadline by 1 week?"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields in response
        # Note: AI might return error if no project data exists
        if "error" not in data:
            # Check for expected simulation response fields
            expected_fields = ["scenario_summary", "risk_score", "recommendation"]
            found_fields = [f for f in expected_fields if f in data]
            print(f"✅ Simulation returned fields: {list(data.keys())}")
            assert len(found_fields) >= 1, f"Expected some of {expected_fields}, got {list(data.keys())}"
        else:
            print(f"⚠️ Simulation returned with message (possibly no data): {data.get('recommendation', data.get('error'))}")
        
    def test_simulate_with_entity_type(self, auth_headers):
        """Test simulation with specific entity type"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/simulate",
            headers=auth_headers,
            json={
                "scenario": "What if we remove a team member from the project?",
                "entity_type": "person",
                "entity_name": "Admin"
            },
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Entity-specific simulation completed: {list(data.keys())}")
    
    def test_simulate_requires_auth(self):
        """Test that simulate endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/simulate",
            json={"scenario": "Test scenario"},
            timeout=10
        )
        assert response.status_code == 401
        print("✅ Simulate endpoint correctly requires authentication")


class TestMessageTranslation:
    """Tests for Message Translation feature (POST /lumi/ai/translate)"""
    
    def test_translate_endpoint_exists(self, auth_headers):
        """Test that translate endpoint exists and accepts POST"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/translate",
            headers=auth_headers,
            json={"text": "Hello world", "target_language": "Spanish"},
            timeout=60
        )
        assert response.status_code == 200
        print(f"✅ Translate endpoint returned status {response.status_code}")
    
    def test_translate_returns_translated_text(self, auth_headers):
        """Test that translation returns original and translated text"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/translate",
            headers=auth_headers,
            json={"text": "Good morning, how are you?", "target_language": "Spanish"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields
        assert "original" in data, "Response missing 'original' field"
        assert "translated" in data, "Response missing 'translated' field"
        assert "target_language" in data, "Response missing 'target_language' field"
        
        # Verify original matches input
        assert data["original"] == "Good morning, how are you?"
        assert data["target_language"] == "Spanish"
        
        # Translated should be different from original (unless error)
        if "error" not in data:
            assert data["translated"] != data["original"], "Translation should differ from original"
            print(f"✅ Translation: '{data['original']}' → '{data['translated']}'")
        else:
            print(f"⚠️ Translation had error: {data.get('error')}")
    
    def test_translate_to_different_language(self, auth_headers):
        """Test translation to French"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/translate",
            headers=auth_headers,
            json={"text": "Thank you very much", "target_language": "French"},
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        assert "translated" in data
        print(f"✅ French translation: '{data.get('translated')}'")
    
    def test_translate_empty_text_rejected(self, auth_headers):
        """Test that empty text is rejected"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/translate",
            headers=auth_headers,
            json={"text": "", "target_language": "Spanish"},
            timeout=10
        )
        # Should reject empty text with 400
        assert response.status_code == 400
        print("✅ Empty text correctly rejected with 400")
    
    def test_translate_requires_auth(self):
        """Test that translate endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/translate",
            json={"text": "Hello", "target_language": "Spanish"},
            timeout=10
        )
        assert response.status_code == 401
        print("✅ Translate endpoint correctly requires authentication")


class TestSmartNotifications:
    """Tests for Smart Notifications feature (GET /lumi/ai/notifications)"""
    
    def test_notifications_endpoint_exists(self, auth_headers):
        """Test that notifications endpoint exists"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/notifications",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        print(f"✅ Notifications endpoint returned status {response.status_code}")
    
    def test_notifications_returns_structured_response(self, auth_headers):
        """Test that notifications returns expected structure"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/notifications",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields
        assert "notifications" in data, "Response missing 'notifications' field"
        assert "total" in data, "Response missing 'total' field"
        assert "unread" in data, "Response missing 'unread' field"
        assert "checked_at" in data, "Response missing 'checked_at' field"
        
        # Notifications should be a list
        assert isinstance(data["notifications"], list), "Notifications should be a list"
        
        print(f"✅ Notifications: {data['total']} total, {data['unread']} unread, {data.get('critical', 0)} critical")
    
    def test_notifications_priority_types(self, auth_headers):
        """Test that notifications have priority fields"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/notifications",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        
        # If there are notifications, check their structure
        if data["notifications"]:
            notif = data["notifications"][0]
            assert "priority" in notif, "Notification missing 'priority' field"
            assert "type" in notif, "Notification missing 'type' field"
            assert "title" in notif, "Notification missing 'title' field"
            
            # Priority should be one of expected values
            valid_priorities = ["critical", "high", "medium", "low"]
            assert notif["priority"] in valid_priorities, f"Invalid priority: {notif['priority']}"
            print(f"✅ First notification: [{notif['priority'].upper()}] {notif['type']} - {notif['title'][:50]}")
        else:
            print("✅ No notifications found (valid empty state)")
    
    def test_notifications_requires_auth(self):
        """Test that notifications endpoint requires authentication"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/notifications",
            timeout=10
        )
        assert response.status_code == 401
        print("✅ Notifications endpoint correctly requires authentication")


class TestEnhancedThreadPanel:
    """Tests for Enhanced Thread Panel features"""
    
    def test_get_channels(self, auth_headers):
        """Get list of channels to find messages"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Retrieved channels: {len(data.get('my_channels', data) if isinstance(data, dict) else data)} channels")
        return data
    
    def test_get_channel_messages(self, auth_headers):
        """Get messages from a channel"""
        # First get channels
        channels_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers,
            timeout=10
        )
        channels_data = channels_response.json()
        channels = channels_data.get('my_channels', channels_data) if isinstance(channels_data, dict) else channels_data
        
        if not channels or len(channels) == 0:
            pytest.skip("No channels available for testing")
        
        channel_id = channels[0]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        messages = response.json()
        print(f"✅ Retrieved {len(messages)} messages from channel")
        return messages, channel_id
    
    def test_thread_endpoint(self, auth_headers):
        """Test thread endpoint exists for a message"""
        # Get messages first
        channels_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers,
            timeout=10
        )
        channels_data = channels_response.json()
        channels = channels_data.get('my_channels', channels_data) if isinstance(channels_data, dict) else channels_data
        
        if not channels:
            pytest.skip("No channels available")
        
        channel_id = channels[0]["id"]
        messages_response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers,
            timeout=10
        )
        messages = messages_response.json()
        
        if not messages:
            pytest.skip("No messages available")
        
        # Get thread for first message
        msg_id = messages[0]["id"]
        thread_response = requests.get(
            f"{BASE_URL}/api/lumi/messages/{msg_id}/thread",
            headers=auth_headers,
            timeout=10
        )
        assert thread_response.status_code == 200
        thread_data = thread_response.json()
        
        # Check thread structure
        assert "parent" in thread_data, "Thread missing 'parent' field"
        assert "replies" in thread_data, "Thread missing 'replies' field"
        print(f"✅ Thread data retrieved: parent message + {len(thread_data['replies'])} replies")
    
    def test_post_thread_reply(self, auth_headers):
        """Test posting a reply to a thread"""
        # Get a message to reply to
        channels_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers,
            timeout=10
        )
        channels_data = channels_response.json()
        channels = channels_data.get('my_channels', channels_data) if isinstance(channels_data, dict) else channels_data
        
        if not channels:
            pytest.skip("No channels available")
        
        channel_id = channels[0]["id"]
        messages_response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers,
            timeout=10
        )
        messages = messages_response.json()
        
        if not messages:
            pytest.skip("No messages available")
        
        msg_id = messages[0]["id"]
        
        # Post a thread reply
        reply_response = requests.post(
            f"{BASE_URL}/api/lumi/messages/{msg_id}/thread",
            headers=auth_headers,
            json={"content": f"Test thread reply from iteration 171 - {time.time()}"},
            timeout=10
        )
        assert reply_response.status_code == 200
        print("✅ Thread reply posted successfully")


class TestExistingFeatures:
    """Tests to verify existing features still work"""
    
    def test_anomalies_endpoint(self, auth_headers):
        """Test anomalies endpoint (for Alerts panel)"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/anomalies",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        print(f"✅ Anomalies endpoint: {data.get('total', 0)} alerts, {data.get('critical', 0)} critical")
    
    def test_command_bar_search(self, auth_headers):
        """Test command bar search"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/command/search",
            headers=auth_headers,
            json={"query": "general", "mode": "search"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print(f"✅ Command bar search: {len(data['results'])} results for 'general'")
    
    def test_knowledge_graph(self, auth_headers):
        """Test knowledge graph endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/knowledge-graph",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data
        assert "edges" in data
        print(f"✅ Knowledge graph: {data['stats']['total_nodes']} nodes, {data['stats']['total_edges']} edges")
    
    def test_bottlenecks(self, auth_headers):
        """Test bottlenecks endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bottlenecks",
            headers=auth_headers,
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        assert "bottlenecks" in data
        print(f"✅ Bottlenecks: Health score {data['health_score']}, {data['total']} bottlenecks")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
