"""
ENZI Sentiment Analysis, Channel Templates, Webhook Templates - Iteration 192
Tests for:
- Sentiment Analysis API (positive/neutral/urgent/negative)
- Channel Templates (project, sprint, incident, standup, general)
- Webhook Templates (GitHub, Jira, CI/CD, Slack-Compatible, Monitoring)
- Rich Message Formatting (markdown rendering via frontend)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSentimentAnalysis:
    """Test ENZI Sentiment Analysis endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_sentiment_analyze_urgent(self):
        """Test sentiment analysis with urgent message"""
        resp = requests.post(f"{BASE_URL}/api/lumi/sentiment/analyze", 
            headers=self.headers,
            json={"message_content": "This is URGENT! Please respond ASAP!"})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert "tone" in data
        assert data["tone"] == "urgent"
        assert "confidence" in data
        print(f"✓ Urgent sentiment: tone={data['tone']}, confidence={data['confidence']}")
    
    def test_sentiment_analyze_positive(self):
        """Test sentiment analysis with positive message"""
        resp = requests.post(f"{BASE_URL}/api/lumi/sentiment/analyze",
            headers=self.headers,
            json={"message_content": "Great job! This is awesome work, thanks so much!"})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["tone"] == "positive"
        print(f"✓ Positive sentiment: tone={data['tone']}, confidence={data['confidence']}")
    
    def test_sentiment_analyze_negative(self):
        """Test sentiment analysis with negative message"""
        resp = requests.post(f"{BASE_URL}/api/lumi/sentiment/analyze",
            headers=self.headers,
            json={"message_content": "There's a problem with the bug, something is wrong and broken"})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["tone"] == "negative"
        print(f"✓ Negative sentiment: tone={data['tone']}, confidence={data['confidence']}")
    
    def test_sentiment_analyze_neutral(self):
        """Test sentiment analysis with neutral message"""
        resp = requests.post(f"{BASE_URL}/api/lumi/sentiment/analyze",
            headers=self.headers,
            json={"message_content": "I will attend the meeting at 3pm today"})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["tone"] == "neutral"
        print(f"✓ Neutral sentiment: tone={data['tone']}, confidence={data['confidence']}")
    
    def test_sentiment_channel_mood(self):
        """Test channel mood endpoint"""
        # First get a channel
        channels_resp = requests.get(f"{BASE_URL}/api/lumi/channels", headers=self.headers)
        assert channels_resp.status_code == 200
        channels = channels_resp.json().get("channels", [])
        if not channels:
            pytest.skip("No channels available for mood test")
        
        channel_id = channels[0]["id"]
        resp = requests.get(f"{BASE_URL}/api/lumi/sentiment/channel/{channel_id}/mood",
            headers=self.headers)
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert "mood" in data
        assert "distribution" in data
        assert all(k in data["distribution"] for k in ["positive", "neutral", "urgent", "negative"])
        print(f"✓ Channel mood: {data['mood']}, distribution={data['distribution']}")
    
    def test_sentiment_unauthorized(self):
        """Test sentiment analysis requires auth"""
        resp = requests.post(f"{BASE_URL}/api/lumi/sentiment/analyze",
            json={"message_content": "test"})
        assert resp.status_code == 401
        print("✓ Sentiment analysis requires authentication")


