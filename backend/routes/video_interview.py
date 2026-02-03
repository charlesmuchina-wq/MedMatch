"""
Video Interview Routes
Handles: Video recording, playback, Whisper transcription, AI analysis
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import tempfile
import os

from emergentintegrations.llm.chat import LlmChat
from emergentintegrations.llm.openai import OpenAISpeechToText

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/video-interview", tags=["Video Interview"])

# Supported video formats
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.webm', '.mov', '.avi', '.mkv']
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

# ============== Models ==============

class VideoSessionCreate(BaseModel):
    title: str = "Practice Session"
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    questions: List[str] = []

class VideoAnalysisRequest(BaseModel):
    session_id: str
    transcript: str
    question: Optional[str] = None

# ============== Routes ==============

@router.post("/sessions/create")
async def create_video_session(session_data: VideoSessionCreate, request: Request):
    """Create a new video interview practice session"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_id = str(uuid.uuid4())
    session = {
        "session_id": session_id,
        "user_id": user.get("user_id"),
        "title": session_data.title,
        "job_title": session_data.job_title,
        "company_name": session_data.company_name,
        "questions": session_data.questions,
        "recordings": [],
        "status": "in_progress",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.video_sessions.insert_one(session)
    
    return {
        "session_id": session_id,
        "message": "Video session created",
        "questions": session_data.questions
    }

@router.get("/sessions")
async def list_video_sessions(request: Request, limit: int = 20):
    """List user's video interview sessions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    sessions = await db.video_sessions.find(
        {"user_id": user.get("user_id")},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {"sessions": sessions, "total": len(sessions)}

@router.get("/sessions/{session_id}")
async def get_video_session(session_id: str, request: Request):
    """Get a specific video session"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session = await db.video_sessions.find_one(
        {"session_id": session_id, "user_id": user.get("user_id")},
        {"_id": 0}
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@router.post("/sessions/{session_id}/upload")
async def upload_video_recording(
    session_id: str,
    file: UploadFile = File(...),
    question_index: int = Form(0),
    question_text: str = Form(""),
    request: Request = None
):
    """Upload a video recording for a session"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate session exists
    session = await db.video_sessions.find_one({
        "session_id": session_id,
        "user_id": user.get("user_id")
    })
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Validate file
    filename = file.filename.lower()
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in SUPPORTED_VIDEO_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Supported: {', '.join(SUPPORTED_VIDEO_FORMATS)}"
        )
    
    content = await file.read()
    if len(content) > MAX_VIDEO_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 100MB.")
    
    # Extract audio and transcribe
    transcript = ""
    try:
        # Save video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_video:
            temp_video.write(content)
            temp_video_path = temp_video.name
        
        # For video files, we extract audio track for transcription
        # The video itself contains audio that Whisper can process
        stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
        
        with open(temp_video_path, "rb") as video_file:
            response = await stt.transcribe(
                file=video_file,
                model="whisper-1",
                response_format="verbose_json"
            )
        
        transcript = response.text if hasattr(response, 'text') else str(response)
        
        # Clean up
        os.unlink(temp_video_path)
        
    except Exception as e:
        logging.error(f"Video transcription error: {e}")
        transcript = "[Transcription failed - please try again]"
    
    # Create recording record
    recording_id = str(uuid.uuid4())
    recording = {
        "recording_id": recording_id,
        "question_index": question_index,
        "question_text": question_text,
        "transcript": transcript,
        "duration": None,  # Could be extracted from video metadata
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update session with recording
    await db.video_sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"recordings": recording},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {
        "recording_id": recording_id,
        "transcript": transcript,
        "message": "Video uploaded and transcribed"
    }

@router.post("/analyze")
async def analyze_video_response(req: VideoAnalysisRequest, request: Request):
    """Analyze a video response transcript with AI"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get session for context
    session = await db.video_sessions.find_one(
        {"session_id": req.session_id, "user_id": user.get("user_id")},
        {"_id": 0}
    )
    
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY)
        
        context = ""
        if session:
            if session.get("job_title"):
                context += f"Target Position: {session['job_title']}\n"
            if session.get("company_name"):
                context += f"Target Company: {session['company_name']}\n"
        
        response = await chat.send_message(
            system_message="""You are an expert interview coach analyzing a candidate's video interview response.

Analyze the transcript and provide detailed feedback. Return JSON:
{
    "overall_score": <1-10>,
    "communication_score": <1-10>,
    "content_score": <1-10>,
    "confidence_indicators": ["indicator 1", "indicator 2"],
    "strengths": ["strength 1", "strength 2"],
    "areas_for_improvement": ["improvement 1", "improvement 2"],
    "filler_words_detected": ["um", "like", etc],
    "filler_word_count": <number>,
    "key_points_made": ["point 1", "point 2"],
    "missing_elements": ["element 1"],
    "suggestions": ["suggestion 1", "suggestion 2"],
    "revised_response": "<improved version of their answer>",
    "body_language_tips": ["tip 1", "tip 2"],
    "tone_assessment": "confident/nervous/neutral/enthusiastic"
}""",
            text=f"""Analyze this video interview response:

{context}
QUESTION: {req.question or 'General interview question'}

CANDIDATE'S RESPONSE (transcript):
{req.transcript}

Provide comprehensive interview coaching feedback.""",
            json_mode=True
        )
        
        import json
        analysis = json.loads(response)
        
        # Store analysis
        analysis_record = {
            "id": str(uuid.uuid4()),
            "session_id": req.session_id,
            "user_id": user.get("user_id"),
            "question": req.question,
            "transcript": req.transcript,
            "analysis": analysis,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.video_analyses.insert_one(analysis_record)
        
        return {
            "analysis": analysis,
            "record_id": analysis_record["id"]
        }
        
    except Exception as e:
        logging.error(f"Video analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.delete("/sessions/{session_id}")
async def delete_video_session(session_id: str, request: Request):
    """Delete a video session"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.video_sessions.delete_one({
        "session_id": session_id,
        "user_id": user.get("user_id")
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Also delete related analyses
    await db.video_analyses.delete_many({"session_id": session_id})
    
    return {"message": "Session deleted"}

@router.get("/common-questions/{job_type}")
async def get_common_video_questions(job_type: str, request: Request):
    """Get common video interview questions by job type"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Predefined common questions by category
    questions_bank = {
        "general": [
            "Tell me about yourself.",
            "Why are you interested in this position?",
            "What are your greatest strengths?",
            "What is your biggest weakness?",
            "Where do you see yourself in 5 years?",
            "Why should we hire you?",
            "Tell me about a challenge you've overcome.",
            "How do you handle stress and pressure?"
        ],
        "behavioral": [
            "Tell me about a time you showed leadership.",
            "Describe a situation where you had to work with a difficult colleague.",
            "Give an example of a goal you reached and how you achieved it.",
            "Tell me about a time you failed and what you learned.",
            "Describe a situation where you had to make a quick decision."
        ],
        "technical": [
            "Walk me through your technical background.",
            "Describe a complex project you've worked on.",
            "How do you stay current with industry trends?",
            "Tell me about a technical problem you solved.",
            "What development methodologies are you familiar with?"
        ],
        "leadership": [
            "Describe your leadership style.",
            "How do you motivate your team?",
            "Tell me about a time you had to deliver difficult feedback.",
            "How do you handle conflicts within your team?",
            "Describe a successful project you led."
        ]
    }
    
    questions = questions_bank.get(job_type.lower(), questions_bank["general"])
    
    return {
        "job_type": job_type,
        "questions": questions,
        "total": len(questions)
    }
