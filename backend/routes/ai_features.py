"""
AI Features Routes
Handles: Cover letter generation, callback prediction, job matching, salary insights
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import json

from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(tags=["AI Features"])

# ============== Models ==============

class CoverLetterRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    job_url: str = ""

class CallbackPredictionRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    job_url: str = ""
    posted_at: str = ""
    location: str = ""

class JobAnalyzeRequest(BaseModel):
    job_title: str
    job_description: str
    company: str

class SalaryInsightsRequest(BaseModel):
    job_title: str
    company: str
    location: str = "Remote"
    experience_years: int = 5

class CoverLetterExportRequest(BaseModel):
    cover_letter: str
    job_title: str
    company: str
    applicant_name: str

class InterviewPrepExportRequest(BaseModel):
    job_title: str
    company: str
    questions: Dict[str, Any]
    applicant_name: str

# ============== Cover Letter Routes ==============

@router.post("/cover-letter/generate")
async def generate_cover_letter(request_data: CoverLetterRequest, request: Request):
    """Generate an AI-powered cover letter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    # Get user's resume
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload your resume first")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert career coach writing compelling cover letters.

Return ONLY valid JSON:
{
    "cover_letter": "<complete professional cover letter>",
    "key_matches": ["<skill/experience that matches job>"],
    "transferable_skills": ["<relevant transferable skill>"],
    "suggestions": ["<tip to improve application>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
JOB DETAILS:
- Title: {request_data.job_title}
- Company: {request_data.company}
- Description: {request_data.job_description[:3000]}

CANDIDATE PROFILE:
- Name: {resume.get('full_name', user.get('name', 'Candidate'))}
- Skills: {', '.join(resume.get('skills', [])[:20])}
- Summary: {resume.get('summary', '')}
- Experience: {json.dumps(resume.get('experience', [])[:3])}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Generate a cover letter:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Save cover letter
        letter_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "job_title": request_data.job_title,
            "company": request_data.company,
            "job_url": request_data.job_url,
            "cover_letter": result.get("cover_letter", ""),
            "key_matches": result.get("key_matches", []),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.cover_letters.insert_one(letter_doc)
        
        return result
        
    except Exception as e:
        logging.error(f"Cover letter generation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate cover letter")

@router.get("/cover-letter/history")
async def get_cover_letter_history(request: Request):
    """Get user's cover letter history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    letters = await db.cover_letters.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    return letters

@router.delete("/cover-letter/{letter_id}")
async def delete_cover_letter(letter_id: str, request: Request):
    """Delete a cover letter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.cover_letters.delete_one({"id": letter_id, "user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cover letter not found")
    
    return {"message": "Cover letter deleted"}

# ============== Callback Prediction Routes ==============

@router.post("/jobs/predict-callback")
async def predict_job_callback(request_data: CallbackPredictionRequest, request: Request):
    """Predict callback probability for a job application"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload your resume first")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert HR analyst predicting job application success.

Return ONLY valid JSON:
{
    "probability_score": <0-100>,
    "probability_label": "<Very Low|Low|Medium|High|Very High>",
    "factors": {
        "skills_match": <0-100>,
        "experience_match": <0-100>,
        "education_fit": <0-100>,
        "timing": "<good|fair|poor>"
    },
    "recommendations": ["<actionable recommendation>"],
    "competition_estimate": "<low|moderate|high|very high>",
    "timing_advice": "<advice about application timing>",
    "missing_qualifications": ["<missing skill or qualification>"],
    "strongest_qualifications": ["<best matching qualification>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
JOB:
- Title: {request_data.job_title}
- Company: {request_data.company}
- Location: {request_data.location}
- Posted: {request_data.posted_at}
- Description: {request_data.job_description[:3000]}

CANDIDATE:
- Skills: {', '.join(resume.get('skills', [])[:25])}
- Summary: {resume.get('summary', '')}
- Experience: {json.dumps(resume.get('experience', [])[:4])}
- Education: {json.dumps(resume.get('education', [])[:2])}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Predict callback probability:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Save prediction
        prediction_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "job_title": request_data.job_title,
            "company": request_data.company,
            "job_url": request_data.job_url,
            "prediction": result,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.callback_predictions.insert_one(prediction_doc)
        
        return result
        
    except Exception as e:
        logging.error(f"Callback prediction error: {e}")
        raise HTTPException(status_code=500, detail="Failed to predict callback")

@router.get("/jobs/prediction-history")
async def get_prediction_history(request: Request):
    """Get prediction history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    predictions = await db.callback_predictions.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    return predictions

@router.delete("/jobs/prediction-history/{prediction_id}")
async def delete_prediction(prediction_id: str, request: Request):
    """Delete a prediction"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.callback_predictions.delete_one({"id": prediction_id, "user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return {"message": "Prediction deleted"}

@router.post("/jobs/quick-probability")
async def get_quick_probability(request_data: CallbackPredictionRequest, request: Request):
    """Get a quick probability estimate without full analysis"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    # Quick heuristic-based scoring
    score = 50  # Base score
    
    if resume:
        # Check skill matches
        job_text = f"{request_data.job_title} {request_data.job_description}".lower()
        candidate_skills = [s.lower() for s in resume.get("skills", [])]
        
        matches = sum(1 for skill in candidate_skills if skill in job_text)
        score += min(matches * 5, 30)  # Up to 30 points for skill matches
        
        # Experience bonus
        if resume.get("experience"):
            score += 10
    
    # Cap score
    score = min(max(score, 10), 95)
    
    label = "Very Low" if score < 20 else "Low" if score < 40 else "Medium" if score < 60 else "High" if score < 80 else "Very High"
    
    return {
        "probability_score": score,
        "probability_label": label,
        "note": "Quick estimate. Use full prediction for detailed analysis."
    }

# ============== Job Analysis Routes ==============

@router.post("/jobs/analyze")
async def analyze_job(request_data: JobAnalyzeRequest, request: Request):
    """Analyze job posting for insights"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a job market analyst providing insights.

Return ONLY valid JSON:
{
    "match_score": <0-100>,
    "match_analysis": "<brief analysis>",
    "required_skills": ["<skill>"],
    "nice_to_have_skills": ["<skill>"],
    "matched_skills": ["<skill you have>"],
    "skills_to_learn": ["<skill to acquire>"],
    "red_flags": ["<potential concern>"],
    "green_flags": ["<positive indicator>"],
    "salary_estimate": "<estimated range>",
    "application_tips": ["<tip>"]
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
JOB:
- Title: {request_data.job_title}
- Company: {request_data.company}
- Description: {request_data.job_description[:3000]}
"""
    
    if resume:
        context += f"""
CANDIDATE:
- Skills: {', '.join(resume.get('skills', [])[:25])}
- Summary: {resume.get('summary', '')}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Analyze this job:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"Job analysis error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze job")

# ============== Salary Insights Routes ==============

@router.post("/salary/insights")
async def get_salary_insights(request_data: SalaryInsightsRequest, request: Request):
    """Get salary insights and negotiation tips"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a salary negotiation expert and market analyst.

Return ONLY valid JSON:
{
    "salary_range": {
        "low": <number>,
        "median": <number>,
        "high": <number>,
        "currency": "USD"
    },
    "factors_affecting_salary": ["<factor>"],
    "negotiation_tips": ["<tip>"],
    "market_outlook": "<growing|stable|declining>",
    "comparable_titles": ["<similar job title>"],
    "skills_that_increase_pay": ["<skill>"],
    "benefits_to_negotiate": ["<benefit>"],
    "timing_advice": "<when to negotiate>"
}"""
    ).with_model("openai", "gpt-5.2")
    
    context = f"""
Position: {request_data.job_title}
Company: {request_data.company}
Location: {request_data.location}
Experience: {request_data.experience_years} years
"""
    
    try:
        response = await chat.send_message(UserMessage(text=f"Provide salary insights:\n{context}"))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"Salary insights error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get salary insights")

# ============== Export Routes ==============

@router.post("/export/cover-letter-html")
async def export_cover_letter_html(request_data: CoverLetterExportRequest):
    """Export cover letter as HTML for PDF generation"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Georgia', serif; max-width: 700px; margin: 40px auto; padding: 20px; line-height: 1.6; }}
        .header {{ margin-bottom: 30px; }}
        .date {{ color: #666; margin-bottom: 20px; }}
        .content {{ white-space: pre-wrap; }}
        .signature {{ margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <strong>{request_data.applicant_name}</strong>
    </div>
    <div class="date">{datetime.now().strftime('%B %d, %Y')}</div>
    <div class="content">{request_data.cover_letter}</div>
    <div class="signature">
        <p>Sincerely,</p>
        <p><strong>{request_data.applicant_name}</strong></p>
    </div>
</body>
</html>
"""
    return {"html": html, "filename": f"cover_letter_{request_data.company.replace(' ', '_')}.html"}

@router.post("/export/interview-prep-html")
async def export_interview_prep_html(request_data: InterviewPrepExportRequest):
    """Export interview prep as HTML"""
    questions = request_data.questions
    
    questions_html = ""
    for category, q_list in questions.items():
        if isinstance(q_list, list) and q_list:
            questions_html += f"<h3>{category.replace('_', ' ').title()}</h3><ul>"
            for q in q_list:
                if isinstance(q, dict):
                    questions_html += f"<li><strong>{q.get('question', '')}</strong><br><em>Tip: {q.get('tip', '')}</em></li>"
                else:
                    questions_html += f"<li>{q}</li>"
            questions_html += "</ul>"
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Arial', sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
        h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
        h3 {{ color: #1e40af; margin-top: 25px; }}
        ul {{ margin: 15px 0; }}
        li {{ margin: 10px 0; }}
        em {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Interview Preparation</h1>
    <h2>{request_data.job_title} at {request_data.company}</h2>
    <p>Prepared for: {request_data.applicant_name}</p>
    <p>Date: {datetime.now().strftime('%B %d, %Y')}</p>
    {questions_html}
</body>
</html>
"""
    return {"html": html, "filename": f"interview_prep_{request_data.company.replace(' ', '_')}.html"}


# ============== Interview Preparation Routes ==============

class InterviewPrepRequest(BaseModel):
    job_title: str
    company: str = ""
    topics: List[str] = []
    difficulty: str = "medium"  # easy, medium, hard
    num_questions: int = 5
    job_description: str = ""  # Optional job description for tailored questions
    resume_skills: List[str] = []  # Optional resume skills for transferable skill focus

class InterviewAnswerRequest(BaseModel):
    question: str
    answer: str
    job_title: str

@router.post("/interview-prep")
async def generate_interview_questions(request_data: InterviewPrepRequest, request: Request):
    """Generate interview questions and tips for a specific role"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    difficulty_map = {
        "easy": "entry-level, focusing on basic concepts and behavioral questions",
        "medium": "intermediate, mixing technical and behavioral questions",
        "hard": "senior-level, including complex scenarios and system design"
    }
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message=f"""You are an expert interview coach with experience at top companies.
Generate realistic interview questions that are {difficulty_map.get(request_data.difficulty, 'intermediate')}.

Return ONLY valid JSON:
{{
    "questions": [
        {{
            "question": "<interview question>",
            "type": "<Behavioral|Technical|Situational>",
            "tip": "<brief advice on how to approach>",
            "sample_points": ["<key point to cover>"]
        }}
    ],
    "general_tips": ["<overall preparation tip>"],
    "company_research": "<what to research about the company>"
}}"""
    ).with_model("openai", "gpt-4o")
    
    topics_str = ", ".join(request_data.topics) if request_data.topics else "general job-related topics"
    skills_str = ", ".join(request_data.resume_skills[:10]) if request_data.resume_skills else ""
    
    # Build context with optional job description
    context = f"""
Generate {request_data.num_questions} interview questions for:
Position: {request_data.job_title}
Company: {request_data.company or 'A leading company'}
Focus Areas: {topics_str}
Difficulty: {request_data.difficulty}
"""
    
    if request_data.job_description:
        context += f"""
Job Description:
{request_data.job_description[:2000]}
"""
    
    if skills_str:
        context += f"""
Candidate's Transferable Skills: {skills_str}
Generate questions that allow the candidate to highlight these skills.
"""
    
    try:
        response = await chat.send_message(UserMessage(text=context))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        
        # Save interview prep
        prep_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["user_id"],
            "job_title": request_data.job_title,
            "company": request_data.company,
            "difficulty": request_data.difficulty,
            "questions": result.get("questions", []),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.interview_preps.insert_one(prep_doc)
        
        return result
        
    except Exception as e:
        logging.error(f"Interview prep error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate questions")

@router.post("/evaluate-answer")
async def evaluate_interview_answer(request_data: InterviewAnswerRequest, request: Request):
    """Evaluate a user's interview answer and provide feedback"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an experienced interview coach. Evaluate answers using STAR method.

Return ONLY valid JSON:
{
    "score": <1-10>,
    "strengths": ["<what was done well>"],
    "improvements": ["<specific improvement>"],
    "improved_answer": "<suggested better version>",
    "star_analysis": {
        "situation": "<was context provided>",
        "task": "<was the task clear>",
        "action": "<were actions specific>",
        "result": "<were results measurable>"
    }
}"""
    ).with_model("openai", "gpt-4o")
    
    context = f"""
Evaluate this interview answer:
Position: {request_data.job_title}
Question: {request_data.question}
Answer: {request_data.answer}
"""
    
    try:
        response = await chat.send_message(UserMessage(text=context))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"Answer evaluation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate answer")

@router.get("/interview-prep/history")
async def get_interview_prep_history(request: Request):
    """Get interview prep history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    preps = await db.interview_preps.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    return preps

# ============== Voice Coach Routes ==============

class VoiceCoachRequest(BaseModel):
    mode: str  # "practice", "feedback", "tips"
    topic: str = "elevator pitch"
    context: str = ""

@router.post("/voice-coach")
async def voice_coach_session(request_data: VoiceCoachRequest, request: Request):
    """Get voice coaching tips and practice prompts"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    mode_prompts = {
        "practice": f"Create a practice scenario for: {request_data.topic}",
        "feedback": f"Provide feedback based on: {request_data.context}",
        "tips": f"Give top 5 tips for: {request_data.topic}"
    }
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a professional communication coach. Help with speaking skills.

Return ONLY valid JSON:
{
    "coaching": "<main coaching content>",
    "key_points": ["<important point>"],
    "practice_script": "<example script to practice>",
    "body_language_tips": ["<non-verbal tip>"],
    "common_mistakes": ["<mistake to avoid>"]
}"""
    ).with_model("openai", "gpt-4o")
    
    try:
        response = await chat.send_message(UserMessage(text=mode_prompts.get(request_data.mode, mode_prompts["tips"])))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        result = json.loads(clean_response)
        result["mode"] = request_data.mode
        result["topic"] = request_data.topic
        
        return result
        
    except Exception as e:
        logging.error(f"Voice coach error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get coaching")

@router.post("/voice-coach/transcribe")
async def transcribe_speech(request: Request):
    """Transcribe speech using Whisper"""
    
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    # Note: This endpoint needs to be called with multipart form data
    # containing 'audio' file and optional 'context' field
    return {
        "success": True,
        "message": "Use multipart form to upload audio file",
        "supported_formats": ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"],
        "max_size_mb": 25
    }

@router.get("/stt/status")
async def get_stt_status(request: Request):
    """Check Speech-to-Text service status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "available": bool(EMERGENT_LLM_KEY),
        "model": "whisper-1",
        "supported_formats": ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"],
        "max_file_size_mb": 25
    }

# ============== KARAU DRAGON AI Assistant ==============

class AssistantRequest(BaseModel):
    message: str
    context: str = "general"  # job_search, resume, interview, career

@router.post("/assistant")
async def ai_assistant(request_data: AssistantRequest, request: Request):
    """KARAU DRAGON AI Assistant - General job search help"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    context_prompts = {
        "job_search": "helping users find and apply for jobs. You can search the web for job opportunities.",
        "resume": "providing resume writing and improvement advice",
        "interview": "preparing users for job interviews",
        "career": "offering career development guidance",
        "general": "assisting with all aspects of job searching"
    }
    
    # Get user's resume for context
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    resume_context = ""
    user_skills = []
    if resume:
        user_skills = resume.get('skills', [])[:10]
        experience_titles = [exp.get('title', '') for exp in resume.get('experience', [])[:3]]
        resume_context = f"""
User Profile:
- Name: {resume.get('full_name', user.get('name', ''))}
- Skills: {', '.join(str(s) for s in user_skills)}
- Recent Positions: {', '.join(experience_titles)}
- Experience: {len(resume.get('experience', []))} positions
"""
    
    # Check if user is asking for job search - trigger web crawl
    message_lower = request_data.message.lower()
    job_search_triggers = ["find job", "search job", "looking for job", "job opportunities", 
                          "find me", "search for", "open positions", "hiring", "vacancies",
                          "recommend job", "suggest job", "match job"]
    
    should_search_jobs = any(trigger in message_lower for trigger in job_search_triggers)
    
    job_results_context = ""
    if should_search_jobs and request_data.context in ["job_search", "general"]:
        # Extract desired job title from message
        desired_title = request_data.message
        
        # Perform web crawl for jobs
        try:
            from routes.jobs import fetch_remoteok_jobs, fetch_remotive_jobs, fetch_indeed_rss, fetch_dice_jobs
            
            # Build search queries from message and resume
            search_terms = []
            # Extract key terms from user message
            for word in request_data.message.split():
                if len(word) > 3 and word.lower() not in ['find', 'search', 'looking', 'want', 'need', 'jobs', 'job', 'position', 'role']:
                    search_terms.append(word)
            
            # Add skills from resume
            for skill in user_skills[:3]:
                skill_str = skill.get('name', skill) if isinstance(skill, dict) else str(skill)
                if len(skill_str) > 2:
                    search_terms.append(skill_str)
            
            search_query = ' '.join(search_terms[:4]) if search_terms else 'engineer manager developer'
            
            # Search multiple job boards
            tasks = [
                fetch_remoteok_jobs(search_query, ""),
                fetch_remotive_jobs(search_query, ""),
                fetch_indeed_rss(search_query, ""),
                fetch_dice_jobs(search_query, ""),
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            all_jobs = []
            for result in results:
                if isinstance(result, list):
                    all_jobs.extend(result)
            
            # Deduplicate and score
            seen = set()
            unique_jobs = []
            for job in all_jobs:
                url = job.get('url', '')
                if url and url not in seen:
                    seen.add(url)
                    # Calculate relevance score
                    job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
                    matches = sum(1 for term in search_terms if term.lower() in job_text)
                    job['match_score'] = min(95, 40 + matches * 12)
                    unique_jobs.append(job)
            
            # Sort by score and take top results
            unique_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            top_jobs = unique_jobs[:5]
            
            if top_jobs:
                job_results_context = f"""

I found {len(unique_jobs)} jobs matching your criteria. Here are the top matches:
"""
                for i, job in enumerate(top_jobs, 1):
                    job_results_context += f"""
{i}. **{job.get('title', 'Unknown')}** at {job.get('company', 'Unknown Company')}
   - Match Score: {job.get('match_score', 50)}%
   - Location: {job.get('location', 'Not specified')}
   - Source: {job.get('source', 'Web')}
   - Apply: {job.get('url', '#')}
"""
                job_results_context += f"""
Total jobs found: {len(unique_jobs)}. Would you like me to search with different criteria?
"""
        except Exception as e:
            logging.error(f"Job search in Dragon AI error: {e}")
            job_results_context = "\n\nI tried to search for jobs but encountered an issue. Please try the Job Search page."
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"karau-{user['user_id']}",
        system_message=f"""You are KARAU DRAGON, an AI career assistant for MedMatch.
You specialize in {context_prompts.get(request_data.context, context_prompts['general'])}.

Personality: Friendly, encouraging, professional, knowledgeable.
Style: Concise but thorough, practical and actionable.

{resume_context}

When users ask for job recommendations, search results are provided below if available.
Always format job listings clearly with match scores.

Help the user with their career journey."""
    ).with_model("openai", "gpt-4o")
    
    try:
        response = await chat.send_message(UserMessage(text=request_data.message))
        
        # Log conversation
        await db.ai_conversations.insert_one({
            "user_id": user["user_id"],
            "context": request_data.context,
            "user_message": request_data.message,
            "assistant_response": response,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "success": True,
            "response": response,
            "context": request_data.context,
            "assistant": "KARAU DRAGON"
        }
        
    except Exception as e:
        logging.error(f"Assistant error: {e}")
        raise HTTPException(status_code=500, detail="Assistant error")

# ============== Q&A Interview Practice ==============

class QAPracticeRequest(BaseModel):
    question: str
    answer: str
    job_context: str = ""

@router.post("/qa-practice")
async def qa_interview_practice(request_data: QAPracticeRequest, request: Request):
    """Practice Q&A with AI feedback"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an interview practice partner using STAR method.

Return ONLY valid JSON:
{
    "score": <1-10>,
    "feedback": "<overall feedback>",
    "strengths": ["<what was good>"],
    "improvements": ["<what to improve>"],
    "example_answer": "<model answer>",
    "follow_up_questions": ["<potential follow-up>"]
}"""
    ).with_model("openai", "gpt-4o")
    
    context = f"""
Context: {request_data.job_context or 'General job interview'}
Question: {request_data.question}
Answer: {request_data.answer}

Provide detailed feedback."""
    
    try:
        response = await chat.send_message(UserMessage(text=context))
        
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"Q&A practice error: {e}")
        raise HTTPException(status_code=500, detail="Failed to evaluate")

# ============== Text-to-Speech (placeholder) ==============

@router.post("/tts")
async def text_to_speech(request: Request):
    """Convert text to speech (placeholder)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "success": True,
        "message": "Text-to-speech feature coming soon",
        "available": False
    }

# ============== Video Interview Practice (placeholder) ==============

@router.post("/video-interview")
async def video_interview_practice(request: Request):
    """Video interview practice (placeholder)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "success": True,
        "message": "Video interview practice feature coming soon",
        "available": False
    }

# ============== Callback Probability (additional endpoint) ==============

@router.post("/callback-probability")
async def callback_probability(request: Request):
    """Callback probability predictor - redirect to existing endpoint"""
    return {
        "success": True,
        "message": "Use /api/jobs/predict-callback for full analysis or /api/jobs/quick-probability for quick estimate"
    }

