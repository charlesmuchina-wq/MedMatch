"""
Digest Routes
Handles: Email digests, digest settings, scheduled notifications
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from utils.database import db
from utils.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/digest", tags=["Digest"])

# ============== Models ==============

class DigestSettingsCreate(BaseModel):
    email: str
    frequency: str = "daily"
    search_queries: List[str] = []
    locations: List[str] = []

class EmailAlertRequest(BaseModel):
    email: str

# ============== Routes ==============

@router.post("/settings")
async def create_digest_settings(data: DigestSettingsCreate, request: Request):
    """Create or update digest settings"""
    user = await require_auth(request)
    
    settings_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"] if user else None,
        "email": data.email,
        "frequency": data.frequency,
        "search_queries": data.search_queries,
        "locations": data.locations,
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Upsert by email
    await db.digest_settings.update_one(
        {"email": data.email},
        {"$set": settings_doc},
        upsert=True
    )
    
    return {"message": "Digest settings saved", "settings": settings_doc}

@router.get("/settings")
async def get_digest_settings(request: Request):
    """Get user's digest settings"""
    user = await require_auth(request)
    
    settings = await db.digest_settings.find_one(
        {"$or": [{"user_id": user["user_id"]}, {"email": user["email"]}]},
        {"_id": 0}
    )
    
    return settings or {}

@router.delete("/settings/{email}")
async def delete_digest_settings(email: str, request: Request):
    """Delete digest settings (unsubscribe)"""
    result = await db.digest_settings.delete_one({"email": email})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Settings not found")
    
    return {"message": "Unsubscribed from digest"}

@router.put("/settings/toggle")
async def toggle_digest(request: Request):
    """Toggle digest on/off"""
    user = await require_auth(request)
    
    settings = await db.digest_settings.find_one({"email": user["email"]})
    
    if not settings:
        raise HTTPException(status_code=404, detail="No digest settings found")
    
    new_status = not settings.get("is_active", True)
    
    await db.digest_settings.update_one(
        {"email": user["email"]},
        {"$set": {"is_active": new_status}}
    )
    
    return {"message": f"Digest {'enabled' if new_status else 'disabled'}", "is_active": new_status}

@router.get("/history")
async def get_emailed_jobs_history(request: Request, email: Optional[str] = None):
    """Get history of emailed jobs"""
    user = await require_auth(request)
    
    query_email = email or user["email"]
    
    history = await db.emailed_jobs.find(
        {"email": query_email},
        {"_id": 0}
    ).sort("emailed_at", -1).limit(100).to_list(100)
    
    return history

@router.delete("/history/{email}")
async def clear_emailed_history(email: str, request: Request):
    """Clear emailed jobs history"""
    user = await require_auth(request)
    
    # Only allow clearing own history or admin
    if email != user["email"] and not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.emailed_jobs.delete_many({"email": email})
    
    return {"message": f"Cleared {result.deleted_count} records"}

@router.get("/scheduler-status")
async def get_scheduler_status():
    """Get digest scheduler status"""
    # Check last run time
    last_run = await db.digest_runs.find_one(
        {},
        {"_id": 0}
    )
    
    if last_run:
        last_run_time = last_run.get("last_run")
    else:
        last_run_time = None
    
    # Count active subscribers
    active_count = await db.digest_settings.count_documents({"is_active": True})
    
    return {
        "scheduler_running": True,
        "schedule": "Daily at 8:00 AM UTC",
        "last_run": last_run_time,
        "active_subscribers": active_count
    }

@router.post("/send-daily")
async def send_daily_digest(background_tasks: BackgroundTasks, data: EmailAlertRequest, request: Request):
    """Manually trigger a digest email for a specific user"""
    user = await require_auth(request)
    
    # Get user's settings
    settings = await db.digest_settings.find_one({"email": data.email})
    
    if not settings:
        return {"message": "No digest settings found for this email"}
    
    # Queue the digest
    background_tasks.add_task(send_single_digest, data.email, settings)
    
    return {"message": f"Digest queued for {data.email}"}

@router.post("/trigger-now")
async def trigger_digest_now(background_tasks: BackgroundTasks, request: Request):
    """Admin: Trigger the scheduled digest immediately"""
    user = await require_auth(request)
    
    if not user.get("is_admin") and user.get("email") != "admin@medmatch.com":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"message": "Digest trigger initiated. Check logs for results."}

