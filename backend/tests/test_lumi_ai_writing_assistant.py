"""
LUMI AI Writing Assistant Backend API Tests
Testing: refine, smart-reply, translate, voice-to-text endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLumiAIRefine:
    """Test /api/lumi/ai/refine endpoint with all tone options"""
    
    def test_refine_professional_tone(self):
        """Test refine with professional instruction"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/refine", json={
            "text": "hey can u help me with this thing asap?",
            "instruction": "professional"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "refined_text" in data, "Response should contain refined_text"
        assert data["instruction"] == "professional"
        assert len(data["refined_text"]) > 0, "Refined text should not be empty"
        print(f"PASS: Professional refinement - '{data['refined_text'][:50]}...'")
    
    def test_refine_friendly_tone(self):
        """Test refine with friendly instruction"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/refine", json={
            "text": "I need the report by end of day",
            "instruction": "friendly"
        })
        assert response.status_code == 200
        data = response.json()
        assert "refined_text" in data
        assert data["instruction"] == "friendly"
        print(f"PASS: Friendly refinement - '{data['refined_text'][:50]}...'")
    
    def test_refine_assertive_tone(self):
        """Test refine with assertive instruction"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/refine", json={
            "text": "I think maybe we should consider doing it differently",
            "instruction": "assertive"
        })
        assert response.status_code == 200
        data = response.json()
        assert "refined_text" in data
        assert data["instruction"] == "assertive"
        print(f"PASS: Assertive refinement - '{data['refined_text'][:50]}...'")
    
    def test_refine_concise_tone(self):
        """Test refine with concise instruction"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/refine", json={
            "text": "I wanted to reach out to you today to discuss the possibility of perhaps meeting sometime next week if you have some free time in your schedule",
            "instruction": "concise"
        })
        assert response.status_code == 200
        data = response.json()
        assert "refined_text" in data
        assert data["instruction"] == "concise"
        # Concise text should ideally be shorter
        print(f"PASS: Concise refinement - '{data['refined_text'][:50]}...'")
    
    def test_refine_empty_text(self):
        """Test refine with empty text should still work (handled by frontend)"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/refine", json={
            "text": "",
            "instruction": "professional"
        })
        # Backend should accept it - frontend prevents empty calls
        assert response.status_code in [200, 422, 500], f"Got unexpected status: {response.status_code}"
        print(f"PASS: Empty text handled with status {response.status_code}")


