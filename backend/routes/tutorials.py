"""
Video Tutorials API Routes
Serves instructional videos for MedMatch-AI KARAU navigation
Updated: Feb 21, 2026 - Added free edge-tts audio generation
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List, Dict
import os
from services.did_avatar_service import DIDService
from services.edge_tts_service import generate_tutorial_audio, get_supported_languages

# Initialize DID service
did_service = DIDService()

router = APIRouter(prefix="/tutorials", tags=["Tutorials"])

VIDEOS_DIR = Path("/app/videos")
TUTORIAL_VIDEOS_DIR = Path("/app/backend/static/videos/tutorials")

# Video metadata - Updated with diverse presenters
VIDEOS = [
    {
        "id": "01_jobseeker_features",
        "title": "Job Seeker Features",
        "description": "Complete guide to dashboard, job search, resume, applications, and interview prep",
        "duration": "40 seconds",
        "category": "job_seeker",
        "filename": "01_jobseeker_features.mp4",
        "presenter": "Professional woman"
    },
    {
        "id": "02_recruiter_features",
        "title": "Recruiter Features",
        "description": "Dashboard, applicant tracking, job postings, and hiring tools",
        "duration": "28 seconds",
        "category": "recruiter",
        "filename": "02_recruiter_features.mp4",
        "presenter": "Pacific Islander woman"
    },
    {
        "id": "03_privacy_matters",
        "title": "Your Privacy Matters",
        "description": "How we protect your data and keep your job search secure",
        "duration": "34 seconds",
        "category": "general",
        "filename": "03_privacy_matters.mp4",
        "presenter": "Asian professional"
    },
    {
        "id": "04_faq_ai_compliance",
        "title": "FAQs: AI Compliance & Data Rights",
        "description": "Understanding AI usage, data ownership, GDPR compliance, and your rights",
        "duration": "52 seconds",
        "category": "general",
        "filename": "04_faq_ai_compliance.mp4",
        "presenter": "Native American woman"
    },
    {
        "id": "05_complete_overview",
        "title": "Complete MedMatch-AI KARAU Overview",
        "description": "AI-powered comprehensive overview of all MedMatch-AI KARAU features for job seekers and recruiters",
        "duration": "60 seconds",
        "category": "overview",
        "filename": "05_complete_overview.mp4",
        "presenter": "AI Avatar (D-ID)",
        "ai_generated": True,
        "voice": "Jenny (en-US)",
        "language": "en"
    }
]

# Multi-language overview videos (AI Avatar generated)
MULTILANG_VIDEOS = {
    "es": {
        "id": "overview_spanish",
        "title": "Descripción General de MedMatch-AI KARAU",
        "description": "Visión completa impulsada por IA de todas las funciones de MedMatch-AI KARAU",
        "duration": "60 seconds",
        "voice": "Elvira (es-ES)",
        "language": "es"
    },
    "fr": {
        "id": "overview_french",
        "title": "Présentation de MedMatch-AI KARAU",
        "description": "Aperçu complet alimenté par l'IA de toutes les fonctionnalités MedMatch-AI KARAU",
        "duration": "60 seconds",
        "voice": "Denise (fr-FR)",
        "language": "fr"
    },
    "de": {
        "id": "overview_german",
        "title": "MedMatch-AI KARAU Übersicht",
        "description": "KI-gestützte umfassende Übersicht aller MedMatch-AI KARAU-Funktionen",
        "duration": "60 seconds",
        "voice": "Katja (de-DE)",
        "language": "de"
    },
    "ja": {
        "id": "overview_japanese",
        "title": "MedMatch-AI KARAU 概要",
        "description": "AIによるMedMatch-AI KARAU全機能の包括的な概要",
        "duration": "60 seconds",
        "voice": "Nanami (ja-JP)",
        "language": "ja"
    },
    "zh": {
        "id": "overview_chinese",
        "title": "MedMatch-AI KARAU 概述",
        "description": "AI驱动的MedMatch-AI KARAU全功能综合概述",
        "duration": "60 seconds",
        "voice": "Xiaoxiao (zh-CN)",
        "language": "zh"
    },
    # African Languages
    "sw": {
        "id": "overview_swahili",
        "title": "Muhtasari wa MedMatch-AI KARAU",
        "description": "Muhtasari kamili wa MedMatch-AI KARAU unaoendelea na AI kwa watafutaji wa kazi na waajiri",
        "duration": "60 seconds",
        "voice": "Zuri (sw-KE)",
        "language": "sw",
        "talk_id": "tlk_7LhG-0hhG3ynEd2KxohrN"
    },
    "af": {
        "id": "overview_afrikaans",
        "title": "MedMatch-AI KARAU Oorsig",
        "description": "KI-aangedrewe omvattende oorsig van alle MedMatch-AI KARAU-funksies",
        "duration": "60 seconds",
        "voice": "Adri (af-ZA)",
        "language": "af",
        "talk_id": "tlk_jKq2BCNU1NiVypyd2xJS4"
    },
    "en-NG": {
        "id": "overview_english_nigeria",
        "title": "MedMatch-AI KARAU Overview (Nigerian English)",
        "description": "AI-powered comprehensive overview with Nigerian English accent",
        "duration": "60 seconds",
        "voice": "Ezinne (en-NG)",
        "language": "en-NG",
        "talk_id": "tlk_hq9691jXrjYhwEOv35sV2"
    }
}

# Getting Started Tutorial Videos (45s each) - All Languages with D-ID Talk IDs
TUTORIAL_VIDEOS = {
    "de": {
        "id": "tutorial_german",
        "title": "Erste Schritte mit MedMatch-AI KARAU",
        "description": "Lernen Sie in wenigen Minuten, wie Sie MedMatch-AI KARAU nutzen können",
        "duration": "45 seconds",
        "voice": "Katja (de-DE)",
        "language": "de",
        "talk_id": "tlk_U_WgYRHRZvTazt9trvZpg"
    },
    "fr": {
        "id": "tutorial_french",
        "title": "Démarrer avec MedMatch-AI KARAU",
        "description": "Apprenez à utiliser MedMatch-AI KARAU en quelques minutes",
        "duration": "45 seconds",
        "voice": "Denise (fr-FR)",
        "language": "fr",
        "talk_id": "tlk_X0fd9qzrvTlsqBWynmMe6"
    },
    "es": {
        "id": "tutorial_spanish",
        "title": "Comenzar con MedMatch-AI KARAU",
        "description": "Aprende a usar MedMatch-AI KARAU en pocos minutos",
        "duration": "45 seconds",
        "voice": "Elvira (es-ES)",
        "language": "es",
        "talk_id": "tlk_h4r6Fu-x5cHidSGm1xr_J"
    },
    "ja": {
        "id": "tutorial_japanese",
        "title": "MedMatch-AI KARAUの使い方",
        "description": "数分でMedMatch-AI KARAUの使い方を学びましょう",
        "duration": "45 seconds",
        "voice": "Nanami (ja-JP)",
        "language": "ja",
        "talk_id": "tlk_8q1WRtDgr1xmiBqucb1nR"
    },
    "zh": {
        "id": "tutorial_chinese",
        "title": "MedMatch-AI KARAU入门指南",
        "description": "几分钟内学会如何使用MedMatch-AI KARAU",
        "duration": "45 seconds",
        "voice": "Xiaoxiao (zh-CN)",
        "language": "zh",
        "talk_id": "tlk_uJmYXojHb0OsKyEEq-KrZ"
    },
    "pt": {
        "id": "tutorial_portuguese",
        "title": "Começando com MedMatch-AI KARAU",
        "description": "Aprenda a usar o MedMatch-AI KARAU em poucos minutos",
        "duration": "45 seconds",
        "voice": "Francisca (pt-BR)",
        "language": "pt",
        "talk_id": "tlk_Lyp35W6ADuqPC23v43DpV"
    },
    "ar": {
        "id": "tutorial_arabic",
        "title": "البدء مع MedMatch-AI KARAU",
        "description": "تعلم كيفية استخدام MedMatch-AI KARAU في دقائق",
        "duration": "45 seconds",
        "voice": "Salma (ar-EG)",
        "language": "ar",
        "talk_id": "tlk_64wv6WIrs1z5JG-NiRo6c"
    },
    "ko": {
        "id": "tutorial_korean",
        "title": "MedMatch-AI KARAU 시작하기",
        "description": "몇 분 안에 MedMatch-AI KARAU 사용법을 배우세요",
        "duration": "45 seconds",
        "voice": "SunHi (ko-KR)",
        "language": "ko",
        "talk_id": "tlk_BqThujQ3B-8YX92KjkYf7"
    },
    "hi": {
        "id": "tutorial_hindi",
        "title": "MedMatch-AI KARAU के साथ शुरुआत",
        "description": "कुछ ही मिनटों में MedMatch-AI KARAU का उपयोग करना सीखें",
        "duration": "45 seconds",
        "voice": "Swara (hi-IN)",
        "language": "hi",
        "talk_id": "tlk_vXxJt9acDRpN4LhZBkJJ7"
    },
    "it": {
        "id": "tutorial_italian",
        "title": "Iniziare con MedMatch-AI KARAU",
        "description": "Impara a usare MedMatch-AI KARAU in pochi minuti",
        "duration": "45 seconds",
        "voice": "Elsa (it-IT)",
        "language": "it",
        "talk_id": "tlk__jTrzZfoNjpnPZ9R1feFS"
    },
    "ru": {
        "id": "tutorial_russian",
        "title": "Начало работы с MedMatch-AI KARAU",
        "description": "Узнайте, как использовать MedMatch-AI KARAU за несколько минут",
        "duration": "45 seconds",
        "voice": "Svetlana (ru-RU)",
        "language": "ru",
        "talk_id": "tlk_0G_ntBt-SX1Iz15Jc232W"
    },
    "nl": {
        "id": "tutorial_dutch",
        "title": "Aan de slag met MedMatch-AI KARAU",
        "description": "Leer in een paar minuten hoe je MedMatch-AI KARAU kunt gebruiken",
        "duration": "45 seconds",
        "voice": "Colette (nl-NL)",
        "language": "nl",
        "talk_id": "tlk_L-sAolNvFfXWpfQsUtgW3"
    },
    "pl": {
        "id": "tutorial_polish",
        "title": "Rozpocznij z MedMatch-AI KARAU",
        "description": "Naucz się korzystać z MedMatch-AI KARAU w kilka minut",
        "duration": "45 seconds",
        "voice": "Zofia (pl-PL)",
        "language": "pl",
        "talk_id": "tlk_ikCuJjKUqU8JQ4ZVCV60e"
    },
    "sv": {
        "id": "tutorial_swedish",
        "title": "Kom igång med MedMatch-AI KARAU",
        "description": "Lär dig använda MedMatch-AI KARAU på några minuter",
        "duration": "45 seconds",
        "voice": "Sofie (sv-SE)",
        "language": "sv",
        "talk_id": "tlk_AjGkGAAH-1-xv_7CX6dob"
    },
    "tr": {
        "id": "tutorial_turkish",
        "title": "MedMatch-AI KARAU'e Başlayın",
        "description": "MedMatch-AI KARAU'i birkaç dakikada kullanmayı öğrenin",
        "duration": "45 seconds",
        "voice": "Emel (tr-TR)",
        "language": "tr",
        "talk_id": "tlk_IYsGbvTgkp2UKbpfrPhxx"
    },
    "vi": {
        "id": "tutorial_vietnamese",
        "title": "Bắt đầu với MedMatch-AI KARAU",
        "description": "Học cách sử dụng MedMatch-AI KARAU trong vài phút",
        "duration": "45 seconds",
        "voice": "HoaiMy (vi-VN)",
        "language": "vi",
        "talk_id": "tlk_aacDqHBufCqnl5ICyXO8J"
    },
    # African Languages - Added Feb 18, 2026
    "sw": {
        "id": "tutorial_swahili",
        "title": "Kuanza na MedMatch-AI KARAU",
        "description": "Jifunze kutumia MedMatch-AI KARAU kwa dakika chache",
        "duration": "45 seconds",
        "voice": "Zuri (sw-KE)",
        "language": "sw"
    },
    "af": {
        "id": "tutorial_afrikaans",
        "title": "Begin met MedMatch-AI KARAU",
        "description": "Leer hoe om MedMatch-AI KARAU binne minute te gebruik",
        "duration": "45 seconds",
        "voice": "Adri (af-ZA)",
        "language": "af"
    },
    "ha": {
        "id": "tutorial_hausa",
        "title": "Fara da MedMatch-AI KARAU",
        "description": "Koyi yadda ake amfani da MedMatch-AI KARAU cikin mintuna",
        "duration": "45 seconds",
        "voice": "Ezinne (en-NG)",
        "language": "ha"
    },
    "zu": {
        "id": "tutorial_zulu",
        "title": "Qala nge-MedMatch-AI KARAU",
        "description": "Funda ukusebenzisa i-MedMatch-AI KARAU ngomzuzu nje",
        "duration": "45 seconds",
        "voice": "Thandile (zu-ZA)",
        "language": "zu"
    }
}

# Role-specific videos
ROLE_VIDEOS = {
    "jobseeker_overview": {
        "id": "jobseeker_overview_30s",
        "title": "Job Seeker Quick Start",
        "description": "30-second guide for job seekers using MedMatch-AI KARAU",
        "duration": "30 seconds",
        "voice": "Jenny (en-US)",
        "target_audience": "jobseeker"
    },
    "recruiter_overview": {
        "id": "recruiter_overview_30s",
        "title": "Recruiter Quick Start",
        "description": "30-second guide for recruiters using MedMatch-AI KARAU",
        "duration": "30 seconds",
        "voice": "Jenny (en-US)",
        "target_audience": "recruiter"
    }
}


@router.get("/videos")
async def list_videos(category: str = None, lang: str = None):
    """List all available tutorial videos, optionally filtered by category or language"""
    videos = VIDEOS.copy()
    
    if category:
        videos = [v for v in videos if v["category"] == category]
    
    # Add URL to each video
    for video in videos:
        video["url"] = f"/api/tutorials/videos/{video['id']}"
        video["exists"] = (VIDEOS_DIR / video["filename"]).exists()
    
    # Include multi-language videos info
    multilang_info = {
        "available_languages": list(MULTILANG_VIDEOS.keys()),
        "role_specific": list(ROLE_VIDEOS.keys())
    }
    
    return {
        "videos": videos,
        "count": len(videos),
        "multilang": multilang_info
    }


@router.get("/videos/multilang")
async def get_multilang_videos():
    """Get all available multi-language overview videos"""
    return {
        "languages": MULTILANG_VIDEOS,
        "tutorials": TUTORIAL_VIDEOS,
        "role_specific": ROLE_VIDEOS,
        "default_language": "en"
    }


@router.get("/videos/tutorials")
async def get_tutorial_videos():
    """Get all Getting Started tutorial videos (45s each)"""
    return {
        "tutorials": TUTORIAL_VIDEOS,
        "total_languages": len(TUTORIAL_VIDEOS),
        "duration": "45 seconds each",
        "note": "AI Avatar videos generated via D-ID API. Use talk_id to fetch video URL."
    }


@router.get("/language-configs")
async def get_language_configurations():
    """
    Get avatar and voice configurations for all supported languages.
    Returns region-appropriate avatar images and matching female voices.
    """
    from services.did_avatar_service import did_service
    
    configs = did_service.get_all_language_configs()
    
    return {
        "languages": configs,
        "total": len(configs),
        "note": "All avatars use region-appropriate images with matching female voices"
    }


@router.get("/language-config/{language}")
async def get_language_config(language: str):
    """Get avatar and voice configuration for a specific language."""
    from services.did_avatar_service import did_service
    
    config = did_service.get_language_config(language)
    
    if not config:
        raise HTTPException(status_code=404, detail=f"No configuration for language: {language}")
    
    return {
        "language": language,
        "config": config
    }


@router.get("/videos/tutorial/{language}")
async def get_tutorial_by_language(language: str):
    """Get Getting Started tutorial video for a specific language"""
    if language in TUTORIAL_VIDEOS:
        tutorial = TUTORIAL_VIDEOS[language]
        return {
            "video": tutorial,
            "talk_id": tutorial.get("talk_id"),
            "note": "Use D-ID API to fetch video URL: GET https://api.d-id.com/talks/{talk_id}"
        }
    
    # List available languages if not found
    raise HTTPException(
        status_code=404, 
        detail={
            "error": f"Tutorial not available in '{language}'",
            "available_languages": list(TUTORIAL_VIDEOS.keys())
        }
    )


@router.get("/videos/overview/{language}")
async def get_overview_by_language(language: str):
    """Get overview video metadata for a specific language"""
    if language == "en":
        # Return the main English overview
        video = next((v for v in VIDEOS if v["id"] == "05_complete_overview"), None)
        if video:
            return {
                "video": video,
                "url": "/api/tutorials/videos/05_complete_overview"
            }
    
    if language in MULTILANG_VIDEOS:
        return {
            "video": MULTILANG_VIDEOS[language],
            "note": "AI Avatar video generated via D-ID API"
        }
    
    # Default to English if language not found
    video = next((v for v in VIDEOS if v["id"] == "05_complete_overview"), None)
    return {
        "video": video,
        "url": "/api/tutorials/videos/05_complete_overview",
        "fallback": True,
        "requested_language": language
    }


@router.get("/videos/role/{role}")
async def get_role_specific_video(role: str):
    """Get role-specific overview video (jobseeker or recruiter)"""
    role_key = f"{role}_overview"
    
    if role_key in ROLE_VIDEOS:
        return {
            "video": ROLE_VIDEOS[role_key],
            "note": "30-second quick start guide"
        }
    
    raise HTTPException(status_code=404, detail=f"No video found for role: {role}")


# ==================== PERMANENT VIDEO STORAGE ====================

@router.post("/videos/download-all")
async def download_all_tutorial_videos(background_tasks: BackgroundTasks):
    """
    Download all D-ID tutorial videos for permanent storage.
    This runs in background and may take several minutes.
    """
    from services.video_storage import download_all_tutorials
    
    # Run download in background
    async def do_download():
        result = await download_all_tutorials(TUTORIAL_VIDEOS)
        import json
        # Save result to a status file
        status_file = TUTORIAL_VIDEOS_DIR / "download_status.json"
        with open(status_file, "w") as f:
            json.dump(result, f, indent=2)
    
    background_tasks.add_task(lambda: __import__('asyncio').get_event_loop().run_until_complete(do_download()))
    
    return {
        "status": "started",
        "message": f"Downloading {len(TUTORIAL_VIDEOS)} tutorial videos in background",
        "check_status": "/api/tutorials/videos/download-status"
    }


@router.get("/videos/download-status")
async def get_download_status():
    """Check the status of video downloads"""
    import json
    status_file = TUTORIAL_VIDEOS_DIR / "download_status.json"
    
    if status_file.exists():
        with open(status_file) as f:
            return json.load(f)
    
    return {"status": "not_started", "message": "No download has been initiated"}


@router.post("/videos/download/{language}")
async def download_single_tutorial(language: str):
    """Download a single tutorial video by language"""
    from services.video_storage import download_video
    
    if language not in TUTORIAL_VIDEOS:
        raise HTTPException(status_code=404, detail=f"No tutorial for language: {language}")
    
    talk_id = TUTORIAL_VIDEOS[language].get("talk_id")
    result = await download_video(talk_id, language)
    
    return result


@router.get("/videos/stored")
async def list_stored_videos():
    """List all permanently stored tutorial videos"""
    from services.video_storage import get_stored_videos
    
    videos = get_stored_videos()
    return {
        "videos": videos,
        "total": len(videos),
        "storage_path": str(TUTORIAL_VIDEOS_DIR)
    }


@router.get("/videos/play/{language}")
async def get_tutorial_video_url(language: str):
    """
    Get the URL to play a tutorial video.
    Returns local URL if downloaded, otherwise D-ID URL.
    """
    if language not in TUTORIAL_VIDEOS:
        raise HTTPException(status_code=404, detail=f"No tutorial for language: {language}")
    
    # Check if we have a local copy
    local_file = TUTORIAL_VIDEOS_DIR / f"tutorial_{language}.mp4"
    if local_file.exists():
        return {
            "language": language,
            "source": "local",
            "url": f"/api/tutorials/video-file/tutorial_{language}.mp4",
            "title": TUTORIAL_VIDEOS[language].get("title")
        }
    
    # Otherwise return D-ID info
    from services.video_storage import get_video_url
    talk_id = TUTORIAL_VIDEOS[language].get("talk_id")
    result = await get_video_url(talk_id)
    
    if result.get("success"):
        return {
            "language": language,
            "source": "d-id",
            "url": result.get("result_url"),
            "talk_id": talk_id,
            "title": TUTORIAL_VIDEOS[language].get("title"),
            "note": "D-ID URLs expire in 24-48 hours. Use /download/{language} to store permanently."
        }
    
    return {
        "language": language,
        "source": "unavailable",
        "error": result.get("error"),
        "talk_id": talk_id
    }


# This catch-all route MUST come after all specific /videos/xxx routes
@router.get("/videos/{video_id}")
async def get_video(video_id: str, lang: str = "en"):
    """Stream a tutorial video, optionally in a specific language"""
    # Find video metadata
    video_meta = next((v for v in VIDEOS if v["id"] == video_id), None)
    
    if not video_meta:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Check for translated version first
    if lang != "en":
        translated_path = VIDEOS_DIR / f"{video_id}_{lang}.mp4"
        if translated_path.exists():
            return FileResponse(
                path=str(translated_path),
                media_type="video/mp4",
                filename=f"{video_id}_{lang}.mp4"
            )
    
    # Fall back to original (English) video
    video_path = VIDEOS_DIR / video_meta["filename"]
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not available")
    
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=video_meta["filename"]
    )


@router.get("/video-file/{filename}")
async def serve_stored_video(filename: str, request: Request):
    """Serve a permanently stored tutorial video with range support for streaming"""
    from starlette.responses import Response
    
    video_path = TUTORIAL_VIDEOS_DIR / filename
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    file_size = video_path.stat().st_size
    range_header = request.headers.get("range")
    
    if range_header:
        # Parse range header: bytes=0-1000
        range_spec = range_header.replace("bytes=", "")
        parts = range_spec.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        end = min(end, file_size - 1)
        
        content_length = end - start + 1
        
        with open(video_path, "rb") as f:
            f.seek(start)
            content = f.read(content_length)
        
        return Response(
            content=content,
            status_code=206,
            media_type="video/mp4",
            headers={
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(content_length),
                "Cache-Control": "public, max-age=3600"
            }
        )
    
    # Full file response - use FileResponse for efficiency
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600"
        }
    )


@router.get("/guide")
async def get_navigation_guide():
    """Get the navigation guide content"""
    guide_path = Path("/app/docs/guides/NAVIGATION_GUIDE.md")
    
    if not guide_path.exists():
        raise HTTPException(status_code=404, detail="Guide not found")
    
    content = guide_path.read_text()
    
    return {
        "title": "MedMatch-AI KARAU Navigation Guide",
        "content": content,
        "format": "markdown"
    }


# Track translation jobs in memory
_translation_jobs: Dict[str, Dict] = {}


@router.post("/translate/{video_id}")
async def request_video_translation(video_id: str, lang: str, background_tasks: BackgroundTasks):
    """
    Request generation of a translated video using D-ID AI Avatar.
    This is an async operation - use the status endpoint to check progress.
    """
    # Validate video exists
    video = next((v for v in VIDEOS if v["id"] == video_id), None)
    if not video:
        raise HTTPException(status_code=404, detail=f"Video {video_id} not found")
    
    # Create job ID
    job_id = f"{video_id}_{lang}"
    
    # Check if already processing
    if job_id in _translation_jobs and _translation_jobs[job_id].get("status") == "generating":
        return {
            "job_id": job_id,
            "status": "generating",
            "message": "Translation already in progress"
        }
    
    # Initialize job
    _translation_jobs[job_id] = {
        "status": "generating",
        "video_id": video_id,
        "language": lang,
        "started_at": None,
        "completed_at": None,
        "video_url": None,
        "error": None
    }
    
    async def generate_translation():
        try:
            from datetime import datetime
            _translation_jobs[job_id]["started_at"] = datetime.now().isoformat()
            
            # Use FREE edge-tts to generate audio (instead of paid D-ID)
            result = await generate_tutorial_audio(video_id, lang)
            
            if result.get("success"):
                _translation_jobs[job_id]["status"] = "ready"
                _translation_jobs[job_id]["audio_url"] = result.get("audio_url")
                _translation_jobs[job_id]["video_url"] = result.get("audio_url")  # For backwards compatibility
                _translation_jobs[job_id]["completed_at"] = datetime.now().isoformat()
            else:
                _translation_jobs[job_id]["status"] = "failed"
                _translation_jobs[job_id]["error"] = result.get("error", "Unknown error")
                
        except Exception as e:
            _translation_jobs[job_id]["status"] = "failed"
            _translation_jobs[job_id]["error"] = str(e)
    
    # Run in background
    background_tasks.add_task(generate_translation)
    
    return {
        "job_id": job_id,
        "status": "generating",
        "message": f"Generating {lang} audio with Microsoft Neural Voice (FREE). Check status endpoint."
    }


@router.get("/translate/{video_id}/status")
async def get_translation_status(video_id: str, lang: str):
    """
    Get the status of a video translation job.
    """
    job_id = f"{video_id}_{lang}"
    
    if job_id not in _translation_jobs:
        # Check if translated video already exists
        translated_path = VIDEOS_DIR / f"{video_id}_{lang}.mp4"
        if translated_path.exists():
            return {
                "job_id": job_id,
                "status": "ready",
                "video_url": f"/api/tutorials/videos/{video_id}?lang={lang}"
            }
        return {
            "job_id": job_id,
            "status": "not_found",
            "message": "No translation job found. Start one with POST /translate/{video_id}"
        }
    
    job = _translation_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job.get("status", "unknown"),
        "video_url": job.get("video_url"),
        "error": job.get("error"),
        "talk_id": job.get("talk_id")
    }


@router.get("/audio/{filename}")
async def serve_audio_file(filename: str):
    """
    Serve generated audio files (edge-tts MP3 files).
    This endpoint provides audio files via /api/tutorials/audio/{filename}
    """
    from services.edge_tts_service import AUDIO_DIR
    
    audio_path = AUDIO_DIR / filename
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=filename,
        headers={
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600"
        }
    )


@router.get("/subtitles/{video_id}")
async def get_subtitles(video_id: str, lang: str = "en"):
    """
    Get subtitles/captions for a video in the specified language.
    Returns WebVTT format.
    
    Supports 22+ languages for all 5 tutorial videos.
    Updated: Feb 22, 2026
    """
    from services.tutorial_subtitles import get_subtitle, get_supported_subtitle_languages
    from fastapi.responses import Response
    
    # Get subtitle content from comprehensive subtitle service
    sub_content = get_subtitle(video_id, lang)
    
    return Response(
        content=sub_content,
        media_type="text/vtt",
        headers={
            "Content-Type": "text/vtt; charset=utf-8",
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.get("/subtitles/languages")
async def get_subtitle_languages():
    """Get list of all supported subtitle languages"""
    from services.tutorial_subtitles import get_supported_subtitle_languages
    return {
        "languages": get_supported_subtitle_languages(),
        "count": len(get_supported_subtitle_languages())
    }


# LEGACY: Old inline subtitles kept for reference but not used
# The new implementation uses services/tutorial_subtitles.py
_LEGACY_subtitles_en = {
    "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Welcome to MedMatch-AI KARAU! As a job seeker, you have access to powerful AI tools.

00:00:05.000 --> 00:00:12.000
Upload your resume and our AI will parse your skills automatically.

00:00:12.000 --> 00:00:20.000
Search across 15 job boards at once. Get interview preparation with real-time feedback.

00:00:20.000 --> 00:00:30.000
Your success predictor shows your chances before you apply.

00:00:30.000 --> 00:00:40.000
Track all your applications in one place. Start your career journey today!
""",
        "02_recruiter_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Recruiters, streamline your hiring with MedMatch-AI KARAU.

