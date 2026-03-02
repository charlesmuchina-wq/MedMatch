"""
Phase 2 Features Testing - DEI Analytics, Talent CRM, and Gap Assessment
Tests: /api/dei-analytics/*, /api/talent-crm/*
Also verifies frontend pages: /dei-analytics, /talent-crm
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://future-comms.preview.emergentagent.com')

class TestHealthAndAuth:
    """Basic health and authentication tests"""
    
    def test_api_health(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("PASS: API health check - 200")
    
    def test_admin_login(self):
        """Login as admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"PASS: Admin login - got token")
        return data["access_token"]


class TestDEIAnalytics:
    """DEI Analytics endpoint tests"""
    
    def test_get_dei_metrics(self):
        """GET /api/dei-analytics/metrics - returns DEI metrics with benchmarks"""
        response = requests.get(f"{BASE_URL}/api/dei-analytics/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "total_applicants" in data
        assert "total_users" in data
        assert "gender_distribution" in data
        assert "geographic_diversity" in data
        assert "pipeline_by_stage" in data
        assert "role_distribution" in data
        assert "dei_score" in data
        assert "benchmarks" in data
        assert "trends" in data
        assert "generated_at" in data
        
        # Validate benchmarks structure
        benchmarks = data["benchmarks"]
        assert "gender_parity_index" in benchmarks
        assert "geographic_diversity_index" in benchmarks
        assert "pipeline_equity_ratio" in benchmarks
        
        # Validate trends structure
        trends = data["trends"]
        assert "gender_parity_change" in trends
        assert "diversity_hires_change" in trends
        assert "inclusion_score_change" in trends
        
        print(f"PASS: DEI metrics - dei_score={data['dei_score']}, total_users={data['total_users']}")
    
    def test_get_dei_goals(self):
        """GET /api/dei-analytics/goals - returns DEI goals and progress"""
        response = requests.get(f"{BASE_URL}/api/dei-analytics/goals")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "goals" in data
        goals = data["goals"]
        assert isinstance(goals, list)
        assert len(goals) >= 1
        
        # Validate goal structure
        goal = goals[0]
        assert "name" in goal
        assert "target" in goal
        assert "current" in goal
        assert "unit" in goal
        assert "category" in goal
        
        print(f"PASS: DEI goals - {len(goals)} goals returned")


class TestTalentCRM:
    """Talent CRM endpoint tests - pools, campaigns, notes"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Store test data for cleanup"""
        self.created_pool_id = None
        self.created_campaign_id = None
        self.test_candidate_id = "test_candidate_123"
    
    def test_get_talent_pools_empty(self):
        """GET /api/talent-crm/pools - list talent pools"""
        response = requests.get(f"{BASE_URL}/api/talent-crm/pools")
        assert response.status_code == 200
        data = response.json()
        assert "pools" in data
        assert isinstance(data["pools"], list)
        print(f"PASS: Get talent pools - {len(data['pools'])} pools found")
    
    def test_create_talent_pool(self):
        """POST /api/talent-crm/pools - create talent pool"""
        pool_data = {
            "name": "TEST_Senior_Engineers_Pool",
            "description": "Pool for senior engineering candidates",
            "tags": ["engineering", "senior", "fullstack"]
        }
        response = requests.post(
            f"{BASE_URL}/api/talent-crm/pools",
            json=pool_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert "pool_id" in data
        assert data["name"] == pool_data["name"]
        assert data["description"] == pool_data["description"]
        assert data["tags"] == pool_data["tags"]
        assert "created_at" in data
        assert "candidates" in data
        
        self.created_pool_id = data["pool_id"]
        print(f"PASS: Create talent pool - pool_id={data['pool_id']}")
        return data["pool_id"]
    
    def test_create_and_verify_pool_persistence(self):
        """Create pool and verify it persists with GET"""
        # Create
        pool_data = {
            "name": "TEST_Data_Scientists_Pool",
            "description": "ML/AI candidates",
            "tags": ["ml", "ai", "data"]
        }
        create_response = requests.post(
            f"{BASE_URL}/api/talent-crm/pools",
            json=pool_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_response.status_code == 200
        created = create_response.json()
        pool_id = created["pool_id"]
        
        # Verify persistence
        get_response = requests.get(f"{BASE_URL}/api/talent-crm/pools")
        assert get_response.status_code == 200
        pools = get_response.json()["pools"]
        
        # Find our created pool
        found = False
        for pool in pools:
            if pool.get("pool_id") == pool_id:
                found = True
                assert pool["name"] == pool_data["name"]
                break
        
        assert found, f"Created pool {pool_id} not found in GET response"
        print(f"PASS: Pool persistence verified - pool_id={pool_id}")
    
    def test_get_campaigns_empty(self):
        """GET /api/talent-crm/campaigns - list campaigns"""
        response = requests.get(f"{BASE_URL}/api/talent-crm/campaigns")
        assert response.status_code == 200
        data = response.json()
        assert "campaigns" in data
        assert isinstance(data["campaigns"], list)
        print(f"PASS: Get campaigns - {len(data['campaigns'])} campaigns found")
    
    def test_create_nurture_campaign(self):
        """POST /api/talent-crm/campaigns - create nurture campaign"""
        # First create a pool to reference
        pool_response = requests.post(
            f"{BASE_URL}/api/talent-crm/pools",
            json={"name": "TEST_Campaign_Pool", "description": "For campaign testing", "tags": []},
            headers={"Content-Type": "application/json"}
        )
        pool_id = pool_response.json()["pool_id"]
        
        campaign_data = {
            "name": "TEST_Engagement_Campaign",
            "pool_id": pool_id,
            "message_template": "Hi {{name}}, we have exciting opportunities for you!",
            "schedule": "weekly"
        }
        response = requests.post(
            f"{BASE_URL}/api/talent-crm/campaigns",
            json=campaign_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert "campaign_id" in data
        assert data["name"] == campaign_data["name"]
        assert data["pool_id"] == pool_id
        assert data["message_template"] == campaign_data["message_template"]
        assert data["schedule"] == campaign_data["schedule"]
        assert data["status"] == "draft"
        assert "sent_count" in data
        assert "open_count" in data
        assert "reply_count" in data
        
        print(f"PASS: Create campaign - campaign_id={data['campaign_id']}")
    
    def test_create_and_verify_campaign_persistence(self):
        """Create campaign and verify it persists with GET"""
        # Create pool first
        pool_response = requests.post(
            f"{BASE_URL}/api/talent-crm/pools",
            json={"name": "TEST_Persistence_Pool", "description": "", "tags": []},
            headers={"Content-Type": "application/json"}
        )
        pool_id = pool_response.json()["pool_id"]
        
        # Create campaign
        campaign_data = {
            "name": "TEST_Verify_Campaign",
            "pool_id": pool_id,
            "message_template": "Testing persistence",
            "schedule": "immediate"
        }
        create_response = requests.post(
            f"{BASE_URL}/api/talent-crm/campaigns",
            json=campaign_data,
            headers={"Content-Type": "application/json"}
        )
        assert create_response.status_code == 200
        campaign_id = create_response.json()["campaign_id"]
        
        # Verify persistence
        get_response = requests.get(f"{BASE_URL}/api/talent-crm/campaigns")
        assert get_response.status_code == 200
        campaigns = get_response.json()["campaigns"]
        
        found = False
        for campaign in campaigns:
            if campaign.get("campaign_id") == campaign_id:
                found = True
                assert campaign["name"] == campaign_data["name"]
                break
        
        assert found, f"Created campaign {campaign_id} not found in GET response"
        print(f"PASS: Campaign persistence verified - campaign_id={campaign_id}")
    
    def test_add_candidate_note(self):
        """POST /api/talent-crm/notes - add candidate note"""
        note_data = {
            "candidate_id": "test_candidate_456",
            "note": "Excellent technical interview, strong Python skills",
            "note_type": "interview"
        }
        response = requests.post(
            f"{BASE_URL}/api/talent-crm/notes",
            json=note_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        
        # Validate response
        assert "note_id" in data
        assert data["candidate_id"] == note_data["candidate_id"]
        assert data["note"] == note_data["note"]
        assert data["note_type"] == note_data["note_type"]
        assert "created_at" in data
        
        print(f"PASS: Add candidate note - note_id={data['note_id']}")
        return data["candidate_id"]
    
    def test_get_candidate_notes(self):
        """GET /api/talent-crm/notes/{candidate_id} - get candidate notes"""
        candidate_id = "test_candidate_789"
        
        # First create a note
        requests.post(
            f"{BASE_URL}/api/talent-crm/notes",
            json={"candidate_id": candidate_id, "note": "Phone screen completed", "note_type": "general"},
            headers={"Content-Type": "application/json"}
        )
        
        # Now get notes
        response = requests.get(f"{BASE_URL}/api/talent-crm/notes/{candidate_id}")
        assert response.status_code == 200
        data = response.json()
        
        assert "notes" in data
        assert isinstance(data["notes"], list)
        assert len(data["notes"]) >= 1
        
        # Validate note structure
        note = data["notes"][0]
        assert "candidate_id" in note
        assert "note" in note
        assert "note_type" in note
        assert "created_at" in note
        
        print(f"PASS: Get candidate notes - {len(data['notes'])} notes for candidate {candidate_id}")


class TestHiringMetrics:
    """Hiring metrics endpoint tests (from ai_talent.py)"""
    
    def test_get_hiring_metrics(self):
        """GET /api/ai-talent/hiring-metrics - get recruitment metrics"""
        response = requests.get(f"{BASE_URL}/api/ai-talent/hiring-metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert "total_applications" in data
        assert "hired" in data
        assert "rejected" in data
        assert "in_progress" in data
        assert "hire_rate" in data
        assert "total_jobs" in data
        assert "active_jobs" in data
        assert "pipeline" in data
        assert "avg_time_to_hire_days" in data
        assert "avg_cost_per_hire" in data
        assert "source_effectiveness" in data
        
        # Validate source_effectiveness structure
        sources = data["source_effectiveness"]
        assert "direct" in sources
        assert "referral" in sources
        assert "job_board" in sources
        assert "social" in sources
        
        print(f"PASS: Hiring metrics - applications={data['total_applications']}, hire_rate={data['hire_rate']}%")


class TestFrontendPageAccess:
    """Test that frontend pages are accessible"""
    
    def test_dei_analytics_page(self):
        """Verify /dei-analytics page is accessible"""
        response = requests.get(f"{BASE_URL}/dei-analytics", allow_redirects=True)
        # Frontend routes return 200 (served by React)
        assert response.status_code == 200
        print("PASS: /dei-analytics page accessible")
    
    def test_talent_crm_page(self):
        """Verify /talent-crm page is accessible"""
        response = requests.get(f"{BASE_URL}/talent-crm", allow_redirects=True)
        assert response.status_code == 200
        print("PASS: /talent-crm page accessible")
    
    def test_hiring_metrics_page(self):
        """Verify /hiring-metrics page is accessible"""
        response = requests.get(f"{BASE_URL}/hiring-metrics", allow_redirects=True)
        assert response.status_code == 200
        print("PASS: /hiring-metrics page accessible")
    
    def test_ai_scoring_page(self):
        """Verify /ai-scoring page is accessible"""
        response = requests.get(f"{BASE_URL}/ai-scoring", allow_redirects=True)
        assert response.status_code == 200
        print("PASS: /ai-scoring page accessible")
    
    def test_jd_generator_page(self):
        """Verify /jd-generator page is accessible"""
        response = requests.get(f"{BASE_URL}/jd-generator", allow_redirects=True)
        assert response.status_code == 200
        print("PASS: /jd-generator page accessible")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
