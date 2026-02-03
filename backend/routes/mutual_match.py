"""
Mutual Match System
===================
GDPR-compliant contact request workflow between recruiters and job seekers.

Features:
- Contact request with candidate consent
- Accept/Decline mechanism  
- Secure in-app messaging
- Time-bound data access
- Push notifications
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone, timedelta
import uuid
import logging

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/mutual-match", tags=["Mutual Match"])

# ============== Models ==============

class ContactRequest(BaseModel):
    """Recruiter's request to contact a candidate"""
    candidate_id: str
    job_id: str
    message: Optional[str] = None  # Optional intro message

class ContactResponse(BaseModel):
    """Candidate's response to contact request"""
    request_id: str
    action: str  # "accept" or "decline"
    message: Optional[str] = None

class SecureMessage(BaseModel):
    """In-app secure message"""
    match_id: str
    content: str

# ============== Helper Functions ==============

async def send_contact_request_notification(candidate_id: str, recruiter: Dict, job: Dict, request_id: str):
    """Send push notification to candidate about contact request"""
    try:
        # Get candidate's push tokens
        tokens = await db.expo_push_tokens.find({"user_id": candidate_id}).to_list(10)
        
        if not tokens:
            return
        
        # Build notification
        title = "Contact Request"
        body = f"{recruiter.get('company_name', 'A recruiter')} wants to contact you about {job.get('title', 'a position')}"
        
        # In production, send via Expo push service
        notification_record = {
            "id": str(uuid.uuid4()),
            "user_id": candidate_id,
            "type": "contact_request",
            "title": title,
            "body": body,
            "data": {
                "request_id": request_id,
                "recruiter_company": recruiter.get("company_name"),
                "job_title": job.get("title"),
                "job_id": job.get("id")
            },
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "read": False
        }
        
        await db.notifications.insert_one(notification_record)
        
        logging.info(f"Contact request notification sent to candidate {candidate_id}")
        
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")

# ============== Contact Request Routes ==============

@router.post("/request")
async def send_contact_request(contact_req: ContactRequest, request: Request, background_tasks: BackgroundTasks):
    """
    Recruiter sends a contact request to a candidate.
    Candidate's PII remains hidden until they accept.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get recruiter profile
    recruiter = await db.recruiter_profiles.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not recruiter:
        raise HTTPException(status_code=403, detail="Recruiter profile required")
    
    if recruiter.get("verification_status") != "verified":
        raise HTTPException(status_code=403, detail="Account verification required")
    
    # Check if request already exists
    existing = await db.contact_requests.find_one({
        "candidate_id": contact_req.candidate_id,
        "recruiter_id": user["user_id"],
        "job_id": contact_req.job_id,
        "status": {"$in": ["pending", "accepted"]}
    })
    
    if existing:
        return {
            "message": "Contact request already exists",
            "request_id": existing.get("id"),
            "status": existing.get("status")
        }
    
    # Get job details
    job = await db.posted_jobs.find_one({"id": contact_req.job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify job belongs to this recruiter
    if job.get("recruiter_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="You can only request contact for your own job postings")
    
    # Get candidate exists check
    candidate = await db.resumes.find_one({"id": contact_req.candidate_id})
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Create contact request
    contact_request = {
        "id": str(uuid.uuid4()),
        "candidate_id": contact_req.candidate_id,
        "candidate_user_id": candidate.get("user_id"),
        "recruiter_id": user["user_id"],
        "organization_id": recruiter.get("organization_id"),
        "job_id": contact_req.job_id,
        "job_title": job.get("title"),
        "company_name": recruiter.get("company_name"),
        "recruiter_name": user.get("name", user.get("email", "").split("@")[0]),
        "message": contact_req.message,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "responded_at": None
    }
    
    await db.contact_requests.insert_one(contact_request)
    
    # Send notification to candidate
    background_tasks.add_task(
        send_contact_request_notification,
        candidate.get("user_id"),
        recruiter,
        job,
        contact_request["id"]
    )
    
    # Log action
    from routes.recruiter_rbac import log_recruiter_action
    await log_recruiter_action(
        user["user_id"],
        recruiter.get("organization_id", "unknown"),
        "CONTACT_REQUEST_SENT",
        {"candidate_id": contact_req.candidate_id, "job_id": contact_req.job_id},
        contact_req.candidate_id
    )
    
    return {
        "message": "Contact request sent successfully",
        "request_id": contact_request["id"],
        "status": "pending",
        "note": "The candidate will be notified and can choose to accept or decline your request."
    }

@router.get("/requests/sent")
async def get_sent_requests(request: Request):
    """Get all contact requests sent by the recruiter"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    requests = await db.contact_requests.find(
        {"recruiter_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    return {
        "requests": requests,
        "total": len(requests)
    }

