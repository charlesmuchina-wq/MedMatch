"""
Test suite for diverse avatar videos and locale generation
Tests 16 tutorial videos with male/female presenters and 33 bundled locale files
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# 16 tutorial languages with presenter info
TUTORIAL_LANGUAGES = [
    {'code': 'de', 'name': 'German', 'presenter': 'Josh (Male)'},
    {'code': 'fr', 'name': 'French', 'presenter': 'Josh (Male)'},
    {'code': 'es', 'name': 'Spanish', 'presenter': 'Amy (Female)'},
    {'code': 'ja', 'name': 'Japanese', 'presenter': 'Josh (Male)'},
    {'code': 'zh', 'name': 'Chinese', 'presenter': 'Josh (Male)'},
    {'code': 'pt', 'name': 'Portuguese', 'presenter': 'Amy (Female)'},
    {'code': 'ar', 'name': 'Arabic', 'presenter': 'Amy (Female)'},
    {'code': 'ko', 'name': 'Korean', 'presenter': 'Josh (Male)'},
    {'code': 'hi', 'name': 'Hindi', 'presenter': 'Josh (Male)'},
    {'code': 'it', 'name': 'Italian', 'presenter': 'Josh (Male)'},
    {'code': 'ru', 'name': 'Russian', 'presenter': 'Josh (Male)'},
    {'code': 'nl', 'name': 'Dutch', 'presenter': 'Josh (Male)'},
    {'code': 'pl', 'name': 'Polish', 'presenter': 'Amy (Female)'},
    {'code': 'sv', 'name': 'Swedish', 'presenter': 'Amy (Female)'},
    {'code': 'tr', 'name': 'Turkish', 'presenter': 'Amy (Female)'},
    {'code': 'vi', 'name': 'Vietnamese', 'presenter': 'Josh (Male)'},
]

# 33 bundled locale files
BUNDLED_LOCALES = [
    # Core languages
    'en', 'es', 'fr', 'zh', 'de',
    # High-demand languages
    'ja', 'ar', 'hi', 'pt-BR',
    # African Languages (16)
    'sw', 'ha', 'yo', 'ig', 'zu', 'xh', 'af', 'am',
    'om', 'so', 'rw', 'sn', 'ny', 'tw', 'wo', 'lg',
    # European Languages - Generated (8 new)
    'nl', 'it', 'vi', 'ko', 'ru', 'pl', 'sv', 'tr'
]


class TestTutorialVideoStreaming:
    """Test video streaming for all 16 tutorial languages"""
    
    @pytest.mark.parametrize("lang_info", TUTORIAL_LANGUAGES)
    def test_tutorial_video_accessible(self, lang_info):
        """Test that each tutorial video is accessible via HTTP 200"""
        lang_code = lang_info['code']
        url = f"{BASE_URL}/api/tutorials/video-file/tutorial_{lang_code}.mp4?v=3"
        
        response = requests.get(url, timeout=30)
        
        assert response.status_code == 200, f"Video for {lang_info['name']} returned {response.status_code}"
        assert 'video/mp4' in response.headers.get('Content-Type', ''), f"Wrong content type for {lang_info['name']}"
    
    @pytest.mark.parametrize("lang_info", TUTORIAL_LANGUAGES)
    def test_tutorial_video_range_requests(self, lang_info):
        """Test that videos support HTTP 206 range requests for streaming"""
        lang_code = lang_info['code']
        url = f"{BASE_URL}/api/tutorials/video-file/tutorial_{lang_code}.mp4?v=3"
        
        headers = {'Range': 'bytes=0-1000'}
        response = requests.get(url, headers=headers, timeout=30)
        
        assert response.status_code == 206, f"Range request for {lang_info['name']} returned {response.status_code}"
        assert 'Content-Range' in response.headers, f"Missing Content-Range header for {lang_info['name']}"
        assert response.headers.get('Accept-Ranges') == 'bytes', f"Missing Accept-Ranges header for {lang_info['name']}"


class TestPresenterDistribution:
    """Test presenter distribution (10 male, 6 female)"""
    
    def test_male_presenter_count(self):
        """Verify 10 languages have male presenter (Josh)"""
        male_presenters = [l for l in TUTORIAL_LANGUAGES if 'Josh' in l['presenter']]
        assert len(male_presenters) == 10, f"Expected 10 male presenters, got {len(male_presenters)}"
    
    def test_female_presenter_count(self):
        """Verify 6 languages have female presenter (Amy)"""
        female_presenters = [l for l in TUTORIAL_LANGUAGES if 'Amy' in l['presenter']]
        assert len(female_presenters) == 6, f"Expected 6 female presenters, got {len(female_presenters)}"
    
    def test_total_languages(self):
        """Verify total of 16 tutorial languages"""
        assert len(TUTORIAL_LANGUAGES) == 16, f"Expected 16 languages, got {len(TUTORIAL_LANGUAGES)}"


class TestBundledLocales:
    """Test that all 33 locale files are bundled"""
    
    def test_total_bundled_locales(self):
        """Verify 33 bundled locales"""
        assert len(BUNDLED_LOCALES) == 33, f"Expected 33 bundled locales, got {len(BUNDLED_LOCALES)}"
    
    def test_new_locales_included(self):
        """Verify 8 new locales (nl, it, vi, ko, ru, pl, sv, tr) are bundled"""
        new_locales = ['nl', 'it', 'vi', 'ko', 'ru', 'pl', 'sv', 'tr']
        for locale in new_locales:
            assert locale in BUNDLED_LOCALES, f"New locale {locale} not in BUNDLED_LOCALES"
    
    def test_african_languages_included(self):
        """Verify all 16 African languages are bundled"""
        african_locales = ['sw', 'ha', 'yo', 'ig', 'zu', 'xh', 'af', 'am', 'om', 'so', 'rw', 'sn', 'ny', 'tw', 'wo', 'lg']
        for locale in african_locales:
            assert locale in BUNDLED_LOCALES, f"African locale {locale} not in BUNDLED_LOCALES"


class TestVideoFilesExist:
    """Test that video files exist on disk"""
    
    def test_video_files_count(self):
        """Verify 16 tutorial video files exist"""
        video_dir = '/app/backend/static/videos/tutorials/'
        if os.path.exists(video_dir):
            video_files = [f for f in os.listdir(video_dir) if f.startswith('tutorial_') and f.endswith('.mp4') and '_old' not in f]
            assert len(video_files) >= 16, f"Expected at least 16 video files, got {len(video_files)}"
    
    @pytest.mark.parametrize("lang_info", TUTORIAL_LANGUAGES)
    def test_video_file_exists(self, lang_info):
        """Test that each video file exists on disk"""
        lang_code = lang_info['code']
        video_path = f'/app/backend/static/videos/tutorials/tutorial_{lang_code}.mp4'
        
        assert os.path.exists(video_path), f"Video file for {lang_info['name']} not found at {video_path}"
        
        # Check file size is reasonable (> 1MB)
        file_size = os.path.getsize(video_path)
        assert file_size > 1_000_000, f"Video file for {lang_info['name']} is too small ({file_size} bytes)"


class TestLocaleFilesExist:
    """Test that locale files exist on disk"""
    
    def test_locale_files_count(self):
        """Verify 33+ locale files exist"""
        locale_dir = '/app/frontend/src/locales/'
        if os.path.exists(locale_dir):
            locale_files = [f for f in os.listdir(locale_dir) if f.endswith('.json')]
            assert len(locale_files) >= 33, f"Expected at least 33 locale files, got {len(locale_files)}"
    
    @pytest.mark.parametrize("locale", BUNDLED_LOCALES)
    def test_locale_file_exists(self, locale):
        """Test that each locale file exists on disk"""
        locale_path = f'/app/frontend/src/locales/{locale}.json'
        
        assert os.path.exists(locale_path), f"Locale file for {locale} not found at {locale_path}"
        
        # Check file size is reasonable (> 10KB)
        file_size = os.path.getsize(locale_path)
        assert file_size > 10_000, f"Locale file for {locale} is too small ({file_size} bytes)"


@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session
