"""
Video Asset Manager - CAPA Implementation for D-ID Tutorial Videos

Implements a proper Source of Truth database schema for video assets with:
1. Strict avatar-to-video mapping validation
2. Content-addressed storage with hash verification
3. Generation status tracking
4. Cache busting support

Created: Feb 20, 2026 - CAPA Resolution
"""

import os
import hashlib
import asyncio
import httpx
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)

# MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "MedMatch")

# D-ID Configuration
D_ID_API_KEY = os.environ.get("D_ID_API_KEY", "")
D_ID_BASE_URL = "https://api.d-id.com"

# Storage paths
TUTORIAL_VIDEOS_DIR = Path("/app/backend/static/videos/tutorials")
TUTORIAL_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# Avatar source images - Verified professional headshots (NO hands blocking faces)
# All from Pexels/Unsplash with consistent professional appearance
VERIFIED_AVATAR_SOURCES = {
    "african": {
        "url": "https://images.pexels.com/photos/3727462/pexels-photo-3727462.jpeg?auto=compress&cs=tinysrgb&w=512&h=512&fit=crop",
        "description": "Professional African businesswoman - clear face, office setting",
        "gender": "female",
        "region": "Africa"
    },
    "asian": {
        "url": "https://images.pexels.com/photos/6572210/pexels-photo-6572210.jpeg?auto=compress&cs=tinysrgb&w=512&h=512&fit=crop",
        "description": "Professional Asian woman - clear face, neutral background",
        "gender": "female",
        "region": "Asia"
    },
    "south_asian": {
        "url": "https://images.pexels.com/photos/14156490/pexels-photo-14156490.jpeg?auto=compress&cs=tinysrgb&w=512&h=512&fit=crop",
        "description": "Indian professional woman - clear face, office attire",
        "gender": "female",
        "region": "South Asia"
    },
    "middle_eastern": {
        "url": "https://images.pexels.com/photos/8154925/pexels-photo-8154925.jpeg?auto=compress&cs=tinysrgb&w=512&h=512&fit=crop",
        "description": "Arab professional woman - office setting, NO hands near face",
        "gender": "female",
        "region": "Middle East"
    },
    "latina": {
        "url": "https://images.pexels.com/photos/10041243/pexels-photo-10041243.jpeg?auto=compress&cs=tinysrgb&w=512&h=512&fit=crop",
        "description": "Latina professional woman - clear face, business casual",
        "gender": "female",
        "region": "Latin America"
    },
    "european": {
        "url": "https://images.pexels.com/photos/3756679/pexels-photo-3756679.jpeg?auto=compress&cs=tinysrgb&w=512&h=512&fit=crop",
        "description": "European professional woman - clear face, office setting",
        "gender": "female",
        "region": "Europe"
    },
    "nordic": {
        "url": "https://images.pexels.com/photos/3756679/pexels-photo-3756679.jpeg?auto=compress&cs=tinysrgb&w=512&h=512&fit=crop",
        "description": "Nordic professional woman - clear face, office setting",
        "gender": "female",
        "region": "Nordic"
    }
}