@router.get("/requests/received")
async def get_received_requests(request: Request):
    """Get all contact requests received by the candidate"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    requests = await db.contact_requests.find(
        {"candidate_user_id": user["user_id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    
    # Enrich with job details
    enriched = []
    for req in requests:
        job = await db.posted_jobs.find_one(
            {"id": req.get("job_id")},
            {"_id": 0, "title": 1, "company": 1, "location": 1, "description": 1}
        )
        req["job_details"] = job
        enriched.append(req)
    
    return {
        "requests": enriched,
        "pending_count": sum(1 for r in requests if r.get("status") == "pending"),
        "total": len(requests)
    }

@router.get("/requests/{request_id}")
async def get_request_details(request_id: str, request: Request):
    """Get details of a specific contact request"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    contact_req = await db.contact_requests.find_one(
        {"id": request_id},
        {"_id": 0}
    )
    
    if not contact_req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Verify user is either recruiter or candidate
    if contact_req.get("recruiter_id") != user["user_id"] and contact_req.get("candidate_user_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this request")
    
    # Get job details
    job = await db.posted_jobs.find_one(
        {"id": contact_req.get("job_id")},
        {"_id": 0}
    )
    
    contact_req["job_details"] = job
    
    return contact_req

# ============== Candidate Response Routes ==============

