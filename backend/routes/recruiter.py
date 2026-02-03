"""
Recruiter Routes
Handles: Job postings, applicant tracking, candidate search, AI prescreening
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import json
import re

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user
from utils.push_service import notify_application_update

router = APIRouter(prefix="/recruiter", tags=["Recruiter"])

# ============== Models ==============

class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    salary: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = []

class JobApplicationStatus(BaseModel):
    status: str

class ApplicantNote(BaseModel):
    note: str

class CandidateSearchRequest(BaseModel):
    keywords: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    location: Optional[str] = None
    experience_years: Optional[int] = None
    limit: int = 20

class AIPreScreenRequest(BaseModel):
    candidate_id: str
    job_id: str

# ============== Job Posting Routes ==============

@router.post("/jobs")
async def create_job_posting(job: JobPosting, request: Request):
    """Recruiters can post jobs for free"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can post jobs")
    
    job_doc = {
        "id": f"posted_{uuid.uuid4().hex[:12]}",
        "recruiter_id": user["user_id"],
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "salary": job.salary,
        "url": job.url,
        "tags": job.tags,
        "source": "MedMatch",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
        "applicant_count": 0
    }
    
    await db.posted_jobs.insert_one(job_doc)
    return {"message": "Job posted successfully", "job_id": job_doc["id"]}

