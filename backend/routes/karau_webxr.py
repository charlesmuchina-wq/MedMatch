"""
Apple Vision Pro / WebXR Spatial Meeting API
Software layer for spatial computing headset integration.
Manages 3D meeting room state, spatial persona placement, and XR session data.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import math
import random
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/webxr", tags=["WebXR Spatial Meetings"])


class SpatialPersona(BaseModel):
    user_id: str
    user_name: str
    position: dict = {"x": 0.0, "y": 0.0, "z": -2.0}
    rotation: dict = {"x": 0.0, "y": 0.0, "z": 0.0}
    scale: float = 1.0
    avatar_type: str = "video_feed"
    headset_type: Optional[str] = None


class RoomEnvironment(BaseModel):
    room_type: str = "boardroom"
    capacity: int = 12
    ambient_lighting: float = 0.7
    skybox: str = "corporate_day"


class XRSessionCreate(BaseModel):
    meeting_id: str
    room_environment: Optional[RoomEnvironment] = None
    enable_hand_tracking: bool = True
    enable_eye_tracking: bool = True
    spatial_audio: bool = True


@router.post("/{meeting_id}/session")
async def create_xr_session(meeting_id: str, data: XRSessionCreate, user=Depends(require_auth)):
    """Create or join a WebXR spatial meeting session."""
    room = data.room_environment or RoomEnvironment()
    seats = _generate_room_layout(room.room_type, room.capacity)

    session_doc = {
        "meeting_id": meeting_id,
        "room_environment": {
            "type": room.room_type,
            "capacity": room.capacity,
            "ambient_lighting": room.ambient_lighting,
            "skybox": room.skybox,
            "dimensions": _get_room_dimensions(room.room_type)
        },
        "seats": seats,
        "personas": [],
        "features": {
            "hand_tracking": data.enable_hand_tracking,
            "eye_tracking": data.enable_eye_tracking,
            "spatial_audio": data.spatial_audio,
            "shared_objects": True
        },
        "created_by": user["user_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "active"
    }

    await db.xr_sessions.update_one(
        {"meeting_id": meeting_id}, {"$set": session_doc}, upsert=True
    )

    return {
        "session_id": meeting_id,
        "room_environment": session_doc["room_environment"],
        "seats": seats,
        "features": session_doc["features"],
        "xr_capabilities": {
            "webxr_supported": True, "immersive_vr": True,
            "immersive_ar": True, "hand_tracking": True, "depth_sensing": True
        }
    }


@router.get("/{meeting_id}/session")
async def get_xr_session(meeting_id: str, user=Depends(require_auth)):
    """Get the current XR session state."""
    session = await db.xr_sessions.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not session:
        return _generate_simulated_session(meeting_id)
    return session


@router.post("/{meeting_id}/persona")
async def update_persona(meeting_id: str, data: SpatialPersona, user=Depends(require_auth)):
    """Update a participant's spatial persona position."""
    persona_data = {
        "user_id": data.user_id, "user_name": data.user_name,
        "position": data.position, "rotation": data.rotation,
        "scale": data.scale, "avatar_type": data.avatar_type,
        "headset_type": data.headset_type or "web_browser",
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.xr_sessions.update_one(
        {"meeting_id": meeting_id, "personas.user_id": data.user_id},
        {"$set": {"personas.$": persona_data}}
    )
    await db.xr_sessions.update_one(
        {"meeting_id": meeting_id, "personas.user_id": {"$ne": data.user_id}},
        {"$push": {"personas": persona_data}}
    )

    return {"success": True, "persona": persona_data}


@router.get("/{meeting_id}/personas")
async def get_all_personas(meeting_id: str, user=Depends(require_auth)):
    """Get all spatial personas in the meeting."""
    session = await db.xr_sessions.find_one({"meeting_id": meeting_id}, {"_id": 0, "personas": 1})
    personas = session.get("personas", []) if session else []
    if not personas:
        personas = _generate_simulated_personas()
    return {"meeting_id": meeting_id, "personas": personas, "count": len(personas)}


@router.get("/{meeting_id}/room-layout")
async def get_room_layout(meeting_id: str):
    """Get the 3D room layout for rendering."""
    session = await db.xr_sessions.find_one(
        {"meeting_id": meeting_id}, {"_id": 0, "room_environment": 1, "seats": 1}
    )
    room_type = session.get("room_environment", {}).get("type", "boardroom") if session else "boardroom"
    return {
        "room_type": room_type,
        "dimensions": _get_room_dimensions(room_type),
        "seats": session.get("seats", _generate_room_layout(room_type, 12)) if session else _generate_room_layout(room_type, 12),
        "objects": _get_room_objects(room_type),
        "lighting": {"ambient": 0.7, "directional": 0.5, "color": "#fff5e6"}
    }


def _get_room_dimensions(room_type):
    dims = {
        "boardroom": {"width": 8, "depth": 6, "height": 3.2},
        "amphitheater": {"width": 12, "depth": 10, "height": 5},
        "lounge": {"width": 10, "depth": 8, "height": 3},
        "open_space": {"width": 15, "depth": 15, "height": 4},
    }
    return dims.get(room_type, dims["boardroom"])


def _generate_room_layout(room_type, capacity):
    seats = []
    rx, rz = 2.5, 1.5
    for i in range(capacity):
        angle = (2 * math.pi * i) / capacity
        seats.append({
            "seat_id": i + 1,
            "position": {"x": round(rx * math.cos(angle), 2), "y": 0, "z": round(rz * math.sin(angle), 2)},
            "rotation": {"y": round(math.degrees(angle + math.pi) % 360, 1)},
            "occupied": False
        })
    return seats


def _get_room_objects(room_type):
    if room_type == "boardroom":
        return [
            {"type": "table", "model": "oval_table", "position": {"x": 0, "y": 0, "z": 0}},
            {"type": "screen", "model": "presentation_screen", "position": {"x": 0, "y": 1.5, "z": -3}},
        ]
    return [{"type": "floor", "model": "open_floor", "position": {"x": 0, "y": 0, "z": 0}}]


def _generate_simulated_session(meeting_id):
    return {
        "meeting_id": meeting_id,
        "room_environment": {"type": "boardroom", "capacity": 12, "ambient_lighting": 0.7,
                             "skybox": "corporate_day", "dimensions": _get_room_dimensions("boardroom")},
        "seats": _generate_room_layout("boardroom", 12),
        "personas": _generate_simulated_personas(),
        "features": {"hand_tracking": True, "eye_tracking": True, "spatial_audio": True, "shared_objects": True},
        "status": "simulated"
    }


def _generate_simulated_personas():
    names = [("Alex Chen", "vision_pro"), ("Sarah Miller", "web_browser"),
             ("James Park", "quest_3"), ("Maria Garcia", "web_browser"),
             ("David Kim", "vision_pro"), ("Emma Wilson", "web_browser")]
    personas = []
    for i, (name, headset) in enumerate(names):
        angle = (2 * math.pi * i) / len(names)
        personas.append({
            "user_id": f"user_{i+1}", "user_name": name,
            "position": {"x": round(2.5 * math.cos(angle), 2), "y": 0, "z": round(1.5 * math.sin(angle), 2)},
            "rotation": {"x": 0, "y": round(math.degrees(angle + math.pi) % 360, 1), "z": 0},
            "scale": 1.0,
            "avatar_type": "spatial_persona" if headset == "vision_pro" else "video_feed",
            "headset_type": headset, "is_speaking": i == 2
        })
    return personas
