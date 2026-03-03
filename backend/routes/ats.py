"""
Application Tracking System Routes
Handles: Application links, status tracking, email notifications
Similar to GiftJob, Greenhouse, Lever ATS standards
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import secrets
import logging

from utils.database import db
from routes.auth import get_current_user, require_auth
from services.email_service import (
    send_application_status_email,
    send_application_invitation_email,
    APPLICATION_STATUSES
)
from utils.push_service import notify_application_update

router = APIRouter(prefix="/ats", tags=["Application Tracking"])
logger = logging.getLogger(__name__)

# ============== Models ==============

class ApplicationLinkCreate(BaseModel):
    job_id: str
    expires_in_days: int = 30
    max_applications: Optional[int] = None
    require_resume: bool = True
    custom_questions: Optional[List[Dict[str, Any]]] = None

class ApplicationInvite(BaseModel):
    candidate_email: EmailStr
    candidate_name: Optional[str] = None
    personal_message: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str
    recruiter_message: Optional[str] = None
    interview_details: Optional[Dict[str, Any]] = None
    send_email: bool = True

class ExternalApplication(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    cover_letter: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    custom_answers: Optional[Dict[str, Any]] = None
    source: Optional[str] = "application_link"

class BulkStatusUpdate(BaseModel):
    application_ids: List[str]
    status: str
    recruiter_message: Optional[str] = None
    send_email: bool = True

# ============== Application Link Management ==============

@router.post("/links")
async def create_application_link(data: ApplicationLinkCreate, request: Request):
    """
    Create a shareable application link for a job posting
    Recruiters can share this link to invite candidates to apply
    """
    user = await require_auth(request)
    
    if user.get("role") not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Only recruiters can create application links")
    
    # Verify job belongs to recruiter (or user is admin)
    query = {"id": data.job_id}
    if user.get("role") != "admin":
        query["recruiter_id"] = user["user_id"]
    
    job = await db.posted_jobs.find_one(query, {"_id": 0})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Generate unique link token
    link_token = secrets.token_urlsafe(24)
    link_id = f"link_{uuid.uuid4().hex[:12]}"
    
    link_doc = {
        "id": link_id,
        "token": link_token,
        "job_id": data.job_id,
        "recruiter_id": user["user_id"],
        "job_title": job.get("title"),
        "company": job.get("company"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)).isoformat() if data.expires_in_days else None,
        "max_applications": data.max_applications,
        "current_applications": 0,
        "require_resume": data.require_resume,
        "custom_questions": data.custom_questions or [],
        "active": True,
        "views": 0
    }
    
    await db.application_links.insert_one(link_doc)
    
    # Generate shareable URL
    app_url = "https://realtime-simulations.preview.emergentagent.com"
    application_url = f"{app_url}/apply/{link_token}"
    
    return {
        "link_id": link_id,
        "application_url": application_url,
        "token": link_token,
        "job_title": job.get("title"),
        "company": job.get("company"),
        "expires_at": link_doc["expires_at"],
        "max_applications": data.max_applications
    }

@router.get("/links")
async def list_application_links(request: Request):
    """List all application links for the recruiter"""
    user = await require_auth(request)
    
    links = await db.application_links.find(
        {"recruiter_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {"links": links, "count": len(links)}

@router.delete("/links/{link_id}")
async def deactivate_application_link(link_id: str, request: Request):
    """Deactivate an application link"""
    user = await require_auth(request)
    
    result = await db.application_links.update_one(
        {"id": link_id, "recruiter_id": user["user_id"]},
        {"$set": {"active": False, "deactivated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return {"message": "Application link deactivated"}

# ============== Public Application Endpoints ==============

@router.get("/apply/{token}")
async def get_application_form(token: str):
    """
    Get application form details (public endpoint)
    Used by job seekers who receive an application link
    """
    link = await db.application_links.find_one(
        {"token": token, "active": True},
        {"_id": 0}
    )
    
    if not link:
        raise HTTPException(status_code=404, detail="Application link not found or expired")
    
    # Check expiration
    if link.get("expires_at"):
        expires = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires:
            raise HTTPException(status_code=410, detail="Application link has expired")
    
    # Check max applications
    if link.get("max_applications") and link.get("current_applications", 0) >= link["max_applications"]:
        raise HTTPException(status_code=410, detail="This position has reached maximum applications")
    
    # Increment view count
    await db.application_links.update_one(
        {"token": token},
        {"$inc": {"views": 1}}
    )
    
    # Get full job details
    job = await db.posted_jobs.find_one(
        {"id": link["job_id"]},
        {"_id": 0}
    )
    
    return {
        "job": {
            "id": link["job_id"],
            "title": link["job_title"],
            "company": link["company"],
            "description": job.get("description") if job else "",
            "location": job.get("location") if job else "",
            "salary": job.get("salary") if job else "",
            "tags": job.get("tags", []) if job else []
        },
        "require_resume": link.get("require_resume", True),
        "custom_questions": link.get("custom_questions", []),
        "recruiter_name": link.get("recruiter_name")
    }

@router.post("/apply/{token}")
async def submit_external_application(
    token: str,
    application: ExternalApplication,
    background_tasks: BackgroundTasks
):
    """
    Submit an application via application link (public endpoint)
    No authentication required - anyone with the link can apply
    """
    link = await db.application_links.find_one(
        {"token": token, "active": True},
        {"_id": 0}
    )
    
    if not link:
        raise HTTPException(status_code=404, detail="Application link not found or expired")
    
    # Check expiration
    if link.get("expires_at"):
        expires = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
        if datetime.now(timezone.utc) > expires:
            raise HTTPException(status_code=410, detail="Application link has expired")
    
    # Check max applications
    if link.get("max_applications") and link.get("current_applications", 0) >= link["max_applications"]:
        raise HTTPException(status_code=410, detail="This position has reached maximum applications")
    
    # Check if already applied
    existing = await db.job_applicants.find_one({
        "job_id": link["job_id"],
        "email": application.email
    })
    if existing:
        raise HTTPException(status_code=409, detail="You have already applied for this position")
    
    # Generate tracking token for the applicant
    tracking_token = secrets.token_urlsafe(16)
    
    # Create application record
    application_id = f"app_{uuid.uuid4().hex[:12]}"
    application_doc = {
        "id": application_id,
        "job_id": link["job_id"],
        "job_title": link["job_title"],
        "company": link["company"],
        "recruiter_id": link["recruiter_id"],
        "link_id": link["id"],
        "tracking_token": tracking_token,
        
        # Applicant info
        "name": application.name,
        "email": application.email,
        "phone": application.phone,
        "resume_url": application.resume_url,
        "cover_letter": application.cover_letter,
        "linkedin_url": application.linkedin_url,
        "portfolio_url": application.portfolio_url,
        "custom_answers": application.custom_answers,
        
        # Status tracking
        "status": "received",
        "status_history": [{
            "status": "received",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "by": "system"
        }],
        
        # Metadata
        "source": application.source or "application_link",
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "notes": [],
        "tags": [],
        "rating": None
    }
    
    await db.job_applicants.insert_one(application_doc)
    
    # Update link application count
    await db.application_links.update_one(
        {"token": token},
        {"$inc": {"current_applications": 1}}
    )
    
    # Send confirmation email in background
    background_tasks.add_task(
        send_application_status_email,
        candidate_email=application.email,
        candidate_name=application.name,
        job_title=link["job_title"],
        company_name=link["company"],
        status="received",
        application_id=application_id,
        tracking_token=tracking_token
    )
    
    return {
        "message": "Application submitted successfully",
        "application_id": application_id,
        "tracking_token": tracking_token,
        "tracking_url": f"https://realtime-simulations.preview.emergentagent.com/track-application/{application_id}?token={tracking_token}"
    }

# ============== Application Tracking (Public) ==============

@router.get("/track/{application_id}")
async def track_application(application_id: str, token: Optional[str] = None):
    """
    Track application status (public endpoint with token verification)
    """
    query = {"id": application_id}
    if token:
        query["tracking_token"] = token
    
    application = await db.job_applicants.find_one(query, {"_id": 0, "tracking_token": 0})
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Get status config
    status_config = APPLICATION_STATUSES.get(application["status"], APPLICATION_STATUSES["received"])
    
    return {
        "application_id": application["id"],
        "job_title": application.get("job_title", ""),
        "company": application.get("company", ""),
        "status": application["status"],
        "status_label": status_config["label"],
        "status_description": status_config["description"],
        "status_emoji": status_config["emoji"],
        "applied_at": application["applied_at"],
        "status_history": application.get("status_history", []),
        "last_updated": application.get("status_updated_at", application["applied_at"])
    }

# ============== Recruiter Status Management ==============

@router.put("/applications/{application_id}/status")
async def update_application_status(
    application_id: str,
    status_update: StatusUpdate,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Update application status with optional email notification
    Enhanced version with more statuses and email support
    """
    user = await require_auth(request)
    
    if user.get("role") not in ["recruiter", "admin"]:
        raise HTTPException(status_code=403, detail="Only recruiters can update status")
    
    # Validate status
    if status_update.status not in APPLICATION_STATUSES:
        valid = list(APPLICATION_STATUSES.keys())
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid}")
    
    # Get application
    query = {"id": application_id}
    if user.get("role") != "admin":
        query["recruiter_id"] = user["user_id"]
    
    application = await db.job_applicants.find_one(query, {"_id": 0})
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update status
    status_entry = {
        "status": status_update.status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "by": user.get("name", user["email"]),
        "message": status_update.recruiter_message
    }
    
    update_data = {
        "status": status_update.status,
        "status_updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if status_update.interview_details:
        update_data["interview_details"] = status_update.interview_details
    
    await db.job_applicants.update_one(
        {"id": application_id},
        {
            "$set": update_data,
            "$push": {"status_history": status_entry}
        }
    )
    
    # Get job details for notification
    job = await db.posted_jobs.find_one({"id": application.get("job_id")}, {"_id": 0})
    job_title = job.get("title", "Position") if job else application.get("job_title", "Position")
    company = job.get("company", "Company") if job else application.get("company", "Company")
    
    # Send email notification if requested
    if status_update.send_email and application.get("email"):
        background_tasks.add_task(
            send_application_status_email,
            candidate_email=application["email"],
            candidate_name=application.get("name", "Applicant"),
            job_title=job_title,
            company_name=company,
            status=status_update.status,
            recruiter_message=status_update.recruiter_message,
            interview_details=status_update.interview_details,
            application_id=application_id,
            tracking_token=application.get("tracking_token")
        )
    
    # Send push notification if user has account
    if application.get("user_id"):
        status_config = APPLICATION_STATUSES[status_update.status]
        background_tasks.add_task(
            notify_application_update,
            user_id=application["user_id"],
            company=company,
            status=status_config["label"],
            application_id=application_id
        )
    
    return {
        "message": f"Status updated to {status_update.status}",
        "email_sent": status_update.send_email and bool(application.get("email")),
        "status_label": APPLICATION_STATUSES[status_update.status]["label"]
    }

@router.post("/applications/bulk-status")
async def bulk_update_status(
    bulk_update: BulkStatusUpdate,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Update status for multiple applications at once
    """
    user = await require_auth(request)
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can update status")
    
    if bulk_update.status not in APPLICATION_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    updated = 0
    emails_queued = 0
    
    for app_id in bulk_update.application_ids:
        application = await db.job_applicants.find_one(
            {"id": app_id, "recruiter_id": user["user_id"]},
            {"_id": 0}
        )
        
        if not application:
            continue
        
        # Update status
        status_entry = {
            "status": bulk_update.status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "by": user.get("name", user["email"]),
            "message": bulk_update.recruiter_message
        }
        
        await db.job_applicants.update_one(
            {"id": app_id},
            {
                "$set": {
                    "status": bulk_update.status,
                    "status_updated_at": datetime.now(timezone.utc).isoformat()
                },
                "$push": {"status_history": status_entry}
            }
        )
        updated += 1
        
        # Queue email
        if bulk_update.send_email and application.get("email"):
            job = await db.posted_jobs.find_one({"id": application.get("job_id")}, {"_id": 0})
            background_tasks.add_task(
                send_application_status_email,
                candidate_email=application["email"],
                candidate_name=application.get("name", "Applicant"),
                job_title=job.get("title", "Position") if job else "Position",
                company_name=job.get("company", "Company") if job else "Company",
                status=bulk_update.status,
                recruiter_message=bulk_update.recruiter_message,
                application_id=app_id,
                tracking_token=application.get("tracking_token")
            )
            emails_queued += 1
    
    return {
        "message": f"Updated {updated} applications",
        "updated_count": updated,
        "emails_queued": emails_queued
    }

# ============== Candidate Invitation ==============

@router.post("/invite")
async def invite_candidate_to_apply(
    invite: ApplicationInvite,
    job_id: str,
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Send email invitation to a candidate to apply for a position
    """
    user = await require_auth(request)
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can send invitations")
    
    # Get job details
    job = await db.posted_jobs.find_one({
        "id": job_id,
        "recruiter_id": user["user_id"]
    }, {"_id": 0})
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Create or get application link
    existing_link = await db.application_links.find_one({
        "job_id": job_id,
        "recruiter_id": user["user_id"],
        "active": True
    })
    
    if existing_link:
        link_token = existing_link["token"]
    else:
        # Create new link
        link_token = secrets.token_urlsafe(24)
        link_doc = {
            "id": f"link_{uuid.uuid4().hex[:12]}",
            "token": link_token,
            "job_id": job_id,
            "recruiter_id": user["user_id"],
            "job_title": job.get("title"),
            "company": job.get("company"),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "active": True,
            "views": 0
        }
        await db.application_links.insert_one(link_doc)
    
    # Generate application URL
    application_url = f"https://realtime-simulations.preview.emergentagent.com/apply/{link_token}"
    
    # Record invitation
    invitation_doc = {
        "id": f"inv_{uuid.uuid4().hex[:12]}",
        "job_id": job_id,
        "recruiter_id": user["user_id"],
        "candidate_email": invite.candidate_email,
        "candidate_name": invite.candidate_name,
        "personal_message": invite.personal_message,
        "application_url": application_url,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "sent"
    }
    await db.application_invitations.insert_one(invitation_doc)
    
    # Send invitation email
    background_tasks.add_task(
        send_application_invitation_email,
        candidate_email=invite.candidate_email,
        candidate_name=invite.candidate_name,
        job_title=job.get("title"),
        company_name=job.get("company"),
        recruiter_name=user.get("name", user["email"]),
        application_link=application_url,
        personal_message=invite.personal_message
    )
    
    return {
        "message": "Invitation sent successfully",
        "invitation_id": invitation_doc["id"],
        "application_url": application_url
    }

@router.get("/invitations")
async def list_invitations(job_id: Optional[str] = None, request: Request = None):
    """List all invitations sent by the recruiter"""
    user = await require_auth(request)
    
    query = {"recruiter_id": user["user_id"]}
    if job_id:
        query["job_id"] = job_id
    
    invitations = await db.application_invitations.find(
        query,
        {"_id": 0}
    ).sort("sent_at", -1).to_list(200)
    
    return {"invitations": invitations, "count": len(invitations)}

# ============== Application Statistics ==============

@router.get("/stats")
async def get_ats_statistics(request: Request):
    """Get ATS statistics for the recruiter"""
    user = await require_auth(request)
    
    recruiter_id = user["user_id"]
    
    # Get application counts by status
    pipeline = [
        {"$match": {"recruiter_id": recruiter_id}},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    status_counts = await db.job_applicants.aggregate(pipeline).to_list(20)
    
    # Get total applications
    total_applications = await db.job_applicants.count_documents({"recruiter_id": recruiter_id})
    
    # Get recent applications (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_applications = await db.job_applicants.count_documents({
        "recruiter_id": recruiter_id,
        "applied_at": {"$gte": week_ago}
    })
    
    # Get active links
    active_links = await db.application_links.count_documents({
        "recruiter_id": recruiter_id,
        "active": True
    })
    
    # Get invitations sent
    total_invitations = await db.application_invitations.count_documents({"recruiter_id": recruiter_id})
    
    return {
        "total_applications": total_applications,
        "recent_applications": recent_applications,
        "by_status": {item["_id"]: item["count"] for item in status_counts},
        "active_links": active_links,
        "invitations_sent": total_invitations,
        "available_statuses": APPLICATION_STATUSES
    }

# ============== Email Log (Admin) ==============

@router.get("/email-logs")
async def get_email_logs(limit: int = 50, request: Request = None):
    """Get email logs (admin/recruiter view)"""
    user = await require_auth(request)
    
    logs = await db.email_logs.find(
        {},
        {"_id": 0, "html": 0, "text": 0}  # Exclude large content
    ).sort("sent_at", -1).to_list(limit)
    
    return {"logs": logs, "count": len(logs)}
