"""
Bot Marketplace Tests - Iteration 205
Tests for the expanded Bot Marketplace with 18 specialized bots across 4 categories:
- Job Toolkit (5 bots): Talent Matcher, Resume Architect, Interview Copilot, EZ Sourcing, Salary Negotiator
- AI Meeting (5 bots): Note-Taker, Smart Scheduler, Search Copilot, Attendance Tracker, Summary Generator
- AI Messenger (3 bots): Knowledge Layer, Multilingual Translator, Omnichannel Assistant  
- Security & QA (5 bots): Compliance Audit, Visual Testing, Bias Auditor, Threat Scanner, Translation QA
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"

# Expected bot IDs for each category
JOB_TOOLKIT_BOTS = ["talent_matcher", "resume_architect", "interview_copilot", "ez_sourcing", "salary_negotiator"]
AI_MEETING_BOTS = ["note_taker", "smart_scheduler", "search_copilot", "attendance_tracker", "summary_generator"]
AI_MESSENGER_BOTS = ["knowledge_layer", "multilingual_translator", "omnichannel_assistant"]
SECURITY_QA_BOTS = ["compliance_audit", "visual_testing", "bias_auditor", "threat_scanner", "translation_qa"]

ALL_BOT_IDS = JOB_TOOLKIT_BOTS + AI_MEETING_BOTS + AI_MESSENGER_BOTS + SECURITY_QA_BOTS


class TestBotCatalog:
    """Tests for GET /api/lumi/bots/catalog endpoint"""
    
    def test_catalog_returns_all_18_bots(self):
        """GET /api/lumi/bots/catalog returns all 18 bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog")
        assert response.status_code == 200
        
        data = response.json()
        assert "bots" in data
        assert "categories" in data
        assert "total" in data
        
        assert data["total"] == 18, f"Expected 18 bots, got {data['total']}"
        assert len(data["bots"]) == 18
        
        # Verify all expected bot IDs are present
        bot_ids = [bot["id"] for bot in data["bots"]]
        for expected_id in ALL_BOT_IDS:
            assert expected_id in bot_ids, f"Bot {expected_id} not found in catalog"
        
        # Verify 4 categories
        assert len(data["categories"]) == 4
        assert "Job Toolkit" in data["categories"]
        assert "AI Meeting" in data["categories"]
        assert "AI Messenger" in data["categories"]
        assert "Security & QA" in data["categories"]
        print(f"PASS: All 18 bots returned with 4 categories")
    
    def test_catalog_job_toolkit_category_filter(self):
        """GET /api/lumi/bots/catalog?category=Job%20Toolkit returns 5 bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", params={"category": "Job Toolkit"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 5, f"Expected 5 Job Toolkit bots, got {data['total']}"
        
        # Verify all bots belong to Job Toolkit
        for bot in data["bots"]:
            assert bot["category"] == "Job Toolkit"
            assert bot["id"] in JOB_TOOLKIT_BOTS
        print(f"PASS: Job Toolkit category returns 5 bots")
    
    def test_catalog_ai_meeting_category_filter(self):
        """GET /api/lumi/bots/catalog?category=AI%20Meeting returns 5 bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", params={"category": "AI Meeting"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 5, f"Expected 5 AI Meeting bots, got {data['total']}"
        
        for bot in data["bots"]:
            assert bot["category"] == "AI Meeting"
            assert bot["id"] in AI_MEETING_BOTS
        print(f"PASS: AI Meeting category returns 5 bots")
    
    def test_catalog_ai_messenger_category_filter(self):
        """GET /api/lumi/bots/catalog?category=AI%20Messenger returns 3 bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", params={"category": "AI Messenger"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 3, f"Expected 3 AI Messenger bots, got {data['total']}"
        
        for bot in data["bots"]:
            assert bot["category"] == "AI Messenger"
            assert bot["id"] in AI_MESSENGER_BOTS
        print(f"PASS: AI Messenger category returns 3 bots")
    
    def test_catalog_security_qa_category_filter(self):
        """GET /api/lumi/bots/catalog?category=Security%20%26%20QA returns 5 bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog", params={"category": "Security & QA"})
        assert response.status_code == 200
        
        data = response.json()
        assert data["total"] == 5, f"Expected 5 Security & QA bots, got {data['total']}"
        
        for bot in data["bots"]:
            assert bot["category"] == "Security & QA"
            assert bot["id"] in SECURITY_QA_BOTS
        print(f"PASS: Security & QA category returns 5 bots")
    
    def test_catalog_bot_structure(self):
        """Verify each bot has correct structure: name, description, icon, rating, install_count, commands"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/catalog")
        assert response.status_code == 200
        
        data = response.json()
        for bot in data["bots"]:
            assert "id" in bot
            assert "name" in bot
            assert "description" in bot
            assert "icon" in bot
            assert "category" in bot
            assert "subcategory" in bot
            assert "featured" in bot
            assert "commands" in bot
            assert isinstance(bot["commands"], list)
            assert "install_count" in bot
            assert isinstance(bot["install_count"], int)
            assert "rating" in bot
            assert 1 <= bot["rating"] <= 5
        print(f"PASS: All bots have correct structure")


class TestFeaturedBots:
    """Tests for GET /api/lumi/bots/featured endpoint"""
    
    def test_featured_bots_endpoint(self):
        """GET /api/lumi/bots/featured returns featured bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/featured")
        assert response.status_code == 200
        
        data = response.json()
        assert "bots" in data
        
        # Should have featured bots (Talent Matcher, Resume Architect, Note-Taker, Search Copilot, Knowledge Layer, Compliance Audit)
        featured_bots = data["bots"]
        assert len(featured_bots) >= 4, f"Expected at least 4 featured bots, got {len(featured_bots)}"
        
        # Each featured bot should have required fields
        for bot in featured_bots:
            assert "id" in bot
            assert "name" in bot
            assert "description" in bot
            assert "category" in bot
            assert "install_count" in bot
            assert "rating" in bot
        print(f"PASS: Featured bots endpoint returns {len(featured_bots)} featured bots")


