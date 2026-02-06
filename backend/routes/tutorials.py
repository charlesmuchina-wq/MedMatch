"""
Video Tutorials API Routes
Serves instructional videos for MedMatch navigation
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from typing import List
import os

router = APIRouter(prefix="/tutorials", tags=["Tutorials"])

VIDEOS_DIR = Path("/app/videos")

# Video metadata
VIDEOS = [
    {
        "id": "01_jobseeker_features",
        "title": "Job Seeker Features",
        "description": "Complete guide to dashboard, job search, resume, applications, and interview prep",
        "duration": "34 seconds",
        "category": "job_seeker",
        "filename": "01_jobseeker_features.mp4"
    },
    {
        "id": "02_recruiter_features",
        "title": "Recruiter Features",
        "description": "Dashboard, applicant tracking, job postings, and hiring tools",
        "duration": "30 seconds",
        "category": "recruiter",
        "filename": "02_recruiter_features.mp4"
    },
    {
        "id": "03_privacy_matters",
        "title": "Your Privacy Matters",
        "description": "How we protect your data and keep your job search secure",
        "duration": "31 seconds",
        "category": "general",
        "filename": "03_privacy_matters.mp4"
    }
]


@router.get("/videos")
async def list_videos(category: str = None):
    """List all available tutorial videos"""
    videos = VIDEOS.copy()
    
    if category:
        videos = [v for v in videos if v["category"] == category]
    
    # Add URL to each video
    for video in videos:
        video["url"] = f"/api/tutorials/videos/{video['id']}"
        video["exists"] = (VIDEOS_DIR / video["filename"]).exists()
    
    return {
        "videos": videos,
        "count": len(videos)
    }


@router.get("/videos/{video_id}")
async def get_video(video_id: str):
    """Stream a tutorial video"""
    # Find video metadata
    video_meta = next((v for v in VIDEOS if v["id"] == video_id), None)
    
    if not video_meta:
        raise HTTPException(status_code=404, detail="Video not found")
    
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
