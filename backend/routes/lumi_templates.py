"""
LUMI Templates - Save and reuse refined AI message templates
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import os

from motor.motor_asyncio import AsyncIOMotorClient
from routes.auth import get_current_user

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "MedMatch")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

router = APIRouter(prefix="/lumi/templates", tags=["LUMI Templates"])


class TemplateCreate(BaseModel):
    name: str
    text: str
    category: Optional[str] = "general"  # general, professional, friendly, translation
    source_action: Optional[str] = ""  # refine, translate, suggest


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    text: Optional[str] = None
    category: Optional[str] = None


@router.post("")
async def create_template(data: TemplateCreate, request: Request):
    """Save a message as a reusable template"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    template = {
        "id": f"tpl_{uuid.uuid4().hex[:10]}",
        "user_id": user["user_id"],
        "name": data.name.strip(),
        "text": data.text,
        "category": data.category,
        "source_action": data.source_action,
        "use_count": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.lumi_templates.insert_one(template)
    template.pop("_id", None)
    return template


@router.get("")
async def list_templates(request: Request, category: Optional[str] = None):
    """List user's saved templates"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    query = {"user_id": user["user_id"]}
    if category:
        query["category"] = category

    templates = await db.lumi_templates.find(query, {"_id": 0}).sort("use_count", -1).to_list(100)
    return {"templates": templates}


@router.put("/{template_id}")
async def update_template(template_id: str, data: TemplateUpdate, request: Request):
    """Update a template"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if data.name is not None:
        updates["name"] = data.name.strip()
    if data.text is not None:
        updates["text"] = data.text
    if data.category is not None:
        updates["category"] = data.category

    result = await db.lumi_templates.update_one(
        {"id": template_id, "user_id": user["user_id"]},
        {"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")

    return {"status": "updated"}


@router.delete("/{template_id}")
async def delete_template(template_id: str, request: Request):
    """Delete a template"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = await db.lumi_templates.delete_one({"id": template_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"status": "deleted"}


@router.post("/{template_id}/apply")
async def apply_template(template_id: str, request: Request):
    """Apply a template (returns text and increments use count)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    template = await db.lumi_templates.find_one(
        {"id": template_id, "user_id": user["user_id"]}, {"_id": 0}
    )
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.lumi_templates.update_one(
        {"id": template_id},
        {"$inc": {"use_count": 1}}
    )

    return {"text": template["text"], "name": template["name"]}
