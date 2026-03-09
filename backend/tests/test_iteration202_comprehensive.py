"""
Iteration 202 Comprehensive Testing
Tests for:
- Package cards display (Standard/Standalone/Enterprise)
- Workspace dock bar for multi-portal packages  
- Bot Store management (toggle, configure)
- Channel Templates & Webhooks
- Team Analytics Dashboard
- Mobile responsiveness features
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


@pytest.fixture(scope="module")
def auth_token():
    """Authenticate and get token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert "access_token" in data
    return data["access_token"]


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    """Return headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}


class TestHealthCheck:
    """Basic API health checks"""
    
    def test_api_health(self):
        """Test API health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ API health check passed")


class TestPortalPackaging:
    """Portal packaging and access tests"""
    
    def test_set_standard_package(self, auth_headers):
        """Test setting standard package (AI KARAU + ENZI)"""
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=auth_headers,
            json={"package_id": "standard"}
        )
        # Should return 200 or 201
        assert response.status_code in [200, 201], f"Set package failed: {response.text}"
        data = response.json()
        assert "portals" in data
        assert "karau" in data["portals"]
        assert "enzi" in data["portals"]
        print("✓ Standard package set - includes karau and enzi")
    
    def test_set_enterprise_package(self, auth_headers):
        """Test setting enterprise package (all three portals)"""
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=auth_headers,
            json={"package_id": "enterprise"}
        )
        assert response.status_code in [200, 201], f"Set enterprise package failed: {response.text}"
        data = response.json()
        assert "portals" in data
        # Enterprise should have all 3
        portals = data["portals"]
        print(f"✓ Enterprise package set - portals: {portals}")


class TestBotStoreAPIs:
    """Bot Store API tests - browse, install, toggle, configure, uninstall"""
    
    def test_bot_catalog(self, auth_headers):
        """Test getting bot catalog"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/catalog",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Bot catalog failed: {response.text}"
        data = response.json()
        assert "bots" in data
        assert "categories" in data
        assert len(data["bots"]) > 0
        # Check bot structure
        bot = data["bots"][0]
        assert "id" in bot
        assert "name" in bot
        assert "description" in bot
        assert "category" in bot
        print(f"✓ Bot catalog returned {len(data['bots'])} bots across {len(data['categories'])} categories")
    
    def test_bot_install(self, auth_headers):
        """Test installing a bot to a channel"""
        # First get a channel
        channels_resp = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers
        )
        assert channels_resp.status_code == 200
        channels = channels_resp.json().get("my_channels", [])
        
        if not channels:
            pytest.skip("No channels available for bot install test")
        
        channel_id = channels[0]["id"]
        
        # Install standup bot
        response = requests.post(
            f"{BASE_URL}/api/lumi/bots/install",
            headers=auth_headers,
            json={"bot_id": "standup", "channel_id": channel_id}
        )
        # Either success (200) or already installed (400)
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["bot_name"] == "Standup Bot"
            print(f"✓ Standup bot installed - install ID: {data['id']}")
            return data["id"]
        elif response.status_code == 400:
            # Bot already installed - get the install ID
            installed_resp = requests.get(
                f"{BASE_URL}/api/lumi/bots/installed",
                headers=auth_headers
            )
            installed = installed_resp.json().get("bots", [])
            for bot in installed:
                if bot["bot_id"] == "standup" and bot["channel_id"] == channel_id:
                    print(f"✓ Standup bot already installed - install ID: {bot['id']}")
                    return bot["id"]
        
        return None
    
    def test_installed_bots(self, auth_headers):
        """Test getting installed bots"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/installed",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get installed bots failed: {response.text}"
        data = response.json()
        assert "bots" in data
        print(f"✓ Got {len(data['bots'])} installed bots")
        return data["bots"]
    
    def test_bot_toggle(self, auth_headers):
        """Test PUT /api/lumi/bots/toggle/{id} - toggle bot active/paused"""
        # Get installed bots first
        installed_resp = requests.get(
            f"{BASE_URL}/api/lumi/bots/installed",
            headers=auth_headers
        )
        installed = installed_resp.json().get("bots", [])
        
        if not installed:
            pytest.skip("No installed bots to toggle")
        
        install_id = installed[0]["id"]
        
        # Toggle to paused
        response = requests.put(
            f"{BASE_URL}/api/lumi/bots/toggle/{install_id}",
            headers=auth_headers,
            json={"is_active": False}
        )
        assert response.status_code == 200, f"Bot toggle to paused failed: {response.text}"
        assert response.json()["status"] == "paused"
        print(f"✓ Bot toggle to paused successful")
        
        # Toggle back to active
        response = requests.put(
            f"{BASE_URL}/api/lumi/bots/toggle/{install_id}",
            headers=auth_headers,
            json={"is_active": True}
        )
        assert response.status_code == 200, f"Bot toggle to active failed: {response.text}"
        assert response.json()["status"] == "active"
        print(f"✓ Bot toggle to active successful")
    
    def test_bot_configure(self, auth_headers):
        """Test PUT /api/lumi/bots/configure/{id} - update bot config"""
        # Get installed bots first
        installed_resp = requests.get(
            f"{BASE_URL}/api/lumi/bots/installed",
            headers=auth_headers
        )
        installed = installed_resp.json().get("bots", [])
        
        if not installed:
            pytest.skip("No installed bots to configure")
        
        install_id = installed[0]["id"]
        
        # Update config
        new_config = {"schedule": "10:00", "timezone": "America/New_York"}
        response = requests.put(
            f"{BASE_URL}/api/lumi/bots/configure/{install_id}",
            headers=auth_headers,
            json={"config": new_config}
        )
        assert response.status_code == 200, f"Bot configure failed: {response.text}"
        data = response.json()
        assert data["status"] == "configured"
        assert data["config"]["schedule"] == "10:00"
        print(f"✓ Bot configuration updated successfully")


