"""
One-Click Apply, Team Collaboration, Multi-Channel Outreach
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/talent-tools", tags=["Talent Tools"])


# --- One-Click Apply ---

class OneClickApplyRequest(BaseModel):
    job_id: str

@router.post("/one-click-apply")
async def one_click_apply(req: OneClickApplyRequest, request: Request):
    """One-click apply using saved profile"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)

    # Check already applied
    existing = await db.applications.find_one(
        {"user_id": user["user_id"], "job_id": req.job_id}, {"_id": 0}
    )
    if existing:
        return {"status": "already_applied", "application_id": existing.get("id")}

    # Get job details
    job = await db.jobs.find_one({"id": req.job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get user profile/resume
    resume = await db.resumes.find_one({"user_id": user["user_id"]}, {"_id": 0})

    app_id = str(uuid.uuid4())
    application = {
        "id": app_id,
        "user_id": user["user_id"],
        "job_id": req.job_id,
        "job": {"title": job.get("title"), "company": job.get("company"), "url": job.get("url", "")},
        "applicant_name": user.get("name", ""),
        "applicant_email": user.get("email", ""),
        "resume_snapshot": {
            "skills": resume.get("skills", []) if resume else [],
            "experience_years": resume.get("experience_years", 0) if resume else 0,
            "summary": resume.get("summary", "") if resume else ""
        },
        "status": "Applied",
        "applied_via": "one-click",
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    await db.applications.insert_one(application)
    application.pop("_id", None)
    return {"status": "applied", "application_id": app_id, "job_title": job.get("title")}


# --- Team Collaboration ---

class CandidateComment(BaseModel):
    candidate_id: str
    job_id: Optional[str] = ""
    comment: str
    mentions: List[str] = []

class CollaborationThread(BaseModel):
    candidate_id: str
    job_id: Optional[str] = ""

@router.post("/collaborate/comment")
async def add_collaboration_comment(req: CandidateComment, request: Request):
    """Add a comment on a candidate for team collaboration"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)

    comment = {
        "id": str(uuid.uuid4()),
        "candidate_id": req.candidate_id,
        "job_id": req.job_id,
        "author_id": user["user_id"],
        "author_name": user.get("name", "Unknown"),
        "comment": req.comment,
        "mentions": req.mentions,
        "reactions": {},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.collaboration_comments.insert_one(comment)
    comment.pop("_id", None)

    # Create notifications for mentioned users
    for mentioned_id in req.mentions:
        await db.notifications.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": mentioned_id,
            "type": "mention",
            "title": f"{user.get('name', 'Someone')} mentioned you",
            "message": f"In a comment about candidate {req.candidate_id}",
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        })

    return comment


@router.get("/collaborate/comments/{candidate_id}")
async def get_collaboration_comments(candidate_id: str, job_id: Optional[str] = None, request: Request = None):
    """Get all collaboration comments for a candidate"""
    from server import db
    query = {"candidate_id": candidate_id}
    if job_id:
        query["job_id"] = job_id
    comments = await db.collaboration_comments.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return {"comments": comments}


@router.post("/collaborate/comment/{comment_id}/react")
async def react_to_comment(comment_id: str, request: Request):
    """React to a collaboration comment"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)
    body = await request.json()
    emoji = body.get("emoji", "thumbsup")

    await db.collaboration_comments.update_one(
        {"id": comment_id},
        {"$set": {f"reactions.{user['user_id']}": emoji}}
    )
    return {"status": "reacted"}


# --- Multi-Channel Outreach ---

class OutreachMessage(BaseModel):
    candidate_ids: List[str]
    channel: str  # email, sms, inmail
    subject: Optional[str] = ""
    message: str
    template_id: Optional[str] = ""

class OutreachTemplate(BaseModel):
    name: str
    channel: str
    subject: Optional[str] = ""
    body: str

@router.post("/outreach/send")
async def send_outreach(req: OutreachMessage, request: Request):
    """Send multi-channel outreach to candidates"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)

    outreach_id = str(uuid.uuid4())
    outreach = {
        "id": outreach_id,
        "sender_id": user["user_id"],
        "sender_name": user.get("name", ""),
        "candidate_ids": req.candidate_ids,
        "channel": req.channel,
        "subject": req.subject,
        "message": req.message,
        "status": "sent",
        "sent_count": len(req.candidate_ids),
        "delivered_count": len(req.candidate_ids),
        "opened_count": 0,
        "replied_count": 0,
        "sent_at": datetime.now(timezone.utc).isoformat()
    }
    await db.outreach_messages.insert_one(outreach)
    outreach.pop("_id", None)
    return outreach


@router.get("/outreach/history")
async def get_outreach_history(request: Request):
    """Get outreach message history"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)
    messages = await db.outreach_messages.find(
        {"sender_id": user["user_id"]}, {"_id": 0}
    ).sort("sent_at", -1).to_list(100)
    return {"messages": messages}


@router.post("/outreach/templates")
async def create_outreach_template(req: OutreachTemplate, request: Request):
    """Create an outreach message template"""
    from routes.auth import require_auth
    from server import db
    user = await require_auth(request)
    template = {
        "id": str(uuid.uuid4()),
        "creator_id": user["user_id"],
        "name": req.name,
        "channel": req.channel,
        "subject": req.subject,
        "body": req.body,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.outreach_templates.insert_one(template)
    template.pop("_id", None)
    return template


@router.get("/outreach/templates")
async def get_outreach_templates(request: Request):
    """Get all outreach templates"""
    from server import db
    templates = await db.outreach_templates.find({}, {"_id": 0}).to_list(50)
    return {"templates": templates}