class TestPopularBots:
    """Tests for GET /api/lumi/bots/popular endpoint"""
    
    def test_popular_bots_returns_top_6(self):
        """GET /api/lumi/bots/popular returns top 6 most installed bots"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/popular")
        assert response.status_code == 200
        
        data = response.json()
        assert "bots" in data
        assert len(data["bots"]) == 6, f"Expected 6 popular bots, got {len(data['bots'])}"
        
        # Verify sorted by install_count descending
        install_counts = [bot["install_count"] for bot in data["bots"]]
        assert install_counts == sorted(install_counts, reverse=True), "Bots should be sorted by install_count desc"
        print(f"PASS: Popular bots returns top 6 by install count")


class TestBotInstallFlow:
    """Tests for bot installation, uninstallation, toggle, and configure"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed - skipping authenticated tests")
        return response.json().get("access_token")
    
    @pytest.fixture
    def test_channel_id(self, auth_token):
        """Create a test channel for bot installation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # First try to get existing channels
        response = requests.get(f"{BASE_URL}/api/lumi/channels", headers=headers)
        if response.status_code == 200:
            channels = response.json().get("channels", [])
            if channels:
                return channels[0]["id"]
        
        # Create a new test channel
        channel_name = f"TEST_bot_install_{uuid.uuid4().hex[:8]}"
        response = requests.post(f"{BASE_URL}/api/lumi/channels", 
            headers=headers,
            json={"name": channel_name})
        
        if response.status_code in [200, 201]:
            return response.json().get("id")
        
        pytest.skip("Could not get or create test channel")
    
    def test_install_bot(self, auth_token, test_channel_id):
        """POST /api/lumi/bots/install installs a bot to a channel"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        # Install talent_matcher bot
        response = requests.post(f"{BASE_URL}/api/lumi/bots/install",
            headers=headers,
            json={"bot_id": "talent_matcher", "channel_id": test_channel_id})
        
        # Could be 200 (installed) or 400 (already installed)
        assert response.status_code in [200, 400], f"Install failed: {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert data["bot_id"] == "talent_matcher"
            assert data["status"] == "installed"
            assert "config" in data
            print(f"PASS: Bot installed successfully")
        else:
            print(f"PASS: Bot already installed (expected)")
    
    def test_get_installed_bots(self, auth_token):
        """GET /api/lumi/bots/installed returns installed bots"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/lumi/bots/installed", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "bots" in data
        assert "count" in data
        print(f"PASS: Get installed bots returns {data['count']} bots")
    
    def test_install_not_found_bot(self, auth_token, test_channel_id):
        """Install non-existent bot returns 404"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/lumi/bots/install",
            headers=headers,
            json={"bot_id": "non_existent_bot", "channel_id": test_channel_id})
        
        assert response.status_code == 404
        print(f"PASS: Non-existent bot returns 404")


