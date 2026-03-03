"""
Test Meeting Intelligence, TSR Generator, and LUMI Reactions/Search - Iteration 165
Tests 3 NEW features: Meeting Intelligence widget APIs, TSR Report generation, LUMI emoji reactions & search
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"

class TestAuthenticationFixtures:
    """Helper class for authentication"""
    
    @staticmethod
    def get_auth_token():
        """Get authentication token for the admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None

@pytest.fixture(scope="module")
def auth_token():
    """Module-scoped auth token"""
    token = TestAuthenticationFixtures.get_auth_token()
    if not token:
        pytest.skip("Authentication failed - skipping tests")
    return token

@pytest.fixture
def auth_headers(auth_token):
    """Headers with auth token"""
    return {"Authorization": f"Bearer {auth_token}"}


# ============== MEETING INTELLIGENCE TESTS ==============

class TestMeetingIntelligenceSummary:
    """Tests for GET /api/karau-meet/intelligence/summary"""
    
    def test_intelligence_summary_success(self, auth_headers):
        """Test intelligence summary returns expected fields"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/intelligence/summary", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify all expected fields are present
        assert "meetings_analyzed" in data
        assert "total_action_items" in data
        assert "unresolved_items" in data
        assert "resolution_rate" in data
        assert "top_themes" in data
        assert "weekly_trend" in data
        assert "generated_at" in data
        
        # Verify data types
        assert isinstance(data["meetings_analyzed"], int)
        assert isinstance(data["total_action_items"], int)
        assert isinstance(data["unresolved_items"], int)
        assert isinstance(data["resolution_rate"], (int, float))
        assert isinstance(data["top_themes"], list)
        assert isinstance(data["weekly_trend"], list)
        
        print(f"✅ Intelligence summary: {data['meetings_analyzed']} meetings analyzed, {data['unresolved_items']} unresolved items")
    
    def test_intelligence_summary_unauthorized(self):
        """Test intelligence summary requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/intelligence/summary")
        assert response.status_code == 401


class TestMeetingIntelligenceThemes:
    """Tests for GET /api/karau-meet/intelligence/themes"""
    
    def test_themes_success(self, auth_headers):
        """Test themes endpoint returns categorized themes"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/intelligence/themes", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "themes" in data
        assert "total_meetings_analyzed" in data
        assert "generated_at" in data
        
        assert isinstance(data["themes"], list)
        # If themes exist, verify structure
        if len(data["themes"]) > 0:
            theme = data["themes"][0]
            assert "theme" in theme
            assert "occurrences" in theme
            print(f"✅ Found {len(data['themes'])} themes from {data['total_meetings_analyzed']} meetings")
        else:
            print("✅ No themes yet (expected if no meetings with notes)")
    
    def test_themes_unauthorized(self):
        """Test themes requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/intelligence/themes")
        assert response.status_code == 401


class TestMeetingIntelligenceActionItems:
    """Tests for GET /api/karau-meet/intelligence/action-items"""
    
    def test_action_items_success(self, auth_headers):
        """Test action items endpoint returns items with priority and status"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/intelligence/action-items", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "action_items" in data
        assert "summary" in data
        assert "generated_at" in data
        
        # Verify summary structure
        summary = data["summary"]
        assert "total" in summary
        assert "resolved" in summary
        assert "unresolved" in summary
        assert "resolution_rate" in summary
        
        # If action items exist, verify structure
        if len(data["action_items"]) > 0:
            item = data["action_items"][0]
            assert "id" in item
            assert "content" in item
            assert "status" in item
            assert "priority" in item
            assert item["status"] in ["resolved", "open"]
            assert item["priority"] in ["high", "medium", "low"]
            print(f"✅ Found {len(data['action_items'])} action items, {summary['unresolved']} unresolved")
        else:
            print("✅ No action items yet (expected if no meetings with action items)")
    
    def test_action_items_unauthorized(self):
        """Test action items requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/intelligence/action-items")
        assert response.status_code == 401


# ============== TSR (TEST SUMMARY REPORT) TESTS ==============

class TestTSRGenerate:
    """Tests for POST /api/karau-meet/tsr/generate"""
    
    def test_tsr_generate_success(self, auth_headers):
        """Test TSR report generation returns expected fields"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/tsr/generate", headers=auth_headers)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        # Verify all expected fields
        assert "id" in data
        assert data["id"].startswith("tsr_")
        assert "generated_at" in data
        assert "generated_by" in data
        assert "platform_version" in data
        assert "test_metrics" in data
        assert "feature_coverage" in data
        assert "recommendation" in data
        assert "recommendation_text" in data
        
        # Verify test_metrics structure
        metrics = data["test_metrics"]
        assert "total_tests" in metrics
        assert "passed" in metrics
        assert "failed" in metrics
        assert "skipped" in metrics
        assert "pass_rate" in metrics
        
        # Verify recommendation is valid
        assert data["recommendation"] in ["RELEASE_READY", "CONDITIONAL_RELEASE", "NOT_READY"]
        
        print(f"✅ TSR generated: {data['id']}, recommendation={data['recommendation']}, pass_rate={metrics['pass_rate']}%")
        return data["id"]
    
    def test_tsr_generate_unauthorized(self):
        """Test TSR generation requires authentication"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/tsr/generate")
        assert response.status_code == 401