@router.post("/respond")
async def respond_to_contact_request(response: ContactResponse, request: Request, background_tasks: BackgroundTasks):
    """
    Candidate accepts or declines a contact request.
    On accept: PII is shared, secure chat opens.
    On decline: Recruiter notified anonymously, PII stays private.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if response.action not in ["accept", "decline"]:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'decline'")
    
    # Get contact request
    contact_req = await db.contact_requests.find_one(
        {"id": response.request_id, "candidate_user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not contact_req:
        raise HTTPException(status_code=404, detail="Contact request not found")
    
    if contact_req.get("status") != "pending":
        raise HTTPException(status_code=400, detail=f"Request already {contact_req.get('status')}")
    
    # Check if expired
    expires_at = contact_req.get("expires_at")
    if expires_at and datetime.fromisoformat(expires_at.replace("Z", "+00:00")) < datetime.now(timezone.utc):
        await db.contact_requests.update_one(
            {"id": response.request_id},
            {"$set": {"status": "expired"}}
        )
        raise HTTPException(status_code=400, detail="Contact request has expired")
    
    now = datetime.now(timezone.utc).isoformat()
    
    if response.action == "accept":
        # Create mutual match
        mutual_match = {
            "id": str(uuid.uuid4()),
            "request_id": response.request_id,
            "candidate_id": contact_req.get("candidate_id"),
            "candidate_user_id": user["user_id"],
            "recruiter_id": contact_req.get("recruiter_id"),
            "organization_id": contact_req.get("organization_id"),
            "job_id": contact_req.get("job_id"),
            "status": "accepted",
            "matched_at": now,
            # Data retention timer starts
            "data_expires_at": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat()
        }
        
        await db.mutual_matches.insert_one(mutual_match)
        
        # Update contact request
        await db.contact_requests.update_one(
            {"id": response.request_id},
            {"$set": {"status": "accepted", "responded_at": now}}
        )
        
        # Get candidate contact info to share
        candidate = await db.resumes.find_one(
            {"user_id": user["user_id"]},
            {"_id": 0, "email": 1, "phone": 1, "full_name": 1}
        )
        
        # Notify recruiter
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": contact_req.get("recruiter_id"),
            "type": "contact_accepted",
            "title": "Contact Request Accepted!",
            "body": f"Your contact request for {contact_req.get('job_title')} has been accepted. You can now view the candidate's contact details.",
            "data": {
                "match_id": mutual_match["id"],
                "candidate_name": candidate.get("full_name"),
                "candidate_email": candidate.get("email"),
                "job_id": contact_req.get("job_id")
            },
            "sent_at": now,
            "read": False
        }
        await db.notifications.insert_one(notification)
        
        return {
            "message": "Contact request accepted",
            "match_id": mutual_match["id"],
            "recruiter_name": contact_req.get("recruiter_name"),
            "company_name": contact_req.get("company_name"),
            "job_title": contact_req.get("job_title"),
            "chat_enabled": True,
            "data_shared": ["email", "phone", "full_name"],
            "data_retention_notice": "Your data will be accessible for 60 days from this match."
        }
    
    else:  # decline
        # Update contact request
        await db.contact_requests.update_one(
            {"id": response.request_id},
            {"$set": {
                "status": "declined",
                "responded_at": now,
                "decline_message": response.message
            }}
        )
        
        # Notify recruiter anonymously
        notification = {
            "id": str(uuid.uuid4()),
            "user_id": contact_req.get("recruiter_id"),
            "type": "contact_declined",
            "title": "Contact Request Update",
            "body": f"The candidate has politely declined your contact request for {contact_req.get('job_title')} at this time.",
            "data": {
                "job_id": contact_req.get("job_id"),
                "request_id": response.request_id
            },
            "sent_at": now,
            "read": False
        }
        await db.notifications.insert_one(notification)
        
        return {
            "message": "Contact request declined",
            "note": "The recruiter has been notified anonymously. Your personal information remains private."
        }

# ============== Secure Messaging Routes ==============

@router.post("/messages/send")
async def send_secure_message(msg: SecureMessage, request: Request):
    """
    Send a secure in-app message within a mutual match.
    No external emails exposed.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify user is part of this match
    match = await db.mutual_matches.find_one(
        {"id": msg.match_id},
        {"_id": 0}
    )
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    # Check if user is either candidate or recruiter
    is_candidate = match.get("candidate_user_id") == user["user_id"]
    is_recruiter = match.get("recruiter_id") == user["user_id"]
    
    if not (is_candidate or is_recruiter):
        raise HTTPException(status_code=403, detail="Not authorized to message in this match")
    
    # Check match is still active
    if match.get("status") != "accepted":
        raise HTTPException(status_code=400, detail="Match is no longer active")
    
    # Check data retention
    expires_at = match.get("data_expires_at")
    if expires_at and datetime.fromisoformat(expires_at.replace("Z", "+00:00")) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Match has expired. Data retention period ended.")
    
    # Create message
    message = {
        "id": str(uuid.uuid4()),
        "match_id": msg.match_id,
        "sender_id": user["user_id"],
        "sender_type": "candidate" if is_candidate else "recruiter",
        "sender_name": user.get("name", user.get("email", "").split("@")[0]),
        "content": msg.content,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "read": False
    }
    
    await db.match_messages.insert_one(message)
    
    # Notify recipient
    recipient_id = match.get("recruiter_id") if is_candidate else match.get("candidate_user_id")
    notification = {
        "id": str(uuid.uuid4()),
        "user_id": recipient_id,
        "type": "new_message",
        "title": "New Message",
        "body": f"You have a new message from {message['sender_name']}",
        "data": {"match_id": msg.match_id, "message_id": message["id"]},
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "read": False
    }
    await db.notifications.insert_one(notification)
    
    return {
        "message": "Message sent",
        "message_id": message["id"]
    }

