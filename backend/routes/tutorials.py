"""
Video Tutorials API Routes
Serves instructional videos for MedMatch navigation
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import os

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
        "title": "Complete MedMatch Overview",
        "description": "AI-powered comprehensive overview of all MedMatch features for job seekers and recruiters",
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
        "title": "Descripción General de MedMatch",
        "description": "Visión completa impulsada por IA de todas las funciones de MedMatch",
        "duration": "60 seconds",
        "voice": "Elvira (es-ES)",
        "language": "es"
    },
    "fr": {
        "id": "overview_french",
        "title": "Présentation de MedMatch",
        "description": "Aperçu complet alimenté par l'IA de toutes les fonctionnalités MedMatch",
        "duration": "60 seconds",
        "voice": "Denise (fr-FR)",
        "language": "fr"
    },
    "de": {
        "id": "overview_german",
        "title": "MedMatch Übersicht",
        "description": "KI-gestützte umfassende Übersicht aller MedMatch-Funktionen",
        "duration": "60 seconds",
        "voice": "Katja (de-DE)",
        "language": "de"
    },
    "ja": {
        "id": "overview_japanese",
        "title": "MedMatch 概要",
        "description": "AIによるMedMatch全機能の包括的な概要",
        "duration": "60 seconds",
        "voice": "Nanami (ja-JP)",
        "language": "ja"
    },
    "zh": {
        "id": "overview_chinese",
        "title": "MedMatch 概述",
        "description": "AI驱动的MedMatch全功能综合概述",
        "duration": "60 seconds",
        "voice": "Xiaoxiao (zh-CN)",
        "language": "zh"
    },
    # African Languages
    "sw": {
        "id": "overview_swahili",
        "title": "Muhtasari wa MedMatch",
        "description": "Muhtasari kamili wa MedMatch unaoendelea na AI kwa watafutaji wa kazi na waajiri",
        "duration": "60 seconds",
        "voice": "Zuri (sw-KE)",
        "language": "sw",
        "talk_id": "tlk_7LhG-0hhG3ynEd2KxohrN"
    },
    "af": {
        "id": "overview_afrikaans",
        "title": "MedMatch Oorsig",
        "description": "KI-aangedrewe omvattende oorsig van alle MedMatch-funksies",
        "duration": "60 seconds",
        "voice": "Adri (af-ZA)",
        "language": "af",
        "talk_id": "tlk_jKq2BCNU1NiVypyd2xJS4"
    },
    "en-NG": {
        "id": "overview_english_nigeria",
        "title": "MedMatch Overview (Nigerian English)",
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
        "title": "Erste Schritte mit MedMatch",
        "description": "Lernen Sie in wenigen Minuten, wie Sie MedMatch nutzen können",
        "duration": "45 seconds",
        "voice": "Katja (de-DE)",
        "language": "de",
        "talk_id": "tlk_U_WgYRHRZvTazt9trvZpg"
    },
    "fr": {
        "id": "tutorial_french",
        "title": "Démarrer avec MedMatch",
        "description": "Apprenez à utiliser MedMatch en quelques minutes",
        "duration": "45 seconds",
        "voice": "Denise (fr-FR)",
        "language": "fr",
        "talk_id": "tlk_X0fd9qzrvTlsqBWynmMe6"
    },
    "es": {
        "id": "tutorial_spanish",
        "title": "Comenzar con MedMatch",
        "description": "Aprende a usar MedMatch en pocos minutos",
        "duration": "45 seconds",
        "voice": "Elvira (es-ES)",
        "language": "es",
        "talk_id": "tlk_h4r6Fu-x5cHidSGm1xr_J"
    },
    "ja": {
        "id": "tutorial_japanese",
        "title": "MedMatchの使い方",
        "description": "数分でMedMatchの使い方を学びましょう",
        "duration": "45 seconds",
        "voice": "Nanami (ja-JP)",
        "language": "ja",
        "talk_id": "tlk_8q1WRtDgr1xmiBqucb1nR"
    },
    "zh": {
        "id": "tutorial_chinese",
        "title": "MedMatch入门指南",
        "description": "几分钟内学会如何使用MedMatch",
        "duration": "45 seconds",
        "voice": "Xiaoxiao (zh-CN)",
        "language": "zh",
        "talk_id": "tlk_uJmYXojHb0OsKyEEq-KrZ"
    },
    "pt": {
        "id": "tutorial_portuguese",
        "title": "Começando com MedMatch",
        "description": "Aprenda a usar o MedMatch em poucos minutos",
        "duration": "45 seconds",
        "voice": "Francisca (pt-BR)",
        "language": "pt",
        "talk_id": "tlk_Lyp35W6ADuqPC23v43DpV"
    },
    "ar": {
        "id": "tutorial_arabic",
        "title": "البدء مع MedMatch",
        "description": "تعلم كيفية استخدام MedMatch في دقائق",
        "duration": "45 seconds",
        "voice": "Salma (ar-EG)",
        "language": "ar",
        "talk_id": "tlk_64wv6WIrs1z5JG-NiRo6c"
    },
    "ko": {
        "id": "tutorial_korean",
        "title": "MedMatch 시작하기",
        "description": "몇 분 안에 MedMatch 사용법을 배우세요",
        "duration": "45 seconds",
        "voice": "SunHi (ko-KR)",
        "language": "ko",
        "talk_id": "tlk_BqThujQ3B-8YX92KjkYf7"
    },
    "hi": {
        "id": "tutorial_hindi",
        "title": "MedMatch के साथ शुरुआत",
        "description": "कुछ ही मिनटों में MedMatch का उपयोग करना सीखें",
        "duration": "45 seconds",
        "voice": "Swara (hi-IN)",
        "language": "hi",
        "talk_id": "tlk_vXxJt9acDRpN4LhZBkJJ7"
    },
    "it": {
        "id": "tutorial_italian",
        "title": "Iniziare con MedMatch",
        "description": "Impara a usare MedMatch in pochi minuti",
        "duration": "45 seconds",
        "voice": "Elsa (it-IT)",
        "language": "it",
        "talk_id": "tlk__jTrzZfoNjpnPZ9R1feFS"
    },
    "ru": {
        "id": "tutorial_russian",
        "title": "Начало работы с MedMatch",
        "description": "Узнайте, как использовать MedMatch за несколько минут",
        "duration": "45 seconds",
        "voice": "Svetlana (ru-RU)",
        "language": "ru",
        "talk_id": "tlk_0G_ntBt-SX1Iz15Jc232W"
    },
    "nl": {
        "id": "tutorial_dutch",
        "title": "Aan de slag met MedMatch",
        "description": "Leer in een paar minuten hoe je MedMatch kunt gebruiken",
        "duration": "45 seconds",
        "voice": "Colette (nl-NL)",
        "language": "nl",
        "talk_id": "tlk_L-sAolNvFfXWpfQsUtgW3"
    },
    "pl": {
        "id": "tutorial_polish",
        "title": "Rozpocznij z MedMatch",
        "description": "Naucz się korzystać z MedMatch w kilka minut",
        "duration": "45 seconds",
        "voice": "Zofia (pl-PL)",
        "language": "pl",
        "talk_id": "tlk_ikCuJjKUqU8JQ4ZVCV60e"
    }
}

# Role-specific videos
ROLE_VIDEOS = {
    "jobseeker_overview": {
        "id": "jobseeker_overview_30s",
        "title": "Job Seeker Quick Start",
        "description": "30-second guide for job seekers using MedMatch",
        "duration": "30 seconds",
        "voice": "Jenny (en-US)",
        "target_audience": "jobseeker"
    },
    "recruiter_overview": {
        "id": "recruiter_overview_30s",
        "title": "Recruiter Quick Start",
        "description": "30-second guide for recruiters using MedMatch",
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
                "url": f"/api/tutorials/videos/05_complete_overview"
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
        "url": f"/api/tutorials/videos/05_complete_overview",
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


@router.get("/guide")
async def get_navigation_guide():
    """Get the navigation guide content"""
    guide_path = Path("/app/docs/guides/NAVIGATION_GUIDE.md")
    
    if not guide_path.exists():
        raise HTTPException(status_code=404, detail="Guide not found")
    
    content = guide_path.read_text()
    
    return {
        "title": "MedMatch Navigation Guide",
        "content": content,
        "format": "markdown"
    }


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


@router.get("/video-file/{filename}")
async def serve_stored_video(filename: str):
    """Serve a permanently stored tutorial video"""
    video_path = TUTORIAL_VIDEOS_DIR / filename
    
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found")
    
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=filename
    )

