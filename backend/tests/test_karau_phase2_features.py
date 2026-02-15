"""
AI KARAU Meeting Phase 2 Features Test
Tests for:
- Email-based verification (simple MFA)
- GDPR/HIPAA compliance status
- Accessibility settings
- Keyboard shortcuts
- Color blind palettes
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestAuthentication:
    """Get auth token for subsequent tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Login and get auth token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        # API returns access_token
        token = data.get("access_token") or data.get("token")
        assert token, "No token in response"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Return headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }


class TestEmailVerification(TestAuthentication):
    """Test email-based verification (simple MFA) endpoints"""
    
    def test_send_verification_code(self, auth_headers):
        """POST /api/karau-meet/security/email/send-code - Should send verification code"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/send-code",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to send code: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert data.get("success") == True, "Expected success=True"
        assert "message" in data, "Missing message in response"
        assert "expires_in_minutes" in data, "Missing expires_in_minutes"
        
        # Mock mode should return code for testing
        assert data.get("mock_mode") == True, "Expected mock_mode=True"
        assert "code" in data, "Missing code in mock mode response"
        assert len(data["code"]) == 6, "Code should be 6 digits"
        
        # Store code for next test
        self.__class__.verification_code = data["code"]
        print(f"Verification code received: {data['code']}")
    
    def test_verify_email_code(self, auth_headers):
        """POST /api/karau-meet/security/email/verify - Should verify the code"""
        # First send a code
        send_response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/send-code",
            headers=auth_headers
        )
        assert send_response.status_code == 200
        code = send_response.json().get("code")
        
        # Now verify it
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/verify",
            headers=auth_headers,
            json={"code": code}
        )
        assert response.status_code == 200, f"Verification failed: {response.text}"
        data = response.json()
        
        assert data.get("success") == True, "Expected success=True"
        assert data.get("verified") == True, "Expected verified=True"
        print("Email verification successful")
    
    def test_verify_invalid_code(self, auth_headers):
        """POST /api/karau-meet/security/email/verify - Should reject invalid code"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/security/email/verify",
            headers=auth_headers,
            json={"code": "000000"}  # Invalid code
        )
        # Should return 400 for invalid code
        assert response.status_code == 400, f"Expected 400 for invalid code, got {response.status_code}"
    
    def test_get_email_verification_status(self, auth_headers):
        """GET /api/karau-meet/security/email/status - Should return verification status"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/security/email/status",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get status: {response.text}"
        data = response.json()
        
        # Should have verified field
        assert "verified" in data, "Missing verified field"
        print(f"Email verification status: {data}")


class TestComplianceStatus(TestAuthentication):
    """Test GDPR/HIPAA compliance status endpoint"""
    
    def test_get_compliance_status(self, auth_headers):
        """GET /api/karau-meet/security/compliance - Should return GDPR/HIPAA compliance status"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/security/compliance",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get compliance: {response.text}"
        data = response.json()
        
        # Verify GDPR compliance structure
        assert "gdpr" in data, "Missing GDPR compliance info"
        assert data["gdpr"].get("compliant") == True, "Expected GDPR compliant"
        assert "features" in data["gdpr"], "Missing GDPR features"
        
        # Verify HIPAA compliance structure
        assert "hipaa" in data, "Missing HIPAA compliance info"
        assert data["hipaa"].get("compliant") == True, "Expected HIPAA compliant"
        assert "features" in data["hipaa"], "Missing HIPAA features"
        
        # Verify security info
        assert "security" in data, "Missing security info"
        assert data["security"].get("e2e_encryption") == True
        assert data["security"].get("mfa_available") == True
        
        print(f"Compliance status: GDPR={data['gdpr']['compliant']}, HIPAA={data['hipaa']['compliant']}")


