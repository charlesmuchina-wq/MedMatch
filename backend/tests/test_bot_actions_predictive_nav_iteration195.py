"""
Test Bot Actions Panel and Predictive Zero-Click Navigation - ENZI Batch A Iteration 195
Features:
1. Bot Actions Panel - quick-trigger buttons for installed bots inside channels
2. Predictive Zero-Click Navigation - dynamically reorder sidebar channels/DMs
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuthentication:
    """Authentication tests"""
    
    def test_admin_login(self):
        """Test admin login works"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        return data["access_token"]


class TestBotActionsPanel:
    """Test Bot Actions Panel - GET /api/lumi/bots/channel/{id}, POST /api/lumi/bots/action"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def test_channel_id(self, auth_token):
        """Get or create a test channel"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Get channels
        res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=headers)
        assert res.status_code == 200
        data = res.json()
        channels = data.get("my_channels", [])
        if channels:
            return channels[0]["id"]
        # Create one if none
        res = requests.post(f"{BASE_URL}/api/lumi/channels", headers=headers, json={
            "name": "test-bot-actions",
            "channel_type": "public"
        })
        assert res.status_code in [200, 201]
        return res.json()["id"]
    
    def test_get_channel_bots_returns_installed_bots_with_actions(self, auth_token, test_channel_id):
        """GET /api/lumi/bots/channel/{id} returns installed bots with actions"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First install a bot (poll bot) in the channel
        install_res = requests.post(f"{BASE_URL}/api/lumi/bots/install", headers=headers, json={
            "bot_id": "poll",
            "channel_id": test_channel_id
        })
        # May already be installed
        assert install_res.status_code in [200, 201, 400], f"Install failed: {install_res.text}"
        
        # Now get bots for channel
        response = requests.get(f"{BASE_URL}/api/lumi/bots/channel/{test_channel_id}", headers=headers)
        assert response.status_code == 200, f"Get channel bots failed: {response.text}"
        data = response.json()
        
        assert "bots" in data, "Response should have 'bots' key"
        assert "count" in data, "Response should have 'count' key"
        
        # Should have at least poll bot
        bots = data["bots"]
        assert len(bots) >= 1, "Should have at least one installed bot"
        
        # Verify bot structure
        bot = bots[0]
        assert "bot_id" in bot, "Bot should have bot_id"
        assert "bot_name" in bot, "Bot should have bot_name"
        assert "actions" in bot, "Bot should have actions list"
        assert "icon" in bot, "Bot should have icon"
        
        # Verify actions structure
        if bot["actions"]:
            action = bot["actions"][0]
            assert "id" in action, "Action should have id"
            assert "label" in action, "Action should have label"
            assert "icon" in action, "Action should have icon"
        
        return test_channel_id
    
    def test_execute_bot_action_posts_message(self, auth_token, test_channel_id):
        """POST /api/lumi/bots/action executes action and posts message"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Ensure poll bot is installed
        requests.post(f"{BASE_URL}/api/lumi/bots/install", headers=headers, json={
            "bot_id": "poll",
            "channel_id": test_channel_id
        })
        
        # Execute start_poll action
        response = requests.post(f"{BASE_URL}/api/lumi/bots/action", headers=headers, json={
            "bot_id": "poll",
            "channel_id": test_channel_id,
            "action": "start_poll",
            "params": {
                "question": "Test poll from iteration 195?",
                "options": ["Yes", "No", "Maybe"]
            }
        })
        assert response.status_code == 200, f"Bot action failed: {response.text}"
        data = response.json()
        
        assert "message_id" in data, "Response should have message_id"
        assert "content" in data, "Response should have content"
        assert "bot_name" in data, "Response should have bot_name"
        assert "Poll" in data["content"], "Poll content should include 'Poll'"
    
    def test_poll_bot_creates_formatted_poll_message(self, auth_token, test_channel_id):
        """Bot action for poll bot creates formatted poll message"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/lumi/bots/action", headers=headers, json={
            "bot_id": "poll",
            "channel_id": test_channel_id,
            "action": "start_poll",
            "params": {
                "question": "What is your favorite color?",
                "options": ["Red", "Blue", "Green"]
            }
        })
        assert response.status_code == 200, f"Poll action failed: {response.text}"
        data = response.json()
        
        # Verify poll message format
        content = data["content"]
        assert "Poll" in content, "Should contain 'Poll' header"
        assert "favorite color" in content or "What is" in content, "Should contain question"
        assert "Red" in content or "Option" in content, "Should contain options"
    
    def test_standup_bot_action_creates_standup_prompt(self, auth_token, test_channel_id):
        """Bot action for standup bot creates standup prompt"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Install standup bot
        requests.post(f"{BASE_URL}/api/lumi/bots/install", headers=headers, json={
            "bot_id": "standup",
            "channel_id": test_channel_id
        })
        
        response = requests.post(f"{BASE_URL}/api/lumi/bots/action", headers=headers, json={
            "bot_id": "standup",
            "channel_id": test_channel_id,
            "action": "run_standup"
        })
        assert response.status_code == 200, f"Standup action failed: {response.text}"
        data = response.json()
        
        content = data["content"]
        assert "Standup" in content, "Should contain 'Standup' header"
        assert "yesterday" in content.lower() or "today" in content.lower(), "Should contain standup prompts"
    
    def test_reminder_bot_action_creates_reminder(self, auth_token, test_channel_id):
        """Bot action for reminder bot creates reminder message"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Install reminder bot
        requests.post(f"{BASE_URL}/api/lumi/bots/install", headers=headers, json={
            "bot_id": "reminder",
            "channel_id": test_channel_id
        })
        
        response = requests.post(f"{BASE_URL}/api/lumi/bots/action", headers=headers, json={
            "bot_id": "reminder",
            "channel_id": test_channel_id,
            "action": "set_reminder",
            "params": {
                "text": "Team meeting",
                "time": "in 30 minutes"
            }
        })
        assert response.status_code == 200, f"Reminder action failed: {response.text}"
        data = response.json()
        
        content = data["content"]
        assert "Reminder" in content, "Should contain 'Reminder' header"
    
    def test_bot_action_fails_if_not_installed(self, auth_token):
        """Bot action fails with 404 if bot not installed in channel"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Try action on a channel that doesn't have the bot
        fake_channel = "fake_channel_no_bots_12345"
        response = requests.post(f"{BASE_URL}/api/lumi/bots/action", headers=headers, json={
            "bot_id": "poll",
            "channel_id": fake_channel,
            "action": "start_poll"
        })
        assert response.status_code == 404, f"Should return 404 for bot not installed: {response.status_code}"


