"""
Domain-Aware Routing Tests - Iteration 204
Tests the domain configuration and routing for the multi-portal communication suite.

Domains tested:
- aikarau.com (ecosystem)
- medmatch.aikarau.com (company/recruiter)
- careers.aikarau.com & jobs.aikarau.com (job seekers)
- connect.aikarau.com & meet.aikarau.com (KARAU meetings)
- enzi.aikarau.com & enzilink.com (ENZI messenger)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestDomainConfig:
    """Test /api/portal/domain-config endpoint"""

    def test_domain_config_default(self):
        """GET /api/portal/domain-config returns ecosystem for no hostname"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "ecosystem"
        assert data["hostname"] == "default"
        assert "all_domains" in data
        # Verify all expected domains are present
        all_domains = data["all_domains"]
        expected_domains = [
            "aikarau.com", "ai.karau.com", "medmatch.aikarau.com",
            "careers.aikarau.com", "jobs.aikarau.com",
            "connect.aikarau.com", "meet.aikarau.com",
            "enzi.aikarau.com", "enzilink.com"
        ]
        for domain in expected_domains:
            assert domain in all_domains, f"Missing domain: {domain}"
        print("PASS: Default domain config returns ecosystem with all domains")

    def test_domain_config_enzilink(self):
        """GET /api/portal/domain-config?hostname=enzilink.com returns enzi portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=enzilink.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "enzi"
        assert data["config"]["title"] == "ENZI Messenger"
        assert data["config"]["audience"] == "all"
        assert data["config"]["standalone"] == True
        assert data["hostname"] == "enzilink.com"
        print("PASS: enzilink.com returns enzi portal with standalone=True")

    def test_domain_config_enzi_aikarau(self):
        """GET /api/portal/domain-config?hostname=enzi.aikarau.com returns enzi portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=enzi.aikarau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "enzi"
        assert data["config"]["title"] == "ENZI Messenger"
        assert data["hostname"] == "enzi.aikarau.com"
        print("PASS: enzi.aikarau.com returns enzi portal")

    def test_domain_config_meet_aikarau(self):
        """GET /api/portal/domain-config?hostname=meet.aikarau.com returns karau portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=meet.aikarau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "karau"
        assert data["config"]["title"] == "AI KARAU Meet"
        assert data["config"]["audience"] == "all"
        assert data["hostname"] == "meet.aikarau.com"
        print("PASS: meet.aikarau.com returns karau portal")

    def test_domain_config_connect_aikarau(self):
        """GET /api/portal/domain-config?hostname=connect.aikarau.com returns karau portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=connect.aikarau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "karau"
        assert data["config"]["title"] == "AI KARAU Connect"
        assert data["hostname"] == "connect.aikarau.com"
        print("PASS: connect.aikarau.com returns karau portal")

    def test_domain_config_medmatch(self):
        """GET /api/portal/domain-config?hostname=medmatch.aikarau.com returns medmatch portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=medmatch.aikarau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "medmatch"
        assert data["config"]["audience"] == "company"
        assert "Enterprise Recruitment Platform" in data["config"]["title"]
        assert data["hostname"] == "medmatch.aikarau.com"
        print("PASS: medmatch.aikarau.com returns medmatch portal with audience=company")

    def test_domain_config_careers(self):
        """GET /api/portal/domain-config?hostname=careers.aikarau.com returns careers portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=careers.aikarau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "careers"
        assert data["config"]["audience"] == "jobseeker"
        assert data["config"]["title"] == "AI KARAU Careers"
        assert data["hostname"] == "careers.aikarau.com"
        print("PASS: careers.aikarau.com returns careers portal for jobseekers")

    def test_domain_config_jobs(self):
        """GET /api/portal/domain-config?hostname=jobs.aikarau.com returns careers portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=jobs.aikarau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "careers"
        assert data["config"]["audience"] == "jobseeker"
        assert data["config"]["title"] == "AI KARAU Jobs"
        assert data["hostname"] == "jobs.aikarau.com"
        print("PASS: jobs.aikarau.com returns careers portal for jobseekers")

    def test_domain_config_ecosystem_main(self):
        """GET /api/portal/domain-config?hostname=aikarau.com returns ecosystem portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=aikarau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "ecosystem"
        assert data["config"]["title"] == "MedMatch-AI KARAU"
        assert data["config"]["audience"] == "recruiter"
        assert data["hostname"] == "aikarau.com"
        print("PASS: aikarau.com returns ecosystem portal")

    def test_domain_config_ai_karau(self):
        """GET /api/portal/domain-config?hostname=ai.karau.com returns ecosystem portal"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=ai.karau.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "ecosystem"
        assert data["config"]["title"] == "AI KARAU Ecosystem"
        assert data["hostname"] == "ai.karau.com"
        print("PASS: ai.karau.com returns ecosystem portal")

    def test_domain_config_unknown_hostname(self):
        """GET /api/portal/domain-config?hostname=unknown.com returns ecosystem default"""
        response = requests.get(f"{BASE_URL}/api/portal/domain-config?hostname=unknown.example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["config"]["portal"] == "ecosystem"
        assert data["hostname"] == "unknown.example.com"
        print("PASS: Unknown hostname returns ecosystem fallback")


class TestPortalPackages:
    """Test portal package endpoints"""

    def test_get_packages(self):
        """GET /api/portal/packages returns available packages"""
        response = requests.get(f"{BASE_URL}/api/portal/packages")
        assert response.status_code == 200
        data = response.json()
        assert "packages" in data
        assert "portals" in data
        
        packages = {p["id"]: p for p in data["packages"]}
        assert "standard" in packages
        assert "medmatch_standalone" in packages
        assert "enterprise" in packages
        
        # Verify standard package auto-bundles KARAU+ENZI
        standard = packages["standard"]
        assert "karau" in standard["portals"]
        assert "enzi" in standard["portals"]
        assert standard["name"] == "AI KARAU + ENZI"
        
        # Verify portal info exists
        portal_info = data["portals"]
        assert "medmatch" in portal_info
        assert "karau" in portal_info
        assert "enzi" in portal_info
        print("PASS: Portal packages endpoint returns all packages with auto-bundling info")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