00:00:05.000 --> 00:00:10.000
Post jobs and reach qualified candidates instantly.

00:00:10.000 --> 00:00:18.000
Use our AI-powered applicant tracking system for efficient screening.

00:00:18.000 --> 00:00:24.000
Schedule interviews seamlessly. Let AI help you find the perfect match!

00:00:24.000 --> 00:00:28.000
Transform your hiring process today.
""",
        "03_privacy_matters": """WEBVTT

00:00:00.000 --> 00:00:05.000
Your privacy matters at MedMatch-AI KARAU.

00:00:05.000 --> 00:00:12.000
We use bank-level encryption for all your personal data.

00:00:12.000 --> 00:00:18.000
Control exactly what recruiters can see about you.

00:00:18.000 --> 00:00:25.000
Your job search stays completely confidential. We comply with GDPR and global privacy laws.

00:00:25.000 --> 00:00:34.000
You own your data and can delete it anytime. Your trust is our priority.
""",
        "04_faq_ai_compliance": """WEBVTT

00:00:00.000 --> 00:00:06.000
Let me answer common questions about AI compliance at MedMatch-AI KARAU.

00:00:06.000 --> 00:00:15.000
Our AI is transparent and explainable. We follow EU AI Act guidelines.

00:00:15.000 --> 00:00:25.000
Your data trains no external models. All AI decisions can be appealed.