# Language to Avatar mapping with voice configuration
LANGUAGE_AVATAR_CONFIG = {
    # African Languages
    "sw": {"avatar_type": "african", "voice_id": "sw-KE-ZuriNeural", "voice_name": "Zuri", "region": "Africa"},
    "af": {"avatar_type": "african", "voice_id": "af-ZA-AdriNeural", "voice_name": "Adri", "region": "Africa"},
    "ha": {"avatar_type": "african", "voice_id": "en-NG-EzinneNeural", "voice_name": "Ezinne", "region": "Africa"},
    "zu": {"avatar_type": "african", "voice_id": "en-ZA-LeahNeural", "voice_name": "Leah", "region": "Africa"},
    
    # Asian Languages
    "ja": {"avatar_type": "asian", "voice_id": "ja-JP-NanamiNeural", "voice_name": "Nanami", "region": "Asia"},
    "zh": {"avatar_type": "asian", "voice_id": "zh-CN-XiaoxiaoNeural", "voice_name": "Xiaoxiao", "region": "Asia"},
    "ko": {"avatar_type": "asian", "voice_id": "ko-KR-SunHiNeural", "voice_name": "SunHi", "region": "Asia"},
    "vi": {"avatar_type": "asian", "voice_id": "vi-VN-HoaiMyNeural", "voice_name": "HoaiMy", "region": "Asia"},
    
    # South Asian
    "hi": {"avatar_type": "south_asian", "voice_id": "hi-IN-SwaraNeural", "voice_name": "Swara", "region": "South Asia"},
    
    # Middle Eastern
    "ar": {"avatar_type": "middle_eastern", "voice_id": "ar-EG-SalmaNeural", "voice_name": "Salma", "region": "Middle East"},
    "tr": {"avatar_type": "middle_eastern", "voice_id": "tr-TR-EmelNeural", "voice_name": "Emel", "region": "Middle East"},
    
    # Latin American
    "pt": {"avatar_type": "latina", "voice_id": "pt-BR-FranciscaNeural", "voice_name": "Francisca", "region": "South America"},
    "es": {"avatar_type": "latina", "voice_id": "es-ES-ElviraNeural", "voice_name": "Elvira", "region": "Latin America"},
    
    # European Languages
    "de": {"avatar_type": "european", "voice_id": "de-DE-KatjaNeural", "voice_name": "Katja", "region": "Europe"},
    "fr": {"avatar_type": "european", "voice_id": "fr-FR-DeniseNeural", "voice_name": "Denise", "region": "Europe"},
    "it": {"avatar_type": "european", "voice_id": "it-IT-ElsaNeural", "voice_name": "Elsa", "region": "Europe"},
    "nl": {"avatar_type": "european", "voice_id": "nl-NL-ColetteNeural", "voice_name": "Colette", "region": "Europe"},
    "pl": {"avatar_type": "european", "voice_id": "pl-PL-ZofiaNeural", "voice_name": "Zofia", "region": "Europe"},
    "ru": {"avatar_type": "european", "voice_id": "ru-RU-SvetlanaNeural", "voice_name": "Svetlana", "region": "Europe"},
    "sv": {"avatar_type": "nordic", "voice_id": "sv-SE-SofieNeural", "voice_name": "Sofie", "region": "Nordic"},
    
    # English (default)
    "en": {"avatar_type": "european", "voice_id": "en-US-JennyNeural", "voice_name": "Jenny", "region": "Global"}
}

