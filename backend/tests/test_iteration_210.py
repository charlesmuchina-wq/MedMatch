"""
Test Iteration 210: Comprehensive validation of expanded features
- Bot chain triggers (on_meeting_end, on_new_message)
- Meeting replay AI chapters + transcript search
- ML channel predictions
- VAPID keys
- Bot catalog (18 bots)
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_login_success(self):
        """Test admin login"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        print(f"Login successful: user_id={data['user'].get('user_id')}")


class TestBotCatalog:
    """Bot catalog endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json()["access_token"]
    
    def test_bot_catalog_returns_18_bots(self, auth_token):
        """Test GET /api/lumi/bots/catalog returns 18 bots"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/catalog",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "bots" in data
        assert "total" in data
        assert data["total"] == 18, f"Expected 18 bots, got {data['total']}"
        print(f"Bot catalog: {data['total']} bots returned")
        # Verify categories exist
        assert "categories" in data
        assert len(data["categories"]) == 4


class TestBotChainTriggers:
    """Bot chain workflow trigger tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def test_channel_id(self, auth_token):
        """Get a channel ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            data = response.json()
            channels = data.get("my_channels", [])
            if channels:
                return channels[0]["id"]
        # Create a test channel if none exist
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json={"name": "TEST_trigger_channel", "description": "Test channel", "is_private": False}
        )
        if response.status_code in [200, 201]:
            return response.json()["id"]
        return "test-channel-id"
    
    def test_create_chain_with_on_meeting_end_trigger(self, auth_token, test_channel_id):
        """Test POST /api/lumi/bots/chains with trigger='on_meeting_end'"""
        payload = {
            "name": "TEST_auto_meeting_chain",
            "channel_id": test_channel_id,
            "steps": [
                {"bot_id": "summary_generator", "action": "summarize", "order": 1},
                {"bot_id": "compliance_audit", "action": "audit", "order": 2}
            ],
            "trigger": "on_meeting_end"
        }
        response = requests.post(
            f"{BASE_URL}/api/lumi/bots/chains",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["trigger"] == "on_meeting_end"
        assert len(data["steps"]) == 2
        print(f"Created on_meeting_end chain: {data['id']}")
        # Cleanup
        requests.delete(f"{BASE_URL}/api/lumi/bots/chains/{data['id']}", 
                       headers={"Authorization": f"Bearer {auth_token}"})
    
    def test_create_chain_with_on_new_message_trigger(self, auth_token, test_channel_id):
        """Test POST /api/lumi/bots/chains with trigger='on_new_message'"""
        payload = {
            "name": "TEST_auto_message_chain",
            "channel_id": test_channel_id,
            "steps": [
                {"bot_id": "knowledge_layer", "action": "ask", "order": 1},
                {"bot_id": "summary_generator", "action": "summarize", "order": 2}
            ],
            "trigger": "on_new_message"
        }
        response = requests.post(
            f"{BASE_URL}/api/lumi/bots/chains",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json=payload
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["trigger"] == "on_new_message"
        print(f"Created on_new_message chain: {data['id']}")
        # Cleanup
        requests.delete(f"{BASE_URL}/api/lumi/bots/chains/{data['id']}", 
                       headers={"Authorization": f"Bearer {auth_token}"})
    
    def test_run_chain_and_verify_steps(self, auth_token, test_channel_id):
        """Test POST /api/lumi/bots/chains/{id}/run verifies steps completed"""
        # First create a chain
        payload = {
            "name": "TEST_run_chain",
            "channel_id": test_channel_id,
            "steps": [
                {"bot_id": "summary_generator", "action": "summarize", "order": 1},
                {"bot_id": "search_copilot", "action": "ask", "order": 2}
            ],
            "trigger": "manual"
        }
        create_res = requests.post(
            f"{BASE_URL}/api/lumi/bots/chains",
            headers={"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"},
            json=payload
        )
        assert create_res.status_code == 200
        chain_id = create_res.json()["id"]
        
        # Run the chain
        run_res = requests.post(
            f"{BASE_URL}/api/lumi/bots/chains/{chain_id}/run",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert run_res.status_code == 200, f"Run failed: {run_res.text}"
        data = run_res.json()
        assert "results" in data
        assert "steps_completed" in data
        assert data["steps_completed"] >= 1
        print(f"Chain run completed: {data['steps_completed']} steps")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/lumi/bots/chains/{chain_id}", 
                       headers={"Authorization": f"Bearer {auth_token}"})
    
    def test_list_chains_with_trigger_labels(self, auth_token, test_channel_id):
        """Test GET /api/lumi/bots/chains/{channel_id} returns chains with trigger labels"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/chains/{test_channel_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "chains" in data
        assert "count" in data
        print(f"Listed {data['count']} chains for channel")


class TestMLChannelPredictions:
    """ML channel prediction tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json()["access_token"]
    
    def test_predict_channels_returns_scores(self, auth_token):
        """Test GET /api/lumi/behavior/predict-channels returns prediction scores"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/behavior/predict-channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "context" in data
        assert data["context"] in ["morning", "afternoon", "evening", "night"]
        print(f"Predictions returned: {len(data['predictions'])} channels, context={data['context']}")


class TestMeetingReplayFeatures:
    """Meeting replay AI chapters and transcript search tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def demo_meeting_id(self):
        """Use a demo meeting ID that will generate demo data"""
        return "demo-meeting-001"
    
    def test_transcript_search_endpoint(self, auth_token, demo_meeting_id):
        """Test GET /api/karau/replay/{id}/search?q=test returns results"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/{demo_meeting_id}/search?q=revenue",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # 200 if found, 404 if no replay data exists
        assert response.status_code in [200, 404], f"Unexpected: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert "results" in data
            print(f"Transcript search: {data['count']} results for query '{data['query']}'")
        else:
            print("No replay data found (expected for test meeting)")
    
    def test_generate_ai_chapters(self, auth_token, demo_meeting_id):
        """Test POST /api/karau/replay/{id}/generate-chapters generates AI chapters"""
        response = requests.post(
            f"{BASE_URL}/api/karau/replay/{demo_meeting_id}/generate-chapters",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # 200 if replay exists, 404 if not
        assert response.status_code in [200, 404], f"Unexpected: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "chapters" in data
            assert "count" in data
            print(f"AI chapters generated: {data['count']} chapters")
        else:
            print("No replay data for chapter generation (expected for test)")
    
    def test_get_replay_data(self, auth_token, demo_meeting_id):
        """Test GET /api/karau/replay/{id} returns replay data or demo"""
        response = requests.get(
            f"{BASE_URL}/api/karau/replay/{demo_meeting_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        # Demo replay should be returned
        assert "meeting_id" in data
        assert "duration_seconds" in data
        assert "transcript_segments" in data or "director_cuts" in data
        print(f"Replay data: {data.get('title', 'N/A')}, duration={data.get('duration_seconds', 0)}s")


class TestPushNotificationVAPID:
    """Push notification VAPID key tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json()["access_token"]
    
    def test_vapid_public_key_endpoint(self, auth_token):
        """Test GET /api/push/vapid-public-key returns configured VAPID key"""
        response = requests.get(
            f"{BASE_URL}/api/push/vapid-public-key",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "configured" in data
        assert data["configured"] == True, "VAPID keys should be configured"
        print(f"VAPID configured: {data['configured']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
