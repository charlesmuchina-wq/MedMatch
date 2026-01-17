"""
Interview Preparation Routes
Handles: Interview questions, answers, company research, voice/video feedback
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import json

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/interview", tags=["Interview Prep"])

# ============== Models ==============

class InterviewQuestionsRequest(BaseModel):
    job_title: str
    company: str
    job_description: str = ""

class InterviewAnswerRequest(BaseModel):
    question: str
    job_title: str
    company: str

class StarPolishRequest(BaseModel):
    situation: str
    task: str
    action: str
    result: str
    question: str = ""

class CompanyResearchRequest(BaseModel):
    company: str
    job_title: str = ""

class MockFeedbackRequest(BaseModel):
    question: str
    answer: str
    job_title: str
    company: str

class VoiceFeedbackRequest(BaseModel):
    transcript: str
    question: str
    job_title: str
    company: str
    audio_duration_seconds: float = 0

class VideoFrameAnalysisRequest(BaseModel):
    frame_data: str
    question: str
    timestamp_seconds: float = 0

# ============== Interview Questions Routes ==============

@router.post("/generate-questions")
async def generate_interview_questions(request_data: InterviewQuestionsRequest, request: Request):
    """Generate tailored interview questions for a specific job"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    # Get user's resume for context
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach. Generate tailored interview questions based on the job and candidate profile.

Return ONLY valid JSON with this structure:
{
    "behavioral_questions": [
        {"question": "<question>", "tip": "<how to answer>"}
    ],
    "technical_questions": [
        {"question": "<question>", "tip": "<how to answer>"}
    ],
    "situational_questions": [
        {"question": "<question>", "tip": "<how to answer>"}
    ],
    "questions_to_ask": ["<question candidate should ask>"],
    "key_topics": ["<topic to prepare>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
JOB: {request_data.job_title} at {request_data.company}
DESCRIPTION: {request_data.job_description[:2000]}
"""
    
    if resume:
        context += f"""
CANDIDATE SKILLS: {', '.join(resume.get('skills', [])[:20])}
EXPERIENCE: {resume.get('summary', '')}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"{context}\n\nGenerate 5 questions per category."))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        questions = json.loads(clean_response)
        
        # Cache the questions
        cache_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "job_title": request_data.job_title,
            "company": request_data.company,
            "questions": questions,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.interview_questions.insert_one(cache_doc)
        
        return questions
        
    except Exception as e:
        logging.error(f"Interview questions error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate questions")

@router.get("/cached-questions")
async def get_cached_questions(request: Request):
    """Get previously generated interview questions"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    questions = await db.interview_questions.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return questions

@router.post("/generate-answer")
async def generate_interview_answer(request_data: InterviewAnswerRequest, request: Request):
    """Generate a sample answer for an interview question"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an interview coach helping candidates prepare answers.

