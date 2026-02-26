"""
KARAU Enterprise Organizations & Tiers
Handles: Company registration, tier licensing, domain verification, conference rooms, branding
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
import uuid
import logging

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/karau-meet/organizations", tags=["KARAU Organizations"])
logger = logging.getLogger(__name__)

# ============ TIER DEFINITIONS ============

TIER_CONFIG = {
    "tier_1": {
        "name": "Basic",
        "max_users": 50,
        "max_rooms": 10,
        "features": ["domain_verification", "company_branding", "conference_rooms"],
    },
    "tier_2": {
        "name": "Professional",
        "max_users": 100,
        "max_rooms": 25,
        "features": ["domain_verification", "company_branding", "conference_rooms", "employee_directory", "last_name_search"],
    },
    "tier_grande": {
        "name": "Grande",
        "max_users": 1000,
        "max_rooms": -1,  # unlimited
        "features": ["domain_verification", "company_branding", "conference_rooms", "employee_directory", "last_name_search", "sso", "bulk_import", "analytics"],
    },
    "recruiter": {
        "name": "Recruiter",
        "max_users": 50,
        "max_rooms": 5,
        "features": ["domain_verification", "company_branding", "recruiter_tools"],
    },
    "personal": {
        "name": "Personal",
        "max_users": 1,
        "max_rooms": 0,
        "features": ["meeting_code_join", "two_step_verification", "age_verification"],
    },
}


# ============ MODELS ============

class CreateOrganizationRequest(BaseModel):
    name: str
    email_domains: List[str]  # e.g. ["medmatch.com", "medmatch.io"]
    tier: str = "tier_1"
    logo_url: Optional[str] = None
    watermark_text: Optional[str] = None
    primary_color: Optional[str] = "#5b5fc7"


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    watermark_text: Optional[str] = None
    primary_color: Optional[str] = None
    tier: Optional[str] = None


class ConferenceRoomRequest(BaseModel):
    name: str
    building: str = ""
    floor: str = ""
    capacity: int = 10
    equipment: List[str] = []  # ["projector", "whiteboard", "video_conf", "phone"]
    location_type: str = "physical"  # physical | virtual | hybrid
    address: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lng: Optional[float] = None


class EmployeeEntry(BaseModel):
    email: str
    first_name: str
    last_name: str
    department: Optional[str] = None
    title: Optional[str] = None


# ============ ORGANIZATION CRUD ============

@router.post("")
async def create_organization(
    request: CreateOrganizationRequest,
    user: dict = Depends(get_current_user)
):
    """Create a new organization (admin only)."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    if request.tier not in TIER_CONFIG:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Options: {list(TIER_CONFIG.keys())}")

    org_id = f"org_{uuid.uuid4().hex[:12]}"
    tier_info = TIER_CONFIG[request.tier]

    org = {
        "org_id": org_id,
        "name": request.name,
        "email_domains": [d.lower().strip() for d in request.email_domains],
        "tier": request.tier,
        "tier_name": tier_info["name"],
        "max_users": tier_info["max_users"],
        "max_rooms": tier_info["max_rooms"],
        "features": tier_info["features"],
        "logo_url": request.logo_url,
        "watermark_text": request.watermark_text or request.name,
        "primary_color": request.primary_color or "#5b5fc7",
        "verified_domains": [],
        "conference_rooms": [],
        "employee_count": 0,
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active",
    }

    await db.karau_organizations.insert_one(org)
    org.pop("_id", None)
    return org


@router.get("")
async def list_organizations(user: dict = Depends(get_current_user)):
    """List all organizations (admin) or user's org."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if user.get("is_admin"):
        orgs = await db.karau_organizations.find({}, {"_id": 0}).to_list(100)
        return {"organizations": orgs, "count": len(orgs)}

    # Non-admin: return their org
    email_domain = user.get("email", "").split("@")[-1].lower()
    org = await db.karau_organizations.find_one(
        {"email_domains": email_domain}, {"_id": 0}
    )
    return {"organizations": [org] if org else [], "count": 1 if org else 0}


@router.get("/{org_id}")
async def get_organization(org_id: str, user: dict = Depends(get_current_user)):
    """Get organization details."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.put("/{org_id}")
