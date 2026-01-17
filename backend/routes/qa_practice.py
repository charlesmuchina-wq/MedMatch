"""
Q&A Interview Practice Routes
Handles: Interview question input, AI-driven answer generation, resume correlation,
         voice recording analysis, and feedback based on job requirements
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import base64
import io
import tempfile
import os

from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai import OpenAISpeechToText

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/qa-practice", tags=["Q&A Practice"])

# Supported audio formats
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm']
MAX_AUDIO_SIZE = 25 * 1024 * 1024  # 25MB

# ============== Models ==============

class JobContext(BaseModel):
    company_name: str = ""
    job_title: str = ""
    job_description: str = ""

class QuestionInput(BaseModel):
    question: str
    question_type: str = "behavioral"  # behavioral, technical, situational, company-fit
    recording_transcript: Optional[str] = None  # User's voice recording transcript

class QAPracticeRequest(BaseModel):
    job_context: JobContext
    questions: List[QuestionInput]
    resume_text: Optional[str] = None
    include_skill_analysis: bool = True

class SingleQuestionRequest(BaseModel):
    question: str
    question_type: str = "behavioral"
    job_context: JobContext
    resume_text: Optional[str] = None
    user_answer: Optional[str] = None  # For feedback on user's answer

class BatchQuestionsRequest(BaseModel):
    questions: List[str]
    job_context: JobContext
    resume_text: Optional[str] = None

class VoiceAnswerRequest(BaseModel):
    question: str
    transcript: str
    job_context: JobContext
    resume_text: Optional[str] = None

# ============== Helper Functions ==============

async def analyze_resume_job_match(resume_text: str, job_context: JobContext) -> Dict:
    """Analyze how well resume matches job requirements"""
    if not resume_text or not job_context.job_description:
        return {"match_score": 0, "matches": [], "gaps": [], "transferable_skills": []}
    
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY)
        response = await chat.send_message(
            system_message="""You are an expert career coach and HR specialist. Analyze the candidate's resume against the job requirements.

Return a JSON object with:
{
    "match_score": <0-100>,
    "direct_matches": ["skill1", "skill2"],
    "transferable_skills": [{"skill": "name", "relevance": "how it transfers"}],
    "experience_alignment": ["relevant experience 1", "relevant experience 2"],
    "gaps": ["missing requirement 1", "missing requirement 2"],
    "strengths_to_highlight": ["strength 1", "strength 2"],
    "talking_points": ["point 1", "point 2"]
}""",
            text=f"""RESUME:
{resume_text}

JOB DETAILS:
Company: {job_context.company_name}
Title: {job_context.job_title}
Description: {job_context.job_description}

Analyze the match and identify transferable skills.""",
            json_mode=True
        )
        
        import json
        return json.loads(response)
    except Exception as e:
        logging.error(f"Resume-job match analysis error: {e}")
        return {"match_score": 0, "matches": [], "gaps": [], "transferable_skills": []}

async def generate_ai_answer(question: str, question_type: str, job_context: JobContext, 
                             resume_text: str = None, match_analysis: Dict = None) -> Dict:
    """Generate AI-driven answer for an interview question"""
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY)
        
        context_parts = []
        if job_context.company_name:
            context_parts.append(f"Company: {job_context.company_name}")
        if job_context.job_title:
            context_parts.append(f"Position: {job_context.job_title}")
        if job_context.job_description:
            context_parts.append(f"Job Requirements: {job_context.job_description[:1000]}")
        
        resume_context = ""
        if resume_text:
            resume_context = f"\nCANDIDATE BACKGROUND:\n{resume_text[:2000]}"
        
        match_context = ""
        if match_analysis:
            strengths = match_analysis.get("strengths_to_highlight", [])
            transferable = match_analysis.get("transferable_skills", [])
            if strengths:
                match_context += f"\nKey Strengths: {', '.join(strengths[:5])}"
            if transferable:
                skills = [t.get("skill", t) if isinstance(t, dict) else t for t in transferable[:5]]
                match_context += f"\nTransferable Skills: {', '.join(skills)}"
        
        response = await chat.send_message(
            system_message=f"""You are an expert interview coach helping a candidate prepare for a {question_type} interview question.

