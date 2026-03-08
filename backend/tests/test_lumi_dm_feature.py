"""
LUMI Messenger - Direct Messages (DM) Feature Tests
Tests for DM-related API endpoints: user search, create/get DM, list DMs
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-ai-hub-1.preview.emergentagent.com').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestLumiDMFeature:
    """Test Direct Messages feature for LUMI Messenger"""
    
    @pytest.fixture(scope="class")
    def auth_data(self):
        """Get authentication token and user data"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200, f"Auth failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in response"
        assert "user" in data, "No user in response"
        return data
    
    @pytest.fixture(scope="class")
    def headers(self, auth_data):
        """Get headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_data['access_token']}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def current_user(self, auth_data):
        """Get current user data"""
        return auth_data["user"]
    
    # ============== User Search Tests ==============
    
    def test_search_users_empty_query(self, headers):
        """GET /api/lumi/users/search with empty query returns recent users"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=",
            headers=headers
        )
        assert response.status_code == 200, f"Search failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "users" in data, "Missing 'users' in response"
        assert isinstance(data["users"], list), "users should be a list"
        
        print(f"✅ User search with empty query returned {len(data['users'])} users")
        return data["users"]
    
    def test_search_users_excludes_current_user(self, headers, current_user):
        """GET /api/lumi/users/search should exclude current user from results"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify current user is not in results
        user_ids = [u.get("user_id") for u in data.get("users", [])]
        assert current_user["user_id"] not in user_ids, "Current user should be excluded from search results"
        
        print(f"✅ Current user ({current_user['user_id']}) correctly excluded from search results")
    
    def test_search_users_with_query(self, headers):
        """GET /api/lumi/users/search?q=test searches by name or email"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=test",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "users" in data
        
        # If users found, verify structure
        if data["users"]:
            user = data["users"][0]
            assert "user_id" in user, "user should have user_id"
            assert "name" in user or "email" in user, "user should have name or email"
        
        print(f"✅ User search with 'test' query returned {len(data['users'])} users")
    
    def test_search_users_requires_auth(self):
        """GET /api/lumi/users/search requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ User search correctly requires authentication")
    
    # ============== Create DM Tests ==============
    
    def test_create_dm_with_recipient(self, headers, current_user):
        """POST /api/lumi/dm creates a DM channel with recipient"""
        # First find a recipient user
        search_response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=",
            headers=headers
        )
        assert search_response.status_code == 200
        users = search_response.json()["users"]
        
        if not users:
            pytest.skip("No other users available to create DM")
        
        recipient = users[0]
        recipient_id = recipient["user_id"]
        
        # Create DM
        response = requests.post(
            f"{BASE_URL}/api/lumi/dm",
            headers=headers,
            json={"recipient_id": recipient_id}
        )
        assert response.status_code == 200, f"Create DM failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data, "DM channel should have id"
        assert data.get("channel_type") == "dm", "channel_type should be 'dm'"
        assert "dm_key" in data, "DM should have dm_key for deduplication"
        assert "members" in data, "DM should have members list"
        assert len(data["members"]) == 2, "DM should have exactly 2 members"
        
        # Verify both users are members
        member_ids = [m["user_id"] for m in data["members"]]
        assert current_user["user_id"] in member_ids, "Current user should be member"
        assert recipient_id in member_ids, "Recipient should be member"
        
        print(f"✅ Created DM channel: {data['id']} with {recipient.get('name', recipient_id)}")
        return data
    
    def test_create_dm_returns_existing_dm(self, headers, current_user):
        """POST /api/lumi/dm with same recipient returns existing DM (no duplicate)"""
        # First find a recipient user
        search_response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=",
            headers=headers
        )
        assert search_response.status_code == 200
        users = search_response.json()["users"]
        
        if not users:
            pytest.skip("No other users available")
        
        recipient_id = users[0]["user_id"]
        
        # Create DM first time
        response1 = requests.post(
            f"{BASE_URL}/api/lumi/dm",
            headers=headers,
            json={"recipient_id": recipient_id}
        )
        assert response1.status_code == 200
        dm1 = response1.json()
        
        # Create DM second time with same recipient
        response2 = requests.post(
            f"{BASE_URL}/api/lumi/dm",
            headers=headers,
            json={"recipient_id": recipient_id}
        )
        assert response2.status_code == 200
        dm2 = response2.json()
        
        # Verify same DM returned (no duplicate)
        assert dm1["id"] == dm2["id"], "Same DM channel should be returned for same recipient"
        assert dm1["dm_key"] == dm2["dm_key"], "dm_key should match"
        
        print(f"✅ Re-creating DM correctly returns existing channel: {dm1['id']}")
    
    def test_create_dm_with_self_fails(self, headers, current_user):
        """POST /api/lumi/dm with own user_id should fail"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/dm",
            headers=headers,
            json={"recipient_id": current_user["user_id"]}
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✅ Creating DM with self correctly fails with 400")
    
    def test_create_dm_with_nonexistent_user_fails(self, headers):
        """POST /api/lumi/dm with non-existent user should fail"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/dm",
            headers=headers,
            json={"recipient_id": "nonexistent_user_xyz"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✅ Creating DM with non-existent user correctly fails with 404")
    
    def test_create_dm_requires_auth(self):
        """POST /api/lumi/dm requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/dm",
            json={"recipient_id": "some_user_id"}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ Create DM correctly requires authentication")
    
    # ============== List DMs Tests ==============
    
    def test_list_dms(self, headers, current_user):
        """GET /api/lumi/dm returns list of DMs with dm_partner info"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/dm",
            headers=headers
        )
        assert response.status_code == 200, f"List DMs failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "dms" in data, "Missing 'dms' in response"
        assert isinstance(data["dms"], list), "dms should be a list"
        
        print(f"✅ List DMs returned {len(data['dms'])} DM conversations")
        
        # Verify dm_partner is populated for each DM
        for dm in data["dms"]:
            assert dm.get("channel_type") == "dm", f"All items should be DM channels"
            assert "dm_partner" in dm, f"DM should have dm_partner info"
            partner = dm["dm_partner"]
            assert "user_id" in partner, "dm_partner should have user_id"
            assert partner["user_id"] != current_user["user_id"], "dm_partner should not be current user"
            print(f"  ✓ DM {dm['id']} with partner: {partner.get('name', partner['user_id'])}")
        
        return data["dms"]
    
    def test_list_dms_requires_auth(self):
        """GET /api/lumi/dm requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/dm")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✅ List DMs correctly requires authentication")
    
    # ============== Channels Filtering Tests ==============
    
    def test_channels_list_excludes_dm_channels(self, headers):
        """GET /api/lumi/channels does NOT include DM channels in my_channels"""
        # First ensure at least one DM exists
        search_response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=",
            headers=headers
        )
        if search_response.status_code == 200 and search_response.json()["users"]:
            # Create a DM if users exist
            recipient_id = search_response.json()["users"][0]["user_id"]
            requests.post(
                f"{BASE_URL}/api/lumi/dm",
                headers=headers,
                json={"recipient_id": recipient_id}
            )
        
        # Get channels list
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify no DM channels in my_channels
        for ch in data.get("my_channels", []):
            assert ch.get("channel_type") != "dm", f"DM channel {ch['id']} should not be in channels list"
        
        # Verify no DM channels in discover
        for ch in data.get("discover", []):
            assert ch.get("channel_type") != "dm", f"DM channel {ch['id']} should not be in discover list"
        
        print(f"✅ Channels list correctly excludes DM channels (my_channels={len(data.get('my_channels', []))})")
    
    # ============== Sending Messages in DM Tests ==============
    
    def test_send_message_in_dm_channel(self, headers):
        """POST /api/lumi/channels/{dm_id}/messages works for DM channels"""
        # First create or get a DM
        search_response = requests.get(
            f"{BASE_URL}/api/lumi/users/search?q=",
            headers=headers
        )
        if search_response.status_code != 200 or not search_response.json()["users"]:
            pytest.skip("No users available to create DM")
        
        recipient_id = search_response.json()["users"][0]["user_id"]
        dm_response = requests.post(
            f"{BASE_URL}/api/lumi/dm",
            headers=headers,
            json={"recipient_id": recipient_id}
        )
        assert dm_response.status_code == 200
        dm = dm_response.json()
        dm_channel_id = dm["id"]
        
        # Send a message in the DM channel
        test_content = f"Test DM message {uuid.uuid4().hex[:8]}"
        msg_response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{dm_channel_id}/messages",
            headers=headers,
            json={"content": test_content}
        )
        assert msg_response.status_code == 200, f"Send message in DM failed: {msg_response.text}"
        msg_data = msg_response.json()
        
        # Verify message structure
        assert "id" in msg_data, "Message should have id"
        assert msg_data["content"] == test_content
        assert msg_data["channel_id"] == dm_channel_id
        
        print(f"✅ Sent message in DM channel {dm_channel_id}: '{test_content[:30]}...'")
        
        # Verify message retrieval
        get_response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{dm_channel_id}/messages",
            headers=headers
        )
        assert get_response.status_code == 200
        messages = get_response.json()["messages"]
        msg_ids = [m["id"] for m in messages]
        assert msg_data["id"] in msg_ids, "Sent message should appear in DM messages list"
        
        print(f"✅ Message verified in DM channel messages list")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
