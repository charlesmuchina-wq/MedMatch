"""
AI KARAU Meeting - Collaboration Service
Whiteboard, File Sharing, and Action Items
"""

import os
import uuid
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
whiteboards = db.karau_whiteboards
shared_files = db.karau_shared_files
action_items = db.karau_action_items


# ============ WHITEBOARD ============

async def create_whiteboard(meeting_id: str, created_by: str) -> Dict:
    """Create a new whiteboard for a meeting"""
    
    whiteboard_id = str(uuid.uuid4())[:8]
    
    whiteboard = {
        "whiteboard_id": whiteboard_id,
        "meeting_id": meeting_id,
        "created_by": created_by,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "elements": [],  # Drawing elements
        "background": "white",
        "width": 1920,
        "height": 1080,
        "collaborators": [created_by],
        "is_locked": False
    }
    
    await whiteboards.insert_one({**whiteboard, "_id": whiteboard_id})
    
    return whiteboard


async def get_whiteboard(meeting_id: str) -> Optional[Dict]:
    """Get whiteboard for a meeting"""
    
    whiteboard = await whiteboards.find_one(
        {"meeting_id": meeting_id},
        {"_id": 0}
    )
    
    return whiteboard


async def add_whiteboard_element(
    meeting_id: str,
    element: Dict,
    user_id: str
) -> Dict:
    """Add a drawing element to the whiteboard"""
    
    element_id = str(uuid.uuid4())[:8]
    
    element_data = {
        "element_id": element_id,
        "type": element.get("type", "path"),  # path, rect, circle, text, line, arrow, image
        "data": element.get("data", {}),
        "style": element.get("style", {
            "stroke": "#000000",
            "strokeWidth": 2,
            "fill": "transparent"
        }),
        "position": element.get("position", {"x": 0, "y": 0}),
        "created_by": user_id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await whiteboards.update_one(
        {"meeting_id": meeting_id},
        {
            "$push": {"elements": element_data},
            "$set": {"updated_at": datetime.utcnow().isoformat()}
        }
    )
    
    return element_data


async def update_whiteboard_element(
    meeting_id: str,
    element_id: str,
    updates: Dict
) -> bool:
    """Update a whiteboard element"""
    
    result = await whiteboards.update_one(
        {"meeting_id": meeting_id, "elements.element_id": element_id},
        {"$set": {
            "elements.$.data": updates.get("data"),
            "elements.$.style": updates.get("style"),
            "elements.$.position": updates.get("position"),
            "updated_at": datetime.utcnow().isoformat()
        }}
    )
    
    return result.modified_count > 0


async def delete_whiteboard_element(
    meeting_id: str,
    element_id: str
) -> bool:
    """Delete a whiteboard element"""
    
    result = await whiteboards.update_one(
        {"meeting_id": meeting_id},
        {
            "$pull": {"elements": {"element_id": element_id}},
            "$set": {"updated_at": datetime.utcnow().isoformat()}
        }
    )
    
    return result.modified_count > 0


async def clear_whiteboard(meeting_id: str) -> bool:
    """Clear all elements from whiteboard"""
    
    result = await whiteboards.update_one(
        {"meeting_id": meeting_id},
        {
            "$set": {
                "elements": [],
                "updated_at": datetime.utcnow().isoformat()
            }
        }
    )
    
    return result.modified_count > 0


async def export_whiteboard(meeting_id: str) -> Optional[Dict]:
    """Export whiteboard as image data"""
    
    whiteboard = await get_whiteboard(meeting_id)
    if not whiteboard:
        return None
    
    # Return whiteboard data for frontend to render as PNG
    return {
        "meeting_id": meeting_id,
        "elements": whiteboard.get("elements", []),
        "width": whiteboard.get("width", 1920),
        "height": whiteboard.get("height", 1080),
        "background": whiteboard.get("background", "white")
    }


# ============ FILE SHARING ============

async def share_file(
    meeting_id: str,
    user_id: str,
    user_name: str,
    file_name: str,
    file_type: str,
    file_size: int,
    file_data: str = None,  # Base64 encoded for small files
    file_url: str = None    # URL for larger files
) -> Dict:
    """Share a file in the meeting"""
    
    file_id = str(uuid.uuid4())[:12]
    
    shared_file = {
        "file_id": file_id,
        "meeting_id": meeting_id,
        "uploaded_by": user_id,
        "uploaded_by_name": user_name,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "file_data": file_data,
        "file_url": file_url,
        "uploaded_at": datetime.utcnow().isoformat(),
        "downloads": 0,
        "is_pinned": False
    }
    
    await shared_files.insert_one({**shared_file, "_id": file_id})
    
    logger.info(f"File '{file_name}' shared in meeting {meeting_id}")
    
    return {
        "file_id": file_id,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": file_size,
        "uploaded_by_name": user_name,
        "uploaded_at": shared_file["uploaded_at"]
    }


async def get_shared_files(meeting_id: str) -> List[Dict]:
    """Get all files shared in a meeting"""
    
    files = await shared_files.find(
        {"meeting_id": meeting_id},
        {"_id": 0, "file_data": 0}  # Exclude file data for listing
    ).sort("uploaded_at", -1).to_list(length=100)
    
    return files


async def get_file(file_id: str) -> Optional[Dict]:
    """Get a specific shared file"""
    
    file = await shared_files.find_one(
        {"file_id": file_id},
        {"_id": 0}
    )
    
    if file:
        # Increment download count
        await shared_files.update_one(
            {"file_id": file_id},
            {"$inc": {"downloads": 1}}
        )
    
    return file


async def delete_shared_file(file_id: str, user_id: str) -> bool:
    """Delete a shared file (only uploader can delete)"""
    
    result = await shared_files.delete_one({
        "file_id": file_id,
        "uploaded_by": user_id
    })
    
    return result.deleted_count > 0


async def pin_file(file_id: str, is_pinned: bool) -> bool:
    """Pin/unpin a file"""
    
    result = await shared_files.update_one(
        {"file_id": file_id},
        {"$set": {"is_pinned": is_pinned}}
    )
    
    return result.modified_count > 0


# ============ ACTION ITEMS ============

async def create_action_item(
    meeting_id: str,
    title: str,
    description: str = "",
    assigned_to: str = None,
    assigned_to_name: str = None,
    due_date: str = None,
    priority: str = "medium",
    created_by: str = None,
    source: str = "manual"  # manual, ai_generated
) -> Dict:
    """Create an action item from a meeting"""
    
    item_id = str(uuid.uuid4())[:8]
    
    action_item = {
        "item_id": item_id,
        "meeting_id": meeting_id,
        "title": title,
        "description": description,
        "assigned_to": assigned_to,
        "assigned_to_name": assigned_to_name,
        "due_date": due_date,
        "priority": priority,  # low, medium, high, urgent
        "status": "pending",   # pending, in_progress, completed, cancelled
        "created_by": created_by,
        "source": source,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "notes": []
    }
    
    await action_items.insert_one({**action_item, "_id": item_id})
    
    logger.info(f"Action item '{title}' created for meeting {meeting_id}")
    
    return action_item


async def get_action_items(
    meeting_id: str = None,
    user_id: str = None,
    status: str = None
) -> List[Dict]:
    """Get action items"""
    
    query = {}
    
    if meeting_id:
        query["meeting_id"] = meeting_id
    
    if user_id:
        query["$or"] = [
            {"assigned_to": user_id},
            {"created_by": user_id}
        ]
    
    if status:
        query["status"] = status
    
    items = await action_items.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).to_list(length=100)
    
    return items


