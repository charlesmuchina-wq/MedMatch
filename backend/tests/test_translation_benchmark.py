"""
Translation Benchmark API Tests
Tests the translation QA endpoints and verifies language coverage
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestTranslationBenchmark:
    """Tests for the Translation QA Benchmark API"""
    
    def test_benchmark_endpoint_accessible(self):
        """Test that benchmark endpoint is accessible"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "summary" in data
        assert "languages" in data
        print(f"✓ Benchmark endpoint accessible")
    
    def test_overall_coverage_above_99_percent(self):
        """Test that overall translation coverage is above 99%"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        overall_avg = data["summary"]["overall_average_coverage"]
        assert overall_avg >= 99.0, f"Overall coverage {overall_avg}% is below 99%"
        print(f"✓ Overall coverage: {overall_avg}%")
    
    def test_all_32_languages_present(self):
        """Test that all 32 languages are present"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        total_languages = data["summary"]["total_languages"]
        assert total_languages >= 32, f"Expected 32 languages, got {total_languages}"
        print(f"✓ Total languages: {total_languages}")
    
    def test_tier1_languages_above_98_percent(self):
        """Test Tier 1 languages (Must Have) are above 98%"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        tier1 = data["tiers"]["tier1"]
        avg_coverage = tier1["average_coverage"]
        assert avg_coverage >= 98, f"Tier 1 coverage {avg_coverage}% is below 98%"
        
        # Check individual languages
        tier1_languages = ["es", "fr", "de", "ja", "zh", "ar", "pt-BR"]
        for lang in tier1_languages:
            if lang in data["languages"]:
                coverage = data["languages"][lang]["coverage"]
                assert coverage >= 98, f"Tier 1 language {lang} coverage {coverage}% is below 98%"
        print(f"✓ Tier 1 average coverage: {avg_coverage}%")
    
    def test_tier2_languages_above_95_percent(self):
        """Test Tier 2 languages (High Value) are above 95%"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        tier2 = data["tiers"]["tier2"]
        avg_coverage = tier2["average_coverage"]
        assert avg_coverage >= 95, f"Tier 2 coverage {avg_coverage}% is below 95%"
        print(f"✓ Tier 2 average coverage: {avg_coverage}%")
    
    def test_african_languages_above_90_percent(self):
        """Test African languages (Tier 3) are above 90%"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        tier3 = data["tiers"]["tier3"]
        avg_coverage = tier3["average_coverage"]
        assert avg_coverage >= 90, f"Tier 3 coverage {avg_coverage}% is below 90%"
        
        # Check specific African languages
        african_langs = ["sw", "ha", "yo", "zu", "am", "xh"]
        failing_langs = []
        for lang in african_langs:
            if lang in data["languages"]:
                coverage = data["languages"][lang]["coverage"]
                grade = data["languages"][lang]["grade"]
                print(f"  - {lang}: {coverage}% (Grade: {grade})")
                if coverage < 90:
                    failing_langs.append(f"{lang}: {coverage}%")
        
        assert len(failing_langs) == 0, f"These African languages are below 90%: {failing_langs}"
        print(f"✓ Tier 3 (African) average coverage: {avg_coverage}%")
    
    def test_all_languages_have_grade_a(self):
        """Test that all languages have Grade A or A+"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        non_a_grades = []
        for lang_code, lang_data in data["languages"].items():
            grade = lang_data.get("grade", "F")
            if grade not in ["A", "A+"]:
                non_a_grades.append(f"{lang_code}: {grade} ({lang_data.get('coverage')}%)")
        
        if non_a_grades:
            print(f"⚠ Languages without Grade A: {non_a_grades}")
        assert len(non_a_grades) == 0, f"These languages don't have Grade A: {non_a_grades}"
        print(f"✓ All languages have Grade A or A+")
    
    def test_no_alerts_triggered(self):
        """Test that no coverage alerts are triggered"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        alerts = data.get("alerts", [])
        if alerts:
            print(f"⚠ Alerts triggered: {alerts}")
        assert len(alerts) == 0, f"Coverage alerts triggered: {alerts}"
        print(f"✓ No alerts triggered")
    
    def test_industry_comparison_data_present(self):
        """Test that industry comparison data is present"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        
        industry = data.get("industry_comparison", {})
        assert "duolingo" in industry
        assert "airbnb" in industry
        print(f"✓ Industry comparison data present")


class TestTranslationQA:
    """Tests for Translation QA endpoints"""
    
    def test_qa_latest_endpoint(self):
        """Test QA latest endpoint"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/latest")
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert "summary" in data
        print(f"✓ QA latest endpoint working")
    
    def test_qa_score_endpoint(self):
        """Test QA score endpoint"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/score")
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "language_scores" in data
        print(f"✓ QA score endpoint working, overall: {data['overall_score']}")
    
    def test_dashboard_summary_endpoint(self):
        """Test dashboard summary endpoint"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/dashboard-summary")
        assert response.status_code == 200
        data = response.json()
        assert "overall_score" in data
        assert "health" in data
        assert "language_status" in data
        print(f"✓ Dashboard summary: health={data['health']}, score={data['overall_score']}")


class TestLanguageSpecificCoverage:
    """Tests for specific language translation coverage - using benchmark endpoint"""
    
    def test_swahili_coverage(self):
        """Test Swahili (sw) translation coverage via benchmark"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        coverage = data["languages"]["sw"]["coverage"]
        grade = data["languages"]["sw"]["grade"]
        assert coverage >= 99, f"Swahili coverage {coverage}% is below 99%"
        assert grade in ["A", "A+"], f"Swahili grade {grade} is not A or A+"
        print(f"✓ Swahili: coverage={coverage}%, grade={grade}")
    
    def test_hausa_coverage(self):
        """Test Hausa (ha) translation coverage via benchmark"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        coverage = data["languages"]["ha"]["coverage"]
        grade = data["languages"]["ha"]["grade"]
        assert coverage >= 99, f"Hausa coverage {coverage}% is below 99%"
        assert grade in ["A", "A+"], f"Hausa grade {grade} is not A or A+"
        print(f"✓ Hausa: coverage={coverage}%, grade={grade}")
    
    def test_arabic_coverage(self):
        """Test Arabic (ar) RTL language coverage via benchmark"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        coverage = data["languages"]["ar"]["coverage"]
        grade = data["languages"]["ar"]["grade"]
        assert coverage >= 99, f"Arabic coverage {coverage}% is below 99%"
        assert grade in ["A", "A+"], f"Arabic grade {grade} is not A or A+"
        print(f"✓ Arabic (RTL): coverage={coverage}%, grade={grade}")
    
    def test_japanese_coverage(self):
        """Test Japanese (ja) coverage via benchmark"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/benchmark")
        assert response.status_code == 200
        data = response.json()
        coverage = data["languages"]["ja"]["coverage"]
        grade = data["languages"]["ja"]["grade"]
        assert coverage >= 99, f"Japanese coverage {coverage}% is below 99%"
        assert grade in ["A", "A+"], f"Japanese grade {grade} is not A or A+"
        print(f"✓ Japanese: coverage={coverage}%, grade={grade}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
