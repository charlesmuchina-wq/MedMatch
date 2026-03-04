"""
LUMI File Storage - Object Storage integration for file sharing in LUMI Messenger
"""
import os
import uuid
import requests
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Query, Header
from fastapi.responses import Response

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi", tags=["LUMI Files"])

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "lumi-messenger"
storage_key = None

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "application/pdf", "text/plain", "text/csv",
    "application/json", "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

def init_storage():
    global storage_key
    if storage_key:
        return storage_key
    resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": EMERGENT_KEY}, timeout=30)
    resp.raise_for_status()
    storage_key = resp.json()["storage_key"]
    return storage_key

def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data, timeout=120
    )
    resp.raise_for_status()
    return resp.json()

def get_object(path: str) -> tuple:
    key = init_storage()
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key}, timeout=60
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")


@router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), channel_id: str = Query(...)):
    """Upload a file to a channel/DM"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    # Validate channel membership
    channel = await db.lumi_channels.find_one(
        {"id": channel_id, "members.user_id": user["user_id"]},
        {"_id": 0, "id": 1}
    )
    if not channel:
        raise HTTPException(status_code=403, detail="Not a member of this channel")

    # Read file
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    content_type = file.content_type or "application/octet-stream"

    # Upload to storage
    ext = file.filename.split(".")[-1] if "." in file.filename else "bin"
    storage_path = f"{APP_NAME}/uploads/{user['user_id']}/{uuid.uuid4()}.{ext}"

    try:
        result = put_object(storage_path, data, content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    # Store reference in DB
    file_id = f"file_{uuid.uuid4().hex[:10]}"
    file_record = {
        "id": file_id,
        "storage_path": result["path"],
        "original_filename": file.filename,
        "content_type": content_type,
        "size": result.get("size", len(data)),
        "channel_id": channel_id,
        "uploaded_by": user["user_id"],
        "uploader_name": user.get("name", user.get("email", "")),
        "is_image": content_type.startswith("image/"),
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.lumi_files.insert_one(file_record)
    file_record.pop("_id", None)

    return file_record


@router.get("/files/{file_id}")
async def download_file(file_id: str, request: Request, auth: str = Query(None)):
    """Download/serve a file. Supports query param auth for img tags."""
    # For query param auth, we need to simulate a proper request
    user = await get_current_user(request)

    if not user and auth:
        # Manually look up session by token (for img src tags)
        session = await db.user_sessions.find_one({"session_token": auth}, {"_id": 0})
        if session:
            user = await db.users.find_one({"user_id": session["user_id"]}, {"_id": 0})

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    record = await db.lumi_files.find_one({"id": file_id, "is_deleted": False}, {"_id": 0})
    if not record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        data, ct = get_object(record["storage_path"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

    return Response(
        content=data,
        media_type=record.get("content_type", ct),
        headers={"Content-Disposition": f'inline; filename="{record["original_filename"]}"'}
    )