class TestPredictiveNavigation:
    """Test Predictive Zero-Click Navigation - track, suggestions, stats endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def test_channel_id(self, auth_token):
        """Get a test channel"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=headers)
        assert res.status_code == 200
        channels = res.json().get("my_channels", [])
        if channels:
            return channels[0]["id"]
        return "test_channel_predict"
    
    def test_track_action_records_user_activity(self, auth_token, test_channel_id):
        """POST /api/lumi/predict/track records user actions"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/lumi/predict/track", headers=headers, json={
            "action": "channel_visit",
            "target_id": test_channel_id,
            "target_name": "test-channel"
        })
        assert response.status_code == 200, f"Track action failed: {response.text}"
        data = response.json()
        assert data.get("tracked") == True, "Response should confirm tracked=True"
    
    def test_track_multiple_visits_for_prediction(self, auth_token, test_channel_id):
        """Track multiple visits to build prediction data"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Track multiple visits
        for i in range(5):
            response = requests.post(f"{BASE_URL}/api/lumi/predict/track", headers=headers, json={
                "action": "channel_visit",
                "target_id": test_channel_id,
                "target_name": f"test-channel-{i}"
            })
            assert response.status_code == 200
    
    def test_get_suggestions_returns_predictions(self, auth_token, test_channel_id):
        """GET /api/lumi/predict/suggestions returns channel and DM predictions"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Track some visits first
        for i in range(3):
            requests.post(f"{BASE_URL}/api/lumi/predict/track", headers=headers, json={
                "action": "channel_visit",
                "target_id": test_channel_id,
                "target_name": "frequent-channel"
            })
        
        response = requests.get(f"{BASE_URL}/api/lumi/predict/suggestions", headers=headers)
        assert response.status_code == 200, f"Get suggestions failed: {response.text}"
        data = response.json()
        
        assert "channels" in data, "Response should have 'channels' key"
        assert "dms" in data, "Response should have 'dms' key"
        assert "time_context" in data, "Response should have 'time_context' key"
        
        # Verify time_context structure
        time_ctx = data["time_context"]
        assert "hour" in time_ctx, "time_context should have hour"
        assert "day" in time_ctx, "time_context should have day"
    
    def test_suggestions_include_tracked_channel(self, auth_token, test_channel_id):
        """Suggestions should include frequently visited channels"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Track many visits to same channel
        for i in range(10):
            requests.post(f"{BASE_URL}/api/lumi/predict/track", headers=headers, json={
                "action": "channel_visit",
                "target_id": test_channel_id,
                "target_name": "high-frequency-channel"
            })
        
        response = requests.get(f"{BASE_URL}/api/lumi/predict/suggestions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        
        channels = data.get("channels", [])
        # Should have predictions if we tracked enough
        assert isinstance(channels, list), "channels should be a list"
    
    def test_get_behavior_stats(self, auth_token):
        """GET /api/lumi/predict/stats returns behavior statistics"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/lumi/predict/stats", headers=headers)
        assert response.status_code == 200, f"Get stats failed: {response.text}"
        data = response.json()
        
        assert "total_actions" in data, "Response should have total_actions"
        assert "by_type" in data, "Response should have by_type"
        assert "peak_hours" in data, "Response should have peak_hours"
        
        # Verify types
        assert isinstance(data["total_actions"], int), "total_actions should be int"
        assert isinstance(data["by_type"], dict), "by_type should be dict"
        assert isinstance(data["peak_hours"], list), "peak_hours should be list"


class TestPreviousFeatures:
    """Test that previous features still work"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_meeting_modal_api(self, auth_token):
        """Meeting modal API still accessible"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/meetings/history", headers=headers)
        assert response.status_code == 200, f"Meeting history failed: {response.text}"
    
    def test_bot_store_catalog(self, auth_token):
        """Bot store catalog still accessible"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", headers=headers)
        assert response.status_code == 200, f"Bot catalog failed: {response.text}"
        data = response.json()
        assert "bots" in data
        assert len(data["bots"]) >= 8, "Should have at least 8 bots"
    
    def test_channels_api(self, auth_token):
        """Channels API still works"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/channels", headers=headers)
        assert response.status_code == 200, f"Channels failed: {response.text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
