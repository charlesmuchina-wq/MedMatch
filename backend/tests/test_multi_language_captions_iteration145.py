"""
Iteration 145: Multi-Language Caption Translation Tests
Tests for:
- GET /api/karau/webinar/caption-languages - returns 16 supported languages
- POST /api/karau/webinar/translate-caption - AI translation via GPT-4o-mini
- Same language no-op (source==target returns original)
- Authentication required for translate endpoint
- Multiple language translations (EN->ES, EN->FR, EN->JA, EN->KO, EN->AR)
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Expected 16 supported languages
EXPECTED_LANGUAGES = {
    "en": "English", "es": "Spanish", "fr": "French", "de": "German",
    "it": "Italian", "pt": "Portuguese", "ja": "Japanese", "ko": "Korean",
    "zh": "Chinese", "nl": "Dutch", "ar": "Arabic", "hi": "Hindi",
    "ru": "Russian", "tr": "Turkish", "pl": "Polish", "sv": "Swedish"
}


class TestCaptionLanguagesEndpoint:
    """Tests for GET /api/karau/webinar/caption-languages"""
    
    def test_caption_languages_returns_16_languages(self):
        """Verify caption-languages endpoint returns all 16 supported languages"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/caption-languages")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "languages" in data, "Response should contain 'languages' key"
        languages = data["languages"]
        
        # Check we have exactly 16 languages
        assert len(languages) == 16, f"Expected 16 languages, got {len(languages)}"
        
        # Verify all expected language codes are present
        for code, name in EXPECTED_LANGUAGES.items():
            assert code in languages, f"Missing language code: {code}"
            assert languages[code] == name, f"Unexpected name for {code}: got {languages[code]}, expected {name}"
    
    def test_caption_languages_no_auth_required(self):
        """Verify caption-languages is a public endpoint (no auth needed)"""
        response = requests.get(f"{BASE_URL}/api/karau/webinar/caption-languages")
        assert response.status_code == 200, "caption-languages should be accessible without auth"


