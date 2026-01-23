"""
Test Suite for New MedMatch Features:
- KARAU Dragon AI
- Translation Widget
- Cloud Storage Upload
- Resume Upload (PDF, DOC, DOCX)
"""
import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://medmatch-ai.preview.emergentagent.com')

class TestDragonAI:
    """KARAU Dragon AI endpoint tests"""
    
    def test_dragon_process_cover_letter_intent(self):
        """Test Dragon AI processes cover letter command"""
        response = requests.post(f"{BASE_URL}/api/dragon/process", json={
            "command": "Help me write a cover letter",
            "user_context": {"has_resume": True, "user_name": "Test User"}
        })
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "speech" in data
        assert data["intent"] == "cover_letter"
        print(f"✅ Dragon AI cover letter intent: {data['intent']}")
    
    def test_dragon_process_job_search_intent(self):
        """Test Dragon AI processes job search command"""
        response = requests.post(f"{BASE_URL}/api/dragon/process", json={
            "command": "Find quality engineer jobs",
            "user_context": {"has_resume": True, "user_name": "Test User"}
        })
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "speech" in data
        assert data["intent"] == "job_search"
        print(f"✅ Dragon AI job search intent: {data['intent']}")
    
    def test_dragon_process_interview_prep_intent(self):
        """Test Dragon AI processes interview prep command"""
        response = requests.post(f"{BASE_URL}/api/dragon/process", json={
            "command": "Prepare me for an interview",
            "user_context": {"has_resume": True, "user_name": "Test User"}
        })
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "speech" in data
        assert data["intent"] == "interview_prep"
        print(f"✅ Dragon AI interview prep intent: {data['intent']}")
    
    def test_dragon_process_resume_intent(self):
        """Test Dragon AI processes resume command"""
        response = requests.post(f"{BASE_URL}/api/dragon/process", json={
            "command": "Show my resume",
            "user_context": {"has_resume": True, "user_name": "Test User"}
        })
        assert response.status_code == 200
        data = response.json()
        assert "intent" in data
        assert "speech" in data
        assert data["intent"] == "resume"
        print(f"✅ Dragon AI resume intent: {data['intent']}")
    
    def test_dragon_process_with_action(self):
        """Test Dragon AI returns action with path"""
        response = requests.post(f"{BASE_URL}/api/dragon/process", json={
            "command": "Help me write a cover letter for Google",
            "user_context": {"has_resume": True, "user_name": "Test User"}
        })
        assert response.status_code == 200
        data = response.json()
        assert "action" in data
        if data.get("action"):
            assert "path" in data["action"]
            assert "label" in data["action"]
        print(f"✅ Dragon AI action: {data.get('action', {}).get('label', 'N/A')}")


class TestTranslationAPI:
    """Translation API endpoint tests"""
    
    def test_get_supported_languages(self):
        """Test getting list of supported languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "total" in data
        assert data["total"] > 0
        
        # Check language structure
        lang = data["languages"][0]
        assert "code" in lang
        assert "name" in lang
        assert "native" in lang
        assert "flag" in lang
        print(f"✅ Supported languages: {data['total']} languages")
    
    def test_translate_text_to_spanish(self):
        """Test translating text to Spanish"""
        response = requests.post(f"{BASE_URL}/api/translate/text", json={
            "text": "Hello, I am looking for a job",
            "target_language": "es"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert "target_language" in data
        assert data["target_language"] == "es"
        assert len(data["translated_text"]) > 0
        print(f"✅ Translation to Spanish: {data['translated_text']}")
    
    def test_translate_text_to_french(self):
        """Test translating text to French"""
        response = requests.post(f"{BASE_URL}/api/translate/text", json={
            "text": "I have 5 years of experience in software development",
            "target_language": "fr"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "fr"
        print(f"✅ Translation to French: {data['translated_text']}")
    
    def test_translate_text_to_german(self):
        """Test translating text to German"""
        response = requests.post(f"{BASE_URL}/api/translate/text", json={
            "text": "Thank you for considering my application",
            "target_language": "de"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "de"
        print(f"✅ Translation to German: {data['translated_text']}")
    
    def test_translate_invalid_language(self):
        """Test translation with invalid language code"""
        response = requests.post(f"{BASE_URL}/api/translate/text", json={
            "text": "Hello world",
            "target_language": "invalid_lang"
        })
        assert response.status_code == 400
        print("✅ Invalid language returns 400")
    
    def test_translate_empty_text(self):
        """Test translation with empty text"""
        response = requests.post(f"{BASE_URL}/api/translate/text", json={
            "text": "",
            "target_language": "es"
        })
        assert response.status_code == 400
        print("✅ Empty text returns 400")


class TestCloudStorageAPI:
    """Cloud Storage API endpoint tests"""
    
    def test_google_drive_download_endpoint_exists(self):
        """Test Google Drive download endpoint exists"""
        # This endpoint requires valid access token, so we just check it exists
        response = requests.post(f"{BASE_URL}/api/cloud/google-drive/download", json={
            "file_id": "test_file_id",
            "access_token": "invalid_token"
        })
        # Should return error (not 404) since endpoint exists
        assert response.status_code != 404
        print(f"✅ Google Drive download endpoint exists (status: {response.status_code})")


class TestResumeUpload:
    """Resume upload endpoint tests"""
    
    def test_resume_upload_endpoint_exists(self):
        """Test resume upload endpoint exists"""
        # Test without file - should return validation error, not 404
        response = requests.post(f"{BASE_URL}/api/resume/upload")
        assert response.status_code != 404
        print(f"✅ Resume upload endpoint exists (status: {response.status_code})")
    
    def test_resume_upload_invalid_file_type(self):
        """Test resume upload rejects invalid file types"""
        # Create a fake text file
        files = {'file': ('test.txt', b'This is a test file', 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/resume/upload", files=files)
        assert response.status_code == 400
        print("✅ Invalid file type returns 400")


class TestHealthAndIntegration:
    """Health check and integration tests"""
    
    def test_health_check(self):
        """Test API health check"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check: {data['status']}")
    
    def test_dragon_and_translation_integration(self):
        """Test Dragon AI and Translation work together"""
        # First, test Dragon AI
        dragon_response = requests.post(f"{BASE_URL}/api/dragon/process", json={
            "command": "Help me write a cover letter",
            "user_context": {"has_resume": True, "user_name": "Test User"}
        })
        assert dragon_response.status_code == 200
        
        # Then, test Translation
        translate_response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert translate_response.status_code == 200
        
        print("✅ Dragon AI and Translation integration working")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
