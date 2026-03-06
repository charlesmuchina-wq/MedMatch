"""
Tests for LUMI Templates and Smart Buckets features - Iteration 187
P1 Features: Save as Template, Smart Buckets (AI-powered categorization)
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLumiTemplates:
    """LUMI Templates CRUD endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_create_template(self, headers):
        """POST /api/lumi/templates - Create a template"""
        payload = {
            "name": "TEST_Professional Meeting",
            "text": "Thank you for your time today. I look forward to our next meeting.",
            "category": "professional",
            "source_action": "refine"
        }
        response = requests.post(f"{BASE_URL}/api/lumi/templates", json=payload, headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "id" in data, "Template ID should be returned"
        assert data["name"] == "TEST_Professional Meeting"
        assert data["text"] == payload["text"]
        assert data["category"] == "professional"
        assert data["use_count"] == 0
        print(f"✓ Created template: {data['id']}")
        return data["id"]
    
    def test_list_templates(self, headers):
        """GET /api/lumi/templates - List user's templates"""
        response = requests.get(f"{BASE_URL}/api/lumi/templates", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "templates" in data, "Response should contain 'templates' array"
        assert isinstance(data["templates"], list)
        print(f"✓ Found {len(data['templates'])} templates")
    
    def test_list_templates_by_category(self, headers):
        """GET /api/lumi/templates?category=professional - Filter by category"""
        response = requests.get(f"{BASE_URL}/api/lumi/templates?category=professional", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        # All returned templates should be 'professional' category
        for tpl in data["templates"]:
            assert tpl["category"] == "professional"
        print(f"✓ Found {len(data['templates'])} professional templates")
    
    def test_create_and_update_template(self, headers):
        """PUT /api/lumi/templates/{id} - Update template name/text/category"""
        # Create a template first
        create_payload = {"name": "TEST_Update Me", "text": "Original text", "category": "general"}
        create_resp = requests.post(f"{BASE_URL}/api/lumi/templates", json=create_payload, headers=headers)
        assert create_resp.status_code == 200
        template_id = create_resp.json()["id"]
        
        # Update it
        update_payload = {"name": "TEST_Updated Name", "text": "Updated text content", "category": "friendly"}
        update_resp = requests.put(f"{BASE_URL}/api/lumi/templates/{template_id}", json=update_payload, headers=headers)
        
        assert update_resp.status_code == 200, f"Expected 200, got {update_resp.status_code}: {update_resp.text}"
        assert update_resp.json()["status"] == "updated"
        
        # Verify update by fetching templates
        list_resp = requests.get(f"{BASE_URL}/api/lumi/templates", headers=headers)
        templates = list_resp.json()["templates"]
        updated = next((t for t in templates if t["id"] == template_id), None)
        assert updated is not None
        assert updated["name"] == "TEST_Updated Name"
        assert updated["text"] == "Updated text content"
        assert updated["category"] == "friendly"
        print(f"✓ Updated template: {template_id}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/lumi/templates/{template_id}", headers=headers)
    
    def test_apply_template(self, headers):
        """POST /api/lumi/templates/{id}/apply - Apply template (returns text, increments use_count)"""
        # Create a template
        create_payload = {"name": "TEST_Apply Me", "text": "This is the template text to apply.", "category": "general"}
        create_resp = requests.post(f"{BASE_URL}/api/lumi/templates", json=create_payload, headers=headers)
        assert create_resp.status_code == 200
        template_id = create_resp.json()["id"]
        initial_use_count = create_resp.json()["use_count"]
        
        # Apply it
        apply_resp = requests.post(f"{BASE_URL}/api/lumi/templates/{template_id}/apply", headers=headers)
        
        assert apply_resp.status_code == 200, f"Expected 200, got {apply_resp.status_code}: {apply_resp.text}"
        data = apply_resp.json()
        assert "text" in data, "Should return template text"
        assert "name" in data, "Should return template name"
        assert data["text"] == "This is the template text to apply."
        assert data["name"] == "TEST_Apply Me"
        
        # Verify use_count incremented
        list_resp = requests.get(f"{BASE_URL}/api/lumi/templates", headers=headers)
        templates = list_resp.json()["templates"]
        applied = next((t for t in templates if t["id"] == template_id), None)
        assert applied is not None
        assert applied["use_count"] == initial_use_count + 1, "use_count should increment"
        print(f"✓ Applied template, use_count: {applied['use_count']}")
        
        # Cleanup
        requests.delete(f"{BASE_URL}/api/lumi/templates/{template_id}", headers=headers)
    
    def test_delete_template(self, headers):
        """DELETE /api/lumi/templates/{id} - Delete a template"""
        # Create a template
        create_payload = {"name": "TEST_Delete Me", "text": "Will be deleted", "category": "general"}
        create_resp = requests.post(f"{BASE_URL}/api/lumi/templates", json=create_payload, headers=headers)
        assert create_resp.status_code == 200
        template_id = create_resp.json()["id"]
        
        # Delete it
        delete_resp = requests.delete(f"{BASE_URL}/api/lumi/templates/{template_id}", headers=headers)
        
        assert delete_resp.status_code == 200, f"Expected 200, got {delete_resp.status_code}: {delete_resp.text}"
        assert delete_resp.json()["status"] == "deleted"
        
        # Verify deletion
        list_resp = requests.get(f"{BASE_URL}/api/lumi/templates", headers=headers)
        templates = list_resp.json()["templates"]
        deleted = next((t for t in templates if t["id"] == template_id), None)
        assert deleted is None, "Template should be deleted"
        print(f"✓ Deleted template: {template_id}")
    
    def test_delete_nonexistent_template(self, headers):
        """DELETE /api/lumi/templates/{id} - Should return 404 for non-existent"""
        response = requests.delete(f"{BASE_URL}/api/lumi/templates/tpl_nonexistent123", headers=headers)
        assert response.status_code == 404
        print("✓ 404 returned for non-existent template")
    
    def test_update_nonexistent_template(self, headers):
        """PUT /api/lumi/templates/{id} - Should return 404 for non-existent"""
        response = requests.put(
            f"{BASE_URL}/api/lumi/templates/tpl_nonexistent123",
            json={"name": "Updated"},
            headers=headers
        )
        assert response.status_code == 404
        print("✓ 404 returned for non-existent template update")
    
    def test_apply_nonexistent_template(self, headers):
        """POST /api/lumi/templates/{id}/apply - Should return 404 for non-existent"""
        response = requests.post(f"{BASE_URL}/api/lumi/templates/tpl_nonexistent123/apply", headers=headers)
        assert response.status_code == 404
        print("✓ 404 returned for non-existent template apply")


class TestLumiSmartBuckets:
    """LUMI Smart Buckets endpoint tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        pytest.skip("Authentication failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def headers(self, auth_token):
        """Auth headers"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    def test_get_bucket_counts(self, headers):
        """GET /api/lumi/buckets/counts - Returns counts per category"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/counts", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "counts" in data, "Response should contain 'counts'"
        
        expected_categories = ["urgent", "action_required", "meeting_request", "fyi", "social"]
        for cat in expected_categories:
            assert cat in data["counts"], f"Missing category: {cat}"
            assert isinstance(data["counts"][cat], int), f"Count for {cat} should be int"
        print(f"✓ Bucket counts: {data['counts']}")
    
    def test_get_bucket_messages_urgent(self, headers):
        """GET /api/lumi/buckets/urgent - Returns messages in urgent bucket"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/urgent", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "messages" in data
        assert "category" in data
        assert data["category"] == "urgent"
        print(f"✓ Found {len(data['messages'])} urgent messages")
    
    def test_get_bucket_messages_action_required(self, headers):
        """GET /api/lumi/buckets/action_required - Returns messages requiring action"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/action_required", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert data["category"] == "action_required"
        print(f"✓ Found {len(data['messages'])} action required messages")
    
    def test_get_bucket_messages_meeting_request(self, headers):
        """GET /api/lumi/buckets/meeting_request - Returns meeting requests"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/meeting_request", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert data["category"] == "meeting_request"
        print(f"✓ Found {len(data['messages'])} meeting request messages")
    
    def test_get_bucket_messages_fyi(self, headers):
        """GET /api/lumi/buckets/fyi - Returns FYI/informational messages"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/fyi", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert data["category"] == "fyi"
        print(f"✓ Found {len(data['messages'])} FYI messages")
    
    def test_get_bucket_messages_social(self, headers):
        """GET /api/lumi/buckets/social - Returns social/casual messages"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/social", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert data["category"] == "social"
        print(f"✓ Found {len(data['messages'])} social messages")
    
    def test_get_bucket_invalid_category(self, headers):
        """GET /api/lumi/buckets/invalid_category - Should return 400"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/invalid_category", headers=headers)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("✓ 400 returned for invalid category")
    
    def test_dismiss_bucket_item(self, headers):
        """POST /api/lumi/buckets/{category}/{item_id}/dismiss - Dismiss a bucket item"""
        # This endpoint doesn't require the item to exist, it just updates if found
        response = requests.post(
            f"{BASE_URL}/api/lumi/buckets/urgent/bc_testitem123/dismiss",
            headers=headers
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["status"] == "dismissed"
        print("✓ Dismiss endpoint working")
    
    def test_scan_messages(self, headers):
        """POST /api/lumi/buckets/scan - AI-scan and categorize messages"""
        response = requests.post(f"{BASE_URL}/api/lumi/buckets/scan", headers=headers)
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "categorized" in data, "Response should contain 'categorized' count"
        assert isinstance(data["categorized"], int)
        print(f"✓ Scan categorized {data['categorized']} messages")


class TestLumiTemplatesAuth:
    """Templates endpoint auth tests"""
    
    def test_templates_require_auth(self):
        """Templates endpoints should require authentication"""
        # No auth header
        response = requests.get(f"{BASE_URL}/api/lumi/templates")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        response = requests.post(f"{BASE_URL}/api/lumi/templates", json={"name": "test", "text": "test"})
        assert response.status_code == 401
        print("✓ Templates require auth")
    
    def test_buckets_require_auth(self):
        """Buckets endpoints should require authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/counts")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        
        response = requests.get(f"{BASE_URL}/api/lumi/buckets/urgent")
        assert response.status_code == 401
        
        response = requests.post(f"{BASE_URL}/api/lumi/buckets/scan")
        assert response.status_code == 401
        print("✓ Buckets require auth")


class TestCleanupTestData:
    """Cleanup TEST_ prefixed data after tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token for admin user"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": "admin@medmatch.com",
            "password": "Swampdrainer2026!"
        })
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    
    def test_cleanup_test_templates(self, auth_token):
        """Remove TEST_ prefixed templates"""
        if not auth_token:
            pytest.skip("No auth token")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/api/lumi/templates", headers=headers)
        if response.status_code == 200:
            templates = response.json().get("templates", [])
            deleted = 0
            for tpl in templates:
                if tpl.get("name", "").startswith("TEST_"):
                    requests.delete(f"{BASE_URL}/api/lumi/templates/{tpl['id']}", headers=headers)
                    deleted += 1
            print(f"✓ Cleaned up {deleted} TEST_ templates")
