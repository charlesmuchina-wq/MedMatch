"""
Test Phase 3-5 Features:
- Phase 3: One-click apply, Team collaboration, Multi-channel outreach
- Phase 4: Webinars, Offer management with AI letter generation, Custom report builder, Real-time translation, SFU infrastructure, E2E encryption
- Phase 5: Semantic search, HRIS sync, Background checks, Compliance dashboard
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPhase3to5Features:
    """Phase 3-5 Backend API Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.token = None
        self.job_id = None
    
    def get_auth_token(self):
        """Login and get access_token"""
        if self.token:
            return self.token
        response = self.session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        self.token = data.get("access_token")
        assert self.token, "No access_token in response"
        return self.token
    
    def auth_headers(self):
        """Get headers with auth token"""
        token = self.get_auth_token()
        return {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    
    def get_job_id(self):
        """Get a valid job_id from database"""
        if self.job_id:
            return self.job_id
        response = self.session.get(f"{BASE_URL}/api/jobs", headers=self.auth_headers())
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            if jobs:
                self.job_id = jobs[0].get("id")
        return self.job_id or f"test-job-{uuid.uuid4().hex[:8]}"
    
    # === PHASE 3: ONE-CLICK APPLY ===
    def test_one_click_apply(self):
        """Test POST /api/talent-tools/one-click-apply"""
        job_id = self.get_job_id()
        response = self.session.post(
            f"{BASE_URL}/api/talent-tools/one-click-apply",
            headers=self.auth_headers(),
            json={"job_id": job_id}
        )
        # Expect 200 for success or 404 if job not found
        assert response.status_code in [200, 404], f"One-click apply failed: {response.status_code} - {response.text}"
        if response.status_code == 200:
            data = response.json()
            assert "status" in data, "Missing status in response"
            assert data["status"] in ["applied", "already_applied"], f"Unexpected status: {data['status']}"
            print(f"One-click apply: {data.get('status')}")
    
    # === PHASE 3: TEAM COLLABORATION ===
    def test_add_collaboration_comment(self):
        """Test POST /api/talent-tools/collaborate/comment"""
        response = self.session.post(
            f"{BASE_URL}/api/talent-tools/collaborate/comment",
            headers=self.auth_headers(),
            json={
                "candidate_id": f"TEST_candidate_{uuid.uuid4().hex[:8]}",
                "comment": "This is a test collaboration comment",
                "mentions": []
            }
        )
        assert response.status_code == 200, f"Add comment failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Comment should have id"
        assert data["comment"] == "This is a test collaboration comment"
        print(f"Comment created: {data.get('id')}")
    
    def test_get_collaboration_comments(self):
        """Test GET /api/talent-tools/collaborate/comments/{candidate_id}"""
        # First create a comment
        test_candidate_id = f"TEST_collab_{uuid.uuid4().hex[:8]}"
        self.session.post(
            f"{BASE_URL}/api/talent-tools/collaborate/comment",
            headers=self.auth_headers(),
            json={"candidate_id": test_candidate_id, "comment": "Test comment for get", "mentions": []}
        )
        # Then retrieve
        response = self.session.get(
            f"{BASE_URL}/api/talent-tools/collaborate/comments/{test_candidate_id}",
            headers=self.auth_headers()
        )
        assert response.status_code == 200, f"Get comments failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "comments" in data, "Response should have comments key"
        print(f"Found {len(data['comments'])} comments")
    
    # === PHASE 3: MULTI-CHANNEL OUTREACH ===
    def test_send_outreach(self):
        """Test POST /api/talent-tools/outreach/send"""
        response = self.session.post(
            f"{BASE_URL}/api/talent-tools/outreach/send",
            headers=self.auth_headers(),
            json={
                "candidate_ids": [f"TEST_outreach_{uuid.uuid4().hex[:8]}"],
                "channel": "email",
                "subject": "Test Outreach Subject",
                "message": "This is a test outreach message."
            }
        )
        assert response.status_code == 200, f"Send outreach failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Outreach should have id"
        assert data["status"] == "sent"
        assert data["channel"] == "email"
        print(f"Outreach sent: {data.get('id')}")
    
    def test_get_outreach_history(self):
        """Test GET /api/talent-tools/outreach/history"""
        response = self.session.get(
            f"{BASE_URL}/api/talent-tools/outreach/history",
            headers=self.auth_headers()
        )
        assert response.status_code == 200, f"Get outreach history failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "messages" in data, "Response should have messages key"
        print(f"Outreach history: {len(data['messages'])} messages")
    
    def test_create_outreach_template(self):
        """Test POST /api/talent-tools/outreach/templates"""
        response = self.session.post(
            f"{BASE_URL}/api/talent-tools/outreach/templates",
            headers=self.auth_headers(),
            json={
                "name": f"TEST_Template_{uuid.uuid4().hex[:8]}",
                "channel": "email",
                "subject": "Position Opportunity at MedMatch",
                "body": "Dear {{candidate_name}}, We have an exciting opportunity..."
            }
        )
        assert response.status_code == 200, f"Create template failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Template should have id"
        assert data["channel"] == "email"
        print(f"Template created: {data.get('name')}")
    
    # === PHASE 4: WEBINARS ===
    def test_create_webinar(self):
        """Test POST /api/advanced/webinars"""
        response = self.session.post(
            f"{BASE_URL}/api/advanced/webinars",
            headers=self.auth_headers(),
            json={
                "title": f"TEST_Webinar_{uuid.uuid4().hex[:8]}",
                "description": "Test webinar for hiring best practices",
                "max_attendees": 500,
                "scheduled_at": "2026-02-15T14:00:00Z"
            }
        )
        assert response.status_code == 200, f"Create webinar failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Webinar should have id"
        assert data["status"] == "scheduled"
        self.webinar_id = data["id"]
        print(f"Webinar created: {data.get('title')}")
    
    def test_list_webinars(self):
        """Test GET /api/advanced/webinars"""
        response = self.session.get(f"{BASE_URL}/api/advanced/webinars")
        assert response.status_code == 200, f"List webinars failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "webinars" in data, "Response should have webinars key"
        print(f"Found {len(data['webinars'])} webinars")
    
    def test_register_for_webinar(self):
        """Test POST /api/advanced/webinars/{id}/register"""
        # First create a webinar
        create_resp = self.session.post(
            f"{BASE_URL}/api/advanced/webinars",
            headers=self.auth_headers(),
            json={"title": f"TEST_Register_Webinar_{uuid.uuid4().hex[:8]}", "max_attendees": 100}
        )
        webinar_id = create_resp.json().get("id") if create_resp.status_code == 200 else None
        if not webinar_id:
            # Get existing webinar
            webinars = self.session.get(f"{BASE_URL}/api/advanced/webinars").json().get("webinars", [])
            webinar_id = webinars[0]["id"] if webinars else "test-webinar"
        
        response = self.session.post(
            f"{BASE_URL}/api/advanced/webinars/{webinar_id}/register",
            headers={"Content-Type": "application/json"},
            json={"name": "Test Attendee", "email": "test.attendee@example.com"}
        )
        assert response.status_code == 200, f"Register failed: {response.status_code} - {response.text}"
        data = response.json()
        assert data.get("status") == "registered"
        print(f"Registered for webinar: {webinar_id}")
    
    # === PHASE 4: OFFER MANAGEMENT ===
    def test_create_offer(self):
        """Test POST /api/advanced/offers"""
        response = self.session.post(
            f"{BASE_URL}/api/advanced/offers",
            headers=self.auth_headers(),
            json={
                "candidate_id": f"TEST_offer_candidate_{uuid.uuid4().hex[:8]}",
                "candidate_name": "Test Candidate",
                "job_id": "test-job-123",
                "job_title": "Senior Bioprocess Engineer",
                "salary": 150000,
                "currency": "USD",
                "start_date": "2026-03-01",
                "benefits": ["Health Insurance", "401k", "Stock Options"],
                "notes": "Top performer, fast-track onboarding"
            }
        )
        assert response.status_code == 200, f"Create offer failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Offer should have id"
        assert data["status"] == "draft"
        assert data["salary"] == 150000
        print(f"Offer created: {data.get('id')}")
    
    def test_list_offers(self):
        """Test GET /api/advanced/offers"""
        response = self.session.get(
            f"{BASE_URL}/api/advanced/offers",
            headers=self.auth_headers()
        )
        assert response.status_code == 200, f"List offers failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "offers" in data, "Response should have offers key"
        print(f"Found {len(data['offers'])} offers")
    
    # === PHASE 4: CUSTOM REPORT BUILDER ===
    def test_create_report(self):
        """Test POST /api/advanced/reports"""
        response = self.session.post(
            f"{BASE_URL}/api/advanced/reports",
            headers=self.auth_headers(),
            json={
                "name": f"TEST_Hiring_Report_{uuid.uuid4().hex[:8]}",
                "report_type": "hiring_funnel",
                "date_range": "30d",
                "metrics": ["applications", "hires"],
                "filters": {}
            }
        )
        assert response.status_code == 200, f"Create report failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Report should have id"
        assert "data" in data, "Report should have data"
        print(f"Report created: {data.get('name')}, type: {data.get('report_type')}")
    
    def test_list_reports(self):
        """Test GET /api/advanced/reports"""
        response = self.session.get(
            f"{BASE_URL}/api/advanced/reports",
            headers=self.auth_headers()
        )
        assert response.status_code == 200, f"List reports failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "reports" in data, "Response should have reports key"
        print(f"Found {len(data['reports'])} reports")
    
    # === PHASE 4: SFU INFRASTRUCTURE ===
    def test_sfu_config(self):
        """Test GET /api/meeting-infra/sfu/config"""
        response = self.session.get(f"{BASE_URL}/api/meeting-infra/sfu/config")
        assert response.status_code == 200, f"SFU config failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "relay_servers" in data, "Should have relay_servers"
        assert "quality_presets" in data, "Should have quality_presets"
        assert data["sfu_enabled"] == True
        print(f"SFU config: {len(data['relay_servers'])} relay servers, max {data.get('max_participants')} participants")
    
    def test_sfu_status(self):
        """Test GET /api/meeting-infra/sfu/status"""
        response = self.session.get(f"{BASE_URL}/api/meeting-infra/sfu/status")
        assert response.status_code == 200, f"SFU status failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "servers" in data, "Should have servers"
        assert "active_meetings" in data, "Should have active_meetings"
        print(f"SFU status: {len(data['servers'])} servers, {data.get('active_meetings')} active meetings")
    
    # === PHASE 4: E2E ENCRYPTION ===
    def test_e2ee_key_exchange(self):
        """Test POST /api/meeting-infra/e2ee/keys"""
        meeting_id = f"TEST_meeting_{uuid.uuid4().hex[:8]}"
        response = self.session.post(
            f"{BASE_URL}/api/meeting-infra/e2ee/keys",
            headers={"Content-Type": "application/json"},
            json={
                "meeting_id": meeting_id,
                "participant_id": "user-123",
                "public_key": "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE..."
            }
        )
        assert response.status_code == 200, f"E2EE key exchange failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "keys" in data, "Should have keys"
        assert data["encryption_protocol"] == "AES-256-GCM"
        print(f"E2EE keys exchanged: {len(data['keys'])} participants")
    
    def test_e2ee_verify(self):
        """Test GET /api/meeting-infra/e2ee/verify/{meeting_id}"""
        meeting_id = f"TEST_verify_{uuid.uuid4().hex[:8]}"
        # First add a key
        self.session.post(
            f"{BASE_URL}/api/meeting-infra/e2ee/keys",
            headers={"Content-Type": "application/json"},
            json={"meeting_id": meeting_id, "participant_id": "user-456", "public_key": "key..."}
        )
        # Then verify
        response = self.session.get(f"{BASE_URL}/api/meeting-infra/e2ee/verify/{meeting_id}")
        assert response.status_code == 200, f"E2EE verify failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "encryption_active" in data
        assert "verification_code" in data
        print(f"E2EE verify: active={data.get('encryption_active')}, code={data.get('verification_code')}")
    
    # === PHASE 4: REAL-TIME TRANSLATION ===
    def test_get_supported_languages(self):
        """Test GET /api/meeting-infra/translate/languages"""
        response = self.session.get(f"{BASE_URL}/api/meeting-infra/translate/languages")
        assert response.status_code == 200, f"Get languages failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "languages" in data, "Should have languages"
        assert len(data["languages"]) >= 10, "Should have at least 10 languages"
        lang_codes = [l["code"] for l in data["languages"]]
        assert "en" in lang_codes, "Should support English"
        assert "es" in lang_codes, "Should support Spanish"
        print(f"Supported languages: {len(data['languages'])}")
    
    # === PHASE 5: SEMANTIC SEARCH ===
    def test_semantic_match(self):
        """Test POST /api/platform/semantic-match"""
        response = self.session.post(
            f"{BASE_URL}/api/platform/semantic-match",
            headers={"Content-Type": "application/json"},
            json={
                "query": "bioprocess engineer with 5+ years experience in monoclonal antibodies",
                "match_type": "candidates",
                "top_k": 10
            },
            timeout=30  # Allow longer timeout for LLM
        )
        assert response.status_code == 200, f"Semantic match failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "query" in data, "Should have query"
        assert "matches" in data, "Should have matches"
        assert "match_type" in data, "Should have match_type"
        print(f"Semantic match: {data.get('match_count')} matches found")
    
    # === PHASE 5: HRIS INTEGRATION ===
    def test_configure_hris(self):
        """Test POST /api/platform/hris/configure"""
        response = self.session.post(
            f"{BASE_URL}/api/platform/hris/configure",
            headers=self.auth_headers(),
            json={
                "provider": "workday",
                "api_url": "https://wd5-impl.workday.com/api/v1",
                "sync_direction": "bidirectional",
                "sync_fields": ["employees", "positions", "departments"]
            }
        )
        assert response.status_code == 200, f"Configure HRIS failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Config should have id"
        assert data["provider"] == "workday"
        assert data["status"] == "configured"
        print(f"HRIS configured: {data.get('provider')}")
    
    def test_hris_sync(self):
        """Test POST /api/platform/hris/sync"""
        response = self.session.post(
            f"{BASE_URL}/api/platform/hris/sync",
            headers=self.auth_headers()
        )
        assert response.status_code == 200, f"HRIS sync failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Sync should have id"
        assert data["status"] == "completed"
        assert "records_synced" in data, "Should have records_synced"
        print(f"HRIS sync: {data.get('status')}, time: {data.get('sync_time_ms')}ms")
    
    # === PHASE 5: BACKGROUND CHECKS ===
    def test_initiate_background_check(self):
        """Test POST /api/platform/background-checks"""
        response = self.session.post(
            f"{BASE_URL}/api/platform/background-checks",
            headers=self.auth_headers(),
            json={
                "candidate_id": f"TEST_bgcheck_{uuid.uuid4().hex[:8]}",
                "candidate_name": "Test Background Check Candidate",
                "check_types": ["identity", "criminal", "education", "employment"],
                "provider": "checkr"
            }
        )
        assert response.status_code == 200, f"Background check failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data, "Check should have id"
        assert data["status"] == "pending"
        assert "results" in data, "Should have results"
        print(f"Background check initiated: {data.get('id')}, status: {data.get('status')}")
    
    # === PHASE 5: COMPLIANCE DASHBOARD ===
    def test_compliance_status(self):
        """Test GET /api/platform/compliance/status"""
        response = self.session.get(f"{BASE_URL}/api/platform/compliance/status")
        assert response.status_code == 200, f"Compliance status failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "certifications" in data, "Should have certifications"
        assert "data_handling" in data, "Should have data_handling"
        certs = data["certifications"]
        assert len(certs) >= 3, "Should have at least 3 certifications"
        # Check for key certifications
        cert_names = [c["name"] for c in certs]
        assert "SOC 2 Type II" in cert_names or "GDPR" in cert_names, "Should have SOC 2 or GDPR"
        print(f"Compliance status: {len(certs)} certifications, encryption_at_rest: {data['data_handling'].get('encryption_at_rest')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
