"""
Test suite for iteration 166 - Testing 3 NEW features:
1) LUMI File Sharing - Upload and download files in channels
2) LUMI Read Receipts - Unread counts, mark as read
3) AI-Powered Theme Summarization - GPT-5.2 generated summaries
"""
import pytest
import requests
import os
import io

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
TEST_EMAIL = "admin@medmatch.com"
TEST_PASSWORD = "Swampdrainer2026!"


class TestAuthenticationSetup:
    """Test authentication and setup"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "access_token" in data
        return data["access_token"]
    
    def test_login_success(self, auth_token):
        """Verify login works and we have a token"""
        assert auth_token is not None
        assert len(auth_token) > 10
        print(f"✅ Login successful, token obtained")


class TestLumiFileSharing:
    """Tests for LUMI File Upload/Download feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def test_channel(self, auth_token):
        """Get first available channel"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        channels = data.get("my_channels", [])
        assert len(channels) > 0, "No channels available for testing"
        return channels[0]
    
    def test_file_upload_endpoint_exists(self, auth_token, test_channel):
        """Test POST /api/lumi/upload exists and validates params"""
        # Test without file - should fail with 422 (validation error)
        response = requests.post(
            f"{BASE_URL}/api/lumi/upload?channel_id={test_channel['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # Either 422 (missing file) or 400 is acceptable
        assert response.status_code in [400, 422], f"Expected 400/422, got {response.status_code}"
        print(f"✅ File upload endpoint exists and validates input")
    
    def test_file_upload_requires_auth(self, auth_token, test_channel):
        """Test upload requires authentication - verify with valid file"""
        test_content = b"Test authentication check"
        files = {"file": ("auth_test.txt", io.BytesIO(test_content), "text/plain")}
        
        # Without auth header should return 401
        response = requests.post(
            f"{BASE_URL}/api/lumi/upload?channel_id={test_channel['id']}",
            files=files
        )
        assert response.status_code == 401, f"Expected 401 without auth, got {response.status_code}"
        print(f"✅ File upload requires authentication (401)")
    
    def test_file_upload_with_image(self, auth_token, test_channel):
        """Test uploading an image file"""
        # Create a simple test image (1x1 pixel PNG)
        png_header = b'\x89PNG\r\n\x1a\n'
        png_ihdr = b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde'
        png_idat = b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
        png_iend = b'\x00\x00\x00\x00IEND\xaeB`\x82'
        test_image = png_header + png_ihdr + png_idat + png_iend
        
        files = {"file": ("test_image.png", io.BytesIO(test_image), "image/png")}
        response = requests.post(
            f"{BASE_URL}/api/lumi/upload?channel_id={test_channel['id']}",
            headers={"Authorization": f"Bearer {auth_token}"},
            files=files
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "id" in data, "File record should have id"
        assert "storage_path" in data, "File record should have storage_path"
        assert "original_filename" in data, "File record should have original_filename"
        assert "content_type" in data, "File record should have content_type"
        assert "is_image" in data, "File record should have is_image"
        assert data["is_image"] == True, "PNG should be marked as image"
        assert data["original_filename"] == "test_image.png"
        print(f"✅ Image file uploaded successfully: {data['id']}")
        return data
    
    def test_file_upload_with_text(self, auth_token, test_channel):
        """Test uploading a text file"""
        test_content = b"This is a test file content for LUMI file sharing feature."
        files = {"file": ("test_document.txt", io.BytesIO(test_content), "text/plain")}
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/upload?channel_id={test_channel['id']}",
            headers={"Authorization": f"Bearer {auth_token}"},
            files=files
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        data = response.json()
        assert data["is_image"] == False, "TXT should not be marked as image"
        assert data["original_filename"] == "test_document.txt"
        print(f"✅ Text file uploaded successfully: {data['id']}")
        return data
    
    def test_file_download_requires_auth(self):
        """Test file download requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/files/file_test123")
        assert response.status_code == 401
        print(f"✅ File download requires authentication (401)")
    
    def test_file_download_nonexistent(self, auth_token):
        """Test downloading non-existent file returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/files/file_nonexistent_xyz",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 404
        print(f"✅ Non-existent file returns 404")
    
    def test_file_upload_to_invalid_channel(self, auth_token):
        """Test uploading to a channel user is not a member of"""
        test_content = b"Test content"
        files = {"file": ("test.txt", io.BytesIO(test_content), "text/plain")}
        
        response = requests.post(
            f"{BASE_URL}/api/lumi/upload?channel_id=invalid_channel_xyz",
            headers={"Authorization": f"Bearer {auth_token}"},
            files=files
        )
        assert response.status_code == 403, f"Expected 403 for non-member, got {response.status_code}"
        print(f"✅ Upload to invalid channel returns 403")


class TestLumiReadReceipts:
    """Tests for LUMI Read Receipts and Unread Counts feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    @pytest.fixture(scope="class")
    def test_channel(self, auth_token):
        """Get first available channel"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels", 
            headers={"Authorization": f"Bearer {auth_token}"})
        assert response.status_code == 200
        data = response.json()
        channels = data.get("my_channels", [])
        assert len(channels) > 0
        return channels[0]
    
    def test_mark_as_read_requires_auth(self):
        """Test mark as read requires authentication"""
        response = requests.post(f"{BASE_URL}/api/lumi/channels/test_ch/read")
        assert response.status_code == 401
        print(f"✅ Mark as read requires authentication (401)")
    
    def test_mark_as_read_success(self, auth_token, test_channel):
        """Test marking a channel as read"""
        response = requests.post(
            f"{BASE_URL}/api/lumi/channels/{test_channel['id']}/read",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Mark as read failed: {response.text}"
        data = response.json()
        assert data.get("status") == "read", f"Expected status 'read', got {data}"
        print(f"✅ Channel {test_channel['id']} marked as read")
    
    def test_get_read_status_requires_auth(self):
        """Test get read status requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/channels/test_ch/read-status")
        assert response.status_code == 401
        print(f"✅ Get read status requires authentication (401)")
    
    def test_get_read_status_success(self, auth_token, test_channel):
        """Test getting read receipts for a channel"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels/{test_channel['id']}/read-status",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get read status failed: {response.text}"
        data = response.json()
        assert "receipts" in data, "Response should have 'receipts' field"
        assert isinstance(data["receipts"], list), "Receipts should be a list"
        print(f"✅ Read status retrieved: {len(data['receipts'])} receipts")
    
    def test_unread_counts_requires_auth(self):
        """Test unread counts requires authentication"""
        response = requests.get(f"{BASE_URL}/api/lumi/unread-counts")
        assert response.status_code == 401
        print(f"✅ Unread counts requires authentication (401)")
    
    def test_unread_counts_success(self, auth_token):
        """Test getting unread message counts"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/unread-counts",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Get unread counts failed: {response.text}"
        data = response.json()
        assert "unread" in data, "Response should have 'unread' field"
        assert isinstance(data["unread"], dict), "Unread should be a dict"
        print(f"✅ Unread counts retrieved: {len(data['unread'])} channels with unread messages")
        for ch_id, count in list(data["unread"].items())[:5]:
            print(f"   Channel {ch_id}: {count} unread")


