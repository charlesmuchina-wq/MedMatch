"""
Video Storage Service
Downloads and permanently stores D-ID avatar videos
"""

import os
import httpx
import asyncio
from pathlib import Path
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# D-ID API Configuration
D_ID_API_KEY = os.environ.get("D_ID_API_KEY", "")
D_ID_BASE_URL = "https://api.d-id.com"

# Video storage directory
VIDEOS_DIR = Path("/app/backend/static/videos/tutorials")
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


async def get_video_url(talk_id: str) -> dict:
    """Get the video URL from D-ID API for a specific talk_id"""
    if not D_ID_API_KEY:
        return {"success": False, "error": "D-ID API key not configured"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{D_ID_BASE_URL}/talks/{talk_id}",
                headers={
                    "Authorization": f"Basic {D_ID_API_KEY}",
                    "Accept": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "talk_id": talk_id,
                    "status": data.get("status"),
                    "result_url": data.get("result_url"),
                    "created_at": data.get("created_at")
                }
            else:
                return {
                    "success": False,
                    "error": f"D-ID API returned {response.status_code}",
                    "detail": response.text
                }
    except Exception as e:
        logger.error(f"Error fetching video URL: {e}")
        return {"success": False, "error": str(e)}


async def download_video(talk_id: str, language: str) -> dict:
    """Download a D-ID video and store it permanently"""
    # First get the video URL
    url_result = await get_video_url(talk_id)
    
    if not url_result.get("success"):
        return url_result
    
    video_url = url_result.get("result_url")
    if not video_url:
        return {"success": False, "error": "No video URL available", "status": url_result.get("status")}
    
    # Download the video
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url, timeout=120.0)
            
            if response.status_code == 200:
                # Save to file
                filename = f"tutorial_{language}.mp4"
                filepath = VIDEOS_DIR / filename
                
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
                file_size = filepath.stat().st_size
                
                return {
                    "success": True,
                    "talk_id": talk_id,
                    "language": language,
                    "filename": filename,
                    "filepath": str(filepath),
                    "file_size_mb": round(file_size / (1024 * 1024), 2),
                    "downloaded_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Download failed with status {response.status_code}"
                }
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        return {"success": False, "error": str(e)}


async def download_all_tutorials(tutorials: dict) -> dict:
    """Download all tutorial videos"""
    results = {
        "downloaded": [],
        "failed": [],
        "total": len(tutorials)
    }
    
    for lang, info in tutorials.items():
        talk_id = info.get("talk_id")
        if not talk_id:
            results["failed"].append({"language": lang, "error": "No talk_id"})
            continue
        
        logger.info(f"Downloading {lang} tutorial: {talk_id}")
        result = await download_video(talk_id, lang)
        
        if result.get("success"):
            results["downloaded"].append({
                "language": lang,
                "filename": result.get("filename"),
                "file_size_mb": result.get("file_size_mb")
            })
        else:
            results["failed"].append({
                "language": lang,
                "error": result.get("error"),
                "status": result.get("status")
            })
        
        # Small delay between downloads
        await asyncio.sleep(1)
    
    results["success_count"] = len(results["downloaded"])
    results["failed_count"] = len(results["failed"])
    
    return results


def get_stored_videos() -> list:
    """List all stored tutorial videos"""
    videos = []
    for filepath in VIDEOS_DIR.glob("*.mp4"):
        videos.append({
            "filename": filepath.name,
            "language": filepath.stem.replace("tutorial_", ""),
            "size_mb": round(filepath.stat().st_size / (1024 * 1024), 2),
            "url": f"/api/tutorials/static/{filepath.name}"
        })
    return videos