00:00:25.000 --> 00:00:35.000
We regularly audit our algorithms for bias. Fair and ethical AI is our commitment.

00:00:35.000 --> 00:00:45.000
Questions? Contact our compliance team anytime.

00:00:45.000 --> 00:00:52.000
We're committed to responsible AI use.
""",
        "05_complete_overview": """WEBVTT

00:00:00.000 --> 00:00:08.000
Welcome to MedMatch-AI KARAU, your AI-powered career companion!

00:00:08.000 --> 00:00:18.000
Whether you're a job seeker or recruiter, we've got you covered.

00:00:18.000 --> 00:00:28.000
Upload resumes, search jobs, prepare for interviews, and connect with opportunities.

00:00:28.000 --> 00:00:40.000
Privacy-first, AI-powered, human-centered. Start your journey today!

00:00:40.000 --> 00:00:50.000
Join thousands of life sciences professionals already using MedMatch-AI KARAU.

00:00:50.000 --> 00:01:00.000
Your next career move starts here.
"""
    }
    
    # Spanish translations
    subtitles_es = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
¡Bienvenido a MedMatch-AI KARAU! Como buscador de empleo, tienes acceso a potentes herramientas de IA.

00:00:05.000 --> 00:00:12.000
Sube tu currículum y nuestra IA analizará tus habilidades automáticamente.

00:00:12.000 --> 00:00:20.000
Busca en 15 bolsas de trabajo a la vez. Prepárate para entrevistas con retroalimentación en tiempo real.

00:00:20.000 --> 00:00:30.000
El predictor de éxito te muestra tus posibilidades antes de aplicar.

00:00:30.000 --> 00:00:40.000
Rastrea todas tus aplicaciones en un solo lugar. ¡Comienza tu viaje profesional hoy!
""",
        "02_recruiter_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Reclutadores, optimicen sus contrataciones con MedMatch-AI KARAU.