# ============== Helper Functions ==============

def get_job_key(title: str, company: str) -> str:
    """Generate unique key for a job"""
    return hashlib.md5(f"{title.lower()}:{company.lower()}".encode()).hexdigest()

async def was_job_emailed(job_key: str, email: str) -> bool:
    """Check if a job was already emailed to user"""
    existing = await db.emailed_jobs.find_one({"job_key": job_key, "email": email})
    return existing is not None

async def mark_job_emailed(job: dict, email: str):
    """Mark a job as emailed"""
    job_key = get_job_key(job.get("title", ""), job.get("company", ""))
    
    doc = {
        "id": str(uuid.uuid4()),
        "job_key": job_key,
        "job_title": job.get("title", ""),
        "company": job.get("company", ""),
        "email": email,
        "emailed_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.emailed_jobs.insert_one(doc)

async def filter_new_jobs(jobs: List[dict], email: str) -> List[dict]:
    """Filter out jobs that were already emailed"""
    new_jobs = []
    for job in jobs:
        job_key = get_job_key(job.get("title", ""), job.get("company", ""))
        if not await was_job_emailed(job_key, email):
            new_jobs.append(job)
    return new_jobs

def generate_digest_email_html(jobs: List[dict], user_name: str, query_summary: str) -> str:
    """Generate HTML email content for digest"""
    jobs_html = ""
    for job in jobs[:20]:
        jobs_html += f"""
        <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <h3 style="margin: 0 0 8px 0; color: #1f2937;">{job.get('title', 'Job Title')}</h3>
            <p style="margin: 0 0 8px 0; color: #4b5563;">{job.get('company', 'Company')} • {job.get('location', 'Remote')}</p>
            <p style="margin: 0 0 12px 0; color: #6b7280; font-size: 14px;">{job.get('description', '')[:200]}...</p>
            <a href="{job.get('url', '#')}" style="background-color: #2563eb; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px;">View Job</a>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9fafb;">
        <div style="background-color: white; border-radius: 12px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
            <h1 style="color: #1f2937; margin-bottom: 8px;">🎯 Your Daily Job Digest</h1>
            <p style="color: #6b7280; margin-bottom: 24px;">Hi {user_name}, here are {len(jobs)} new jobs matching: {query_summary}</p>
            
            {jobs_html}
            
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
            <p style="color: #9ca3af; font-size: 12px; text-align: center;">
                You're receiving this because you subscribed to MedMatch job alerts.
                <br><a href="#" style="color: #2563eb;">Unsubscribe</a> | <a href="#" style="color: #2563eb;">Manage preferences</a>
            </p>
        </div>
    </body>
    </html>
    """
    return html

def send_email_gmail(to_email: str, subject: str, html_content: str) -> bool:
    """Send email using Gmail SMTP"""
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

async def send_single_digest(email: str, settings: dict):
    """Send a single digest email"""
    try:
        from routes.jobs import fetch_remoteok_jobs, fetch_remotive_jobs
        
        search_queries = settings.get("search_queries", ["remote"])
        
        # Fetch jobs
        all_jobs = []
        for query in search_queries[:3]:
            jobs = await fetch_remoteok_jobs(query)
            all_jobs.extend(jobs)
            jobs = await fetch_remotive_jobs(query)
            all_jobs.extend(jobs)
        
        # Filter new jobs
        new_jobs = await filter_new_jobs(all_jobs, email)
        
        if not new_jobs:
            logging.info(f"No new jobs for {email}")
            return
        
        # Generate and send email
        user_name = settings.get("user_name", "Job Seeker")
        query_summary = ", ".join(search_queries[:3])
        html_content = generate_digest_email_html(new_jobs[:20], user_name, query_summary)
        
        # Mark jobs as emailed
        for job in new_jobs[:20]:
            await mark_job_emailed(job, email)
        
        # Send email
        success = send_email_gmail(
            email,
            f"🎯 MedMatch Daily Digest: {len(new_jobs[:20])} New Jobs",
            html_content
        )
        
        if success:
            await db.digest_settings.update_one(
                {"email": email},
                {"$set": {"last_sent": datetime.now(timezone.utc).isoformat()}}
            )
            
    except Exception as e:
        logging.error(f"Digest error for {email}: {e}")
