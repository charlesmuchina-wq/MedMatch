"""
LUMI Messenger - New Features Test Suite for Iteration 176
Tests for: Emoji Picker, Keyboard Shortcuts, Admin Audit Log, Privacy & Compliance, Content Moderation, Calendar Sync
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test Credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


class TestAuthAndSetup:
    """Authentication and setup tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    def test_admin_login(self, admin_token):
        """Test admin login returns valid token"""
        assert admin_token is not None
        assert len(admin_token) > 0
        print(f"Admin login successful, token length: {len(admin_token)}")


class TestContentModeration:
    """Content moderation API tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_moderation_check_clean_text(self, auth_headers):
        """POST /api/lumi/moderation/check - clean text returns clean:true"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/moderation/check",
            headers=auth_headers,
            json={"text": "Hello, this is a professional message about our project."}
        )
        assert response.status_code == 200, f"Moderation check failed: {response.text}"
        data = response.json()
        assert "clean" in data
        assert data["clean"] == True
        assert "flags" in data
        assert len(data["flags"]) == 0
        print(f"Clean text moderation passed: {data}")
    
    def test_moderation_check_profanity(self, auth_headers):
        """POST /api/lumi/moderation/check - profanity returns clean:false"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/moderation/check",
            headers=auth_headers,
            json={"text": "This message contains damn and shit words"}
        )
        assert response.status_code == 200, f"Moderation check failed: {response.text}"
        data = response.json()
        assert "clean" in data
        assert data["clean"] == False
        assert "filtered_text" in data
        assert "flags" in data
        assert len(data["flags"]) > 0
        print(f"Profanity moderation passed: {data}")
    
    def test_moderation_settings_get(self, auth_headers):
        """GET /api/lumi/moderation/settings - returns default settings"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/moderation/settings",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get moderation settings failed: {response.text}"
        data = response.json()
        assert "enabled" in data
        assert "auto_filter" in data
        assert "notify_admin" in data
        assert "block_messages" in data
        print(f"Moderation settings: {data}")
    
    def test_moderation_settings_update(self, auth_headers):
        """PUT /api/lumi/moderation/settings - updates settings"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/moderation/settings",
            headers=auth_headers,
            json={"enabled": True, "auto_filter": True, "notify_admin": True, "block_messages": False}
        )
        assert response.status_code == 200, f"Update moderation settings failed: {response.text}"
        data = response.json()
        assert data.get("status") == "saved"
        print(f"Moderation settings updated: {data}")
    
    def test_moderation_unauthorized(self):
        """POST /api/lumi/moderation/check - returns 401 without auth"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/moderation/check",
            json={"text": "Test message"}
        )
        assert response.status_code == 401
        print("Moderation API correctly requires authentication")


class TestComplianceFrameworks:
    """Privacy & Compliance API tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_compliance_frameworks_list(self, auth_headers):
        """GET /api/lumi/compliance/frameworks - returns 6 frameworks"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/compliance/frameworks",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get compliance frameworks failed: {response.text}"
        data = response.json()
        assert "frameworks" in data
        frameworks = data["frameworks"]
        assert len(frameworks) == 6, f"Expected 6 frameworks, got {len(frameworks)}"
        
        # Verify all expected frameworks exist
        framework_ids = [f["id"] for f in frameworks]
        expected_ids = ["hipaa", "gdpr", "uk_dpa", "australia_privacy", "china_pipl", "japan_appi"]
        for expected in expected_ids:
            assert expected in framework_ids, f"Missing framework: {expected}"
        
        print(f"Compliance frameworks: {[f['name'] for f in frameworks]}")
    
    def test_compliance_frameworks_have_requirements(self, auth_headers):
        """GET /api/lumi/compliance/frameworks - each framework has requirements"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/compliance/frameworks",
            headers=auth_headers
        )
        data = response.json()
        for fw in data["frameworks"]:
            assert "requirements" in fw, f"Framework {fw['id']} missing requirements"
            assert len(fw["requirements"]) > 0, f"Framework {fw['id']} has empty requirements"
            assert "name" in fw
            assert "region" in fw
            assert "description" in fw
        print("All frameworks have requirements")
    
    def test_compliance_status(self, auth_headers):
        """GET /api/lumi/compliance/status - returns score and controls"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/compliance/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get compliance status failed: {response.text}"
        data = response.json()
        
        assert "overall_score" in data
        assert isinstance(data["overall_score"], int)
        assert data["overall_score"] > 0
        
        assert "frameworks_covered" in data
        assert data["frameworks_covered"] == 6
        
        assert "platform_controls" in data
        controls = data["platform_controls"]
        assert "encryption_in_transit" in controls
        assert "audit_logging" in controls
        assert "content_moderation" in controls
        
        print(f"Compliance status: score={data['overall_score']}%, controls={len(controls)}")
    
    def test_compliance_karau_reference(self, auth_headers):
        """GET /api/lumi/compliance/status - includes KARAU reference"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/compliance/status",
            headers=auth_headers
        )
        data = response.json()
        assert "karau_compliance_reference" in data
        karau_ref = data["karau_compliance_reference"]
        assert "name" in karau_ref
        assert "shared_controls" in karau_ref
        print(f"KARAU compliance reference: {karau_ref['name']}")
    
    def test_compliance_unauthorized(self):
        """GET /api/lumi/compliance/frameworks - returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/lumi/compliance/frameworks")
        assert response.status_code == 401
        print("Compliance API correctly requires authentication")