00:00:05.000 --> 00:00:10.000
Publiquen empleos y lleguen a candidatos calificados al instante.

00:00:10.000 --> 00:00:18.000
Usen nuestro sistema de seguimiento de candidatos impulsado por IA.

00:00:18.000 --> 00:00:24.000
Programen entrevistas sin problemas. ¡Dejen que la IA les ayude a encontrar al candidato perfecto!

00:00:24.000 --> 00:00:28.000
Transformen su proceso de contratación hoy.
""",
        "03_privacy_matters": """WEBVTT

00:00:00.000 --> 00:00:05.000
Tu privacidad importa en MedMatch-AI KARAU.

00:00:05.000 --> 00:00:12.000
Usamos encriptación de nivel bancario para todos tus datos personales.

00:00:12.000 --> 00:00:18.000
Controla exactamente qué pueden ver los reclutadores sobre ti.

00:00:18.000 --> 00:00:25.000
Tu búsqueda de empleo permanece completamente confidencial. Cumplimos con GDPR y leyes de privacidad globales.

00:00:25.000 --> 00:00:34.000
Eres dueño de tus datos y puedes eliminarlos en cualquier momento. Tu confianza es nuestra prioridad.
""",
        "04_faq_ai_compliance": """WEBVTT

00:00:00.000 --> 00:00:06.000
Permíteme responder preguntas comunes sobre cumplimiento de IA en MedMatch-AI KARAU.