@router.get("/messages/{match_id}")
async def get_match_messages(match_id: str, request: Request):
    """Get all messages in a mutual match conversation"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify user is part of this match
    match = await db.mutual_matches.find_one(
        {"id": match_id},
        {"_id": 0}
    )
    
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match.get("candidate_user_id") != user["user_id"] and match.get("recruiter_id") != user["user_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    messages = await db.match_messages.find(
        {"match_id": match_id},
        {"_id": 0}
    ).sort("sent_at", 1).to_list(200)
    
    # Mark messages as read
    await db.match_messages.update_many(
        {"match_id": match_id, "sender_id": {"$ne": user["user_id"]}, "read": False},
        {"$set": {"read": True}}
    )
    
    return {
        "match_id": match_id,
        "messages": messages,
        "total": len(messages)
    }

# ============== Matches List Routes ==============

@router.get("/matches")
async def get_user_matches(request: Request):
    """Get all mutual matches for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get matches where user is either candidate or recruiter
    matches = await db.mutual_matches.find(
        {"$or": [
            {"candidate_user_id": user["user_id"]},
            {"recruiter_id": user["user_id"]}
        ]},
        {"_id": 0}
    ).sort("matched_at", -1).to_list(100)
    
    # Enrich with other party info
    enriched = []
    for match in matches:
        is_candidate = match.get("candidate_user_id") == user["user_id"]
        
        if is_candidate:
            # Get recruiter info
            recruiter = await db.recruiter_profiles.find_one(
                {"user_id": match.get("recruiter_id")},
                {"_id": 0, "company_name": 1, "job_title": 1}
            )
            match["other_party"] = {
                "type": "recruiter",
                "company": recruiter.get("company_name") if recruiter else "Unknown",
                "title": recruiter.get("job_title") if recruiter else ""
            }
        else:
            # Get candidate info (limited)
            candidate = await db.resumes.find_one(
                {"user_id": match.get("candidate_user_id")},
                {"_id": 0, "full_name": 1}
            )
            match["other_party"] = {
                "type": "candidate",
                "name": candidate.get("full_name") if candidate else "Candidate"
            }
        
        # Get job details
        job = await db.posted_jobs.find_one(
            {"id": match.get("job_id")},
            {"_id": 0, "title": 1, "company": 1}
        )
        match["job_details"] = job
        
        # Get unread message count
        unread_count = await db.match_messages.count_documents({
            "match_id": match["id"],
            "sender_id": {"$ne": user["user_id"]},
            "read": False
        })
        match["unread_messages"] = unread_count
        
        enriched.append(match)
    
    return {
        "matches": enriched,
        "total": len(enriched)
    }

# ============== Ghost Mode (Candidate Control) ==============

@router.post("/ghost-mode/toggle")
async def toggle_ghost_mode(request: Request, organization_id: Optional[str] = None):
    """
    Toggle ghost mode - hide profile from specific organizations.
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if organization_id:
        # Add to blocked list
        await db.resumes.update_one(
            {"user_id": user["user_id"]},
            {"$addToSet": {"blocked_organizations": organization_id}}
        )
        message = "Organization blocked. They can no longer see your profile."
    else:
        # Toggle global visibility
        resume = await db.resumes.find_one({"user_id": user["user_id"]})
        current_searchable = resume.get("searchable", True) if resume else True
        
        await db.resumes.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"searchable": not current_searchable}}
        )
        message = f"Profile visibility {'hidden' if current_searchable else 'visible'}"
    
    return {"message": message}

@router.get("/ghost-mode/status")
async def get_ghost_mode_status(request: Request):
    """Get current ghost mode status"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    resume = await db.resumes.find_one(
        {"user_id": user["user_id"]},
        {"_id": 0, "searchable": 1, "blocked_organizations": 1}
    )
    
    if not resume:
        return {"searchable": True, "blocked_organizations": []}
    
    return {
        "searchable": resume.get("searchable", True),
        "blocked_organizations": resume.get("blocked_organizations", [])
    }