class TestAdminAuditLog:
    """Admin Audit Log API tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_audit_log_get(self, auth_headers):
        """GET /api/lumi/admin/audit-log - returns logs array"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/admin/audit-log",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get audit log failed: {response.text}"
        data = response.json()
        
        assert "logs" in data
        assert "categories" in data
        assert "stats" in data
        assert isinstance(data["logs"], list)
        
        print(f"Audit log: {len(data['logs'])} entries, categories: {data['categories']}")
    
    def test_audit_log_category_filter(self, auth_headers):
        """GET /api/lumi/admin/audit-log?category=moderation - filters by category"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/admin/audit-log?category=moderation",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        # All logs should be moderation category if filter works
        for log in data["logs"]:
            assert log.get("category") == "moderation" or len(data["logs"]) == 0
        print(f"Filtered audit log (moderation): {len(data['logs'])} entries")
    
    def test_audit_log_all_category(self, auth_headers):
        """GET /api/lumi/admin/audit-log?category=all - returns all logs"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/admin/audit-log?category=all",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        print(f"All audit logs: {len(data['logs'])} entries")
    
    def test_audit_log_unauthorized(self):
        """GET /api/lumi/admin/audit-log - returns 401 without auth"""
        response = requests.get(f"{BASE_URL}/api/lumi/admin/audit-log")
        assert response.status_code == 401
        print("Audit log API correctly requires authentication")


class TestCalendarSync:
    """Google Calendar Sync API tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_calendar_sync_non_google_user(self, auth_headers):
        """POST /api/lumi/calendar/sync - returns skipped for non-Google users"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/calendar/sync",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Calendar sync failed: {response.text}"
        data = response.json()
        
        # Non-Google SSO users should get skipped response
        assert "status" in data
        assert data["status"] == "skipped"
        assert "reason" in data
        print(f"Calendar sync for non-Google user: {data}")
    
    def test_calendar_sync_unauthorized(self):
        """POST /api/lumi/calendar/sync - returns 401 without auth"""
        response = requests.post(f"{BASE_URL}/api/lumi/calendar/sync")
        assert response.status_code == 401
        print("Calendar sync API correctly requires authentication")


class TestLumiChannelsAndMessages:
    """Channel and message tests for moderation integration"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_get_channels(self, auth_headers):
        """GET /api/lumi/channels - returns user's channels"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get channels failed: {response.text}"
        data = response.json()
        assert "my_channels" in data
        assert isinstance(data["my_channels"], list)
        print(f"User has {len(data['my_channels'])} channels")
        return data["my_channels"]
    
    def test_send_clean_message(self, auth_headers):
        """POST /api/lumi/channels/{id}/messages - send clean message succeeds"""
        # Get channels first
        channels_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        channels = channels_res.json().get("my_channels", [])
        
        if len(channels) == 0:
            pytest.skip("No channels available for message test")
        
        channel_id = channels[0]["id"]
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers,
            json={"content": "Test message from iteration 176 - clean content"}
        )
        assert response.status_code == 200, f"Send message failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "content" in data
        assert data["content"] == "Test message from iteration 176 - clean content"
        print(f"Sent clean message: {data['id']}")


class TestEmojiPicker:
    """Emoji picker related API tests (client-side component)"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_emoji_in_message(self, auth_headers):
        """Send message with emoji works correctly"""
        channels_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        channels = channels_res.json().get("my_channels", [])
        
        if len(channels) == 0:
            pytest.skip("No channels available for emoji test")
        
        channel_id = channels[0]["id"]
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers,
            json={"content": "Testing emoji picker 😀🎉👍"}
        )
        assert response.status_code == 200, f"Send emoji message failed: {response.text}"
        data = response.json()
        assert "😀" in data["content"] or "emoji" in data["content"].lower()
        print(f"Sent message with emojis: {data['content']}")
    
    def test_message_reactions(self, auth_headers):
        """React to message with emoji"""
        # Get channels and messages
        channels_res = requests.get(f"{BASE_URL}/api/lumi/channels", headers=auth_headers)
        channels = channels_res.json().get("my_channels", [])
        
        if len(channels) == 0:
            pytest.skip("No channels available for reaction test")
        
        channel_id = channels[0]["id"]
        messages_res = requests.get(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/messages",
            headers=auth_headers
        )
        messages = messages_res.json().get("messages", [])
        
        if len(messages) == 0:
            pytest.skip("No messages available for reaction test")
        
        message_id = messages[-1]["id"]
        response = requests.post(
            f"{BASE_URL}/api/lumi/messages/{message_id}/react",
            headers=auth_headers,
            json={"emoji": "👍"}
        )
        assert response.status_code == 200, f"Add reaction failed: {response.text}"
        data = response.json()
        assert "reactions" in data
        print(f"Added reaction to message: {data['reactions']}")


class TestProfileAndCapabilities:
    """Profile and AI capabilities tests"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get authenticated headers"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}
    
    def test_profile_capabilities(self, auth_headers):
        """GET /api/lumi/profile/capabilities - returns AI capabilities list"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/profile/capabilities",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Get capabilities failed: {response.text}"
        data = response.json()
        
        assert "capabilities" in data
        assert len(data["capabilities"]) >= 10
        assert "user" in data
        
        # Check for specific capabilities
        cap_ids = [c["id"] for c in data["capabilities"]]
        assert "threading" in cap_ids
        assert "reactions" in cap_ids
        
        print(f"User has {len(data['capabilities'])} AI capabilities")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
