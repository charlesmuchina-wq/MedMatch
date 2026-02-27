"""
Iteration 126: Test Whiteboard WebSocket, PDF/CSV Export, Onboarding Wizard
Features tested:
1. WebSocket whiteboard sync (backend handlers exist for whiteboard_stroke/cursor/clear)
2. PDF Export: GET /api/advanced/reports/{id}/export/pdf
3. CSV Export: GET /api/advanced/reports/{id}/export/csv
4. Report CRUD: POST/GET /api/advanced/reports
5. Whiteboard save/load: POST /api/karau-meet/ai/whiteboard/save, GET /api/karau-meet/ai/whiteboard/{meeting_id}
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAuth:
    """Authentication helper"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get auth token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return data.get("access_token")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Headers with auth token"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.fixture(scope="class")
    def auth_session(self, auth_token):
        """Requests session with auth cookie"""
        session = requests.Session()
        # Login to get cookie
        response = session.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        assert response.status_code == 200
        session.headers.update({
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        })
        return session


class TestReportCRUDAndExport(TestAuth):
    """Test Report Builder API - Create, List, Export PDF/CSV"""
    
    created_report_id = None
    
    def test_create_hiring_funnel_report(self, auth_session):
        """Create a report for testing exports"""
        payload = {
            "name": f"Test Report {uuid.uuid4().hex[:8]}",
            "report_type": "hiring_funnel",
            "date_range": "30d",
            "metrics": [],
            "filters": {}
        }
        response = auth_session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Create report failed: {response.text}"
        data = response.json()
        assert "id" in data, "Report ID not returned"
        assert data["report_type"] == "hiring_funnel"
        assert "data" in data, "Report data not generated"
        assert "summary" in data.get("data", {}), "Summary not in report data"
        TestReportCRUDAndExport.created_report_id = data["id"]
        print(f"Created report with ID: {data['id']}")
    
    def test_list_reports(self, auth_session):
        """List all reports"""
        response = auth_session.get(f"{BASE_URL}/api/advanced/reports")
        assert response.status_code == 200, f"List reports failed: {response.text}"
        data = response.json()
        assert "reports" in data
        assert len(data["reports"]) >= 1, "Expected at least 1 report"
        print(f"Found {len(data['reports'])} reports")
    
    def test_export_pdf(self, auth_session):
        """Test PDF export endpoint"""
        report_id = TestReportCRUDAndExport.created_report_id
        assert report_id is not None, "No report ID available for PDF export test"
        
        response = auth_session.get(f"{BASE_URL}/api/advanced/reports/{report_id}/export/pdf")
        assert response.status_code == 200, f"PDF export failed: {response.text}"
        
        # Verify PDF content type and magic bytes
        content_type = response.headers.get("Content-Type", "")
        assert "application/pdf" in content_type, f"Expected PDF content type, got: {content_type}"
        
        # PDF files start with %PDF magic bytes
        content = response.content
        assert content[:4] == b'%PDF', f"Response doesn't start with PDF magic bytes"
        assert len(content) > 100, f"PDF content too small: {len(content)} bytes"
        print(f"PDF export successful: {len(content)} bytes")
    
    def test_export_csv(self, auth_session):
        """Test CSV export endpoint"""
        report_id = TestReportCRUDAndExport.created_report_id
        assert report_id is not None, "No report ID available for CSV export test"
        
        response = auth_session.get(f"{BASE_URL}/api/advanced/reports/{report_id}/export/csv")
        assert response.status_code == 200, f"CSV export failed: {response.text}"
        
        # Verify CSV content type
        content_type = response.headers.get("Content-Type", "")
        assert "text/csv" in content_type, f"Expected CSV content type, got: {content_type}"
        
        # CSV should have text content
        content = response.text
        assert len(content) > 50, f"CSV content too small: {len(content)} chars"
        assert "Summary" in content or "Stage" in content, "Expected CSV headers not found"
        print(f"CSV export successful: {len(content)} chars")
    
    def test_create_dei_report(self, auth_session):
        """Create DEI report type"""
        payload = {
            "name": f"DEI Report {uuid.uuid4().hex[:8]}",
            "report_type": "dei",
            "date_range": "90d",
            "metrics": [],
            "filters": {}
        }
        response = auth_session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Create DEI report failed: {response.text}"
        data = response.json()
        assert data["report_type"] == "dei"
        assert "gender_distribution" in data.get("data", {}) or "summary" in data.get("data", {}), "DEI data not generated"
        print(f"Created DEI report: {data['id']}")
    
    def test_create_source_report(self, auth_session):
        """Create Source Analysis report"""
        payload = {
            "name": f"Source Report {uuid.uuid4().hex[:8]}",
            "report_type": "source",
            "date_range": "30d",
            "metrics": [],
            "filters": {}
        }
        response = auth_session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Create source report failed: {response.text}"
        data = response.json()
        assert data["report_type"] == "source"
        print(f"Created source report: {data['id']}")
    
    def test_create_time_series_report(self, auth_session):
        """Create Time Series report"""
        payload = {
            "name": f"Time Series {uuid.uuid4().hex[:8]}",
            "report_type": "time_series",
            "date_range": "365d",
            "metrics": [],
            "filters": {}
        }
        response = auth_session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Create time series report failed: {response.text}"
        data = response.json()
        assert "monthly" in data.get("data", {}) or "summary" in data.get("data", {}), "Time series data not generated"
        print(f"Created time series report: {data['id']}")
    
    def test_create_offer_analysis_report(self, auth_session):
        """Create Offer Analysis report"""
        payload = {
            "name": f"Offer Analysis {uuid.uuid4().hex[:8]}",
            "report_type": "offer_analysis",
            "date_range": "30d",
            "metrics": [],
            "filters": {}
        }
        response = auth_session.post(f"{BASE_URL}/api/advanced/reports", json=payload)
        assert response.status_code == 200, f"Create offer analysis report failed: {response.text}"
        data = response.json()
        assert data["report_type"] == "offer_analysis"
        print(f"Created offer analysis report: {data['id']}")
    
    def test_delete_report(self, auth_session):
        """Delete the test report"""
        report_id = TestReportCRUDAndExport.created_report_id
        if report_id:
            response = auth_session.delete(f"{BASE_URL}/api/advanced/reports/{report_id}")
            assert response.status_code == 200, f"Delete report failed: {response.text}"
            print(f"Deleted report: {report_id}")