00:00:06.000 --> 00:00:15.000
Nuestra IA es transparente y explicable. Seguimos las directrices del Acta de IA de la UE.

00:00:15.000 --> 00:00:25.000
Tus datos no entrenan modelos externos. Todas las decisiones de IA pueden ser apeladas.

00:00:25.000 --> 00:00:35.000
Auditamos regularmente nuestros algoritmos para detectar sesgos. IA justa y ética es nuestro compromiso.

00:00:35.000 --> 00:00:45.000
¿Preguntas? Contacta a nuestro equipo de cumplimiento en cualquier momento.

00:00:45.000 --> 00:00:52.000
Estamos comprometidos con el uso responsable de la IA.
""",
        "05_complete_overview": """WEBVTT

00:00:00.000 --> 00:00:08.000
¡Bienvenido a MedMatch-AI KARAU, tu compañero de carrera impulsado por IA!

00:00:08.000 --> 00:00:18.000
Ya seas buscador de empleo o reclutador, te tenemos cubierto.

00:00:18.000 --> 00:00:28.000
Sube currículums, busca empleos, prepárate para entrevistas y conecta con oportunidades.

00:00:28.000 --> 00:00:40.000
Privacidad primero, impulsado por IA, centrado en el humano. ¡Comienza tu viaje hoy!

