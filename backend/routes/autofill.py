"""
Resume Auto-Fill Routes
Handles: Generate auto-fill data from resume, format for common job application forms
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import uuid
import logging
import json

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/autofill", tags=["Auto-Fill"])

# ============== Models ==============

class AutoFillRequest(BaseModel):
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    custom_fields: Optional[List[str]] = []

class AutoFillField(BaseModel):
    field_name: str
    field_label: str
    value: str
    category: str

# ============== Common Form Fields ==============

COMMON_FORM_FIELDS = {
    "personal": [
        {"name": "full_name", "label": "Full Name", "resume_key": "full_name"},
        {"name": "first_name", "label": "First Name", "resume_key": "full_name", "transform": "first"},
        {"name": "last_name", "label": "Last Name", "resume_key": "full_name", "transform": "last"},
        {"name": "email", "label": "Email Address", "resume_key": "email"},
        {"name": "phone", "label": "Phone Number", "resume_key": "phone"},
        {"name": "location", "label": "Location/City", "resume_key": "location"},
        {"name": "address", "label": "Address", "resume_key": "address"},
        {"name": "linkedin", "label": "LinkedIn URL", "resume_key": "linkedin_url"},
        {"name": "portfolio", "label": "Portfolio/Website", "resume_key": "portfolio_url"},
    ],
    "professional": [
        {"name": "current_title", "label": "Current Job Title", "resume_key": "current_title"},
        {"name": "current_company", "label": "Current Company", "resume_key": "current_company"},
        {"name": "years_experience", "label": "Years of Experience", "resume_key": "years_experience"},
        {"name": "summary", "label": "Professional Summary", "resume_key": "summary"},
        {"name": "headline", "label": "Professional Headline", "resume_key": "headline"},
    ],
    "education": [
        {"name": "highest_degree", "label": "Highest Degree", "resume_key": "education", "transform": "highest_degree"},
        {"name": "university", "label": "University/School", "resume_key": "education", "transform": "institution"},
        {"name": "graduation_year", "label": "Graduation Year", "resume_key": "education", "transform": "year"},
        {"name": "major", "label": "Major/Field of Study", "resume_key": "education", "transform": "major"},
        {"name": "gpa", "label": "GPA", "resume_key": "education", "transform": "gpa"},
    ],
    "skills": [
        {"name": "skills_list", "label": "Skills (comma-separated)", "resume_key": "skills", "transform": "comma_list"},
        {"name": "top_skills", "label": "Top 5 Skills", "resume_key": "skills", "transform": "top_5"},
        {"name": "technical_skills", "label": "Technical Skills", "resume_key": "skills", "transform": "technical"},
        {"name": "languages", "label": "Languages", "resume_key": "languages"},
    ],
    "work_history": [
        {"name": "most_recent_job", "label": "Most Recent Job", "resume_key": "experience", "transform": "recent_title"},
        {"name": "most_recent_company", "label": "Most Recent Company", "resume_key": "experience", "transform": "recent_company"},
        {"name": "most_recent_dates", "label": "Employment Dates", "resume_key": "experience", "transform": "recent_dates"},
        {"name": "work_history_text", "label": "Work History Summary", "resume_key": "experience", "transform": "summary_text"},
    ]
}

# ============== Main Auto-Fill Endpoint ==============

@router.get("/data")
async def get_autofill_data(request: Request):
    """Get all auto-fill data from user's resume"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user's resume
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not resume:
        raise HTTPException(
            status_code=404, 
            detail="No resume found. Please upload your resume first."
        )
    
    # Build auto-fill data
    autofill_data = {}
    
    for category, fields in COMMON_FORM_FIELDS.items():
        autofill_data[category] = []
        for field in fields:
            value = extract_field_value(resume, field)
            if value:
                autofill_data[category].append({
                    "field_name": field["name"],
                    "field_label": field["label"],
                    "value": value
                })
    
    return {
        "autofill_data": autofill_data,
        "resume_name": resume.get("full_name", ""),
        "last_updated": resume.get("updated_at") or resume.get("created_at"),
        "fields_available": sum(len(fields) for fields in autofill_data.values())
    }