class TestBotReviewSystem:
    """Tests for bot review submission and retrieval"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed")
        return response.json().get("access_token")
    
    def test_submit_review(self, auth_token):
        """POST /api/lumi/bots/review submits a bot review (1-5 rating)"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/lumi/bots/review",
            headers=headers,
            json={
                "bot_id": "talent_matcher",
                "rating": 5,
                "review": "TEST_review: Great bot for finding talent!"
            })
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "reviewed"
        print(f"PASS: Review submitted successfully")
    
    def test_submit_invalid_rating(self, auth_token):
        """Submit review with invalid rating returns 400"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/lumi/bots/review",
            headers=headers,
            json={
                "bot_id": "talent_matcher",
                "rating": 10,  # Invalid - must be 1-5
                "review": "Invalid"
            })
        
        assert response.status_code == 400
        print(f"PASS: Invalid rating returns 400")
    
    def test_get_bot_reviews(self):
        """GET /api/lumi/bots/reviews/{bot_id} returns reviews for a bot"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/reviews/talent_matcher")
        assert response.status_code == 200
        
        data = response.json()
        assert "reviews" in data
        assert "count" in data
        assert "avg_rating" in data
        print(f"PASS: Get reviews returns {data['count']} reviews with avg rating {data['avg_rating']}")
    
    def test_get_reviews_nonexistent_bot(self):
        """GET /api/lumi/bots/reviews/{invalid_bot_id} returns 404"""
        response = requests.get(f"{BASE_URL}/api/lumi/bots/reviews/nonexistent_bot")
        assert response.status_code == 404
        print(f"PASS: Non-existent bot reviews returns 404")


class TestBotAction:
    """Tests for bot action execution"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed")
        return response.json().get("access_token")
    
    @pytest.fixture
    def channel_with_bot(self, auth_token):
        """Get or create channel with installed bot"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get installed bots to find a channel with a bot
        response = requests.get(f"{BASE_URL}/api/lumi/bots/installed", headers=headers)
        if response.status_code == 200:
            bots = response.json().get("bots", [])
            for bot in bots:
                if bot.get("is_active", True):
                    return {"channel_id": bot["channel_id"], "bot_id": bot["bot_id"]}
        
        pytest.skip("No installed bot found for action test")
    
    def test_bot_action_not_installed(self, auth_token):
        """POST /api/lumi/bots/action fails if bot not installed in channel"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.post(f"{BASE_URL}/api/lumi/bots/action",
            headers=headers,
            json={
                "bot_id": "talent_matcher",
                "channel_id": "fake_channel_123",
                "action": "match"
            })
        
        assert response.status_code == 404
        print(f"PASS: Action on non-installed bot returns 404")


class TestBotToggleAndConfigure:
    """Tests for toggle and configure endpoints"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code != 200:
            pytest.skip("Authentication failed")
        return response.json().get("access_token")
    
    @pytest.fixture
    def installed_bot(self, auth_token):
        """Get an installed bot"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.get(f"{BASE_URL}/api/lumi/bots/installed", headers=headers)
        if response.status_code == 200:
            bots = response.json().get("bots", [])
            if bots:
                return bots[0]
        pytest.skip("No installed bot found")
    
    def test_toggle_bot(self, auth_token, installed_bot):
        """PUT /api/lumi/bots/toggle/{id} toggles bot active/paused"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        install_id = installed_bot["id"]
        current_active = installed_bot.get("is_active", True)
        
        # Toggle to opposite state
        response = requests.put(f"{BASE_URL}/api/lumi/bots/toggle/{install_id}",
            headers=headers,
            json={"is_active": not current_active})
        
        assert response.status_code == 200
        data = response.json()
        expected_status = "paused" if current_active else "active"
        assert data["status"] == expected_status
        
        # Toggle back
        requests.put(f"{BASE_URL}/api/lumi/bots/toggle/{install_id}",
            headers=headers,
            json={"is_active": current_active})
        
        print(f"PASS: Toggle bot works correctly")
    
    def test_configure_bot(self, auth_token, installed_bot):
        """PUT /api/lumi/bots/configure/{id} updates bot config"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        install_id = installed_bot["id"]
        
        response = requests.put(f"{BASE_URL}/api/lumi/bots/configure/{install_id}",
            headers=headers,
            json={"config": {"test_setting": True}})
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "configured"
        assert data["config"]["test_setting"] == True
        print(f"PASS: Configure bot works correctly")
    
    def test_toggle_nonexistent_bot(self, auth_token):
        """Toggle non-existent install returns 404"""
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
        
        response = requests.put(f"{BASE_URL}/api/lumi/bots/toggle/nonexistent_install_id",
            headers=headers,
            json={"is_active": False})
        
        assert response.status_code == 404
        print(f"PASS: Toggle non-existent bot returns 404")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
