"""
Talent CRM Routes
Candidate relationship management, nurture campaigns, talent pools
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/talent-crm", tags=["Talent CRM"])


class TalentPoolCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    tags: List[str] = []

class CandidateNote(BaseModel):
    candidate_id: str
    note: str
    note_type: str = "general"

class NurtureCampaign(BaseModel):
    name: str
    pool_id: str
    message_template: str
    schedule: Optional[str] = "immediate"


@router.get("/pools")
async def get_talent_pools(request: Request):
    """Get all talent pools"""
    try:
        from server import db
        pools = await db.talent_pools.find({}).sort("created_at", -1).to_list(100)
        for p in pools:
            p["pool_id"] = str(p.pop("_id"))
            p["candidate_count"] = len(p.get("candidates", []))
        return {"pools": pools}
    except Exception as e:
        logger.error(f"Error fetching pools: {e}")
        return {"pools": []}


@router.post("/pools")
async def create_talent_pool(req: TalentPoolCreate, request: Request):
    """Create a talent pool"""
    try:
        from server import db
        pool = {
            "name": req.name,
            "description": req.description,
            "tags": req.tags,
            "candidates": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = await db.talent_pools.insert_one(pool)
        pool["pool_id"] = str(result.inserted_id)
        pool.pop("_id", None)
        return pool
    except Exception as e:
        logger.error(f"Pool creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create pool")


@router.post("/pools/{pool_id}/candidates/{candidate_id}")
async def add_candidate_to_pool(pool_id: str, candidate_id: str, request: Request):
    """Add a candidate to a talent pool"""
    try:
        from server import db
        from bson import ObjectId
        await db.talent_pools.update_one(
            {"_id": ObjectId(pool_id)},
            {"$addToSet": {"candidates": candidate_id}}
        )
        return {"status": "added"}
    except Exception as e:
        logger.error(f"Add to pool error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add candidate")


@router.delete("/pools/{pool_id}/candidates/{candidate_id}")
async def remove_candidate_from_pool(pool_id: str, candidate_id: str, request: Request):
    """Remove candidate from pool"""
    try:
        from server import db
        from bson import ObjectId
        await db.talent_pools.update_one(
            {"_id": ObjectId(pool_id)},
            {"$pull": {"candidates": candidate_id}}
        )
        return {"status": "removed"}
    except Exception as e:
        logger.error(f"Remove from pool error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove candidate")


# --- Candidate Notes ---

@router.post("/notes")
async def add_candidate_note(req: CandidateNote, request: Request):
    """Add a note about a candidate"""
    try:
        from server import db
        note = {
            "candidate_id": req.candidate_id,
            "note": req.note,
            "note_type": req.note_type,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = await db.candidate_notes.insert_one(note)
        note["note_id"] = str(result.inserted_id)
        note.pop("_id", None)
        return note
    except Exception as e:
        logger.error(f"Note creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add note")


@router.get("/notes/{candidate_id}")
async def get_candidate_notes(candidate_id: str, request: Request):
    """Get all notes for a candidate"""
    try:
        from server import db
        notes = await db.candidate_notes.find(
            {"candidate_id": candidate_id}, {"_id": 0}
        ).sort("created_at", -1).to_list(100)
        return {"notes": notes}
    except Exception as e:
        logger.error(f"Notes fetch error: {e}")
        return {"notes": []}


# --- Nurture Campaigns ---

@router.post("/campaigns")
async def create_campaign(req: NurtureCampaign, request: Request):
    """Create a nurture campaign"""
    try:
        from server import db
        campaign = {
            "name": req.name,
            "pool_id": req.pool_id,
            "message_template": req.message_template,
            "schedule": req.schedule,
            "status": "draft",
            "sent_count": 0,
            "open_count": 0,
            "reply_count": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = await db.nurture_campaigns.insert_one(campaign)
        campaign["campaign_id"] = str(result.inserted_id)
        campaign.pop("_id", None)
        return campaign
    except Exception as e:
        logger.error(f"Campaign creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create campaign")


@router.get("/campaigns")
async def get_campaigns(request: Request):
    """Get all nurture campaigns"""
    try:
        from server import db
        campaigns = await db.nurture_campaigns.find({}).sort("created_at", -1).to_list(50)
        for c in campaigns:
            c["campaign_id"] = str(c.pop("_id"))
        return {"campaigns": campaigns}
    except Exception as e:
        logger.error(f"Campaign fetch error: {e}")
        return {"campaigns": []}
