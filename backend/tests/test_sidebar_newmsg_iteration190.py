"""
Test ENZI Sidebar restructure, New Message panel, and invite APIs (Iteration 190)
Features tested:
- GET /api/lumi/invite/link - returns invite_url, sms_text, linkedin_url
- GET /api/lumi/domain/colleagues - domain discovery  
- GET /api/lumi/invite/history - invite history
- GET /api/lumi/users/search - user search for New Message panel
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestENZISidebarAPIs:
    """Tests for ENZI sidebar restructure backend APIs"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, "No access_token in login response"
        return data["access_token"]
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers for requests"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    # Invite Link API Tests
    def test_get_invite_link(self, headers):
        """GET /api/lumi/invite/link - returns invite URL with share texts"""
        response = requests.get(f"{BASE_URL}/api/lumi/invite/link", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Verify all required fields
        assert "invite_url" in data, "Missing invite_url"
        assert "sms_text" in data, "Missing sms_text"
        assert "linkedin_url" in data, "Missing linkedin_url"
        assert "twitter_url" in data, "Missing twitter_url"
        assert "invite_id" in data, "Missing invite_id"
        
        # Verify URL format
        assert data["invite_url"].startswith("http"), f"Invalid invite_url: {data['invite_url']}"
        assert "invite_token=" in data["invite_url"], "invite_url should contain invite_token param"
        
        # Verify SMS text contains invite URL
        assert data["invite_url"] in data["sms_text"], "SMS text should contain invite URL"
        
        print(f"PASS: Invite link generated: {data['invite_id'][:8]}...")
    
    # Domain Colleagues API Tests
    def test_get_domain_colleagues(self, headers):
        """GET /api/lumi/domain/colleagues - domain discovery"""
        response = requests.get(f"{BASE_URL}/api/lumi/domain/colleagues", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        # Should have colleagues list and domain info
        assert "colleagues" in data, "Missing colleagues field"
        assert "domain" in data, "Missing domain field"
        assert "is_company_domain" in data, "Missing is_company_domain field"
        
        # medmatch.com is a company domain
        print(f"PASS: Domain colleagues returned - domain: {data['domain']}, is_company: {data['is_company_domain']}, count: {len(data.get('colleagues', []))}")
    
    def test_get_domain_colleagues_with_search(self, headers):
        """GET /api/lumi/domain/colleagues?q=test - search colleagues"""
        response = requests.get(f"{BASE_URL}/api/lumi/domain/colleagues?q=test", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "colleagues" in data
        print(f"PASS: Domain search returned {len(data.get('colleagues', []))} results")
    
    # Invite History API Tests
    def test_get_invite_history(self, headers):
        """GET /api/lumi/invite/history - returns invite history"""
        response = requests.get(f"{BASE_URL}/api/lumi/invite/history", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "invites" in data, "Missing invites field"
        assert "count" in data, "Missing count field"
        assert isinstance(data["invites"], list), "invites should be a list"
        
        # Verify history items structure if any exist
        if len(data["invites"]) > 0:
            inv = data["invites"][0]
            assert "id" in inv or "invited_email" in inv or "type" in inv, "Invite item should have id/email/type"
        
        print(f"PASS: Invite history returned {data['count']} invites")
    
    # User Search API Tests (for New Message panel)
    def test_user_search_by_name(self, headers):
        """GET /api/lumi/users/search?q=recruiter - search users by name"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=recruiter", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "users" in data, "Missing users field"
        assert isinstance(data["users"], list), "users should be a list"
        
        print(f"PASS: User search 'recruiter' returned {len(data['users'])} users")
    
    def test_user_search_by_email(self, headers):
        """GET /api/lumi/users/search?q=test - search users by email"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=test", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "users" in data
        print(f"PASS: User search 'test' returned {len(data['users'])} users")
    
    def test_user_search_unknown(self, headers):
        """GET /api/lumi/users/search?q=unknown@test.com - no results triggers invite fallback"""
        response = requests.get(f"{BASE_URL}/api/lumi/users/search?q=unknown_xyz_123@test.com", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "users" in data
        # Expect empty or very few results for unknown user
        print(f"PASS: Unknown user search returned {len(data['users'])} users (0 expected, triggers invite fallback)")
    
    # Channels API (for sidebar Recent view)
    def test_get_channels(self, headers):
        """GET /api/lumi/channels - for Recent view showing channels"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "my_channels" in data or "channels" in data, "Should have channels"
        
        channels = data.get("my_channels", data.get("channels", []))
        print(f"PASS: Channels returned {len(channels)} channels")
    
    # DM API (for sidebar Recent view)
    def test_get_dms(self, headers):
        """GET /api/lumi/dm - for Recent view showing DMs"""
        response = requests.get(f"{BASE_URL}/api/lumi/dm", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "dms" in data, "Should have dms"
        
        print(f"PASS: DMs returned {len(data.get('dms', []))} conversations")
    
    # Bucket counts (for Smart Buckets in sidebar)
    def test_get_bucket_counts(self, headers):
        """GET /api/lumi/buckets/counts - for Smart Buckets in sidebar"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/counts", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "counts" in data, "Should have counts"
        counts = data["counts"]
        
        # Verify expected bucket types
        expected_buckets = ["urgent", "action_required", "meeting_request", "fyi", "social"]
        for bucket in expected_buckets:
            assert bucket in counts, f"Missing bucket count: {bucket}"
        
        print(f"PASS: Bucket counts returned - urgent: {counts.get('urgent', 0)}, action_required: {counts.get('action_required', 0)}")
    
    # Unread counts (for unread badges in sidebar)
    def test_get_unread_counts(self, headers):
        """GET /api/lumi/unread-counts - for unread badges"""
        response = requests.get(f"{BASE_URL}/api/lumi/unread-counts", headers=headers)
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        
        assert "unread" in data, "Should have unread counts"
        
        print(f"PASS: Unread counts returned")


class TestENZIAuthRequired:
    """Verify auth is required for protected endpoints"""
    
    def test_invite_link_requires_auth(self):
        """GET /api/lumi/invite/link without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/lumi/invite/link")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("PASS: Invite link requires auth")
    
    def test_domain_colleagues_requires_auth(self):
        """GET /api/lumi/domain/colleagues without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/lumi/domain/colleagues")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("PASS: Domain colleagues requires auth")
    
    def test_invite_history_requires_auth(self):
        """GET /api/lumi/invite/history without auth should fail"""
        response = requests.get(f"{BASE_URL}/api/lumi/invite/history")
        assert response.status_code in [401, 403], f"Should require auth, got {response.status_code}"
        print("PASS: Invite history requires auth")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