Generate a comprehensive, personalized answer that:
1. Directly addresses the question
2. Incorporates the candidate's actual experience and skills
3. Aligns with the company and role requirements
4. Uses the STAR method for behavioral questions
5. Is specific and includes metrics where possible
6. Sounds natural and authentic, not scripted

Return a JSON object:
{{
    "suggested_answer": "<comprehensive answer>",
    "key_points": ["point 1", "point 2", "point 3"],
    "skills_demonstrated": ["skill 1", "skill 2"],
    "follow_up_tips": ["tip 1", "tip 2"],
    "what_to_avoid": ["pitfall 1", "pitfall 2"],
    "confidence_level": "high/medium/low based on resume match"
}}""",
            text=f"""INTERVIEW QUESTION ({question_type}):
{question}

JOB CONTEXT:
{chr(10).join(context_parts)}
{resume_context}
{match_context}

Generate a tailored answer for this specific question.""",
            json_mode=True
        )
        
        import json
        return json.loads(response)
    except Exception as e:
        logging.error(f"AI answer generation error: {e}")
        return {
            "suggested_answer": "Unable to generate answer. Please try again.",
            "key_points": [],
            "skills_demonstrated": [],
            "follow_up_tips": [],
            "what_to_avoid": [],
            "confidence_level": "low"
        }

async def analyze_user_answer(question: str, user_answer: str, job_context: JobContext,
                              resume_text: str = None) -> Dict:
    """Analyze and provide feedback on user's answer"""
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY)
        
        response = await chat.send_message(
            system_message="""You are an expert interview coach providing constructive feedback on a candidate's answer.

Analyze the answer and return a JSON object:
{
    "overall_score": <1-10>,
    "strengths": ["what they did well 1", "what they did well 2"],
    "areas_for_improvement": ["improvement 1", "improvement 2"],
    "missing_elements": ["what should be added"],
    "specific_suggestions": ["concrete suggestion 1", "concrete suggestion 2"],
    "revised_answer": "<improved version of their answer>",
    "delivery_tips": ["tip for how to present this answer"],
    "relevance_to_job": "high/medium/low",
    "authenticity_score": <1-10>,
    "star_method_usage": "excellent/good/needs work/not applicable"
}""",
            text=f"""QUESTION:
{question}

CANDIDATE'S ANSWER:
{user_answer}

JOB CONTEXT:
Company: {job_context.company_name}
Position: {job_context.job_title}
Requirements: {job_context.job_description[:1000] if job_context.job_description else 'Not provided'}

CANDIDATE RESUME:
{resume_text[:1500] if resume_text else 'Not provided'}

Provide detailed, constructive feedback.""",
            json_mode=True
        )
        
        import json
        return json.loads(response)
    except Exception as e:
        logging.error(f"User answer analysis error: {e}")
        return {
            "overall_score": 5,
            "strengths": [],
            "areas_for_improvement": ["Unable to analyze. Please try again."],
            "missing_elements": [],
            "specific_suggestions": [],
            "revised_answer": "",
            "delivery_tips": [],
            "relevance_to_job": "unknown",
            "authenticity_score": 5,
            "star_method_usage": "not applicable"
        }

# ============== Routes ==============

