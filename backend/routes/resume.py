"""
Resume Routes
Handles: Resume upload, parsing, profiles, skills management
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import io

from PyPDF2 import PdfReader
from docx import Document as DocxDocument
from emergentintegrations.llm.chat import LlmChat, UserMessage

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(tags=["Resume"])

# ============== Models ==============

class ResumeData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str = ""
    email: str = ""
    phone: str = ""
    skills: List[str] = []
    experience: List[Dict[str, Any]] = []
    education: List[Dict[str, Any]] = []
    summary: str = ""
    raw_text: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ResumeProfile(BaseModel):
    name: str
    is_default: bool = False

class SkillsUpdate(BaseModel):
    skills: List[str]

# ============== Helper Functions ==============

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = DocxDocument(io.BytesIO(file_content))
        text_content = []
        for para in doc.paragraphs:
            text_content.append(para.text)
        return "\n".join(text_content)
    except Exception as e:
        logging.error(f"Error extracting text from DOCX: {e}")
        return ""

# ============== Routes ==============

@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...), request: Request = None):
    """Upload and parse a resume (PDF, DOC, DOCX)"""
    filename_lower = file.filename.lower()
    valid_extensions = ['.pdf', '.doc', '.docx']
    
    if not any(filename_lower.endswith(ext) for ext in valid_extensions):
        raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are supported")
    
    content = await file.read()
    
    # Extract text based on file type
    if filename_lower.endswith('.pdf'):
        raw_text = extract_text_from_pdf(content)
    elif filename_lower.endswith('.docx'):
        raw_text = extract_text_from_docx(content)
    elif filename_lower.endswith('.doc'):
        # .doc files (old Word format) are harder to parse without external tools
        # For now, show a helpful message
        raise HTTPException(
            status_code=400, 
            detail="Legacy .doc format is not supported. Please save your document as .docx or PDF and try again."
        )
    
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    
    # Parse with AI
    resume_data = await parse_resume_with_ai(raw_text)
    
    # Get user if authenticated
    user = None
    if request:
        user = await get_current_user(request)
    
    # Save to database
    resume_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"] if user else None,
        **resume_data,
        "raw_text": raw_text,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if user:
        # Update existing or insert new
        await db.resumes.update_one(
            {"user_id": user["user_id"]},
            {"$set": resume_doc},
            upsert=True
        )
    else:
        await db.resumes.insert_one(resume_doc)
    
    return {"message": "Resume uploaded successfully", "resume": {k: v for k, v in resume_doc.items() if k != "_id"}}

@router.get("/resume")
async def get_resume(request: Request):
    """Get current user's resume"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if not resume:
        return None
    
    return resume

@router.put("/resume/skills")
async def update_skills(skills_update: SkillsUpdate, request: Request):
    """Update resume skills"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.resumes.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"skills": skills_update.skills, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {"message": "Skills updated"}

# ============== Resume Profiles ==============

@router.get("/resume/profiles")
async def get_resume_profiles(request: Request):
    """Get all resume profiles for user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profiles = await db.resume_profiles.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(20)
    
    return profiles

@router.post("/resume/profiles")
async def create_resume_profile(profile: ResumeProfile, request: Request):
    """Create a new resume profile"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    profile_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "name": profile.name,
        "is_default": profile.is_default,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    if profile.is_default:
        await db.resume_profiles.update_many(
            {"user_id": user["user_id"]},
            {"$set": {"is_default": False}}
        )
    
    await db.resume_profiles.insert_one(profile_doc)
    return {"message": "Profile created", "profile": profile_doc}

@router.put("/resume/profiles/{profile_id}")
async def update_resume_profile(profile_id: str, updates: Dict[str, Any], request: Request):
    """Update a resume profile"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.resume_profiles.update_one(
        {"id": profile_id, "user_id": user["user_id"]},
        {"$set": updates}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Profile updated"}

@router.delete("/resume/profiles/{profile_id}")
async def delete_resume_profile(profile_id: str, request: Request):
    """Delete a resume profile"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.resume_profiles.delete_one({"id": profile_id, "user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Profile deleted"}

@router.post("/resume/profiles/{profile_id}/set-default")
async def set_default_profile(profile_id: str, request: Request):
    """Set a profile as default"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await db.resume_profiles.update_many(
        {"user_id": user["user_id"]},
        {"$set": {"is_default": False}}
    )
    
    result = await db.resume_profiles.update_one(
        {"id": profile_id, "user_id": user["user_id"]},
        {"$set": {"is_default": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return {"message": "Default profile set"}

@router.post("/resume/profiles/upload")
async def upload_resume_to_profile(file: UploadFile = File(...), profile_name: str = "Default", request: Request = None):
    """Upload resume to a specific profile (PDF, DOC, DOCX)"""
    user = None
    if request:
        user = await get_current_user(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    filename_lower = file.filename.lower()
    valid_extensions = ['.pdf', '.doc', '.docx']
    
    if not any(filename_lower.endswith(ext) for ext in valid_extensions):
        raise HTTPException(status_code=400, detail="Only PDF, DOC, and DOCX files are supported")
    
    content = await file.read()
    
    # Extract text based on file type
    if filename_lower.endswith('.pdf'):
        raw_text = extract_text_from_pdf(content)
    elif filename_lower.endswith('.docx'):
        raw_text = extract_text_from_docx(content)
    elif filename_lower.endswith('.doc'):
        raise HTTPException(
            status_code=400, 
            detail="Legacy .doc format is not supported. Please save as .docx or PDF."
        )
    
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    
    resume_data = await parse_resume_with_ai(raw_text)
    
    profile_id = str(uuid.uuid4())
    profile_doc = {
        "id": profile_id,
        "user_id": user["user_id"],
        "name": profile_name,
        "resume_data": resume_data,
        "raw_text": raw_text,
        "is_default": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.resume_profiles.insert_one(profile_doc)
    
    return {"message": "Resume uploaded to profile", "profile_id": profile_id, "resume": resume_data}

# ============== Helper Functions ==============

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF content"""
    pdf_reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

async def parse_resume_with_ai(raw_text: str) -> dict:
    """Parse resume text using AI"""
    if not EMERGENT_LLM_KEY:
        # Basic parsing without AI
        return {
            "full_name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": [],
            "education": [],
            "summary": raw_text[:500]
        }
    
    try:
        import json
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message="""You are an expert resume parser. Extract structured information from the resume text.
            
Return ONLY valid JSON with this structure:
{
    "full_name": "<full name>",
    "email": "<email>",
    "phone": "<phone>",
    "skills": ["<skill1>", "<skill2>", ...],
    "experience": [
        {
            "title": "<job title>",
            "company": "<company>",
            "duration": "<duration>",
            "description": "<brief description>"
        }
    ],
    "education": [
        {
            "degree": "<degree>",
            "institution": "<school>",
            "year": "<year>"
        }
    ],
    "summary": "<professional summary in 2-3 sentences>"
}"""
        ).with_model("openai", "gpt-5.2")
        
        response = await chat.send_message(UserMessage(text=f"Parse this resume:\n\n{raw_text[:8000]}"))
        
        # Clean JSON response
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        
        return json.loads(clean_response)
        
    except Exception as e:
        logging.error(f"AI resume parsing error: {e}")
        return {
            "full_name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": [],
            "education": [],
            "summary": raw_text[:500]
        }
