"""
Video Asset API Routes - CAPA Implementation

Provides endpoints for:
1. Fetching validated video configurations (Source of Truth)
2. Video generation triggers
3. Asset validation and status checking
4. Frontend configuration endpoint

Created: Feb 20, 2026 - CAPA Resolution
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
import logging

from services.video_asset_manager import video_asset_manager, LANGUAGE_AVATAR_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/video-assets", tags=["Video Assets"])


@router.get("/config")
async def get_frontend_config():
    """
    Get complete video configuration for frontend.
    This is the SINGLE SOURCE OF TRUTH for avatar-video mapping.
    Frontend should fetch this and use it for all video displays.
    """
    try:
        config = await video_asset_manager.get_frontend_config()
        return config
    except Exception as e:
        logger.error(f"Error getting frontend config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/{language_code}")
async def get_language_config(language_code: str):
    """Get configuration for a specific language."""
    if language_code not in LANGUAGE_AVATAR_CONFIG:
        raise HTTPException(status_code=404, detail=f"Language not supported: {language_code}")
    
    config = video_asset_manager.get_language_config(language_code)
    asset = await video_asset_manager.get_asset(language_code)
    
    return {
        "config": config,
        "asset": asset,
        "is_ready": asset and asset.get("status") == "ready"
    }


@router.get("/validate/{language_code}")
async def validate_video_asset(language_code: str):
    """
    Validate that a video asset matches expected configuration.
    Use this to check if regeneration is needed.
    """
    if language_code not in LANGUAGE_AVATAR_CONFIG:
        raise HTTPException(status_code=404, detail=f"Language not supported: {language_code}")
    
    validation = await video_asset_manager.validate_asset(language_code)
    return validation


@router.get("/validate-all")
async def validate_all_assets():
    """Validate all video assets and return summary."""
    results = {
        "valid": [],
        "invalid": [],
        "missing": []
    }
    
    for lang_code in LANGUAGE_AVATAR_CONFIG.keys():
        validation = await video_asset_manager.validate_asset(lang_code)
        
        if validation.get("valid"):
            results["valid"].append(lang_code)
        elif validation.get("reason") == "no_record" or validation.get("reason") == "file_missing":
            results["missing"].append({"language": lang_code, "reason": validation.get("reason")})
        else:
            results["invalid"].append({"language": lang_code, "reason": validation.get("reason")})
    
    return {
        "total_languages": len(LANGUAGE_AVATAR_CONFIG),
        "valid_count": len(results["valid"]),
        "invalid_count": len(results["invalid"]),
        "missing_count": len(results["missing"]),
        "results": results
    }


@router.post("/generate/{language_code}")
async def generate_video(language_code: str, background_tasks: BackgroundTasks):
    """
    Trigger video generation for a specific language.
    Runs in background to avoid timeout.
    """
    if language_code not in LANGUAGE_AVATAR_CONFIG:
        raise HTTPException(status_code=404, detail=f"Language not supported: {language_code}")
    
    # Queue the generation
    background_tasks.add_task(video_asset_manager.generate_video, language_code)
    
    config = video_asset_manager.get_language_config(language_code)
    
    return {
        "status": "queued",
        "language_code": language_code,
        "avatar_type": config["avatar_type"],
        "voice_name": config["voice_name"],
        "message": f"Video generation queued for {language_code}. Check status with GET /api/video-assets/status/{language_code}"
    }


@router.post("/generate-all")
async def generate_all_videos(
    background_tasks: BackgroundTasks,
    languages: Optional[List[str]] = None
):
    """
    Trigger regeneration of all videos or specific languages.
    This is a long-running operation.
    """
    if languages:
        # Validate languages
        invalid = [l for l in languages if l not in LANGUAGE_AVATAR_CONFIG]
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid languages: {invalid}")
        target_languages = languages
    else:
        target_languages = list(LANGUAGE_AVATAR_CONFIG.keys())
    
    # Queue all regenerations
    for lang in target_languages:
        background_tasks.add_task(video_asset_manager.generate_video, lang)
    
    return {
        "status": "queued",
        "languages": target_languages,
        "total": len(target_languages),
        "message": "Video generation queued for all languages. This may take several minutes."
    }


@router.get("/status/{language_code}")
async def get_video_status(language_code: str):
    """Get current status of a video asset."""
    if language_code not in LANGUAGE_AVATAR_CONFIG:
        raise HTTPException(status_code=404, detail=f"Language not supported: {language_code}")
    
    asset = await video_asset_manager.get_asset(language_code)
    config = video_asset_manager.get_language_config(language_code)
    
    if not asset:
        return {
            "status": "not_generated",
            "language_code": language_code,
            "config": config
        }
    
    return {
        "status": asset.get("status", "unknown"),
        "language_code": language_code,
        "content_hash": asset.get("content_hash"),
        "file_size_bytes": asset.get("file_size_bytes"),
        "generated_at": asset.get("generated_at"),
        "d_id_talk_id": asset.get("d_id_talk_id"),
        "error": asset.get("error"),
        "config": config
    }


@router.get("/url/{language_code}")
async def get_video_url(language_code: str):
    """
    Get validated video URL with cache-busting parameters.
    Frontend should use this endpoint to get the correct URL.
    """
    if language_code not in LANGUAGE_AVATAR_CONFIG:
        raise HTTPException(status_code=404, detail=f"Language not supported: {language_code}")
    
    url_info = await video_asset_manager.get_video_url(language_code)
    return url_info


@router.get("/assets")
async def list_all_assets():
    """List all video assets from database."""
    assets = await video_asset_manager.get_all_assets()
    return {
        "assets": assets,
        "total": len(assets)
    }


@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of all supported languages with their configurations."""
    languages = []
    for lang_code, config in LANGUAGE_AVATAR_CONFIG.items():
        full_config = video_asset_manager.get_language_config(lang_code)
        languages.append({
            "code": lang_code,
            "avatar_type": config["avatar_type"],
            "voice_name": config["voice_name"],
            "region": config["region"],
            "thumbnail_url": full_config["thumbnail_url"]
        })
    
    return {
        "languages": languages,
        "total": len(languages)
    }
