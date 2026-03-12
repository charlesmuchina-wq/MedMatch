"""
Test Suite for Phases 2-4:
- Push Notifications (VAPID keys)
- Bot-to-Bot Chaining
- Recording Stats
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"

@pytest.fixture(scope="session")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="session")
def auth_token(api_client):
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL, "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("access_token")  # API returns access_token not token
    pytest.skip(f"Auth failed: {response.status_code}")

@pytest.fixture(scope="session")
def authenticated_client(api_client, auth_token):
    api_client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return api_client

@pytest.fixture(scope="session")
def admin_channel_id(authenticated_client):
    response = authenticated_client.get(f"{BASE_URL}/api/lumi/channels")
    if response.status_code == 200:
        channels = response.json().get("my_channels", [])  # API returns my_channels
        if channels:
            return channels[0]["id"]
    pytest.skip("No channels available")

# ============== Push Notifications ==============
class TestPushNotifications:
    def test_vapid_public_key_configured(self, api_client):
        """GET /api/push/vapid-public-key returns configured=true"""
        response = api_client.get(f"{BASE_URL}/api/push/vapid-public-key")
        assert response.status_code == 200
        data = response.json()
        assert data.get("configured") == True
        assert len(data.get("publicKey", "")) > 10

    def test_push_subscribe(self, authenticated_client):
        """POST /api/push/subscribe accepts subscription"""
        subscription = {
            "endpoint": f"https://fcm.googleapis.com/fcm/send/{uuid.uuid4().hex}",
            "keys": {"p256dh": "BNcRdreALRFXTkOOUHK1EtK2wtaz5Ry4YfYCA_0QTp", "auth": "tBHItJI5svbp"}
        }
        response = authenticated_client.post(f"{BASE_URL}/api/push/subscribe", json=subscription)
        assert response.status_code == 200
        assert "subscription_id" in response.json()

# ============== Recording Stats ==============
class TestRecordingStats:
    def test_recording_stats(self, authenticated_client):
        """GET /api/karau-meet/recordings/stats returns stats"""
        response = authenticated_client.get(f"{BASE_URL}/api/karau-meet/recordings/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_recordings" in data
        assert isinstance(data["total_recordings"], int)

# ============== Bot-to-Bot Chaining ==============
class TestBotChains:
    def test_create_bot_chain(self, authenticated_client, admin_channel_id):
        """POST /api/lumi/bots/chains creates chain"""
        chain = {
            "name": f"TEST_wf_{uuid.uuid4().hex[:6]}",
            "channel_id": admin_channel_id,
            "steps": [
                {"bot_id": "summary_generator", "action": "summarize", "order": 1},
                {"bot_id": "talent_matcher", "action": "match", "order": 2}
            ]
        }
        response = authenticated_client.post(f"{BASE_URL}/api/lumi/bots/chains", json=chain)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert len(data["steps"]) == 2
        TestBotChains.chain_id = data["id"]

    def test_list_chains(self, authenticated_client, admin_channel_id):
        """GET /api/lumi/bots/chains/{channel_id} lists chains"""
        response = authenticated_client.get(f"{BASE_URL}/api/lumi/bots/chains/{admin_channel_id}")
        assert response.status_code == 200
        assert "chains" in response.json()

    def test_run_chain(self, authenticated_client, admin_channel_id):
        """POST /api/lumi/bots/chains/{chain_id}/run executes chain"""
        # Create chain
        chain = {
            "name": f"TEST_run_{uuid.uuid4().hex[:6]}",
            "channel_id": admin_channel_id,
            "steps": [
                {"bot_id": "summary_generator", "action": "summarize", "order": 1},
                {"bot_id": "note_taker", "action": "notes", "order": 2}
            ]
        }
        create = authenticated_client.post(f"{BASE_URL}/api/lumi/bots/chains", json=chain)
        chain_id = create.json()["id"]
        # Run - AI takes time
        response = authenticated_client.post(f"{BASE_URL}/api/lumi/bots/chains/{chain_id}/run", timeout=90)
        assert response.status_code == 200
        data = response.json()
        assert data["steps_completed"] >= 1
        authenticated_client.delete(f"{BASE_URL}/api/lumi/bots/chains/{chain_id}")

    def test_delete_chain(self, authenticated_client, admin_channel_id):
        """DELETE /api/lumi/bots/chains/{chain_id} deletes chain"""
        chain = {
            "name": f"TEST_del_{uuid.uuid4().hex[:6]}",
            "channel_id": admin_channel_id,
            "steps": [
                {"bot_id": "summary_generator", "action": "summarize", "order": 1},
                {"bot_id": "talent_matcher", "action": "match", "order": 2}
            ]
        }
        create = authenticated_client.post(f"{BASE_URL}/api/lumi/bots/chains", json=chain)
        chain_id = create.json()["id"]
        response = authenticated_client.delete(f"{BASE_URL}/api/lumi/bots/chains/{chain_id}")
        assert response.status_code == 200
        assert response.json().get("status") == "deleted"

    def test_chain_requires_two_steps(self, authenticated_client, admin_channel_id):
        """Chain needs at least 2 steps"""
        chain = {
            "name": "TEST_single",
            "channel_id": admin_channel_id,
            "steps": [{"bot_id": "summary_generator", "action": "summarize", "order": 1}]
        }
        response = authenticated_client.post(f"{BASE_URL}/api/lumi/bots/chains", json=chain)
        assert response.status_code == 400
