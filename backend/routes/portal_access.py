"""
Portal Access Manager
Manages user access across portals: MedMatch, AI KARAU, ENZI
Package structure:
  - Standard: AI KARAU + ENZI (bundled)
  - Standalone: MedMatch Job Toolkit
  - Enterprise: All 3 portals
"""
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user, create_session, create_session_token

router = APIRouter(prefix="/portal", tags=["Portal Access"])

PACKAGES = {
    "standard": {
        "name": "AI KARAU + ENZI",
        "description": "Communication suite — video meetings + messaging",
        "portals": ["karau", "enzi"],
        "price": 0,
        "is_default": True
    },
    "medmatch_standalone": {
        "name": "MedMatch Job Toolkit",
        "description": "AI-powered job search, resume builder, interview prep",
        "portals": ["medmatch"],
        "price": 0,
        "is_default": False
    },
    "enterprise": {
        "name": "Enterprise Suite",
        "description": "All 3 portals — recruit, meet, and message in one platform",
        "portals": ["medmatch", "karau", "enzi"],
        "price": 0,
        "is_default": False
    }
}

PORTAL_INFO = {
    "medmatch": {"name": "MedMatch Job Toolkit", "path": "/", "icon": "briefcase", "color": "#00B894"},
    "karau": {"name": "AI KARAU", "path": "/karau-meet", "icon": "video", "color": "#6C5CE7"},
    "enzi": {"name": "ENZI Messenger", "path": "/lumi", "icon": "message-square", "color": "#00CEC9"}
}


class SetPackageRequest(BaseModel):
    package_id: str


@router.get("/packages")
async def get_packages():
    """Get all available portal packages"""
    return {"packages": [{"id": k, **v} for k, v in PACKAGES.items()], "portals": PORTAL_INFO}


@router.get("/access")
async def get_portal_access(request: Request):
    """Get current user's portal access"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    uid = user["user_id"]
    access = await db.portal_access.find_one({"user_id": uid}, {"_id": 0})

    if not access:
        # Default: give all portals (enterprise) for existing users
        access = {
            "user_id": uid,
            "package_id": "enterprise",
            "portals": ["medmatch", "karau", "enzi"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.portal_access.insert_one({**access})

    return {
        "package_id": access.get("package_id", "enterprise"),
        "package_name": PACKAGES.get(access.get("package_id", "enterprise"), {}).get("name", "Enterprise Suite"),
        "portals": access.get("portals", ["medmatch", "karau", "enzi"]),
        "portal_info": {p: PORTAL_INFO[p] for p in access.get("portals", []) if p in PORTAL_INFO}
    }


@router.post("/set-package")
async def set_package(req: SetPackageRequest, request: Request):
    """Set user's portal package"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if req.package_id not in PACKAGES:
        raise HTTPException(status_code=400, detail="Invalid package")

    pkg = PACKAGES[req.package_id]
    await db.portal_access.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "user_id": user["user_id"],
            "package_id": req.package_id,
            "portals": pkg["portals"],
            "updated_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    return {"status": "updated", "package_id": req.package_id, "portals": pkg["portals"]}


@router.post("/sync-session")
async def sync_session(request: Request, response: Response):
    """Synchronize session across portals — creates cookie + returns token"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Create a new session token
    session_token = create_session_token()
    await create_session(user["user_id"], session_token)

    # Set cookie for MedMatch (cookie-based auth)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,
        path="/"
    )

    return {
        "token": session_token,
        "user": {
            "user_id": user["user_id"],
            "email": user.get("email", ""),
            "name": user.get("name", ""),
            "role": user.get("role", ""),
            "auth_method": user.get("auth_method", ""),
        }
    }


@router.get("/check-access/{portal}")
async def check_portal_access(portal: str, request: Request):
    """Check if current user has access to a specific portal"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if portal not in PORTAL_INFO:
        raise HTTPException(status_code=400, detail="Invalid portal")

    access = await db.portal_access.find_one({"user_id": user["user_id"]}, {"_id": 0})
    portals = access.get("portals", ["medmatch", "karau", "enzi"]) if access else ["medmatch", "karau", "enzi"]

    return {
        "has_access": portal in portals,
        "portal": portal,
        "portal_info": PORTAL_INFO.get(portal, {})
    }