@router.get("/jobs")
async def get_recruiter_jobs(request: Request):
    """Get jobs posted by current recruiter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view posted jobs")
    
    jobs = await db.posted_jobs.find(
        {"recruiter_id": user["user_id"]},
        {"_id": 0}
    ).to_list(100)
    
    return jobs

@router.put("/jobs/{job_id}")
async def update_job_posting(job_id: str, job: JobPosting, request: Request):
    """Update a job posting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can update jobs")
    
    result = await db.posted_jobs.update_one(
        {"id": job_id, "recruiter_id": user["user_id"]},
        {"$set": {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "salary": job.salary,
            "url": job.url,
            "tags": job.tags,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Job not found or not authorized")
    
    return {"message": "Job updated successfully"}

@router.delete("/jobs/{job_id}")
async def delete_job_posting(job_id: str, request: Request):
    """Delete a job posting"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.posted_jobs.delete_one({
        "id": job_id,
        "recruiter_id": user["user_id"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted"}

# ============== Applicant Tracking Routes ==============

@router.get("/jobs/{job_id}/applicants")
async def get_job_applicants(job_id: str, request: Request):
    """Recruiter views all applicants for a specific job"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view applicants")
    
    # Verify the job belongs to this recruiter
    job = await db.posted_jobs.find_one({
        "id": job_id,
        "recruiter_id": user["user_id"]
    })
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get all applicants for this job
    applicants = await db.job_applicants.find(
        {"job_id": job_id},
        {"_id": 0}
    ).sort("applied_at", -1).to_list(500)
    
    return {
        "job": {
            "id": job["id"],
            "title": job["title"],
            "company": job["company"]
        },
        "applicants": applicants,
        "total_count": len(applicants)
    }

@router.put("/applicants/{application_id}/status")
async def update_applicant_status(
    application_id: str, 
    status_update: JobApplicationStatus, 
    request: Request,
    background_tasks: BackgroundTasks
):
    """Recruiter updates an applicant's status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can update applicant status")
    
    valid_statuses = ["new", "reviewing", "shortlisted", "interviewing", "offered", "rejected", "hired"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    # Get the application first to send notification
    application = await db.job_applicants.find_one(
        {"id": application_id, "recruiter_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    result = await db.job_applicants.update_one(
        {"id": application_id, "recruiter_id": user["user_id"]},
        {"$set": {
            "status": status_update.status,
            "status_updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Get job details for notification
    job = await db.posted_jobs.find_one({"id": application.get("job_id")}, {"_id": 0})
    company_name = job.get("company", "Company") if job else "Company"
    
    # Send push notification to applicant in background
    if application.get("user_id"):
        # Map internal status to user-friendly status
        status_map = {
            "reviewing": "Viewed",
            "shortlisted": "Shortlisted",
            "interviewing": "Interview",
            "offered": "Offer",
            "rejected": "Rejected",
            "hired": "Hired"
        }
        friendly_status = status_map.get(status_update.status, status_update.status.title())
        
        background_tasks.add_task(
            notify_application_update,
            user_id=application["user_id"],
            company=company_name,
            status=friendly_status,
            application_id=application_id
        )
    
    return {"message": f"Status updated to {status_update.status}"}

@router.post("/applicants/{application_id}/notes")
async def add_applicant_note(application_id: str, note_data: ApplicantNote, request: Request):
    """Recruiter adds a note to an applicant"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can add notes")
    
    note = {
        "id": f"note_{uuid.uuid4().hex[:8]}",
        "text": note_data.note,
        "created_by": user.get("name", user["email"]),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.job_applicants.update_one(
        {"id": application_id, "recruiter_id": user["user_id"]},
        {"$push": {"notes": note}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": "Note added", "note": note}

@router.get("/dashboard/stats")
async def get_recruiter_dashboard_stats(request: Request):
    """Get recruiter dashboard statistics"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view dashboard")
    
    # Get job counts
    total_jobs = await db.posted_jobs.count_documents({"recruiter_id": user["user_id"]})
    active_jobs = await db.posted_jobs.count_documents({"recruiter_id": user["user_id"], "status": "active"})
    
    # Get applicant counts by status
    pipeline = [
        {"$match": {"recruiter_id": user["user_id"]}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_counts = await db.job_applicants.aggregate(pipeline).to_list(100)
    
    applicant_stats = {item["_id"]: item["count"] for item in status_counts}
    total_applicants = sum(applicant_stats.values())
    
    # Get recent applicants
    recent_applicants = await db.job_applicants.find(
        {"recruiter_id": user["user_id"]},
        {"_id": 0}
    ).sort("applied_at", -1).limit(5).to_list(5)
    
    return {
        "jobs": {
            "total": total_jobs,
            "active": active_jobs
        },
        "applicants": {
            "total": total_applicants,
            "by_status": applicant_stats,
            "recent": recent_applicants
        }
    }

# ============== Candidate Search Routes ==============

@router.post("/candidates/search")
async def search_candidates(search: CandidateSearchRequest, request: Request):
    """Recruiter searches for candidates based on skills, keywords, location"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can search candidates")
    
    # Build search query
    query = {"searchable": {"$ne": False}}
    
    if search.skills:
        query["skills"] = {"$in": [re.compile(skill, re.IGNORECASE) for skill in search.skills]}
    
    if search.keywords:
        keyword_regex = "|".join(search.keywords)
        query["$or"] = [
            {"summary": {"$regex": keyword_regex, "$options": "i"}},
            {"raw_text": {"$regex": keyword_regex, "$options": "i"}},
            {"full_name": {"$regex": keyword_regex, "$options": "i"}}
        ]
    
    # Get matching resumes
    candidates = await db.resumes.find(
        query,
        {"_id": 0, "raw_text": 0}
    ).limit(search.limit).to_list(search.limit)
    
    # Calculate relevance score for each candidate
    results = []
    for candidate in candidates:
        score = 0
        matched_skills = []
        
        candidate_skills = [s.lower() for s in candidate.get("skills", [])]
        
        for skill in search.skills or []:
            if any(skill.lower() in cs for cs in candidate_skills):
                score += 10
                matched_skills.append(skill)
        
        for keyword in search.keywords or []:
            if keyword.lower() in candidate.get("summary", "").lower():
                score += 5
        
        results.append({
            "id": candidate.get("id"),
            "full_name": candidate.get("full_name", "Anonymous"),
            "email": candidate.get("email", ""),
            "skills": candidate.get("skills", [])[:15],
            "summary": candidate.get("summary", "")[:300],
            "experience": candidate.get("experience", [])[:3],
            "relevance_score": score,
            "matched_skills": matched_skills
        })
    
    # Sort by relevance score
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "candidates": results,
        "total_found": len(results),
        "search_criteria": {
            "skills": search.skills,
            "keywords": search.keywords
        }
    }

@router.get("/candidates/{candidate_id}")
async def get_candidate_profile(candidate_id: str, request: Request):
    """Recruiter views a specific candidate's full profile"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can view candidates")
    
    candidate = await db.resumes.find_one(
        {"id": candidate_id},
        {"_id": 0, "raw_text": 0}
    )
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate

# ============== AI Prescreening Routes ==============

@router.post("/ai-prescreen")
async def ai_prescreen_candidate(prescreen: AIPreScreenRequest, request: Request):
    """AI-powered candidate prescreening based on resume vs job requirements"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can use AI prescreening")
    
    # Get candidate resume
    candidate = await db.resumes.find_one({"id": prescreen.candidate_id}, {"_id": 0})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Get job posting
    job = await db.posted_jobs.find_one({"id": prescreen.job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="AI features not configured")
    
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    
    # AI prescreening analysis
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert HR recruiter and talent acquisition specialist. Analyze the candidate's resume against the job requirements and provide a comprehensive prescreening assessment.

Return ONLY valid JSON with this structure:
{
    "overall_score": <0-100>,
    "recommendation": "<Strong Match|Good Match|Potential Match|Weak Match|Not Recommended>",
    "summary": "<2-3 sentence executive summary>",
    "skills_analysis": {
        "matched_skills": ["<skill1>", "<skill2>"],
        "missing_skills": ["<skill1>", "<skill2>"],
        "transferable_skills": ["<skill1 - how it transfers>", "<skill2 - how it transfers>"],
        "skills_score": <0-100>
    },
    "experience_analysis": {
        "relevant_experience": ["<experience1>", "<experience2>"],
        "experience_gaps": ["<gap1>"],
        "years_relevant": <number>,
        "experience_score": <0-100>
    },
    "education_fit": {
        "meets_requirements": <true/false>,
        "relevant_education": ["<degree/cert>"],
        "education_score": <0-100>
    },
    "culture_indicators": {
        "strengths": ["<strength1>", "<strength2>"],
        "potential_concerns": ["<concern1>"]
    },
    "interview_questions": [
        "<suggested question 1>",
        "<suggested question 2>",
        "<suggested question 3>"
    ],
    "red_flags": ["<any concerns>"],
    "green_flags": ["<positive indicators>"],
    "salary_expectation_fit": "<likely fit / may be overqualified / may be underqualified / unknown>"
}"""
    ).with_model("openai", "gpt-5.2")
    
    # Build context
    candidate_context = f"""
CANDIDATE PROFILE:
Name: {candidate.get('full_name', 'Unknown')}

SKILLS:
{', '.join(candidate.get('skills', [])[:30])}

PROFESSIONAL SUMMARY:
{candidate.get('summary', 'Not provided')}

EXPERIENCE:
"""
    for exp in candidate.get('experience', [])[:5]:
        candidate_context += f"- {exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')})\n  {exp.get('description', '')[:200]}\n"
    
    candidate_context += "\nEDUCATION:\n"
    for edu in candidate.get('education', [])[:3]:
        candidate_context += f"- {edu.get('degree', '')} from {edu.get('institution', '')} ({edu.get('year', '')})\n"
    
    job_context = f"""
JOB REQUIREMENTS:
Title: {job.get('title', '')}
Company: {job.get('company', '')}
Location: {job.get('location', '')}
Salary: {job.get('salary', 'Not specified')}

DESCRIPTION:
{job.get('description', '')[:3000]}

REQUIRED TAGS/SKILLS:
{', '.join(job.get('tags', []))}
"""
    
    user_message = UserMessage(
        text=f"{candidate_context}\n\n{job_context}\n\nProvide a comprehensive prescreening assessment."
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        analysis = json.loads(clean_response)
        
        # Store the analysis
        await db.job_applicants.update_one(
            {"job_id": prescreen.job_id, "applicant_id": candidate.get("user_id")},
            {"$set": {"ai_analysis": analysis, "ai_analyzed_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {
            "candidate_name": candidate.get('full_name', 'Unknown'),
            "job_title": job.get('title', ''),
            "analysis": analysis
        }
        
    except Exception as e:
        logging.error(f"AI prescreening error: {e}")
        raise HTTPException(status_code=500, detail="AI analysis failed")
