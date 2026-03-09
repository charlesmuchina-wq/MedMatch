"""
Meeting-to-Channel Sync Service
When a KARAU meeting ends, auto-create an ENZI channel for continued collaboration.

Rules:
- Default ON (host can opt out via meeting settings)
- Internal members (same domain email) added automatically
- External members require admin approval
- Meeting transcript/notes become first channel message
- Channel name derived from meeting title
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import logging
import re

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/meeting-sync", tags=["Meeting-Channel Sync"])
logger = logging.getLogger(__name__)


class MeetingSyncSettings(BaseModel):
    auto_create_channel: bool = True
    include_transcript: bool = True
    include_notes: bool = True
    channel_visibility: str = "internal"  # "internal" or "all"


class ExternalApprovalRequest(BaseModel):
    meeting_id: str
    user_ids: List[str]
    channel_id: str


def slugify_title(title: str) -> str:
    """Convert meeting title to channel-friendly slug"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:40] or "meeting"


def get_email_domain(email: str) -> str:
    """Extract domain from email"""
    return email.split('@')[-1].lower() if '@' in email else ''


async def get_host_domain(host_id: str) -> str:
    """Get the email domain of the meeting host"""
    user = await db.users.find_one({"user_id": host_id}, {"_id": 0, "email": 1})
    return get_email_domain(user.get("email", "")) if user else ""


