"""
Jobs Routes
Handles: Job search, job alerts, applications, saved jobs, manual job entry
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import logging
import asyncio
import httpx
import hashlib

from utils.database import db
from utils.config import EMERGENT_LLM_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID
from routes.auth import get_current_user

router = APIRouter(tags=["Jobs"])

# ============== Quality Engineering Search Terms ==============
# Expanded search keywords for Quality/Medical Device professionals
QUALITY_ENGINEERING_KEYWORDS = [
    # Supplier Quality
    "Supplier Quality Manager",
    "Supplier Quality Engineer",
    "Supplier Quality Director",
    "Vendor Quality",
    "Supply Chain Quality",
    
    # Manufacturing Quality
    "Manufacturing Quality Engineer",
    "Manufacturing Quality Manager",
    "Production Quality",
    "Process Quality Engineer",
    "Quality Control Manager",
    "QC Engineer",
    
    # Quality Management
    "Quality Manager",
    "Quality Director",
    "VP of Quality",
    "Head of Quality",
    "Quality Assurance Manager",
    "QA Manager",
    "QA Engineer",
    "Quality Systems Manager",
    "QMS Manager",
    
    # Regulatory & Compliance
    "Regulatory Compliance",
    "Compliance Manager",
    "FDA Compliance",
    "ISO 13485",
    "ISO 9001",
    "GMP Quality",
    "cGMP",
    
    # Medical Device
    "Medical Device Quality",
    "Medical Device QA",
    "Design Quality Engineer",
    "Post-Market Quality",
    
    # Auditing
    "Lead Auditor",
    "Quality Auditor",
    "Internal Auditor",
    "Audit Manager",
    
    # Six Sigma / Lean
    "Six Sigma Black Belt",
    "Six Sigma Green Belt",
    "Lean Manufacturing",
    "Continuous Improvement Manager",
    "Process Improvement",
    
    # Specialized
    "CAPA Manager",
    "Corrective Action",
    "Root Cause Analysis",
    "Metrology Engineer",
    "Calibration Manager",
    "Validation Engineer",
    "Quality Validation",
    
    # Automotive/Aerospace
    "IATF 16949",
    "AS9100",
    "Automotive Quality",
    "Aerospace Quality"
]

# ============== Models ==============

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

class ManualJobCreate(BaseModel):
    title: str
    company: str
    location: str = "Remote"
    description: str
    url: str = ""
    salary: str = ""
    tags: List[str] = []

class ApplicationCreate(BaseModel):
    job: Job
    notes: str = ""

class ApplicationStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class JobAlertCreate(BaseModel):
    keywords: List[str]
    locations: List[str] = []
    email: str

class QuickApplyRequest(BaseModel):
    job: Job

# Job board sites
GOOGLE_CSE_JOB_SITES = [
    "indeed.com/viewjob", "linkedin.com/jobs", "glassdoor.com/job-listing",
    "ziprecruiter.com/jobs", "monster.com/job", "careerbuilder.com/job",
    "dice.com/jobs", "simplyhired.com/job"
]

# ============== Job Search Routes ==============

@router.get("/jobs/quality-keywords")
async def get_quality_engineering_keywords():
    """Get suggested search keywords for Quality Engineering professionals"""
    # Group keywords by category
    categories = {
        "Supplier Quality": [
            "Supplier Quality Manager", "Supplier Quality Engineer", 
            "Supplier Quality Director", "Vendor Quality", "Supply Chain Quality"
        ],
        "Manufacturing Quality": [
            "Manufacturing Quality Engineer", "Manufacturing Quality Manager",
            "Production Quality", "Process Quality Engineer", "QC Engineer"
        ],
        "Quality Management": [
            "Quality Manager", "Quality Director", "VP of Quality",
            "Quality Assurance Manager", "QA Manager", "QMS Manager"
        ],
        "Regulatory & Compliance": [
            "Regulatory Compliance", "FDA Compliance", "ISO 13485",
            "ISO 9001", "GMP Quality", "cGMP"
        ],
        "Medical Device": [
            "Medical Device Quality", "Medical Device QA", 
            "Design Quality Engineer", "Post-Market Quality"
        ],
        "Auditing": [
            "Lead Auditor", "Quality Auditor", "Internal Auditor", "Audit Manager"
        ],
        "Six Sigma / Lean": [
            "Six Sigma Black Belt", "Six Sigma Green Belt",
            "Lean Manufacturing", "Continuous Improvement Manager"
        ],
        "Specialized": [
            "CAPA Manager", "Root Cause Analysis", "Metrology Engineer",
            "Calibration Manager", "Validation Engineer"
        ],
        "Industry Specific": [
            "IATF 16949", "AS9100", "Automotive Quality", "Aerospace Quality"
        ]
    }
    
    return {
        "keywords": QUALITY_ENGINEERING_KEYWORDS,
        "categories": categories,
        "popular_searches": [
            "Supplier Quality Manager Remote",
            "Quality Engineer Medical Device",
            "ISO 13485 Quality Manager",
            "Six Sigma Black Belt Remote",
            "FDA Compliance Manager"
        ]
    }

@router.get("/jobs/search")
async def search_jobs(
    q: str = "",
    location: str = "Remote",
    sources: str = "all"
):
    """Search for jobs across multiple sources"""
    all_jobs = []
    
    # Fetch from multiple sources in parallel
    tasks = []
    
    if sources in ["all", "remoteok"]:
        tasks.append(fetch_remoteok_jobs(q, location))
    if sources in ["all", "remotive"]:
        tasks.append(fetch_remotive_jobs(q, location))
    if sources in ["all", "jobicy"]:
        tasks.append(fetch_jobicy_jobs(q, location))
    if sources in ["all", "arbeitnow"]:
        tasks.append(fetch_arbeitnow_jobs(q, location))
    if sources in ["all", "himalayas"]:
        tasks.append(fetch_himalayas_jobs(q, location))
    
    # Google CSE if configured
    if GOOGLE_API_KEY and GOOGLE_CSE_ID and sources in ["all", "google"]:
        for site in GOOGLE_CSE_JOB_SITES[:3]:
            tasks.append(fetch_google_cse_jobs(q, location, site))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, list):
            all_jobs.extend(result)
    
    # Deduplicate by URL
    seen_urls = set()
    unique_jobs = []
    for job in all_jobs:
        job_url = job.get("url", "")
        if job_url and job_url not in seen_urls:
            seen_urls.add(job_url)
            unique_jobs.append(job)
        elif not job_url:
            unique_jobs.append(job)
    
    return {"jobs": unique_jobs[:100], "total": len(unique_jobs)}

@router.post("/jobs/manual")
async def create_manual_job(job: ManualJobCreate, request: Request):
    """Create a manual job entry"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    job_doc = {
        "id": str(uuid.uuid4()),
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "description": job.description,
        "url": job.url,
        "salary": job.salary,
        "tags": job.tags,
        "source": "Manual Entry",
        "posted_at": datetime.now(timezone.utc).isoformat(),
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.manual_jobs.insert_one(job_doc)
    job_doc.pop("_id", None)
    return {"message": "Job created", "job": job_doc}

