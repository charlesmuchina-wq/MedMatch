"""
In-house, zero-cost error tracking / observability.

- POST /api/observability/error   : capture a client-side error (optional auth)
- GET  /api/observability/errors  : admin — list captured errors (filters)
- GET  /api/observability/errors/stats : admin — counts/rollups
- PATCH/DELETE /api/observability/errors/{id} : admin — resolve / delete

Backend unhandled 5xx exceptions are captured by middleware in server.py and
stored in the same `error_logs` collection. No external service required.
"""
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid

from utils.database import db
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/observability", tags=["Observability"])

MAX_MSG = 2000
MAX_STACK = 8000


class ClientError(BaseModel):
    message: str
    stack: Optional[str] = ""
    url: Optional[str] = ""
    level: Optional[str] = "error"      # error | warning | info
    source: Optional[str] = "frontend"
    context: Optional[dict] = None
    release: Optional[str] = ""


def _is_admin(user: Optional[dict]) -> bool:
    return bool(user and (
        user.get("is_admin") or user.get("role") == "admin"
        or user.get("email") == "admin@medmatch.com"
    ))


async def store_error(doc: dict):
    """Shared helper used by this route and the backend exception middleware."""
    doc.setdefault("id", f"err_{uuid.uuid4().hex[:12]}")
    doc.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    doc.setdefault("resolved", False)
    doc["message"] = (doc.get("message") or "")[:MAX_MSG]
    doc["stack"] = (doc.get("stack") or "")[:MAX_STACK]
    await db.error_logs.insert_one(doc)
    return doc["id"]


@router.post("/error")
async def report_error(err: ClientError, request: Request):
    """Capture a client-side error. Auth optional so anonymous errors are still recorded."""
    user = await get_current_user(request)
    err_id = await store_error({
        "message": err.message,
        "stack": err.stack or "",
        "url": err.url or "",
        "level": err.level if err.level in {"error", "warning", "info"} else "error",
        "source": "frontend",
        "context": err.context or {},
        "release": err.release or "",
        "user_agent": request.headers.get("user-agent", ""),
        "user_id": user.get("user_id") if user else None,
        "user_email": user.get("email") if user else None,
        "environment": __import__("os").environ.get("ENVIRONMENT", "development"),
    })
    return {"logged": True, "id": err_id}


@router.get("/errors")
async def list_errors(
    request: Request,
    source: Optional[str] = None,
    level: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
):
    user = await require_auth(request)
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    query = {}
    if source:
        query["source"] = source
    if level:
        query["level"] = level
    if resolved is not None:
        query["resolved"] = resolved
    errors = await db.error_logs.find(query, {"_id": 0}).sort("created_at", -1).to_list(min(limit, 500))
    return {"errors": errors, "count": len(errors)}


@router.get("/errors/stats")
async def error_stats(request: Request):
    user = await require_auth(request)
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    total = await db.error_logs.count_documents({})
    unresolved = await db.error_logs.count_documents({"resolved": False})
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    last_24h = await db.error_logs.count_documents({"created_at": {"$gte": since}})

    by_source, by_level = {}, {}
    async for d in db.error_logs.aggregate([{"$group": {"_id": "$source", "c": {"$sum": 1}}}]):
        by_source[d["_id"] or "unknown"] = d["c"]
    async for d in db.error_logs.aggregate([{"$group": {"_id": "$level", "c": {"$sum": 1}}}]):
        by_level[d["_id"] or "error"] = d["c"]
    return {
        "total": total, "unresolved": unresolved, "last_24h": last_24h,
        "by_source": by_source, "by_level": by_level,
    }


class ResolveBody(BaseModel):
    resolved: bool = True


@router.patch("/errors/{error_id}")
async def resolve_error(error_id: str, body: ResolveBody, request: Request):
    user = await require_auth(request)
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.error_logs.update_one(
        {"id": error_id}, {"$set": {"resolved": body.resolved}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Error not found")
    return {"id": error_id, "resolved": body.resolved}


@router.delete("/errors/{error_id}")
async def delete_error(error_id: str, request: Request):
    user = await require_auth(request)
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.error_logs.delete_one({"id": error_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Error not found")
    return {"deleted": True}
