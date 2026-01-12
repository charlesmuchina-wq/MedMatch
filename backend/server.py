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
import re
from concurrent.futures import ThreadPoolExecutor

# JobSpy - Powerful job scraper for LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter
try:
    from jobspy import scrape_jobs
    JOBSPY_AVAILABLE = True
except ImportError:
    JOBSPY_AVAILABLE = False
    logging.warning("JobSpy not available - using fallback APIs only")

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
ALERT_RECIPIENT = os.environ.get('ALERT_RECIPIENT')

# Google Custom Search API Configuration
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.environ.get('GOOGLE_CSE_ID')

# Job board sites to search via Google CSE
GOOGLE_CSE_JOB_SITES = [
    "indeed.com/viewjob",
    "linkedin.com/jobs",
    "glassdoor.com/job-listing",
    "ziprecruiter.com/jobs",
    "monster.com/job",
    "careerbuilder.com/job",
    "dice.com/jobs",
    "simplyhired.com/job"
]

# Expanded search keywords for Quality/Medical Device professionals
QUALITY_SEARCH_TERMS = [
    "Supplier Quality Manager",
    "Supplier Quality Director",
    "Quality Manager",
    "Quality Director",
    "Lead Auditor",
    "Medical Device",
    "Medical Devices",
    "Manufacturing Quality",
    "Quality Assurance Manager",
    "Quality Assurance Director",
    "Regulatory Compliance",
    "ISO 13485",
    "FDA Compliance",
    "Quality Engineer",
    "Supplier Quality Engineer",
    "Quality Systems",
    "QMS Manager",
    "Audit Manager",
    "Compliance Manager",
    "Quality Control Manager"
]

# Models
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

class DeepSearchRequest(BaseModel):
    use_ai: bool = True

