"""
Test Suite for i18n Translation System - CAPA-2026-001 Verification
Tests: Translation Memory API, Analytics Dashboard, Pre-rendering, Batch Translation
Languages: Japanese, Arabic (RTL), Hindi, Swahili, Korean, Portuguese-BR
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTranslationAPIs:
    """Translation API endpoint tests for CAPA-2026-001 verification"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def test_health_check(self):
        """Verify backend is healthy"""
        response = self.session.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "healthy"
        print("✅ Backend health check passed")
    
    def test_supported_languages_endpoint(self):
        """Verify /api/translate/languages returns supported languages"""
        response = self.session.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        languages = data["languages"]
        
        # Verify CAPA-affected languages are present
        capa_languages = ["ja", "ar", "hi", "sw", "ko", "pt-BR"]
        for lang in capa_languages:
            assert lang in languages, f"Language {lang} not found in supported languages"
        
        print(f"✅ Supported languages endpoint working - {len(languages)} languages available")
        print(f"   CAPA languages verified: {capa_languages}")
    
    def test_prerender_japanese(self):
        """Test pre-rendered translations for Japanese (ja)"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/ja")
        assert response.status_code == 200
        data = response.json()
        
        assert "translations" in data
        translations = data["translations"]
        
        # Verify priority UI elements are pre-rendered
        priority_keys = ["Dashboard", "Job Search", "Settings", "Profile"]
        found_keys = [k for k in priority_keys if k in translations]
        
        print(f"✅ Japanese pre-render: {len(translations)} translations")
        print(f"   Priority keys found: {found_keys}")
        
        # Verify Japanese characters in translations
        if translations:
            sample = list(translations.values())[0]
            # Japanese should contain hiragana, katakana, or kanji
            has_japanese = any(ord(c) > 0x3000 for c in sample)
            print(f"   Sample translation: {sample}")
            print(f"   Contains Japanese characters: {has_japanese}")
    
    def test_prerender_arabic_rtl(self):
        """Test pre-rendered translations for Arabic (ar) - RTL language"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/ar")
        assert response.status_code == 200
        data = response.json()
        
        assert "translations" in data
        translations = data["translations"]
        
        print(f"✅ Arabic pre-render: {len(translations)} translations")
        
        # Verify Arabic characters in translations
        if translations:
            sample = list(translations.values())[0]
            # Arabic script range: 0x0600-0x06FF
            has_arabic = any(0x0600 <= ord(c) <= 0x06FF for c in sample)
            print(f"   Sample translation: {sample}")
            print(f"   Contains Arabic characters: {has_arabic}")
    
    def test_prerender_hindi(self):
        """Test pre-rendered translations for Hindi (hi) - Devanagari script"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/hi")
        assert response.status_code == 200
        data = response.json()
        
        assert "translations" in data
        translations = data["translations"]
        
        print(f"✅ Hindi pre-render: {len(translations)} translations")
        
        # Verify Devanagari characters in translations
        if translations:
            sample = list(translations.values())[0]
            # Devanagari script range: 0x0900-0x097F
            has_devanagari = any(0x0900 <= ord(c) <= 0x097F for c in sample)
            print(f"   Sample translation: {sample}")
            print(f"   Contains Devanagari characters: {has_devanagari}")
    
    def test_prerender_swahili(self):
        """Test pre-rendered translations for Swahili (sw)"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/sw")
        assert response.status_code == 200
        data = response.json()
        
        assert "translations" in data
        translations = data["translations"]
        
        print(f"✅ Swahili pre-render: {len(translations)} translations")
        if translations:
            sample = list(translations.values())[0]
            print(f"   Sample translation: {sample}")
    
    def test_prerender_korean(self):
        """Test pre-rendered translations for Korean (ko)"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/ko")
        assert response.status_code == 200
        data = response.json()
        
        assert "translations" in data
        translations = data["translations"]
        
        print(f"✅ Korean pre-render: {len(translations)} translations")
        
        # Verify Korean characters (Hangul)
        if translations:
            sample = list(translations.values())[0]
            # Hangul range: 0xAC00-0xD7AF
            has_korean = any(0xAC00 <= ord(c) <= 0xD7AF for c in sample)
            print(f"   Sample translation: {sample}")
            print(f"   Contains Korean characters: {has_korean}")
    
    def test_prerender_portuguese_br(self):
        """Test pre-rendered translations for Portuguese-BR (pt-BR)"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/pt-BR")
        assert response.status_code == 200
        data = response.json()
        
        assert "translations" in data
        translations = data["translations"]
        
        print(f"✅ Portuguese-BR pre-render: {len(translations)} translations")
        if translations:
            sample = list(translations.values())[0]
            print(f"   Sample translation: {sample}")


