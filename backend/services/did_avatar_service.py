"""
D-ID AI Avatar Video Generation Service

Creates AI-powered talking head videos using D-ID's API.
Supports multiple presenters, voices, and backgrounds.
Updated Feb 11, 2026: Region-appropriate avatars and voice matching
"""

import os
import httpx
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import base64

logger = logging.getLogger(__name__)

# D-ID API Configuration
D_ID_API_KEY = os.environ.get("D_ID_API_KEY", "")
D_ID_BASE_URL = "https://api.d-id.com"

# Video storage
AVATAR_VIDEOS_DIR = Path("/app/videos/avatars")
AVATAR_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Region-appropriate avatar source images
# Using diverse stock photos that match regions and maintain consistent female presentation
AVATAR_IMAGES = {
    # European avatars (light skin, professional appearance)
    "european_female": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=512&h=512&fit=crop",
    "nordic_female": "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=512&h=512&fit=crop",
    
    # Asian avatars
    "asian_female": "https://images.unsplash.com/photo-1594744803329-e58b31de8bf5?w=512&h=512&fit=crop",
    "south_asian_female": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=512&h=512&fit=crop",
    
    # African avatars
    "african_female": "https://images.unsplash.com/photo-1531123897727-8f129e1688ce?w=512&h=512&fit=crop",
    
    # Middle Eastern avatars  
    "middle_eastern_female": "https://images.unsplash.com/photo-1598550874175-4d0ef436c909?w=512&h=512&fit=crop",
    
    # Latina avatars
    "latina_female": "https://images.unsplash.com/photo-1573497019418-b400bb3ab074?w=512&h=512&fit=crop",
    
    # Default MedMatch-AI KARAU avatar
    "default": "https://customer-assets.emergentagent.com/job_hirescience/artifacts/mux577io_MedMatch-AI KARAU%20Image.jpeg"
}

# Language to Avatar and Voice mapping
# Ensures region-appropriate avatar with matching female voice
LANGUAGE_CONFIG = {
    # European Languages
    "de": {"avatar": "european_female", "voice_id": "de-DE-KatjaNeural", "voice_name": "Katja", "gender": "female", "region": "Europe"},
    "fr": {"avatar": "european_female", "voice_id": "fr-FR-DeniseNeural", "voice_name": "Denise", "gender": "female", "region": "Europe"},
    "es": {"avatar": "latina_female", "voice_id": "es-ES-ElviraNeural", "voice_name": "Elvira", "gender": "female", "region": "Europe"},
    "it": {"avatar": "european_female", "voice_id": "it-IT-ElsaNeural", "voice_name": "Elsa", "gender": "female", "region": "Europe"},
    "nl": {"avatar": "european_female", "voice_id": "nl-NL-ColetteNeural", "voice_name": "Colette", "gender": "female", "region": "Europe"},
    "pl": {"avatar": "european_female", "voice_id": "pl-PL-ZofiaNeural", "voice_name": "Zofia", "gender": "female", "region": "Europe"},
    "sv": {"avatar": "nordic_female", "voice_id": "sv-SE-SofieNeural", "voice_name": "Sofie", "gender": "female", "region": "Nordic"},
    "ru": {"avatar": "european_female", "voice_id": "ru-RU-SvetlanaNeural", "voice_name": "Svetlana", "gender": "female", "region": "Europe"},
    
    # Asian Languages
    "ja": {"avatar": "asian_female", "voice_id": "ja-JP-NanamiNeural", "voice_name": "Nanami", "gender": "female", "region": "Asia"},
    "zh": {"avatar": "asian_female", "voice_id": "zh-CN-XiaoxiaoNeural", "voice_name": "Xiaoxiao", "gender": "female", "region": "Asia"},
    "ko": {"avatar": "asian_female", "voice_id": "ko-KR-SunHiNeural", "voice_name": "SunHi", "gender": "female", "region": "Asia"},
    "vi": {"avatar": "asian_female", "voice_id": "vi-VN-HoaiMyNeural", "voice_name": "HoaiMy", "gender": "female", "region": "Asia"},
    "hi": {"avatar": "south_asian_female", "voice_id": "hi-IN-SwaraNeural", "voice_name": "Swara", "gender": "female", "region": "South Asia"},
    
    # Middle Eastern Languages
    "ar": {"avatar": "middle_eastern_female", "voice_id": "ar-EG-SalmaNeural", "voice_name": "Salma", "gender": "female", "region": "Middle East"},
    "tr": {"avatar": "middle_eastern_female", "voice_id": "tr-TR-EmelNeural", "voice_name": "Emel", "gender": "female", "region": "Middle East"},
    
    # South American
    "pt": {"avatar": "latina_female", "voice_id": "pt-BR-FranciscaNeural", "voice_name": "Francisca", "gender": "female", "region": "South America"},
    
    # African Languages
    "sw": {"avatar": "african_female", "voice_id": "sw-KE-ZuriNeural", "voice_name": "Zuri", "gender": "female", "region": "Africa"},
    "af": {"avatar": "african_female", "voice_id": "af-ZA-AdriNeural", "voice_name": "Adri", "gender": "female", "region": "Africa"},
    "zu": {"avatar": "african_female", "voice_id": "zu-ZA-ThandileNeural", "voice_name": "Thandile", "gender": "female", "region": "Africa"},
    "ha": {"avatar": "african_female", "voice_id": "en-NG-EzinneNeural", "voice_name": "Ezinne", "gender": "female", "region": "Africa"},
    
    # English variants
    "en": {"avatar": "default", "voice_id": "en-US-JennyNeural", "voice_name": "Jenny", "gender": "female", "region": "Global"},
    "en-US": {"avatar": "default", "voice_id": "en-US-JennyNeural", "voice_name": "Jenny", "gender": "female", "region": "North America"},
    "en-GB": {"avatar": "european_female", "voice_id": "en-GB-SoniaNeural", "voice_name": "Sonia", "gender": "female", "region": "UK"},
    "en-AU": {"avatar": "european_female", "voice_id": "en-AU-NatashaNeural", "voice_name": "Natasha", "gender": "female", "region": "Australia"},
    "en-NG": {"avatar": "african_female", "voice_id": "en-NG-EzinneNeural", "voice_name": "Ezinne", "gender": "female", "region": "Africa"},
    "en-KE": {"avatar": "african_female", "voice_id": "en-KE-AsiliaNeural", "voice_name": "Asilia", "gender": "female", "region": "Africa"},
}