async def convert_meeting_to_channel(meeting_data: dict) -> dict:
    """
    Auto-convert an ended meeting into an ENZI channel.
    Only internal members (same domain) are added by default.
    External members are queued for admin approval.
    """
    meeting_id = meeting_data.get("meeting_id") or meeting_data.get("id")
    title = meeting_data.get("title", "Meeting")
    host_id = meeting_data.get("host_id")
    participants = meeting_data.get("participants", [])
    
    # Check if sync is disabled for this meeting
    settings = meeting_data.get("sync_settings", {})
    if settings.get("auto_create_channel") is False:
        return {"skipped": True, "reason": "Host disabled auto-channel"}
    
    # Check if channel already exists for this meeting
    existing = await db.lumi_channels.find_one(
        {"meeting_source_id": meeting_id},
        {"_id": 0, "id": 1}
    )
    if existing:
        return {"skipped": True, "reason": "Channel already exists", "channel_id": existing["id"]}
    
    # Get host domain for internal/external classification
    host_domain = await get_host_domain(host_id)
    
    # Classify participants
    internal_members = []
    external_pending = []
    
    for p in participants:
        p_id = p.get("user_id") or p if isinstance(p, str) else None
        p_name = p.get("user_name", "User") if isinstance(p, dict) else "User"
        if not p_id:
            continue
        
        # Look up user email
        user_doc = await db.users.find_one({"user_id": p_id}, {"_id": 0, "email": 1, "name": 1})
        p_email = user_doc.get("email", "") if user_doc else ""
        p_name = user_doc.get("name", p_name) if user_doc else p_name
        p_domain = get_email_domain(p_email)
        
        member_data = {
            "user_id": p_id,
            "name": p_name,
            "email": p_email,
            "role": "admin" if p_id == host_id else "member",
            "joined_at": datetime.now(timezone.utc).isoformat()
        }
        
        if host_domain and p_domain == host_domain:
            internal_members.append(member_data)
        else:
            external_pending.append(member_data)
    
    # Ensure host is always in internal members
    if not any(m["user_id"] == host_id for m in internal_members):
        host_doc = await db.users.find_one({"user_id": host_id}, {"_id": 0, "email": 1, "name": 1})
        internal_members.insert(0, {
            "user_id": host_id,
            "name": host_doc.get("name", "Host") if host_doc else "Host",
            "email": host_doc.get("email", "") if host_doc else "",
            "role": "admin",
            "joined_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Create channel
    now = datetime.now(timezone.utc).isoformat()
    channel_id = f"mtg-{str(uuid.uuid4())[:8]}"
    date_str = datetime.now(timezone.utc).strftime("%b-%d").lower()
    channel_name = f"meeting-{slugify_title(title)}-{date_str}"
    
    channel = {
        "id": channel_id,
        "name": channel_name,
        "description": f"Post-meeting channel from: {title}",
        "channel_type": "meeting-followup",
        "created_by": host_id,
        "members": internal_members,
        "is_private": True,
        "meeting_source_id": meeting_id,
        "meeting_title": title,
        "external_pending": [{"user_id": ep["user_id"], "name": ep["name"], "email": ep["email"], "status": "pending"} for ep in external_pending],
        "created_at": now,
        "message_count": 0
    }
    
    await db.lumi_channels.insert_one(channel)
    
    # Post meeting summary as first message
    summary_parts = [f"**Meeting Recap: {title}**\n"]
    summary_parts.append(f"Participants: {', '.join(m['name'] for m in internal_members)}")
    
    if meeting_data.get("ended_at"):
        summary_parts.append(f"Ended: {meeting_data['ended_at'][:16].replace('T', ' at ')}")
    
    # Include transcript/notes if available
    if settings.get("include_notes", True) and meeting_data.get("ai_notes"):
        summary_parts.append(f"\n**Meeting Notes:**\n{meeting_data['ai_notes']}")
    
    if settings.get("include_transcript", True) and meeting_data.get("transcript"):
        summary_parts.append(f"\n**Transcript:**\n{meeting_data['transcript'][:2000]}")
    
    summary_parts.append("\n---\n*Continue your discussion in this channel.*")
    
    await db.lumi_messages.insert_one({
        "id": str(uuid.uuid4()),
        "channel_id": channel_id,
        "content": "\n".join(summary_parts),
        "sender_id": "system",
        "sender_name": "Meeting Sync Bot",
        "type": "meeting-recap",
        "meeting_id": meeting_id,
        "created_at": now
    })
    
    # If there are external pending members, create approval requests
    if external_pending:
        for ep in external_pending:
            await db.external_approvals.insert_one({
                "id": str(uuid.uuid4()),
                "channel_id": channel_id,
                "meeting_id": meeting_id,
                "user_id": ep["user_id"],
                "user_name": ep["name"],
                "user_email": ep["email"],
                "status": "pending",
                "requested_at": now
            })
    
    del channel["_id"]
    return {
        "channel_id": channel_id,
        "channel_name": channel_name,
        "internal_members": len(internal_members),
        "external_pending": len(external_pending),
        "meeting_id": meeting_id
    }


# ═══════ API Endpoints ═══════

@router.post("/convert")
async def manually_convert_meeting(request: Request, meeting_id: str):
    """Manually trigger meeting-to-channel conversion"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    meeting = await db.karau_meetings.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0}
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    if meeting.get("host_id") != user.get("user_id"):
        raise HTTPException(status_code=403, detail="Only the host can convert a meeting")
    
    result = await convert_meeting_to_channel(meeting)
    return result


@router.get("/settings")
async def get_sync_settings(request: Request):
    """Get user's meeting sync settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    settings = await db.user_settings.find_one(
        {"user_id": user.get("user_id"), "type": "meeting_sync"},
        {"_id": 0}
    )
    return settings or {
        "auto_create_channel": True,
        "include_transcript": True,
        "include_notes": True,
        "channel_visibility": "internal"
    }


@router.put("/settings")
async def update_sync_settings(req: MeetingSyncSettings, request: Request):
    """Update user's meeting sync settings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await db.user_settings.update_one(
        {"user_id": user.get("user_id"), "type": "meeting_sync"},
        {"$set": {
            "user_id": user.get("user_id"),
            "type": "meeting_sync",
            **req.dict()
        }},
        upsert=True
    )
    return {"status": "updated", **req.dict()}


@router.get("/pending-approvals")
async def get_pending_approvals(request: Request):
    """Get pending external member approval requests (admin only)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if user is admin of any channels with pending approvals
    approvals = await db.external_approvals.find(
        {"status": "pending"},
        {"_id": 0}
    ).sort("requested_at", -1).limit(50).to_list(50)
    
    # Filter to approvals for channels where user is admin
    result = []
    for a in approvals:
        ch = await db.lumi_channels.find_one(
            {"id": a["channel_id"], "members": {"$elemMatch": {"user_id": user.get("user_id"), "role": "admin"}}},
            {"_id": 0, "id": 1, "name": 1}
        )
        if ch:
            a["channel_name"] = ch.get("name")
            result.append(a)
    
    return {"approvals": result, "count": len(result)}


@router.post("/approve-external")
async def approve_external_member(req: ExternalApprovalRequest, request: Request):
    """Approve external members to join a meeting-created channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Verify user is admin of the channel
    ch = await db.lumi_channels.find_one(
        {"id": req.channel_id, "members": {"$elemMatch": {"user_id": user.get("user_id"), "role": "admin"}}},
        {"_id": 0}
    )
    if not ch:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    now = datetime.now(timezone.utc).isoformat()
    approved_count = 0
    
    for uid in req.user_ids:
        approval = await db.external_approvals.find_one(
            {"channel_id": req.channel_id, "user_id": uid, "status": "pending"},
            {"_id": 0}
        )
        if not approval:
            continue
        
        # Add to channel
        await db.lumi_channels.update_one(
            {"id": req.channel_id},
            {"$push": {"members": {
                "user_id": uid,
                "name": approval.get("user_name", "External"),
                "email": approval.get("user_email", ""),
                "role": "member",
                "joined_at": now,
                "external": True,
                "approved_by": user.get("user_id")
            }}}
        )
        
        # Update approval status
        await db.external_approvals.update_one(
            {"channel_id": req.channel_id, "user_id": uid},
            {"$set": {"status": "approved", "approved_by": user.get("user_id"), "approved_at": now}}
        )
        
        # Remove from pending
        await db.lumi_channels.update_one(
            {"id": req.channel_id},
            {"$pull": {"external_pending": {"user_id": uid}}}
        )
        
        approved_count += 1
    
    return {"approved": approved_count, "channel_id": req.channel_id}


@router.post("/deny-external")
async def deny_external_member(req: ExternalApprovalRequest, request: Request):
    """Deny external members from joining a meeting channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    ch = await db.lumi_channels.find_one(
        {"id": req.channel_id, "members": {"$elemMatch": {"user_id": user.get("user_id"), "role": "admin"}}},
        {"_id": 0}
    )
    if not ch:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    denied_count = 0
    for uid in req.user_ids:
        await db.external_approvals.update_one(
            {"channel_id": req.channel_id, "user_id": uid},
            {"$set": {"status": "denied", "denied_by": user.get("user_id"), "denied_at": datetime.now(timezone.utc).isoformat()}}
        )
        await db.lumi_channels.update_one(
            {"id": req.channel_id},
            {"$pull": {"external_pending": {"user_id": uid}}}
        )
        denied_count += 1
    
    return {"denied": denied_count, "channel_id": req.channel_id}


@router.get("/channels")
async def get_meeting_channels(request: Request):
    """Get all channels created from meetings"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    channels = await db.lumi_channels.find(
        {"channel_type": "meeting-followup", "members.user_id": user.get("user_id")},
        {"_id": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    return {"channels": channels, "count": len(channels)}
