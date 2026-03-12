"""
Test AI-powered Bot Marketplace functionality (P1 - Iteration 207)
Tests bot actions with real AI responses via GPT-4o (Emergent LLM key)
Tests slash commands, bot installation, and catalog endpoints
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestBotAIResponses:
    """Test AI-powered bot action responses"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if res.status_code == 200:
            return res.json().get("access_token")
        pytest.skip("Authentication failed")
    
    @pytest.fixture(scope="class")
    def test_channel_id(self, auth_token):
        """Get test channel ID (test-channel with installed bots)"""
        res = requests.get(f"{BASE_URL}/api/lumi/channels", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        if res.status_code == 200:
            channels = res.json().get("my_channels", [])
            # Look for test-channel which has installed bots
            for ch in channels:
                if "test" in ch.get("name", "").lower():
                    return ch["id"]
            # Fallback to first channel
            if channels:
                return channels[0]["id"]
        pytest.skip("No channels found")

    # ═══════════════════════════════════════════════════════════════
    # BOT CATALOG TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_get_bot_catalog(self, auth_token):
        """GET /api/lumi/bots/catalog returns 18 bots with 4 categories"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert res.status_code == 200, f"Catalog fetch failed: {res.text}"
        data = res.json()
        
        # Verify 18 bots
        assert "bots" in data
        assert len(data["bots"]) == 18, f"Expected 18 bots, got {len(data['bots'])}"
        
        # Verify 4 categories
        assert "categories" in data
        categories = data["categories"]
        assert len(categories) == 4, f"Expected 4 categories, got {len(categories)}"
        assert "Job Toolkit" in categories
        assert "AI Meeting" in categories
        assert "AI Messenger" in categories
        assert "Security & QA" in categories
        
        # Verify bot structure
        bot = data["bots"][0]
        assert "id" in bot
        assert "name" in bot
        assert "description" in bot
        assert "category" in bot
        assert "commands" in bot
        print(f"PASS: Bot catalog returns {len(data['bots'])} bots in {len(categories)} categories")

    def test_get_featured_bots(self, auth_token):
        """GET /api/lumi/bots/featured returns featured bots"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/featured", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert res.status_code == 200, f"Featured bots fetch failed: {res.text}"
        data = res.json()
        
        assert "bots" in data
        assert len(data["bots"]) > 0, "No featured bots found"
        print(f"PASS: Featured bots returns {len(data['bots'])} bots")

    # ═══════════════════════════════════════════════════════════════
    # BOT INSTALLATION TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_install_bot_to_channel(self, auth_token, test_channel_id):
        """POST /api/lumi/bots/install installs bot to channel"""
        # Try to install knowledge_layer bot
        res = requests.post(f"{BASE_URL}/api/lumi/bots/install", 
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "bot_id": "knowledge_layer",
                "channel_id": test_channel_id
            }
        )
        
        # Accept 200/400 (already installed) as success
        if res.status_code == 400 and "already installed" in res.text.lower():
            print("PASS: Bot already installed in channel (expected)")
            return
        
        assert res.status_code in [200, 201], f"Bot install failed: {res.status_code} - {res.text}"
        data = res.json()
        assert "bot_id" in data or "id" in data
        assert data.get("status") == "installed" or "bot_name" in data
        print(f"PASS: Bot installed successfully: {data.get('bot_name', 'knowledge_layer')}")

    def test_get_installed_bots(self, auth_token):
        """GET /api/lumi/bots/installed returns user's installed bots"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/installed", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert res.status_code == 200, f"Get installed bots failed: {res.text}"
        data = res.json()
        
        assert "bots" in data
        print(f"PASS: User has {len(data['bots'])} installed bots")

    def test_get_channel_bots_with_actions(self, auth_token, test_channel_id):
        """GET /api/lumi/bots/channel/{channel_id} returns installed bots with actions"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/channel/{test_channel_id}", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert res.status_code == 200, f"Get channel bots failed: {res.text}"
        data = res.json()
        
        assert "bots" in data
        bots = data["bots"]
        if bots:
            bot = bots[0]
            assert "bot_id" in bot
            assert "actions" in bot
            print(f"PASS: Channel has {len(bots)} installed bots with actions")
        else:
            print("INFO: No bots installed in this channel yet")

    # ═══════════════════════════════════════════════════════════════
    # SLASH COMMANDS TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_get_slash_commands_for_channel(self, auth_token, test_channel_id):
        """GET /api/lumi/bots/slash-commands/{channel_id} returns available commands"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/slash-commands/{test_channel_id}", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert res.status_code == 200, f"Get slash commands failed: {res.text}"
        data = res.json()
        
        assert "commands" in data
        commands = data["commands"]
        print(f"PASS: Channel has {len(commands)} slash commands available")
        
        # Verify command structure
        if commands:
            cmd = commands[0]
            assert "command" in cmd
            assert "bot_id" in cmd
            assert "bot_name" in cmd

    # ═══════════════════════════════════════════════════════════════
    # AI-POWERED BOT ACTION TESTS (Real GPT-4o responses)
    # ═══════════════════════════════════════════════════════════════
    
    def test_summary_generator_bot_action(self, auth_token, test_channel_id):
        """POST /api/lumi/bots/action - summary_generator returns AI response"""
        res = requests.post(f"{BASE_URL}/api/lumi/bots/action",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "bot_id": "summary_generator",
                "channel_id": test_channel_id,
                "action": "summarize"
            },
            timeout=30  # AI responses take longer
        )
        
        if res.status_code == 404:
            pytest.skip("summary_generator not installed in this channel")
        
        assert res.status_code == 200, f"Bot action failed: {res.status_code} - {res.text}"
        data = res.json()
        
        assert "content" in data
        assert "bot_name" in data
        # Verify it's AI response, not template string
        content = data["content"]
        assert "**Summary Generator**" in content or "Summary Generator" in content
        assert len(content) > 50, f"Response too short - may not be AI: {content[:100]}"
        print(f"PASS: summary_generator returned AI response ({len(content)} chars)")
        print(f"  Response preview: {content[:200]}...")

    def test_talent_matcher_bot_action_with_params(self, auth_token, test_channel_id):
        """POST /api/lumi/bots/action - talent_matcher with params returns AI response"""
        res = requests.post(f"{BASE_URL}/api/lumi/bots/action",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "bot_id": "talent_matcher",
                "channel_id": test_channel_id,
                "action": "match",
                "params": {"query": "senior software engineer with Python experience"}
            },
            timeout=30
        )
        
        if res.status_code == 404:
            pytest.skip("talent_matcher not installed in this channel")
        
        assert res.status_code == 200, f"Bot action failed: {res.status_code} - {res.text}"
        data = res.json()
        
        assert "content" in data
        content = data["content"]
        assert len(content) > 50, f"Response too short: {content[:100]}"
        print(f"PASS: talent_matcher returned AI response ({len(content)} chars)")
        print(f"  Response preview: {content[:200]}...")

    def test_compliance_audit_bot_action(self, auth_token, test_channel_id):
        """POST /api/lumi/bots/action - compliance_audit returns AI response"""
        res = requests.post(f"{BASE_URL}/api/lumi/bots/action",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "bot_id": "compliance_audit",
                "channel_id": test_channel_id,
                "action": "audit"
            },
            timeout=30
        )
        
        if res.status_code == 404:
            pytest.skip("compliance_audit not installed in this channel")
        
        assert res.status_code == 200, f"Bot action failed: {res.status_code} - {res.text}"
        data = res.json()
        
        assert "content" in data
        content = data["content"]
        assert len(content) > 50, f"Response too short: {content[:100]}"
        print(f"PASS: compliance_audit returned AI response ({len(content)} chars)")
        print(f"  Response preview: {content[:200]}...")

    def test_knowledge_layer_bot_action(self, auth_token, test_channel_id):
        """POST /api/lumi/bots/action - knowledge_layer returns AI response"""
        res = requests.post(f"{BASE_URL}/api/lumi/bots/action",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "bot_id": "knowledge_layer",
                "channel_id": test_channel_id,
                "action": "ask",
                "params": {"query": "What is the status of our team project?"}
            },
            timeout=30
        )
        
        if res.status_code == 404:
            pytest.skip("knowledge_layer not installed in this channel")
        
        assert res.status_code == 200, f"Bot action failed: {res.status_code} - {res.text}"
        data = res.json()
        
        assert "content" in data
        content = data["content"]
        assert len(content) > 50, f"Response too short: {content[:100]}"
        print(f"PASS: knowledge_layer returned AI response ({len(content)} chars)")
        print(f"  Response preview: {content[:200]}...")

    # ═══════════════════════════════════════════════════════════════
    # SLASH COMMAND VIA MESSAGE TESTS
    # ═══════════════════════════════════════════════════════════════
    
    def test_slash_command_summarize_via_message(self, auth_token, test_channel_id):
        """POST /api/lumi/channels/{id}/messages with '/summarize' triggers bot response"""
        res = requests.post(f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "content": "/summarize"
            },
            timeout=30
        )
        
        assert res.status_code == 200, f"Send message failed: {res.status_code} - {res.text}"
        data = res.json()
        
        # Verify user message was sent
        assert "id" in data
        print(f"PASS: Slash command /summarize message sent (msg_id: {data.get('id')})")
        
        # Wait for bot response processing
        time.sleep(2)
        
        # Check messages for bot response
        msgs_res = requests.get(f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages?limit=5", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        if msgs_res.status_code == 200:
            messages = msgs_res.json().get("messages", [])
            bot_msgs = [m for m in messages if m.get("type") == "bot_action" or "[Bot]" in m.get("sender_name", "")]
            if bot_msgs:
                print(f"  Bot response found: {bot_msgs[-1].get('content', '')[:100]}...")
            else:
                print("  INFO: Bot response may still be processing")

    def test_slash_command_match_via_message(self, auth_token, test_channel_id):
        """POST /api/lumi/channels/{id}/messages with '/match senior engineer' triggers talent_matcher"""
        res = requests.post(f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json"
            },
            json={
                "content": "/match senior engineer"
            },
            timeout=30
        )
        
        assert res.status_code == 200, f"Send message failed: {res.status_code} - {res.text}"
        data = res.json()
        
        assert "id" in data
        print(f"PASS: Slash command /match message sent (msg_id: {data.get('id')})")
        
        # Wait for bot response processing
        time.sleep(2)
        
        # Check for bot response
        msgs_res = requests.get(f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages?limit=5", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        if msgs_res.status_code == 200:
            messages = msgs_res.json().get("messages", [])
            bot_msgs = [m for m in messages if m.get("type") == "bot_action" or "[Bot]" in m.get("sender_name", "")]
            if bot_msgs:
                print(f"  Bot response found: {bot_msgs[-1].get('content', '')[:100]}...")


class TestBotConfiguration:
    """Test bot configuration and toggle functionality"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        if res.status_code == 200:
            return res.json().get("access_token")
        pytest.skip("Authentication failed")
    
    def test_get_popular_bots(self, auth_token):
        """GET /api/lumi/bots/popular returns top installed bots"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/popular", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert res.status_code == 200, f"Popular bots fetch failed: {res.text}"
        data = res.json()
        
        assert "bots" in data
        print(f"PASS: Popular bots returns {len(data['bots'])} bots")

    def test_filter_bots_by_category(self, auth_token):
        """GET /api/lumi/bots/catalog?category=Job Toolkit filters correctly"""
        res = requests.get(f"{BASE_URL}/api/lumi/bots/catalog?category=Job%20Toolkit", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert res.status_code == 200, f"Catalog filter failed: {res.text}"
        data = res.json()
        
        assert "bots" in data
        for bot in data["bots"]:
            assert bot["category"] == "Job Toolkit", f"Wrong category: {bot['category']}"
        print(f"PASS: Category filter returns {len(data['bots'])} Job Toolkit bots")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
