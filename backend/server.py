from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import asyncio
from PyPDF2 import PdfReader
import io
from emergentintegrations.llm.chat import LlmChat, UserMessage
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

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

# Gmail Configuration
GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
ALERT_RECIPIENT = os.environ.get('ALERT_RECIPIENT')

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
    status: str = "Applied"
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""

class JobAlert(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    keywords: List[str] = []
    locations: List[str] = []
    is_active: bool = True
    email: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_sent: Optional[datetime] = None

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

class JobAlertCreate(BaseModel):
    keywords: List[str]
    locations: List[str] = []
    email: str

class EmailAlertRequest(BaseModel):
    email: str

# Helper function to extract text from PDF
def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# Gmail email sending
def send_email_gmail(to_email: str, subject: str, html_content: str) -> bool:
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        logging.error("Gmail credentials not configured")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = GMAIL_ADDRESS
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        
        logging.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

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
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except:
        return {"match_score": 50, "analysis": "Unable to analyze match"}

# AI-powered web crawler for job discovery
async def ai_crawl_jobs(query: str, resume_skills: List[str] = []) -> List[dict]:
    """Use AI to analyze and enhance job search results"""
    if not EMERGENT_LLM_KEY:
        return []
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a job search expert. Given a search query and user skills, suggest:
        1. Related job titles to search for
        2. Keywords that would find matching jobs
        3. Industry-specific terms
        
        Return a JSON object with:
        - related_titles: array of 5 related job titles
        - keywords: array of 10 search keywords
        - industries: array of 3 relevant industries
        
        Return ONLY valid JSON."""
    ).with_model("openai", "gpt-5.2")
    
    skills_text = ', '.join(resume_skills[:15]) if resume_skills else 'general'
    user_message = UserMessage(
        text=f"Search query: {query}\nUser skills: {skills_text}\n\nSuggest related job searches."
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except:
        return {"related_titles": [], "keywords": [], "industries": []}

# Fetch jobs from RemoteOK API
async def fetch_remoteok_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            headers = {"User-Agent": "MedMatch/1.0"}
            response = await http_client.get("https://remoteok.com/api", headers=headers)
            if response.status_code == 200:
                jobs = response.json()
                jobs = jobs[1:] if len(jobs) > 1 else []
                
                result = []
                for job in jobs[:100]:
                    job_location = job.get('location', 'Remote') or 'Remote'
                    
                    # Filter by query
                    matches_query = not query or \
                        query.lower() in job.get('position', '').lower() or \
                        query.lower() in job.get('company', '').lower() or \
                        query.lower() in ' '.join(job.get('tags', [])).lower()
                    
                    # Filter by location
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        location.lower() == 'remote' or \
                        location.lower() == 'worldwide'
                    
                    if matches_query and matches_location:
                        result.append({
                            "id": f"rok_{job.get('id', uuid.uuid4())}",
                            "title": job.get('position', 'Unknown'),
                            "company": job.get('company', 'Unknown'),
                            "location": job_location,
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
async def fetch_remotive_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            params = {}
            if query:
                params["search"] = query
            response = await http_client.get("https://remotive.com/api/remote-jobs", params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])[:100]
                
                result = []
                for job in jobs:
                    job_location = job.get('candidate_required_location', 'Worldwide') or 'Worldwide'
                    
                    # Filter by location
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        location.lower() == 'remote' or \
                        location.lower() == 'worldwide'
                    
                    if matches_location:
                        result.append({
                            "id": f"rem_{job.get('id', uuid.uuid4())}",
                            "title": job.get('title', 'Unknown'),
                            "company": job.get('company_name', 'Unknown'),
                            "location": job_location,
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

# Fetch jobs from Jobicy API (no auth required)
async def fetch_jobicy_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            params = {"count": 50, "geo": "anywhere"}
            if query:
                params["tag"] = query.replace(" ", "-").lower()
            if location and location.lower() not in ['remote', 'worldwide', 'anywhere']:
                params["geo"] = location.lower()
            
            response = await http_client.get("https://jobicy.com/api/v2/remote-jobs", params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                result = []
                for job in jobs:
                    result.append({
                        "id": f"jcy_{job.get('id', uuid.uuid4())}",
                        "title": job.get('jobTitle', 'Unknown'),
                        "company": job.get('companyName', 'Unknown'),
                        "location": job.get('jobGeo', 'Remote'),
                        "description": job.get('jobDescription', ''),
                        "url": job.get('url', ''),
                        "salary": f"{job.get('annualSalaryMin', '')} - {job.get('annualSalaryMax', '')}" if job.get('annualSalaryMin') else '',
                        "tags": [job.get('jobIndustry', '')] if job.get('jobIndustry') else [],
                        "source": "Jobicy",
                        "posted_at": job.get('pubDate', '')
                    })
                return result
    except Exception as e:
        logging.error(f"Jobicy API error: {e}")
    return []

# Fetch jobs from Arbeitnow API (no auth required)
async def fetch_arbeitnow_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            response = await http_client.get("https://www.arbeitnow.com/api/job-board-api")
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('data', [])[:50]
                
                result = []
                for job in jobs:
                    job_location = job.get('location', 'Remote')
                    job_title = job.get('title', '')
                    job_company = job.get('company_name', '')
                    job_desc = job.get('description', '')
                    
                    # Filter by query
                    matches_query = not query or \
                        query.lower() in job_title.lower() or \
                        query.lower() in job_company.lower() or \
                        query.lower() in job_desc.lower()
                    
                    # Filter by location
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        job.get('remote', False)
                    
                    if matches_query and matches_location:
                        result.append({
                            "id": f"arb_{job.get('slug', uuid.uuid4())}",
                            "title": job_title,
                            "company": job_company,
                            "location": job_location + (" (Remote)" if job.get('remote') else ""),
                            "description": job_desc,
                            "url": job.get('url', ''),
                            "salary": "",
                            "tags": job.get('tags', []),
                            "source": "Arbeitnow",
                            "posted_at": job.get('created_at', '')
                        })
                return result
    except Exception as e:
        logging.error(f"Arbeitnow API error: {e}")
    return []

# Fetch jobs from Himalayas API (tech jobs, no auth)
async def fetch_himalayas_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            params = {"limit": 50}
            response = await http_client.get("https://himalayas.app/jobs/api", params=params)
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('jobs', [])
                
                result = []
                for job in jobs:
                    job_title = job.get('title', '')
                    job_company = job.get('companyName', '')
                    job_location = ', '.join(job.get('locationRestrictions', [])) or 'Worldwide'
                    
                    # Filter by query
                    matches_query = not query or \
                        query.lower() in job_title.lower() or \
                        query.lower() in job_company.lower()
                    
                    if matches_query:
                        result.append({
                            "id": f"him_{job.get('id', uuid.uuid4())}",
                            "title": job_title,
                            "company": job_company,
                            "location": job_location,
                            "description": job.get('description', ''),
                            "url": job.get('applicationLink', '') or f"https://himalayas.app/jobs/{job.get('id')}",
                            "salary": job.get('salaryRange', ''),
                            "tags": job.get('categories', []),
                            "source": "Himalayas",
                            "posted_at": job.get('pubDate', '')
                        })
                return result
    except Exception as e:
        logging.error(f"Himalayas API error: {e}")
    return []

# Filter jobs by date
def filter_jobs_by_date(jobs: List[dict], days: int) -> List[dict]:
    if days <= 0:
        return jobs
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    filtered = []
    
    for job in jobs:
        posted_at = job.get('posted_at', '')
        if not posted_at:
            filtered.append(job)  # Include jobs without date
            continue
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ']:
                try:
                    job_date = datetime.strptime(posted_at[:19], fmt[:len(posted_at)])
                    if job_date.tzinfo is None:
                        job_date = job_date.replace(tzinfo=timezone.utc)
                    if job_date >= cutoff_date:
                        filtered.append(job)
                    break
                except:
                    continue
            else:
                filtered.append(job)  # Include if can't parse date
        except:
            filtered.append(job)
    
    return filtered

# Generate job alert email HTML
def generate_job_alert_html(jobs: List[dict], keywords: List[str]) -> str:
    job_items = ""
    for job in jobs[:10]:  # Limit to 10 jobs per email
        tags_html = ''.join([f'<span style="background:#E2E8F0;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:4px;">{tag}</span>' for tag in job.get('tags', [])[:3]])
        job_items += f"""
        <div style="border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin-bottom:12px;">
            <h3 style="margin:0 0 8px 0;color:#0F172A;">{job['title']}</h3>
            <p style="margin:0 0 8px 0;color:#64748B;">{job['company']} • {job['location']}</p>
            {f'<p style="color:#10B981;font-weight:500;margin:0 0 8px 0;">{job["salary"]}</p>' if job.get('salary') else ''}
            <div style="margin-bottom:12px;">{tags_html}</div>
            <a href="{job['url']}" style="display:inline-block;background:#0F172A;color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:14px;">View Job</a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family:'Inter',Arial,sans-serif;background:#F8FAFC;padding:20px;">
        <div style="max-width:600px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;">
            <div style="background:#0F172A;color:white;padding:24px;text-align:center;">
                <h1 style="margin:0;font-size:24px;">MedMatch Job Alert</h1>
                <p style="margin:8px 0 0 0;opacity:0.8;">New jobs matching: {', '.join(keywords)}</p>
            </div>
            <div style="padding:24px;">
                <p style="color:#64748B;margin-bottom:20px;">We found {len(jobs)} new remote jobs that match your profile!</p>
                {job_items}
            </div>
            <div style="background:#F1F5F9;padding:16px;text-align:center;color:#64748B;font-size:12px;">
                <p>You're receiving this because you set up job alerts on MedMatch.</p>
            </div>
        </div>
    </body>
    </html>
    """

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
    
    doc = resume.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.resumes.delete_many({})
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

# Job search endpoints with filters
@api_router.get("/jobs/search")
async def search_jobs(
    query: str = "",
    source: str = "all",
    location: str = "",
    days: int = 0
):
    jobs = []
    
    # Fetch from all sources in parallel
    tasks = []
    
    if source in ["all", "remoteok"]:
        tasks.append(fetch_remoteok_jobs(query, location))
    if source in ["all", "remotive"]:
        tasks.append(fetch_remotive_jobs(query, location))
    if source in ["all", "jobicy"]:
        tasks.append(fetch_jobicy_jobs(query, location))
    if source in ["all", "arbeitnow"]:
        tasks.append(fetch_arbeitnow_jobs(query, location))
    if source in ["all", "himalayas"]:
        tasks.append(fetch_himalayas_jobs(query, location))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            jobs.extend(result)
    
    # Filter by date if specified
    if days > 0:
        jobs = filter_jobs_by_date(jobs, days)
    
    # Remove duplicates by title+company
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    return unique_jobs

# AI-enhanced job search
@api_router.get("/jobs/ai-search")
async def ai_enhanced_search(query: str = ""):
    # Get resume for context
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    skills = resume_doc.get('skills', []) if resume_doc else []
    
    # Get AI suggestions
    suggestions = await ai_crawl_jobs(query, skills)
    
    # Search with original query and AI suggestions
    all_jobs = []
    queries_to_search = [query] if query else []
    
    if isinstance(suggestions, dict):
        queries_to_search.extend(suggestions.get('related_titles', [])[:3])
        queries_to_search.extend(suggestions.get('keywords', [])[:3])
    
    for q in queries_to_search[:5]:  # Limit to 5 searches
        jobs = await search_jobs(query=q, source="all")
        all_jobs.extend(jobs)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    return {
        "jobs": unique_jobs[:100],
        "suggestions": suggestions if isinstance(suggestions, dict) else {}
    }

# Quick search presets
@api_router.get("/jobs/presets")
async def get_search_presets():
    return {
        "presets": [
            {
                "id": "supplier-quality-manager",
                "name": "Supplier Quality Manager",
                "query": "Supplier Quality Manager",
                "icon": "shield-check"
            },
            {
                "id": "supplier-quality-director",
                "name": "Supplier Quality Director",
                "query": "Supplier Quality Director",
                "icon": "award"
            },
            {
                "id": "quality-assurance",
                "name": "Quality Assurance",
                "query": "Quality Assurance",
                "icon": "check-circle"
            },
            {
                "id": "regulatory-compliance",
                "name": "Regulatory Compliance",
                "query": "Regulatory Compliance",
                "icon": "file-text"
            },
            {
                "id": "qa-engineer",
                "name": "QA Engineer",
                "query": "QA Engineer",
                "icon": "code"
            },
            {
                "id": "medical-device",
                "name": "Medical Device",
                "query": "Medical Device Quality",
                "icon": "heart-pulse"
            }
        ],
        "locations": [
            "Worldwide",
            "USA",
            "Europe",
            "UK",
            "Canada",
            "Germany",
            "Remote"
        ]
    }

@api_router.post("/jobs/analyze")
async def analyze_job(request: JobAnalyzeRequest):
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

# Job Alerts endpoints
@api_router.post("/alerts")
async def create_job_alert(data: JobAlertCreate):
    alert = JobAlert(
        keywords=data.keywords,
        locations=data.locations,
        email=data.email
    )
    doc = alert.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.job_alerts.insert_one(doc)
    return alert

@api_router.get("/alerts")
async def get_job_alerts():
    docs = await db.job_alerts.find({}, {"_id": 0}).to_list(100)
    return docs

@api_router.delete("/alerts/{alert_id}")
async def delete_job_alert(alert_id: str):
    result = await db.job_alerts.delete_one({"id": alert_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted"}

@api_router.post("/alerts/send-now")
async def send_job_alert_now(background_tasks: BackgroundTasks, data: EmailAlertRequest):
    """Send job alert email immediately"""
    # Get resume skills
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    keywords = ["Supplier Quality", "Quality Manager", "Regulatory Compliance"]
    if resume_doc and resume_doc.get('skills'):
        keywords = resume_doc['skills'][:5]
    
    # Fetch matching jobs
    jobs = []
    for keyword in keywords[:3]:
        fetched = await search_jobs(query=keyword, source="all", days=7)
        jobs.extend(fetched)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    if not unique_jobs:
        return {"message": "No matching jobs found", "jobs_count": 0}
    
    # Generate and send email
    html_content = generate_job_alert_html(unique_jobs[:10], keywords[:3])
    
    def send_email_task():
        send_email_gmail(
            data.email,
            f"MedMatch: {len(unique_jobs)} New Jobs Matching Your Profile",
            html_content
        )
    
    background_tasks.add_task(send_email_task)
    
    return {"message": f"Job alert sent to {data.email}", "jobs_count": len(unique_jobs)}

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
