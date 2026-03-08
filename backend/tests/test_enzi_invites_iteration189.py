"""
ENZI Invite System Tests - Iteration 189
Tests for:
- POST /api/lumi/invite/send - Send email invitations
- GET /api/lumi/invite/link - Generate shareable invite links
- GET /api/lumi/invite/validate/<token> - Validate invite tokens
- POST /api/lumi/invite/register - Register via invite token
- GET /api/lumi/domain/colleagues - Domain-based company discovery
- GET /api/lumi/invite/history - Invite history
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture(scope="module")
def admin_token(api_client):
    """Get admin authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "admin@medmatch.com",
        "password": "Swampdrainer2026!"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Admin authentication failed - skipping tests")

@pytest.fixture(scope="module")
def test_user_token(api_client):
    """Get test user authentication token"""
    response = api_client.post(f"{BASE_URL}/api/auth/login", json={
        "email": "test@medmatch.io",
        "password": "TestPassword123!"
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    pytest.skip("Test user authentication failed - skipping tests")

class TestHealthCheck:
    """Verify API is accessible before running tests"""
    
    def test_api_health(self, api_client):
        """Test API health endpoint"""
        response = api_client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        print("API health check passed")


class TestInviteSendAPI:
    """Tests for POST /api/lumi/invite/send"""
    
    def test_send_invite_requires_auth(self, api_client):
        """Test that sending invites requires authentication"""
        response = api_client.post(f"{BASE_URL}/api/lumi/invite/send", json={
            "emails": ["test@example.com"]
        })
        assert response.status_code == 401
        print("Invite send correctly requires authentication")
    
    def test_send_single_invite(self, api_client, admin_token):
        """Test sending a single invite"""
        unique_email = f"test_invite_{uuid.uuid4().hex[:8]}@example.com"
        response = api_client.post(
            f"{BASE_URL}/api/lumi/invite/send",
            json={"emails": [unique_email], "message": "Join us on ENZI!"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["email"] == unique_email
        assert result["status"] == "invited"
        assert "invite_id" in result
        print(f"Single invite sent successfully: {result}")
    
    def test_send_multiple_invites(self, api_client, admin_token):
        """Test sending multiple invites at once"""
        emails = [
            f"multi_test1_{uuid.uuid4().hex[:8]}@example.com",
            f"multi_test2_{uuid.uuid4().hex[:8]}@example.com"
        ]
        response = api_client.post(
            f"{BASE_URL}/api/lumi/invite/send",
            json={"emails": emails},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2
        assert data["count"] == 2
        print(f"Multiple invites sent: {data['count']} invites")
    
    def test_invite_already_registered_user(self, api_client, admin_token):
        """Test inviting an already registered user"""
        # test@medmatch.io is a known registered user
        response = api_client.post(
            f"{BASE_URL}/api/lumi/invite/send",
            json={"emails": ["test@medmatch.io"]},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        result = data["results"][0]
        assert result["status"] == "already_registered"
        assert result["email_sent"] == False
        print("Already registered user handled correctly")


class TestInviteLinkAPI:
    """Tests for GET /api/lumi/invite/link"""
    
    def test_generate_link_requires_auth(self):
        """Test that generating link requires authentication"""
        # Use fresh session to avoid cached credentials
        response = requests.get(f"{BASE_URL}/api/lumi/invite/link")
        assert response.status_code == 401
        print("Invite link correctly requires authentication")
    
    def test_generate_invite_link(self, api_client, admin_token):
        """Test generating a shareable invite link"""
        response = api_client.get(
            f"{BASE_URL}/api/lumi/invite/link",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "invite_url" in data
        assert "invite_id" in data
        assert "sms_text" in data
        assert "linkedin_url" in data
        assert "twitter_url" in data
        
        # Verify URL format
        assert "/lumi?invite_token=" in data["invite_url"]
        assert "linkedin.com" in data["linkedin_url"]
        assert "twitter.com" in data["twitter_url"]
        
        print(f"Invite link generated: {data['invite_url']}")
        return data["invite_id"]


class TestInviteValidateAPI:
    """Tests for GET /api/lumi/invite/validate/<token>"""
    
    def test_validate_invalid_token(self, api_client):
        """Test validating an invalid token returns 404"""
        response = api_client.get(f"{BASE_URL}/api/lumi/invite/validate/invalid-token-12345")
        assert response.status_code == 404
        print("Invalid token correctly returns 404")
    
    def test_validate_valid_token(self, api_client, admin_token):
        """Test validating a valid token"""
        # First generate a new invite link
        link_response = api_client.get(
            f"{BASE_URL}/api/lumi/invite/link",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert link_response.status_code == 200
        invite_id = link_response.json()["invite_id"]
        
        # Now validate the token
        response = api_client.get(f"{BASE_URL}/api/lumi/invite/validate/{invite_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] == True
        assert "invite" in data
        assert data["invite"]["id"] == invite_id
        assert "invited_by_name" in data["invite"]
        print(f"Valid token validated: {data}")


class TestInviteRegisterAPI:
    """Tests for POST /api/lumi/invite/register"""
    
    def test_register_with_invalid_token(self, api_client):
        """Test registration with invalid token"""
        response = api_client.post(
            f"{BASE_URL}/api/lumi/invite/register",
            json={
                "invite_token": "invalid-token-xyz",
                "name": "Test User",
                "email": "test@test.com",
                "password": "password123"
            }
        )
        assert response.status_code == 404
        print("Invalid token registration correctly rejected")
    
    def test_register_with_valid_token(self, api_client, admin_token):
        """Test registration with valid invite token"""
        # First generate a new invite link
        link_response = api_client.get(
            f"{BASE_URL}/api/lumi/invite/link",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert link_response.status_code == 200
        invite_id = link_response.json()["invite_id"]
        
        # Register with the invite token
        unique_email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
        response = api_client.post(
            f"{BASE_URL}/api/lumi/invite/register",
            json={
                "invite_token": invite_id,
                "name": "New Invited User",
                "email": unique_email,
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["email"] == unique_email.lower()
        assert data["user"]["name"] == "New Invited User"
        print(f"User registered via invite: {data['user']['email']}")
    
    def test_register_with_used_token(self, api_client, admin_token):
        """Test that already-used tokens are rejected"""
        # Generate and use a token
        link_response = api_client.get(
            f"{BASE_URL}/api/lumi/invite/link",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        invite_id = link_response.json()["invite_id"]
        
        # First registration
        unique_email1 = f"first_user_{uuid.uuid4().hex[:8]}@example.com"
        api_client.post(
            f"{BASE_URL}/api/lumi/invite/register",
            json={
                "invite_token": invite_id,
                "name": "First User",
                "email": unique_email1,
                "password": "SecurePass123!"
            }
        )
        
        # Second registration with same token
        unique_email2 = f"second_user_{uuid.uuid4().hex[:8]}@example.com"
        response = api_client.post(
            f"{BASE_URL}/api/lumi/invite/register",
            json={
                "invite_token": invite_id,
                "name": "Second User",
                "email": unique_email2,
                "password": "SecurePass123!"
            }
        )
        assert response.status_code == 400
        print("Used token correctly rejected for second registration")


class TestInviteHistoryAPI:
    """Tests for GET /api/lumi/invite/history"""
    
    def test_history_requires_auth(self):
        """Test that history requires authentication"""
        # Use fresh session to avoid cached credentials
        response = requests.get(f"{BASE_URL}/api/lumi/invite/history")
        assert response.status_code == 401
        print("Invite history correctly requires authentication")
    
    def test_get_invite_history(self, api_client, admin_token):
        """Test getting invite history"""
        response = api_client.get(
            f"{BASE_URL}/api/lumi/invite/history",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "invites" in data
        assert "count" in data
        assert isinstance(data["invites"], list)
        print(f"Invite history retrieved: {data['count']} invites")


class TestDomainColleaguesAPI:
    """Tests for GET /api/lumi/domain/colleagues"""
    
    def test_colleagues_requires_auth(self):
        """Test that domain colleagues requires authentication"""
        # Use fresh session to avoid cached credentials
        response = requests.get(f"{BASE_URL}/api/lumi/domain/colleagues")
        assert response.status_code == 401
        print("Domain colleagues correctly requires authentication")
    
    def test_get_domain_colleagues(self, api_client, admin_token):
        """Test getting colleagues from the same domain"""
        response = api_client.get(
            f"{BASE_URL}/api/lumi/domain/colleagues",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "colleagues" in data
        assert "domain" in data
        assert "is_company_domain" in data
        
        # medmatch.com is in FREE_DOMAINS so should not be a company domain
        if not data["is_company_domain"]:
            assert "message" in data
            print(f"Free domain detected: {data['domain']}")
        else:
            print(f"Company domain: {data['domain']} with {len(data['colleagues'])} colleagues")


class TestDomainInfoAPI:
    """Tests for GET /api/lumi/domain/info"""
    
    def test_domain_info_requires_auth(self):
        """Test that domain info requires authentication"""
        # Use fresh session to avoid cached credentials
        response = requests.get(f"{BASE_URL}/api/lumi/domain/info")
        assert response.status_code == 401
        print("Domain info correctly requires authentication")
    
    def test_get_domain_info(self, api_client, admin_token):
        """Test getting domain information"""
        response = api_client.get(
            f"{BASE_URL}/api/lumi/domain/info",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "domain" in data
        assert "is_company_domain" in data
        print(f"Domain info: {data}")


class TestENZIBranding:
    """Tests to ensure ENZI branding is properly applied"""
    
    def test_invite_email_contains_enzi(self, api_client, admin_token):
        """Test that invite functionality references ENZI"""
        # Generate an invite link
        response = api_client.get(
            f"{BASE_URL}/api/lumi/invite/link",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # The SMS text should mention ENZI
        assert "ENZI" in data["sms_text"]
        print(f"Invite SMS text contains ENZI: {data['sms_text']}")
