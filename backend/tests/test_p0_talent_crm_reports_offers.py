"""
P0 Features Testing: Talent CRM, Report Builder, Offer Management
Tests the 3 newly built pages that were previously placeholders:
- Talent CRM (/talent-crm): contacts, pipeline, pools, campaigns, interactions, stage management
- Report Builder (/report-builder): report generation, visual charts, deletion
- Offer Management (/offer-management): offers, status workflows, AI letter generation
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://karau-enzi-nexus.preview.emergentagent.com")


class TestAuth:
    """Authentication to get session cookie for protected endpoints"""
    
    @pytest.fixture(scope="class")
    def session(self):
        """Create authenticated session"""
        s = requests.Session()
        s.headers.update({"Content-Type": "application/json"})
        return s
    
    @pytest.fixture(scope="class")
    def auth_token(self, session):
        """Login as admin and get auth token"""
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data, f"No access_token in response: {data}"
        token = data["access_token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        print(f"✅ AUTH: Login successful, got token: {token[:20]}...")
        return token


class TestTalentCRMContacts(TestAuth):
    """Talent CRM - Contacts CRUD, Pipeline, Stage Management"""
    
    def test_get_contacts(self, session, auth_token):
        """GET /api/talent-crm/contacts - List all contacts"""
        response = session.get(f"{BASE_URL}/api/talent-crm/contacts")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "contacts" in data, f"Expected 'contacts' key, got: {data.keys()}"
        print(f"✅ GET contacts: {len(data['contacts'])} contacts found")
    
    def test_get_pipeline_stats(self, session, auth_token):
        """GET /api/talent-crm/pipeline - Get pipeline statistics"""
        response = session.get(f"{BASE_URL}/api/talent-crm/pipeline")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "stages" in data, f"Expected 'stages' key, got: {data.keys()}"
        assert "total" in data, f"Expected 'total' key, got: {data.keys()}"
        print(f"✅ GET pipeline: total={data['total']}, stages={list(data['stages'].keys())}")
    
    def test_create_contact(self, session, auth_token):
        """POST /api/talent-crm/contacts - Create new contact"""
        payload = {
            "name": "TEST_Contact_P0",
            "email": "test.p0.contact@example.com",
            "phone": "+1234567890",
            "title": "Senior Developer",
            "company": "Test Company Inc",
            "source": "manual",
            "stage": "new",
            "tags": ["python", "senior"],
            "notes": "Created during P0 testing"
        }
        response = session.post(f"{BASE_URL}/api/talent-crm/contacts", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id' in response: {data}"
        assert data["name"] == payload["name"], f"Name mismatch: {data['name']}"
        assert data["stage"] == "new", f"Stage mismatch: {data['stage']}"
        print(f"✅ POST contact: created id={data['id']}, name={data['name']}")
        # Store for later tests
        TestTalentCRMContacts.created_contact_id = data["id"]
    
    def test_search_contacts(self, session, auth_token):
        """GET /api/talent-crm/contacts?search=TEST - Search contacts"""
        response = session.get(f"{BASE_URL}/api/talent-crm/contacts?search=TEST_Contact_P0")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "contacts" in data, f"Expected 'contacts': {data}"
        # Should find our test contact
        test_contacts = [c for c in data["contacts"] if "TEST_Contact_P0" in c.get("name", "")]
        print(f"✅ SEARCH contacts: found {len(test_contacts)} matching 'TEST_Contact_P0'")
    
    def test_filter_contacts_by_stage(self, session, auth_token):
        """GET /api/talent-crm/contacts?stage=new - Filter by stage"""
        response = session.get(f"{BASE_URL}/api/talent-crm/contacts?stage=new")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "contacts" in data, f"Expected 'contacts': {data}"
        print(f"✅ FILTER by stage=new: {len(data['contacts'])} contacts in 'new' stage")
    
    def test_update_contact_stage(self, session, auth_token):
        """PUT /api/talent-crm/contacts/{id}/stage - Update contact stage"""
        contact_id = getattr(TestTalentCRMContacts, 'created_contact_id', None)
        if not contact_id:
            pytest.skip("No created contact ID available")
        
        response = session.put(
            f"{BASE_URL}/api/talent-crm/contacts/{contact_id}/stage",
            json={"stage": "screening"}
        )
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("status") == "updated" or data.get("stage") == "screening", f"Unexpected response: {data}"
        print(f"✅ UPDATE stage to 'screening': success")
    
    def test_update_contact_details(self, session, auth_token):
        """PUT /api/talent-crm/contacts/{id} - Update contact details"""
        contact_id = getattr(TestTalentCRMContacts, 'created_contact_id', None)
        if not contact_id:
            pytest.skip("No created contact ID available")
        
        response = session.put(
            f"{BASE_URL}/api/talent-crm/contacts/{contact_id}",
            json={"title": "Lead Developer", "company": "Updated Company"}
        )
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("title") == "Lead Developer" or "status" in data, f"Update may have failed: {data}"
        print(f"✅ UPDATE contact details: success")


class TestTalentCRMInteractions(TestAuth):
    """Talent CRM - Interaction Logging"""
    
    def test_add_interaction(self, session, auth_token):
        """POST /api/talent-crm/interactions - Log an interaction"""
        contact_id = getattr(TestTalentCRMContacts, 'created_contact_id', None)
        if not contact_id:
            # Create a contact first
            response = session.post(f"{BASE_URL}/api/talent-crm/contacts", json={
                "name": "TEST_Interaction_Contact",
                "email": "interaction@test.com"
            })
            if response.status_code == 200:
                contact_id = response.json().get("id")
                TestTalentCRMContacts.created_contact_id = contact_id
            else:
                pytest.skip("Could not create contact for interaction test")
        
        payload = {
            "contact_id": contact_id,
            "interaction_type": "call",
            "summary": "Initial phone screen completed",
            "outcome": "positive"
        }
        response = session.post(f"{BASE_URL}/api/talent-crm/interactions", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data or "summary" in data, f"Unexpected response: {data}"
        print(f"✅ POST interaction: logged '{payload['interaction_type']}' for contact")
    
    def test_get_interactions(self, session, auth_token):
        """GET /api/talent-crm/interactions/{contact_id} - Get contact's interactions"""
        contact_id = getattr(TestTalentCRMContacts, 'created_contact_id', None)
        if not contact_id:
            pytest.skip("No contact ID available")
        
        response = session.get(f"{BASE_URL}/api/talent-crm/interactions/{contact_id}")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "interactions" in data, f"Expected 'interactions': {data}"
        print(f"✅ GET interactions: {len(data['interactions'])} interactions for contact")


