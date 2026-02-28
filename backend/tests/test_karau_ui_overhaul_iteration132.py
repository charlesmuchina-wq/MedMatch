"""
Test suite for KARAU Meeting Portal UI Overhaul - Iteration 132
Tests: Dashboard redesign, collapsible meetings, floating AI Avatar, color scheme changes
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestKarauUIOverhaulBackend:
    """Backend API tests for UI Overhaul features"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for authenticated requests"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    # Templates API tests
    def test_templates_endpoint_returns_templates(self):
        """GET /api/karau-features/templates returns list of templates"""
        response = requests.get(f"{BASE_URL}/api/karau-features/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert len(data["templates"]) >= 6, "Should have at least 6 templates"
    
    def test_templates_have_required_fields(self):
        """Templates should have template_id, name, industry fields"""
        response = requests.get(f"{BASE_URL}/api/karau-features/templates")
        data = response.json()
        for template in data["templates"]:
            assert "template_id" in template
            assert "name" in template
            assert "industry" in template
    
    # AI Assistant API tests (for floating avatar)
    def test_ai_assistant_requires_auth(self):
        """POST /api/karau-features/ai-assistant/ask requires authentication"""
        response = requests.post(f"{BASE_URL}/api/karau-features/ai-assistant/ask", json={
            "meeting_id": "general",
            "question": "Hello"
        })
        assert response.status_code in [401, 403], "Should require authentication"
    
    def test_ai_assistant_general_context(self, auth_token):
        """POST /api/karau-features/ai-assistant/ask works with general meeting_id"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/ai-assistant/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"meeting_id": "general", "question": "What is KARAU?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data, "Response should have answer field"
        assert len(data["answer"]) > 0, "Answer should not be empty"
    
    def test_ai_assistant_returns_suggestions(self, auth_token):
        """AI Assistant returns follow_up_suggestions"""
        response = requests.post(
            f"{BASE_URL}/api/karau-features/ai-assistant/ask",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"meeting_id": "general", "question": "Tell me about meeting features"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "follow_up_suggestions" in data, "Should have follow_up_suggestions"
    
    # Meeting creation (used by dashboard)
    def test_create_meeting_for_ui(self, auth_token):
        """POST /api/karau-meet/meetings creates meeting from dashboard"""
        response = requests.post(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"title": "TEST_UI_Overhaul_Meeting"}
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert "meeting_id" in data
        # Clean up
        meeting_id = data["meeting_id"]
        return meeting_id
    
    def test_get_meetings_list(self, auth_token):
        """GET /api/karau-meet/meetings returns list for dashboard"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/meetings",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "meetings" in data
    
    # Languages API (for multi-language badge)
    def test_languages_endpoint(self):
        """GET /api/karau-features/languages returns supported languages"""
        response = requests.get(f"{BASE_URL}/api/karau-features/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) >= 14, "Should support at least 14 languages"


class TestHealthAndBasicEndpoints:
    """Basic health check tests"""
    
    def test_api_health(self):
        """API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
    
    def test_karau_root_returns_info(self):
        """Root endpoint returns API info"""
        response = requests.get(f"{BASE_URL}/api")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
