"""
Video Subtitles API Tests
Tests for subtitle/caption endpoints for tutorial videos
Feature: Video player closed captions with multi-language support
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://lumi-prestige.preview.emergentagent.com').rstrip('/')

# Test video IDs as specified in the bug report
VIDEO_IDS = [
    "01_jobseeker_features",
    "02_recruiter_features", 
    "03_privacy_matters",
    "04_faq_ai_compliance",
    "05_complete_overview"
]

# Supported subtitle languages
LANGUAGES = ["en", "es", "fr", "de"]


class TestSubtitleEndpoints:
    """Test /api/tutorials/subtitles/{video_id} endpoint"""
    
    def test_subtitles_endpoint_returns_200_for_all_videos_english(self):
        """Test that all 5 videos have English subtitles available"""
        for video_id in VIDEO_IDS:
            response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/{video_id}?lang=en")
            assert response.status_code == 200, f"Video {video_id} English subtitle endpoint failed: {response.status_code}"
            
    def test_subtitles_return_valid_webvtt_format(self):
        """Test that subtitles return valid WebVTT content"""
        for video_id in VIDEO_IDS:
            response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/{video_id}?lang=en")
            assert response.status_code == 200
            
            content = response.text
            # WebVTT files must start with "WEBVTT"
            assert content.strip().startswith("WEBVTT"), f"Video {video_id} subtitle not in WebVTT format"
            # Should contain timestamp format
            assert "-->" in content, f"Video {video_id} subtitle missing timestamp markers"
            
    def test_subtitles_have_correct_content_type(self):
        """Test that content type is text/vtt"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=en")
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "text/vtt" in content_type, f"Expected text/vtt, got {content_type}"
        
    def test_spanish_subtitles_available(self):
        """Test Spanish subtitle availability as specified in bug report"""
        # As per bug report: Spanish subtitles available at /api/tutorials/subtitles/{video_id}?lang=es
        for video_id in ["01_jobseeker_features", "02_recruiter_features"]:
            response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/{video_id}?lang=es")
            assert response.status_code == 200, f"Video {video_id} Spanish subtitle not available"
            
            content = response.text
            assert content.strip().startswith("WEBVTT"), "Spanish subtitle not in WebVTT format"
            # Spanish content should contain Spanish characters/words
            assert any(char in content for char in ["á", "é", "í", "ó", "ú", "ñ", "¡", "¿"]) or "Bienvenido" in content, \
                f"Video {video_id} Spanish subtitle may not contain Spanish content"
                
    def test_french_subtitles_available(self):
        """Test French subtitle availability"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=fr")
        assert response.status_code == 200
        content = response.text
        assert "Bienvenue" in content or "français" in content.lower() or "votre" in content, \
            "French subtitle may not contain French content"
            
    def test_german_subtitles_available(self):
        """Test German subtitle availability"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=de")
        assert response.status_code == 200
        content = response.text
        assert "Willkommen" in content or "Sie" in content, \
            "German subtitle may not contain German content"
            
    def test_fallback_to_english_for_unsupported_language(self):
        """Test that unsupported language falls back to English"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=xyz")
        assert response.status_code == 200
        content = response.text
        assert "WEBVTT" in content, "Fallback subtitle should still be valid WebVTT"
        # Should contain English content as fallback
        assert "MedMatch" in content or "Welcome" in content, "Should fallback to English content"


class TestVideoListEndpoint:
    """Test /api/tutorials/videos endpoint"""
    
    def test_videos_list_returns_all_5_videos(self):
        """Test that videos list endpoint returns all 5 tutorial videos"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        
        data = response.json()
        assert "videos" in data
        assert len(data["videos"]) == 5, f"Expected 5 videos, got {len(data['videos'])}"
        
    def test_videos_list_contains_expected_video_ids(self):
        """Test that all expected video IDs are present"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        
        data = response.json()
        video_ids = [v["id"] for v in data["videos"]]
        
        for expected_id in VIDEO_IDS:
            assert expected_id in video_ids, f"Missing video: {expected_id}"


class TestSubtitleContentQuality:
    """Test subtitle content quality and completeness"""
    
    def test_jobseeker_features_subtitle_has_multiple_cues(self):
        """Test that jobseeker features video has multiple subtitle cues"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=en")
        assert response.status_code == 200
        
        content = response.text
        # Count timestamp markers (-->)
        cue_count = content.count("-->")
        assert cue_count >= 4, f"Expected at least 4 subtitle cues, got {cue_count}"
        
    def test_subtitle_timestamps_are_valid_format(self):
        """Test that subtitle timestamps follow WebVTT format"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=en")
        assert response.status_code == 200
        
        content = response.text
        # WebVTT timestamp format: HH:MM:SS.mmm --> HH:MM:SS.mmm
        import re
        timestamp_pattern = r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}"
        matches = re.findall(timestamp_pattern, content)
        assert len(matches) >= 4, f"Expected valid timestamp format, found {len(matches)} valid timestamps"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