@router.post("/analyze-match")
async def analyze_job_match(job_context: JobContext, request: Request):
    """Analyze resume-job match before Q&A session"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user's resume
    resume = await db.resumes.find_one({"user_id": user.get("user_id")}, {"_id": 0})
    resume_text = resume.get("raw_text", "") if resume else ""
    
    if not resume_text:
        return {
            "match_analysis": None,
            "message": "No resume found. Upload a resume for personalized answers."
        }
    
    match_analysis = await analyze_resume_job_match(resume_text, job_context)
    
    # Store analysis for session
    session_id = str(uuid.uuid4())
    await db.qa_sessions.insert_one({
        "session_id": session_id,
        "user_id": user.get("user_id"),
        "job_context": job_context.dict(),
        "match_analysis": match_analysis,
        "created_at": datetime.now(timezone.utc),
        "questions": []
    })
    
    return {
        "session_id": session_id,
        "match_analysis": match_analysis,
        "ready_for_practice": True
    }

@router.post("/generate-answer")
async def generate_single_answer(req: SingleQuestionRequest, request: Request):
    """Generate AI answer for a single question"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get resume if not provided
    resume_text = req.resume_text
    if not resume_text:
        resume = await db.resumes.find_one({"user_id": user.get("user_id")}, {"_id": 0})
        resume_text = resume.get("raw_text", "") if resume else ""
    
    # Get match analysis
    match_analysis = None
    if resume_text and req.job_context.job_description:
        match_analysis = await analyze_resume_job_match(resume_text, req.job_context)
    
    # Generate answer
    ai_answer = await generate_ai_answer(
        question=req.question,
        question_type=req.question_type,
        job_context=req.job_context,
        resume_text=resume_text,
        match_analysis=match_analysis
    )
    
    # If user provided their answer, also analyze it
    feedback = None
    if req.user_answer:
        feedback = await analyze_user_answer(
            question=req.question,
            user_answer=req.user_answer,
            job_context=req.job_context,
            resume_text=resume_text
        )
    
    # Store in history
    qa_record = {
        "id": str(uuid.uuid4()),
        "user_id": user.get("user_id"),
        "question": req.question,
        "question_type": req.question_type,
        "job_context": req.job_context.dict(),
        "ai_answer": ai_answer,
        "user_answer": req.user_answer,
        "feedback": feedback,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.qa_history.insert_one(qa_record)
    
    return {
        "question": req.question,
        "question_type": req.question_type,
        "ai_answer": ai_answer,
        "match_analysis": match_analysis,
        "user_feedback": feedback,
        "record_id": qa_record["id"]
    }

@router.post("/batch-generate")
async def generate_batch_answers(req: BatchQuestionsRequest, request: Request):
    """Generate AI answers for multiple questions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get resume
    resume_text = req.resume_text
    if not resume_text:
        resume = await db.resumes.find_one({"user_id": user.get("user_id")}, {"_id": 0})
        resume_text = resume.get("raw_text", "") if resume else ""
    
    # Get match analysis once
    match_analysis = None
    if resume_text and req.job_context.job_description:
        match_analysis = await analyze_resume_job_match(resume_text, req.job_context)
    
    # Generate answers for all questions
    results = []
    for question in req.questions[:10]:  # Limit to 10 questions
        ai_answer = await generate_ai_answer(
            question=question,
            question_type="general",
            job_context=req.job_context,
            resume_text=resume_text,
            match_analysis=match_analysis
        )
        results.append({
            "question": question,
            "ai_answer": ai_answer
        })
    
    return {
        "match_analysis": match_analysis,
        "answers": results,
        "total_questions": len(results)
    }

@router.post("/analyze-voice-answer")
async def analyze_voice_answer(req: VoiceAnswerRequest, request: Request):
    """Analyze a voice-recorded answer (transcript provided)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get resume
    resume_text = req.resume_text
    if not resume_text:
        resume = await db.resumes.find_one({"user_id": user.get("user_id")}, {"_id": 0})
        resume_text = resume.get("raw_text", "") if resume else ""
    
    # Analyze the transcribed answer
    feedback = await analyze_user_answer(
        question=req.question,
        user_answer=req.transcript,
        job_context=req.job_context,
        resume_text=resume_text
    )
    
    # Generate ideal answer for comparison
    match_analysis = await analyze_resume_job_match(resume_text, req.job_context) if resume_text else None
    ideal_answer = await generate_ai_answer(
        question=req.question,
        question_type="general",
        job_context=req.job_context,
        resume_text=resume_text,
        match_analysis=match_analysis
    )
    
    # Store recording analysis
    record = {
        "id": str(uuid.uuid4()),
        "user_id": user.get("user_id"),
        "question": req.question,
        "transcript": req.transcript,
        "feedback": feedback,
        "ideal_answer": ideal_answer,
        "job_context": req.job_context.dict(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "type": "voice_recording"
    }
    await db.qa_recordings.insert_one(record)
    
    return {
        "question": req.question,
        "your_answer": req.transcript,
        "feedback": feedback,
        "suggested_answer": ideal_answer,
        "record_id": record["id"]
    }

@router.get("/history")
async def get_qa_history(request: Request, limit: int = 20):
    """Get user's Q&A practice history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    history = await db.qa_history.find(
        {"user_id": user.get("user_id")},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    recordings = await db.qa_recordings.find(
        {"user_id": user.get("user_id")},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {
        "text_answers": history,
        "voice_recordings": recordings,
        "total": len(history) + len(recordings)
    }

@router.post("/common-questions")
async def get_common_questions(job_context: JobContext, request: Request):
    """Generate common interview questions for a specific job"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        chat = LlmChat(api_key=EMERGENT_LLM_KEY)
        
        response = await chat.send_message(
            system_message="""Generate common interview questions for the specified job.

Return a JSON object:
{
    "behavioral_questions": ["question 1", "question 2", "question 3"],
    "technical_questions": ["question 1", "question 2", "question 3"],
    "situational_questions": ["question 1", "question 2"],
    "company_specific_questions": ["question 1", "question 2"],
    "questions_to_ask_interviewer": ["question 1", "question 2"]
}

Generate 3-5 questions per category, tailored to the specific role and company.""",
            text=f"""Generate interview questions for:
Company: {job_context.company_name or 'Not specified'}
Position: {job_context.job_title}
Job Description: {job_context.job_description[:1500] if job_context.job_description else 'Not provided'}""",
            json_mode=True
        )
        
        import json
        questions = json.loads(response)
        
        return {
            "job_context": job_context.dict(),
            "questions": questions
        }
    except Exception as e:
        logging.error(f"Common questions generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate questions")

@router.delete("/history/{record_id}")
async def delete_qa_record(record_id: str, request: Request):
    """Delete a Q&A practice record"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Try to delete from both collections
    result1 = await db.qa_history.delete_one({
        "id": record_id,
        "user_id": user.get("user_id")
    })
    result2 = await db.qa_recordings.delete_one({
        "id": record_id,
        "user_id": user.get("user_id")
    })
    
    if result1.deleted_count == 0 and result2.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {"message": "Record deleted successfully"}


# ============== Audio Transcription Endpoints ==============

@router.post("/transcribe-audio")
async def transcribe_audio_file(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    request: Request = None
):
    """
    Transcribe an uploaded audio file to text using OpenAI Whisper.
    Supports: MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM
    Max size: 25MB
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate file extension
    filename = file.filename.lower()
    file_ext = os.path.splitext(filename)[1]
    if file_ext not in SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported audio format. Supported: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_AUDIO_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is 25MB. Your file: {len(content) / (1024*1024):.1f}MB"
        )
    
    try:
        # Initialize Whisper STT
        stt = OpenAISpeechToText(api_key=EMERGENT_LLM_KEY)
        
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            # Transcribe
            with open(temp_path, "rb") as audio_file:
                transcribe_params = {
                    "file": audio_file,
                    "model": "whisper-1",
                    "response_format": "verbose_json"
                }
                
                # Add language if specified
                if language:
                    transcribe_params["language"] = language
                
                response = await stt.transcribe(**transcribe_params)
            
            # Extract transcript
            transcript_text = response.text if hasattr(response, 'text') else str(response)
            
            # Get duration and segments if available
            duration = getattr(response, 'duration', None)
            segments = []
            if hasattr(response, 'segments'):
                segments = [
                    {
                        "start": seg.start if hasattr(seg, 'start') else seg.get('start'),
                        "end": seg.end if hasattr(seg, 'end') else seg.get('end'),
                        "text": seg.text if hasattr(seg, 'text') else seg.get('text')
                    }
                    for seg in response.segments
                ]
            
            # Store transcription record
            record = {
                "id": str(uuid.uuid4()),
                "user_id": user.get("user_id"),
                "filename": file.filename,
                "transcript": transcript_text,
                "duration": duration,
                "language": language or "auto-detected",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.audio_transcriptions.insert_one(record)
            
            return {
                "success": True,
                "transcript": transcript_text,
                "duration": duration,
                "segments": segments[:20] if segments else [],  # Limit segments
                "record_id": record["id"],
                "detected_language": getattr(response, 'language', language)
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logging.error(f"Audio transcription error: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/transcriptions")
async def get_transcription_history(request: Request, limit: int = 10):
    """Get user's audio transcription history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    transcriptions = await db.audio_transcriptions.find(
        {"user_id": user.get("user_id")},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(length=limit)
    
    return {"transcriptions": transcriptions}