async def update_organization(
    org_id: str,
    request: UpdateOrganizationRequest,
    user: dict = Depends(get_current_user)
):
    """Update organization settings (admin/IT admin only)."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    updates = {}
    if request.name is not None:
        updates["name"] = request.name
    if request.logo_url is not None:
        updates["logo_url"] = request.logo_url
    if request.watermark_text is not None:
        updates["watermark_text"] = request.watermark_text
    if request.primary_color is not None:
        updates["primary_color"] = request.primary_color
    if request.tier is not None:
        if request.tier not in TIER_CONFIG:
            raise HTTPException(status_code=400, detail="Invalid tier")
        tier_info = TIER_CONFIG[request.tier]
        updates["tier"] = request.tier
        updates["tier_name"] = tier_info["name"]
        updates["max_users"] = tier_info["max_users"]
        updates["max_rooms"] = tier_info["max_rooms"]
        updates["features"] = tier_info["features"]

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.karau_organizations.update_one(
        {"org_id": org_id}, {"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Organization not found")

    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    return org


# ============ DOMAIN VERIFICATION ============

@router.post("/{org_id}/verify-domain")
async def verify_domain(
    org_id: str,
    domain: str,
    user: dict = Depends(get_current_user)
):
    """Verify an email domain for the organization."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    domain = domain.lower().strip()
    if domain not in org.get("email_domains", []):
        raise HTTPException(status_code=400, detail="Domain not in organization's domain list")

    verified = org.get("verified_domains", [])
    if domain not in verified:
        await db.karau_organizations.update_one(
            {"org_id": org_id},
            {"$addToSet": {"verified_domains": domain}}
        )

    return {"success": True, "domain": domain, "verified": True}


@router.get("/{org_id}/check-email")
async def check_email_domain(org_id: str, email: str):
    """Check if an email belongs to this organization's verified domains."""
    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    domain = email.lower().split("@")[-1]
    is_internal = domain in org.get("email_domains", [])
    is_verified = domain in org.get("verified_domains", [])

    return {
        "email": email,
        "domain": domain,
        "is_internal": is_internal,
        "is_verified_domain": is_verified,
        "org_name": org["name"],
        "org_id": org_id,
    }


# ============ CONFERENCE ROOMS ============

@router.post("/{org_id}/rooms")
async def create_conference_room(
    org_id: str,
    request: ConferenceRoomRequest,
    user: dict = Depends(get_current_user)
):
    """Create a conference room for the organization."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    max_rooms = org.get("max_rooms", 10)
    current_count = len(org.get("conference_rooms", []))
    if max_rooms != -1 and current_count >= max_rooms:
        raise HTTPException(
            status_code=400,
            detail=f"Room limit reached ({max_rooms}). Upgrade your tier for more rooms."
        )

    room = {
        "room_id": f"room_{uuid.uuid4().hex[:8]}",
        "name": request.name,
        "building": request.building,
        "floor": request.floor,
        "capacity": min(request.capacity, 1000),
        "equipment": request.equipment,
        "location_type": request.location_type,
        "address": request.address,
        "geo_lat": request.geo_lat,
        "geo_lng": request.geo_lng,
        "status": "available",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.karau_organizations.update_one(
        {"org_id": org_id},
        {"$push": {"conference_rooms": room}}
    )
    return room


@router.get("/{org_id}/rooms")
async def list_conference_rooms(org_id: str, user: dict = Depends(get_current_user)):
    """List conference rooms for the organization."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    rooms = org.get("conference_rooms", [])
    return {"rooms": rooms, "count": len(rooms), "max_rooms": org.get("max_rooms", 10)}


@router.put("/{org_id}/rooms/{room_id}")
async def update_conference_room(
    org_id: str,
    room_id: str,
    request: ConferenceRoomRequest,
    user: dict = Depends(get_current_user)
):
    """Update a conference room."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.karau_organizations.update_one(
        {"org_id": org_id, "conference_rooms.room_id": room_id},
        {"$set": {
            "conference_rooms.$.name": request.name,
            "conference_rooms.$.building": request.building,
            "conference_rooms.$.floor": request.floor,
            "conference_rooms.$.capacity": request.capacity,
            "conference_rooms.$.equipment": request.equipment,
            "conference_rooms.$.location_type": request.location_type,
            "conference_rooms.$.address": request.address,
            "conference_rooms.$.geo_lat": request.geo_lat,
            "conference_rooms.$.geo_lng": request.geo_lng,
            "conference_rooms.$.updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Room not found")

    return {"success": True, "room_id": room_id}


@router.delete("/{org_id}/rooms/{room_id}")
async def delete_conference_room(
    org_id: str,
    room_id: str,
    user: dict = Depends(get_current_user)
):
    """Delete a conference room."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    await db.karau_organizations.update_one(
        {"org_id": org_id},
        {"$pull": {"conference_rooms": {"room_id": room_id}}}
    )
    return {"success": True, "room_id": room_id}


