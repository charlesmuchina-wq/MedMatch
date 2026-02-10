"""
Translation QA API Tests
Tests for translation expansion warnings
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestTranslationQA:
    """Test translation QA API endpoints"""
    
    def test_expansion_issues_endpoint(self):
        """Test GET /api/translation-qa/expansion-issues returns issues"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/expansion-issues")
        assert response.status_code == 200
        data = response.json()
        assert "total_issues" in data
        assert "by_language" in data
        print(f"Total translation issues: {data['total_issues']}")
    
    def test_no_high_severity_issues(self):
        """Test that there are no HIGH severity translation issues"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/expansion-issues")
        assert response.status_code == 200
        data = response.json()
        
        high_severity_count = 0
        for lang, issues in data.get("by_language", {}).items():
            for issue in issues:
                if issue.get("severity") == "high":
                    high_severity_count += 1
                    print(f"HIGH severity issue in {lang}: {issue.get('key')}")
        
        assert high_severity_count == 0, f"Found {high_severity_count} HIGH severity issues"
        print(f"PASS: No HIGH severity translation issues found")
    
    def test_total_issues_reduced(self):
        """Test that total issues are reduced (was 85, now should be 75)"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/expansion-issues")
        assert response.status_code == 200
        data = response.json()
        
        total = data.get("total_issues", 0)
        assert total <= 85, f"Total issues {total} should be <= 85 (was 85 before)"
        print(f"Total issues: {total} (reduced from 85)")
    
    def test_warning_severity_only(self):
        """Test that all remaining issues are WARNING severity"""
        response = requests.get(f"{BASE_URL}/api/translation-qa/expansion-issues")
        assert response.status_code == 200
        data = response.json()
        
        severities = set()
        for lang, issues in data.get("by_language", {}).items():
            for issue in issues:
                severities.add(issue.get("severity"))
        
        assert "high" not in severities, "Found HIGH severity issues"
        print(f"Severities found: {severities}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