class TestAiThemeSummarization:
    """Tests for AI-Powered Theme Summarization feature"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_ai_summary_requires_auth(self):
        """Test AI summary requires authentication"""
        response = requests.get(f"{BASE_URL}/api/karau-meet/intelligence/ai-summary")
        assert response.status_code == 401
        print(f"✅ AI summary requires authentication (401)")
    
    def test_ai_summary_endpoint_success(self, auth_token):
        """Test AI summary endpoint returns proper structure"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/intelligence/ai-summary",
            headers={"Authorization": f"Bearer {auth_token}"},
            timeout=30  # AI calls may take a few seconds
        )
        assert response.status_code == 200, f"AI summary failed: {response.text}"
        data = response.json()
        
        # Required fields
        assert "summary" in data, "Response should have 'summary' field"
        assert "generated_at" in data, "Response should have 'generated_at' field"
        
        # Optional fields that may be present if there's data
        # key_insights and recommendations may be empty lists if no data
        if "key_insights" in data:
            assert isinstance(data["key_insights"], list), "key_insights should be a list"
        if "recommendations" in data:
            assert isinstance(data["recommendations"], list), "recommendations should be a list"
        
        print(f"✅ AI summary retrieved successfully")
        print(f"   Summary: {data['summary'][:100]}..." if len(data.get('summary', '')) > 100 else f"   Summary: {data.get('summary', 'N/A')}")
        
        if data.get("key_insights"):
            print(f"   Key Insights: {len(data['key_insights'])} items")
            for i, insight in enumerate(data['key_insights'][:3]):
                print(f"     {i+1}. {insight[:80]}..." if len(insight) > 80 else f"     {i+1}. {insight}")
        
        if data.get("recommendations"):
            print(f"   Recommendations: {len(data['recommendations'])} items")
            for i, rec in enumerate(data['recommendations'][:2]):
                print(f"     {i+1}. {rec[:80]}..." if len(rec) > 80 else f"     {i+1}. {rec}")
        
        return data
    
    def test_intelligence_summary_endpoint(self, auth_token):
        """Test intelligence summary endpoint (provides data for AI summary)"""
        response = requests.get(
            f"{BASE_URL}/api/karau-meet/intelligence/summary",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Intelligence summary failed: {response.text}"
        data = response.json()
        
        # Verify expected fields
        assert "meetings_analyzed" in data
        assert "total_action_items" in data
        assert "unresolved_items" in data
        assert "resolution_rate" in data
        assert "generated_at" in data
        
        print(f"✅ Intelligence summary retrieved:")
        print(f"   Meetings analyzed: {data['meetings_analyzed']}")
        print(f"   Total action items: {data['total_action_items']}")
        print(f"   Unresolved items: {data['unresolved_items']}")
        print(f"   Resolution rate: {data['resolution_rate']}%")


class TestExistingLumiFeatures:
    """Regression tests for existing LUMI features"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get authentication token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        })
        assert response.status_code == 200
        return response.json()["access_token"]
    
    def test_channels_list(self, auth_token):
        """Test channels list endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/channels",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "my_channels" in data
        print(f"✅ Channels list: {len(data['my_channels'])} channels")
    
    def test_dm_list(self, auth_token):
        """Test DM list endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/dm",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "dms" in data
        print(f"✅ DM list: {len(data['dms'])} conversations")
    
    def test_search_messages(self, auth_token):
        """Test search endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/lumi/search?q=test",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        print(f"✅ Search results: {len(data['results'])} messages found for 'test'")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