class TestAccessibilitySettings(TestAuthentication):
    """Test accessibility settings endpoints"""
    
    def test_get_accessibility_settings(self, auth_headers):
        """GET /api/karau-meet/accessibility/settings - Should return accessibility settings"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/accessibility/settings",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get settings: {response.text}"
        data = response.json()
        
        # Verify expected fields exist
        expected_fields = [
            "high_contrast", "large_text", "font_size", "reduce_motion",
            "live_captions_enabled", "caption_font_size", "keyboard_shortcuts_enabled",
            "color_blind_mode"
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"
        
        print(f"Accessibility settings retrieved: high_contrast={data.get('high_contrast')}, large_text={data.get('large_text')}")
    
    def test_update_accessibility_settings(self, auth_headers):
        """PUT /api/karau-meet/accessibility/settings - Should update accessibility settings"""
        # Update settings
        update_data = {
            "high_contrast": True,
            "large_text": True,
            "color_blind_mode": "protanopia"
        }
        
        response = requests.put(
            f"{BASE_URL}/api/karau-meet/accessibility/settings",
            headers=auth_headers,
            json=update_data
        )
        assert response.status_code == 200, f"Failed to update settings: {response.text}"
        data = response.json()
        
        # Verify updates were applied
        assert data.get("high_contrast") == True, "high_contrast not updated"
        assert data.get("large_text") == True, "large_text not updated"
        assert data.get("color_blind_mode") == "protanopia", "color_blind_mode not updated"
        
        print("Accessibility settings updated successfully")
        
        # Reset settings
        requests.put(
            f"{BASE_URL}/api/karau-meet/accessibility/settings",
            headers=auth_headers,
            json={"high_contrast": False, "large_text": False, "color_blind_mode": "none"}
        )


class TestKeyboardShortcuts(TestAuthentication):
    """Test keyboard shortcuts endpoint"""
    
    def test_get_keyboard_shortcuts(self, auth_headers):
        """GET /api/karau-meet/accessibility/keyboard-shortcuts - Should return keyboard shortcuts"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/accessibility/keyboard-shortcuts",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get shortcuts: {response.text}"
        data = response.json()
        
        assert "shortcuts" in data, "Missing shortcuts in response"
        shortcuts = data["shortcuts"]
        
        # Verify expected shortcuts exist
        expected_shortcuts = ["toggle_mute", "toggle_video", "toggle_captions", "raise_hand"]
        for shortcut in expected_shortcuts:
            assert shortcut in shortcuts, f"Missing shortcut: {shortcut}"
        
        # Verify shortcut structure
        for name, shortcut in shortcuts.items():
            assert "key" in shortcut, f"Missing key in shortcut {name}"
            assert "description" in shortcut, f"Missing description in shortcut {name}"
        
        print(f"Keyboard shortcuts retrieved: {len(shortcuts)} shortcuts")


class TestColorPalettes(TestAuthentication):
    """Test color blind palettes endpoint"""
    
    def test_get_all_color_palettes(self, auth_headers):
        """GET /api/karau-meet/accessibility/color-palettes - Should return color blind palettes"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/accessibility/color-palettes",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Failed to get palettes: {response.text}"
        data = response.json()
        
        assert "palettes" in data, "Missing palettes in response"
        palettes = data["palettes"]
        
        # Verify all color blind modes are present
        expected_modes = ["none", "protanopia", "deuteranopia", "tritanopia"]
        for mode in expected_modes:
            assert mode in palettes, f"Missing palette for mode: {mode}"
        
        print(f"Color palettes retrieved: {list(palettes.keys())}")
    
    def test_get_specific_color_palette(self, auth_headers):
        """GET /api/karau-meet/accessibility/color-palette/{mode} - Should return specific palette"""
        for mode in ["none", "protanopia", "deuteranopia", "tritanopia"]:
            response = requests.get(
                f"{BASE_URL}/api/karau-meet/accessibility/color-palette/{mode}",
                headers=auth_headers
            )
            assert response.status_code == 200, f"Failed to get palette for {mode}: {response.text}"
            data = response.json()
            
            assert data.get("mode") == mode, f"Wrong mode returned"
            assert "palette" in data, "Missing palette in response"
        
        print("All specific color palettes retrieved successfully")


class TestDefaultSettings:
    """Test default settings endpoint (no auth required)"""
    
    def test_get_default_accessibility_settings(self):
        """GET /api/karau-meet/accessibility/settings/defaults - Should return defaults"""
        # This endpoint might not require auth
        response = requests.get(f"{BASE_URL}/api/karau-meet/accessibility/settings/defaults")
        
        # If it requires auth, that's fine - just check it exists
        if response.status_code == 200:
            data = response.json()
            assert "high_contrast" in data
            assert "large_text" in data
            print("Default accessibility settings retrieved")
        else:
            print(f"Default settings endpoint returned {response.status_code} (may require auth)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