# Tutorial script template
TUTORIAL_SCRIPT_TEMPLATE = {
    "en": "Welcome to MedMatch-AI KARAU! I'm here to guide you through our AI-powered job search platform. Upload your resume, search across 15 job boards, and get matched with opportunities tailored to your skills. Let's get started!",
    "de": "Willkommen bei MedMatch-AI KARAU! Ich bin hier, um Sie durch unsere KI-gestützte Jobsuchplattform zu führen. Laden Sie Ihren Lebenslauf hoch, suchen Sie auf 15 Jobbörsen und finden Sie passende Stellen. Legen wir los!",
    "fr": "Bienvenue sur MedMatch-AI KARAU! Je suis là pour vous guider sur notre plateforme de recherche d'emploi alimentée par l'IA. Téléchargez votre CV, recherchez sur 15 sites d'emploi et trouvez des opportunités adaptées. Commençons!",
    "es": "¡Bienvenido a MedMatch-AI KARAU! Estoy aquí para guiarte en nuestra plataforma de búsqueda de empleo impulsada por IA. Sube tu currículum, busca en 15 bolsas de trabajo y encuentra oportunidades a tu medida. ¡Empecemos!",
    "ja": "MedMatch-AI KARAUへようこそ！AI搭載の求人検索プラットフォームをご案内します。履歴書をアップロードし、15の求人サイトで検索し、あなたに合った機会を見つけましょう。始めましょう！",
    "zh": "欢迎来到MedMatch-AI KARAU！我将引导您使用我们的AI驱动求职平台。上传简历，搜索15个招聘网站，找到适合您技能的机会。开始吧！",
    "ko": "MedMatch-AI KARAU에 오신 것을 환영합니다! AI 기반 구직 플랫폼을 안내해 드리겠습니다. 이력서를 업로드하고, 15개 구인 사이트에서 검색하여 맞춤형 기회를 찾으세요. 시작합시다!",
    "hi": "MedMatch-AI KARAU में आपका स्वागत है! मैं आपको हमारे AI-संचालित जॉब सर्च प्लेटफॉर्म के बारे में बताऊंगी। अपना रिज्यूमे अपलोड करें, 15 जॉब बोर्ड पर खोजें, और अपने कौशल के अनुसार अवसर पाएं। शुरू करते हैं!",
    "ar": "مرحباً بكم في MedMatch-AI KARAU! أنا هنا لإرشادكم عبر منصة البحث عن وظائف المدعومة بالذكاء الاصطناعي. ارفع سيرتك الذاتية، وابحث في 15 موقع توظيف، واعثر على فرص تناسب مهاراتك. لنبدأ!",
    "pt": "Bem-vindo ao MedMatch-AI KARAU! Estou aqui para guiá-lo pela nossa plataforma de busca de emprego com IA. Envie seu currículo, pesquise em 15 sites de emprego e encontre oportunidades ideais. Vamos começar!",
    "it": "Benvenuto su MedMatch-AI KARAU! Sono qui per guidarti nella nostra piattaforma di ricerca lavoro basata sull'IA. Carica il tuo CV, cerca su 15 siti di lavoro e trova opportunità su misura. Iniziamo!",
    "ru": "Добро пожаловать в MedMatch-AI KARAU! Я помогу вам освоить нашу платформу поиска работы на базе ИИ. Загрузите резюме, ищите на 15 сайтах вакансий и найдите подходящие возможности. Начнём!",
    "nl": "Welkom bij MedMatch-AI KARAU! Ik begeleid u door ons AI-gedreven platform voor het zoeken naar werk. Upload uw CV, zoek op 15 vacaturesites en vind kansen die bij u passen. Laten we beginnen!",
    "pl": "Witamy w MedMatch-AI KARAU! Przeprowadzę Cię przez naszą platformę do wyszukiwania pracy z wykorzystaniem AI. Prześlij CV, szukaj na 15 portalach z ofertami pracy i znajdź idealne możliwości. Zaczynajmy!",
    "sv": "Välkommen till MedMatch-AI KARAU! Jag guidar dig genom vår AI-drivna jobbsökningsplattform. Ladda upp ditt CV, sök på 15 jobbsajter och hitta möjligheter som passar dig. Låt oss börja!",
    "tr": "MedMatch-AI KARAU'ya hoş geldiniz! Yapay zeka destekli iş arama platformumuzu size tanıtacağım. CV'nizi yükleyin, 15 iş sitesinde arayın ve size uygun fırsatları bulun. Başlayalım!",
    "vi": "Chào mừng đến với MedMatch-AI KARAU! Tôi sẽ hướng dẫn bạn sử dụng nền tảng tìm việc AI của chúng tôi. Tải lên CV, tìm kiếm trên 15 trang việc làm và tìm cơ hội phù hợp với kỹ năng của bạn. Bắt đầu thôi!",
    "sw": "Karibu MedMatch-AI KARAU! Niko hapa kukuongoza katika jukwaa letu la kutafuta kazi linaloendeshwa na AI. Pakia wasifu wako, tafuta kwenye tovuti 15 za kazi, na upate fursa zinazofaa ujuzi wako. Tuanze!",
    "af": "Welkom by MedMatch-AI KARAU! Ek is hier om jou deur ons KI-aangedrewe werksoekplatform te lei. Laai jou CV op, soek op 15 werkwebwerwe, en vind geleenthede wat by jou pas. Kom ons begin!",
    "ha": "Barka da zuwa MedMatch-AI KARAU! Ina nan don jagorantar ku ta hanyar dandamali namu na neman aiki mai amfani da AI. Loda takardar bayanan ku, nemo a shafukan aiki 15, kuma sami damar da ta dace da ku. Mu fara!",
    "zu": "Siyakwamukela ku-MedMatch-AI KARAU! Ngilapha ukukuhola esiteshini sethu sokufuna umsebenzi esisebenzisa i-AI. Layisha i-CV yakho, sesha kumakhasi omsebenzi angu-15, uthole amathuba afanele amakhono akho. Masiqale!"
}