Return ONLY valid JSON with this structure:
{
    "sample_answer": "<complete answer using STAR method if applicable>",
    "key_points": ["<point to emphasize>"],
    "what_to_avoid": ["<common mistake>"],
    "follow_up_questions": ["<potential follow-up>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"Question: {request_data.question}\nJob: {request_data.job_title} at {request_data.company}"
    
    if resume:
        context += f"\nCandidate skills: {', '.join(resume.get('skills', [])[:15])}"
        context += f"\nExperience: {resume.get('summary', '')[:500]}"
    
    try:
        response = await chat.send_message(UserMessage(text=context))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"Answer generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate answer")

@router.post("/polish-star")
async def polish_star_answer(request_data: StarPolishRequest, request: Request):
    """Polish a STAR method answer"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach specializing in the STAR method.

Return ONLY valid JSON:
{
    "polished_answer": "<complete polished answer>",
    "improvements": ["<what was improved>"],
    "strength_score": <1-10>,
    "tips": ["<additional tip>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
Situation: {request_data.situation}
Task: {request_data.task}
Action: {request_data.action}
Result: {request_data.result}
Question context: {request_data.question}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Polish this STAR answer:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"STAR polish error: {e}")
        raise HTTPException(status_code=500, detail="Failed to polish answer")

@router.post("/research-company")
async def research_company(request_data: CompanyResearchRequest, request: Request):
    """Get company research for interview preparation"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a company research specialist helping with interview prep.

Return ONLY valid JSON:
{
    "company_overview": "<brief overview>",
    "culture_values": ["<value>"],
    "recent_news": ["<recent development>"],
    "interview_tips": ["<company-specific tip>"],
    "questions_to_ask": ["<thoughtful question about company>"],
    "potential_challenges": ["<challenge the company faces>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    try:
        response = await chat.send_message(UserMessage(
            text=f"Research {request_data.company} for a {request_data.job_title} interview."
        ))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"Company research error: {e}")
        raise HTTPException(status_code=500, detail="Failed to research company")

@router.post("/mock-feedback")
async def get_mock_interview_feedback(request_data: MockFeedbackRequest, request: Request):
    """Get AI feedback on a mock interview answer"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert interview coach providing constructive feedback.

Return ONLY valid JSON:
{
    "overall_score": <1-10>,
    "strengths": ["<strength>"],
    "areas_to_improve": ["<area>"],
    "specific_feedback": "<detailed feedback>",
    "improved_version": "<how to improve the answer>",
    "confidence_indicators": ["<what shows confidence>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
Question: {request_data.question}
Candidate's Answer: {request_data.answer}
Position: {request_data.job_title} at {request_data.company}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Provide feedback:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Save feedback
        feedback_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "type": "mock",
            "question": request_data.question,
            "answer": request_data.answer,
            "feedback": result,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.interview_feedback.insert_one(feedback_doc)
        
        return result
        
    except Exception as e:
        logging.error(f"Mock feedback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate feedback")

@router.post("/voice-feedback")
async def get_voice_interview_feedback(request_data: VoiceFeedbackRequest, request: Request):
    """Get AI feedback on a voice interview recording"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a voice interview coach analyzing speech patterns.

Return ONLY valid JSON:
{
    "overall_score": <1-10>,
    "content_score": <1-10>,
    "clarity_score": <1-10>,
    "pace_analysis": "<too fast/good/too slow>",
    "filler_words_detected": ["<um>", "<like>"],
    "strengths": ["<strength>"],
    "improvements": ["<improvement>"],
    "specific_feedback": "<detailed feedback>",
    "recommended_duration": "<optimal duration for this type of answer>"
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
Question: {request_data.question}
Transcript: {request_data.transcript}
Duration: {request_data.audio_duration_seconds} seconds
Position: {request_data.job_title} at {request_data.company}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Analyze this voice response:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Save feedback
        feedback_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "type": "voice",
            "question": request_data.question,
            "transcript": request_data.transcript,
            "duration": request_data.audio_duration_seconds,
            "feedback": result,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.interview_feedback.insert_one(feedback_doc)
        
        return result
        
    except Exception as e:
        logging.error(f"Voice feedback error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze voice response")

@router.post("/video-feedback")
async def analyze_video_recording(request_data: Dict[str, Any], request: Request):
    """Analyze a video interview recording"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a video interview coach analyzing presentation skills.

Return ONLY valid JSON:
{
    "overall_score": <1-10>,
    "content_analysis": {
        "score": <1-10>,
        "feedback": "<feedback>"
    },
    "presentation_analysis": {
        "eye_contact": "<feedback>",
        "posture": "<feedback>",
        "energy_level": "<feedback>"
    },
    "strengths": ["<strength>"],
    "improvements": ["<improvement>"],
    "body_language_tips": ["<tip>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
Question: {request_data.get('question', '')}
Transcript: {request_data.get('transcript', '')}
Duration: {request_data.get('duration', 0)} seconds
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Analyze this video interview:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Save recording
        recording_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "question": request_data.get('question', ''),
            "transcript": request_data.get('transcript', ''),
            "analysis": result,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.video_recordings.insert_one(recording_doc)
        
        return {"recording_id": recording_doc["id"], "analysis": result}
        
    except Exception as e:
        logging.error(f"Video analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze video")

@router.get("/video-recordings")
async def get_video_recordings(request: Request):
    """Get user's video recordings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    recordings = await db.video_recordings.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    return recordings

@router.delete("/video-recordings/{recording_id}")
async def delete_video_recording(recording_id: str, request: Request):
    """Delete a video recording"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.video_recordings.delete_one({
        "id": recording_id,
        "user_id": user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    return {"message": "Recording deleted"}

@router.post("/analyze-video-frame")
async def analyze_video_frame(request_data: VideoFrameAnalysisRequest, request: Request):
    """Analyze a single video frame for body language"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # For now, return simulated analysis
    # In production, this would use computer vision
    return {
        "timestamp": request_data.timestamp_seconds,
        "posture": "good",
        "eye_contact": "direct",
        "facial_expression": "engaged",
        "confidence_score": 7.5,
        "tips": ["Maintain eye contact with camera", "Relax your shoulders"]
    }