00:00:40.000 --> 00:00:50.000
Únete a miles de profesionales de ciencias de la vida que ya usan MedMatch-AI KARAU.

00:00:50.000 --> 00:01:00.000
Tu próximo movimiento de carrera comienza aquí.
"""
    }
    
    # French translations
    subtitles_fr = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Bienvenue sur MedMatch-AI KARAU ! En tant que chercheur d'emploi, vous avez accès à des outils IA puissants.

00:00:05.000 --> 00:00:12.000
Téléchargez votre CV et notre IA analysera vos compétences automatiquement.

00:00:12.000 --> 00:00:20.000
Recherchez sur 15 sites d'emploi à la fois. Préparez vos entretiens avec des retours en temps réel.

00:00:20.000 --> 00:00:30.000
Le prédicteur de succès vous montre vos chances avant de postuler.

00:00:30.000 --> 00:00:40.000
Suivez toutes vos candidatures en un seul endroit. Commencez votre parcours professionnel aujourd'hui !
"""
    }
    
    # German translations
    subtitles_de = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Willkommen bei MedMatch-AI KARAU! Als Jobsuchender haben Sie Zugang zu leistungsstarken KI-Tools.

00:00:05.000 --> 00:00:12.000
Laden Sie Ihren Lebenslauf hoch und unsere KI analysiert Ihre Fähigkeiten automatisch.