# ============== Applications Routes ==============

@router.get("/applications")
async def get_applications(request: Request):
    """Get user's job applications"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    applications = await db.applications.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("applied_at", -1).to_list(500)
    
    return applications

@router.post("/applications")
async def create_application(app_data: ApplicationCreate, request: Request):
    """Create a new job application"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check for duplicate
    existing = await db.applications.find_one({
        "user_id": user["user_id"],
        "job.url": app_data.job.url
    }, {"_id": 0})
    
    if existing:
        return {"message": "Already applied", "application": existing, "duplicate": True}
    
    application = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "job": app_data.job.model_dump(),
        "status": "Applied",
        "job_status": "Active",
        "notes": app_data.notes,
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.applications.insert_one(application)
    # Remove MongoDB _id before returning
    application.pop("_id", None)
    return {"message": "Application recorded", "application": application}

@router.post("/applications/quick-apply")
async def quick_apply(data: QuickApplyRequest, request: Request):
    """Quick apply - records application and returns job URL"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    job_url = data.job.url
    
    # Check if already applied
    existing = await db.applications.find_one({
        "user_id": user["user_id"],
        "job.url": job_url
    }, {"_id": 0})
    
    if existing:
        return {"redirect_url": job_url, "already_applied": True, "application_id": existing.get("id")}
    
    # Record application
    application = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "job": data.job.model_dump(),
        "status": "Applied",
        "job_status": "Active",
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "external_url": job_url
    }
    
    await db.applications.insert_one(application)
    
    return {"redirect_url": job_url, "already_applied": False, "application_id": application["id"]}

@router.get("/applications/check/{url:path}")
async def check_application(url: str, request: Request):
    """Check if user has already applied to a job"""
    user = await get_current_user(request)
    if not user:
        return {"applied": False}
    
    existing = await db.applications.find_one({
        "user_id": user["user_id"],
        "job.url": url
    }, {"_id": 0})
    
    return {"applied": existing is not None, "application": existing if existing else None}

@router.put("/applications/{app_id}/status")
async def update_application_status(app_id: str, update: ApplicationStatusUpdate, request: Request):
    """Update application status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    update_data = {"status": update.status, "updated_at": datetime.now(timezone.utc).isoformat()}
    if update.notes:
        update_data["notes"] = update.notes
    
    result = await db.applications.update_one(
        {"id": app_id, "user_id": user["user_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": "Status updated"}

@router.put("/applications/{app_id}/job-status")
async def update_job_status(app_id: str, request: Request, job_status: str = "Active"):
    """Update the job posting status (Active, Closed, Filled)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.applications.update_one(
        {"id": app_id, "user_id": user["user_id"]},
        {"$set": {"job_status": job_status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": f"Job status updated to {job_status}"}

@router.delete("/applications/{app_id}")
async def delete_application(app_id: str, request: Request):
    """Delete an application"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.applications.delete_one({"id": app_id, "user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Application not found")
    
    return {"message": "Application deleted"}

# ============== Saved Jobs Routes ==============

@router.get("/saved-jobs")
async def get_saved_jobs(request: Request):
    """Get user's saved jobs"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    saved = await db.saved_jobs.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("saved_at", -1).to_list(500)
    
    return saved

@router.post("/saved-jobs")
async def save_job(job: Job, request: Request):
    """Save a job for later"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    saved_job = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "job": job.model_dump(),
        "saved_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.saved_jobs.insert_one(saved_job)
    saved_job.pop("_id", None)
    return {"message": "Job saved", "saved_job": saved_job}

@router.delete("/saved-jobs/{job_id}")
async def unsave_job(job_id: str, request: Request):
    """Remove a saved job"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.saved_jobs.delete_one({"id": job_id, "user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Saved job not found")
    
    return {"message": "Job removed from saved"}

# ============== Job Alerts Routes ==============

@router.get("/job-alerts")
async def get_job_alerts(request: Request):
    """Get user's job alerts"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    alerts = await db.job_alerts.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).to_list(50)
    
    return alerts

@router.post("/job-alerts")
async def create_job_alert(alert: JobAlertCreate, request: Request):
    """Create a new job alert"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    alert_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "keywords": alert.keywords,
        "locations": alert.locations,
        "email": alert.email or user["email"],
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.job_alerts.insert_one(alert_doc)
    alert_doc.pop("_id", None)
    return {"message": "Alert created", "alert": alert_doc}

@router.delete("/job-alerts/{alert_id}")
async def delete_job_alert(alert_id: str, request: Request):
    """Delete a job alert"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.job_alerts.delete_one({"id": alert_id, "user_id": user["user_id"]})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert deleted"}

# ============== Helper Functions ==============

async def fetch_remoteok_jobs(query: str = "", location: str = "") -> List[dict]:
    """Fetch jobs from RemoteOK API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://remoteok.com/api",
                headers={"User-Agent": "MedMatch/1.0"},
                timeout=15.0
            )
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for item in data[1:21]:  # Skip first (legal) item
                    if query.lower() in str(item).lower() or not query:
                        jobs.append({
                            "id": str(item.get("id", uuid.uuid4())),
                            "title": item.get("position", ""),
                            "company": item.get("company", ""),
                            "location": item.get("location", "Remote"),
                            "description": item.get("description", "")[:500],
                            "url": item.get("url", ""),
                            "salary": item.get("salary", ""),
                            "tags": item.get("tags", []),
                            "source": "RemoteOK",
                            "posted_at": item.get("date", "")
                        })
                return jobs
    except Exception as e:
        logging.error(f"RemoteOK error: {e}")
    return []

async def fetch_remotive_jobs(query: str = "", location: str = "") -> List[dict]:
    """Fetch jobs from Remotive API"""
    try:
        async with httpx.AsyncClient() as client:
            params = {"limit": 20}
            if query:
                params["search"] = query
            response = await client.get(
                "https://remotive.com/api/remote-jobs",
                params=params,
                timeout=15.0
            )
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for item in data.get("jobs", [])[:20]:
                    jobs.append({
                        "id": str(item.get("id", uuid.uuid4())),
                        "title": item.get("title", ""),
                        "company": item.get("company_name", ""),
                        "location": item.get("candidate_required_location", "Remote"),
                        "description": item.get("description", "")[:500],
                        "url": item.get("url", ""),
                        "salary": item.get("salary", ""),
                        "tags": [item.get("category", "")],
                        "source": "Remotive",
                        "posted_at": item.get("publication_date", "")
                    })
                return jobs
    except Exception as e:
        logging.error(f"Remotive error: {e}")
    return []

async def fetch_jobicy_jobs(query: str = "", location: str = "") -> List[dict]:
    """Fetch jobs from Jobicy API"""
    try:
        async with httpx.AsyncClient() as client:
            params = {"count": 20, "geo": "usa"}
            if query:
                params["tag"] = query
            response = await client.get(
                "https://jobicy.com/api/v2/remote-jobs",
                params=params,
                timeout=15.0
            )
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for item in data.get("jobs", [])[:20]:
                    jobs.append({
                        "id": str(uuid.uuid4()),
                        "title": item.get("jobTitle", ""),
                        "company": item.get("companyName", ""),
                        "location": item.get("jobGeo", "Remote"),
                        "description": item.get("jobExcerpt", "")[:500],
                        "url": item.get("url", ""),
                        "salary": f"{item.get('annualSalaryMin', '')}-{item.get('annualSalaryMax', '')}",
                        "tags": [item.get("jobIndustry", "")],
                        "source": "Jobicy",
                        "posted_at": item.get("pubDate", "")
                    })
                return jobs
    except Exception as e:
        logging.error(f"Jobicy error: {e}")
    return []

async def fetch_arbeitnow_jobs(query: str = "", location: str = "") -> List[dict]:
    """Fetch jobs from Arbeitnow API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.arbeitnow.com/api/job-board-api",
                timeout=15.0
            )
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for item in data.get("data", [])[:20]:
                    if query.lower() in str(item).lower() or not query:
                        jobs.append({
                            "id": str(item.get("slug", uuid.uuid4())),
                            "title": item.get("title", ""),
                            "company": item.get("company_name", ""),
                            "location": item.get("location", "Remote"),
                            "description": item.get("description", "")[:500],
                            "url": item.get("url", ""),
                            "tags": item.get("tags", []),
                            "source": "Arbeitnow",
                            "posted_at": item.get("created_at", "")
                        })
                return jobs
    except Exception as e:
        logging.error(f"Arbeitnow error: {e}")
    return []

