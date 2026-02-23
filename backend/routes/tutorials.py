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


@router.get("/subtitles/languages")
async def get_subtitle_languages():
    """Get list of all supported subtitle languages"""
    from services.tutorial_subtitles import get_supported_subtitle_languages
    return {
        "languages": get_supported_subtitle_languages(),
        "count": len(get_supported_subtitle_languages())
    }


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


# ==================== ADMIN: BATCH AUDIO GENERATION ====================

# Track batch generation status in memory
_batch_generation_status: Dict[str, Dict] = {}

@router.post("/admin/generate-all-audio")
async def generate_all_audio(background_tasks: BackgroundTasks):
    """
    Admin endpoint: Generate audio for ALL video-language combinations.
    This runs in background and pre-caches all audio files for instant playback.
    """
    from services.edge_tts_service import TUTORIAL_SCRIPTS, LANGUAGE_VOICES, generate_tutorial_audio
    import asyncio
    from datetime import datetime
    
    # Calculate total combinations
    total = sum(len(scripts) for scripts in TUTORIAL_SCRIPTS.values())
    
    # Initialize status
    job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    _batch_generation_status[job_id] = {
        "status": "running",
        "total": total,
        "completed": 0,
        "failed": 0,
        "current": None,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "errors": []
    }
    
    async def generate_all():
        status = _batch_generation_status[job_id]
        
        for video_id, scripts in TUTORIAL_SCRIPTS.items():
            for lang in scripts.keys():
                status["current"] = f"{video_id} ({lang})"
                try:
                    result = await generate_tutorial_audio(video_id, lang)
                    if result.get("success"):
                        status["completed"] += 1
                    else:
                        status["failed"] += 1
                        status["errors"].append(f"{video_id}/{lang}: {result.get('error')}")
                except Exception as e:
                    status["failed"] += 1
                    status["errors"].append(f"{video_id}/{lang}: {str(e)}")
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
        
        status["status"] = "completed"
        status["current"] = None
        status["completed_at"] = datetime.now().isoformat()
    
    # Run in background
    background_tasks.add_task(lambda: __import__('asyncio').get_event_loop().run_until_complete(generate_all()))
    
    return {
        "job_id": job_id,
        "status": "started",
        "total_combinations": total,
        "message": f"Generating {total} audio files in background. Check status at /api/tutorials/admin/generation-status/{job_id}"
    }


@router.get("/admin/generation-status/{job_id}")
async def get_generation_status(job_id: str):
    """Get the status of a batch audio generation job"""
    if job_id not in _batch_generation_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = _batch_generation_status[job_id]
    progress = (status["completed"] + status["failed"]) / status["total"] * 100 if status["total"] > 0 else 0
    
    return {
        **status,
        "progress_percent": round(progress, 1)
    }


@router.get("/admin/audio-coverage")
async def get_audio_coverage():
    """
    Admin endpoint: Get current audio file coverage statistics.
    Shows which video-language combinations have pre-generated audio.
    """
    from services.edge_tts_service import TUTORIAL_SCRIPTS, AUDIO_DIR
    
    # Get all generated audio files
    audio_files = set(os.listdir(AUDIO_DIR)) if AUDIO_DIR.exists() else set()
    
    coverage = {}
    total_possible = 0
    total_generated = 0
    
    for video_id, scripts in TUTORIAL_SCRIPTS.items():
        video_coverage = {
            "total": len(scripts),
            "generated": 0,
            "missing": []
        }
        
        for lang in scripts.keys():
            total_possible += 1
            # Check if any audio file exists for this combo (filename pattern: {video_id}_{lang}_*.mp3)
            has_audio = any(f.startswith(f"{video_id}_{lang}_") for f in audio_files)
            if has_audio:
                video_coverage["generated"] += 1
                total_generated += 1
            else:
                video_coverage["missing"].append(lang)
        
        coverage[video_id] = video_coverage
    
    return {
        "summary": {
            "total_combinations": total_possible,
            "generated": total_generated,
            "missing": total_possible - total_generated,
            "coverage_percent": round(total_generated / total_possible * 100, 1) if total_possible > 0 else 0
        },
        "by_video": coverage,
        "audio_files_count": len(audio_files)
    }


# End of tutorials router - all subtitles now served from services/tutorial_subtitles.py
