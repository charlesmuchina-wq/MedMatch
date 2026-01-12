from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import asyncio
from PyPDF2 import PdfReader
import io
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Define Models
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

class Job(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    company: str
    location: str = "Remote"
    description: str = ""
    url: str = ""
    salary: str = ""
    tags: List[str] = []
    source: str = ""
    posted_at: Optional[str] = None
    match_score: Optional[int] = None
    match_analysis: Optional[str] = None

class SavedJob(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job: Job
    saved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""

class Application(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job: Job
    status: str = "Applied"  # Applied, Interview, Offer, Rejected
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""

class SkillsUpdate(BaseModel):
    skills: List[str]

class ApplicationCreate(BaseModel):
    job: Job
    notes: str = ""

class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class JobAnalyzeRequest(BaseModel):
    job_title: str
    job_description: str
    company: str

class ManualJobCreate(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    description: str
    url: str = ""
    salary: str = ""
    tags: List[str] = []

# Helper function to extract text from PDF
def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# AI-powered resume parsing
async def parse_resume_with_ai(raw_text: str) -> dict:
    if not EMERGENT_LLM_KEY:
        return {"error": "LLM key not configured"}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are an expert resume parser. Extract information from the resume and return a JSON object with these fields:
        - full_name: string
        - email: string
        - phone: string
        - skills: array of strings (technical skills, certifications, tools)
        - experience: array of objects with {title, company, duration, description}
        - education: array of objects with {degree, institution, year}
        - summary: brief professional summary (2-3 sentences)
        
        Return ONLY valid JSON, no markdown or extra text."""
    ).with_model("openai", "gpt-5.2")
    
    user_message = UserMessage(text=f"Parse this resume:\n\n{raw_text[:8000]}")
    response = await chat.send_message(user_message)
    
    try:
        import json
        # Clean response - remove markdown code blocks if present
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except:
        return {
            "full_name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": [],
            "education": [],
            "summary": raw_text[:500]
        }

# AI-powered job matching
async def analyze_job_match(resume_data: dict, job: dict) -> dict:
    if not EMERGENT_LLM_KEY:
        return {"match_score": 50, "analysis": "AI analysis unavailable"}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a job matching expert. Analyze how well a candidate's resume matches a job posting.
        Return a JSON object with:
        - match_score: number 0-100
        - analysis: string with 2-3 sentences explaining the match, highlighting strengths and gaps
        
        Return ONLY valid JSON, no markdown."""
    ).with_model("openai", "gpt-5.2")
    
    resume_summary = f"""
    Skills: {', '.join(resume_data.get('skills', [])[:20])}
    Experience: {resume_data.get('summary', '')}
    """
    
    job_summary = f"""
    Title: {job.get('title', '')}
    Company: {job.get('company', '')}
    Description: {job.get('description', '')[:2000]}
    """
    
    user_message = UserMessage(
        text=f"Resume:\n{resume_summary}\n\nJob Posting:\n{job_summary}\n\nAnalyze the match."
    )
    response = await chat.send_message(user_message)
    
    try:
        import json
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except:
        return {"match_score": 50, "analysis": "Unable to analyze match"}

# Fetch jobs from RemoteOK API
async def fetch_remoteok_jobs(query: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"User-Agent": "MedMatch/1.0"}
            response = await client.get("https://remoteok.com/api", headers=headers)
            if response.status_code == 200:
                jobs = response.json()
                # Skip first item (legal notice)
                jobs = jobs[1:] if len(jobs) > 1 else []
                
                result = []
                for job in jobs[:50]:
                    if query.lower() in job.get('position', '').lower() or \
                       query.lower() in job.get('company', '').lower() or \
                       query.lower() in ' '.join(job.get('tags', [])).lower() or \
                       not query:
                        result.append({
                            "id": str(job.get('id', uuid.uuid4())),
                            "title": job.get('position', 'Unknown'),
                            "company": job.get('company', 'Unknown'),
                            "location": job.get('location', 'Remote'),
                            "description": job.get('description', ''),
                            "url": job.get('url', ''),
                            "salary": job.get('salary', ''),
                            "tags": job.get('tags', []),
                            "source": "RemoteOK",
                            "posted_at": job.get('date', '')
                        })
                return result
    except Exception as e:
        logging.error(f"RemoteOK API error: {e}")
    return []

# Fetch jobs from Remotive API
async def fetch_remotive_jobs(query: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            params = {"search": query} if query else {}
            response = await client.get("https://remotive.com/api/remote-jobs", params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])[:50]
                
                result = []
                for job in jobs:
                    result.append({
                        "id": str(job.get('id', uuid.uuid4())),
                        "title": job.get('title', 'Unknown'),
                        "company": job.get('company_name', 'Unknown'),
                        "location": job.get('candidate_required_location', 'Remote'),
                        "description": job.get('description', ''),
                        "url": job.get('url', ''),
                        "salary": job.get('salary', ''),
                        "tags": job.get('tags', []) or [job.get('category', '')],
                        "source": "Remotive",
                        "posted_at": job.get('publication_date', '')
                    })
                return result
    except Exception as e:
        logging.error(f"Remotive API error: {e}")
    return []


# Routes
@api_router.get("/")
async def root():
    return {"message": "MedMatch API - Remote Job Finder"}

# Resume endpoints
@api_router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    content = await file.read()
    raw_text = extract_text_from_pdf(content)
    
    # Parse with AI
    parsed_data = await parse_resume_with_ai(raw_text)
    
    resume = ResumeData(
        full_name=parsed_data.get('full_name', ''),
        email=parsed_data.get('email', ''),
        phone=parsed_data.get('phone', ''),
        skills=parsed_data.get('skills', []),
        experience=parsed_data.get('experience', []),
        education=parsed_data.get('education', []),
        summary=parsed_data.get('summary', ''),
        raw_text=raw_text
    )
    
    # Save to DB (upsert - one resume per user for simplicity)
    doc = resume.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.resumes.delete_many({})  # Clear existing
    await db.resumes.insert_one(doc)
    
    return resume

@api_router.get("/resume")
async def get_resume():
    doc = await db.resumes.find_one({}, {"_id": 0})
    if not doc:
        return None
    if isinstance(doc.get('created_at'), str):
        doc['created_at'] = datetime.fromisoformat(doc['created_at'])
    if isinstance(doc.get('updated_at'), str):
        doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
    return doc

@api_router.put("/resume/skills")
async def update_skills(data: SkillsUpdate):
    result = await db.resumes.update_one(
        {},
        {"$set": {"skills": data.skills, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"message": "Skills updated"}

# Job search endpoints
@api_router.get("/jobs/search")
async def search_jobs(query: str = "", source: str = "all"):
    jobs = []
    
    if source in ["all", "remoteok"]:
        remoteok_jobs = await fetch_remoteok_jobs(query)
        jobs.extend(remoteok_jobs)
    
    if source in ["all", "remotive"]:
        remotive_jobs = await fetch_remotive_jobs(query)
        jobs.extend(remotive_jobs)
    
    return jobs

@api_router.post("/jobs/analyze")
async def analyze_job(request: JobAnalyzeRequest):
    # Get resume data
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    if not resume_doc:
        raise HTTPException(status_code=404, detail="Please upload your resume first")
    
    job_data = {
        "title": request.job_title,
        "company": request.company,
        "description": request.job_description
    }
    
    result = await analyze_job_match(resume_doc, job_data)
    return result

# Saved jobs endpoints
@api_router.post("/jobs/save")
async def save_job(job: Job):
    saved = SavedJob(job=job)
    doc = saved.model_dump()
    doc['saved_at'] = doc['saved_at'].isoformat()
    
    # Check if already saved
    existing = await db.saved_jobs.find_one({"job.id": job.id})
    if existing:
        raise HTTPException(status_code=400, detail="Job already saved")
    
    await db.saved_jobs.insert_one(doc)
    return saved

@api_router.get("/jobs/saved")
async def get_saved_jobs():
    docs = await db.saved_jobs.find({}, {"_id": 0}).to_list(100)
    for doc in docs:
        if isinstance(doc.get('saved_at'), str):
            doc['saved_at'] = datetime.fromisoformat(doc['saved_at'])
    return docs

@api_router.delete("/jobs/saved/{job_id}")
async def remove_saved_job(job_id: str):
    result = await db.saved_jobs.delete_one({"id": job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved job not found")
    return {"message": "Job removed from saved"}

# Application tracking endpoints
@api_router.post("/applications")
async def create_application(data: ApplicationCreate):
    app_doc = Application(job=data.job, notes=data.notes)
    doc = app_doc.model_dump()
    doc['applied_at'] = doc['applied_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.applications.insert_one(doc)
    return app_doc

@api_router.get("/applications")
async def get_applications():
    docs = await db.applications.find({}, {"_id": 0}).to_list(100)
    for doc in docs:
        if isinstance(doc.get('applied_at'), str):
            doc['applied_at'] = datetime.fromisoformat(doc['applied_at'])
        if isinstance(doc.get('updated_at'), str):
            doc['updated_at'] = datetime.fromisoformat(doc['updated_at'])
    return docs

@api_router.put("/applications/{app_id}")
async def update_application(app_id: str, data: ApplicationStatusUpdate):
    update_data = {"status": data.status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if data.notes is not None:
        update_data["notes"] = data.notes
    
    result = await db.applications.update_one(
        {"id": app_id},
        {"$set": update_data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application updated"}

@api_router.delete("/applications/{app_id}")
async def delete_application(app_id: str):
    result = await db.applications.delete_one({"id": app_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted"}

# Manual job creation
@api_router.post("/jobs/manual")
async def create_manual_job(job: ManualJobCreate):
    new_job = Job(
        title=job.title,
        company=job.company,
        location=job.location,
        description=job.description,
        url=job.url,
        salary=job.salary,
        tags=job.tags,
        source="Manual"
    )
    return new_job

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
