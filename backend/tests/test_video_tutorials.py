"""
Test Video Tutorials API - Getting Started Section
Tests the video-file endpoint for 16 language tutorial videos
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# All 16 tutorial languages
TUTORIAL_LANGUAGES = ['de', 'fr', 'es', 'ja', 'zh', 'pt', 'ar', 'ko', 'hi', 'it', 'ru', 'nl', 'pl', 'sv', 'tr', 'vi']


class TestVideoTutorialsAPI:
    """Test video tutorials API endpoints"""
    
    def test_videos_list_endpoint(self):
        """Test GET /api/tutorials/videos returns video list"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        
        data = response.json()
        assert "videos" in data
        assert "count" in data
        assert data["count"] >= 5  # At least 5 main videos
        
    def test_tutorials_list_endpoint(self):
        """Test GET /api/tutorials/videos/tutorials returns tutorial list"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/tutorials")
        assert response.status_code == 200
        
        data = response.json()
        assert "tutorials" in data
        assert "total_languages" in data
        assert data["total_languages"] == 16
        
    @pytest.mark.parametrize("lang", TUTORIAL_LANGUAGES)
    def test_video_file_endpoint(self, lang):
        """Test GET /api/tutorials/video-file/tutorial_{lang}.mp4 returns video"""
        response = requests.get(
            f"{BASE_URL}/api/tutorials/video-file/tutorial_{lang}.mp4",
            stream=True
        )
        assert response.status_code == 200
        assert response.headers.get('content-type') == 'video/mp4'
        
        # Check file size is reasonable (> 1MB)
        content_length = response.headers.get('content-length')
        if content_length:
            assert int(content_length) > 1000000, f"Video file for {lang} is too small"
    
    def test_video_file_cors_headers(self):
        """Test CORS headers are present for video files"""
        response = requests.get(
            f"{BASE_URL}/api/tutorials/video-file/tutorial_de.mp4",
            headers={"Origin": "https://multilingual-help-5.preview.emergentagent.com"},
            stream=True
        )
        assert response.status_code == 200
        assert 'access-control-allow-origin' in response.headers
        
    def test_video_file_not_found(self):
        """Test 404 for non-existent video file"""
        response = requests.get(f"{BASE_URL}/api/tutorials/video-file/nonexistent.mp4")
        assert response.status_code == 404
        
    def test_tutorial_by_language_endpoint(self):
        """Test GET /api/tutorials/videos/tutorial/{language} returns tutorial info"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/tutorial/de")
        assert response.status_code == 200
        
        data = response.json()
        assert "video" in data
        assert data["video"]["language"] == "de"
        assert "talk_id" in data
        
    def test_tutorial_by_language_not_found(self):
        """Test 404 for non-existent language"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/tutorial/xx")
        assert response.status_code == 404


class TestVideoPlayEndpoint:
    """Test video play URL endpoint"""
    
    @pytest.mark.parametrize("lang", TUTORIAL_LANGUAGES[:5])  # Test first 5 languages
    def test_play_endpoint_returns_local_url(self, lang):
        """Test GET /api/tutorials/videos/play/{language} returns local URL"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/play/{lang}")
        assert response.status_code == 200
        
        data = response.json()
        assert "language" in data
        assert data["language"] == lang
        assert "source" in data
        # Should be local since videos are stored
        assert data["source"] == "local"
        assert "url" in data
        assert f"tutorial_{lang}.mp4" in data["url"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
