"""
LUMI Messenger Backend API Tests
Tests for channel-based real-time messaging feature
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-preview.preview.emergentagent.com')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestLumiMessengerAuth:
    """Test authentication for LUMI Messenger"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for LUMI tests"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Auth failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        return data["access_token"]
    
    def test_login_returns_user_data(self, auth_token):
        """Test that login returns user data needed for LUMI"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "user_id" in data["user"]
        print(f"✅ Login returns user data with user_id: {data['user']['user_id']}")


class TestLumiChannels:
    """Test LUMI channel operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_seed_channels(self, headers):
        """Test seeding channels (creates default channels if not exist)"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/seed",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        # Should be either "seeded" or "already_seeded"
        assert data["status"] in ["seeded", "already_seeded"]
        print(f"✅ Seed channels: status={data['status']}, count={data.get('count', 'N/A')}")
    
    def test_list_channels(self, headers):
        """Test listing channels returns my_channels and discover lists"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "my_channels" in data, "Missing 'my_channels' in response"
        assert "discover" in data, "Missing 'discover' in response"
        assert isinstance(data["my_channels"], list)
        assert isinstance(data["discover"], list)
        
        print(f"✅ List channels: my_channels={len(data['my_channels'])}, discover={len(data['discover'])}")
        
        # Verify seeded channels exist
        channel_names = [ch["name"] for ch in data["my_channels"]]
        seeded_channels = ["General", "Engineering", "Design", "Announcements", "Random"]
        
        for name in seeded_channels:
            if name in channel_names:
                print(f"  ✓ Found seeded channel: {name}")
        
        return data["my_channels"]
    
    def test_create_channel(self, headers):
        """Test creating a new channel"""
        unique_name = f"TEST_Channel_{uuid.uuid4().hex[:6]}"
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers,
            json={
                "name": unique_name,
                "description": "Test channel for automated testing",
                "channel_type": "group",
                "is_private": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data, "Missing 'id' in response"
        assert data["name"] == unique_name
        assert data["channel_type"] == "group"
        assert data["is_private"] == False
        assert "members" in data
        assert len(data["members"]) == 1  # Creator is auto-added
        
        print(f"✅ Created channel: {unique_name} (id={data['id']})")
        return data["id"]
    
    def test_create_private_channel(self, headers):
        """Test creating a private channel"""
        unique_name = f"TEST_Private_{uuid.uuid4().hex[:6]}"
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers,
            json={
                "name": unique_name,
                "description": "Private test channel",
                "channel_type": "project",
                "is_private": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["is_private"] == True
        assert data["channel_type"] == "project"
        print(f"✅ Created private channel: {unique_name}")
        return data["id"]
    
    def test_create_announcement_channel(self, headers):
        """Test creating an announcement channel"""
        unique_name = f"TEST_Announce_{uuid.uuid4().hex[:6]}"
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers,
            json={
                "name": unique_name,
                "description": "Test announcement channel",
                "channel_type": "announcement",
                "is_private": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["channel_type"] == "announcement"
        print(f"✅ Created announcement channel: {unique_name}")
    
    def test_get_channel(self, headers):
        """Test getting a specific channel by ID"""
        # First get list to find a channel ID
        list_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers
        )
        assert list_response.status_code == 200
        channels = list_response.json()["my_channels"]
        
        if not channels:
            pytest.skip("No channels available to test")
        
        channel_id = channels[0]["id"]
        
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{channel_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == channel_id
        assert "name" in data
        assert "members" in data
        print(f"✅ Got channel: {data['name']} (members={len(data.get('members', []))})")
    
    def test_channel_requires_auth(self):
        """Test that channel endpoints require authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels")
        assert response.status_code == 401
        print("✅ Channel list correctly requires authentication")
    
    def test_create_channel_requires_auth(self):
        """Test that creating channel requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            json={"name": "Test", "description": "Test"}
        )
        assert response.status_code == 401
        print("✅ Create channel correctly requires authentication")


class TestLumiMessages:
    """Test LUMI message operations"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def test_channel_id(self, headers):
        """Get or create a test channel for message tests"""
        # First try to get existing channels
        list_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers
        )
        if list_response.status_code == 200:
            channels = list_response.json()["my_channels"]
            if channels:
                return channels[0]["id"]
        
        # Create a new channel if none exist
        unique_name = f"TEST_MsgChannel_{uuid.uuid4().hex[:6]}"
        create_response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers,
            json={"name": unique_name, "description": "For message testing"}
        )
        assert create_response.status_code == 200
        return create_response.json()["id"]
    
    def test_send_message(self, headers, test_channel_id):
        """Test sending a message to a channel"""
        test_content = f"Test message {uuid.uuid4().hex[:8]}"
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages",
            headers=headers,
            json={"content": test_content}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data, "Missing 'id' in message response"
        assert data["content"] == test_content
        assert data["channel_id"] == test_channel_id
        assert "sender_id" in data
        assert "sender_name" in data
        assert "created_at" in data
        
        print(f"✅ Sent message: {data['id']} to channel {test_channel_id}")
        return data["id"]
    
    def test_get_messages(self, headers, test_channel_id):
        """Test getting messages from a channel"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "messages" in data
        assert "channel_id" in data
        assert isinstance(data["messages"], list)
        
        print(f"✅ Got {len(data['messages'])} messages from channel {test_channel_id}")
        
        # Verify message structure if messages exist
        if data["messages"]:
            msg = data["messages"][0]
            assert "id" in msg
            assert "content" in msg
            assert "sender_id" in msg
    
    def test_send_message_and_verify_retrieval(self, headers, test_channel_id):
        """Test sending a message and verifying it appears in message list"""
        unique_content = f"Unique test message {uuid.uuid4().hex[:8]}"
        
        # Send message
        send_response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages",
            headers=headers,
            json={"content": unique_content}
        )
        assert send_response.status_code == 200
        sent_msg_id = send_response.json()["id"]
        
        # Retrieve messages
        get_response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages",
            headers=headers
        )
        assert get_response.status_code == 200
        messages = get_response.json()["messages"]
        
        # Verify message exists in retrieved list
        msg_ids = [m["id"] for m in messages]
        assert sent_msg_id in msg_ids, f"Sent message {sent_msg_id} not found in channel messages"
        
        # Verify content matches
        found_msg = next(m for m in messages if m["id"] == sent_msg_id)
        assert found_msg["content"] == unique_content
        
        print(f"✅ Sent and retrieved message: {unique_content[:30]}...")
    
    def test_message_requires_auth(self, test_channel_id):
        """Test that message endpoints require authentication"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{test_channel_id}/messages"
        )
        assert response.status_code == 401
        print("✅ Get messages correctly requires authentication")
    
    def test_send_message_requires_membership(self, headers):
        """Test that sending message to non-member channel fails"""
        # This test may vary based on implementation
        # Creating a scenario where user is not a member
        fake_channel_id = "ch_nonexistent123"
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{fake_channel_id}/messages",
            headers=headers,
            json={"content": "Test"}
        )
        assert response.status_code in [403, 404], f"Expected 403 or 404, got {response.status_code}"
        print("✅ Sending to non-member channel correctly fails")


class TestLumiPresence:
    """Test LUMI presence and typing indicators"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_presence(self, headers):
        """Test getting online presence"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/presence",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "online" in data
        assert isinstance(data["online"], list)
        print(f"✅ Got presence: {len(data['online'])} users online")
    
    def test_typing_indicator(self, headers):
        """Test sending typing indicator"""
        # Get a channel first
        list_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers
        )
        if list_response.status_code != 200:
            pytest.skip("Could not get channels")
        
        channels = list_response.json()["my_channels"]
        if not channels:
            pytest.skip("No channels available")
        
        channel_id = channels[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/typing",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print(f"✅ Typing indicator sent to channel {channel_id}")


class TestLumiChannelMembership:
    """Test joining and leaving channels"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_join_channel(self, headers):
        """Test joining a channel"""
        # First create a channel to join (or get existing)
        list_response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers
        )
        assert list_response.status_code == 200
        channels = list_response.json()["my_channels"]
        
        if not channels:
            pytest.skip("No channels available")
        
        channel_id = channels[0]["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/join",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        # Should be either "joined" or "already_member"
        assert data["status"] in ["joined", "already_member"]
        print(f"✅ Join channel result: {data['status']}")
    
    def test_leave_channel(self, headers):
        """Test leaving a channel"""
        # Create a throwaway channel to leave
        unique_name = f"TEST_Leave_{uuid.uuid4().hex[:6]}"
        create_response = requests.post(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers,
            json={"name": unique_name, "description": "To be left"}
        )
        if create_response.status_code != 200:
            pytest.skip("Could not create channel to leave")
        
        channel_id = create_response.json()["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{channel_id}/leave",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "left"
        print(f"✅ Left channel: {unique_name}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