class TestTalentCRMPools(TestAuth):
    """Talent CRM - Pools Tab"""
    
    def test_get_pools(self, session, auth_token):
        """GET /api/talent-crm/pools - List all pools"""
        response = session.get(f"{BASE_URL}/api/talent-crm/pools")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "pools" in data, f"Expected 'pools' key: {data}"
        print(f"✅ GET pools: {len(data['pools'])} pools found")
    
    def test_create_pool(self, session, auth_token):
        """POST /api/talent-crm/pools - Create new pool"""
        payload = {
            "name": "TEST_P0_Senior_Devs",
            "description": "Pool for P0 testing",
            "tags": ["senior", "python"]
        }
        response = session.post(f"{BASE_URL}/api/talent-crm/pools", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "pool_id" in data, f"Expected 'pool_id': {data}"
        assert data["name"] == payload["name"], f"Name mismatch: {data}"
        print(f"✅ POST pool: created pool_id={data['pool_id']}, name={data['name']}")
        TestTalentCRMPools.created_pool_id = data["pool_id"]
    
    def test_delete_pool(self, session, auth_token):
        """DELETE /api/talent-crm/pools/{pool_id} - Delete pool"""
        pool_id = getattr(TestTalentCRMPools, 'created_pool_id', None)
        if not pool_id:
            pytest.skip("No pool ID available")
        
        response = session.delete(f"{BASE_URL}/api/talent-crm/pools/{pool_id}")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("status") == "deleted", f"Expected 'deleted' status: {data}"
        print(f"✅ DELETE pool: pool_id={pool_id} deleted")


class TestTalentCRMCampaigns(TestAuth):
    """Talent CRM - Campaigns Tab"""
    
    def test_get_campaigns(self, session, auth_token):
        """GET /api/talent-crm/campaigns - List all campaigns"""
        response = session.get(f"{BASE_URL}/api/talent-crm/campaigns")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "campaigns" in data, f"Expected 'campaigns' key: {data}"
        print(f"✅ GET campaigns: {len(data['campaigns'])} campaigns found")


class TestReportBuilder(TestAuth):
    """Report Builder - Report Generation, Charts, Deletion"""
    
    def test_get_reports(self, session, auth_token):
        """GET /api/advanced/reports - List user's reports"""
        response = session.get(f"{BASE_URL}/api/advanced/reports")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "reports" in data, f"Expected 'reports' key: {data}"
        print(f"✅ GET reports: {len(data['reports'])} reports found")
    
    def test_create_hiring_funnel_report(self, session, auth_token):
        """POST /api/advanced/reports - Create hiring funnel report"""
        payload = {
            "name": "TEST_P0_Hiring_Funnel",
            "report_type": "hiring_funnel",
            "date_range": "30d",
            "metrics": [],
            "filters": {}
        }
        response = session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id': {data}"
        assert "data" in data, f"Expected 'data' (report results): {data}"
        assert data["report_type"] == "hiring_funnel", f"Type mismatch: {data}"
        # Check report data has funnel stages
        report_data = data.get("data", {})
        assert "stages" in report_data or "funnel" in report_data, f"Expected funnel data: {report_data}"
        print(f"✅ POST hiring_funnel report: id={data['id']}, has_data={bool(report_data)}")
        TestReportBuilder.created_report_id = data["id"]
    
    def test_create_dei_report(self, session, auth_token):
        """POST /api/advanced/reports - Create DEI report"""
        payload = {
            "name": "TEST_P0_DEI_Report",
            "report_type": "dei",
            "date_range": "90d",
            "metrics": [],
            "filters": {}
        }
        response = session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id': {data}"
        report_data = data.get("data", {})
        # DEI report should have gender distribution
        assert "gender_distribution" in report_data or "summary" in report_data, f"Expected DEI data: {report_data}"
        print(f"✅ POST dei report: id={data['id']}, has_gender_data={'gender_distribution' in report_data}")
    
    def test_create_source_analysis_report(self, session, auth_token):
        """POST /api/advanced/reports - Create source analysis report"""
        payload = {
            "name": "TEST_P0_Source_Analysis",
            "report_type": "source",
            "date_range": "30d",
            "metrics": [],
            "filters": {}
        }
        response = session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id': {data}"
        report_data = data.get("data", {})
        assert "sources" in report_data or "source_quality" in report_data, f"Expected source data: {report_data}"
        print(f"✅ POST source report: id={data['id']}, has_sources={'sources' in report_data}")
    
    def test_create_time_series_report(self, session, auth_token):
        """POST /api/advanced/reports - Create time series report"""
        payload = {
            "name": "TEST_P0_Time_Series",
            "report_type": "time_series",
            "date_range": "90d",
            "metrics": [],
            "filters": {}
        }
        response = session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id': {data}"
        report_data = data.get("data", {})
        assert "monthly" in report_data, f"Expected monthly time series data: {report_data}"
        print(f"✅ POST time_series report: id={data['id']}, monthly_points={len(report_data.get('monthly', []))}")
    
    def test_create_offer_analysis_report(self, session, auth_token):
        """POST /api/advanced/reports - Create offer analysis report"""
        payload = {
            "name": "TEST_P0_Offer_Analysis",
            "report_type": "offer_analysis",
            "date_range": "30d",
            "metrics": [],
            "filters": {}
        }
        response = session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id': {data}"
        report_data = data.get("data", {})
        assert "by_status" in report_data or "summary" in report_data, f"Expected offer data: {report_data}"
        print(f"✅ POST offer_analysis report: id={data['id']}")
    
    def test_delete_report(self, session, auth_token):
        """DELETE /api/advanced/reports/{id} - Delete report"""
        report_id = getattr(TestReportBuilder, 'created_report_id', None)
        if not report_id:
            pytest.skip("No report ID available")
        
        response = session.delete(f"{BASE_URL}/api/advanced/reports/{report_id}")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("status") == "deleted", f"Expected 'deleted': {data}"
        print(f"✅ DELETE report: id={report_id} deleted")


class TestOfferManagement(TestAuth):
    """Offer Management - CRUD, Status Workflow, AI Letter Generation"""
    
    def test_get_offers(self, session, auth_token):
        """GET /api/advanced/offers - List user's offers"""
        response = session.get(f"{BASE_URL}/api/advanced/offers")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "offers" in data, f"Expected 'offers' key: {data}"
        print(f"✅ GET offers: {len(data['offers'])} offers found")
    
    def test_create_offer(self, session, auth_token):
        """POST /api/advanced/offers - Create new offer"""
        payload = {
            "candidate_id": "",
            "candidate_name": "TEST_P0_Candidate",
            "job_id": "",
            "job_title": "Senior Software Engineer",
            "salary": 150000,
            "currency": "USD",
            "start_date": "2026-03-01",
            "benefits": ["Health", "401k", "RSU"],
            "notes": "P0 testing offer",
            "equity": "0.15%",
            "bonus": 25000,
            "hiring_manager": "Jane Smith"
        }
        response = session.post(f"{BASE_URL}/api/advanced/offers", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "id" in data, f"Expected 'id': {data}"
        assert data["status"] == "draft", f"Initial status should be 'draft': {data['status']}"
        assert data["salary"] == 150000, f"Salary mismatch: {data['salary']}"
        assert data["bonus"] == 25000, f"Bonus mismatch: {data['bonus']}"
        assert data["equity"] == "0.15%", f"Equity mismatch: {data['equity']}"
        print(f"✅ POST offer: id={data['id']}, status={data['status']}, salary={data['salary']}")
        TestOfferManagement.created_offer_id = data["id"]
    
    def test_get_single_offer(self, session, auth_token):
        """GET /api/advanced/offers/{id} - Get single offer details"""
        offer_id = getattr(TestOfferManagement, 'created_offer_id', None)
        if not offer_id:
            pytest.skip("No offer ID available")
        
        response = session.get(f"{BASE_URL}/api/advanced/offers/{offer_id}")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("id") == offer_id, f"ID mismatch: {data}"
        assert "timeline" in data, f"Expected 'timeline' in offer details: {data.keys()}"
        print(f"✅ GET single offer: id={offer_id}, timeline_events={len(data.get('timeline', []))}")
    
    def test_update_status_draft_to_pending(self, session, auth_token):
        """PUT /api/advanced/offers/{id}/status - Draft -> Pending Approval"""
        offer_id = getattr(TestOfferManagement, 'created_offer_id', None)
        if not offer_id:
            pytest.skip("No offer ID available")
        
        response = session.put(
            f"{BASE_URL}/api/advanced/offers/{offer_id}/status",
            json={"status": "pending_approval"}
        )
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("status") == "pending_approval", f"Status not updated: {data}"
        print(f"✅ UPDATE status: draft -> pending_approval")
    
    def test_update_status_pending_to_sent(self, session, auth_token):
        """PUT /api/advanced/offers/{id}/status - Pending -> Sent"""
        offer_id = getattr(TestOfferManagement, 'created_offer_id', None)
        if not offer_id:
            pytest.skip("No offer ID available")
        
        # First approve
        response = session.put(
            f"{BASE_URL}/api/advanced/offers/{offer_id}/status",
            json={"status": "approved"}
        )
        assert response.status_code == 200, f"Approve failed: {response.status_code} {response.text}"
        
        # Then send
        response = session.put(
            f"{BASE_URL}/api/advanced/offers/{offer_id}/status",
            json={"status": "sent"}
        )
        assert response.status_code == 200, f"Send failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("status") == "sent", f"Status not updated to 'sent': {data}"
        print(f"✅ UPDATE status: approved -> sent")
    
    def test_update_status_sent_to_accepted(self, session, auth_token):
        """PUT /api/advanced/offers/{id}/status - Sent -> Accepted"""
        offer_id = getattr(TestOfferManagement, 'created_offer_id', None)
        if not offer_id:
            pytest.skip("No offer ID available")
        
        response = session.put(
            f"{BASE_URL}/api/advanced/offers/{offer_id}/status",
            json={"status": "accepted"}
        )
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("status") == "accepted", f"Status not updated: {data}"
        print(f"✅ UPDATE status: sent -> accepted")
    
    def test_create_offer_for_ai_letter(self, session, auth_token):
        """Create new offer for AI letter generation test"""
        payload = {
            "candidate_id": "",
            "candidate_name": "TEST_P0_AI_Letter",
            "job_id": "",
            "job_title": "Data Scientist",
            "salary": 180000,
            "currency": "USD",
            "start_date": "2026-04-01",
            "benefits": ["Health Insurance", "Stock Options", "Remote Work"],
            "notes": "For AI letter generation test",
            "equity": "0.25%",
            "bonus": 30000,
            "hiring_manager": "John Manager"
        }
        response = session.post(f"{BASE_URL}/api/advanced/offers", json=payload)
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        TestOfferManagement.ai_letter_offer_id = data["id"]
        print(f"✅ Created offer for AI letter test: id={data['id']}")
    
    def test_generate_ai_offer_letter(self, session, auth_token):
        """POST /api/advanced/offers/{id}/generate-letter - AI letter generation"""
        offer_id = getattr(TestOfferManagement, 'ai_letter_offer_id', None)
        if not offer_id:
            pytest.skip("No offer ID for AI letter test")
        
        response = session.post(f"{BASE_URL}/api/advanced/offers/{offer_id}/generate-letter")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "letter" in data, f"Expected 'letter' in response: {data}"
        letter = data["letter"]
        assert len(letter) > 100, f"Letter too short: {len(letter)} chars"
        # Check letter contains key info
        assert "TEST_P0_AI_Letter" in letter or "Data Scientist" in letter, f"Letter missing candidate/job info"
        print(f"✅ AI LETTER: generated {len(letter)} chars")
        print(f"   Letter preview: {letter[:150]}...")


class TestOfferStatsAndFilters(TestAuth):
    """Offer Management - Stats and Filtering"""
    
    def test_offer_stats(self, session, auth_token):
        """GET /api/advanced/offers/stats/summary - Offer statistics"""
        response = session.get(f"{BASE_URL}/api/advanced/offers/stats/summary")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert "stats" in data or "total" in data, f"Expected stats data: {data}"
        print(f"✅ GET offer stats: {data}")


class TestContactDeletion(TestAuth):
    """Cleanup - Delete test contacts"""
    
    def test_delete_contact(self, session, auth_token):
        """DELETE /api/talent-crm/contacts/{id} - Cleanup test contact"""
        contact_id = getattr(TestTalentCRMContacts, 'created_contact_id', None)
        if not contact_id:
            pytest.skip("No contact to delete")
        
        response = session.delete(f"{BASE_URL}/api/talent-crm/contacts/{contact_id}")
        assert response.status_code == 200, f"Failed: {response.status_code} {response.text}"
        data = response.json()
        assert data.get("status") == "deleted", f"Expected 'deleted': {data}"
        print(f"✅ DELETE contact: id={contact_id} cleaned up")


# Run with: pytest test_p0_talent_crm_reports_offers.py -v --tb=short