# ============ BRANDING ============

@router.get("/branding/by-domain")
async def get_branding_by_domain(email: str):
    """Get organization branding by email domain (public endpoint for meeting UI)."""
    domain = email.lower().split("@")[-1]
    org = await db.karau_organizations.find_one(
        {"email_domains": domain},
        {"_id": 0, "logo_url": 1, "watermark_text": 1, "primary_color": 1, "name": 1, "tier": 1, "org_id": 1}
    )
    if not org:
        return {"has_branding": False}

    return {
        "has_branding": True,
        "org_id": org.get("org_id"),
        "org_name": org.get("name"),
        "logo_url": org.get("logo_url"),
        "watermark_text": org.get("watermark_text"),
        "primary_color": org.get("primary_color", "#5b5fc7"),
        "tier": org.get("tier"),
    }


@router.get("/branding/{org_id}")
async def get_branding(org_id: str):
    """Get organization branding by org ID (public for meeting footer)."""
    org = await db.karau_organizations.find_one(
        {"org_id": org_id},
        {"_id": 0, "logo_url": 1, "watermark_text": 1, "primary_color": 1, "name": 1, "tier": 1}
    )
    if not org:
        return {"has_branding": False}

    return {
        "has_branding": True,
        "org_name": org.get("name"),
        "logo_url": org.get("logo_url"),
        "watermark_text": org.get("watermark_text"),
        "primary_color": org.get("primary_color", "#5b5fc7"),
        "tier": org.get("tier"),
    }


# ============ EMPLOYEE DIRECTORY (Phase 2 placeholder) ============

@router.post("/{org_id}/employees")
async def add_employee(
    org_id: str,
    employee: EmployeeEntry,
    user: dict = Depends(get_current_user)
):
    """Add an employee to the directory."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check tier limit
    max_users = org.get("max_users", 50)
    current = org.get("employee_count", 0)
    if current >= max_users:
        raise HTTPException(status_code=400, detail=f"User limit reached ({max_users}). Upgrade tier.")

    emp = {
        "employee_id": f"emp_{uuid.uuid4().hex[:8]}",
        "email": employee.email.lower(),
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department": employee.department,
        "title": employee.title,
        "org_id": org_id,
        "status": "active",
        "added_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.karau_employees.insert_one(emp)
    await db.karau_organizations.update_one(
        {"org_id": org_id}, {"$inc": {"employee_count": 1}}
    )

    emp.pop("_id", None)
    return emp


@router.get("/{org_id}/employees")
async def list_employees(
    org_id: str,
    search: str = "",
    user: dict = Depends(get_current_user)
):
    """List/search employees. Supports last name search."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    query = {"org_id": org_id, "status": "active"}
    if search:
        query["$or"] = [
            {"last_name": {"$regex": search, "$options": "i"}},
            {"first_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]

    employees = await db.karau_employees.find(query, {"_id": 0}).to_list(100)
    return {"employees": employees, "count": len(employees)}


@router.post("/{org_id}/employees/bulk")
async def bulk_add_employees(
    org_id: str,
    employees: List[EmployeeEntry],
    user: dict = Depends(get_current_user)
):
    """Bulk add employees (CSV import support)."""
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    org = await db.karau_organizations.find_one({"org_id": org_id}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    max_users = org.get("max_users", 50)
    current = org.get("employee_count", 0)
    available = max_users - current
    if len(employees) > available:
        raise HTTPException(
            status_code=400,
            detail=f"Can only add {available} more employees (limit: {max_users})"
        )

    docs = []
    for emp in employees:
        docs.append({
            "employee_id": f"emp_{uuid.uuid4().hex[:8]}",
            "email": emp.email.lower(),
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "department": emp.department,
            "title": emp.title,
            "org_id": org_id,
            "status": "active",
            "added_at": datetime.now(timezone.utc).isoformat(),
        })

    if docs:
        await db.karau_employees.insert_many(docs)
        await db.karau_organizations.update_one(
            {"org_id": org_id}, {"$inc": {"employee_count": len(docs)}}
        )

    return {"added": len(docs), "total": current + len(docs), "max": max_users}


# ============ TIER INFO (Public) ============

@router.get("/tiers/info")
async def get_tier_info():
    """Get all available tier configurations."""
    return {"tiers": TIER_CONFIG}