class TestChannelTemplates:
    """Test ENZI Channel Templates endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
    
    def test_list_channel_templates(self):
        """Test listing channel templates returns 5 templates"""
        resp = requests.get(f"{BASE_URL}/api/lumi/templates/channels/list", headers=self.headers)
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) == 5, f"Expected 5 templates, got {len(templates)}"
        
        # Verify all expected templates exist
        template_ids = [t["id"] for t in templates]
        expected_ids = ["project", "sprint", "incident", "standup", "general"]
        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"
        
        print(f"✓ Channel templates: {template_ids}")
    
    def test_channel_template_structure(self):
        """Test channel template has required fields"""
        resp = requests.get(f"{BASE_URL}/api/lumi/templates/channels/list", headers=self.headers)
        assert resp.status_code == 200
        templates = resp.json()["templates"]
        
        for t in templates:
            assert "id" in t
            assert "name" in t
            assert "description" in t
            assert "type" in t
        
        print("✓ All templates have required fields (id, name, description, type)")
    
    def test_create_channel_from_template_project(self):
        """Test creating channel from project template"""
        unique_prefix = f"TEST-{str(uuid.uuid4())[:6]}"
        resp = requests.post(f"{BASE_URL}/api/lumi/templates/channels/create",
            headers=self.headers,
            json={"template_id": "project", "name_prefix": unique_prefix})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert "id" in data
        assert "name" in data
        assert unique_prefix in data["name"]
        assert data["template_id"] == "project"
        print(f"✓ Created channel from project template: {data['name']}")
    
    def test_create_channel_from_template_sprint(self):
        """Test creating channel from sprint template"""
        unique_prefix = f"Q1-{str(uuid.uuid4())[:4]}"
        resp = requests.post(f"{BASE_URL}/api/lumi/templates/channels/create",
            headers=self.headers,
            json={"template_id": "sprint", "name_prefix": unique_prefix})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["template_id"] == "sprint"
        print(f"✓ Created channel from sprint template: {data['name']}")
    
    def test_create_channel_from_template_incident(self):
        """Test creating channel from incident template"""
        unique_prefix = f"INC-{str(uuid.uuid4())[:4]}"
        resp = requests.post(f"{BASE_URL}/api/lumi/templates/channels/create",
            headers=self.headers,
            json={"template_id": "incident", "name_prefix": unique_prefix})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["template_id"] == "incident"
        print(f"✓ Created channel from incident template: {data['name']}")
    
    def test_create_channel_invalid_template(self):
        """Test creating channel with invalid template returns 404"""
        resp = requests.post(f"{BASE_URL}/api/lumi/templates/channels/create",
            headers=self.headers,
            json={"template_id": "nonexistent", "name_prefix": "Test"})
        assert resp.status_code == 404
        print("✓ Invalid template returns 404")
    
    def test_create_channel_unauthorized(self):
        """Test creating channel requires auth"""
        resp = requests.post(f"{BASE_URL}/api/lumi/templates/channels/create",
            json={"template_id": "project", "name_prefix": "Test"})
        assert resp.status_code == 401
        print("✓ Create channel requires authentication")


class TestWebhookTemplates:
    """Test ENZI Webhook Templates endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Get a channel for webhook tests
        channels_resp = requests.get(f"{BASE_URL}/api/lumi/channels", headers=self.headers)
        if channels_resp.status_code == 200:
            channels = channels_resp.json().get("channels", [])
            self.channel_id = channels[0]["id"] if channels else None
        else:
            self.channel_id = None
    
    def test_list_webhook_templates(self):
        """Test listing webhook templates returns 5 templates"""
        resp = requests.get(f"{BASE_URL}/api/lumi/automation/webhook-templates/list", headers=self.headers)
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert "templates" in data
        templates = data["templates"]
        assert len(templates) == 5, f"Expected 5 templates, got {len(templates)}"
        
        # Verify all expected templates exist
        template_ids = [t["id"] for t in templates]
        expected_ids = ["github", "jira", "cicd", "slack", "monitoring"]
        for expected_id in expected_ids:
            assert expected_id in template_ids, f"Missing template: {expected_id}"
        
        print(f"✓ Webhook templates: {template_ids}")
    
    def test_webhook_template_structure(self):
        """Test webhook template has required fields"""
        resp = requests.get(f"{BASE_URL}/api/lumi/automation/webhook-templates/list", headers=self.headers)
        assert resp.status_code == 200
        templates = resp.json()["templates"]
        
        for t in templates:
            assert "id" in t
            assert "name" in t
            assert "description" in t
            assert "events" in t
            assert "format_help" in t
        
        print("✓ All webhook templates have required fields")
    
    def test_create_webhook_from_template_github(self):
        """Test creating webhook from GitHub template"""
        if not self.channel_id:
            pytest.skip("No channel available for webhook test")
        
        resp = requests.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            headers=self.headers,
            json={"template_id": "github", "channel_id": self.channel_id})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert "id" in data
        assert "url" in data
        assert "sample_curl" in data
        assert data["name"] == "GitHub"
        print(f"✓ Created GitHub webhook: {data['url'][:60]}...")
    
    def test_create_webhook_from_template_jira(self):
        """Test creating webhook from Jira template"""
        if not self.channel_id:
            pytest.skip("No channel available for webhook test")
        
        resp = requests.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            headers=self.headers,
            json={"template_id": "jira", "channel_id": self.channel_id})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["name"] == "Jira"
        print(f"✓ Created Jira webhook")
    
    def test_create_webhook_from_template_cicd(self):
        """Test creating webhook from CI/CD template"""
        if not self.channel_id:
            pytest.skip("No channel available for webhook test")
        
        resp = requests.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            headers=self.headers,
            json={"template_id": "cicd", "channel_id": self.channel_id})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["name"] == "CI/CD Pipeline"
        print(f"✓ Created CI/CD webhook")
    
    def test_create_webhook_from_template_slack(self):
        """Test creating webhook from Slack-Compatible template"""
        if not self.channel_id:
            pytest.skip("No channel available for webhook test")
        
        resp = requests.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            headers=self.headers,
            json={"template_id": "slack", "channel_id": self.channel_id})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["name"] == "Slack-Compatible"
        print(f"✓ Created Slack-Compatible webhook")
    
    def test_create_webhook_from_template_monitoring(self):
        """Test creating webhook from Monitoring template"""
        if not self.channel_id:
            pytest.skip("No channel available for webhook test")
        
        resp = requests.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            headers=self.headers,
            json={"template_id": "monitoring", "channel_id": self.channel_id})
        assert resp.status_code == 200, f"Failed: {resp.text}"
        data = resp.json()
        assert data["name"] == "Monitoring & Alerts"
        print(f"✓ Created Monitoring webhook")
    
    def test_create_webhook_invalid_template(self):
        """Test creating webhook with invalid template returns 404"""
        if not self.channel_id:
            pytest.skip("No channel available for webhook test")
        
        resp = requests.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            headers=self.headers,
            json={"template_id": "nonexistent", "channel_id": self.channel_id})
        assert resp.status_code == 404
        print("✓ Invalid webhook template returns 404")
    
    def test_create_webhook_unauthorized(self):
        """Test creating webhook requires auth"""
        resp = requests.post(f"{BASE_URL}/api/lumi/automation/webhook-templates/create",
            json={"template_id": "github", "channel_id": "test"})
        assert resp.status_code == 401
        print("✓ Create webhook requires authentication")