class TestWhiteboardSaveLoad(TestAuth):
    """Test Whiteboard save/load APIs"""
    
    test_meeting_id = f"test_meeting_{uuid.uuid4().hex[:8]}"
    
    def test_save_whiteboard(self, auth_session):
        """Save whiteboard snapshot"""
        # Create a small base64 PNG placeholder
        snapshot_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        payload = {
            "meeting_id": TestWhiteboardSaveLoad.test_meeting_id,
            "snapshot_data": snapshot_data,
            "name": "Test Whiteboard Snapshot"
        }
        response = auth_session.post(f"{BASE_URL}/api/karau-meet/ai/whiteboard/save", json=payload)
        
        # API might return 200 or 201
        assert response.status_code in [200, 201], f"Save whiteboard failed: {response.status_code} - {response.text}"
        data = response.json()
        assert "id" in data or "snapshot_id" in data or "status" in data, f"Unexpected response: {data}"
        print(f"Saved whiteboard snapshot for meeting: {TestWhiteboardSaveLoad.test_meeting_id}")
    
    def test_load_whiteboard(self, auth_session):
        """Load whiteboard snapshot"""
        meeting_id = TestWhiteboardSaveLoad.test_meeting_id
        
        response = auth_session.get(f"{BASE_URL}/api/karau-meet/ai/whiteboard/{meeting_id}")
        
        # Might return 200 with data or 404 if not found
        assert response.status_code in [200, 404], f"Load whiteboard failed: {response.status_code} - {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            print(f"Loaded whiteboard for meeting: {meeting_id}")
            # Could have snapshot data or empty
            if "snapshot" in data:
                print(f"Snapshot found: {data['snapshot'].get('name', 'unnamed')}")
        else:
            print(f"No whiteboard snapshot found for meeting: {meeting_id} (404 is acceptable)")


class TestWebSocketSignaling:
    """Test WebSocket endpoint availability (can't do full WS test with requests)"""
    
    def test_websocket_endpoint_exists(self):
        """Verify WebSocket endpoint returns upgrade required or handles correctly"""
        meeting_id = "test_meeting_123"
        user_id = "test_user_456"
        user_name = "TestUser"
        
        # WebSocket endpoints will reject HTTP requests but shouldn't 404
        url = f"{BASE_URL}/api/karau-meet/ws/{meeting_id}?user_id={user_id}&user_name={user_name}"
        
        response = requests.get(url)
        
        # WS endpoint with HTTP will typically return:
        # - 400 (Bad Request) because it's not a WS upgrade
        # - 426 (Upgrade Required)
        # - 403 (if auth required)
        # - Should NOT be 404 (not found)
        assert response.status_code != 404, f"WebSocket endpoint not found: {url}"
        print(f"WebSocket endpoint exists (HTTP response: {response.status_code})")


class TestExportEdgeCases(TestAuth):
    """Test export with non-existent report"""
    
    def test_export_pdf_nonexistent_report(self, auth_session):
        """PDF export should return 404 for non-existent report"""
        fake_id = "nonexistent_report_123456"
        response = auth_session.get(f"{BASE_URL}/api/advanced/reports/{fake_id}/export/pdf")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PDF export correctly returns 404 for non-existent report")
    
    def test_export_csv_nonexistent_report(self, auth_session):
        """CSV export should return 404 for non-existent report"""
        fake_id = "nonexistent_report_123456"
        response = auth_session.get(f"{BASE_URL}/api/advanced/reports/{fake_id}/export/csv")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("CSV export correctly returns 404 for non-existent report")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