00:00:12.000 --> 00:00:20.000
Suchen Sie auf 15 Jobbörsen gleichzeitig. Bereiten Sie sich auf Interviews mit Echtzeit-Feedback vor.

00:00:20.000 --> 00:00:30.000
Der Erfolgsprädiktor zeigt Ihre Chancen vor der Bewerbung.

00:00:30.000 --> 00:00:40.000
Verfolgen Sie alle Ihre Bewerbungen an einem Ort. Starten Sie heute Ihre Karrierereise!
"""
    }
    
    # Japanese translations
    subtitles_ja = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
MedMatch-AI KARAUへようこそ！求職者として、強力なAIツールにアクセスできます。

00:00:05.000 --> 00:00:12.000
履歴書をアップロードすると、AIが自動的にスキルを分析します。

00:00:12.000 --> 00:00:20.000
15の求人サイトを一度に検索。リアルタイムフィードバックで面接準備。

00:00:20.000 --> 00:00:30.000
成功予測機能で応募前にチャンスを確認できます。

00:00:30.000 --> 00:00:40.000
すべての応募を一か所で管理。今日からキャリアの旅を始めましょう！
""",
        "02_recruiter_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
採用担当者の皆様、MedMatch-AI KARAUで採用を効率化しましょう。

00:00:05.000 --> 00:00:10.000
求人を投稿し、即座に適格な候補者にリーチ。

00:00:10.000 --> 00:00:18.000
AI搭載の応募者追跡システムで効率的なスクリーニング。

00:00:18.000 --> 00:00:24.000
シームレスな面接スケジュール。AIが最適な人材探しをサポート！

00:00:24.000 --> 00:00:28.000
今日から採用プロセスを変革しましょう。
"""
    }
    
    # Chinese (Simplified) translations
    subtitles_zh = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
欢迎使用MedMatch-AI KARAU！作为求职者，您可以使用强大的AI工具。

00:00:05.000 --> 00:00:12.000
上传您的简历，我们的AI将自动分析您的技能。

00:00:12.000 --> 00:00:20.000
同时搜索15个招聘网站。通过实时反馈准备面试。

00:00:20.000 --> 00:00:30.000
成功预测器在申请前显示您的机会。

00:00:30.000 --> 00:00:40.000
在一个地方跟踪所有申请。今天就开始您的职业之旅！
""",
        "02_recruiter_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
招聘人员，使用MedMatch-AI KARAU简化您的招聘流程。

00:00:05.000 --> 00:00:10.000
发布职位，即时接触合格候选人。

00:00:10.000 --> 00:00:18.000
使用AI驱动的申请人跟踪系统进行高效筛选。

00:00:18.000 --> 00:00:24.000
无缝安排面试。让AI帮助您找到最佳人选！

00:00:24.000 --> 00:00:28.000
今天就变革您的招聘流程。
"""
    }
    
    # Portuguese translations
    subtitles_pt = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Bem-vindo ao MedMatch-AI KARAU! Como candidato, você tem acesso a ferramentas poderosas de IA.

00:00:05.000 --> 00:00:12.000
Carregue seu currículo e nossa IA analisará suas habilidades automaticamente.

00:00:12.000 --> 00:00:20.000
Pesquise em 15 sites de emprego de uma vez. Prepare-se para entrevistas com feedback em tempo real.

00:00:20.000 --> 00:00:30.000
O preditor de sucesso mostra suas chances antes de se candidatar.

00:00:30.000 --> 00:00:40.000
Acompanhe todas as suas candidaturas em um só lugar. Comece sua jornada profissional hoje!
"""
    }
    
    # Arabic translations
    subtitles_ar = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
مرحبًا بك في MedMatch-AI KARAU! كباحث عن عمل، لديك إمكانية الوصول إلى أدوات ذكاء اصطناعي قوية.

00:00:05.000 --> 00:00:12.000
قم بتحميل سيرتك الذاتية وسيقوم الذكاء الاصطناعي بتحليل مهاراتك تلقائيًا.

00:00:12.000 --> 00:00:20.000
ابحث في 15 موقع توظيف في وقت واحد. استعد للمقابلات مع تعليقات فورية.

00:00:20.000 --> 00:00:30.000
يُظهر لك متنبئ النجاح فرصك قبل التقديم.

