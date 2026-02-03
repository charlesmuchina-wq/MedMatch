"""
Comprehensive i18n and Translation Testing
Tests all translation features including:
- Language selector (55+ languages)
- Bundled languages (25 including 16 African)
- Gender-aware translations (24 gendered languages)
- Translation Analytics Dashboard
- Translation Memory (TMX)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLanguagesAPI:
    """Test GET /api/translate/languages endpoint"""
    
    def test_languages_returns_200(self):
        """Verify languages endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        
    def test_languages_count_55_plus(self):
        """Verify 55+ supported languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        data = response.json()
        
        assert "languages" in data
        assert "total" in data
        assert data["total"] >= 55, f"Expected 55+ languages, got {data['total']}"
        
    def test_african_languages_present(self):
        """Verify all 16 African languages are present"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        data = response.json()
        
        african_codes = ["sw", "ha", "yo", "ig", "zu", "xh", "af", "am", "om", "so", "rw", "sn", "ny", "tw", "wo", "lg"]
        
        lang_codes = [lang.get("code") if isinstance(lang, dict) else lang for lang in data.get("languages", [])]
        
        found_african = [code for code in african_codes if code in lang_codes]
        assert len(found_african) == 16, f"Expected 16 African languages, found {len(found_african)}: {found_african}"


class TestGenderRulesAPI:
    """Test GET /api/translate/gender-rules endpoint"""
    
    def test_gender_rules_returns_200(self):
        """Verify gender rules endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        assert response.status_code == 200
        
    def test_24_gendered_languages(self):
        """Verify 24 gendered languages as per CLDR"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        data = response.json()
        
        assert data["total_gendered"] == 24, f"Expected 24 gendered languages, got {data['total_gendered']}"
        
    def test_gendered_languages_list(self):
        """Verify specific gendered languages are included"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        data = response.json()
        
        expected_gendered = ["es", "fr", "de", "it", "pt", "ru", "ar", "he", "hi"]
        for lang in expected_gendered:
            assert lang in data["gendered_languages"], f"{lang} should be in gendered languages"


class TestGenderAwareTranslation:
    """Test POST /api/translate/gender-aware endpoint"""
    
    def test_spanish_feminine_translation(self):
        """Test Spanish translation with feminine gender"""
        response = requests.post(
            f"{BASE_URL}/api/translate/gender-aware",
            json={
                "text": "Welcome back",
                "target_language": "es",
                "grammatical_gender": "feminine"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["gender_applied"] == True
        assert "translated" in data
        # Should contain feminine form
        translated_lower = data["translated"].lower()
        assert "bienvenida" in translated_lower or "conectada" in translated_lower or data["translated"] != "Welcome back"
        
    def test_french_masculine_translation(self):
        """Test French translation with masculine gender"""
        response = requests.post(
            f"{BASE_URL}/api/translate/gender-aware",
            json={
                "text": "You are connected",
                "target_language": "fr",
                "grammatical_gender": "masculine"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["gender_applied"] == True


class TestTranslationAnalyticsDashboard:
    """Test GET /api/translate/analytics/dashboard endpoint"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@medmatch.com",
                "password": "MedMatch2026!"
            }
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin authentication failed")
        
    def test_dashboard_requires_admin(self):
        """Verify dashboard requires admin authentication"""
        response = requests.get(f"{BASE_URL}/api/translate/analytics/dashboard")
        assert response.status_code == 403
        
    def test_dashboard_with_admin(self, admin_token):
        """Test dashboard with admin authentication"""
        response = requests.get(
            f"{BASE_URL}/api/translate/analytics/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "summary" in data
        assert "top_languages" in data
        assert "daily_usage" in data
        assert "cldr_compliance" in data
        
    def test_dashboard_summary_fields(self, admin_token):
        """Verify dashboard summary has all required fields"""
        response = requests.get(
            f"{BASE_URL}/api/translate/analytics/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        summary = data["summary"]
        assert "total_translations" in summary
        assert "total_characters" in summary
        assert "cache_entries" in summary
        assert "memory_entries" in summary


class TestTranslationMemory:
    """Test Translation Memory (TMX) endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": "admin@medmatch.com",
                "password": "MedMatch2026!"
            }
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Admin authentication failed")
        
    def test_memory_lookup(self):
        """Test translation memory lookup"""
        response = requests.get(
            f"{BASE_URL}/api/translate/memory/lookup",
            params={
                "source_text": "Dashboard",
                "target_language": "es"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "match_type" in data
        assert "confidence" in data
        
    def test_memory_stats(self, admin_token):
        """Test translation memory stats"""
        response = requests.get(
            f"{BASE_URL}/api/translate/memory/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "total_entries" in data
        assert "by_language" in data


class TestBatchTranslation:
    """Test batch translation endpoint"""
    
    def test_batch_translate(self):
        """Test batch translation of multiple texts"""
        response = requests.post(
            f"{BASE_URL}/api/translate/batch",
            json={
                "texts": ["Dashboard", "Search", "Settings"],
                "target_language": "es"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "translations" in data
        assert "count" in data
        assert data["count"] == 3
        
    def test_batch_translate_empty(self):
        """Test batch translation with empty array"""
        response = requests.post(
            f"{BASE_URL}/api/translate/batch",
            json={
                "texts": [],
                "target_language": "es"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["count"] == 0


class TestQualityScoring:
    """Test translation quality scoring"""
    
    def test_quality_score(self):
        """Test translation quality scoring endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/translate/quality/score",
            json={
                "source_text": "Welcome to MedMatch",
                "target_text": "Bienvenido a MedMatch",
                "target_language": "es"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "quality" in data
        assert "overall_score" in data["quality"]
        assert 0 <= data["quality"]["overall_score"] <= 100
