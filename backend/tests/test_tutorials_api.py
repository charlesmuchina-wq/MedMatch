"""
Video Tutorials API Tests
Tests: Video listing, video streaming, guide endpoint
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Expected videos from the tutorials API
EXPECTED_VIDEOS = [
    "01_jobseeker_intro",
    "02_recruiter_dashboard",
    "03_job_search",
    "04_ats_system",
    "05_resume_upload",
    "06_interview_prep"
]


class TestTutorialsAPI:
    """Test tutorials API endpoints"""
    
    def test_list_all_videos(self):
        """GET /api/tutorials/videos - List all tutorial videos"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        print(f"GET /api/tutorials/videos: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert "videos" in data, "Response should contain videos array"
        assert "count" in data, "Response should contain count"
        assert data["count"] == 6, f"Expected 6 videos, got {data['count']}"
        
        # Verify all expected videos are present
        video_ids = [v["id"] for v in data["videos"]]
        for expected_id in EXPECTED_VIDEOS:
            assert expected_id in video_ids, f"Video {expected_id} should be in list"
        
        print(f"Found {data['count']} videos")
    
    def test_list_videos_by_category_job_seeker(self):
        """GET /api/tutorials/videos?category=job_seeker - Filter by job seeker category"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos", params={"category": "job_seeker"})
        print(f"GET /api/tutorials/videos?category=job_seeker: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned videos should be job_seeker category
        for video in data["videos"]:
            assert video["category"] == "job_seeker", f"Video {video['id']} should be job_seeker category"
        
        print(f"Found {data['count']} job seeker videos")
    
    def test_list_videos_by_category_recruiter(self):
        """GET /api/tutorials/videos?category=recruiter - Filter by recruiter category"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos", params={"category": "recruiter"})
        print(f"GET /api/tutorials/videos?category=recruiter: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        # All returned videos should be recruiter category
        for video in data["videos"]:
            assert video["category"] == "recruiter", f"Video {video['id']} should be recruiter category"
        
        print(f"Found {data['count']} recruiter videos")
    
    def test_video_metadata_structure(self):
        """Verify video metadata has all required fields"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["id", "title", "description", "duration", "category", "filename", "url", "exists"]
        
        for video in data["videos"]:
            for field in required_fields:
                assert field in video, f"Video {video.get('id', 'unknown')} missing field: {field}"
            
            # Verify video file exists
            assert video["exists"] == True, f"Video file {video['filename']} should exist"
        
        print("All videos have required metadata fields")
    
    def test_get_video_stream_valid(self):
        """GET /api/tutorials/videos/:video_id - Stream a valid video"""
        video_id = "01_jobseeker_intro"
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/{video_id}", stream=True)
        print(f"GET /api/tutorials/videos/{video_id}: {response.status_code}")
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert response.headers.get("content-type") == "video/mp4", "Content-Type should be video/mp4"
        
        # Verify we get some content
        content_length = response.headers.get("content-length")
        if content_length:
            assert int(content_length) > 0, "Video should have content"
            print(f"Video size: {int(content_length) / 1024:.1f} KB")
    
    def test_get_video_stream_invalid(self):
        """GET /api/tutorials/videos/:video_id - Invalid video returns 404"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/invalid_video_id")
        print(f"GET /api/tutorials/videos/invalid_video_id: {response.status_code}")
        
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    def test_get_navigation_guide(self):
        """GET /api/tutorials/guide - Get navigation guide"""
        response = requests.get(f"{BASE_URL}/api/tutorials/guide")
        print(f"GET /api/tutorials/guide: {response.status_code}")
        
        # Guide may or may not exist
        if response.status_code == 200:
            data = response.json()
            assert "title" in data, "Response should contain title"
            assert "content" in data, "Response should contain content"
            assert "format" in data, "Response should contain format"
            print(f"Guide title: {data.get('title', 'N/A')}")
        elif response.status_code == 404:
            print("Navigation guide not found (optional)")
        else:
            print(f"Unexpected status: {response.status_code}")


class TestVideoContent:
    """Test video content and streaming"""
    
    def test_all_videos_streamable(self):
        """Verify all videos can be streamed"""
        for video_id in EXPECTED_VIDEOS:
            response = requests.get(f"{BASE_URL}/api/tutorials/videos/{video_id}", stream=True)
            assert response.status_code == 200, f"Video {video_id} should be streamable"
            print(f"Video {video_id}: OK")
    
    def test_video_content_type(self):
        """Verify videos return correct content type"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/01_jobseeker_intro", stream=True)
        assert response.status_code == 200
        
        content_type = response.headers.get("content-type")
        assert content_type == "video/mp4", f"Expected video/mp4, got {content_type}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
