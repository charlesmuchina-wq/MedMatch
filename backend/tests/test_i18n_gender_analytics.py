"""
i18n Gender Support and Translation Analytics Tests
Tests for:
- Gender-aware translation API
- Gender rules API
- Translation Analytics Dashboard
- Bundled languages verification
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGenderRulesAPI:
    """Test GET /api/translate/gender-rules endpoint"""
    
    def test_gender_rules_returns_200(self):
        """Verify gender rules endpoint returns 200"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        assert response.status_code == 200
        
    def test_gender_rules_structure(self):
        """Verify gender rules response structure"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        data = response.json()
        
        assert "rules" in data
        assert "gendered_languages" in data
        assert "total_gendered" in data
        
    def test_gender_rules_spanish_is_gendered(self):
        """Verify Spanish is listed as gendered language"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        data = response.json()
        
        assert "es" in data["gendered_languages"]
        assert data["rules"]["es"]["has_gender"] == True
        assert "masculine" in data["rules"]["es"]["genders"]
        assert "feminine" in data["rules"]["es"]["genders"]
        
    def test_gender_rules_english_not_gendered(self):
        """Verify English is not gendered"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        data = response.json()
        
        assert data["rules"]["en"]["has_gender"] == False
        assert data["rules"]["en"]["genders"] == []
        
    def test_gender_rules_24_gendered_languages(self):
        """Verify 24 gendered languages as per CLDR"""
        response = requests.get(f"{BASE_URL}/api/translate/gender-rules")
        data = response.json()
        
        assert data["total_gendered"] == 24
        assert len(data["gendered_languages"]) == 24


class TestGenderAwareTranslation:
    """Test POST /api/translate/gender-aware endpoint"""
    
    def test_gender_aware_spanish_feminine(self):
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
        
        assert data["target_language"] == "es"
        assert data["grammatical_gender"] == "feminine"
        assert data["gender_applied"] == True
        assert "translated" in data
        # Feminine form should contain "Bienvenida" not "Bienvenido"
        assert "Bienvenida" in data["translated"] or "bienvenida" in data["translated"].lower()
        
    def test_gender_aware_spanish_masculine(self):
        """Test Spanish translation with masculine gender"""
        response = requests.post(
            f"{BASE_URL}/api/translate/gender-aware",
            json={
                "text": "Welcome back",
                "target_language": "es",
                "grammatical_gender": "masculine"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["grammatical_gender"] == "masculine"
        assert data["gender_applied"] == True
        
    def test_gender_aware_french_feminine(self):
        """Test French translation with feminine gender"""
        response = requests.post(
            f"{BASE_URL}/api/translate/gender-aware",
            json={
                "text": "You are welcome",
                "target_language": "fr",
                "grammatical_gender": "feminine"
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["target_language"] == "fr"
        assert data["gender_applied"] == True
        
    def test_gender_aware_non_gendered_language(self):
        """Test gender-aware translation for non-gendered language (English)"""
        response = requests.post(
            f"{BASE_URL}/api/translate/gender-aware",
            json={
                "text": "Hello",
                "target_language": "en",
                "grammatical_gender": "feminine"
            }
        )
        # Should return 400 since English is not gendered
        assert response.status_code == 400
        
    def test_gender_aware_missing_gender_field(self):
        """Test gender-aware translation without grammatical_gender field"""
        response = requests.post(
            f"{BASE_URL}/api/translate/gender-aware",
            json={
                "text": "Hello",
                "target_language": "es"
            }
        )
        # Should return 422 validation error
        assert response.status_code == 422


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
        
    def test_analytics_dashboard_requires_auth(self):
        """Verify analytics dashboard requires authentication"""
        response = requests.get(f"{BASE_URL}/api/translate/analytics/dashboard")
        assert response.status_code == 403
        
    def test_analytics_dashboard_with_admin_auth(self, admin_token):
        """Test analytics dashboard with admin authentication"""
        response = requests.get(
            f"{BASE_URL}/api/translate/analytics/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        
    def test_analytics_dashboard_structure(self, admin_token):
        """Verify analytics dashboard response structure"""
        response = requests.get(
            f"{BASE_URL}/api/translate/analytics/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        # Verify summary section
        assert "summary" in data
        assert "total_translations" in data["summary"]
        assert "total_characters" in data["summary"]
        assert "cache_entries" in data["summary"]
        assert "memory_entries" in data["summary"]
        
        # Verify top_languages section
        assert "top_languages" in data
        
        # Verify daily_usage section
        assert "daily_usage" in data
        
        # Verify CLDR compliance section
        assert "cldr_compliance" in data
        assert data["cldr_compliance"]["tmx_enabled"] == True
        
    def test_analytics_dashboard_summary_values(self, admin_token):
        """Verify analytics dashboard summary has valid values"""
        response = requests.get(
            f"{BASE_URL}/api/translate/analytics/dashboard",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        data = response.json()
        
        # Values should be non-negative integers
        assert data["summary"]["total_translations"] >= 0
        assert data["summary"]["total_characters"] >= 0
        assert data["summary"]["cache_entries"] >= 0
        assert data["summary"]["memory_entries"] >= 0


class TestBundledLanguages:
    """Test bundled languages are properly configured"""
    
    def test_languages_endpoint(self):
        """Verify languages endpoint returns bundled languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        assert response.status_code == 200
        data = response.json()
        
        # Should have languages list
        assert "languages" in data
        
    def test_swahili_is_bundled(self):
        """Verify Swahili (sw) is in bundled languages"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        data = response.json()
        
        # Find Swahili in languages list
        sw_found = False
        for lang in data.get("languages", []):
            if isinstance(lang, dict) and lang.get("code") == "sw":
                sw_found = True
                break
            elif lang == "sw":
                sw_found = True
                break
        
        assert sw_found, "Swahili should be in languages list"
        
    def test_african_languages_bundled(self):
        """Verify African languages are bundled"""
        response = requests.get(f"{BASE_URL}/api/translate/languages")
        data = response.json()
        
        # Expected African languages
        african_langs = ["sw", "ha", "yo", "ig", "zu", "xh", "af", "am", "om", "so", "rw", "sn", "ny", "tw", "wo", "lg"]
        
        # Get language codes from response
        lang_codes = []
        for lang in data.get("languages", []):
            if isinstance(lang, dict):
                lang_codes.append(lang.get("code"))
            else:
                lang_codes.append(lang)
        
        # Check at least some African languages are present
        found_african = [l for l in african_langs if l in lang_codes]
        assert len(found_african) >= 10, f"Expected at least 10 African languages, found {len(found_african)}"


class TestTranslationMemory:
    """Test Translation Memory endpoints"""
    
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
        
    def test_memory_stats_endpoint(self, admin_token):
        """Test translation memory stats endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/translate/memory/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "total_entries" in data
        assert "by_language" in data
        
    def test_memory_lookup_endpoint(self):
        """Test translation memory lookup endpoint"""
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


class TestQualityScoring:
    """Test Translation Quality Scoring endpoints"""
    
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
        
    def test_quality_score_endpoint(self):
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
        assert data["quality"]["overall_score"] >= 0
        assert data["quality"]["overall_score"] <= 100
        
    def test_quality_stats_requires_admin(self):
        """Verify quality stats requires admin auth"""
        response = requests.get(f"{BASE_URL}/api/translate/quality/stats")
        assert response.status_code == 403
        
    def test_quality_stats_with_admin(self, admin_token):
        """Test quality stats with admin authentication"""
        response = requests.get(
            f"{BASE_URL}/api/translate/quality/stats",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "total_scored" in data
        assert "by_language" in data
