"""
AI Features Routes
Handles: Cover letter generation, callback prediction, job matching, salary insights
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
