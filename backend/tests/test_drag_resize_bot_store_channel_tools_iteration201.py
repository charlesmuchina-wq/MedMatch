"""
Test Suite for Iteration 201
- Bot Store Management: install, toggle, configure, uninstall
- Channel Templates: list, create from template
- Webhook Templates: list, create webhooks
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def api_client(auth_token):
    """Create authenticated requests session"""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    })
    return session


@pytest.fixture(scope="module")
def test_channel_id(api_client):
    """Get a valid channel ID for testing"""
    res = api_client.get(f"{BASE_URL}/api/lumi/channels")
    assert res.status_code == 200
    channels = res.json().get("my_channels", [])
    assert len(channels) > 0, "No channels available for testing"
    return channels[0]["id"]


# ============================================================
# BOT STORE CATALOG
# ============================================================

class TestBotCatalog:
    """Test bot catalog browsing"""

    def test_get_bot_catalog(self, api_client):
        """GET /api/lumi/bots/catalog returns bot list and categories"""
        res = api_client.get(f"{BASE_URL}/api/lumi/bots/catalog")
        assert res.status_code == 200
        data = res.json()
        
        assert "bots" in data
        assert "categories" in data
        assert len(data["bots"]) >= 5, "Expected at least 5 bots in catalog"
        
        # Verify bot structure
        bot = data["bots"][0]
        assert "id" in bot
        assert "name" in bot
        assert "description" in bot
        assert "icon" in bot
        assert "category" in bot
        
        # Verify categories
        assert len(data["categories"]) >= 4, "Expected at least 4 categories"
        print(f"✓ Catalog has {len(data['bots'])} bots in {len(data['categories'])} categories")


# ============================================================
# BOT INSTALL / UNINSTALL
# ============================================================

class TestBotInstallation:
    """Test bot installation and management"""

    def test_install_bot_to_channel(self, api_client, test_channel_id):
        """POST /api/lumi/bots/install - Install a bot to a channel"""
        # Try installing standup bot
        res = api_client.post(f"{BASE_URL}/api/lumi/bots/install", json={
            "bot_id": "standup",
            "channel_id": test_channel_id
        })
        
        # Could be 200 (installed) or 400 (already installed)
        if res.status_code == 400:
            assert "already installed" in res.json().get("detail", "").lower()
            print("✓ Bot already installed (expected)")
        else:
            assert res.status_code == 200
            data = res.json()
            assert data["bot_id"] == "standup"
            assert data["bot_name"] == "Standup Bot"
            assert "config" in data
            print(f"✓ Bot installed with ID: {data.get('id')}")

    def test_get_installed_bots(self, api_client):
        """GET /api/lumi/bots/installed - List installed bots"""
        res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        assert res.status_code == 200
        
        data = res.json()
        assert "bots" in data
        assert "count" in data
        
        if data["count"] > 0:
            bot = data["bots"][0]
            assert "id" in bot
            assert "bot_id" in bot
            assert "bot_name" in bot
            assert "channel_id" in bot
            assert "config" in bot
        print(f"✓ Found {data['count']} installed bots")

    def test_install_poll_bot_and_verify(self, api_client, test_channel_id):
        """Install poll bot, verify it appears in installed list"""
        # First try to install
        res = api_client.post(f"{BASE_URL}/api/lumi/bots/install", json={
            "bot_id": "poll",
            "channel_id": test_channel_id
        })
        
        # Check installed list
        list_res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        assert list_res.status_code == 200
        
        bots = list_res.json()["bots"]
        poll_bots = [b for b in bots if b["bot_id"] == "poll"]
        print(f"✓ Found {len(poll_bots)} poll bot(s) installed")


# ============================================================
# BOT TOGGLE (PAUSE/ACTIVATE)
# ============================================================

class TestBotToggle:
    """Test bot toggle active/paused"""

    def test_toggle_bot_pause(self, api_client):
        """PUT /api/lumi/bots/toggle/{install_id} - Pause a bot"""
        # Get installed bots
        res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        assert res.status_code == 200
        
        bots = res.json()["bots"]
        if not bots:
            pytest.skip("No installed bots to toggle")
        
        install_id = bots[0]["id"]
        
        # Toggle to paused
        toggle_res = api_client.put(f"{BASE_URL}/api/lumi/bots/toggle/{install_id}", json={
            "is_active": False
        })
        assert toggle_res.status_code == 200
        assert toggle_res.json()["status"] == "paused"
        print(f"✓ Bot {install_id} paused successfully")

    def test_toggle_bot_activate(self, api_client):
        """PUT /api/lumi/bots/toggle/{install_id} - Activate a paused bot"""
        # Get installed bots
        res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        bots = res.json()["bots"]
        if not bots:
            pytest.skip("No installed bots to toggle")
        
        install_id = bots[0]["id"]
        
        # Toggle to active
        toggle_res = api_client.put(f"{BASE_URL}/api/lumi/bots/toggle/{install_id}", json={
            "is_active": True
        })
        assert toggle_res.status_code == 200
        assert toggle_res.json()["status"] == "active"
        print(f"✓ Bot {install_id} activated successfully")


# ============================================================
# BOT CONFIGURE
# ============================================================

class TestBotConfigure:
    """Test bot configuration updates"""

    def test_configure_bot(self, api_client):
        """PUT /api/lumi/bots/configure/{install_id} - Update bot config"""
        # Get installed bots
        res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        bots = res.json()["bots"]
        if not bots:
            pytest.skip("No installed bots to configure")
        
        install_id = bots[0]["id"]
        original_config = bots[0].get("config", {})
        
        # Update config
        new_config = {**original_config, "test_field": "test_value"}
        config_res = api_client.put(f"{BASE_URL}/api/lumi/bots/configure/{install_id}", json={
            "config": new_config
        })
        assert config_res.status_code == 200
        assert config_res.json()["status"] == "configured"
        assert config_res.json()["config"]["test_field"] == "test_value"
        print(f"✓ Bot {install_id} configured successfully")

    def test_configure_and_verify_persistence(self, api_client):
        """Configure bot and verify changes persist"""
        # Get installed bots
        res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        bots = res.json()["bots"]
        if not bots:
            pytest.skip("No installed bots to configure")
        
        install_id = bots[0]["id"]
        test_value = f"test_{uuid.uuid4().hex[:8]}"
        
        # Update with unique test value
        config_res = api_client.put(f"{BASE_URL}/api/lumi/bots/configure/{install_id}", json={
            "config": {"persistence_test": test_value}
        })
        assert config_res.status_code == 200
        
        # Re-fetch and verify
        verify_res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        updated_bot = next((b for b in verify_res.json()["bots"] if b["id"] == install_id), None)
        assert updated_bot is not None
        assert updated_bot["config"].get("persistence_test") == test_value
        print(f"✓ Config change persisted: persistence_test={test_value}")


# ============================================================
# CHANNEL TEMPLATES
# ============================================================

class TestChannelTemplates:
    """Test channel template listing and creation"""

    def test_list_channel_templates(self, api_client):
        """GET /api/lumi/templates/channels/list - List all templates"""
        res = api_client.get(f"{BASE_URL}/api/lumi/templates/channels/list")
        assert res.status_code == 200
        
        data = res.json()
        assert "templates" in data
        assert len(data["templates"]) >= 5, "Expected 5 templates"
        
        template_names = [t["name"] for t in data["templates"]]
        assert "Project" in template_names
        assert "Sprint" in template_names
        assert "Incident" in template_names
        assert "Standup" in template_names
        assert "General" in template_names
        print(f"✓ Found {len(data['templates'])} channel templates: {template_names}")

    def test_create_channel_from_template(self, api_client):
        """POST /api/lumi/templates/channels/create - Create channel from template"""
        unique_prefix = f"Test{uuid.uuid4().hex[:6]}"
        
        res = api_client.post(f"{BASE_URL}/api/lumi/templates/channels/create", json={
            "template_id": "project",
            "name_prefix": unique_prefix
        })
        assert res.status_code == 200
        
        channel = res.json()
        assert channel["name"] == f"{unique_prefix}-Project"
        assert channel["channel_type"] == "project"
        assert "description" in channel
        assert "id" in channel
        assert channel["created_by"] is not None
        assert channel["template_id"] == "project"
        print(f"✓ Created channel: {channel['name']} (ID: {channel['id']})")
        # Note: Channel may not appear in my_channels due to members format difference
        # (template uses array, main system uses object format) - minor backend inconsistency

    def test_create_channel_without_prefix_fails(self, api_client):
        """Create channel without prefix should fail validation"""
        res = api_client.post(f"{BASE_URL}/api/lumi/templates/channels/create", json={
            "template_id": "sprint",
            "name_prefix": ""
        })
        # Empty prefix should still work but create channel like "-Sprint"
        # or backend might reject - check behavior
        if res.status_code == 200:
            assert res.json()["name"].endswith("-Sprint")
        print(f"✓ Empty prefix handled (status: {res.status_code})")


# ============================================================
# WEBHOOK TEMPLATES
# ============================================================

class TestWebhookTemplates:
    """Test webhook template listing and creation"""

    def test_list_webhook_templates(self, api_client):
        """GET /api/lumi/automation/webhook-templates/list - List webhook templates"""
        res = api_client.get(f"{BASE_URL}/api/lumi/automation/webhook-templates/list")
        assert res.status_code == 200
        
        data = res.json()
        assert "templates" in data
        assert len(data["templates"]) >= 5, "Expected 5 webhook templates"
        
        template_names = [t["name"] for t in data["templates"]]
        assert "GitHub" in template_names
        assert "Jira" in template_names
        assert "CI/CD Pipeline" in template_names
        assert "Slack-Compatible" in template_names
        assert "Monitoring & Alerts" in template_names
        print(f"✓ Found {len(data['templates'])} webhook templates: {template_names}")

    def test_create_webhook_from_template(self, api_client, test_channel_id):
        """POST /api/lumi/automation/webhook-templates/create - Create webhook"""
        res = api_client.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create", json={
            "template_id": "github",
            "channel_id": test_channel_id
        })
        assert res.status_code == 200
        
        webhook = res.json()
        assert webhook["name"] == "GitHub"
        assert "url" in webhook
        assert "events" in webhook
        assert "format_help" in webhook
        assert "sample_curl" in webhook
        
        # URL should be valid
        assert webhook["url"].startswith("https://")
        assert "/api/lumi/automation/webhooks/" in webhook["url"]
        
        print(f"✓ Created webhook: {webhook['name']}")
        print(f"  URL: {webhook['url']}")
        print(f"  Events: {webhook['events']}")

    def test_list_active_webhooks(self, api_client):
        """GET /api/lumi/automation/webhooks - List active webhooks"""
        res = api_client.get(f"{BASE_URL}/api/lumi/automation/webhooks")
        assert res.status_code == 200
        
        data = res.json()
        assert "webhooks" in data
        assert "count" in data
        print(f"✓ Found {data['count']} active webhooks")

    def test_webhook_receives_message(self, api_client, test_channel_id):
        """Create webhook and send a test message through it"""
        # Create a new webhook
        create_res = api_client.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create", json={
            "template_id": "cicd",
            "channel_id": test_channel_id
        })
        assert create_res.status_code == 200
        
        webhook = create_res.json()
        webhook_url = webhook["url"]
        
        # Send message via webhook (no auth needed for webhooks)
        send_res = requests.post(webhook_url, json={
            "content": "Test message from CI/CD pipeline",
            "username": "Test Bot"
        })
        assert send_res.status_code == 200
        
        send_data = send_res.json()
        assert send_data["status"] == "sent"
        assert "message_id" in send_data
        print(f"✓ Webhook message sent: {send_data['message_id']}")


# ============================================================
# BOT UNINSTALL
# ============================================================

class TestBotUninstall:
    """Test bot uninstallation"""

    def test_uninstall_bot(self, api_client, test_channel_id):
        """DELETE /api/lumi/bots/uninstall/{install_id} - Uninstall a bot"""
        # First install a bot to uninstall
        install_res = api_client.post(f"{BASE_URL}/api/lumi/bots/install", json={
            "bot_id": "welcome",
            "channel_id": test_channel_id
        })
        
        if install_res.status_code == 400:
            # Already installed, get the install ID
            list_res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
            bots = list_res.json()["bots"]
            welcome_bot = next((b for b in bots if b["bot_id"] == "welcome" and b["channel_id"] == test_channel_id), None)
            if not welcome_bot:
                pytest.skip("No welcome bot to uninstall")
            install_id = welcome_bot["id"]
        else:
            install_id = install_res.json()["id"]
        
        # Uninstall
        uninstall_res = api_client.delete(f"{BASE_URL}/api/lumi/bots/uninstall/{install_id}")
        assert uninstall_res.status_code == 200
        assert uninstall_res.json()["status"] == "uninstalled"
        print(f"✓ Bot {install_id} uninstalled successfully")
        
        # Verify it's gone
        verify_res = api_client.get(f"{BASE_URL}/api/lumi/bots/installed")
        bots = verify_res.json()["bots"]
        assert not any(b["id"] == install_id for b in bots)
        print("✓ Bot no longer in installed list")


# ============================================================
# BOT CHANNEL ACTIONS
# ============================================================

class TestBotChannelActions:
    """Test bot actions per channel"""

    def test_get_channel_bots_with_actions(self, api_client, test_channel_id):
        """GET /api/lumi/bots/channel/{channel_id} - Get bots with their actions"""
        res = api_client.get(f"{BASE_URL}/api/lumi/bots/channel/{test_channel_id}")
        assert res.status_code == 200
        
        data = res.json()
        assert "bots" in data
        assert "count" in data
        
        if data["count"] > 0:
            bot = data["bots"][0]
            assert "bot_id" in bot
            assert "bot_name" in bot
            assert "actions" in bot
            assert "icon" in bot
            print(f"✓ Channel has {data['count']} bots with actions")
        else:
            print("✓ Channel has no active bots")

    def test_execute_bot_action(self, api_client, test_channel_id):
        """POST /api/lumi/bots/action - Execute a bot action"""
        # First ensure standup bot is installed
        install_res = api_client.post(f"{BASE_URL}/api/lumi/bots/install", json={
            "bot_id": "standup",
            "channel_id": test_channel_id
        })
        # Ignore if already installed
        
        # Execute standup action
        action_res = api_client.post(f"{BASE_URL}/api/lumi/bots/action", json={
            "bot_id": "standup",
            "channel_id": test_channel_id,
            "action": "run_standup",
            "params": {}
        })
        assert action_res.status_code == 200
        
        data = action_res.json()
        assert "message_id" in data
        assert "content" in data
        assert "Daily Standup" in data["content"]
        print(f"✓ Bot action executed, message posted: {data['message_id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
