"""
Enterprise API Routes
Handles: API Key Management, Webhooks, ATS Integration, Bulk Operations
Premium/Enterprise tier features for recruiters
"""
from fastapi import APIRouter, HTTPException, Request, Response, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import uuid
import logging
import secrets
import hashlib
import hmac
import json
import csv
import io
import httpx

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/enterprise", tags=["Enterprise API"])

# ============== Constants ==============

PREMIUM_TIERS = ["recruiter_premium", "recruiter_premium_annual", "enterprise"]
GROWTH_TIERS = ["recruiter_growth", "recruiter_growth_annual"] + PREMIUM_TIERS

# Rate limits by tier (requests per hour)
TIER_RATE_LIMITS = {
    "recruiter_starter": 100,
    "recruiter_starter_annual": 100,
    "recruiter_growth": 500,
    "recruiter_growth_annual": 500,
    "recruiter_premium": 2000,
    "recruiter_premium_annual": 2000,
    "enterprise": 10000
}

# Webhook event types
WEBHOOK_EVENTS = [
    "application.created",
    "application.status_changed",
    "candidate.profile_updated",
    "candidate.credential_verified",
    "job.posted",
    "job.expired",
    "interview.scheduled",
    "interview.completed",
    "message.received"
]

# ============== Models ==============

class APIKeyCreate(BaseModel):
    name: str
    scopes: List[str] = ["read:candidates", "read:applications"]
    expires_in_days: Optional[int] = 365

class WebhookCreate(BaseModel):
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None
    description: Optional[str] = None

class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    active: Optional[bool] = None
    description: Optional[str] = None

class BulkCandidateExport(BaseModel):
    format: str = "csv"  # csv, json
    filters: Optional[Dict[str, Any]] = None
    fields: Optional[List[str]] = None

class BulkCandidateImport(BaseModel):
    candidates: List[Dict[str, Any]]
    source: str = "api_import"

# ============== Helper Functions ==============

def generate_api_key() -> tuple:
    """Generate a secure API key and its hash"""
    # Generate a secure random key
    key_bytes = secrets.token_bytes(32)
    api_key = f"mm_live_{secrets.token_urlsafe(32)}"
    
    # Hash for storage (never store raw key)
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    
    # Return prefix for display and full key (shown only once)
    return api_key, key_hash, api_key[:12] + "..."

def verify_api_key(api_key: str, stored_hash: str) -> bool:
    """Verify an API key against its stored hash"""
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return hmac.compare_digest(key_hash, stored_hash)

def generate_webhook_secret() -> str:
    """Generate a webhook signing secret"""
    return f"whsec_{secrets.token_urlsafe(32)}"