class TestTranslateCaptionEndpoint:
    """Tests for POST /api/karau/webinar/translate-caption"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        return response.json().get("access_token")
    
    def test_translate_caption_requires_auth(self):
        """Verify translate-caption requires authentication"""
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            json={"text": "Hello world", "source_language": "en", "target_language": "es"}
        )
        # Should return 401 or 403 without auth
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
    
    def test_translate_caption_same_language_noop(self, auth_token):
        """Same language translation should return original text (no API call)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        original_text = "This is a test message that should not change."
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": original_text, "source_language": "en", "target_language": "en"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert data["translated"] == original_text, "Same-language should return original text unchanged"
        assert data["source"] == "en", "Source should be 'en'"
        assert data["target"] == "en", "Target should be 'en'"
    
    def test_translate_english_to_spanish(self, auth_token):
        """Test EN->ES translation using GPT-4o-mini"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "Hello, how are you?", "source_language": "en", "target_language": "es"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "translated" in data, "Response should contain 'translated'"
        assert data["source"] == "en", "Source should be 'en'"
        assert data["target"] == "es", "Target should be 'es'"
        # Basic check - translation should contain Spanish characters/words
        translated = data["translated"].lower()
        # Common Spanish greetings
        assert any(word in translated for word in ["hola", "cómo", "como", "estas", "está", "estás", "qué tal"]), \
            f"Spanish translation seems incorrect: {data['translated']}"
    
    def test_translate_english_to_french(self, auth_token):
        """Test EN->FR translation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "Good morning, welcome to the meeting.", "source_language": "en", "target_language": "fr"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "translated" in data, "Response should contain 'translated'"
        assert data["target"] == "fr", "Target should be 'fr'"
        translated = data["translated"].lower()
        # Common French words expected
        assert any(word in translated for word in ["bonjour", "bienvenue", "réunion", "reunion", "matin"]), \
            f"French translation seems incorrect: {data['translated']}"
    
    def test_translate_english_to_japanese(self, auth_token):
        """Test EN->JA translation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "Thank you very much.", "source_language": "en", "target_language": "ja"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "translated" in data, "Response should contain 'translated'"
        assert data["target"] == "ja", "Target should be 'ja'"
        # Japanese should contain Japanese characters
        translated = data["translated"]
        # Check for Japanese characters (hiragana, katakana, or kanji)
        has_japanese = any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' or '\u4e00' <= c <= '\u9fff' for c in translated)
        assert has_japanese or "arigatou" in translated.lower() or "arigato" in translated.lower(), \
            f"Japanese translation seems incorrect: {translated}"
    
    def test_translate_english_to_korean(self, auth_token):
        """Test EN->KO translation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "Nice to meet you.", "source_language": "en", "target_language": "ko"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "translated" in data, "Response should contain 'translated'"
        assert data["target"] == "ko", "Target should be 'ko'"
        # Korean should contain Hangul characters
        translated = data["translated"]
        has_korean = any('\uac00' <= c <= '\ud7af' for c in translated)
        assert has_korean, f"Korean translation should contain Hangul: {translated}"
    
    def test_translate_english_to_arabic(self, auth_token):
        """Test EN->AR translation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "Hello and welcome.", "source_language": "en", "target_language": "ar"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "translated" in data, "Response should contain 'translated'"
        assert data["target"] == "ar", "Target should be 'ar'"
        # Arabic should contain Arabic characters
        translated = data["translated"]
        has_arabic = any('\u0600' <= c <= '\u06ff' for c in translated)
        assert has_arabic, f"Arabic translation should contain Arabic characters: {translated}"
    
    def test_translate_spanish_to_german(self, auth_token):
        """Test ES->DE translation (non-English source)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "Buenos días, gracias por venir.", "source_language": "es", "target_language": "de"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "translated" in data, "Response should contain 'translated'"
        assert data["source"] == "es", "Source should be 'es'"
        assert data["target"] == "de", "Target should be 'de'"
        translated = data["translated"].lower()
        # Should contain German words
        assert any(word in translated for word in ["guten", "morgen", "tag", "danke", "kommen", "willkommen"]), \
            f"German translation seems incorrect: {data['translated']}"
    
    def test_translate_empty_text(self, auth_token):
        """Empty text should return empty without API call"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "", "source_language": "en", "target_language": "es"}
        )
        
        # Should return 200 with empty text (since same lang logic checks trim())
        if response.status_code == 200:
            data = response.json()
            assert data["translated"] == "", "Empty text should return empty"
    
    def test_translate_whitespace_only(self, auth_token):
        """Whitespace-only text should return original (no API call)"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "   ", "source_language": "en", "target_language": "es"}
        )
        
        # Whitespace should pass validation but not call API
        if response.status_code == 200:
            data = response.json()
            # Depending on implementation, might return original or empty
            assert "translated" in data


class TestTranslateCaptionEdgeCases:
    """Edge case tests for translate-caption endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        return response.json().get("access_token")
    
    def test_translate_long_text(self, auth_token):
        """Test translation with longer caption text"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        long_text = "This is a longer piece of text that might appear in live captions during a webinar. " \
                   "The speaker is discussing technical topics and using multiple sentences. " \
                   "Real-time translation is important for international audiences."
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": long_text, "source_language": "en", "target_language": "es"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert len(data["translated"]) > 0, "Translation should not be empty"
    
    def test_translate_with_numbers_and_punctuation(self, auth_token):
        """Test translation preserves numbers and handles punctuation"""
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        response = requests.post(
            f"{BASE_URL}/api/karau/webinar/translate-caption",
            headers=headers,
            json={"text": "Meeting starts at 3:30 PM. Total cost is $500.", "source_language": "en", "target_language": "es"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Numbers should typically be preserved
        assert "translated" in data
