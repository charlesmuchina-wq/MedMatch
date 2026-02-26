"""
AI KARAU Meeting - Collaboration API Routes
Whiteboard, File Sharing, and Action Items
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
import base64

from services.karau_meet.collaboration_service import (
    create_whiteboard,
    get_whiteboard,
    add_whiteboard_element,
    update_whiteboard_element,
    delete_whiteboard_element,
    clear_whiteboard,
    export_whiteboard,
    share_file,
    get_shared_files,
    get_file,
    delete_shared_file,
    pin_file,
    create_action_item,
    get_action_items,
    update_action_item,
    add_action_item_note,
    delete_action_item,
    extract_action_items_from_transcript
)
from routes.auth import get_current_user, require_auth

router = APIRouter(prefix="/karau-meet/collab", tags=["AI KARAU Collaboration"])


# ============ WHITEBOARD ENDPOINTS ============

class WhiteboardElementRequest(BaseModel):
    type: str  # path, rect, circle, text, line, arrow, image
    data: Dict
    style: Optional[Dict] = None
    position: Optional[Dict] = None


class WhiteboardElementUpdate(BaseModel):
    data: Optional[Dict] = None
    style: Optional[Dict] = None
    position: Optional[Dict] = None


@router.post("/meetings/{meeting_id}/whiteboard")
async def create_meeting_whiteboard(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Create a whiteboard for a meeting"""
    
    whiteboard = await create_whiteboard(meeting_id, user["user_id"])
    return whiteboard