class DIDService:
    """
    D-ID Avatar Video Generation Service.
    
    Creates AI talking head videos from:
    - Text scripts
    - Audio files
    - Custom presenter images
    """
    
    def __init__(self):
        self.api_key = D_ID_API_KEY
        self.base_url = D_ID_BASE_URL
        
        if not self.api_key:
            logger.warning("D-ID API key not configured")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers with authentication."""
        return {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def get_presenters(self) -> List[Dict]:
        """Get available D-ID presenters."""
        if not self.api_key:
            return self._get_mock_presenters()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/talks/presenters",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json().get("presenters", [])
                else:
                    logger.error(f"Failed to get presenters: {response.status_code}")
                    return self._get_mock_presenters()
        except Exception as e:
            logger.error(f"Error getting presenters: {e}")
            return self._get_mock_presenters()
    
    def _get_mock_presenters(self) -> List[Dict]:
        """Return mock presenters for development."""
        return [
            {
                "presenter_id": "amy-jcwCkr1grs",
                "name": "Amy",
                "gender": "female",
                "thumbnail": "https://d-id.com/presenters/amy.png"
            },
            {
                "presenter_id": "anna-Vcnva67YRC",
                "name": "Anna",
                "gender": "female",
                "thumbnail": "https://d-id.com/presenters/anna.png"
            },
            {
                "presenter_id": "josh-jp4VsYVnXa",
                "name": "Josh",
                "gender": "male",
                "thumbnail": "https://d-id.com/presenters/josh.png"
            }
        ]
    
    async def get_voices(self) -> List[Dict]:
        """Get available voices for text-to-speech."""
        # D-ID supports Microsoft Azure voices
        return [
            # English
            {"voice_id": "en-US-JennyNeural", "name": "Jenny", "language": "en-US", "gender": "female"},
            {"voice_id": "en-US-GuyNeural", "name": "Guy", "language": "en-US", "gender": "male"},
            {"voice_id": "en-GB-SoniaNeural", "name": "Sonia", "language": "en-GB", "gender": "female"},
            {"voice_id": "en-AU-NatashaNeural", "name": "Natasha", "language": "en-AU", "gender": "female"},
            {"voice_id": "en-KE-ChilembaNeural", "name": "Chilemba", "language": "en-KE", "gender": "male"},
            {"voice_id": "en-NG-AbeoNeural", "name": "Abeo", "language": "en-NG", "gender": "male"},
            {"voice_id": "en-NG-EzinneNeural", "name": "Ezinne", "language": "en-NG", "gender": "female"},
            # Spanish
            {"voice_id": "es-ES-ElviraNeural", "name": "Elvira", "language": "es-ES", "gender": "female"},
            {"voice_id": "es-MX-DaliaNeural", "name": "Dalia", "language": "es-MX", "gender": "female"},
            # Portuguese
            {"voice_id": "pt-BR-FranciscaNeural", "name": "Francisca", "language": "pt-BR", "gender": "female"},
            {"voice_id": "pt-BR-AntonioNeural", "name": "Antonio", "language": "pt-BR", "gender": "male"},
            {"voice_id": "pt-PT-DuarteNeural", "name": "Duarte", "language": "pt-PT", "gender": "male"},
            {"voice_id": "pt-PT-RaquelNeural", "name": "Raquel", "language": "pt-PT", "gender": "female"},
            # French
            {"voice_id": "fr-FR-DeniseNeural", "name": "Denise", "language": "fr-FR", "gender": "female"},
            # German
            {"voice_id": "de-DE-KatjaNeural", "name": "Katja", "language": "de-DE", "gender": "female"},
            # Japanese
            {"voice_id": "ja-JP-NanamiNeural", "name": "Nanami", "language": "ja-JP", "gender": "female"},
            # Chinese
            {"voice_id": "zh-CN-XiaoxiaoNeural", "name": "Xiaoxiao", "language": "zh-CN", "gender": "female"},
            # Arabic
            {"voice_id": "ar-SA-ZariyahNeural", "name": "Zariyah", "language": "ar-SA", "gender": "female"},
            # Hindi
            {"voice_id": "hi-IN-SwaraNeural", "name": "Swara", "language": "hi-IN", "gender": "female"},
            # African Languages
            {"voice_id": "sw-KE-ZuriNeural", "name": "Zuri", "language": "sw-KE", "gender": "female"},
            {"voice_id": "sw-KE-RafikiNeural", "name": "Rafiki", "language": "sw-KE", "gender": "male"},
            {"voice_id": "sw-TZ-RehemaNeural", "name": "Rehema", "language": "sw-TZ", "gender": "female"},
            {"voice_id": "sw-TZ-DaudiNeural", "name": "Daudi", "language": "sw-TZ", "gender": "male"},
            {"voice_id": "af-ZA-AdriNeural", "name": "Adri", "language": "af-ZA", "gender": "female"},
            {"voice_id": "af-ZA-WillemNeural", "name": "Willem", "language": "af-ZA", "gender": "male"},
            # Multilingual (41+ languages)
            {"voice_id": "en-US-JennyMultilingualNeural", "name": "Jenny Multilingual", "language": "multilingual", "gender": "female"},
        ]
    
    async def create_talk_video(
        self,
        script: str,
        presenter_id: Optional[str] = None,
        voice_id: str = "en-US-JennyNeural",
        background_color: str = "#1a1a2e",
        title: str = "MedMatch-AI KARAU Video",
        source_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a talking head video from text script.
        
        Args:
            script: The text script for the avatar to speak
            presenter_id: D-ID presenter ID (optional, uses default if not provided)
            voice_id: Microsoft Azure voice ID
            background_color: Background color hex code
            title: Video title for storage
            source_url: Custom image URL for the avatar presenter
        
        Returns:
            Video creation result with URL or status
        """
        if not self.api_key:
            return self._create_mock_video(script, title)
        
        # Default MedMatch-AI KARAU presenter image
        default_source = "https://customer-assets.emergentagent.com/job_hirescience/artifacts/mux577io_MedMatch-AI KARAU%20Image.jpeg"
        
        # Prepare the request payload
        payload = {
            "source_url": source_url or default_source,
            "script": {
                "type": "text",
                "input": script,
                "provider": {
                    "type": "microsoft",
                    "voice_id": voice_id
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.5,
                "stitch": True
            }
        }
        
        # Add presenter if specified (overrides source_url)
        if presenter_id:
            del payload["source_url"]
            payload["presenter_id"] = presenter_id
        
        try:
            async with httpx.AsyncClient() as client:
                # Create the talk
                response = await client.post(
                    f"{self.base_url}/talks",
                    headers=self._get_headers(),
                    json=payload,
                    timeout=60.0
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    talk_id = result.get("id")
                    
                    logger.info(f"Talk created: {talk_id}")
                    
                    # Poll for completion
                    video_url = await self._poll_for_completion(talk_id)
                    
                    return {
                        "success": True,
                        "talk_id": talk_id,
                        "video_url": video_url,
                        "title": title,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_detail = response.text
                    logger.error(f"Failed to create talk: {response.status_code} - {error_detail}")
                    return {
                        "success": False,
                        "error": f"API Error: {response.status_code}",
                        "detail": error_detail
                    }
        
        except Exception as e:
            logger.error(f"Error creating talk video: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _poll_for_completion(self, talk_id: str, max_attempts: int = 60) -> Optional[str]:
        """Poll for video completion."""
        async with httpx.AsyncClient() as client:
            for attempt in range(max_attempts):
                try:
                    response = await client.get(
                        f"{self.base_url}/talks/{talk_id}",
                        headers=self._get_headers(),
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        status = result.get("status")
                        
                        if status == "done":
                            return result.get("result_url")
                        elif status == "error":
                            logger.error(f"Talk failed: {result.get('error')}")
                            return None
                        
                        logger.info(f"Talk status: {status} (attempt {attempt + 1})")
                    
                    await asyncio.sleep(2)  # Wait 2 seconds between polls
                    
                except Exception as e:
                    logger.error(f"Poll error: {e}")
                    await asyncio.sleep(2)
        
        return None
    
    def _create_mock_video(self, script: str, title: str) -> Dict[str, Any]:
        """Create a mock video response for development."""
        mock_id = f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save script to file for reference
        script_file = AVATAR_VIDEOS_DIR / f"{mock_id}_script.txt"
        script_file.write_text(script)
        
        return {
            "success": True,
            "mock": True,
            "talk_id": mock_id,
            "video_url": f"/videos/avatars/{mock_id}_mock.mp4",
            "script_saved": str(script_file),
            "title": title,
            "message": "D-ID API key not configured. Script saved for later processing.",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def create_medmatch_overview(self, duration: str = "60s") -> Dict[str, Any]:
        """Create a MedMatch-AI KARAU overview video with predefined script."""
        scripts = {
            "60s": """Finding your dream job in life sciences just got smarter. Meet MedMatch-AI KARAU.
            
Upload your resume — our AI instantly matches you with jobs from 15+ specialized boards. 
No more ghost jobs. No more endless scrolling. 
Get a Trust Score for every match, prep for interviews with AI coaching, and receive alerts for jobs near you.

Recruiters — track candidates through our ATS, use blind screening to eliminate bias, and stay compliant with built-in EU AI Act monitoring. Every decision is logged and auditable.

Available in 25 languages. Web, iOS, Android, and Desktop. Enterprise-ready with GDPR compliance and crypto-shredding for data protection.

MedMatch-AI KARAU — Intelligent hiring for life sciences. Start free today.""",
            
            "30s": """Job hunting in life sciences? MedMatch-AI KARAU's Dragon AI searches 15+ job boards and filters out ghost jobs — instantly.

Upload your resume, get matched with verified positions, and prep for interviews with AI coaching. Available in 25 languages.

MedMatch-AI KARAU — Where life science careers meet AI. Try it free.""",
            
            "15s": """Still applying to ghost jobs? MedMatch-AI KARAU's AI filters out fake listings and matches you with REAL opportunities in pharma, biotech, and medical devices. Link in bio. You're welcome."""
        }
        
        script = scripts.get(duration, scripts["60s"])
        
        return await self.create_talk_video(
            script=script,
            voice_id="en-US-JennyNeural",
            background_color="#1a1a2e",
            title=f"MedMatch-AI KARAU Overview ({duration})"
        )
    
    def get_language_config(self, language_code: str) -> Dict[str, Any]:
        """
        Get the avatar and voice configuration for a specific language.
        
        Args:
            language_code: ISO language code (e.g., 'de', 'fr', 'sw')
        
        Returns:
            Configuration dict with avatar URL and voice settings
        """
        config = LANGUAGE_CONFIG.get(language_code, LANGUAGE_CONFIG.get("en"))
        avatar_key = config["avatar"]
        
        return {
            "language": language_code,
            "avatar_url": AVATAR_IMAGES.get(avatar_key, AVATAR_IMAGES["default"]),
            "avatar_type": avatar_key,
            "voice_id": config["voice_id"],
            "voice_name": config["voice_name"],
            "gender": config["gender"],
            "region": config["region"]
        }
    
    async def create_tutorial_video(
        self,
        language_code: str,
        script: str,
        title: str = None
    ) -> Dict[str, Any]:
        """
        Create a tutorial video with region-appropriate avatar and voice.
        
        Args:
            language_code: ISO language code (e.g., 'de', 'fr', 'sw')
            script: The tutorial script in the specified language
            title: Optional video title
        
        Returns:
            Video creation result with URL or status
        """
        # Get language-specific configuration
        lang_config = self.get_language_config(language_code)
        
        logger.info(f"Creating tutorial for {language_code}: avatar={lang_config['avatar_type']}, voice={lang_config['voice_name']}")
        
        return await self.create_talk_video(
            script=script,
            voice_id=lang_config["voice_id"],
            source_url=lang_config["avatar_url"],
            background_color="#1a1a2e",
            title=title or f"MedMatch-AI KARAU Tutorial ({language_code})"
        )
    
    def get_all_language_configs(self) -> Dict[str, Dict]:
        """Get all available language configurations."""
        return {
            code: self.get_language_config(code)
            for code in LANGUAGE_CONFIG.keys()
        }
    
    async def get_credits(self) -> Dict[str, Any]:
        """Check D-ID API credits/usage."""
        if not self.api_key:
            return {"mock": True, "credits": "unlimited (mock mode)"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/credits",
                    headers=self._get_headers(),
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Failed to get credits: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}


# Initialize service
did_service = DIDService()

__all__ = ['did_service', 'DIDService']
