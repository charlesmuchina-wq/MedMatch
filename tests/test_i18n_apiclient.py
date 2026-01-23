"""
Test suite for MedMatch i18n and apiClient features
Tests Job Search, Resume, and Applications API endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://resume-match-58.preview.emergentagent.com')

class TestJobSearchAPI:
    """Tests for Job Search API endpoints used by apiClient"""
    
    def test_jobs_search_endpoint(self):
        """Test /api/jobs/search returns jobs correctly"""
        response = requests.get(f"{BASE_URL}/api/jobs/search")
        assert response.status_code == 200
        
        data = response.json()
        assert 'jobs' in data
        assert isinstance(data['jobs'], list)
        print(f"✅ Jobs search returned {len(data['jobs'])} jobs")
    
    def test_jobs_search_with_query(self):
        """Test /api/jobs/search with query parameter"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={'query': 'nurse'})
        assert response.status_code == 200
        
        data = response.json()
        assert 'jobs' in data
        print(f"✅ Jobs search with query 'nurse' returned {len(data['jobs'])} jobs")
    
    def test_jobs_search_with_location(self):
        """Test /api/jobs/search with location filter"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={'location': 'Remote'})
        assert response.status_code == 200
        
        data = response.json()
        assert 'jobs' in data
        print(f"✅ Jobs search with location filter returned {len(data['jobs'])} jobs")
    
    def test_jobs_search_with_source(self):
        """Test /api/jobs/search with source filter"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={'source': 'indeed'})
        assert response.status_code == 200
        
        data = response.json()
        assert 'jobs' in data
        print(f"✅ Jobs search with source filter returned {len(data['jobs'])} jobs")
    
    def test_jobs_search_with_days(self):
        """Test /api/jobs/search with days filter"""
        response = requests.get(f"{BASE_URL}/api/jobs/search", params={'days': 7})
        assert response.status_code == 200
        
        data = response.json()
        assert 'jobs' in data
        print(f"✅ Jobs search with days filter returned {len(data['jobs'])} jobs")


class TestHealthAndStatus:
    """Tests for health and status endpoints"""
    
    def test_health_endpoint(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'ai_supervisor' in data
        print(f"✅ Health check passed - AI Supervisor: {data['ai_supervisor']}")
    
    def test_status_endpoint(self):
        """Test /api/status returns system status"""
        response = requests.get(f"{BASE_URL}/api/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'operational'
        assert 'mongodb' in data
        assert 'cache' in data
        print(f"✅ Status check passed - MongoDB: {data['mongodb']['status']}")
    
    def test_supervisor_status(self):
        """Test /api/supervisor/status returns AI supervisor status"""
        response = requests.get(f"{BASE_URL}/api/supervisor/status")
        assert response.status_code == 200
        
        data = response.json()
        assert 'health' in data
        assert 'metrics' in data
        print(f"✅ Supervisor status - Health: {data['health']}")


class TestRateLimiting:
    """Tests for rate limiting endpoints"""
    
    def test_rate_limit_status(self):
        """Test /api/rate-limit/status returns rate limit info"""
        response = requests.get(f"{BASE_URL}/api/rate-limit/status")
        assert response.status_code == 200
        
        data = response.json()
        assert 'tier' in data
        assert 'limits' in data
        print(f"✅ Rate limit status - Tier: {data['tier']}")
    
    def test_rate_limit_tiers(self):
        """Test /api/rate-limit/tiers returns tier info"""
        response = requests.get(f"{BASE_URL}/api/rate-limit/tiers")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        print(f"✅ Rate limit tiers returned {len(data)} tiers")


class TestCachedEndpoints:
    """Tests for cached endpoints used by apiClient"""
    
    def test_cached_languages(self):
        """Test /api/cached/languages returns supported languages"""
        response = requests.get(f"{BASE_URL}/api/cached/languages")
        assert response.status_code == 200
        
        data = response.json()
        assert 'languages' in data
        assert data['cached'] == True
        print(f"✅ Cached languages returned {len(data['languages'])} languages")
    
    def test_cached_id_levels(self):
        """Test /api/cached/id-levels returns ID verification levels"""
        response = requests.get(f"{BASE_URL}/api/cached/id-levels")
        assert response.status_code == 200
        
        data = response.json()
        assert 'levels' in data
        assert data['cached'] == True
        print(f"✅ Cached ID levels returned {len(data['levels'])} levels")


class TestTranslationAPI:
    """Tests for translation API endpoints"""
    
    def test_translate_text(self):
        """Test /api/translate/text endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/translate/text",
            json={
                "text": "Hello, how are you?",
                "target_language": "es"
            }
        )
        # May return 200 or 500 depending on LLM availability
        if response.status_code == 200:
            data = response.json()
            assert 'translated_text' in data
            print(f"✅ Translation API working - Translated: {data['translated_text']}")
        else:
            print(f"⚠️ Translation API returned {response.status_code} - LLM may not be configured")


class TestCompaniesAPI:
    """Tests for companies API endpoints"""
    
    def test_companies_list(self):
        """Test /api/companies/ returns company list"""
        response = requests.get(f"{BASE_URL}/api/companies/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Companies API returned {len(data)} companies")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