class TestRichMessageFormatting:
    """Test message content is preserved for markdown rendering"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Login and get auth token"""
        login_resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert login_resp.status_code == 200
        self.token = login_resp.json().get("access_token")
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        
        # Get a channel for message tests
        channels_resp = requests.get(f"{BASE_URL}/api/lumi/channels", headers=self.headers)
        if channels_resp.status_code == 200:
            channels = channels_resp.json().get("channels", [])
            self.channel_id = channels[0]["id"] if channels else None
        else:
            self.channel_id = None
    
    def test_send_markdown_bold_message(self):
        """Test sending message with bold markdown is preserved"""
        if not self.channel_id:
            pytest.skip("No channel available")
        
        content = "This is **bold** text and __also bold__"
        resp = requests.post(f"{BASE_URL}/api/lumi/channels/{self.channel_id}/messages",
            headers=self.headers,
            json={"content": content})
        assert resp.status_code in [200, 201], f"Failed: {resp.text}"
        data = resp.json()
        assert data["content"] == content
        print("✓ Bold markdown preserved in message")
    
    def test_send_markdown_italic_message(self):
        """Test sending message with italic markdown is preserved"""
        if not self.channel_id:
            pytest.skip("No channel available")
        
        content = "This is *italic* text and _also italic_"
        resp = requests.post(f"{BASE_URL}/api/lumi/channels/{self.channel_id}/messages",
            headers=self.headers,
            json={"content": content})
        assert resp.status_code in [200, 201], f"Failed: {resp.text}"
        data = resp.json()
        assert data["content"] == content
        print("✓ Italic markdown preserved in message")
    
    def test_send_code_block_message(self):
        """Test sending message with code block is preserved"""
        if not self.channel_id:
            pytest.skip("No channel available")
        
        content = "Here is code:\n```python\nprint('hello world')\n```"
        resp = requests.post(f"{BASE_URL}/api/lumi/channels/{self.channel_id}/messages",
            headers=self.headers,
            json={"content": content})
        assert resp.status_code in [200, 201], f"Failed: {resp.text}"
        data = resp.json()
        assert "```python" in data["content"]
        print("✓ Code block preserved in message")
    
    def test_send_inline_code_message(self):
        """Test sending message with inline code is preserved"""
        if not self.channel_id:
            pytest.skip("No channel available")
        
        content = "Use the `npm install` command"
        resp = requests.post(f"{BASE_URL}/api/lumi/channels/{self.channel_id}/messages",
            headers=self.headers,
            json={"content": content})
        assert resp.status_code in [200, 201], f"Failed: {resp.text}"
        data = resp.json()
        assert "`npm install`" in data["content"]
        print("✓ Inline code preserved in message")
    
    def test_send_link_message(self):
        """Test sending message with link is preserved"""
        if not self.channel_id:
            pytest.skip("No channel available")
        
        content = "Check out [Google](https://google.com)"
        resp = requests.post(f"{BASE_URL}/api/lumi/channels/{self.channel_id}/messages",
            headers=self.headers,
            json={"content": content})
        assert resp.status_code in [200, 201], f"Failed: {resp.text}"
        data = resp.json()
        assert "[Google]" in data["content"]
        print("✓ Link markdown preserved in message")