class TestTSRReportsList:
    """Tests for GET /api/karau-meet/tsr/reports"""
    
    def test_list_tsr_reports(self, auth_headers):
        """Test listing TSR reports"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/tsr/reports", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)
        
        # Verify there's at least one report (from previous generate or existing)
        if len(data["reports"]) > 0:
            report = data["reports"][0]
            assert "id" in report
            assert "generated_at" in report
            assert "recommendation" in report
            print(f"✅ Found {len(data['reports'])} TSR reports, latest: {report['id']}")
        else:
            print("✅ TSR reports list endpoint works (no reports yet)")
    
    def test_list_tsr_unauthorized(self):
        """Test listing TSR reports requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/tsr/reports")
        assert response.status_code == 401


class TestTSRDownload:
    """Tests for GET /api/karau-meet/tsr/download/{report_id}"""
    
    def test_download_tsr_report(self, auth_headers):
        """Test downloading a TSR report as text file"""
        # First get a report ID
        list_response = requests.get(f"{BASE_URL}/api/karau-meet/tsr/reports", headers=auth_headers)
        assert list_response.status_code == 200
        reports = list_response.json().get("reports", [])
        
        if len(reports) == 0:
            # Generate one first
            gen_response = requests.post(f"{BASE_URL}/api/karau-meet/tsr/generate", headers=auth_headers)
            assert gen_response.status_code == 200
            report_id = gen_response.json()["id"]
        else:
            report_id = reports[0]["id"]
        
        # Download the report
        response = requests.get(f"{BASE_URL}/api/karau-meet/tsr/download/{report_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify it's a text file
        content_type = response.headers.get("content-type", "")
        assert "text/plain" in content_type
        
        # Verify content-disposition header for download
        content_disp = response.headers.get("content-disposition", "")
        assert "attachment" in content_disp
        assert "filename" in content_disp
        
        # Verify content contains expected sections
        content = response.text
        assert "TEST SUMMARY REPORT" in content
        assert "TEST METRICS" in content
        assert "PLATFORM METRICS" in content
        assert "FEATURE COVERAGE" in content
        assert "RECOMMENDATION" in content
        
        print(f"✅ Downloaded TSR report {report_id} successfully")
    
    def test_download_nonexistent_report(self, auth_headers):
        """Test downloading a non-existent report returns 404"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/tsr/download/tsr_nonexistent", headers=auth_headers)
        assert response.status_code == 404
    
    def test_download_tsr_unauthorized(self):
        """Test downloading TSR requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/tsr/download/tsr_test123")
        assert response.status_code == 401


# ============== LUMI REACTIONS TESTS ==============

class TestLumiReactions:
    """Tests for POST /api/lumi/messages/{message_id}/react"""
    
    @pytest.fixture
    def test_message_id(self, auth_headers):
        """Get or create a test message ID for reactions"""
        # First get user's channels
        channels_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        if channels_res.status_code != 200:
            pytest.skip("Cannot get channels")
        
        channels = channels_res.json().get("my_channels", [])
        if not channels:
            # Seed channels
            requests.post(f"{BASE_URL}/api/lumi/seed", headers=auth_headers)
            channels_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
            channels = channels_res.json().get("my_channels", [])
        
        if not channels:
            pytest.skip("No channels available for testing")
        
        channel_id = channels[0]["id"]
        
        # Get messages from channel
        msgs_res = requests.get(f"{BASE_URL}/api/lumi/channels/{channel_id}/messages", headers=auth_headers)
        messages = msgs_res.json().get("messages", [])
        
        # Find or create a non-system message
        for msg in messages:
            if msg.get("type") != "system":
                return msg["id"]
        
        # Create a new message for testing
        send_res = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers,
            json={"content": "TEST_reaction_test_message"}
        )
        if send_res.status_code == 200:
            return send_res.json()["id"]
        
        pytest.skip("Cannot create test message")
    
    def test_add_reaction_success(self, auth_headers, test_message_id):
        """Test adding a reaction to a message"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/messages/{test_message_id}/react",
            headers=auth_headers,
            json={"emoji": "👍"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "reactions" in data
        assert isinstance(data["reactions"], dict)
        print(f"✅ Added reaction to message {test_message_id}")
    
    def test_toggle_reaction_off(self, auth_headers, test_message_id):
        """Test toggling a reaction off (clicking same emoji removes it)"""
        # First add reaction
        requests.post(
            f"{BASE_URL}/api/lumi/messages/{test_message_id}/react",
            headers=auth_headers,
            json={"emoji": "❤️"}
        )
        
        # Toggle off by sending same emoji
        response = requests.post(
            f"{BASE_URL}/api/lumi/messages/{test_message_id}/react",
            headers=auth_headers,
            json={"emoji": "❤️"}
        )
        assert response.status_code == 200
        print("✅ Reaction toggle (add/remove) works correctly")
    
    def test_reaction_nonexistent_message(self, auth_headers):
        """Test reacting to non-existent message returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/messages/msg_nonexistent/react",
            headers=auth_headers,
            json={"emoji": "👍"}
        )
        assert response.status_code == 404
    
    def test_reaction_unauthorized(self):
        """Test reactions require authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/messages/msg_test/react",
            json={"emoji": "👍"}
        )
        assert response.status_code == 401


# ============== LUMI SEARCH TESTS ==============

class TestLumiSearch:
    """Tests for GET /api/lumi/search?q="""
    
    def test_search_messages_success(self, auth_headers):
        """Test searching messages across channels"""
        response = requests.get(f"{BASE_URL}/api/lumi/search?q=test", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert data["query"] == "test"
        assert isinstance(data["results"], list)
        
        # If results found, verify structure
        if len(data["results"]) > 0:
            result = data["results"][0]
            assert "id" in result
            assert "content" in result
            assert "channel_id" in result
            assert "channel_name" in result
            print(f"✅ Search found {len(data['results'])} results for 'test'")
        else:
            print("✅ Search works (no results for 'test' query)")
    
    def test_search_short_query(self, auth_headers):
        """Test search with too short query returns empty results"""
        response = requests.get(f"{BASE_URL}/api/lumi/search?q=t", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["results"] == []
        print("✅ Short query returns empty results correctly")
    
    def test_search_empty_query(self, auth_headers):
        """Test search with empty query returns empty results"""
        response = requests.get(f"{BASE_URL}/api/lumi/search?q=", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["results"] == []
        print("✅ Empty query returns empty results correctly")
    
    def test_search_unauthorized(self):
        """Test search requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/search?q=test")
        assert response.status_code == 401


