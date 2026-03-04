"""
Test LUMI ESY Color Theme + AI Features - Iteration 169
Tests:
1. ESY Color Theme integration (visual verification via frontend)
2. Conversational AI Chat (/api/lumi/ai/ask)
3. Interactive Decision Cards (/api/lumi/ai/decision-card)
4. Proactive Anomaly Alerts (/api/lumi/ai/anomalies)
5. AI Insights: Sentiment, Tasks, Reports
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestAuthentication:
    """Authentication tests for LUMI"""
    
    def test_login_success(self):
        """Test login with valid admin credentials"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        print(f"✅ Login successful - User: {data['user'].get('email')}")
        return data["access_token"]


class TestLumiConversationalAI:
    """Test Conversational AI Chat endpoint - /api/lumi/ai/ask"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_ai_ask_endpoint_exists(self, auth_token):
        """Test that /api/lumi/ai/ask endpoint exists and responds"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/ask",
            json={"question": "What tasks are overdue?"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Should return 200 with an answer (may take time due to LLM call)
        assert response.status_code == 200, f"AI ask failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "answer" in data, "No answer in response"
        print(f"✅ AI Ask endpoint working - Answer length: {len(data.get('answer', ''))}")
    
    def test_ai_ask_with_channel_context(self, auth_token):
        """Test AI ask with specific channel context"""
        # First get a channel ID
        channels_res = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if channels_res.status_code == 200:
            channels = channels_res.json().get("my_channels", [])
            if channels:
                channel_id = channels[0]["id"]
                response = requests.post(
                    f"{BASE_URL}/api/lumi/ai/ask",
                    json={
                        "question": "Summarize recent discussions",
                        "channel_id": channel_id
                    },
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                assert response.status_code == 200
                data = response.json()
                assert "answer" in data
                print(f"✅ AI Ask with channel context working")
    
    def test_ai_ask_requires_auth(self):
        """Test that AI ask requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/ask",
            json={"question": "Test question"}
        )
        assert response.status_code == 401, "AI ask should require auth"
        print("✅ AI Ask correctly requires authentication")


class TestLumiAnomalyAlerts:
    """Test Proactive Anomaly Alerts - /api/lumi/ai/anomalies"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_get_anomalies(self, auth_token):
        """Test GET /api/lumi/ai/anomalies returns alerts array"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/ai/anomalies",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Anomalies failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "alerts" in data, "No alerts key in response"
        assert isinstance(data["alerts"], list), "Alerts should be an array"
        assert "total" in data, "No total count in response"
        assert "checked_at" in data, "No checked_at timestamp"
        print(f"✅ Anomalies endpoint working - {data['total']} alerts found")
    
    def test_anomalies_requires_auth(self):
        """Test anomalies endpoint requires auth"""
        response = requests.get(f"{BASE_URL}/api/lumi/ai/anomalies")
        assert response.status_code == 401
        print("✅ Anomalies correctly requires authentication")


class TestLumiDecisionCards:
    """Test Interactive Decision Cards - /api/lumi/ai/decision-card"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_generate_decision_cards(self, auth_token):
        """Test POST /api/lumi/ai/decision-card returns cards array"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/decision-card",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Decision cards failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "cards" in data, "No cards key in response"
        assert isinstance(data["cards"], list), "Cards should be an array"
        assert "generated_at" in data, "No generated_at timestamp"
        print(f"✅ Decision Cards endpoint working - {len(data['cards'])} cards generated")
    
    def test_decision_card_action_execution(self, auth_token):
        """Test executing an action on a decision card"""
        # Generate cards first
        gen_response = requests.post(
            f"{BASE_URL}/api/lumi/ai/decision-card",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if gen_response.status_code == 200:
            cards = gen_response.json().get("cards", [])
            if cards:
                card_id = cards[0]["id"]
                # Execute an action
                action_response = requests.post(
                    f"{BASE_URL}/api/lumi/ai/decision-card/{card_id}/action",
                    json={"action_type": "resolve", "payload": "test"},
                    headers={"Authorization": f"Bearer {auth_token}"}
                )
                assert action_response.status_code == 200, f"Action execution failed: {action_response.text}"
                data = action_response.json()
                assert data.get("success") == True
                print(f"✅ Decision Card action execution working")


class TestLumiSentimentAnalysis:
    """Test AI Sentiment Analysis - /api/lumi/ai/sentiment/{channel_id}"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def channel_id(self, auth_token):
        """Get a channel ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            channels = response.json().get("my_channels", [])
            if channels:
                return channels[0]["id"]
        return None
    
    def test_sentiment_analysis(self, auth_token, channel_id):
        """Test POST /api/lumi/ai/sentiment/{channel_id} returns score and label"""
        if not channel_id:
            pytest.skip("No channel available for sentiment test")
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/sentiment/{channel_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Sentiment failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "score" in data, "No score in response"
        assert "label" in data, "No label in response"
        assert isinstance(data["score"], (int, float)), "Score should be numeric"
        print(f"✅ Sentiment Analysis working - Score: {data['score']}, Label: {data['label']}")


class TestLumiTaskExtraction:
    """Test AI Task Extraction - /api/lumi/ai/extract-tasks/{channel_id}"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def channel_id(self, auth_token):
        """Get a channel ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            channels = response.json().get("my_channels", [])
            if channels:
                return channels[0]["id"]
        return None
    
    def test_extract_tasks(self, auth_token, channel_id):
        """Test POST /api/lumi/ai/extract-tasks/{channel_id} returns tasks array"""
        if not channel_id:
            pytest.skip("No channel available for task extraction test")
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/extract-tasks/{channel_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Task extraction failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "tasks" in data, "No tasks in response"
        assert isinstance(data["tasks"], list), "Tasks should be an array"
        print(f"✅ Task Extraction working - {len(data.get('tasks', []))} tasks extracted")


class TestLumiChannelReport:
    """Test AI Channel Report - /api/lumi/ai/report/{channel_id}"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture
    def channel_id(self, auth_token):
        """Get a channel ID for testing"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            channels = response.json().get("my_channels", [])
            if channels:
                return channels[0]["id"]
        return None
    
    def test_generate_report(self, auth_token, channel_id):
        """Test POST /api/lumi/ai/report/{channel_id} returns report text"""
        if not channel_id:
            pytest.skip("No channel available for report test")
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/report/{channel_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Report generation failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "report" in data, "No report in response"
        print(f"✅ Report Generation working - Report length: {len(data.get('report', ''))}")


class TestLumiCoreEndpoints:
    """Test core LUMI endpoints still working"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for tests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_get_channels(self, auth_token):
        """Test channel listing"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "my_channels" in data
        print(f"✅ Channels endpoint working - {len(data.get('my_channels', []))} channels")
    
    def test_get_dms(self, auth_token):
        """Test DM listing"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/dm",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dms" in data
        print(f"✅ DMs endpoint working - {len(data.get('dms', []))} DMs")
    
    def test_get_presence(self, auth_token):
        """Test presence endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/presence/all",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "presence" in data
        print(f"✅ Presence endpoint working")
    
    def test_health_check(self):
        """Test health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