class TestKineticTypographyAnimations:
    """Verify CSS animations exist for kinetic typography"""
    
    def test_index_css_has_stagger_animations(self):
        """Verify stagger-in animations exist in index.css"""
        # Read the CSS file from the frontend
        # This is a static test verifying the CSS structure
        css_path = "/app/frontend/src/index.css"
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        assert "@keyframes stagger-in" in css_content
        assert ".animate-stagger-in" in css_content
        assert ".animate-stagger-in-1" in css_content
        assert ".animate-stagger-in-2" in css_content
        print("✓ Stagger-in animations exist in CSS")
    
    def test_index_css_has_scale_in_animation(self):
        """Verify scale-in animation exists"""
        css_path = "/app/frontend/src/index.css"
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        assert "@keyframes scale-in" in css_content
        assert ".animate-scale-in" in css_content
        print("✓ Scale-in animation exists in CSS")
    
    def test_index_css_has_shimmer_animation(self):
        """Verify shimmer animation exists"""
        css_path = "/app/frontend/src/index.css"
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        assert "@keyframes shimmer" in css_content
        assert ".shimmer-text" in css_content
        print("✓ Shimmer animation exists in CSS")
    
    def test_index_css_has_float_animation(self):
        """Verify float animation exists"""
        css_path = "/app/frontend/src/index.css"
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        assert "@keyframes float" in css_content
        assert ".animate-float" in css_content
        print("✓ Float animation exists in CSS")
    
    def test_index_css_has_sentiment_tone_badges(self):
        """Verify sentiment tone badge styles exist"""
        css_path = "/app/frontend/src/index.css"
        with open(css_path, 'r') as f:
            css_content = f.read()
        
        assert ".tone-positive" in css_content
        assert ".tone-neutral" in css_content
        assert ".tone-urgent" in css_content
        assert ".tone-negative" in css_content
        print("✓ Sentiment tone badge styles exist in CSS")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