@router.get("/meetings/{meeting_id}/whiteboard")
async def get_meeting_whiteboard(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get whiteboard for a meeting"""
    
    whiteboard = await get_whiteboard(meeting_id)
    
    if not whiteboard:
        # Auto-create whiteboard if it doesn't exist
        whiteboard = await create_whiteboard(meeting_id, user["user_id"])
    
    return whiteboard


@router.post("/meetings/{meeting_id}/whiteboard/elements")
async def add_element(
    meeting_id: str,
    request: WhiteboardElementRequest,
    user: dict = Depends(require_auth)
):
    """Add an element to the whiteboard"""
    
    element = await add_whiteboard_element(
        meeting_id=meeting_id,
        element={
            "type": request.type,
            "data": request.data,
            "style": request.style,
            "position": request.position
        },
        user_id=user["user_id"]
    )
    
    return element


@router.put("/meetings/{meeting_id}/whiteboard/elements/{element_id}")
async def update_element(
    meeting_id: str,
    element_id: str,
    request: WhiteboardElementUpdate,
    user: dict = Depends(require_auth)
):
    """Update a whiteboard element"""
    
    success = await update_whiteboard_element(
        meeting_id=meeting_id,
        element_id=element_id,
        updates=request.dict(exclude_none=True)
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Element not found")
    
    return {"success": True}


@router.delete("/meetings/{meeting_id}/whiteboard/elements/{element_id}")
async def remove_element(
    meeting_id: str,
    element_id: str,
    user: dict = Depends(require_auth)
):
    """Delete a whiteboard element"""
    
    success = await delete_whiteboard_element(meeting_id, element_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Element not found")
    
    return {"success": True}


@router.delete("/meetings/{meeting_id}/whiteboard/clear")
async def clear_meeting_whiteboard(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Clear all whiteboard elements"""
    
    success = await clear_whiteboard(meeting_id)
    return {"success": success}


@router.get("/meetings/{meeting_id}/whiteboard/export")
async def export_meeting_whiteboard(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Export whiteboard data for rendering"""
    
    data = await export_whiteboard(meeting_id)
    
    if not data:
        raise HTTPException(status_code=404, detail="Whiteboard not found")
    
    return data


# ============ FILE SHARING ENDPOINTS ============

class ShareFileRequest(BaseModel):
    file_name: str
    file_type: str
    file_size: int
    file_data: Optional[str] = None  # Base64 for small files
    file_url: Optional[str] = None   # URL for larger files


@router.post("/meetings/{meeting_id}/files")
async def share_meeting_file(
    meeting_id: str,
    request: ShareFileRequest,
    user: dict = Depends(require_auth)
):
    """Share a file in the meeting"""
    
    file = await share_file(
        meeting_id=meeting_id,
        user_id=user["user_id"],
        user_name=user.get("name", user.get("email", "Unknown")),
        file_name=request.file_name,
        file_type=request.file_type,
        file_size=request.file_size,
        file_data=request.file_data,
        file_url=request.file_url
    )
    
    return file


@router.post("/meetings/{meeting_id}/files/upload")
async def upload_meeting_file(
    meeting_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(require_auth)
):
    """Upload a file to share in the meeting"""
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # For small files, store as base64
    if file_size < 5 * 1024 * 1024:  # 5MB limit for inline storage
        file_data = base64.b64encode(content).decode('utf-8')
        file_url = None
    else:
        # For larger files, would upload to cloud storage
        # For now, reject files over 5MB
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    shared = await share_file(
        meeting_id=meeting_id,
        user_id=user["user_id"],
        user_name=user.get("name", user.get("email", "Unknown")),
        file_name=file.filename,
        file_type=file.content_type or "application/octet-stream",
        file_size=file_size,
        file_data=file_data,
        file_url=file_url
    )
    
    return shared


@router.get("/meetings/{meeting_id}/files")
async def list_meeting_files(
    meeting_id: str,
    user: dict = Depends(require_auth)
):
    """Get all files shared in a meeting"""
    
    files = await get_shared_files(meeting_id)
    return {"files": files}


@router.get("/files/{file_id}")
async def download_file(
    file_id: str,
    user: dict = Depends(require_auth)
):
    """Download a shared file"""
    
    file = await get_file(file_id)
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return file


@router.delete("/files/{file_id}")
async def remove_file(
    file_id: str,
    user: dict = Depends(require_auth)
):
    """Delete a shared file"""
    
    success = await delete_shared_file(file_id, user["user_id"])
    
    if not success:
        raise HTTPException(status_code=403, detail="Cannot delete file. You may not be the owner.")
    
    return {"success": True}


@router.put("/files/{file_id}/pin")
async def toggle_pin_file(
    file_id: str,
    is_pinned: bool,
    user: dict = Depends(require_auth)
):
    """Pin or unpin a file"""
    
    success = await pin_file(file_id, is_pinned)
    return {"success": success}


# ============ ACTION ITEMS ENDPOINTS ============

class ActionItemRequest(BaseModel):
    title: str
    description: str = ""
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"


class ActionItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_to_name: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class ActionItemNoteRequest(BaseModel):
    note: str


@router.post("/meetings/{meeting_id}/action-items")
async def create_meeting_action_item(
    meeting_id: str,
    request: ActionItemRequest,
    user: dict = Depends(require_auth)
):
    """Create an action item for a meeting"""
    
    item = await create_action_item(
        meeting_id=meeting_id,
        title=request.title,
        description=request.description,
        assigned_to=request.assigned_to,
        assigned_to_name=request.assigned_to_name,
        due_date=request.due_date,
        priority=request.priority,
        created_by=user["user_id"]
    )
    
    return item


@router.get("/meetings/{meeting_id}/action-items")
async def list_meeting_action_items(
    meeting_id: str,
    status: Optional[str] = None,
    user: dict = Depends(require_auth)
):
    """Get all action items for a meeting"""
    
    items = await get_action_items(meeting_id=meeting_id, status=status)
    return {"action_items": items}


@router.get("/action-items")
async def list_my_action_items(
    status: Optional[str] = None,
    user: dict = Depends(require_auth)
):
    """Get all action items assigned to or created by the user"""
    
    items = await get_action_items(user_id=user["user_id"], status=status)
    return {"action_items": items}


@router.put("/action-items/{item_id}")
async def update_meeting_action_item(
    item_id: str,
    request: ActionItemUpdate,
    user: dict = Depends(require_auth)
):
    """Update an action item"""
    
    result = await update_action_item(
        item_id=item_id,
        updates=request.dict(exclude_none=True)
    )
    
    return result


@router.post("/action-items/{item_id}/notes")
async def add_note_to_action_item(
    item_id: str,
    request: ActionItemNoteRequest,
    user: dict = Depends(require_auth)
):
    """Add a note to an action item"""
    
    note = await add_action_item_note(
        item_id=item_id,
        note=request.note,
        user_id=user["user_id"],
        user_name=user.get("name", user.get("email", "Unknown"))
    )
    
    return note


@router.delete("/action-items/{item_id}")
async def remove_action_item(
    item_id: str,
    user: dict = Depends(require_auth)
):
    """Delete an action item"""
    
    success = await delete_action_item(item_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Action item not found")
    
    return {"success": True}


@router.post("/meetings/{meeting_id}/action-items/extract")
async def extract_action_items(
    meeting_id: str,
    transcript: str,
    participants: List[str] = [],
    user: dict = Depends(require_auth)
):
    """AI-powered extraction of action items from transcript"""
    
    items = await extract_action_items_from_transcript(
        meeting_id=meeting_id,
        transcript=transcript,
        participants=participants
    )
    
    return {"action_items": items, "count": len(items)}
