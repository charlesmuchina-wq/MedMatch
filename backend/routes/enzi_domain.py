"""
ENZI Domain-Based Company Discovery
- Users with same email domain can find each other
- Company/domain-based internal messaging
- Domain user directory
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/domain", tags=["ENZI Domain Discovery"])


def _extract_domain(email: str) -> str:
    if "@" in email:
        return email.split("@")[1].lower()
    return ""


# Common free email domains to exclude from company matching
FREE_DOMAINS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com",
    "icloud.com", "mail.com", "protonmail.com", "zoho.com", "yandex.com",
    "live.com", "msn.com", "me.com", "mac.com", "googlemail.com",
    "medmatch.io", "medmatch.com"  # Platform test domains
}


@router.get("/colleagues")
async def get_domain_colleagues(request: Request, q: Optional[str] = None):
    """Find users from the same email domain (company colleagues)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    domain = _extract_domain(user.get("email", ""))
    if not domain or domain in FREE_DOMAINS:
        return {"colleagues": [], "domain": domain, "is_company_domain": False, "message": "Free email domains don't have company colleagues. Invite your team directly!"}

    query = {"email": {"$regex": f"@{domain}$", "$options": "i"}, "user_id": {"$ne": user.get("user_id")}}
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"email": {"$regex": q, "$options": "i"}}
        ]

    colleagues = await db.users.find(query, {"_id": 0, "password_hash": 0}).limit(50).to_list(50)

    return {
        "colleagues": [
            {
                "user_id": c.get("user_id"),
                "name": c.get("name", c.get("email", "").split("@")[0]),
                "email": c.get("email"),
                "role": c.get("role", "user"),
                "created_at": c.get("created_at")
            }
            for c in colleagues
        ],
        "domain": domain,
        "is_company_domain": True,
        "count": len(colleagues)
    }


@router.get("/info")
async def get_domain_info(request: Request):
    """Get domain/company info for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    domain = _extract_domain(user.get("email", ""))
    is_company = domain and domain not in FREE_DOMAINS

    if not is_company:
        return {"domain": domain, "is_company_domain": False, "user_count": 0}

    count = await db.users.count_documents({"email": {"$regex": f"@{domain}$", "$options": "i"}})

    return {
        "domain": domain,
        "is_company_domain": True,
        "user_count": count,
        "company_name": domain.split(".")[0].title()
    }