async def update_action_item(
    item_id: str,
    updates: Dict
) -> Dict:
    """Update an action item"""
    
    allowed_updates = [
        "title", "description", "assigned_to", "assigned_to_name",
        "due_date", "priority", "status"
    ]
    
    update_data = {k: v for k, v in updates.items() if k in allowed_updates}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    if updates.get("status") == "completed":
        update_data["completed_at"] = datetime.utcnow().isoformat()
    
    await action_items.update_one(
        {"item_id": item_id},
        {"$set": update_data}
    )
    
    return {"success": True, "item_id": item_id}


async def add_action_item_note(
    item_id: str,
    note: str,
    user_id: str,
    user_name: str
) -> Dict:
    """Add a note to an action item"""
    
    note_data = {
        "note_id": str(uuid.uuid4())[:6],
        "note": note,
        "user_id": user_id,
        "user_name": user_name,
        "created_at": datetime.utcnow().isoformat()
    }
    
    await action_items.update_one(
        {"item_id": item_id},
        {
            "$push": {"notes": note_data},
            "$set": {"updated_at": datetime.utcnow().isoformat()}
        }
    )
    
    return note_data


async def delete_action_item(item_id: str) -> bool:
    """Delete an action item"""
    
    result = await action_items.delete_one({"item_id": item_id})
    return result.deleted_count > 0


async def extract_action_items_from_transcript(
    meeting_id: str,
    transcript: str,
    participants: List[str]
) -> List[Dict]:
    """
    AI-powered extraction of action items from meeting transcript.
    In production, this would use an LLM to extract action items.
    """
    
    # Placeholder for AI extraction
    # Keywords that might indicate action items
    action_keywords = [
        "will do", "need to", "should", "must", "action item",
        "follow up", "by next", "deadline", "assigned to",
        "take care of", "responsible for", "complete by"
    ]
    
    extracted_items = []
    
    # Simple keyword-based extraction (replace with LLM in production)
    sentences = transcript.split('.')
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(keyword in sentence_lower for keyword in action_keywords):
            # Create action item
            item = await create_action_item(
                meeting_id=meeting_id,
                title=sentence.strip()[:100],
                description=sentence.strip(),
                source="ai_generated"
            )
            extracted_items.append(item)
    
    return extracted_items