async def fetch_himalayas_jobs(query: str = "", location: str = "") -> List[dict]:
    """Fetch jobs from Himalayas API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://himalayas.app/jobs/api",
                params={"limit": 20},
                timeout=15.0
            )
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for item in data.get("jobs", [])[:20]:
                    if query.lower() in str(item).lower() or not query:
                        jobs.append({
                            "id": str(item.get("id", uuid.uuid4())),
                            "title": item.get("title", ""),
                            "company": item.get("companyName", ""),
                            "location": "Remote",
                            "description": item.get("description", "")[:500],
                            "url": item.get("applicationLink", ""),
                            "tags": item.get("categories", []),
                            "source": "Himalayas",
                            "posted_at": item.get("pubDate", "")
                        })
                return jobs
    except Exception as e:
        logging.error(f"Himalayas error: {e}")
    return []

async def fetch_google_cse_jobs(query: str, location: str = "Remote", site: str = "indeed.com", num_results: int = 10) -> List[dict]:
    """Fetch jobs using Google Custom Search"""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return []
    
    try:
        search_query = f"{query} {location} site:{site}"
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={
                    "key": GOOGLE_API_KEY,
                    "cx": GOOGLE_CSE_ID,
                    "q": search_query,
                    "num": num_results
                },
                timeout=15.0
            )
            if response.status_code == 200:
                data = response.json()
                jobs = []
                for item in data.get("items", []):
                    jobs.append({
                        "id": str(uuid.uuid4()),
                        "title": item.get("title", "").split(" - ")[0],
                        "company": item.get("pagemap", {}).get("organization", [{}])[0].get("name", ""),
                        "location": location,
                        "description": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "source": f"Google ({site.split('.')[0].title()})",
                        "posted_at": ""
                    })
                return jobs
    except Exception as e:
        logging.error(f"Google CSE error: {e}")
    return []
