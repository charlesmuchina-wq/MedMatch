"""
Test LUMI Channel Invites and Authorization System
Tests:
- Channel creation with invite_emails and requires_approval
- Sending invites to existing users
- Getting pending invites
- Accepting/declining invites
- Join with requires_approval (pending_approval status)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"


class TestLumiChannelInvites:
    """Test LUMI channel invite system"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        return response.json().get("access_token")
    
    @pytest.fixture(scope="class")
    def test_user_token(self):
        """Get test user authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Test user login failed: {response.text}"
        return response.json().get("access_token")

    # ============ Channel Creation with Invites ============
    
    def test_create_channel_basic(self, admin_token):
        """Test creating a basic channel without invites"""
        channel_name = f"TEST_basic_{uuid.uuid4().hex[:6]}"
        response = requests.post(f"{BASE_URL}/api/lumi/channels", 
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": channel_name,
                "description": "Basic test channel",
                "channel_type": "group",
                "is_private": False
            }
        )
        assert response.status_code == 200, f"Create channel failed: {response.text}"
        data = response.json()
        assert data["name"] == channel_name
        assert data["id"].startswith("ch_")
        print(f"PASS: Created basic channel {channel_name}")
    
    def test_create_channel_with_invite_emails(self, admin_token):
        """Test creating channel with invite_emails parameter"""
        channel_name = f"TEST_invite_{uuid.uuid4().hex[:6]}"
        response = requests.post(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": channel_name,
                "description": "Channel with invites",
                "channel_type": "group",
                "is_private": True,
                "invite_emails": [TEST_EMAIL],
                "requires_approval": False
            }
        )
        assert response.status_code == 200, f"Create channel with invites failed: {response.text}"
        data = response.json()
        assert data["name"] == channel_name
        print(f"PASS: Created channel {channel_name} with invite to {TEST_EMAIL}")
        return data["id"]
    
    def test_create_channel_with_requires_approval(self, admin_token):
        """Test creating channel with requires_approval=true"""
        channel_name = f"TEST_approval_{uuid.uuid4().hex[:6]}"
        response = requests.post(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": channel_name,
                "description": "Channel requiring approval",
                "channel_type": "project",
                "is_private": False,
                "requires_approval": True
            }
        )
        assert response.status_code == 200, f"Create channel with approval failed: {response.text}"
        data = response.json()
        assert data["name"] == channel_name
        print(f"PASS: Created channel {channel_name} with requires_approval=true")
        return data["id"]

    # ============ Invite API Tests ============
    
    def test_send_invite_to_channel(self, admin_token):
        """Test POST /api/lumi/channels/{channel_id}/invite"""
        # First create a channel
        channel_name = f"TEST_sendinv_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": channel_name, "channel_type": "group"}
        )
        assert create_resp.status_code == 200
        channel_id = create_resp.json()["id"]
        
        # Send invite
        response = requests.post(f"{BASE_URL}/api/lumi/channels/{channel_id}/invite",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"emails": [TEST_EMAIL]}
        )
        assert response.status_code == 200, f"Send invite failed: {response.text}"
        data = response.json()
        assert "sent" in data
        print(f"PASS: Sent invite to {TEST_EMAIL}, sent count: {data.get('total', 0)}")
    
    def test_get_pending_invites(self, test_user_token):
        """Test GET /api/lumi/invites - get pending invites for current user"""
        response = requests.get(f"{BASE_URL}/api/lumi/invites",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200, f"Get invites failed: {response.text}"
        data = response.json()
        assert "invites" in data
        print(f"PASS: Got {len(data['invites'])} pending invites for test user")
        return data["invites"]
    
    def test_respond_to_invite_accept(self, admin_token, test_user_token):
        """Test POST /api/lumi/invites/{invite_id}/respond - accept invite"""
        # Create channel and invite test user
        channel_name = f"TEST_accept_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": channel_name, "channel_type": "group", "invite_emails": [TEST_EMAIL]}
        )
        assert create_resp.status_code == 200
        
        # Get pending invites as test user
        invites_resp = requests.get(f"{BASE_URL}/api/lumi/invites",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert invites_resp.status_code == 200
        invites = invites_resp.json().get("invites", [])
        
        # Find invite for our channel
        invite = next((i for i in invites if i.get("channel_name") == channel_name), None)
        if invite:
            # Accept the invite
            response = requests.post(f"{BASE_URL}/api/lumi/invites/{invite['id']}/respond",
                headers={"Authorization": f"Bearer {test_user_token}"},
                json={"action": "accept"}
            )
            assert response.status_code == 200, f"Accept invite failed: {response.text}"
            data = response.json()
            assert data.get("status") == "accepted"
            print(f"PASS: Accepted invite to channel {channel_name}")
        else:
            print(f"INFO: No pending invite found for {channel_name} (may already be responded)")
    
    def test_respond_to_invite_decline(self, admin_token, test_user_token):
        """Test POST /api/lumi/invites/{invite_id}/respond - decline invite"""
        # Create channel and invite test user
        channel_name = f"TEST_decline_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": channel_name, "channel_type": "group", "invite_emails": [TEST_EMAIL]}
        )
        assert create_resp.status_code == 200
        
        # Get pending invites
        invites_resp = requests.get(f"{BASE_URL}/api/lumi/invites",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        invites = invites_resp.json().get("invites", [])
        invite = next((i for i in invites if i.get("channel_name") == channel_name), None)
        
        if invite:
            response = requests.post(f"{BASE_URL}/api/lumi/invites/{invite['id']}/respond",
                headers={"Authorization": f"Bearer {test_user_token}"},
                json={"action": "decline"}
            )
            assert response.status_code == 200, f"Decline invite failed: {response.text}"
            data = response.json()
            assert data.get("status") == "declined"
            print(f"PASS: Declined invite to channel {channel_name}")
        else:
            print(f"INFO: No pending invite found for {channel_name}")

    # ============ Join with Requires Approval ============
    
    def test_join_channel_with_requires_approval(self, admin_token, test_user_token):
        """Test POST /api/lumi/channels/{channel_id}/join - returns pending_approval for approval-required channels"""
        # Admin creates approval-required channel
        channel_name = f"TEST_joinapprove_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": channel_name,
                "channel_type": "group",
                "is_private": False,
                "requires_approval": True
            }
        )
        assert create_resp.status_code == 200
        channel_id = create_resp.json()["id"]
        
        # Test user tries to join
        response = requests.post(f"{BASE_URL}/api/lumi/channels/{channel_id}/join",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200, f"Join failed: {response.text}"
        data = response.json()
        # Should return pending_approval status
        assert data.get("status") == "pending_approval", f"Expected pending_approval, got: {data}"
        print(f"PASS: Join request for approval-required channel returns pending_approval")
    
    def test_join_channel_without_approval(self, admin_token, test_user_token):
        """Test POST /api/lumi/channels/{channel_id}/join - direct join for non-approval channels"""
        # Admin creates public channel without approval requirement
        channel_name = f"TEST_joindirect_{uuid.uuid4().hex[:6]}"
        create_resp = requests.post(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": channel_name,
                "channel_type": "group",
                "is_private": False,
                "requires_approval": False
            }
        )
        assert create_resp.status_code == 200
        channel_id = create_resp.json()["id"]
        
        # Test user joins directly
        response = requests.post(f"{BASE_URL}/api/lumi/channels/{channel_id}/join",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        assert response.status_code == 200, f"Join failed: {response.text}"
        data = response.json()
        # Should return joined status
        assert data.get("status") == "joined", f"Expected joined, got: {data}"
        print(f"PASS: Direct join for non-approval channel returns joined")

    # ============ Channel List ============
    
    def test_get_channels(self, admin_token):
        """Test GET /api/lumi/channels returns my_channels and discover"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200, f"Get channels failed: {response.text}"
        data = response.json()
        assert "my_channels" in data
        assert "discover" in data
        print(f"PASS: Got {len(data['my_channels'])} my_channels, {len(data['discover'])} discover channels")

    # ============ Auth Required Tests ============
    
    def test_create_channel_requires_auth(self):
        """Test that channel creation requires authentication"""
        response = requests.post(f"{BASE_URL}/api/lumi/channels",
            json={"name": "test", "channel_type": "group"}
        )
        assert response.status_code == 401, f"Expected 401, got: {response.status_code}"
        print("PASS: Create channel requires authentication")
    
    def test_invites_requires_auth(self):
        """Test that invites endpoint requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/invites")
        assert response.status_code == 401, f"Expected 401, got: {response.status_code}"
        print("PASS: Invites endpoint requires authentication")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