00:00:30.000 --> 00:00:40.000
تتبع جميع طلباتك في مكان واحد. ابدأ رحلتك المهنية اليوم!
"""
    }
    
    # Hindi translations
    subtitles_hi = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
MedMatch-AI KARAU में आपका स्वागत है! नौकरी चाहने वाले के रूप में, आपके पास शक्तिशाली AI उपकरण उपलब्ध हैं।

00:00:05.000 --> 00:00:12.000
अपना रिज्यूमे अपलोड करें और हमारा AI स्वचालित रूप से आपके कौशल का विश्लेषण करेगा।

00:00:12.000 --> 00:00:20.000
एक साथ 15 जॉब बोर्ड पर खोजें। रीयल-टाइम फीडबैक के साथ इंटरव्यू की तैयारी करें।

00:00:20.000 --> 00:00:30.000
सफलता भविष्यवक्ता आवेदन करने से पहले आपकी संभावनाएं दिखाता है।

00:00:30.000 --> 00:00:40.000
अपने सभी आवेदनों को एक जगह ट्रैक करें। आज ही अपनी करियर यात्रा शुरू करें!
"""
    }
    
    # Korean translations
    subtitles_ko = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
MedMatch-AI KARAU에 오신 것을 환영합니다! 구직자로서 강력한 AI 도구를 사용할 수 있습니다.

00:00:05.000 --> 00:00:12.000
이력서를 업로드하면 AI가 자동으로 기술을 분석합니다.

00:00:12.000 --> 00:00:20.000
15개 구직 사이트를 한 번에 검색하세요. 실시간 피드백으로 면접을 준비하세요.

00:00:20.000 --> 00:00:30.000
성공 예측기가 지원 전에 가능성을 보여줍니다.

00:00:30.000 --> 00:00:40.000
모든 지원서를 한 곳에서 추적하세요. 오늘 커리어 여정을 시작하세요!
"""
    }
    
    # Italian translations
    subtitles_it = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Benvenuto su MedMatch-AI KARAU! Come cercatore di lavoro, hai accesso a potenti strumenti AI.

00:00:05.000 --> 00:00:12.000
Carica il tuo CV e la nostra AI analizzerà automaticamente le tue competenze.

00:00:12.000 --> 00:00:20.000
Cerca su 15 siti di lavoro contemporaneamente. Preparati ai colloqui con feedback in tempo reale.

00:00:20.000 --> 00:00:30.000
Il predittore di successo mostra le tue possibilità prima di candidarti.

00:00:30.000 --> 00:00:40.000
Monitora tutte le tue candidature in un unico posto. Inizia oggi il tuo percorso professionale!
"""
    }
    
    # Russian translations
    subtitles_ru = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Добро пожаловать в MedMatch-AI KARAU! Как соискатель, вы имеете доступ к мощным инструментам ИИ.

00:00:05.000 --> 00:00:12.000
Загрузите резюме, и наш ИИ автоматически проанализирует ваши навыки.

00:00:12.000 --> 00:00:20.000
Ищите на 15 сайтах вакансий одновременно. Готовьтесь к собеседованиям с обратной связью в реальном времени.

00:00:20.000 --> 00:00:30.000
Предиктор успеха показывает ваши шансы перед подачей заявки.

00:00:30.000 --> 00:00:40.000
Отслеживайте все заявки в одном месте. Начните свой карьерный путь сегодня!
"""
    }
    
    # Swahili translations
    subtitles_sw = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Karibu MedMatch-AI KARAU! Kama mtafutaji wa kazi, una ufikiaji wa zana za AI zenye nguvu.

00:00:05.000 --> 00:00:12.000
Pakia CV yako na AI yetu itachambua ujuzi wako kiotomatiki.

00:00:12.000 --> 00:00:20.000
Tafuta kwenye tovuti 15 za kazi mara moja. Jiandae kwa mahojiano na maoni ya wakati halisi.

00:00:20.000 --> 00:00:30.000
Kitabiri cha mafanikio kinakuonyesha nafasi zako kabla ya kuomba.

00:00:30.000 --> 00:00:40.000
Fuatilia maombi yako yote mahali pamoja. Anza safari yako ya kazi leo!
"""
    }
    
    # Vietnamese translations
    subtitles_vi = {
        "01_jobseeker_features": """WEBVTT

00:00:00.000 --> 00:00:05.000
Chào mừng đến với MedMatch-AI KARAU! Là người tìm việc, bạn có quyền truy cập các công cụ AI mạnh mẽ.

00:00:05.000 --> 00:00:12.000
Tải CV của bạn lên và AI của chúng tôi sẽ tự động phân tích kỹ năng của bạn.

00:00:12.000 --> 00:00:20.000
Tìm kiếm trên 15 trang việc làm cùng lúc. Chuẩn bị phỏng vấn với phản hồi thời gian thực.

00:00:20.000 --> 00:00:30.000
Công cụ dự đoán thành công cho thấy cơ hội của bạn trước khi ứng tuyển.

00:00:30.000 --> 00:00:40.000
Theo dõi tất cả đơn ứng tuyển tại một nơi. Bắt đầu hành trình nghề nghiệp ngay hôm nay!
"""
    }
    
    # Select subtitle set based on language
    subtitle_sets = {
        "en": subtitles_en,
        "es": subtitles_es,
        "fr": subtitles_fr,
        "de": subtitles_de,
        "ja": subtitles_ja,
        "zh": subtitles_zh,
        "pt": subtitles_pt,
        "ar": subtitles_ar,
        "hi": subtitles_hi,
        "ko": subtitles_ko,
        "it": subtitles_it,
        "ru": subtitles_ru,
        "sw": subtitles_sw,
        "vi": subtitles_vi
    }
    
    # Get subtitles for video and language
    selected_subs = subtitle_sets.get(lang, subtitles_en)
    sub_content = selected_subs.get(video_id, subtitles_en.get(video_id, "WEBVTT\n\n"))
    
    # If no subtitle for this language, fall back to English with a note
    if lang not in subtitle_sets and video_id in subtitles_en:
        sub_content = subtitles_en[video_id]
    
    from fastapi.responses import Response
    return Response(
        content=sub_content,
        media_type="text/vtt",
        headers={
            "Content-Type": "text/vtt; charset=utf-8",
            "Access-Control-Allow-Origin": "*"
        }
    )

