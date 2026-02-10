"""
Video Tutorials API Tests
Tests for the GettingStartedSection video player and language selector
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
        assert data["count"] >= 5
        print(f"Videos list: {data['count']} videos found")
    
    def test_tutorials_list_endpoint(self):
        """Test GET /api/tutorials/videos/tutorials returns 16 languages"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/tutorials")
        assert response.status_code == 200
        data = response.json()
        assert "tutorials" in data
        assert "total_languages" in data
        assert data["total_languages"] == 16
        print(f"Tutorials: {data['total_languages']} languages available")
    
    @pytest.mark.parametrize("lang", TUTORIAL_LANGUAGES)
    def test_video_file_endpoint(self, lang):
        """Test GET /api/tutorials/video-file/tutorial_{lang}.mp4 returns video"""
        response = requests.get(
            f"{BASE_URL}/api/tutorials/video-file/tutorial_{lang}.mp4",
            stream=True
        )
        assert response.status_code == 200
        assert response.headers.get("content-type") == "video/mp4"
        assert "accept-ranges" in response.headers
        assert response.headers.get("accept-ranges") == "bytes"
        # Check content-length is reasonable (> 1MB)
        content_length = int(response.headers.get("content-length", 0))
        assert content_length > 1000000, f"Video {lang} too small: {content_length} bytes"
        print(f"Video {lang}: {content_length / 1024 / 1024:.2f} MB")
    
    @pytest.mark.parametrize("lang", TUTORIAL_LANGUAGES[:3])  # Test first 3 languages
    def test_video_range_request(self, lang):
        """Test range requests return HTTP 206 with correct headers"""
        response = requests.get(
            f"{BASE_URL}/api/tutorials/video-file/tutorial_{lang}.mp4",
            headers={"Range": "bytes=0-1000"}
        )
        assert response.status_code == 206
        assert "content-range" in response.headers
        assert response.headers.get("content-type") == "video/mp4"
        content_range = response.headers.get("content-range")
        assert content_range.startswith("bytes 0-1000/")
        print(f"Range request {lang}: {content_range}")
    
    def test_video_file_not_found(self):
        """Test non-existent video returns 404"""
        response = requests.get(f"{BASE_URL}/api/tutorials/video-file/nonexistent.mp4")
        assert response.status_code == 404
    
    def test_video_content_valid_mp4(self):
        """Test video content starts with valid MP4 header (ftyp)"""
        response = requests.get(
            f"{BASE_URL}/api/tutorials/video-file/tutorial_de.mp4",
            headers={"Range": "bytes=0-31"}
        )
        assert response.status_code == 206
        content = response.content
        # MP4 files start with ftyp box
        assert b'ftyp' in content[:32], "Video does not have valid MP4 header"
        print("Video has valid MP4 header (ftyp)")
    
    def test_video_moov_atom_position(self):
        """Test moov atom is near the beginning (faststart)"""
        response = requests.get(
            f"{BASE_URL}/api/tutorials/video-file/tutorial_de.mp4",
            headers={"Range": "bytes=0-100"}
        )
        assert response.status_code == 206
        content = response.content
        # moov atom should be within first 100 bytes for faststart
        assert b'moov' in content, "moov atom not found in first 100 bytes - faststart may not be enabled"
        moov_pos = content.find(b'moov')
        print(f"moov atom found at position {moov_pos}")
        assert moov_pos < 50, f"moov atom at position {moov_pos} - should be near beginning"


class TestVideoTutorialMetadata:
    """Test video tutorial metadata endpoints"""
    
    def test_tutorial_by_language(self):
        """Test GET /api/tutorials/videos/tutorial/{language}"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/tutorial/de")
        assert response.status_code == 200
        data = response.json()
        assert "video" in data
        assert data["video"]["language"] == "de"
        print(f"German tutorial: {data['video']['title']}")
    
    def test_tutorial_invalid_language(self):
        """Test invalid language returns 404 with available languages"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/tutorial/invalid")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "available_languages" in data["detail"]
    
    def test_multilang_videos_endpoint(self):
        """Test GET /api/tutorials/videos/multilang"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/multilang")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "tutorials" in data
        assert "default_language" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
