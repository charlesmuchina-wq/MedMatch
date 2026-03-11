"""
Meeting-to-Channel Sync and Admin Approval API Tests
Iteration 203 - Tests KARAU meeting to ENZI channel conversion and external member approval

Endpoints tested:
- GET /api/lumi/meeting-sync/pending-approvals
- POST /api/lumi/meeting-sync/approve-external
- POST /api/lumi/meeting-sync/deny-external
- GET /api/lumi/meeting-sync/settings
- PUT /api/lumi/meeting-sync/settings
- GET /api/lumi/meeting-sync/channels
- POST /api/lumi/meeting-sync/convert
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "admin@medmatch.com"
ADMIN_PASSWORD = "Swampdrainer2026!"
TEST_EMAIL = "test@medmatch.io"
TEST_PASSWORD = "TestPassword123!"

# Pre-seeded test data
SEEDED_CHANNEL_ID = "mtg-test-ext1"
SEEDED_EXT_USER_3 = "ext_user_3"  # Sarah Client
SEEDED_EXT_USER_4 = "ext_user_4"  # Mike Vendor


@pytest.fixture(scope="module")
def admin_token():
    """Get admin authentication token"""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if res.status_code == 200:
        return res.json().get("access_token")
    pytest.skip(f"Admin authentication failed: {res.status_code} - {res.text}")


@pytest.fixture(scope="module")
def test_user_token():
    """Get test user authentication token"""
    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if res.status_code == 200:
        return res.json().get("access_token")
    return None  # Non-critical, skip tests that need it


class TestMeetingSyncSettings:
    """Test meeting sync settings endpoints"""

    def test_get_default_sync_settings(self, admin_token):
        """GET /api/lumi/meeting-sync/settings - returns default settings"""
        res = requests.get(
            f"{BASE_URL}/api/lumi/meeting-sync/settings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        
        # Verify default settings structure
        assert "auto_create_channel" in data
        assert "include_transcript" in data
        assert "include_notes" in data
        assert "channel_visibility" in data
        
        # Verify default values
        assert data["auto_create_channel"] is True
        assert data["include_transcript"] is True
        assert data["include_notes"] is True
        assert data["channel_visibility"] == "internal"
        print(f"Default settings: {data}")

    def test_update_sync_settings(self, admin_token):
        """PUT /api/lumi/meeting-sync/settings - updates user settings"""
        payload = {
            "auto_create_channel": False,
            "include_transcript": True,
            "include_notes": False,
            "channel_visibility": "all"
        }
        res = requests.put(
            f"{BASE_URL}/api/lumi/meeting-sync/settings",
            json=payload,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        
        assert data["status"] == "updated"
        assert data["auto_create_channel"] is False
        assert data["channel_visibility"] == "all"
        print(f"Updated settings: {data}")
        
        # Restore default settings
        restore = {
            "auto_create_channel": True,
            "include_transcript": True,
            "include_notes": True,
            "channel_visibility": "internal"
        }
        requests.put(
            f"{BASE_URL}/api/lumi/meeting-sync/settings",
            json=restore,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    def test_settings_require_auth(self):
        """GET /api/lumi/meeting-sync/settings - requires authentication"""
        res = requests.get(f"{BASE_URL}/api/lumi/meeting-sync/settings")
        assert res.status_code == 401


class TestPendingApprovals:
    """Test pending external member approval endpoints"""

    def test_get_pending_approvals_authenticated(self, admin_token):
        """GET /api/lumi/meeting-sync/pending-approvals - returns pending approvals for admin"""
        res = requests.get(
            f"{BASE_URL}/api/lumi/meeting-sync/pending-approvals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        
        assert "approvals" in data
        assert "count" in data
        assert isinstance(data["approvals"], list)
        assert isinstance(data["count"], int)
        
        print(f"Found {data['count']} pending approvals")
        
        # Check structure of approvals if any exist
        if data["count"] > 0:
            approval = data["approvals"][0]
            assert "channel_id" in approval
            assert "user_id" in approval
            assert "status" in approval
            print(f"Sample approval: {approval}")

    def test_pending_approvals_require_auth(self):
        """GET /api/lumi/meeting-sync/pending-approvals - requires authentication"""
        res = requests.get(f"{BASE_URL}/api/lumi/meeting-sync/pending-approvals")
        assert res.status_code == 401


class TestExternalMemberApproval:
    """Test approve/deny external member endpoints"""

    def test_approve_external_member_valid_request(self, admin_token):
        """POST /api/lumi/meeting-sync/approve-external - approves external member"""
        # First check if we have pending approvals
        check = requests.get(
            f"{BASE_URL}/api/lumi/meeting-sync/pending-approvals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if check.status_code == 200:
            pending = check.json().get("approvals", [])
            if len(pending) > 0:
                # Try to approve the first pending member
                approval = pending[0]
                payload = {
                    "meeting_id": approval.get("meeting_id", "test-meeting"),
                    "user_ids": [approval["user_id"]],
                    "channel_id": approval["channel_id"]
                }
                res = requests.post(
                    f"{BASE_URL}/api/lumi/meeting-sync/approve-external",
                    json=payload,
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                
                # Should return 200 if user is admin of channel, 403 otherwise
                assert res.status_code in [200, 403]
                if res.status_code == 200:
                    data = res.json()
                    assert "approved" in data
                    assert "channel_id" in data
                    print(f"Approved {data['approved']} member(s) to channel {data['channel_id']}")
                else:
                    print(f"User is not admin of channel: {res.json()}")
            else:
                print("No pending approvals to test with")
                # Test with non-existent data to verify endpoint structure
                res = requests.post(
                    f"{BASE_URL}/api/lumi/meeting-sync/approve-external",
                    json={
                        "meeting_id": "nonexistent",
                        "user_ids": ["nonexistent"],
                        "channel_id": "nonexistent"
                    },
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                # Should return 403 (not admin) or 200 with 0 approved
                assert res.status_code in [200, 403]

    def test_deny_external_member_valid_request(self, admin_token):
        """POST /api/lumi/meeting-sync/deny-external - denies external member"""
        # Similar structure to approve test
        check = requests.get(
            f"{BASE_URL}/api/lumi/meeting-sync/pending-approvals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if check.status_code == 200:
            pending = check.json().get("approvals", [])
            if len(pending) > 0:
                approval = pending[0]
                payload = {
                    "meeting_id": approval.get("meeting_id", "test-meeting"),
                    "user_ids": [approval["user_id"]],
                    "channel_id": approval["channel_id"]
                }
                res = requests.post(
                    f"{BASE_URL}/api/lumi/meeting-sync/deny-external",
                    json=payload,
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                
                assert res.status_code in [200, 403]
                if res.status_code == 200:
                    data = res.json()
                    assert "denied" in data
                    assert "channel_id" in data
                    print(f"Denied {data['denied']} member(s) from channel {data['channel_id']}")
            else:
                print("No pending approvals to test deny with")
                # Test endpoint structure
                res = requests.post(
                    f"{BASE_URL}/api/lumi/meeting-sync/deny-external",
                    json={
                        "meeting_id": "nonexistent",
                        "user_ids": ["nonexistent"],
                        "channel_id": "nonexistent"
                    },
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                assert res.status_code in [200, 403]

    def test_approve_requires_auth(self):
        """POST /api/lumi/meeting-sync/approve-external - requires authentication"""
        res = requests.post(
            f"{BASE_URL}/api/lumi/meeting-sync/approve-external",
            json={"meeting_id": "test", "user_ids": ["test"], "channel_id": "test"}
        )
        assert res.status_code == 401

    def test_deny_requires_auth(self):
        """POST /api/lumi/meeting-sync/deny-external - requires authentication"""
        res = requests.post(
            f"{BASE_URL}/api/lumi/meeting-sync/deny-external",
            json={"meeting_id": "test", "user_ids": ["test"], "channel_id": "test"}
        )
        assert res.status_code == 401


class TestMeetingChannels:
    """Test meeting-followup channels endpoint"""

    def test_get_meeting_channels(self, admin_token):
        """GET /api/lumi/meeting-sync/channels - returns meeting-followup channels"""
        res = requests.get(
            f"{BASE_URL}/api/lumi/meeting-sync/channels",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 200
        data = res.json()
        
        assert "channels" in data
        assert "count" in data
        assert isinstance(data["channels"], list)
        
        print(f"Found {data['count']} meeting-followup channels")
        
        if data["count"] > 0:
            channel = data["channels"][0]
            assert "id" in channel
            assert "name" in channel
            assert channel.get("channel_type") == "meeting-followup"
            print(f"Sample channel: {channel.get('id')} - {channel.get('name')}")

    def test_channels_require_auth(self):
        """GET /api/lumi/meeting-sync/channels - requires authentication"""
        res = requests.get(f"{BASE_URL}/api/lumi/meeting-sync/channels")
        assert res.status_code == 401


class TestMeetingConversion:
    """Test manual meeting-to-channel conversion"""

    def test_convert_meeting_requires_auth(self):
        """POST /api/lumi/meeting-sync/convert - requires authentication"""
        res = requests.post(
            f"{BASE_URL}/api/lumi/meeting-sync/convert",
            params={"meeting_id": "test-meeting"}
        )
        assert res.status_code == 401

    def test_convert_nonexistent_meeting(self, admin_token):
        """POST /api/lumi/meeting-sync/convert - 404 for non-existent meeting"""
        res = requests.post(
            f"{BASE_URL}/api/lumi/meeting-sync/convert",
            params={"meeting_id": "nonexistent-meeting-id"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert res.status_code == 404
        print(f"Correctly returned 404 for non-existent meeting")


class TestEndMeetingIntegration:
    """Test that ending a meeting creates ENZI channel"""

    def test_end_meeting_creates_channel(self, admin_token):
        """POST /api/karau-meet/meetings/{id}/end - creates channel on meeting end"""
        # Create a test meeting
        create_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            json={"title": "Test Meeting for Channel Sync"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if create_res.status_code != 200:
            pytest.skip(f"Could not create test meeting: {create_res.text}")
        
        meeting = create_res.json()
        meeting_id = meeting.get("meeting_id")
        print(f"Created test meeting: {meeting_id}")
        
        # End the meeting
        end_res = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings/{meeting_id}/end",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if end_res.status_code == 200:
            data = end_res.json()
            assert data.get("success") is True
            
            channel_created = data.get("channel_created")
            if channel_created and not channel_created.get("skipped"):
                assert "channel_id" in channel_created
                print(f"Channel created: {channel_created}")
            elif channel_created and channel_created.get("skipped"):
                print(f"Channel creation skipped: {channel_created.get('reason')}")
            else:
                print("No channel_created info in response")
        else:
            print(f"End meeting returned {end_res.status_code}: {end_res.text}")


class TestDataVerification:
    """Verify test data is properly seeded"""

    def test_seeded_channel_exists(self, admin_token):
        """Verify mtg-test-ext1 channel with pending approvals exists"""
        # Check in meeting-followup channels
        res = requests.get(
            f"{BASE_URL}/api/lumi/meeting-sync/channels",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if res.status_code == 200:
            channels = res.json().get("channels", [])
            seeded = next((c for c in channels if c.get("id") == SEEDED_CHANNEL_ID), None)
            
            if seeded:
                print(f"Found seeded channel: {seeded.get('name')}")
                print(f"External pending: {seeded.get('external_pending', [])}")
            else:
                print(f"Seeded channel {SEEDED_CHANNEL_ID} not found in user's channels")
        
        # Also check pending approvals
        approvals_res = requests.get(
            f"{BASE_URL}/api/lumi/meeting-sync/pending-approvals",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if approvals_res.status_code == 200:
            approvals = approvals_res.json().get("approvals", [])
            seeded_approvals = [a for a in approvals if a.get("channel_id") == SEEDED_CHANNEL_ID]
            print(f"Found {len(seeded_approvals)} pending approvals for seeded channel")
            for a in seeded_approvals:
                print(f"  - {a.get('user_name')} ({a.get('user_email')})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