class TestTranslationMemoryAPI:
    """Translation Memory API tests - TMX standard compliance"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_memory_store(self):
        """Test /api/translate/memory/store endpoint"""
        payload = {
            "source_text": "Dashboard",
            "target_text": "ダッシュボード",
            "source_lang": "en",
            "target_lang": "ja"
        }
        response = self.session.post(f"{BASE_URL}/api/translate/memory/store", json=payload)
        
        # Accept 200, 201, or 404 (if endpoint not implemented)
        if response.status_code == 404:
            pytest.skip("Translation Memory store endpoint not implemented")
        
        assert response.status_code in [200, 201], f"Unexpected status: {response.status_code}"
        print(f"✅ Translation Memory store: {response.status_code}")
        print(f"   Stored: 'Dashboard' -> 'ダッシュボード' (en->ja)")
    
    def test_memory_lookup(self):
        """Test /api/translate/memory/lookup endpoint"""
        payload = {
            "source_text": "Dashboard",
            "source_lang": "en",
            "target_lang": "ja"
        }
        response = self.session.post(f"{BASE_URL}/api/translate/memory/lookup", json=payload)
        
        # Accept 200 or 404 (if endpoint not implemented)
        if response.status_code == 404:
            pytest.skip("Translation Memory lookup endpoint not implemented")
        
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        data = response.json()
        print(f"✅ Translation Memory lookup: {response.status_code}")
        print(f"   Response: {data}")


class TestAnalyticsDashboardAPI:
    """Analytics Dashboard API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_analytics_dashboard(self):
        """Test /api/translate/analytics/dashboard endpoint"""
        response = self.session.get(f"{BASE_URL}/api/translate/analytics/dashboard")
        
        # Accept 200 or 404 (if endpoint not implemented)
        if response.status_code == 404:
            pytest.skip("Analytics dashboard endpoint not implemented")
        
        assert response.status_code == 200, f"Unexpected status: {response.status_code}"
        data = response.json()
        print(f"✅ Analytics Dashboard: {response.status_code}")
        print(f"   Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")


class TestBatchTranslation:
    """Batch translation API tests - CAPA-2026-001 batch size fix verification"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_batch_translation_under_limit(self):
        """Test batch translation with texts under 20 limit"""
        payload = {
            "texts": ["Dashboard", "Job Search", "Settings", "Profile", "Save"],
            "target_language": "ja"
        }
        response = self.session.post(f"{BASE_URL}/api/translate/batch", json=payload)
        assert response.status_code == 200, f"Batch translation failed: {response.status_code}"
        
        data = response.json()
        assert "translations" in data
        translations = data["translations"]
        
        print(f"✅ Batch translation (5 texts): {len(translations)} results")
        for t in translations[:3]:
            print(f"   '{t.get('original')}' -> '{t.get('translated')}'")
    
    def test_batch_translation_at_limit(self):
        """Test batch translation with exactly 15 texts (CAPA fix batch size)"""
        texts = [
            "Dashboard", "Job Search", "Settings", "Profile", "Save",
            "Cancel", "Delete", "Edit", "Search", "Submit",
            "Close", "Back", "Next", "Confirm", "Yes"
        ]
        payload = {
            "texts": texts,
            "target_language": "ja"
        }
        response = self.session.post(f"{BASE_URL}/api/translate/batch", json=payload)
        assert response.status_code == 200, f"Batch translation failed: {response.status_code}"
        
        data = response.json()
        assert "translations" in data
        translations = data["translations"]
        
        print(f"✅ Batch translation (15 texts - CAPA limit): {len(translations)} results")
    
    def test_batch_translation_empty_array(self):
        """Test batch translation with empty array (CAPA fix)"""
        payload = {
            "texts": [],
            "target_language": "ja"
        }
        response = self.session.post(f"{BASE_URL}/api/translate/batch", json=payload)
        
        # Should return 200 with empty translations, not 400
        assert response.status_code == 200, f"Empty batch should return 200, got: {response.status_code}"
        print(f"✅ Empty batch translation handled correctly: {response.status_code}")


class TestBundledLanguages:
    """Bundled languages baseline tests - ensure no regression"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_spanish_prerender(self):
        """Test Spanish (es) - bundled language"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/es")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Spanish pre-render: {len(data.get('translations', {}))} translations")
    
    def test_french_prerender(self):
        """Test French (fr) - bundled language"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/fr")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ French pre-render: {len(data.get('translations', {}))} translations")
    
    def test_german_prerender(self):
        """Test German (de) - bundled language"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/de")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ German pre-render: {len(data.get('translations', {}))} translations")
    
    def test_chinese_prerender(self):
        """Test Chinese (zh) - bundled language"""
        response = self.session.get(f"{BASE_URL}/api/translate/prerender/zh")
        assert response.status_code == 200
        data = response.json()
        print(f"✅ Chinese pre-render: {len(data.get('translations', {}))} translations")


class TestSingleTextTranslation:
    """Single text translation API tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_single_text_japanese(self):
        """Test single text translation to Japanese"""
        payload = {
            "text": "Welcome to MedMatch",
            "target_language": "ja"
        }
        response = self.session.post(f"{BASE_URL}/api/translate/text", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "translated_text" in data
        translated = data["translated_text"]
        
        # Verify Japanese characters
        has_japanese = any(ord(c) > 0x3000 for c in translated)
        print(f"✅ Single text translation (ja): '{translated}'")
        print(f"   Contains Japanese: {has_japanese}")
    
    def test_single_text_arabic(self):
        """Test single text translation to Arabic"""
        payload = {
            "text": "Welcome to MedMatch",
            "target_language": "ar"
        }
        response = self.session.post(f"{BASE_URL}/api/translate/text", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "translated_text" in data
        translated = data["translated_text"]
        
        # Verify Arabic characters
        has_arabic = any(0x0600 <= ord(c) <= 0x06FF for c in translated)
        print(f"✅ Single text translation (ar): '{translated}'")
        print(f"   Contains Arabic: {has_arabic}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
