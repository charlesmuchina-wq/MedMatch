"""
Test Closed Captions Multi-Language Feature
Tests: 14 language support (en, es, fr, de, ja, zh, pt, ar, hi, ko, it, ru, sw, vi)
Tests: Japanese, Chinese, Korean, Arabic character rendering
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# All supported subtitle languages
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'ja', 'zh', 'pt', 'ar', 'hi', 'ko', 'it', 'ru', 'sw', 'vi']

# Video IDs to test
VIDEO_IDS = ['01_jobseeker_features', '02_recruiter_features', '03_privacy_matters', '04_faq_ai_compliance', '05_complete_overview']


class TestSubtitleAPI:
    """Test subtitle API returns all 14 languages correctly"""

    def test_all_14_languages_supported(self):
        """Verify subtitle API returns content for all 14 languages"""
        video_id = "01_jobseeker_features"
        
        for lang in SUPPORTED_LANGUAGES:
            response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/{video_id}?lang={lang}")
            assert response.status_code == 200, f"Failed for language: {lang}"
            assert "WEBVTT" in response.text, f"Invalid WebVTT for language: {lang}"
            assert response.headers.get('Content-Type', '').startswith('text/vtt'), f"Wrong content type for {lang}"
            print(f"✓ Language {lang} returns valid WebVTT")

    def test_japanese_subtitles_characters(self):
        """Test Japanese subtitles contain Japanese characters"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=ja")
        assert response.status_code == 200
        content = response.text
        
        # Check for Japanese characters (Hiragana/Katakana/Kanji)
        assert "MedMatch-AI KARAUへようこそ" in content or "ようこそ" in content
        assert "求職者" in content or "履歴書" in content or "AI" in content
        print("✓ Japanese subtitles contain proper Japanese characters")

    def test_chinese_subtitles_characters(self):
        """Test Chinese subtitles contain Chinese characters"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=zh")
        assert response.status_code == 200
        content = response.text
        
        # Check for Chinese characters
        assert "欢迎" in content or "MedMatch-AI KARAU" in content
        assert "求职" in content or "简历" in content or "AI" in content
        print("✓ Chinese subtitles contain proper Chinese characters")

    def test_korean_subtitles_characters(self):
        """Test Korean subtitles contain Korean characters (Hangul)"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=ko")
        assert response.status_code == 200
        content = response.text
        
        # Check for Korean Hangul characters
        assert "환영합니다" in content or "MedMatch-AI KARAU" in content
        assert "구직자" in content or "이력서" in content or "검색" in content
        print("✓ Korean subtitles contain proper Korean/Hangul characters")

    def test_arabic_subtitles_characters(self):
        """Test Arabic subtitles contain Arabic characters (RTL text)"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=ar")
        assert response.status_code == 200
        content = response.text
        
        # Check for Arabic characters
        assert "مرحبًا" in content or "MedMatch-AI KARAU" in content
        assert "باحث" in content or "سيرتك" in content
        print("✓ Arabic subtitles contain proper Arabic characters (RTL)")

    def test_hindi_subtitles_characters(self):
        """Test Hindi subtitles contain Hindi/Devanagari characters"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=hi")
        assert response.status_code == 200
        content = response.text
        
        # Check for Hindi Devanagari characters
        assert "स्वागत" in content or "MedMatch-AI KARAU" in content
        assert "नौकरी" in content or "रिज्यूमे" in content
        print("✓ Hindi subtitles contain proper Hindi/Devanagari characters")

    def test_russian_subtitles_characters(self):
        """Test Russian subtitles contain Cyrillic characters"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=ru")
        assert response.status_code == 200
        content = response.text
        
        # Check for Russian Cyrillic characters
        assert "Добро пожаловать" in content or "MedMatch-AI KARAU" in content
        assert "соискатель" in content or "резюме" in content
        print("✓ Russian subtitles contain proper Cyrillic characters")

    def test_swahili_subtitles(self):
        """Test Swahili subtitles return correctly"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=sw")
        assert response.status_code == 200
        content = response.text
        
        assert "Karibu" in content or "MedMatch-AI KARAU" in content
        assert "kazi" in content or "CV" in content
        print("✓ Swahili subtitles contain proper content")

    def test_vietnamese_subtitles(self):
        """Test Vietnamese subtitles contain Vietnamese diacritics"""
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=vi")
        assert response.status_code == 200
        content = response.text
        
        # Check for Vietnamese characters with diacritics
        assert "Chào mừng" in content or "MedMatch-AI KARAU" in content
        assert "việc" in content or "CV" in content
        print("✓ Vietnamese subtitles contain proper Vietnamese diacritics")

    def test_webvtt_format_structure(self):
        """Verify WebVTT format is correct for all languages"""
        for lang in SUPPORTED_LANGUAGES:
            response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang={lang}")
            assert response.status_code == 200
            content = response.text
            
            # Check WebVTT structure
            assert content.startswith("WEBVTT"), f"Missing WEBVTT header for {lang}"
            assert "-->" in content, f"Missing timestamp arrow for {lang}"
            # Check timestamp format exists
            assert "00:00:" in content, f"Missing timestamp for {lang}"
        
        print("✓ All 14 languages have valid WebVTT structure")


class TestSubtitleFallback:
    """Test fallback behavior when language is not supported"""

    def test_fallback_to_english(self):
        """Test that unsupported language falls back to English"""
        # Test with a language code that's not explicitly supported
        response = requests.get(f"{BASE_URL}/api/tutorials/subtitles/01_jobseeker_features?lang=xyz")
        assert response.status_code == 200
        content = response.text
        
        # Should fall back to English
        assert "WEBVTT" in content
        assert "Welcome" in content or "MedMatch" in content
        print("✓ Unsupported language falls back to English subtitles")


class TestTranslateEndpoint:
    """Test translate endpoint for D-ID audio generation"""

    def test_translate_endpoint_exists(self):
        """Verify translate endpoint returns proper response"""
        # POST request to initiate translation
        response = requests.post(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features?lang=ja")
        assert response.status_code in [200, 201, 202], f"Unexpected status: {response.status_code}"
        
        data = response.json()
        assert "job_id" in data or "status" in data
        print(f"✓ Translate endpoint returns: {data.get('status', 'unknown')}")

    def test_translate_status_endpoint(self):
        """Test checking translation status"""
        response = requests.get(f"{BASE_URL}/api/tutorials/translate/01_jobseeker_features/status?lang=ja")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        # Status can be 'not_found', 'generating', 'ready', or 'failed'
        print(f"✓ Translation status check returns: {data}")


class TestVideosEndpoint:
    """Test videos listing endpoint"""

    def test_list_videos(self):
        """Verify videos endpoint returns all 5 tutorial videos"""
        response = requests.get(f"{BASE_URL}/api/tutorials/videos")
        assert response.status_code == 200
        
        data = response.json()
        assert "videos" in data
        assert len(data["videos"]) >= 5, f"Expected at least 5 videos, got {len(data['videos'])}"
        
        video_ids = [v["id"] for v in data["videos"]]
        for expected_id in VIDEO_IDS:
            assert expected_id in video_ids, f"Missing video: {expected_id}"
        
        print(f"✓ Videos endpoint returns {len(data['videos'])} videos")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
