"""
Talent CRM Routes — Full contact management, pipeline, interactions, campaigns
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/talent-crm", tags=["Talent CRM"])


# --- Models ---

class TalentPoolCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    tags: List[str] = []

class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    title: Optional[str] = ""
    company: Optional[str] = ""
    source: Optional[str] = "manual"
    stage: Optional[str] = "new"
    tags: List[str] = []
    notes: Optional[str] = ""

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    stage: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class InteractionCreate(BaseModel):
    contact_id: str
    interaction_type: str  # call, email, meeting, note, linkedin
    summary: str
    outcome: Optional[str] = ""

class NurtureCampaign(BaseModel):
    name: str
    pool_id: Optional[str] = ""
    message_template: str
    schedule: Optional[str] = "immediate"


PIPELINE_STAGES = ["new", "contacted", "screening", "interview", "offer", "hired", "rejected", "archived"]


# --- Talent Pools ---

@router.get("/pools")
async def get_talent_pools(request: Request):
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
        pool["candidate_count"] = 0
        return pool
    except Exception as e:
        logger.error(f"Pool creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create pool")


@router.delete("/pools/{pool_id}")
async def delete_talent_pool(pool_id: str, request: Request):
    try:
        from server import db
        from bson import ObjectId
        await db.talent_pools.delete_one({"_id": ObjectId(pool_id)})
        return {"status": "deleted", "pool_id": pool_id}
    except Exception as e:
        logger.error(f"Pool delete error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete pool")


@router.post("/pools/{pool_id}/candidates/{contact_id}")
async def add_contact_to_pool(pool_id: str, contact_id: str, request: Request):
    try:
        from server import db
        from bson import ObjectId
        await db.talent_pools.update_one(
            {"_id": ObjectId(pool_id)},
            {"$addToSet": {"candidates": contact_id}}
        )
        return {"status": "added"}
    except Exception as e:
        logger.error(f"Add to pool error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add to pool")


@router.delete("/pools/{pool_id}/candidates/{contact_id}")
async def remove_contact_from_pool(pool_id: str, contact_id: str, request: Request):
    try:
        from server import db
        from bson import ObjectId
        await db.talent_pools.update_one(
            {"_id": ObjectId(pool_id)},
            {"$pull": {"candidates": contact_id}}
        )
        return {"status": "removed"}
    except Exception as e:
        logger.error(f"Remove from pool error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove")


# --- Contacts CRUD ---

@router.get("/contacts")
async def list_contacts(request: Request, stage: Optional[str] = None, search: Optional[str] = None):
    try:
        from server import db
        query = {}
        if stage and stage != "all":
            query["stage"] = stage
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"company": {"$regex": search, "$options": "i"}},
                {"title": {"$regex": search, "$options": "i"}}
            ]
        contacts = await db.crm_contacts.find(query).sort("updated_at", -1).to_list(200)
        for c in contacts:
            c["id"] = str(c.pop("_id"))
        return {"contacts": contacts}
    except Exception as e:
        logger.error(f"Contacts fetch error: {e}")
        return {"contacts": []}


@router.post("/contacts")
async def create_contact(req: ContactCreate, request: Request):
    try:
        from server import db
        contact = {
            "name": req.name,
            "email": req.email,
            "phone": req.phone,
            "title": req.title,
            "company": req.company,
            "source": req.source,
            "stage": req.stage,
            "tags": req.tags,
            "notes": req.notes,
            "interactions_count": 0,
            "last_interaction": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        result = await db.crm_contacts.insert_one(contact)
        contact["id"] = str(result.inserted_id)
        contact.pop("_id", None)
        return contact
    except Exception as e:
        logger.error(f"Contact creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create contact")


@router.get("/contacts/{contact_id}")
async def get_contact(contact_id: str, request: Request):
    try:
        from server import db
        from bson import ObjectId
        contact = await db.crm_contacts.find_one({"_id": ObjectId(contact_id)})
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        contact["id"] = str(contact.pop("_id"))
        interactions = await db.crm_interactions.find(
            {"contact_id": contact_id}
        ).sort("created_at", -1).to_list(50)
        for i in interactions:
            i["id"] = str(i.pop("_id"))
        return {"contact": contact, "interactions": interactions}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Contact fetch error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch contact")


@router.put("/contacts/{contact_id}")
async def update_contact(contact_id: str, req: ContactUpdate, request: Request):
    try:
        from server import db
        from bson import ObjectId
        updates = {k: v for k, v in req.dict().items() if v is not None}
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.crm_contacts.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": updates}
        )
        contact = await db.crm_contacts.find_one({"_id": ObjectId(contact_id)})
        if contact:
            contact["id"] = str(contact.pop("_id"))
        return contact or {"status": "updated"}
    except Exception as e:
        logger.error(f"Contact update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update contact")


@router.delete("/contacts/{contact_id}")
async def delete_contact(contact_id: str, request: Request):
    try:
        from server import db
        from bson import ObjectId
        await db.crm_contacts.delete_one({"_id": ObjectId(contact_id)})
        await db.crm_interactions.delete_many({"contact_id": contact_id})
        return {"status": "deleted", "contact_id": contact_id}
    except Exception as e:
        logger.error(f"Contact delete error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete contact")


@router.put("/contacts/{contact_id}/stage")
async def update_contact_stage(contact_id: str, request: Request):
    try:
        from server import db
        from bson import ObjectId
        body = await request.json()
        stage = body.get("stage", "new")
        if stage not in PIPELINE_STAGES:
            raise HTTPException(status_code=400, detail=f"Invalid stage: {stage}")
        await db.crm_contacts.update_one(
            {"_id": ObjectId(contact_id)},
            {"$set": {"stage": stage, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"status": "updated", "stage": stage}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stage update error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update stage")


# --- Interactions ---

@router.post("/interactions")
async def add_interaction(req: InteractionCreate, request: Request):
    try:
        from server import db
        interaction = {
            "contact_id": req.contact_id,
            "type": req.interaction_type,
            "summary": req.summary,
            "outcome": req.outcome,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        result = await db.crm_interactions.insert_one(interaction)
        interaction["id"] = str(result.inserted_id)
        interaction.pop("_id", None)
        # Update contact's interaction count
        from bson import ObjectId
        await db.crm_contacts.update_one(
            {"_id": ObjectId(req.contact_id)},
            {
                "$inc": {"interactions_count": 1},
                "$set": {
                    "last_interaction": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        return interaction
    except Exception as e:
        logger.error(f"Interaction creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add interaction")


@router.get("/interactions/{contact_id}")
async def get_interactions(contact_id: str, request: Request):
    try:
        from server import db
        interactions = await db.crm_interactions.find(
            {"contact_id": contact_id}
        ).sort("created_at", -1).to_list(100)
        for i in interactions:
            i["id"] = str(i.pop("_id"))
        return {"interactions": interactions}
    except Exception as e:
        logger.error(f"Interactions fetch error: {e}")
        return {"interactions": []}


# --- Pipeline Stats ---

@router.get("/pipeline")
async def get_pipeline_stats(request: Request):
    try:
        from server import db
        pipeline = await db.crm_contacts.aggregate([
            {"$group": {"_id": "$stage", "count": {"$sum": 1}}}
        ]).to_list(20)
        stages = {s: 0 for s in PIPELINE_STAGES}
        for p in pipeline:
            if p["_id"] in stages:
                stages[p["_id"]] = p["count"]
        total = sum(stages.values())
        return {"stages": stages, "total": total, "stage_order": PIPELINE_STAGES}
    except Exception as e:
        logger.error(f"Pipeline stats error: {e}")
        return {"stages": {}, "total": 0, "stage_order": PIPELINE_STAGES}


# --- Campaigns ---

@router.post("/campaigns")
async def create_campaign(req: NurtureCampaign, request: Request):
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
    try:
        from server import db
        campaigns = await db.nurture_campaigns.find({}).sort("created_at", -1).to_list(50)
        for c in campaigns:
            c["campaign_id"] = str(c.pop("_id"))
        return {"campaigns": campaigns}
    except Exception as e:
        logger.error(f"Campaign fetch error: {e}")
        return {"campaigns": []}