def extract_field_value(resume: dict, field: dict) -> Optional[str]:
    """Extract and transform a field value from resume"""
    key = field.get("resume_key")
    transform = field.get("transform")
    value = resume.get(key)
    
    if not value:
        return None
    
    # Apply transformations
    if transform == "first" and isinstance(value, str):
        return value.split()[0] if value else None
    
    elif transform == "last" and isinstance(value, str):
        parts = value.split()
        return parts[-1] if len(parts) > 1 else None
    
    elif transform == "highest_degree" and isinstance(value, list) and len(value) > 0:
        return value[0].get("degree", "")
    
    elif transform == "institution" and isinstance(value, list) and len(value) > 0:
        return value[0].get("institution") or value[0].get("school", "")
    
    elif transform == "year" and isinstance(value, list) and len(value) > 0:
        return value[0].get("year") or value[0].get("graduation_year", "")
    
    elif transform == "major" and isinstance(value, list) and len(value) > 0:
        return value[0].get("major") or value[0].get("field", "")
    
    elif transform == "gpa" and isinstance(value, list) and len(value) > 0:
        return value[0].get("gpa", "")
    
    elif transform == "comma_list" and isinstance(value, list):
        return ", ".join(value[:20])
    
    elif transform == "top_5" and isinstance(value, list):
        return ", ".join(value[:5])
    
    elif transform == "technical" and isinstance(value, list):
        # Filter for common technical skills
        tech_keywords = ["python", "java", "javascript", "react", "sql", "aws", "docker", 
                        "kubernetes", "git", "linux", "node", "angular", "vue", "typescript",
                        "c++", "c#", "ruby", "go", "rust", "swift", "kotlin", "scala",
                        "mongodb", "postgresql", "mysql", "redis", "graphql", "rest", "api"]
        technical = [s for s in value if any(kw in s.lower() for kw in tech_keywords)]
        return ", ".join(technical[:10]) if technical else None
    
    elif transform == "recent_title" and isinstance(value, list) and len(value) > 0:
        return value[0].get("title", "")
    
    elif transform == "recent_company" and isinstance(value, list) and len(value) > 0:
        return value[0].get("company", "")
    
    elif transform == "recent_dates" and isinstance(value, list) and len(value) > 0:
        exp = value[0]
        start = exp.get("start_date") or exp.get("dates", "").split("-")[0].strip()
        end = exp.get("end_date") or (exp.get("dates", "").split("-")[1].strip() if "-" in exp.get("dates", "") else "Present")
        return f"{start} - {end}" if start else None
    
    elif transform == "summary_text" and isinstance(value, list):
        # Generate work history summary
        summaries = []
        for exp in value[:3]:
            title = exp.get("title", "")
            company = exp.get("company", "")
            if title and company:
                summaries.append(f"{title} at {company}")
        return "; ".join(summaries) if summaries else None
    
    # Default: return value as string
    if isinstance(value, list):
        return ", ".join(str(v) for v in value[:10])
    return str(value) if value else None

# ============== Tailored Auto-Fill ==============

@router.post("/tailored")
async def get_tailored_autofill(autofill_request: AutoFillRequest, request: Request):
    """Get auto-fill data tailored to a specific job"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get user's resume
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")
    
    # Get base auto-fill data
    base_data = {}
    for category, fields in COMMON_FORM_FIELDS.items():
        for field in fields:
            value = extract_field_value(resume, field)
            if value:
                base_data[field["name"]] = value
    
    # If job details provided, generate tailored content
    tailored_content = {}
    if autofill_request.job_description and EMERGENT_LLM_KEY:
        tailored_content = await generate_tailored_content(
            resume, 
            autofill_request.job_title,
            autofill_request.company_name,
            autofill_request.job_description
        )
    
    return {
        "base_data": base_data,
        "tailored_content": tailored_content,
        "job_context": {
            "title": autofill_request.job_title,
            "company": autofill_request.company_name
        }
    }

async def generate_tailored_content(resume: dict, job_title: str, company: str, job_description: str) -> dict:
    """Generate AI-tailored content for specific job application"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="""You are an expert career coach helping tailor job application content.
