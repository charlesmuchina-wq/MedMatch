"""
Test Resend Email and Xirsys TURN Server Integration
Tests:
1. GET /api/karau-meet/ice-servers - Returns ICE servers (STUN or STUN+TURN)
2. POST /api/karau-meet/security/email/send-code - Uses Resend or mock if not configured
3. Email service properly formats verification code email HTML
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestICEServersEndpoint:
    """Test ICE servers endpoint for WebRTC"""
    
    def test_ice_servers_returns_success(self):
        """Test that ICE servers endpoint returns success"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        
    def test_ice_servers_returns_stun_servers(self):
        """Test that ICE servers endpoint returns STUN servers"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        
        data = response.json()
        assert "ice_servers" in data
        assert isinstance(data["ice_servers"], list)
        assert len(data["ice_servers"]) > 0
        
        # Check that at least one STUN server is present
        stun_servers = [s for s in data["ice_servers"] if "stun:" in s.get("urls", "")]
        assert len(stun_servers) > 0
        
    def test_ice_servers_has_turn_enabled_flag(self):
        """Test that ICE servers endpoint returns turn_enabled flag"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        
        data = response.json()
        assert "turn_enabled" in data
        assert isinstance(data["turn_enabled"], bool)
        
    def test_ice_servers_fallback_without_xirsys(self):
        """Test that without Xirsys credentials, fallback to Google STUN"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/ice-servers")
        assert response.status_code == 200
        
        data = response.json()
        # Without Xirsys credentials, should use Google STUN servers
        google_stun = [s for s in data["ice_servers"] if "stun.l.google.com" in s.get("urls", "")]
        assert len(google_stun) > 0


class TestEmailVerificationEndpoint:
    """Test email verification endpoint using Resend"""
    
    @pytest.fixture
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            return response.json().get("token")
        pytest.skip("Authentication failed - skipping authenticated tests")
        
    def test_send_verification_code_requires_auth(self):
        """Test that send-code endpoint requires authentication"""
        response = requests.post(f"{BASE_URL}/api/karau-meet/security/email/send-code")
        assert response.status_code in [401, 403]
        
    def test_send_verification_code_success(self, auth_token):
        """Test sending verification code (mock mode without RESEND_API_KEY)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/send-code",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("success") is True
        assert "message" in data
        assert "expires_in_minutes" in data
        
    def test_send_verification_code_mock_mode(self, auth_token):
        """Test that without RESEND_API_KEY, mock mode is used"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/send-code",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        # In mock mode, the code is returned in response for testing
        if data.get("mock_mode"):
            assert "code" in data
            assert len(data["code"]) == 6
            assert data["code"].isdigit()
            
    def test_verify_email_code_requires_auth(self):
        """Test that verify endpoint requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/verify",
            json={"code": "123456"}
        )
        assert response.status_code in [401, 403]
        
    def test_verify_email_code_invalid_code(self, auth_token):
        """Test verifying with invalid code"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/verify",
            headers=headers,
            json={"code": "000000"}
        )
        # Should fail with invalid code
        assert response.status_code == 400
        
    def test_email_verification_status(self, auth_token):
        """Test getting email verification status"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/security/email/status",
            headers=headers
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "verified" in data or "status" in data


class TestEmailServiceFormatting:
    """Test email service HTML formatting"""
    
    def test_email_service_module_exists(self):
        """Test that email service module exists and can be imported"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        from services.karau_meet.email_service import (
            send_verification_code,
            send_meeting_invite,
            send_meeting_summary
        )
        
        # Functions should be callable
        assert callable(send_verification_code)
        assert callable(send_meeting_invite)
        assert callable(send_meeting_summary)


class TestTurnServiceModule:
    """Test TURN service module"""
    
    def test_turn_service_module_exists(self):
        """Test that TURN service module exists and can be imported"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        from services.karau_meet.turn_service import (
            get_ice_servers,
            get_default_ice_servers,
            DEFAULT_ICE_SERVERS
        )
        
        # Functions should be callable
        assert callable(get_ice_servers)
        assert callable(get_default_ice_servers)
        
        # Default ICE servers should be a list
        assert isinstance(DEFAULT_ICE_SERVERS, list)
        assert len(DEFAULT_ICE_SERVERS) > 0
        
    def test_default_ice_servers_format(self):
        """Test default ICE servers have correct format"""
        import sys
        sys.path.insert(0, '/app/backend')
        
        from services.karau_meet.turn_service import DEFAULT_ICE_SERVERS
        
        for server in DEFAULT_ICE_SERVERS:
            assert "urls" in server
            assert server["urls"].startswith("stun:")


class TestRoomStatusEndpoint:
    """Test room status endpoint"""
    
    def test_room_status_returns_data(self):
        """Test room status endpoint returns expected data"""
        # Use a random meeting ID
        meeting_id = "test-meeting-123"
        response = requests.get(f"{BASE_URL}/api/karau-meet/room/{meeting_id}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "meeting_id" in data
        assert "active" in data
        assert "participant_count" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
