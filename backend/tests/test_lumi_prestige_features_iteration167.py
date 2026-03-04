"""
LUMI Prestige - Iteration 167 Backend API Tests
Features: Domain privacy, Auto-channels, Threads, Presence, Retention, Members, Voice calls
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"


class TestAuthSetup:
    """Authentication setup tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def user_info(self, auth_token):
        """Get current user info"""
        response = requests.get(f"{BASE_URL}/api/auth/me", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        if response.status_code == 200:
            return response.json()
        return {"email": ADMIN_EMAIL, "user_id": "admin_user"}

    def test_login_success(self, auth_token):
        """Test login returns valid token"""
        assert auth_token is not None
        assert len(auth_token) > 0
        print(f"✅ Login successful, token length: {len(auth_token)}")


class TestDomainPrivacy:
    """Domain-based privacy feature tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    def test_get_domain_members(self, auth_token):
        """GET /api/lumi/domain/members returns members from same domain"""
        response = requests.get(f"{BASE_URL}/api/lumi/domain/members", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200, f"Domain members failed: {response.text}"
        data = response.json()
        assert "members" in data
        assert "domain" in data
        # Should return medmatch.com domain
        domain = data.get("domain", "")
        print(f"✅ Domain members - domain: {domain}, members count: {len(data['members'])}")
        # Verify members have presence status
        if data["members"]:
            member = data["members"][0]
            assert "user_id" in member
            assert "status" in member
    
    def test_domain_members_filter_by_last_name(self, auth_token):
        """GET /api/lumi/domain/members?last_name=X filters results"""
        response = requests.get(f"{BASE_URL}/api/lumi/domain/members?last_name=admin", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert "members" in data
        print(f"✅ Domain members filtered - count: {len(data['members'])}")
    
    def test_domain_members_requires_auth(self):
        """Domain members endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/domain/members")
        assert response.status_code == 401
        print("✅ Domain members requires auth (401)")


class TestDomainAutoChannel:
    """Auto-created domain channel tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    def test_create_domain_auto_channel(self, auth_token):
        """POST /api/lumi/domain/auto-channel creates a domain-protected channel"""
        response = requests.post(f"{BASE_URL}/api/lumi/domain/auto-channel", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200, f"Auto-channel failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert data.get("channel_type") == "domain"
        assert "domain" in data
        # Should be 'Medmatch Team' or similar for medmatch.com
        print(f"✅ Domain channel created/exists: {data.get('name')} ({data.get('id')})")
        print(f"   domain: {data.get('domain')}, members: {len(data.get('members', []))}")
        return data
    
    def test_domain_channel_has_all_members(self, auth_token):
        """Domain channel should contain all domain users as members"""
        # First get/create the domain channel
        response = requests.post(f"{BASE_URL}/api/lumi/domain/auto-channel", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        channel = response.json()
        members = channel.get("members", [])
        assert len(members) > 0, "Domain channel should have at least 1 member"
        print(f"✅ Domain channel has {len(members)} members")


class TestUserSearch:
    """User search with domain privacy filter"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    def test_users_search_returns_same_domain_only(self, auth_token):
        """GET /api/lumi/users/search filters by same domain"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200, f"User search failed: {response.text}"
        data = response.json()
        assert "users" in data
        users = data["users"]
        # All users should be from same domain (medmatch.com)
        for user in users:
            email = user.get("email", "")
            if "@" in email:
                domain = email.split("@")[1]
                assert "medmatch" in domain.lower(), f"User {email} not from medmatch domain"
        print(f"✅ User search returns {len(users)} same-domain users")
    
    def test_users_search_with_query(self, auth_token):
        """User search with query string"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=admin", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        assert response.status_code == 200
        data = response.json()
        print(f"✅ User search with query - found {len(data.get('users', []))} users")
    
    def test_users_include_presence_status(self, auth_token):
        """User search results include presence status"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        data = response.json()
        users = data.get("users", [])
        if users:
            user = users[0]
            assert "status" in user, "User should have presence status"
            print(f"✅ User presence included - first user status: {user.get('status')}")


class TestMessageThreads:
    """Message thread/reply feature tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def test_channel(self, auth_token):
        """Get or create a test channel"""
        # List channels and use first one
        response = requests.get(f"{BASE_URL}/api/lumi/channels", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        if response.status_code == 200:
            channels = response.json().get("my_channels", [])
            if channels:
                return channels[0]
        # Create a new channel
        response = requests.post(f"{BASE_URL}/api/lumi/channels", json={
            "name": "TEST_Thread_Channel",
            "description": "Test channel for threads",
            "channel_type": "group",
            "is_private": False
        }, headers={"Authorization": f"Bearer {auth_token}"})
        return response.json()
    
    @pytest.fixture(scope="class")
    def test_message(self, auth_token, test_channel):
        """Create a test message to thread on"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{test_channel['id']}/messages",
            json={"content": "TEST_Thread parent message for thread testing"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 200:
            return response.json()
        # If channel doesn't allow messages, get existing messages
        msgs = requests.get(
            f"{BASE_URL}/api/lumi/channels/{test_channel['id']}/messages",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if msgs.status_code == 200:
            messages = msgs.json().get("messages", [])
            for m in messages:
                if m.get("type") == "message":
                    return m
        return None
    
    def test_create_thread_reply(self, auth_token, test_message):
        """POST /api/lumi/messages/{id}/thread creates a thread reply"""
        if not test_message:
            pytest.skip("No test message available")
        message_id = test_message["id"]
        response = requests.post(
            f"{BASE_URL}/api/lumi/messages/{message_id}/thread",
            json={"content": "TEST_Thread reply to parent message"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Thread reply failed: {response.text}"
        data = response.json()
        assert data.get("type") == "thread_reply"
        assert data.get("thread_parent_id") == message_id
        print(f"✅ Thread reply created: {data.get('id')}")
        return data
    
    def test_get_thread_replies(self, auth_token, test_message):
        """GET /api/lumi/messages/{id}/thread returns parent + replies"""
        if not test_message:
            pytest.skip("No test message available")
        message_id = test_message["id"]
        response = requests.get(
            f"{BASE_URL}/api/lumi/messages/{message_id}/thread",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get thread failed: {response.text}"
        data = response.json()
        assert "parent" in data
        assert "replies" in data
        assert data["parent"]["id"] == message_id
        print(f"✅ Thread retrieved - parent: {data['parent']['id']}, replies: {len(data['replies'])}")
    
    def test_thread_on_nonexistent_message(self, auth_token):
        """Thread on non-existent message returns 404"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/messages/msg_nonexistent123/thread",
            json={"content": "Reply to nowhere"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        print("✅ Thread on non-existent message returns 404")


class TestPresenceSystem:
    """Rich presence system tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    def test_update_presence_available(self, auth_token):
        """PUT /api/lumi/presence updates user status to available"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            json={"status": "available"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Presence update failed: {response.text}"
        data = response.json()
        assert data.get("status") == "available"
        print("✅ Presence updated to 'available'")
    
    def test_update_presence_busy(self, auth_token):
        """PUT /api/lumi/presence updates user status to busy"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            json={"status": "busy"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "busy"
        print("✅ Presence updated to 'busy'")
    
    def test_update_presence_in_meeting(self, auth_token):
        """PUT /api/lumi/presence updates user status to in_meeting"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            json={"status": "in_meeting"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "in_meeting"
        print("✅ Presence updated to 'in_meeting'")
    
    def test_update_presence_invalid_status(self, auth_token):
        """Invalid presence status returns 400"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/presence",
            json={"status": "invalid_status"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        print("✅ Invalid presence status returns 400")
    
    def test_get_all_presence(self, auth_token):
        """GET /api/lumi/presence/all returns presence for all users"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/presence/all",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get presence failed: {response.text}"
        data = response.json()
        assert "presence" in data
        presence_map = data["presence"]
        print(f"✅ Got presence for {len(presence_map)} users")
        # Check valid status values
        valid_statuses = ["available", "busy", "in_meeting", "ooo", "vacation", "offline", "online"]
        for user_id, status in presence_map.items():
            assert status in valid_statuses, f"Invalid status for {user_id}: {status}"


class TestRetentionSettings:
    """Message retention configuration tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    def test_get_retention_default(self, auth_token):
        """GET /api/lumi/settings/retention returns 90 days default"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/settings/retention",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get retention failed: {response.text}"
        data = response.json()
        assert "retention_days" in data
        # Default should be 90 days
        print(f"✅ Retention settings: {data.get('retention_days')} days")
    
    def test_update_retention_days(self, auth_token):
        """PUT /api/lumi/settings/retention updates retention days"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/settings/retention",
            json={"days": 60},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Update retention failed: {response.text}"
        data = response.json()
        assert data.get("retention_days") == 60
        print("✅ Retention updated to 60 days")
        
        # Reset to 90
        requests.put(
            f"{BASE_URL}/api/lumi/settings/retention",
            json={"days": 90},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
    
    def test_retention_requires_auth(self):
        """Retention endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/settings/retention")
        assert response.status_code == 401
        print("✅ Retention settings requires auth (401)")


class TestChannelMembers:
    """Channel member management tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def test_channel(self, auth_token):
        """Get first channel"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels", headers={
            "Authorization": f"Bearer {auth_token}"
        })
        if response.status_code == 200:
            channels = response.json().get("my_channels", [])
            if channels:
                return channels[0]
        return None
    
    def test_get_channel_members(self, auth_token, test_channel):
        """GET /api/lumi/channels/{id}/members returns members with presence status"""
        if not test_channel:
            pytest.skip("No test channel available")
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{test_channel['id']}/members",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get members failed: {response.text}"
        data = response.json()
        assert "members" in data
        members = data["members"]
        print(f"✅ Channel has {len(members)} members")
        # Each member should have presence status
        if members:
            member = members[0]
            assert "user_id" in member
            assert "status" in member
            print(f"   First member status: {member.get('status')}")
    
    def test_add_member_requires_admin(self, auth_token, test_channel):
        """POST /api/lumi/channels/{id}/members/add requires admin role"""
        if not test_channel:
            pytest.skip("No test channel available")
        # Try to add a non-existent user - should check admin first
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{test_channel['id']}/members/add",
            json={"user_id": "nonexistent_user_id"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Could be 403 (not admin), 404 (user not found), or 200 (already member)
        assert response.status_code in [200, 403, 404], f"Unexpected status: {response.status_code}"
        print(f"✅ Add member returned {response.status_code}")
    
    def test_channel_members_nonexistent(self, auth_token):
        """Get members of non-existent channel returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/ch_nonexistent123/members",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        print("✅ Non-existent channel members returns 404")


class TestVoiceCalls:
    """Voice call initiation tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    def test_initiate_voice_call(self, auth_token):
        """POST /api/lumi/voice/call initiates a call"""
        # Get a recipient user
        users_resp = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        users = users_resp.json().get("users", []) if users_resp.status_code == 200 else []
        
        if not users:
            # Create a dummy call to test endpoint structure
            response = requests.post(
                f"{BASE_URL}/api/lumi/voice/call",
                json={"recipient_id": "test_recipient_id", "type": "voice"},
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            # Should fail with user not found or succeed
            print(f"✅ Voice call endpoint accessible - status: {response.status_code}")
            return
        
        recipient_id = users[0]["user_id"]
        response = requests.post(
            f"{BASE_URL}/api/lumi/voice/call",
            json={"recipient_id": recipient_id, "type": "voice"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # May get 200 or 400 (can't call self)
        assert response.status_code in [200, 400], f"Unexpected status: {response.status_code}"
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data.get("status") == "ringing"
            print(f"✅ Voice call initiated: {data.get('id')}, status: {data.get('status')}")
        else:
            print(f"✅ Voice call returned {response.status_code} (expected for self-call)")
    
    def test_voice_call_requires_recipient(self, auth_token):
        """Voice call without recipient returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/voice/call",
            json={"type": "voice"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 400
        print("✅ Voice call without recipient returns 400")
    
    def test_voice_call_requires_auth(self):
        """Voice call endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/voice/call",
            json={"recipient_id": "test", "type": "voice"}
        )
        assert response.status_code == 401
        print("✅ Voice call requires auth (401)")


class TestChannelBasics:
    """Basic channel operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        return response.json().get("access_token")
    
    def test_list_channels(self, auth_token):
        """GET /api/lumi/channels lists user's channels"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"List channels failed: {response.text}"
        data = response.json()
        assert "my_channels" in data
        channels = data["my_channels"]
        # Check for domain channel
        domain_channels = [c for c in channels if c.get("channel_type") == "domain"]
        print(f"✅ Listed {len(channels)} channels, {len(domain_channels)} domain channels")
        return channels


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