def sign_webhook_payload(payload: dict, secret: str) -> str:
    """Sign a webhook payload for verification"""
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    signature = hmac.new(
        secret.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

async def check_tier_access(user: dict, required_tiers: list) -> bool:
    """Check if user has access to premium features"""
    user_tier = user.get("subscription_plan", "recruiter_starter")
    return user_tier in required_tiers

async def get_rate_limit(user: dict) -> int:
    """Get rate limit based on user tier"""
    user_tier = user.get("subscription_plan", "recruiter_starter")
    return TIER_RATE_LIMITS.get(user_tier, 100)

# ============== API Key Management ==============

@router.post("/api-keys")
async def create_api_key(data: APIKeyCreate, request: Request):
    """
    Create a new API key for programmatic access
    Premium tier required
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can create API keys")
    
    # Check tier access
    if not await check_tier_access(user, PREMIUM_TIERS):
        raise HTTPException(
            status_code=403, 
            detail="API access requires Premium or Enterprise tier. Please upgrade your subscription."
        )
    
    # Check existing key count (limit to 5)
    existing_count = await db.api_keys.count_documents({
        "user_id": user["user_id"],
        "revoked": {"$ne": True}
    })
    if existing_count >= 5:
        raise HTTPException(status_code=400, detail="Maximum 5 active API keys allowed")
    
    # Validate scopes
    valid_scopes = [
        "read:candidates", "write:candidates",
        "read:applications", "write:applications",
        "read:jobs", "write:jobs",
        "read:interviews", "write:interviews",
        "webhooks:manage"
    ]
    for scope in data.scopes:
        if scope not in valid_scopes:
            raise HTTPException(status_code=400, detail=f"Invalid scope: {scope}")
    
    # Generate key
    api_key, key_hash, key_preview = generate_api_key()
    
    expires_at = None
    if data.expires_in_days:
        expires_at = (datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)).isoformat()
    
    key_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "organization_id": user.get("organization_id"),
        "name": data.name,
        "key_hash": key_hash,
        "key_preview": key_preview,
        "scopes": data.scopes,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": expires_at,
        "last_used_at": None,
        "usage_count": 0,
        "revoked": False
    }
    
    await db.api_keys.insert_one(key_doc)
    
    # Return the full key ONLY ONCE
    return {
        "message": "API key created successfully. Store this key securely - it won't be shown again.",
        "api_key": api_key,
        "key_id": key_doc["id"],
        "name": data.name,
        "scopes": data.scopes,
        "expires_at": expires_at,
        "rate_limit": await get_rate_limit(user)
    }

@router.get("/api-keys")
async def list_api_keys(request: Request):
    """List all API keys for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    keys = await db.api_keys.find(
        {"user_id": user["user_id"], "revoked": {"$ne": True}},
        {"_id": 0, "key_hash": 0}
    ).to_list(100)
    
    return {
        "api_keys": keys,
        "count": len(keys),
        "tier": user.get("subscription_plan", "recruiter_starter"),
        "rate_limit": await get_rate_limit(user)
    }

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(key_id: str, request: Request):
    """Revoke an API key"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.api_keys.update_one(
        {"id": key_id, "user_id": user["user_id"]},
        {"$set": {
            "revoked": True,
            "revoked_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="API key not found")
    
    return {"message": "API key revoked successfully"}

@router.post("/api-keys/{key_id}/rotate")
async def rotate_api_key(key_id: str, request: Request):
    """Rotate an API key (revoke old, create new with same settings)"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find existing key
    existing = await db.api_keys.find_one(
        {"id": key_id, "user_id": user["user_id"], "revoked": {"$ne": True}}
    )
    if not existing:
        raise HTTPException(status_code=404, detail="API key not found")
    
    # Revoke old key
    await db.api_keys.update_one(
        {"id": key_id},
        {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create new key with same settings
    api_key, key_hash, key_preview = generate_api_key()
    
    new_key_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "organization_id": user.get("organization_id"),
        "name": existing["name"],
        "key_hash": key_hash,
        "key_preview": key_preview,
        "scopes": existing["scopes"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": existing.get("expires_at"),
        "last_used_at": None,
        "usage_count": 0,
        "revoked": False,
        "rotated_from": key_id
    }
    
    await db.api_keys.insert_one(new_key_doc)
    
    return {
        "message": "API key rotated successfully",
        "api_key": api_key,
        "key_id": new_key_doc["id"],
        "previous_key_id": key_id
    }

# ============== Webhook Management ==============

@router.post("/webhooks")
async def create_webhook(data: WebhookCreate, request: Request):
    """
    Create a webhook endpoint for ATS integration
    Growth tier or higher required
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can create webhooks")
    
    # Check tier access
    if not await check_tier_access(user, GROWTH_TIERS):
        raise HTTPException(
            status_code=403,
            detail="Webhooks require Growth tier or higher. Please upgrade your subscription."
        )
    
    # Validate events
    for event in data.events:
        if event not in WEBHOOK_EVENTS:
            raise HTTPException(status_code=400, detail=f"Invalid event type: {event}")
    
    # Check existing webhook count
    existing_count = await db.webhooks.count_documents({
        "user_id": user["user_id"],
        "active": True
    })
    max_webhooks = 10 if await check_tier_access(user, PREMIUM_TIERS) else 3
    if existing_count >= max_webhooks:
        raise HTTPException(status_code=400, detail=f"Maximum {max_webhooks} active webhooks allowed for your tier")
    
    # Generate secret if not provided
    secret = data.secret or generate_webhook_secret()
    
    webhook_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["user_id"],
        "organization_id": user.get("organization_id"),
        "url": str(data.url),
        "events": data.events,
        "secret": secret,
        "description": data.description,
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_triggered_at": None,
        "success_count": 0,
        "failure_count": 0
    }
    
    await db.webhooks.insert_one(webhook_doc)
    
    return {
        "message": "Webhook created successfully",
        "webhook_id": webhook_doc["id"],
        "url": webhook_doc["url"],
        "events": data.events,
        "secret": secret,
        "note": "Store this secret securely for signature verification"
    }

@router.get("/webhooks")
async def list_webhooks(request: Request):
    """List all webhooks for the current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    webhooks = await db.webhooks.find(
        {"user_id": user["user_id"]},
        {"_id": 0, "secret": 0}
    ).to_list(100)
    
    return {
        "webhooks": webhooks,
        "count": len(webhooks),
        "available_events": WEBHOOK_EVENTS
    }

@router.get("/webhooks/{webhook_id}")
async def get_webhook(webhook_id: str, request: Request):
    """Get webhook details"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "user_id": user["user_id"]},
        {"_id": 0}
    )
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Get recent deliveries
    deliveries = await db.webhook_deliveries.find(
        {"webhook_id": webhook_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(20)
    
    return {
        **webhook,
        "recent_deliveries": deliveries
    }

@router.put("/webhooks/{webhook_id}")
async def update_webhook(webhook_id: str, data: WebhookUpdate, request: Request):
    """Update a webhook"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    update_data = {}
    if data.url:
        update_data["url"] = str(data.url)
    if data.events:
        for event in data.events:
            if event not in WEBHOOK_EVENTS:
                raise HTTPException(status_code=400, detail=f"Invalid event type: {event}")
        update_data["events"] = data.events
    if data.active is not None:
        update_data["active"] = data.active
    if data.description:
        update_data["description"] = data.description
    
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await db.webhooks.update_one(
        {"id": webhook_id, "user_id": user["user_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {"message": "Webhook updated successfully"}

@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, request: Request):
    """Delete a webhook"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.webhooks.delete_one(
        {"id": webhook_id, "user_id": user["user_id"]}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    return {"message": "Webhook deleted successfully"}

@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(webhook_id: str, request: Request):
    """Send a test event to a webhook"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    webhook = await db.webhooks.find_one(
        {"id": webhook_id, "user_id": user["user_id"]}
    )
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    # Send test payload
    test_payload = {
        "event": "test",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "message": "This is a test webhook delivery from MedMatch",
            "webhook_id": webhook_id
        }
    }
    
    signature = sign_webhook_payload(test_payload, webhook["secret"])
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                webhook["url"],
                json=test_payload,
                headers={
                    "Content-Type": "application/json",
                    "X-MedMatch-Signature": signature,
                    "X-MedMatch-Event": "test",
                    "X-MedMatch-Delivery": str(uuid.uuid4())
                }
            )
        
        success = 200 <= response.status_code < 300
        
        # Log delivery
        await db.webhook_deliveries.insert_one({
            "id": str(uuid.uuid4()),
            "webhook_id": webhook_id,
            "event": "test",
            "payload": test_payload,
            "response_status": response.status_code,
            "success": success,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        
        return {
            "success": success,
            "status_code": response.status_code,
            "message": "Test webhook sent successfully" if success else "Webhook endpoint returned error"
        }
        
    except Exception as e:
        logging.error(f"Webhook test failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to deliver test webhook"
        }

# ============== Webhook Trigger Function (Internal) ==============

async def trigger_webhooks(user_id: str, event: str, data: dict):
    """
    Trigger all active webhooks for a user with matching event
    Called internally when events occur
    """
    webhooks = await db.webhooks.find({
        "user_id": user_id,
        "active": True,
        "events": event
    }).to_list(100)
    
    for webhook in webhooks:
        payload = {
            "event": event,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        signature = sign_webhook_payload(payload, webhook["secret"])
        delivery_id = str(uuid.uuid4())
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook["url"],
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-MedMatch-Signature": signature,
                        "X-MedMatch-Event": event,
                        "X-MedMatch-Delivery": delivery_id
                    }
                )
            
            success = 200 <= response.status_code < 300
            
            # Log delivery
            await db.webhook_deliveries.insert_one({
                "id": delivery_id,
                "webhook_id": webhook["id"],
                "event": event,
                "payload": payload,
                "response_status": response.status_code,
                "success": success,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            # Update webhook stats
            if success:
                await db.webhooks.update_one(
                    {"id": webhook["id"]},
                    {
                        "$inc": {"success_count": 1},
                        "$set": {"last_triggered_at": datetime.now(timezone.utc).isoformat()}
                    }
                )
            else:
                await db.webhooks.update_one(
                    {"id": webhook["id"]},
                    {"$inc": {"failure_count": 1}}
                )
                
        except Exception as e:
            logging.error(f"Webhook delivery failed for {webhook['id']}: {e}")
            await db.webhook_deliveries.insert_one({
                "id": delivery_id,
                "webhook_id": webhook["id"],
                "event": event,
                "payload": payload,
                "error": str(e),
                "success": False,
                "created_at": datetime.now(timezone.utc).isoformat()
            })

# ============== Bulk Export ==============

@router.post("/export/candidates")
async def export_candidates(data: BulkCandidateExport, request: Request):
    """
    Export candidates in CSV or JSON format
    Premium tier required
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can export candidates")
    
    if not await check_tier_access(user, PREMIUM_TIERS):
        raise HTTPException(
            status_code=403,
            detail="Bulk export requires Premium or Enterprise tier"
        )
    
    # Build query
    query = {}
    if data.filters:
        if "skills" in data.filters:
            query["skills"] = {"$in": data.filters["skills"]}
        if "location" in data.filters:
            query["location"] = {"$regex": data.filters["location"], "$options": "i"}
    
    # Default fields
    default_fields = ["name", "email", "skills", "experience_years", "location", "created_at"]
    fields = data.fields or default_fields
    
    # Build projection
    projection = {"_id": 0}
    for field in fields:
        projection[field] = 1
    
    # Get candidates (limit to 1000 for safety)
    candidates = await db.resumes.find(query, projection).to_list(1000)
    
    if data.format == "json":
        return {
            "candidates": candidates,
            "count": len(candidates),
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
    
    # CSV format
    if not candidates:
        return Response(
            content="No candidates found",
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=candidates.csv"}
        )
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    
    for candidate in candidates:
        # Flatten lists for CSV
        row = {}
        for field in fields:
            value = candidate.get(field, "")
            if isinstance(value, list):
                row[field] = "; ".join(str(v) for v in value)
            else:
                row[field] = value
        writer.writerow(row)
    
    csv_content = output.getvalue()
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=candidates_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )

@router.post("/export/applications")
async def export_applications(data: BulkCandidateExport, request: Request):
    """
    Export job applications in CSV or JSON format
    Premium tier required
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can export applications")
    
    if not await check_tier_access(user, PREMIUM_TIERS):
        raise HTTPException(
            status_code=403,
            detail="Bulk export requires Premium or Enterprise tier"
        )
    
    # Get recruiter's jobs
    recruiter_jobs = await db.posted_jobs.find(
        {"recruiter_id": user["user_id"]},
        {"id": 1}
    ).to_list(1000)
    job_ids = [j["id"] for j in recruiter_jobs]
    
    # Get applications for those jobs
    applications = await db.applications.find(
        {"job_id": {"$in": job_ids}},
        {"_id": 0}
    ).to_list(5000)
    
    if data.format == "json":
        return {
            "applications": applications,
            "count": len(applications),
            "exported_at": datetime.now(timezone.utc).isoformat()
        }
    
    # CSV format
    fields = ["applicant_id", "job_id", "status", "applied_at", "notes"]
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    
    for app in applications:
        writer.writerow(app)
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=applications_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )

# ============== Bulk Import ==============

@router.post("/import/candidates")
async def import_candidates(data: BulkCandidateImport, request: Request):
    """
    Bulk import candidates from external ATS
    Premium tier required
    """
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if user.get("role") != "recruiter":
        raise HTTPException(status_code=403, detail="Only recruiters can import candidates")
    
    if not await check_tier_access(user, PREMIUM_TIERS):
        raise HTTPException(
            status_code=403,
            detail="Bulk import requires Premium or Enterprise tier"
        )
    
    if len(data.candidates) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 candidates per import")
    
    imported = 0
    errors = []
    
    for idx, candidate in enumerate(data.candidates):
        try:
            # Validate required fields
            if not candidate.get("email"):
                errors.append({"index": idx, "error": "Email is required"})
                continue
            
            # Check if candidate exists
            existing = await db.imported_candidates.find_one(
                {"email": candidate["email"], "recruiter_id": user["user_id"]}
            )
            
            candidate_doc = {
                "id": str(uuid.uuid4()),
                "recruiter_id": user["user_id"],
                "organization_id": user.get("organization_id"),
                "email": candidate["email"],
                "name": candidate.get("name", ""),
                "phone": candidate.get("phone", ""),
                "skills": candidate.get("skills", []),
                "experience_years": candidate.get("experience_years"),
                "location": candidate.get("location", ""),
                "source": data.source,
                "external_id": candidate.get("external_id"),
                "notes": candidate.get("notes", ""),
                "imported_at": datetime.now(timezone.utc).isoformat()
            }
            
            if existing:
                await db.imported_candidates.update_one(
                    {"_id": existing["_id"]},
                    {"$set": candidate_doc}
                )
            else:
                await db.imported_candidates.insert_one(candidate_doc)
            
            imported += 1
            
        except Exception as e:
            errors.append({"index": idx, "error": str(e)})
    
    return {
        "message": f"Import completed: {imported} candidates processed",
        "imported": imported,
        "errors": errors,
        "total_submitted": len(data.candidates)
    }

# ============== ATS Integration Endpoints ==============

@router.get("/ats/status")
async def get_ats_status(request: Request):
    """Get ATS integration status and available features"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    tier = user.get("subscription_plan", "recruiter_starter")
    
    # Count active integrations
    api_keys = await db.api_keys.count_documents({
        "user_id": user["user_id"],
        "revoked": {"$ne": True}
    })
    
    webhooks = await db.webhooks.count_documents({
        "user_id": user["user_id"],
        "active": True
    })
    
    return {
        "tier": tier,
        "features": {
            "api_access": tier in PREMIUM_TIERS,
            "webhooks": tier in GROWTH_TIERS,
            "bulk_export": tier in PREMIUM_TIERS,
            "bulk_import": tier in PREMIUM_TIERS,
            "sso": tier == "enterprise"
        },
        "integrations": {
            "api_keys": api_keys,
            "webhooks": webhooks
        },
        "rate_limit": TIER_RATE_LIMITS.get(tier, 100),
        "webhook_events": WEBHOOK_EVENTS
    }

@router.get("/ats/docs")
async def get_ats_documentation():
    """Get ATS integration documentation"""
    return {
        "api_version": "v1",
        "base_url": "/api/enterprise",
        "authentication": {
            "type": "Bearer Token",
            "header": "Authorization: Bearer mm_live_xxxxx",
            "description": "Include your API key in the Authorization header"
        },
        "endpoints": {
            "candidates": {
                "list": "GET /api/candidates",
                "get": "GET /api/candidates/{id}",
                "search": "POST /api/recruiter/search"
            },
            "applications": {
                "list": "GET /api/recruiter/applications",
                "update_status": "PUT /api/recruiter/applications/{id}/status"
            },
            "jobs": {
                "list": "GET /api/recruiter/jobs",
                "create": "POST /api/recruiter/jobs",
                "update": "PUT /api/recruiter/jobs/{id}"
            }
        },
        "webhooks": {
            "events": WEBHOOK_EVENTS,
            "signature_header": "X-MedMatch-Signature",
            "signature_format": "sha256=<hex_digest>",
            "verification": "HMAC-SHA256 of JSON payload with your webhook secret"
        },
        "rate_limits": TIER_RATE_LIMITS
    }
