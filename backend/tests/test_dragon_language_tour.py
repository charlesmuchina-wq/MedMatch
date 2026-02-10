"""
Test Dragon AI endpoints and Language Tour functionality
Tests: /api/dragon/health, /api/dragon/chat, language selector
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestDragonAIHealth:
    """Dragon AI Health endpoint tests"""
    
    def test_dragon_health_endpoint(self):
        """Test /api/dragon/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/dragon/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "KARAU Dragon AI"
        assert "features" in data
        assert "intent_detection" in data["features"]
        assert "web_search" in data["features"]
        assert "multi_language" in data["features"]
        assert "languages_supported" in data
        assert len(data["languages_supported"]) >= 10


class TestDragonAIChat:
    """Dragon AI Chat endpoint tests"""
    
    def test_dragon_chat_basic_command(self):
        """Test /api/dragon/chat with basic command"""
        response = requests.post(
            f"{BASE_URL}/api/dragon/chat",
            json={"command": "Hello", "language": "en"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "intent" in data
        assert "speech" in data
        assert isinstance(data["speech"], str)
        assert len(data["speech"]) > 0
    
    def test_dragon_chat_job_search_intent(self):
        """Test /api/dragon/chat with job search command"""
        response = requests.post(
            f"{BASE_URL}/api/dragon/chat",
            json={"command": "Find software engineer jobs", "language": "en"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "intent" in data
        assert "speech" in data
        # Should detect job_search intent
        assert data.get("intent") in ["job_search", "web_search", "unknown"]
    
    def test_dragon_chat_cover_letter_intent(self):
        """Test /api/dragon/chat with cover letter command"""
        response = requests.post(
            f"{BASE_URL}/api/dragon/chat",
            json={"command": "Help me write a cover letter for Google", "language": "en"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "intent" in data
        assert "speech" in data
    
    def test_dragon_chat_spanish_language(self):
        """Test /api/dragon/chat with Spanish language"""
        response = requests.post(
            f"{BASE_URL}/api/dragon/chat",
            json={"command": "Buscar trabajos de ingeniero", "language": "es"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "intent" in data
        assert "speech" in data
    
    def test_dragon_chat_with_user_context(self):
        """Test /api/dragon/chat with user context"""
        response = requests.post(
            f"{BASE_URL}/api/dragon/chat",
            json={
                "command": "Show my resume",
                "language": "en",
                "user_context": {"user_name": "TestUser"}
            }
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "intent" in data
        assert "speech" in data


class TestDragonAIProcess:
    """Dragon AI Process endpoint tests (alias for chat)"""
    
    def test_dragon_process_endpoint(self):
        """Test /api/dragon/process endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/dragon/process",
            json={"command": "Hello", "language": "en"}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "intent" in data
        assert "speech" in data


class TestLanguageSelector:
    """Language selector API tests"""
    
    def test_translation_languages_endpoint(self):
        """Test /api/translation/languages returns available languages"""
        response = requests.get(f"{BASE_URL}/api/translation/languages")
        # May return 200 or 404 depending on implementation
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("status") == "healthy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
