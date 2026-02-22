"""
Tests for Video Tutorial bug fixes:
1. Video modal text contrast
2. Spanish subtitles for ALL 5 videos
3. Audio translation endpoints
4. Google Translate URL format
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL').rstrip('/')

class TestSpanishSubtitles:
    """Test that Spanish subtitles are available for ALL 5 videos"""
    
    VIDEO_IDS = [
        "01_jobseeker_features",
        "02_recruiter_features",
        "03_privacy_matters",
        "04_faq_ai_compliance",
        "05_complete_overview"
    ]
    
    def test_spanish_subtitles_video_01(self):
        """Test Spanish subtitles for video 01 - Job Seeker Features"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=es")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content = response.text
        assert "WEBVTT" in content, "Expected WebVTT format"
        assert "buscador de empleo" in content.lower() or "bienvenido" in content.lower() or "karau" in content.lower(), "Expected Spanish content"
        print(f"✓ Video 01 Spanish subtitles: {len(content)} bytes")
    
    def test_spanish_subtitles_video_02(self):
        """Test Spanish subtitles for video 02 - Recruiter Features"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/02_recruiter_features?lang=es")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content = response.text
        assert "WEBVTT" in content, "Expected WebVTT format"
        assert "reclutador" in content.lower() or "contrat" in content.lower() or "candidat" in content.lower(), "Expected Spanish content for recruiters"
        print(f"✓ Video 02 Spanish subtitles: {len(content)} bytes")
    
    def test_spanish_subtitles_video_03(self):
        """Test Spanish subtitles for video 03 - Privacy Matters"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/03_privacy_matters?lang=es")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content = response.text
        assert "WEBVTT" in content, "Expected WebVTT format"
        assert "privacidad" in content.lower() or "datos" in content.lower() or "gdpr" in content.lower(), "Expected Spanish privacy content"
        print(f"✓ Video 03 Spanish subtitles: {len(content)} bytes")
    
    def test_spanish_subtitles_video_04(self):
        """Test Spanish subtitles for video 04 - FAQ AI Compliance"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/04_faq_ai_compliance?lang=es")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content = response.text
        assert "WEBVTT" in content, "Expected WebVTT format"
        assert "ia" in content.lower() or "ai" in content.lower() or "cumplimiento" in content.lower() or "preguntas" in content.lower(), "Expected Spanish AI/FAQ content"
        print(f"✓ Video 04 Spanish subtitles: {len(content)} bytes")
    
    def test_spanish_subtitles_video_05(self):
        """Test Spanish subtitles for video 05 - Complete Overview"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/05_complete_overview?lang=es")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        content = response.text
        assert "WEBVTT" in content, "Expected WebVTT format"
        assert "bienvenido" in content.lower() or "karau" in content.lower() or "viaje" in content.lower() or "carrera" in content.lower(), "Expected Spanish overview content"
        print(f"✓ Video 05 Spanish subtitles: {len(content)} bytes")
    
    def test_all_spanish_subtitles_have_content(self):
        """Verify all 5 videos have meaningful Spanish subtitle content"""
        for video_id in self.VIDEO_IDS:
            response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/{video_id}?lang=es")
            assert response.status_code == 200, f"Video {video_id}: Expected 200, got {response.status_code}"
            content = response.text
            
            # Must have proper WebVTT format with timestamps
            assert "WEBVTT" in content, f"Video {video_id}: Missing WebVTT header"
            assert "-->" in content, f"Video {video_id}: Missing timestamp markers"
            
            # Must have actual text content (not just headers)
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('WEBVTT') and '-->' not in l]
            text_lines = [l for l in lines if len(l) > 5 and not l.startswith('00:')]
            assert len(text_lines) >= 3, f"Video {video_id}: Expected at least 3 text lines, got {len(text_lines)}"
            
            print(f"✓ {video_id}: {len(text_lines)} text lines")


class TestVideoListAPI:
    """Test the video listing API"""
    
    def test_videos_list(self):
        """Test that videos list returns all 5 videos"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        assert data["count"] == 5, f"Expected 5 videos, got {data['count']}"
        
        video_ids = [v["id"] for v in data["videos"]]
        assert "01_jobseeker_features" in video_ids
        assert "02_recruiter_features" in video_ids
        assert "03_privacy_matters" in video_ids
        assert "04_faq_ai_compliance" in video_ids
        assert "05_complete_overview" in video_ids
        print(f"✓ Videos API returns all 5 videos")


class TestAudioTranslation:
    """Test audio translation endpoints"""
    
    def test_translate_status_endpoint(self):
        """Test the translation status endpoint exists"""
        response = requests.get(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features/status?lang=es")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        print(f"✓ Translation status endpoint works: {data['status']}")
    
    def test_translate_request_endpoint(self):
        """Test requesting a translation"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=es")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["generating", "ready"]
        print(f"✓ Translation request endpoint works: {data['status']}")


class TestMultiLanguageSubtitles:
    """Test subtitles work for multiple languages"""
    
    def test_english_subtitles(self):
        """Test English subtitles"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=en")
        assert response.status_code == 200
        assert "WEBVTT" in response.text
        assert "Welcome" in response.text or "MedMatch" in response.text
        print("✓ English subtitles work")
    
    def test_french_subtitles(self):
        """Test French subtitles"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=fr")
        assert response.status_code == 200
        assert "WEBVTT" in response.text
        print("✓ French subtitles work")
    
    def test_german_subtitles(self):
        """Test German subtitles"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=de")
        assert response.status_code == 200
        assert "WEBVTT" in response.text
        print("✓ German subtitles work")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