class TestLumiAISmartReply:
    """Test /api/lumi/ai/smart-reply endpoint"""
    
    def test_smart_reply_with_context(self):
        """Test smart reply generates suggestions based on conversation"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/smart-reply", json={
            "messages": [
                {"sender": "Alice", "content": "Hey team, are we still on for the meeting tomorrow?"},
                {"sender": "Bob", "content": "I think so, let me check my calendar"},
                {"sender": "Alice", "content": "Great, please confirm when you can!"}
            ],
            "channel_name": "general"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "suggestions" in data, "Response should contain suggestions"
        assert isinstance(data["suggestions"], list), "Suggestions should be a list"
        assert len(data["suggestions"]) > 0, "Should have at least one suggestion"
        print(f"PASS: Smart reply generated {len(data['suggestions'])} suggestions")
        for i, s in enumerate(data["suggestions"]):
            print(f"  Suggestion {i+1}: {s[:60]}...")
    
    def test_smart_reply_empty_messages(self):
        """Test smart reply with empty messages array"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/smart-reply", json={
            "messages": [],
            "channel_name": "test-channel"
        })
        # Should handle gracefully - may return empty or error
        assert response.status_code in [200, 422, 500]
        print(f"PASS: Empty messages handled with status {response.status_code}")
    
    def test_smart_reply_single_message(self):
        """Test smart reply with single message context"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/smart-reply", json={
            "messages": [
                {"sender": "Manager", "content": "Can you provide an update on the project status?"}
            ],
            "channel_name": "project-updates"
        })
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        print(f"PASS: Single message context - {len(data.get('suggestions', []))} suggestions")


class TestLumiAITranslate:
    """Test /api/lumi/ai/translate endpoint with multiple languages"""
    
    def test_translate_to_spanish(self):
        """Test translation to Spanish"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/translate", json={
            "text": "Hello, how are you today?",
            "target_language": "es"
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "es"
        assert data["target_name"] == "Spanish"
        print(f"PASS: Spanish translation - '{data['translated_text']}'")
    
    def test_translate_to_french(self):
        """Test translation to French"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/translate", json={
            "text": "The meeting is scheduled for tomorrow at 3pm",
            "target_language": "fr"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "fr"
        print(f"PASS: French translation - '{data['translated_text']}'")
    
    def test_translate_to_german(self):
        """Test translation to German"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/translate", json={
            "text": "Please review the document and provide feedback",
            "target_language": "de"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "de"
        print(f"PASS: German translation - '{data['translated_text']}'")
    
    def test_translate_to_japanese(self):
        """Test translation to Japanese"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/translate", json={
            "text": "Thank you for your help",
            "target_language": "ja"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "ja"
        print(f"PASS: Japanese translation - '{data['translated_text']}'")
    
    def test_translate_to_chinese(self):
        """Test translation to Chinese"""
        response = requests.post(f"{BASE_URL}/api/lumi/ai/translate", json={
            "text": "Welcome to the team!",
            "target_language": "zh"
        })
        assert response.status_code == 200
        data = response.json()
        assert "translated_text" in data
        assert data["target_language"] == "zh"
        print(f"PASS: Chinese translation - '{data['translated_text']}'")
    
    def test_translate_all_supported_languages(self):
        """Test all 10 supported languages from frontend"""
        languages = ["es", "fr", "de", "ja", "zh", "ko", "pt", "ar", "hi", "ru"]
        text = "This is a test message"
        results = {}
        
        for lang in languages:
            response = requests.post(f"{BASE_URL}/api/lumi/ai/translate", json={
                "text": text,
                "target_language": lang
            })
            if response.status_code == 200:
                data = response.json()
                results[lang] = "PASS"
                print(f"  {lang}: '{data.get('translated_text', '')[:40]}...'")
            else:
                results[lang] = f"FAIL ({response.status_code})"
        
        passed = sum(1 for v in results.values() if v == "PASS")
        print(f"PASS: {passed}/{len(languages)} languages translated successfully")
        assert passed >= 8, f"At least 8/10 languages should work, got {passed}"


class TestLumiAIVoiceToText:
    """Test /api/lumi/ai/voice-to-text endpoint"""
    
    def test_voice_to_text_endpoint_exists(self):
        """Verify endpoint exists and accepts file uploads"""
        # Since we can't easily create audio file in test, verify endpoint responds
        response = requests.post(f"{BASE_URL}/api/lumi/ai/voice-to-text", files={})
        # Should return 422 for missing file, not 404
        assert response.status_code in [422, 400], f"Expected 422/400, got {response.status_code}"
        print(f"PASS: Voice-to-text endpoint exists (status {response.status_code} for missing file)")
    
    def test_voice_to_text_invalid_format(self):
        """Test with invalid file format"""
        import io
        fake_file = io.BytesIO(b"not an audio file")
        response = requests.post(
            f"{BASE_URL}/api/lumi/ai/voice-to-text",
            files={"file": ("test.txt", fake_file, "text/plain")}
        )
        # Should reject non-audio formats
        assert response.status_code in [400, 500, 422]
        print(f"PASS: Invalid format rejected with status {response.status_code}")


class TestHealthAndRouting:
    """Basic health and routing tests"""
    
    def test_api_health(self):
        """Verify API is healthy"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("PASS: API health check passed")
    
    def test_lumi_ai_routes_registered(self):
        """Verify LUMI AI routes are properly registered"""
        # Test route existence via OPTIONS or invalid method
        endpoints = [
            "/api/lumi/ai/refine",
            "/api/lumi/ai/smart-reply",
            "/api/lumi/ai/translate",
            "/api/lumi/ai/voice-to-text"
        ]
        for ep in endpoints:
            response = requests.options(f"{BASE_URL}{ep}")
            # 200 or 405 means route exists
            assert response.status_code in [200, 204, 405], f"Route {ep} not found"
            print(f"PASS: Route {ep} registered")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