# Helper functions
def extract_text_from_pdf(file_content: bytes) -> str:
    pdf_reader = PdfReader(io.BytesIO(file_content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

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
            "full_name": "", "email": "", "phone": "",
            "skills": [], "experience": [], "education": [],
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

# AI-powered deep web crawler for comprehensive job discovery
async def ai_deep_crawl(resume_skills: List[str] = []) -> dict:
    """Use AI to generate comprehensive search strategy"""
    if not EMERGENT_LLM_KEY:
        return {"search_queries": QUALITY_SEARCH_TERMS[:10], "related_titles": [], "industries": []}
    
    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=str(uuid.uuid4()),
        system_message="""You are a job search strategist specializing in Quality Assurance, Medical Devices, and Manufacturing roles.
        
        Generate SIMPLE search queries (1-3 words each) that job boards can understand.
        Focus on:
        - Supplier Quality (Manager, Director, Engineer)
        - Medical Device Quality
        - Lead Auditor roles
        - Manufacturing Quality
        - Quality Management Systems
        - Regulatory Compliance (FDA, ISO)
        
        Return a JSON object with:
        - search_queries: array of 15 SIMPLE search terms (1-3 words each, NO boolean operators)
        - related_titles: array of 10 job titles
        - industries: array of 5 target industries
        - keywords: array of 15 single-word keywords
        
        Example search_queries: ["Quality Manager", "Supplier Quality", "Lead Auditor", "Medical Device", "ISO Auditor"]
        
        Return ONLY valid JSON."""
    ).with_model("openai", "gpt-5.2")
    
    skills_text = ', '.join(resume_skills[:20]) if resume_skills else 'Quality Management, ISO 13485, FDA, Supplier Quality'
    user_message = UserMessage(
        text=f"Generate simple job search terms for a professional with these skills:\n{skills_text}\n\nFocus on remote Quality, Medical Device, and Manufacturing roles."
    )
    
    try:
        response = await chat.send_message(user_message)
        clean_response = response.strip()
        if clean_response.startswith("```"):
            clean_response = clean_response.split("```")[1]
            if clean_response.startswith("json"):
                clean_response = clean_response[4:]
        return json.loads(clean_response)
    except Exception as e:
        logging.error(f"AI deep crawl error: {e}")
        return {
            "search_queries": QUALITY_SEARCH_TERMS,
            "related_titles": ["Quality Manager", "Quality Director", "Lead Auditor", "Supplier Quality Manager"],
            "industries": ["Medical Devices", "Pharmaceutical", "Manufacturing"],
            "keywords": ["quality", "auditor", "ISO", "FDA", "compliance"]
        }

# Job fetching functions for each source
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
                    job_title = job.get('position', '').lower()
                    job_desc = job.get('description', '').lower()
                    job_tags = ' '.join(job.get('tags', [])).lower()
                    
                    matches_query = not query or \
                        query.lower() in job_title or \
                        query.lower() in job.get('company', '').lower() or \
                        query.lower() in job_tags or \
                        query.lower() in job_desc
                    
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        location.lower() in ['remote', 'worldwide', 'any']
                    
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
                    
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        location.lower() in ['remote', 'worldwide', 'any']
                    
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

async def fetch_jobicy_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            params = {"count": 50, "geo": "anywhere"}
            if query:
                params["tag"] = query.replace(" ", "-").lower()[:20]
            if location and location.lower() not in ['remote', 'worldwide', 'anywhere', 'any']:
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

async def fetch_arbeitnow_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            response = await http_client.get("https://www.arbeitnow.com/api/job-board-api")
            if response.status_code == 200:
                data = response.json()
                jobs = data.get('data', [])[:100]
                
                result = []
                for job in jobs:
                    job_location = job.get('location', 'Remote')
                    job_title = job.get('title', '').lower()
                    job_desc = job.get('description', '').lower()
                    
                    matches_query = not query or \
                        query.lower() in job_title or \
                        query.lower() in job.get('company_name', '').lower() or \
                        query.lower() in job_desc
                    
                    matches_location = not location or \
                        location.lower() in job_location.lower() or \
                        job.get('remote', False) or \
                        location.lower() in ['remote', 'worldwide', 'any']
                    
                    if matches_query and matches_location:
                        result.append({
                            "id": f"arb_{job.get('slug', uuid.uuid4())}",
                            "title": job.get('title', 'Unknown'),
                            "company": job.get('company_name', 'Unknown'),
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
                    job_title = job.get('title', '').lower()
                    job_company = job.get('companyName', '').lower()
                    
                    matches_query = not query or \
                        query.lower() in job_title or \
                        query.lower() in job_company
                    
                    if matches_query:
                        result.append({
                            "id": f"him_{job.get('id', uuid.uuid4())}",
                            "title": job.get('title', 'Unknown'),
                            "company": job.get('companyName', 'Unknown'),
                            "location": ', '.join(job.get('locationRestrictions', [])) or 'Worldwide',
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

# NEW: Fetch from Adzuna (free tier available)
async def fetch_adzuna_jobs(query: str = "", location: str = "") -> List[dict]:
    try:
        # Adzuna has a free API but requires registration - using public feed
        async with httpx.AsyncClient(timeout=15.0) as http_client:
            # Try multiple country endpoints
            countries = ['us', 'gb', 'ca', 'de']
            all_jobs = []
            
            for country in countries[:2]:  # Limit to 2 countries for speed
                try:
                    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
                    params = {
                        "app_id": "public",
                        "app_key": "public",
                        "results_per_page": 20,
                        "what": query or "quality manager",
                        "what_or": "quality auditor supplier",
                        "where": location if location and location.lower() not in ['any', 'remote', 'worldwide'] else ""
                    }
                    response = await http_client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        for job in data.get('results', []):
                            all_jobs.append({
                                "id": f"adz_{job.get('id', uuid.uuid4())}",
                                "title": job.get('title', 'Unknown'),
                                "company": job.get('company', {}).get('display_name', 'Unknown'),
                                "location": job.get('location', {}).get('display_name', 'Remote'),
                                "description": job.get('description', ''),
                                "url": job.get('redirect_url', ''),
                                "salary": f"${job.get('salary_min', '')}-${job.get('salary_max', '')}" if job.get('salary_min') else '',
                                "tags": [job.get('category', {}).get('label', '')],
                                "source": f"Adzuna ({country.upper()})",
                                "posted_at": job.get('created', '')
                            })
                except:
                    continue
            return all_jobs
    except Exception as e:
        logging.error(f"Adzuna API error: {e}")
    return []

# NEW: Fetch from JSearch (RapidAPI free tier)
async def fetch_jsearch_jobs(query: str = "", location: str = "") -> List[dict]:
    # Placeholder - would integrate with proper API key
    return []

# GOOGLE CUSTOM SEARCH API - Search job boards directly via Google
async def fetch_google_cse_jobs(query: str, location: str = "Remote", site: str = "indeed.com", num_results: int = 10) -> List[dict]:
    """
    Fetch jobs from any job board using Google Custom Search API
    Based on the Google Sheets script approach for searching Indeed
    """
    if not GOOGLE_API_KEY:
        logging.warning("Google API Key not configured")
        return []
    
    try:
        async with httpx.AsyncClient(timeout=20.0) as http_client:
            # Build optimized search query for job postings
            # Format: "job title" "location" site:jobboard.com
            search_query = f'"{query}" "{location}" job site:{site}'
            
            params = {
                "q": search_query,
                "key": GOOGLE_API_KEY,
                "num": min(num_results, 10),
            }
            
            # Only add CSE ID if configured - otherwise Google will require one
            # For this to work without CSE, user needs Programmable Search Engine
            if GOOGLE_CSE_ID:
                params["cx"] = GOOGLE_CSE_ID
            else:
                # Cannot use Custom Search API without CSE ID
                logging.warning("Google CSE ID not configured - skipping Google search")
                return []
            
            response = await http_client.get(
                "https://www.googleapis.com/customsearch/v1",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                logging.info(f"Google CSE returned {len(items)} results for '{query}' on {site}")
                
                result = []
                for item in items:
                    job_url = item.get("link", "")
                    title = item.get("title", "Unknown")
                    snippet = item.get("snippet", "")
                    
                    # Extract company from snippet (pattern: "at Company -" or "Company -")
                    company = "Unknown"
                    company_match = re.search(r'(?:at\s+)?([\w\s&.,-]+?)(?:\s*[-–|•]|\s+is\s+)', snippet)
                    if company_match:
                        company = company_match.group(1).strip()[:50]
                    
                    # Extract salary from snippet
                    salary = ""
                    salary_match = re.search(r'\$[\d,]+(?:\s*[-–]\s*\$[\d,]+)?(?:\s*(?:a\s*year|per\s*year|annually|/yr|K))?', snippet, re.IGNORECASE)
                    if salary_match:
                        salary = salary_match.group(0)
                    
                    # Determine source from URL
                    source = "Google Search"
                    if "indeed.com" in job_url:
                        source = "Indeed (Google)"
                    elif "linkedin.com" in job_url:
                        source = "LinkedIn (Google)"
                    elif "glassdoor.com" in job_url:
                        source = "Glassdoor (Google)"
                    elif "ziprecruiter.com" in job_url:
                        source = "ZipRecruiter (Google)"
                    elif "monster.com" in job_url:
                        source = "Monster (Google)"
                    elif "dice.com" in job_url:
                        source = "Dice (Google)"
                    elif "careerbuilder.com" in job_url:
                        source = "CareerBuilder (Google)"
                    
                    result.append({
                        "id": f"gcse_{abs(hash(job_url))}",
                        "title": title.replace(" | Indeed.com", "").replace(" - LinkedIn", "").replace(" | Glassdoor", "").strip(),
                        "company": company if company != "Unknown" else title.split(" at ")[-1].split(" - ")[0][:30] if " at " in title else "Unknown",
                        "location": location,
                        "description": snippet,
                        "url": job_url,
                        "salary": salary,
                        "tags": [],
                        "source": source,
                        "posted_at": ""
                    })
                
                return result
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                logging.error(f"Google CSE API error: {response.status_code} - {error_data.get('error', {}).get('message', response.text[:200])}")
                return []
                
    except Exception as e:
        logging.error(f"Google CSE error: {e}")
        return []

# Fetch jobs from multiple job sites via Google CSE
async def fetch_google_cse_all_sites(query: str, location: str = "Remote") -> List[dict]:
    """Search multiple job boards simultaneously using Google Custom Search"""
    all_jobs = []
    
    # Search Indeed, LinkedIn, Glassdoor, ZipRecruiter via Google
    sites_to_search = [
        "indeed.com",
        "linkedin.com/jobs",
        "glassdoor.com",
        "ziprecruiter.com"
    ]
    
    tasks = [
        fetch_google_cse_jobs(query, location, site, 10)
        for site in sites_to_search
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
    
    return all_jobs

# JOBSPY INTEGRATION - Scrape from LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter
def fetch_jobspy_jobs_sync(query: str, location: str = "USA", sites: List[str] = None, results_wanted: int = 25, hours_old: int = 72) -> List[dict]:
    """Synchronous JobSpy scraper - runs in thread pool"""
    if not JOBSPY_AVAILABLE:
        return []
    
    if sites is None:
        sites = ["indeed", "linkedin", "glassdoor", "google", "zip_recruiter"]
    
    try:
        # Use optimized search term for Quality/Medical Device roles
        search_term = query or "quality manager"
        
        # Google needs special search term format
        google_search_term = f"{search_term} jobs remote" if "google" in sites else None
        
        jobs_df = scrape_jobs(
            site_name=sites,
            search_term=search_term,
            google_search_term=google_search_term,
            location=location if location and location.lower() not in ['any', 'worldwide'] else "USA",
            results_wanted=results_wanted,
            hours_old=hours_old,
            is_remote=True,
            country_indeed='USA',
            verbose=0
        )
        
        if jobs_df is None or jobs_df.empty:
            return []
        
        result = []
        for _, row in jobs_df.iterrows():
            # Build salary string
            salary = ""
            if row.get('min_amount') and row.get('max_amount'):
                interval = row.get('interval', 'yearly')
                salary = f"${int(row['min_amount']):,} - ${int(row['max_amount']):,}/{interval}"
            elif row.get('min_amount'):
                salary = f"${int(row['min_amount']):,}+"
            
            # Build location string
            loc_parts = []
            if row.get('city'):
                loc_parts.append(str(row['city']))
            if row.get('state'):
                loc_parts.append(str(row['state']))
            if row.get('is_remote'):
                loc_parts.append("Remote")
            location_str = ", ".join(loc_parts) if loc_parts else "Remote"
            
            job = {
                "id": f"jspy_{row.get('site', 'unknown')}_{hash(str(row.get('job_url', '')))}",
                "title": str(row.get('title', 'Unknown')),
                "company": str(row.get('company', 'Unknown')),
                "location": location_str,
                "description": str(row.get('description', ''))[:5000],
                "url": str(row.get('job_url', '')),
                "salary": salary,
                "tags": [str(row.get('job_type', ''))] if row.get('job_type') else [],
                "source": f"JobSpy ({str(row.get('site', 'Unknown')).title()})",
                "posted_at": str(row.get('date_posted', '')) if row.get('date_posted') else ''
            }
            result.append(job)
        
        return result
    except Exception as e:
        logging.error(f"JobSpy error: {e}")
        return []

async def fetch_jobspy_jobs(query: str, location: str = "USA", sites: List[str] = None, results_wanted: int = 25) -> List[dict]:
    """Async wrapper for JobSpy - runs in thread pool to avoid blocking"""
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(
            executor,
            fetch_jobspy_jobs_sync,
            query,
            location,
            sites,
            results_wanted,
            72  # hours_old
        )
    return result

# Placeholder functions for removed APIs
async def fetch_linkedin_jobs(query: str = "", location: str = "") -> List[dict]:
    # Now handled by JobSpy
    return []

async def fetch_indeed_jobs(query: str = "", location: str = "") -> List[dict]:
    # Now handled by JobSpy
    return []

async def fetch_freejobs_api(query: str = "", location: str = "") -> List[dict]:
    return []

def filter_jobs_by_date(jobs: List[dict], days: int) -> List[dict]:
    if days <= 0:
        return jobs
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
    filtered = []
    
    for job in jobs:
        posted_at = job.get('posted_at', '')
        if not posted_at:
            filtered.append(job)
            continue
        
        try:
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
                filtered.append(job)
        except:
            filtered.append(job)
    
    return filtered

def filter_jobs_by_relevance(jobs: List[dict], keywords: List[str]) -> List[dict]:
    """Filter and score jobs by relevance to quality/medical device keywords"""
    relevance_keywords = [
        'quality', 'supplier', 'auditor', 'audit', 'iso', 'fda', 'medical device',
        'manufacturing', 'compliance', 'regulatory', 'qms', 'capa', 'ncr',
        'validation', 'verification', 'inspection', '13485', 'gmp', 'cgmp',
        'pharmaceutical', 'healthcare', 'biotech', 'med tech', 'qa', 'qc',
        'director', 'manager', 'engineer', 'lead', 'senior', 'principal'
    ]
    relevance_keywords.extend([k.lower() for k in keywords if k])
    
    scored_jobs = []
    for job in jobs:
        score = 0
        title_lower = job.get('title', '').lower()
        desc_lower = job.get('description', '').lower()
        tags_lower = ' '.join(job.get('tags', [])).lower()
        
        for keyword in relevance_keywords:
            if keyword in title_lower:
                score += 10
            if keyword in desc_lower:
                score += 2
            if keyword in tags_lower:
                score += 5
        
        job['relevance_score'] = min(score, 100)
        scored_jobs.append(job)
    
    # Sort by relevance score (highest first)
    scored_jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    return scored_jobs

def generate_job_alert_html(jobs: List[dict], keywords: List[str]) -> str:
    job_items = ""
    for job in jobs[:15]:
        tags_html = ''.join([f'<span style="background:#E2E8F0;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:4px;">{tag}</span>' for tag in job.get('tags', [])[:3]])
        relevance = job.get('relevance_score', 0)
        relevance_badge = f'<span style="background:#10B981;color:white;padding:2px 8px;border-radius:12px;font-size:11px;">Match: {min(relevance, 100)}%</span>' if relevance else ''
        
        job_items += f"""
        <div style="border:1px solid #E2E8F0;border-radius:8px;padding:16px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:start;">
                <h3 style="margin:0 0 8px 0;color:#0F172A;">{job['title']}</h3>
                {relevance_badge}
            </div>
            <p style="margin:0 0 8px 0;color:#64748B;">{job['company']} • {job['location']}</p>
            <p style="margin:0 0 8px 0;color:#94A3B8;font-size:12px;">Source: {job.get('source', 'Unknown')}</p>
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
                <p style="margin:8px 0 0 0;opacity:0.8;">AI-Powered Search: {', '.join(keywords[:3])}</p>
            </div>
            <div style="padding:24px;">
                <p style="color:#64748B;margin-bottom:20px;">We found <strong>{len(jobs)}</strong> jobs matching your Quality/Medical Device profile!</p>
                {job_items}
                <p style="color:#94A3B8;font-size:12px;margin-top:20px;text-align:center;">
                    Searched across: RemoteOK, Remotive, Jobicy, Arbeitnow, Himalayas, and more
                </p>
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
    return {"message": "MedMatch API - Remote Job Finder with AI Crawler"}

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

# Enhanced job search with multiple sources including JobSpy
@api_router.get("/jobs/search")
async def search_jobs(
    query: str = "",
    source: str = "all",
    location: str = "",
    days: int = 0
):
    jobs = []
    tasks = []
    
    # Free API sources
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
    
    # Google CSE sources
    if source in ["all", "google"] and GOOGLE_API_KEY and query:
        tasks.append(fetch_google_cse_all_sites(query, location or "Remote"))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            jobs.extend(result)
    
    if days > 0:
        jobs = filter_jobs_by_date(jobs, days)
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    return unique_jobs

# Google CSE Direct Search endpoint - search specific job boards via Google
@api_router.get("/jobs/google-search")
async def google_search_jobs(
    query: str = "Quality Manager",
    location: str = "Remote",
    site: str = "indeed.com/viewjob"
):
    """
    Direct Google Custom Search for job boards.
    Supports: indeed.com, linkedin.com, glassdoor.com, ziprecruiter.com, monster.com, dice.com
    """
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=400, detail="Google API Key not configured")
    
    jobs = await fetch_google_cse_jobs(query, location, site, 10)
    return {
        "jobs": jobs,
        "query": query,
        "location": location,
        "site": site,
        "total": len(jobs)
    }

# Deep AI-powered search across ALL sources including JobSpy (LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter)
@api_router.post("/jobs/deep-search")
async def deep_search_jobs(request: DeepSearchRequest):
    """AI-powered comprehensive search across ALL job sources including LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter + Google CSE"""
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    skills = resume_doc.get('skills', []) if resume_doc else []
    
    # Get AI-generated search strategy
    search_strategy = {}
    if request.use_ai:
        search_strategy = await ai_deep_crawl(skills)
    
    search_queries = search_strategy.get('search_queries', QUALITY_SEARCH_TERMS)[:10]
    
    all_jobs = []
    sources_searched = []
    
    # 1. Use Google Custom Search API to search Indeed, LinkedIn, Glassdoor directly
    if GOOGLE_API_KEY:
        logging.info("Starting Google CSE job search...")
        for query in search_queries[:3]:
            try:
                google_results = await fetch_google_cse_all_sites(query, "Remote")
                all_jobs.extend(google_results)
                if google_results:
                    sources_searched.extend(["Indeed (Google)", "LinkedIn (Google)", "Glassdoor (Google)"])
            except Exception as e:
                logging.error(f"Google CSE error for '{query}': {e}")
    
    # 2. Use JobSpy to scrape from major job boards (LinkedIn, Indeed, Glassdoor, Google, ZipRecruiter)
    if JOBSPY_AVAILABLE:
        logging.info("Starting JobSpy deep search...")
        for query in search_queries[:3]:
            try:
                jobspy_results = await fetch_jobspy_jobs(
                    query=query,
                    location="USA",
                    sites=["indeed", "linkedin", "glassdoor", "zip_recruiter"],
                    results_wanted=15
                )
                all_jobs.extend(jobspy_results)
                if jobspy_results:
                    sources_searched.extend(["LinkedIn (JobSpy)", "Indeed (JobSpy)", "Glassdoor (JobSpy)", "ZipRecruiter (JobSpy)"])
            except Exception as e:
                logging.error(f"JobSpy search error for '{query}': {e}")
    
    # 3. Search free API sources in parallel
    for query in search_queries[:6]:
        tasks = [
            fetch_remoteok_jobs(query, ""),
            fetch_remotive_jobs(query, ""),
            fetch_jobicy_jobs(query, ""),
            fetch_arbeitnow_jobs(query, ""),
            fetch_himalayas_jobs(query, ""),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
    
    sources_searched.extend(["RemoteOK", "Remotive", "Jobicy", "Arbeitnow", "Himalayas"])
    
    # Deduplicate
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Filter and score by relevance
    keywords = search_strategy.get('keywords', ['quality', 'auditor', 'medical', 'supplier'])
    relevant_jobs = filter_jobs_by_relevance(unique_jobs, keywords)
    
    return {
        "jobs": relevant_jobs[:300],
        "total_found": len(relevant_jobs),
        "search_strategy": search_strategy,
        "queries_used": search_queries[:6],
        "sources_searched": list(set(sources_searched)),
        "jobspy_enabled": JOBSPY_AVAILABLE,
        "google_cse_enabled": bool(GOOGLE_API_KEY)
    }

# Quick search presets - TheirStack inspired with technology and industry filters
@api_router.get("/jobs/presets")
async def get_search_presets():
    return {
        "presets": [
            {"id": "supplier-quality-manager", "name": "Supplier Quality Manager", "query": "Supplier Quality Manager", "icon": "shield-check"},
            {"id": "supplier-quality-director", "name": "Supplier Quality Director", "query": "Supplier Quality Director", "icon": "award"},
            {"id": "quality-manager", "name": "Quality Manager", "query": "Quality Manager", "icon": "check-circle"},
            {"id": "quality-director", "name": "Quality Director", "query": "Quality Director", "icon": "award"},
            {"id": "lead-auditor", "name": "Lead Auditor", "query": "Lead Auditor", "icon": "search"},
            {"id": "medical-device", "name": "Medical Device", "query": "Medical Device Quality", "icon": "heart-pulse"},
            {"id": "manufacturing-quality", "name": "Manufacturing Quality", "query": "Manufacturing Quality", "icon": "settings"},
            {"id": "regulatory-compliance", "name": "Regulatory Compliance", "query": "Regulatory Compliance", "icon": "file-text"},
            {"id": "iso-auditor", "name": "ISO Auditor", "query": "ISO Auditor", "icon": "check-circle"},
            {"id": "fda-compliance", "name": "FDA Compliance", "query": "FDA Compliance", "icon": "shield-check"},
        ],
        "locations": [
            "Worldwide", "USA", "Europe", "UK", "Canada", "Germany", "Remote"
        ],
        "industries": [
            "Medical Devices", "Pharmaceutical", "Healthcare", "Biotechnology", 
            "Manufacturing", "Automotive", "Aerospace", "Electronics", "Consumer Goods"
        ],
        "technologies": [
            "ISO 13485", "ISO 9001", "FDA 21 CFR 820", "EU MDR", "GMP", "CGMP",
            "Six Sigma", "Lean Manufacturing", "SAP", "Oracle", "Minitab",
            "Quality Management Systems", "ERP", "MES"
        ],
        "salary_ranges": [
            {"label": "Any", "min": 0, "max": 0},
            {"label": "$50k-$80k", "min": 50000, "max": 80000},
            {"label": "$80k-$120k", "min": 80000, "max": 120000},
            {"label": "$120k-$150k", "min": 120000, "max": 150000},
            {"label": "$150k+", "min": 150000, "max": 500000}
        ],
        "quality_terms": QUALITY_SEARCH_TERMS
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

# Saved jobs
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

# Applications
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
    
    result = await db.applications.update_one({"id": app_id}, {"$set": update_data})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application updated"}

@api_router.delete("/applications/{app_id}")
async def delete_application(app_id: str):
    result = await db.applications.delete_one({"id": app_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    return {"message": "Application deleted"}

# Job Alerts
@api_router.post("/alerts")
async def create_job_alert(data: JobAlertCreate):
    alert = JobAlert(keywords=data.keywords, locations=data.locations, email=data.email)
    doc = alert.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.job_alerts.insert_one(doc)
    return alert

@api_router.get("/alerts")
async def get_job_alerts():
    return await db.job_alerts.find({}, {"_id": 0}).to_list(100)

@api_router.delete("/alerts/{alert_id}")
async def delete_job_alert(alert_id: str):
    result = await db.job_alerts.delete_one({"id": alert_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted"}

@api_router.post("/alerts/send-now")
async def send_job_alert_now(background_tasks: BackgroundTasks, data: EmailAlertRequest):
    """Send comprehensive job alert email with AI-powered search"""
    resume_doc = await db.resumes.find_one({}, {"_id": 0})
    skills = resume_doc.get('skills', []) if resume_doc else []
    
    # Use AI to generate search strategy
    search_strategy = await ai_deep_crawl(skills)
    search_queries = search_strategy.get('search_queries', QUALITY_SEARCH_TERMS)[:10]
    
    all_jobs = []
    
    # Search with multiple queries
    for query in search_queries[:6]:
        tasks = [
            fetch_remoteok_jobs(query, ""),
            fetch_remotive_jobs(query, ""),
            fetch_jobicy_jobs(query, ""),
            fetch_arbeitnow_jobs(query, ""),
            fetch_himalayas_jobs(query, ""),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
    
    # Deduplicate and filter
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job['title'].lower()}_{job['company'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    # Score by relevance
    keywords = search_strategy.get('keywords', ['quality', 'auditor', 'medical', 'supplier'])
    relevant_jobs = filter_jobs_by_relevance(unique_jobs, keywords)
    
    if not relevant_jobs:
        return {"message": "No matching jobs found", "jobs_count": 0}
    
    # Generate and send email
    html_content = generate_job_alert_html(relevant_jobs[:15], search_queries[:5])
    
    def send_email_task():
        send_email_gmail(
            data.email,
            f"MedMatch: {len(relevant_jobs)} Quality/Medical Device Jobs Found",
            html_content
        )
    
    background_tasks.add_task(send_email_task)
    
    return {
        "message": f"Job alert sent to {data.email}",
        "jobs_count": len(relevant_jobs),
        "queries_used": search_queries[:6]
    }

@api_router.post("/jobs/manual")
async def create_manual_job(job: ManualJobCreate):
    new_job = Job(
        title=job.title, company=job.company, location=job.location,
        description=job.description, url=job.url, salary=job.salary,
        tags=job.tags, source="Manual"
    )
    return new_job

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