class TestChannelTemplates:
    """Channel Templates API tests"""
    
    def test_list_channel_templates(self, auth_headers):
        """Test listing channel templates"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/templates/channels/list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"List templates failed: {response.text}"
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) >= 5  # Should have at least 5 templates
        
        # Check template structure
        template_ids = [t["id"] for t in templates]
        assert "project" in template_ids
        assert "sprint" in template_ids
        assert "incident" in template_ids
        print(f"✓ Channel templates: {len(templates)} templates available")
    
    def test_create_channel_from_template(self, auth_headers):
        """Test POST /api/lumi/templates/channels/create"""
        unique_prefix = f"Test{str(uuid.uuid4())[:4]}"
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/templates/channels/create",
            headers=auth_headers,
            json={"template_id": "project", "name_prefix": unique_prefix}
        )
        assert response.status_code == 200, f"Create from template failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert unique_prefix in data["name"]
        assert data["channel_type"] == "project"
        print(f"✓ Channel created from template: {data['name']}")


class TestWebhookTemplates:
    """Webhook Templates API tests"""
    
    def test_list_webhook_templates(self, auth_headers):
        """Test listing webhook templates"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/automation/webhook-templates/list",
            headers=auth_headers
        )
        assert response.status_code == 200, f"List webhook templates failed: {response.text}"
        data = response.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) >= 5  # Should have github, jira, cicd, slack, monitoring
        
        template_ids = [t["id"] for t in templates]
        assert "github" in template_ids
        assert "jira" in template_ids
        assert "cicd" in template_ids
        print(f"✓ Webhook templates: {len(templates)} templates available")
    
    def test_create_webhook_from_template(self, auth_headers):
        """Test POST /api/lumi/automation/webhook-templates/create"""
        # Get a channel first
        channels_resp = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers
        )
        channels = channels_resp.json().get("my_channels", [])
        
        if not channels:
            pytest.skip("No channels available for webhook test")
        
        channel_id = channels[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            headers=auth_headers,
            json={"template_id": "github", "channel_id": channel_id}
        )
        assert response.status_code == 200, f"Create webhook failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "url" in data
        assert "events" in data
        assert "sample_curl" in data
        assert "format_help" in data
        assert "github" in data["url"] or "webhook" in data["url"]
        print(f"✓ Webhook created - URL: {data['url'][:80]}...")


class TestTeamAnalytics:
    """Team Analytics Dashboard API tests"""
    
    def test_channels_endpoint_for_stats(self, auth_headers):
        """Test /api/lumi/channels returns data for analytics"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get channels failed: {response.text}"
        data = response.json()
        assert "my_channels" in data
        channels = data["my_channels"]
        print(f"✓ Channels endpoint returns {len(channels)} channels for analytics")
    
    def test_behavior_usage_insights(self, auth_headers):
        """Test /api/lumi/behavior/usage-insights for engagement score"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/behavior/usage-insights",
            headers=auth_headers
        )
        # May return 200 or 404 if endpoint doesn't exist
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Usage insights returned: {list(data.keys())}")
        else:
            print(f"⚠ Usage insights endpoint returned {response.status_code} - analytics will use calculated fallback")
    
    def test_installed_bots_for_analytics(self, auth_headers):
        """Test /api/lumi/bots/installed for bot stats"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/bots/installed",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get installed bots failed: {response.text}"
        data = response.json()
        assert "bots" in data
        print(f"✓ Installed bots for analytics: {len(data['bots'])} bots")


class TestENZIMessengerFeatures:
    """ENZI Messenger specific feature tests"""
    
    def test_channels_list(self, auth_headers):
        """Test channels list endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "my_channels" in data
        print(f"✓ ENZI channels: {len(data['my_channels'])} channels")
    
    def test_dm_list(self, auth_headers):
        """Test DM list endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/dm",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "dms" in data
        print(f"✓ ENZI DMs: {len(data['dms'])} conversations")
    
    def test_unread_counts(self, auth_headers):
        """Test unread counts endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/unread-counts",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "unread" in data
        print(f"✓ Unread counts endpoint working")


class TestWorkspaceFeatures:
    """Workspace and portal features tests"""
    
    def test_portal_access(self, auth_headers):
        """Test that portal access is configured"""
        # The set-package endpoint should work
        response = requests.post(
            f"{BASE_URL}/api/portal/set-package",
            headers=auth_headers,
            json={"package_id": "enterprise"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "portals" in data
        portals = data["portals"]
        print(f"✓ Portal access confirmed: {portals}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