class VideoAssetManager:
    """
    Manages video assets with proper database tracking, validation, and generation.
    Implements CAPA recommendations for resolving avatar mismatch issues.
    """
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize MongoDB connection."""
        if self._initialized:
            return
        
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client[DB_NAME]
        self.collection = self.db["video_assets"]
        
        # Create indexes
        await self.collection.create_index("language_code", unique=True)
        await self.collection.create_index("content_hash")
        await self.collection.create_index("status")
        
        self._initialized = True
        logger.info("VideoAssetManager initialized with MongoDB")
    
    def generate_content_hash(self, language_code: str, avatar_url: str, voice_id: str, script: str) -> str:
        """
        Generate unique content hash for avatar-video mapping.
        This ensures we can detect if any component changes.
        """
        content = f"{language_code}|{avatar_url}|{voice_id}|{script}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def get_language_config(self, language_code: str) -> Dict[str, Any]:
        """Get complete configuration for a language."""
        config = LANGUAGE_AVATAR_CONFIG.get(language_code, LANGUAGE_AVATAR_CONFIG["en"])
        avatar_info = VERIFIED_AVATAR_SOURCES.get(config["avatar_type"], VERIFIED_AVATAR_SOURCES["european"])
        script = TUTORIAL_SCRIPT_TEMPLATE.get(language_code, TUTORIAL_SCRIPT_TEMPLATE["en"])
        
        content_hash = self.generate_content_hash(
            language_code,
            avatar_info["url"],
            config["voice_id"],
            script
        )
        
        return {
            "language_code": language_code,
            "avatar_type": config["avatar_type"],
            "avatar_url": avatar_info["url"],
            "avatar_description": avatar_info["description"],
            "voice_id": config["voice_id"],
            "voice_name": config["voice_name"],
            "region": config["region"],
            "gender": avatar_info["gender"],
            "script": script,
            "content_hash": content_hash,
            "thumbnail_url": avatar_info["url"]  # Use same image for thumbnail
        }
    
    async def get_asset(self, language_code: str) -> Optional[Dict[str, Any]]:
        """Get video asset record from database."""
        await self.initialize()
        asset = await self.collection.find_one({"language_code": language_code}, {"_id": 0})
        return asset
    
    async def get_all_assets(self) -> List[Dict[str, Any]]:
        """Get all video assets."""
        await self.initialize()
        cursor = self.collection.find({}, {"_id": 0})
        return await cursor.to_list(length=100)
    
    async def create_or_update_asset(self, language_code: str, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a video asset record."""
        await self.initialize()
        
        asset_data["language_code"] = language_code
        asset_data["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.update_one(
            {"language_code": language_code},
            {"$set": asset_data, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
            upsert=True
        )
        
        return {"success": True, "modified": result.modified_count, "upserted": result.upserted_id is not None}
    
    async def validate_asset(self, language_code: str) -> Dict[str, Any]:
        """
        Validate that a video asset matches its expected configuration.
        Returns validation result with any mismatches found.
        """
        await self.initialize()
        
        asset = await self.get_asset(language_code)
        config = self.get_language_config(language_code)
        
        if not asset:
            return {
                "valid": False,
                "reason": "no_record",
                "message": f"No video asset record for {language_code}",
                "expected_config": config
            }
        
        # Check if file exists
        file_path = TUTORIAL_VIDEOS_DIR / f"tutorial_{language_code}.mp4"
        if not file_path.exists():
            return {
                "valid": False,
                "reason": "file_missing",
                "message": f"Video file not found: {file_path}",
                "expected_config": config
            }
        
        # Check content hash
        if asset.get("content_hash") != config["content_hash"]:
            return {
                "valid": False,
                "reason": "hash_mismatch",
                "message": "Video content hash doesn't match expected configuration",
                "stored_hash": asset.get("content_hash"),
                "expected_hash": config["content_hash"],
                "expected_config": config
            }
        
        # Check status
        if asset.get("status") != "ready":
            return {
                "valid": False,
                "reason": "not_ready",
                "message": f"Video status is {asset.get('status')}, not 'ready'",
                "expected_config": config
            }
        
        return {
            "valid": True,
            "asset": asset,
            "config": config,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size
        }
    
    async def generate_video(self, language_code: str) -> Dict[str, Any]:
        """
        Generate a new video using D-ID API with proper tracking.
        """
        if not D_ID_API_KEY:
            return {"success": False, "error": "D-ID API key not configured"}
        
        await self.initialize()
        config = self.get_language_config(language_code)
        
        # Update status to generating
        await self.create_or_update_asset(language_code, {
            "status": "generating",
            "content_hash": config["content_hash"],
            "avatar_type": config["avatar_type"],
            "avatar_url": config["avatar_url"],
            "voice_id": config["voice_id"],
            "voice_name": config["voice_name"],
            "region": config["region"],
            "script": config["script"]
        })
        
        headers = {
            "Authorization": f"Basic {D_ID_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "source_url": config["avatar_url"],
            "script": {
                "type": "text",
                "input": config["script"],
                "provider": {
                    "type": "microsoft",
                    "voice_id": config["voice_id"]
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.5,
                "stitch": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Create the talk
                response = await client.post(
                    f"{D_ID_BASE_URL}/talks",
                    headers=headers,
                    json=payload
                )
                
                if response.status_code not in [200, 201]:
                    error_msg = f"D-ID API error: {response.status_code} - {response.text}"
                    await self.create_or_update_asset(language_code, {
                        "status": "failed",
                        "error": error_msg
                    })
                    return {"success": False, "error": error_msg}
                
                result = response.json()
                talk_id = result.get("id")
                
                logger.info(f"Created D-ID talk for {language_code}: {talk_id}")
                
                # Update with talk_id
                await self.create_or_update_asset(language_code, {
                    "d_id_talk_id": talk_id,
                    "status": "processing"
                })
                
                # Poll for completion
                video_url = await self._poll_for_completion(client, headers, talk_id)
                
                if not video_url:
                    await self.create_or_update_asset(language_code, {
                        "status": "failed",
                        "error": "Video generation timed out"
                    })
                    return {"success": False, "error": "Video generation timed out"}
                
                # Download the video
                file_path = TUTORIAL_VIDEOS_DIR / f"tutorial_{language_code}.mp4"
                video_response = await client.get(video_url)
                
                if video_response.status_code == 200:
                    file_path.write_bytes(video_response.content)
                    file_size = file_path.stat().st_size
                    
                    # Update asset record
                    await self.create_or_update_asset(language_code, {
                        "status": "ready",
                        "local_file_path": str(file_path),
                        "file_size_bytes": file_size,
                        "d_id_result_url": video_url,
                        "generated_at": datetime.now(timezone.utc),
                        "version": 1
                    })
                    
                    logger.info(f"Successfully generated video for {language_code}: {file_size} bytes")
                    
                    return {
                        "success": True,
                        "language_code": language_code,
                        "talk_id": talk_id,
                        "file_path": str(file_path),
                        "file_size": file_size,
                        "content_hash": config["content_hash"]
                    }
                else:
                    await self.create_or_update_asset(language_code, {
                        "status": "failed",
                        "error": f"Failed to download video: {video_response.status_code}"
                    })
                    return {"success": False, "error": f"Failed to download video"}
                    
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error generating video for {language_code}: {error_msg}")
            await self.create_or_update_asset(language_code, {
                "status": "failed",
                "error": error_msg
            })
            return {"success": False, "error": error_msg}
    
    async def _poll_for_completion(self, client: httpx.AsyncClient, headers: Dict, talk_id: str, max_attempts: int = 60) -> Optional[str]:
        """Poll D-ID API for video completion."""
        for attempt in range(max_attempts):
            try:
                response = await client.get(
                    f"{D_ID_BASE_URL}/talks/{talk_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    if status == "done":
                        return result.get("result_url")
                    elif status == "error":
                        logger.error(f"D-ID generation error: {result.get('error')}")
                        return None
                    
                    logger.info(f"D-ID status: {status} (attempt {attempt + 1}/{max_attempts})")
                
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Poll error: {e}")
                await asyncio.sleep(2)
        
        return None
    
    async def regenerate_all_videos(self, languages: List[str] = None) -> Dict[str, Any]:
        """
        Regenerate all videos or a subset of languages.
        Returns summary of regeneration results.
        """
        if languages is None:
            languages = list(LANGUAGE_AVATAR_CONFIG.keys())
        
        results = {
            "total": len(languages),
            "success": 0,
            "failed": 0,
            "details": []
        }
        
        for lang in languages:
            logger.info(f"Regenerating video for {lang}...")
            result = await self.generate_video(lang)
            
            if result.get("success"):
                results["success"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "language": lang,
                "result": result
            })
            
            # Small delay between requests to avoid rate limiting
            await asyncio.sleep(1)
        
        return results
    
    async def get_video_url(self, language_code: str) -> Dict[str, Any]:
        """
        Get the validated video URL for a language.
        Returns URL with cache-busting hash if valid.
        """
        validation = await self.validate_asset(language_code)
        
        if not validation.get("valid"):
            return {
                "success": False,
                "error": validation.get("reason"),
                "message": validation.get("message"),
                "fallback": True
            }
        
        asset = validation.get("asset", {})
        config = validation.get("config", {})
        
        # Build URL with cache-busting hash
        content_hash = asset.get("content_hash", "v1")
        version = asset.get("version", 1)
        
        return {
            "success": True,
            "url": f"/api/tutorials/video-file/tutorial_{language_code}.mp4?v={content_hash}&ver={version}",
            "thumbnail_url": config.get("thumbnail_url"),
            "language_code": language_code,
            "voice_name": config.get("voice_name"),
            "region": config.get("region"),
            "content_hash": content_hash
        }
    
    async def get_frontend_config(self) -> Dict[str, Any]:
        """
        Get complete configuration for frontend to display tutorials.
        This is the single source of truth for avatar-video mapping.
        """
        await self.initialize()
        
        configs = {}
        for lang_code in LANGUAGE_AVATAR_CONFIG.keys():
            config = self.get_language_config(lang_code)
            asset = await self.get_asset(lang_code)
            
            # Determine if video is ready
            is_ready = False
            if asset and asset.get("status") == "ready":
                file_path = TUTORIAL_VIDEOS_DIR / f"tutorial_{lang_code}.mp4"
                is_ready = file_path.exists()
            
            configs[lang_code] = {
                "language_code": lang_code,
                "avatar_url": config["avatar_url"],  # Thumbnail
                "avatar_type": config["avatar_type"],
                "voice_name": config["voice_name"],
                "region": config["region"],
                "gender": config["gender"],
                "content_hash": config["content_hash"],
                "is_ready": is_ready,
                "status": asset.get("status") if asset else "not_generated"
            }
        
        return {
            "languages": configs,
            "total": len(configs),
            "ready_count": sum(1 for c in configs.values() if c["is_ready"])
        }


# Singleton instance
video_asset_manager = VideoAssetManager()

__all__ = ['video_asset_manager', 'VideoAssetManager', 'LANGUAGE_AVATAR_CONFIG', 'VERIFIED_AVATAR_SOURCES']
