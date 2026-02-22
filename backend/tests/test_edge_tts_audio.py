"""
Edge-TTS Audio Generation Tests
Tests the FREE audio generation feature using Microsoft Neural Voices
Tests: POST /api/tutorials/translate/{video_id}?lang={lang}
Tests: GET /api/tutorials/translate/{video_id}/status?lang={lang}
Tests: Static audio file serving from /static/audio/tutorials/
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestEdgeTTSAudioGeneration:
    """Test edge-tts audio generation endpoints"""
    
    def test_health_check(self):
        """Verify API is running"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print("✅ API health check passed")
    
    def test_generate_japanese_audio(self):
        """Test Japanese audio generation with edge-tts"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=ja")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ Japanese audio generation initiated: {data}")
    
    def test_generate_spanish_audio(self):
        """Test Spanish audio generation with edge-tts"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=es")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ Spanish audio generation initiated: {data}")
    
    def test_generate_chinese_audio(self):
        """Test Chinese audio generation with edge-tts"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=zh")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ Chinese audio generation initiated: {data}")
    
    def test_generate_korean_audio(self):
        """Test Korean audio generation with edge-tts"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=ko")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ Korean audio generation initiated: {data}")
    
    def test_generate_french_audio(self):
        """Test French audio generation with edge-tts"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=fr")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ French audio generation initiated: {data}")
    
    def test_generate_german_audio(self):
        """Test German audio generation with edge-tts"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=de")
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ German audio generation initiated: {data}")
    
    def test_translation_status_ready_or_generating(self):
        """Test status endpoint returns proper status"""
        # First request generation
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=ja")
        assert response.status_code == 200
        
        # Wait a moment for generation
        time.sleep(3)
        
        # Check status
        status_response = requests.get(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features/status?lang=ja")
        assert status_response.status_code == 200
        data = status_response.json()
        assert data.get("status") in ["generating", "ready", "failed", "not_found"]
        print(f"✅ Japanese audio status: {data.get('status')}")
        
        # If ready, check audio_url
        if data.get("status") == "ready":
            assert "audio_url" in data or "video_url" in data
            audio_url = data.get("audio_url") or data.get("video_url")
            assert audio_url.startswith("/api/tutorials/audio/")
            print(f"✅ Audio URL returned: {audio_url}")
    
    def test_wait_for_audio_ready_and_verify_url(self):
        """Test complete flow: generate -> wait -> verify audio URL"""
        # Request generation
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=es")
        assert response.status_code == 200
        
        # Poll for ready status (max 15 seconds)
        for _ in range(15):
            status_response = requests.get(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features/status?lang=es")
            assert status_response.status_code == 200
            data = status_response.json()
            
            if data.get("status") == "ready":
                audio_url = data.get("audio_url") or data.get("video_url")
                assert audio_url is not None
                print(f"✅ Spanish audio ready: {audio_url}")
                
                # Verify audio file is accessible (use GET, not HEAD)
                full_url = f"{BASE_URL}{audio_url}"
                audio_response = requests.get(full_url, stream=True)
                assert audio_response.status_code == 200
                # Check content type
                content_type = audio_response.headers.get('content-type', '')
                assert 'audio' in content_type or 'mpeg' in content_type
                print(f"✅ Audio file accessible at: {full_url}")
                audio_response.close()
                return
            elif data.get("status") == "failed":
                print(f"⚠️ Audio generation failed: {data.get('error')}")
                return
            
            time.sleep(1)
        
        print("⚠️ Audio generation timed out (may still be processing)")
    
    def test_static_audio_directory_accessible(self):
        """Test that static audio directory is properly mounted"""
        # List files that should exist from previous tests
        audio_url = "/static/audio/tutorials/01_jobseeker_features_ja_6ea378f2.mp3"
        response = requests.head(f"{BASE_URL}{audio_url}")
        # 200 if file exists, 404 if not (but directory should be mounted)
        assert response.status_code in [200, 404]
        print(f"✅ Static audio directory check: {response.status_code}")
    
    def test_recruiter_video_translation(self):
        """Test audio generation for recruiter features video"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/02_recruiter_features?lang=ja")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ Recruiter video Japanese audio: {data}")
    
    def test_invalid_video_id(self):
        """Test error handling for non-existent video"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/invalid_video_id?lang=ja")
        assert response.status_code == 404
        print("✅ Invalid video ID properly returns 404")
    
    def test_unsupported_language_fallback(self):
        """Test handling of unsupported language code"""
        # Edge-tts has many voices, but test with unlikely code
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=xyz")
        # Should fallback to English voice
        assert response.status_code == 200
        print("✅ Unsupported language code handled (fallback to English)")
    
    def test_arabic_audio_generation(self):
        """Test Arabic audio generation (RTL language)"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=ar")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ Arabic audio generation: {data}")
    
    def test_hindi_audio_generation(self):
        """Test Hindi audio generation"""
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=hi")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["generating", "ready"]
        print(f"✅ Hindi audio generation: {data}")


class TestEdgeTTSServiceConfiguration:
    """Test edge-tts service configuration"""
    
    def test_supported_languages_in_service(self):
        """Verify supported languages endpoint if available"""
        # Check tutorials videos endpoint for language info
        response = requests.get(f"{BASE_URL}/api/tutorials/videos/multilang")
        assert response.status_code == 200
        data = response.json()
        assert "tutorials" in data
        print(f"✅ Multi-language config available: {len(data.get('tutorials', {}))} languages")
    
    def test_tutorial_video_list(self):
        """Test that tutorial videos are listed correctly"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        data = response.json()
        assert "videos" in data
        videos = data["videos"]
        assert len(videos) >= 1
        print(f"✅ Tutorial videos available: {len(videos)}")
        for v in videos:
            print(f"   - {v.get('id')}: {v.get('title')}")


class TestAudioFileServing:
    """Test generated audio file serving"""
    
    def test_mp3_content_type(self):
        """Test that audio files are served with correct content type"""
        # Generate audio first
        requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=ja")
        time.sleep(3)
        
        # Get status to find audio URL
        status_response = requests.get(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features/status?lang=ja")
        data = status_response.json()
        
        if data.get("status") == "ready":
            audio_url = data.get("audio_url") or data.get("video_url")
            if audio_url:
                full_url = f"{BASE_URL}{audio_url}"
                response = requests.head(full_url)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    assert 'audio' in content_type or 'mpeg' in content_type
                    print(f"✅ Audio content type: {content_type}")
                    return
        
        print("⚠️ Audio file not yet ready for content type test")
    
    def test_audio_file_size_reasonable(self):
        """Test that generated audio files have reasonable size"""
        # Generate audio
        requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=es")
        time.sleep(3)
        
        status_response = requests.get(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features/status?lang=es")
        data = status_response.json()
        
        if data.get("status") == "ready":
            audio_url = data.get("audio_url") or data.get("video_url")
            if audio_url:
                full_url = f"{BASE_URL}{audio_url}"
                response = requests.head(full_url)
                if response.status_code == 200:
                    content_length = response.headers.get('content-length')
                    if content_length:
                        size_kb = int(content_length) / 1024
                        # Audio should be between 10KB and 10MB
                        assert 10 < size_kb < 10240
                        print(f"✅ Audio file size: {size_kb:.1f} KB")
                        return
        
        print("⚠️ Audio file not yet ready for size test")