Based on the resume and job description, generate tailored content for common application fields.
Return ONLY valid JSON with these fields:
{
    "tailored_summary": "<2-3 sentence summary highlighting relevant experience for this specific role>",
    "tailored_headline": "<one-line professional headline tailored to this job>",
    "why_interested": "<2-3 sentences explaining genuine interest in this role/company>",
    "relevant_skills": "<comma-separated list of skills most relevant to this job>",
    "key_achievements": "<2-3 bullet points of most relevant achievements>",
    "cover_letter_opener": "<compelling opening paragraph for cover letter>"
}"""
        ).with_model("openai", "gpt-5.2")
        
        context = f"""
CANDIDATE RESUME:
Name: {resume.get('full_name', 'Candidate')}
Summary: {resume.get('summary', '')}
Skills: {', '.join(resume.get('skills', [])[:20])}
Recent Experience: {json.dumps(resume.get('experience', [])[:2])}

JOB DETAILS:
Title: {job_title or 'Not specified'}
Company: {company or 'Not specified'}
Description: {job_description[:2000]}

Generate tailored application content.
"""
        
        response = await chat.send_message(UserMessage(text=context))
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"Failed to generate tailored content: {e}")
        return {}

# ============== Copy-Ready Format ==============

@router.get("/copy-ready")
async def get_copy_ready_data(request: Request, format: str = "plain"):
    """Get auto-fill data in copy-ready format"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")
    
    # Build copy-ready sections
    sections = {
        "contact_info": [],
        "professional_summary": "",
        "skills_text": "",
        "education_text": "",
        "experience_text": ""
    }
    
    # Contact info
    if resume.get("full_name"):
        sections["contact_info"].append(f"Name: {resume['full_name']}")
    if resume.get("email"):
        sections["contact_info"].append(f"Email: {resume['email']}")
    if resume.get("phone"):
        sections["contact_info"].append(f"Phone: {resume['phone']}")
    if resume.get("location"):
        sections["contact_info"].append(f"Location: {resume['location']}")
    
    # Summary
    sections["professional_summary"] = resume.get("summary", "")
    
    # Skills
    skills = resume.get("skills", [])
    sections["skills_text"] = ", ".join(skills[:20]) if skills else ""
    
    # Education
    education_parts = []
    for edu in resume.get("education", [])[:3]:
        degree = edu.get("degree", "")
        institution = edu.get("institution") or edu.get("school", "")
        year = edu.get("year") or edu.get("graduation_year", "")
        if degree or institution:
            education_parts.append(f"{degree} - {institution} ({year})" if year else f"{degree} - {institution}")
    sections["education_text"] = "\n".join(education_parts)
    
    # Experience
    experience_parts = []
    for exp in resume.get("experience", [])[:5]:
        title = exp.get("title", "")
        company = exp.get("company", "")
        dates = exp.get("dates") or exp.get("duration", "")
        description = exp.get("description", "")
        if title or company:
            exp_text = f"{title} at {company}"
            if dates:
                exp_text += f" ({dates})"
            if description:
                exp_text += f"\n{description[:300]}"
            experience_parts.append(exp_text)
    sections["experience_text"] = "\n\n".join(experience_parts)
    
    return {
        "sections": sections,
        "full_text": format_full_text(sections) if format == "full" else None
    }

def format_full_text(sections: dict) -> str:
    """Format all sections into full text"""
    parts = []
    
    if sections.get("contact_info"):
        parts.append("CONTACT INFORMATION\n" + "\n".join(sections["contact_info"]))
    
    if sections.get("professional_summary"):
        parts.append("PROFESSIONAL SUMMARY\n" + sections["professional_summary"])
    
    if sections.get("skills_text"):
        parts.append("SKILLS\n" + sections["skills_text"])
    
    if sections.get("education_text"):
        parts.append("EDUCATION\n" + sections["education_text"])
    
    if sections.get("experience_text"):
        parts.append("EXPERIENCE\n" + sections["experience_text"])
    
    return "\n\n".join(parts)

# ============== Field Suggestions ==============

@router.get("/field-suggestions")
async def get_field_suggestions(request: Request, field_name: str):
    """Get suggestions for a specific field based on resume"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="No resume found")
    
    suggestions = []
    
    # Find the field definition
    for category, fields in COMMON_FORM_FIELDS.items():
        for field in fields:
            if field["name"] == field_name:
                value = extract_field_value(resume, field)
                if value:
                    suggestions.append({"source": "resume", "value": value})
                break
    
    return {
        "field_name": field_name,
        "suggestions": suggestions
    }
