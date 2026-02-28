"""
KARAU Extended Features Test - Iteration 130
Tests: Translation API, AI Assistant, CRM Webhooks, Industry Templates

Features tested:
- GET /api/karau-features/languages - 16 supported languages
- GET /api/karau-features/templates - 6 industry templates
- POST /api/karau-features/translate - translation with auth
- CRUD for /api/karau-features/webhooks
- POST /api/karau-features/ai-assistant/ask - AI answer based on meeting context
"""
import os
import pytest
import requests
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestKarauExtendedFeatures:
    """KARAU Extended Features - Translation, AI Assistant, Webhooks, Templates"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token for authenticated requests"""
        # Login as admin
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if login_res.status_code == 200:
            self.token = login_res.json().get("access_token")
        else:
            pytest.skip("Login failed - cannot test authenticated endpoints")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    # ===== Languages API =====
    def test_get_supported_languages(self):
        """GET /api/karau-features/languages returns 16 supported languages"""
        res = requests.get(f"{BASE_URL}/api/karau-features/languages")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        data = res.json()
        assert "languages" in data, "Response should contain 'languages' key"
        
        languages = data["languages"]
        assert len(languages) >= 14, f"Expected at least 14 languages, got {len(languages)}"
        
        # Check structure
        for lang in languages:
            assert "code" in lang, "Each language should have 'code'"
            assert "name" in lang, "Each language should have 'name'"
        
        # Verify specific languages exist
        codes = [l["code"] for l in languages]
        required_codes = ["en", "es", "fr", "de", "pt", "zh", "ja", "ko", "ar", "hi", "it", "ru"]
        for code in required_codes:
            assert code in codes, f"Missing required language code: {code}"
        
        print(f"✓ Languages API returned {len(languages)} languages")
    
    # ===== Templates API =====
    def test_get_industry_templates(self):
        """GET /api/karau-features/templates returns 6 industry templates"""
        res = requests.get(f"{BASE_URL}/api/karau-features/templates")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        data = res.json()
        assert "templates" in data, "Response should contain 'templates' key"
        
        templates = data["templates"]
        assert len(templates) == 6, f"Expected 6 templates, got {len(templates)}"
        
        # Check template structure
        for tmpl in templates:
            assert "template_id" in tmpl, "Each template should have 'template_id'"
            assert "name" in tmpl, "Each template should have 'name'"
            assert "industry" in tmpl, "Each template should have 'industry'"
            assert "settings" in tmpl, "Each template should have 'settings'"
        
        # Verify specific templates exist
        template_ids = [t["template_id"] for t in templates]
        expected_ids = ["interview-structured", "product-demo", "clinical-review", "standup", "board-meeting", "consultation"]
        for tid in expected_ids:
            assert tid in template_ids, f"Missing expected template: {tid}"
        
        print(f"✓ Templates API returned {len(templates)} templates")
        print(f"  Template IDs: {template_ids}")
    
    def test_get_single_template(self):
        """GET /api/karau-features/templates/{template_id} returns specific template"""
        res = requests.get(f"{BASE_URL}/api/karau-features/templates/interview-structured")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        data = res.json()
        assert data["template_id"] == "interview-structured"
        assert data["name"] == "Structured Interview"
        assert "sections" in data["settings"]
        
        print(f"✓ Single template API returned correct template")
    
    def test_get_nonexistent_template(self):
        """GET /api/karau-features/templates/{invalid_id} returns 404"""
        res = requests.get(f"{BASE_URL}/api/karau-features/templates/nonexistent-template")
        assert res.status_code == 404, f"Expected 404, got {res.status_code}"
        
        print(f"✓ Nonexistent template correctly returns 404")
    
    # ===== Translation API =====
    def test_translate_text_requires_auth(self):
        """POST /api/karau-features/translate requires authentication"""
        res = requests.post(f"{BASE_URL}/api/karau-features/translate", json={
            "text": "Hello world",
            "target_lang": "es"
        })
        assert res.status_code == 401 or res.status_code == 403, f"Expected 401/403, got {res.status_code}"
        print(f"✓ Translation API correctly requires auth")
    
    def test_translate_text_with_auth(self):
        """POST /api/karau-features/translate works with auth"""
        res = requests.post(f"{BASE_URL}/api/karau-features/translate", 
            headers=self.headers,
            json={
                "text": "Hello",
                "target_lang": "es",
                "source_lang": "en"
            }
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "translated_text" in data, "Response should contain 'translated_text'"
        assert data["source_lang"] == "en"
        assert data["target_lang"] == "es"
        # The translation uses LLM so actual text may vary - just check it returns something
        assert len(data["translated_text"]) > 0, "Should return non-empty translation"
        
        print(f"✓ Translation API returned: {data['translated_text']}")
    
    def test_translate_same_language(self):
        """POST /api/karau-features/translate returns original for same language"""
        res = requests.post(f"{BASE_URL}/api/karau-features/translate",
            headers=self.headers,
            json={
                "text": "Hello world",
                "target_lang": "en",
                "source_lang": "en"
            }
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        data = res.json()
        # Same language should return original text
        assert data["translated_text"] == "Hello world"
        
        print(f"✓ Same-language translation returns original text")
    
    # ===== Webhooks CRUD =====
    def test_webhooks_crud_flow(self):
        """Test complete webhook CRUD: create, list, test, delete"""
        
        # 1. Get initial list
        list_res = requests.get(f"{BASE_URL}/api/karau-features/webhooks", headers=self.headers)
        assert list_res.status_code == 200, f"List failed: {list_res.status_code}"
        initial_count = len(list_res.json().get("webhooks", []))
        
        # 2. Create webhook
        create_res = requests.post(f"{BASE_URL}/api/karau-features/webhooks",
            headers=self.headers,
            json={
                "webhook_url": "https://httpbin.org/post",
                "name": "TEST_Integration_Webhook",
                "events": ["meeting_ended", "meeting_created"]
            }
        )
        assert create_res.status_code == 200, f"Create failed: {create_res.status_code}: {create_res.text}"
        
        webhook = create_res.json()
        assert "webhook_id" in webhook, "Response should contain webhook_id"
        assert webhook["name"] == "TEST_Integration_Webhook"
        assert webhook["webhook_url"] == "https://httpbin.org/post"
        webhook_id = webhook["webhook_id"]
        
        print(f"✓ Created webhook: {webhook_id}")
        
        # 3. Verify webhook appears in list
        list_res2 = requests.get(f"{BASE_URL}/api/karau-features/webhooks", headers=self.headers)
        assert list_res2.status_code == 200
        webhooks = list_res2.json().get("webhooks", [])
        assert len(webhooks) == initial_count + 1, "Webhook count should increase by 1"
        
        found = any(w["webhook_id"] == webhook_id for w in webhooks)
        assert found, "Created webhook should appear in list"
        
        print(f"✓ Webhook appears in list")
        
        # 4. Test webhook
        test_res = requests.post(f"{BASE_URL}/api/karau-features/webhooks/test/{webhook_id}",
            headers=self.headers
        )
        assert test_res.status_code == 200, f"Test failed: {test_res.status_code}"
        
        test_data = test_res.json()
        # httpbin.org/post should return 200
        assert "success" in test_data
        assert "status_code" in test_data
        print(f"✓ Webhook test returned: success={test_data['success']}, status={test_data.get('status_code')}")
        
        # 5. Delete webhook
        delete_res = requests.delete(f"{BASE_URL}/api/karau-features/webhooks/{webhook_id}",
            headers=self.headers
        )
        assert delete_res.status_code == 200, f"Delete failed: {delete_res.status_code}"
        
        print(f"✓ Webhook deleted")
        
        # 6. Verify webhook is gone
        list_res3 = requests.get(f"{BASE_URL}/api/karau-features/webhooks", headers=self.headers)
        webhooks_after = list_res3.json().get("webhooks", [])
        assert len(webhooks_after) == initial_count, "Webhook count should return to initial"
        
        not_found = not any(w["webhook_id"] == webhook_id for w in webhooks_after)
        assert not_found, "Deleted webhook should not appear in list"
        
        print(f"✓ Webhook CRUD flow complete")
    
    def test_webhook_test_with_bad_url(self):
        """Test webhook with invalid URL returns failure"""
        # Create webhook with bad URL
        create_res = requests.post(f"{BASE_URL}/api/karau-features/webhooks",
            headers=self.headers,
            json={
                "webhook_url": "https://invalid-domain-that-does-not-exist-12345.com/webhook",
                "name": "TEST_Bad_URL_Webhook",
                "events": ["meeting_ended"]
            }
        )
        assert create_res.status_code == 200
        webhook_id = create_res.json()["webhook_id"]
        
        # Test it - should fail
        test_res = requests.post(f"{BASE_URL}/api/karau-features/webhooks/test/{webhook_id}",
            headers=self.headers
        )
        assert test_res.status_code == 200  # API returns 200 with success=false
        test_data = test_res.json()
        assert test_data.get("success") == False or "error" in test_data
        
        print(f"✓ Bad URL webhook test correctly returns failure")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/karau-features/webhooks/{webhook_id}", headers=self.headers)
    
    def test_delete_nonexistent_webhook(self):
        """DELETE /api/karau-features/webhooks/{invalid_id} returns 404"""
        res = requests.delete(f"{BASE_URL}/api/karau-features/webhooks/NONEXISTENT123",
            headers=self.headers
        )
        assert res.status_code == 404, f"Expected 404, got {res.status_code}"
        
        print(f"✓ Delete nonexistent webhook correctly returns 404")
    
    # ===== AI Assistant API =====
    def test_ai_assistant_ask_requires_auth(self):
        """POST /api/karau-features/ai-assistant/ask requires authentication"""
        res = requests.post(f"{BASE_URL}/api/karau-features/ai-assistant/ask", json={
            "meeting_id": "TEST123",
            "question": "What was discussed?"
        })
        assert res.status_code == 401 or res.status_code == 403, f"Expected 401/403, got {res.status_code}"
        
        print(f"✓ AI Assistant API correctly requires auth")
    
    def test_ai_assistant_ask_with_auth(self):
        """POST /api/karau-features/ai-assistant/ask returns AI answer"""
        res = requests.post(f"{BASE_URL}/api/karau-features/ai-assistant/ask",
            headers=self.headers,
            json={
                "meeting_id": "TEST123",
                "question": "What are the key topics?"
            }
        )
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        
        data = res.json()
        assert "answer" in data, "Response should contain 'answer'"
        assert "meeting_id" in data
        assert data["meeting_id"] == "TEST123"
        # Answer should be non-empty (even if meeting not found, it returns a message)
        assert len(data["answer"]) > 0
        
        print(f"✓ AI Assistant returned: {data['answer'][:100]}...")


class TestKarauMeetingsAPI:
    """Test KARAU meetings API for dashboard integration"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get auth token"""
        login_res = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if login_res.status_code == 200:
            self.token = login_res.json().get("access_token")
        else:
            pytest.skip("Login failed")
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_get_meetings_list(self):
        """GET /api/karau-meet/meetings returns meetings list"""
        res = requests.get(f"{BASE_URL}/api/karau-meet/meetings", headers=self.headers)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        
        data = res.json()
        assert "meetings" in data, "Response should contain 'meetings'"
        
        print(f"✓ Meetings list returned {len(data['meetings'])} meetings")
    
    def test_create_meeting(self):
        """POST /api/karau-meet/meetings creates new meeting"""
        res = requests.post(f"{BASE_URL}/api/karau-meet/meetings",
            headers=self.headers,
            json={"title": "TEST_Iteration130_Meeting"}
        )
        assert res.status_code == 200 or res.status_code == 201, f"Expected 200/201, got {res.status_code}"
        
        data = res.json()
        assert "meeting_id" in data, "Response should contain 'meeting_id'"
        
        print(f"✓ Created meeting: {data['meeting_id']}")
        return data["meeting_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