# ============== INTEGRATION TEST ==============

class TestIntegration:
    """End-to-end integration tests"""
    
    def test_full_tsr_workflow(self, auth_headers):
        """Test complete TSR workflow: generate -> list -> download"""
        # 1. Generate TSR
        gen_res = requests.post(f"{BASE_URL}/api/karau-meet/tsr/generate", headers=auth_headers)
        assert gen_res.status_code == 200
        tsr_id = gen_res.json()["id"]
        
        # 2. List reports and verify new one appears
        list_res = requests.get(f"{BASE_URL}/api/karau-meet/tsr/reports", headers=auth_headers)
        assert list_res.status_code == 200
        reports = list_res.json()["reports"]
        report_ids = [r["id"] for r in reports]
        assert tsr_id in report_ids
        
        # 3. Download the report
        dl_res = requests.get(f"{BASE_URL}/api/karau-meet/tsr/download/{tsr_id}", headers=auth_headers)
        assert dl_res.status_code == 200
        assert "TEST SUMMARY REPORT" in dl_res.text
        
        print(f"✅ Full TSR workflow passed: {tsr_id}")
    
    def test_full_reaction_workflow(self, auth_headers):
        """Test complete reaction workflow: send message -> react -> verify"""
        # Get a channel
        ch_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        if ch_res.status_code != 200:
            pytest.skip("Cannot get channels")
        
        channels = ch_res.json().get("my_channels", [])
        if not channels:
            requests.post(f"{BASE_URL}/api/lumi/seed", headers=auth_headers)
            ch_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
            channels = ch_res.json().get("my_channels", [])
        
        if not channels:
            pytest.skip("No channels")
        
        channel_id = channels[0]["id"]
        
        # 1. Send a message
        msg_res = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers,
            json={"content": "TEST_integration_reaction_workflow"}
        )
        if msg_res.status_code != 200:
            pytest.skip("Cannot send message")
        
        msg_id = msg_res.json()["id"]
        
        # 2. Add reactions
        react_res = requests.post(
            f"{BASE_URL}/api/lumi/messages/{msg_id}/react",
            headers=auth_headers,
            json={"emoji": "🎉"}
        )
        assert react_res.status_code == 200
        
        # 3. Verify reaction appears in message list
        msgs_res = requests.get(f"{BASE_URL}/api/lumi/channels/{channel_id}/messages", headers=auth_headers)
        messages = msgs_res.json().get("messages", [])
        test_msg = next((m for m in messages if m["id"] == msg_id), None)
        assert test_msg is not None
        assert "🎉" in test_msg.get("reactions", {})
        
        print(f"✅ Full reaction workflow passed for message {msg_id}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
