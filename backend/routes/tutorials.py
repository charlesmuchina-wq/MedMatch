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
        "id": "01_jobseeker_intro",
        "title": "Getting Started as a Job Seeker",
        "description": "Complete guide to creating your profile and finding jobs",
        "duration": "29 seconds",
        "category": "job_seeker",
        "filename": "01_jobseeker_intro.mp4"
    },
    {
        "id": "02_recruiter_dashboard",
        "title": "Recruiter Dashboard Overview",
        "description": "Managing job postings, tracking applicants, and hiring",
        "duration": "28 seconds",
        "category": "recruiter",
        "filename": "02_recruiter_dashboard.mp4"
    },
    {
        "id": "03_job_search",
        "title": "Finding Your Perfect Job",
        "description": "Search, filter, and apply to jobs with AI matching",
        "duration": "26 seconds",
        "category": "job_seeker",
        "filename": "03_job_search.mp4"
    },
    {
        "id": "04_ats_system",
        "title": "Applicant Tracking System",
        "description": "Create application links and track candidates",
        "duration": "24 seconds",
        "category": "recruiter",
        "filename": "04_ats_system.mp4"
    },
    {
        "id": "05_resume_upload",
        "title": "Upload Your Resume",
        "description": "AI-powered resume parsing and profile completion",
        "duration": "24 seconds",
        "category": "job_seeker",
        "filename": "05_resume_upload.mp4"
    },
    {
        "id": "06_interview_prep",
        "title": "Interview Preparation",
        "description": "Practice questions and AI feedback for interviews",
        "duration": "23 seconds",
        "category": "job_seeker",
        "filename": "06_interview_prep.mp4"
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
