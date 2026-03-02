"""
SLAM-Based Spatial Awareness & 360° Multi-Focus Framing API
Software layer for hardware integration with realistic simulation data.
- SLAM: 3D room mapping, user position tracking, auto-framing adjustments
- 360°: Panoramic feed processing, individual headshot extraction, ROI detection
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import random
import math
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/spatial", tags=["SLAM & 360 Framing"])


# ========== SLAM Spatial Awareness ==========

class SpatialPosition(BaseModel):
    user_id: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0  # depth from camera
    yaw: float = 0.0  # head rotation
    pitch: float = 0.0
    face_confidence: float = 0.95


class RoomMapUpdate(BaseModel):
    meeting_id: str
    room_dimensions: Optional[dict] = None  # {"width": 5.0, "depth": 4.0, "height": 2.8}
    positions: List[SpatialPosition] = []
    lighting_quality: float = 0.8  # 0-1


class FrameAdjustment(BaseModel):
    user_id: str
    crop_x: float = 0.0
    crop_y: float = 0.0
    crop_width: float = 1.0
    crop_height: float = 1.0
    brightness_adjust: float = 0.0
    contrast_adjust: float = 0.0


@router.post("/{meeting_id}/room-map")
async def update_room_map(meeting_id: str, data: RoomMapUpdate, user=Depends(require_auth)):
    """Update the SLAM-derived 3D room map with user positions."""
    now = datetime.now(timezone.utc).isoformat()

    positions_data = []
    for p in data.positions:
        positions_data.append({
            "user_id": p.user_id,
            "x": p.x, "y": p.y, "z": p.z,
            "yaw": p.yaw, "pitch": p.pitch,
            "face_confidence": p.face_confidence
        })

    await db.slam_room_maps.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "meeting_id": meeting_id,
            "room_dimensions": data.room_dimensions or {"width": 5.0, "depth": 4.0, "height": 2.8},
            "positions": positions_data,
            "lighting_quality": data.lighting_quality,
            "updated_at": now,
            "updated_by": user["user_id"]
        }},
        upsert=True
    )

    # Generate auto-framing adjustments based on positions
    adjustments = []
    for p in data.positions:
        adj = _calculate_frame_adjustment(p)
        adjustments.append(adj)

    return {
        "success": True,
        "room_map_updated": True,
        "frame_adjustments": adjustments,
        "tracking_points": len(positions_data)
    }


@router.get("/{meeting_id}/room-map")
async def get_room_map(meeting_id: str, user=Depends(require_auth)):
    """Get the current SLAM room map for a meeting."""
    room = await db.slam_room_maps.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not room:
        # Return realistic simulation data
        return _generate_simulated_room_map(meeting_id)
    return room


@router.get("/{meeting_id}/tracking")
async def get_spatial_tracking(meeting_id: str, user=Depends(require_auth)):
    """Get real-time spatial tracking data with frame adjustments."""
    room = await db.slam_room_maps.find_one({"meeting_id": meeting_id}, {"_id": 0})

    if room and room.get("positions"):
        positions = room["positions"]
    else:
        # Simulate realistic tracking data
        positions = _generate_simulated_positions(meeting_id)

    adjustments = [_calculate_frame_adjustment(SpatialPosition(**p)) for p in positions]
    lighting = room.get("lighting_quality", 0.78) if room else 0.78

    return {
        "meeting_id": meeting_id,
        "positions": positions,
        "frame_adjustments": adjustments,
        "room_lighting": {
            "quality": lighting,
            "recommendation": "optimal" if lighting > 0.7 else "increase_lighting",
            "auto_enhance": lighting < 0.6
        },
        "slam_status": "active",
        "tracking_fps": 30,
        "depth_accuracy_mm": 12
    }


# ========== 360° Multi-Focus Framing ==========

class PanoramicFeed(BaseModel):
    meeting_id: str
    feed_width: int = 3840  # 4K panoramic
    feed_height: int = 1080
    detected_faces: List[dict] = []  # [{"user_id": "x", "bbox": [x,y,w,h]}]


@router.post("/{meeting_id}/panoramic/process")
async def process_panoramic_feed(meeting_id: str, data: PanoramicFeed, user=Depends(require_auth)):
    """Process a 360° panoramic feed and extract individual headshot regions."""
    headshots = []

    if data.detected_faces:
        for face in data.detected_faces:
            bbox = face.get("bbox", [0, 0, 200, 200])
            headshots.append({
                "user_id": face.get("user_id", "unknown"),
                "crop_region": {
                    "x": max(0, bbox[0] - 40),
                    "y": max(0, bbox[1] - 60),
                    "width": bbox[2] + 80,
                    "height": bbox[3] + 100
                },
                "quality_score": round(random.uniform(0.85, 0.98), 2),
                "gaze_direction": round(random.uniform(-15, 15), 1),
                "is_speaking": random.random() > 0.7
            })
    else:
        # Simulate detected faces in a boardroom
        headshots = _generate_simulated_headshots(data.feed_width, data.feed_height)

    await db.panoramic_frames.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "meeting_id": meeting_id,
            "feed_dimensions": {"width": data.feed_width, "height": data.feed_height},
            "headshots": headshots,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }},
        upsert=True
    )

    return {
        "meeting_id": meeting_id,
        "headshots_extracted": len(headshots),
        "headshots": headshots,
        "panoramic_status": "processing",
        "camera_type": "360_owl"
    }


@router.get("/{meeting_id}/panoramic/headshots")
async def get_panoramic_headshots(meeting_id: str, user=Depends(require_auth)):
    """Get the latest extracted headshots from a 360° feed."""
    frame = await db.panoramic_frames.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not frame:
        return {
            "meeting_id": meeting_id,
            "headshots": _generate_simulated_headshots(3840, 1080),
            "panoramic_status": "simulated",
            "camera_connected": False
        }
    return {
        "meeting_id": meeting_id,
        "headshots": frame.get("headshots", []),
        "panoramic_status": "active",
        "camera_connected": True
    }


def _calculate_frame_adjustment(pos: SpatialPosition) -> dict:
    """Calculate optimal frame crop based on spatial position."""
    # Simulate intelligent auto-framing
    center_offset_x = pos.x * 0.05  # Horizontal shift
    center_offset_y = pos.y * 0.05  # Vertical shift
    depth_zoom = max(0.6, min(1.0, 1.0 - (pos.z * 0.1)))  # Zoom based on depth

    brightness = max(-0.3, min(0.3, -pos.z * 0.05))
    contrast = 0.05 if pos.face_confidence > 0.9 else 0.1

    return {
        "user_id": pos.user_id,
        "crop_x": round(0.5 + center_offset_x - depth_zoom / 2, 3),
        "crop_y": round(0.5 + center_offset_y - depth_zoom / 2, 3),
        "crop_width": round(depth_zoom, 3),
        "crop_height": round(depth_zoom, 3),
        "brightness_adjust": round(brightness, 3),
        "contrast_adjust": round(contrast, 3),
        "auto_framing_active": True
    }


def _generate_simulated_room_map(meeting_id: str) -> dict:
    """Generate realistic SLAM room map simulation."""
    return {
        "meeting_id": meeting_id,
        "room_dimensions": {"width": 6.2, "depth": 4.8, "height": 2.9},
        "positions": _generate_simulated_positions(meeting_id),
        "lighting_quality": 0.78,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "slam_status": "simulated"
    }


def _generate_simulated_positions(meeting_id: str) -> list:
    """Generate realistic user positions around a conference table."""
    names = ["Alex Chen", "Sarah Miller", "James Park", "Maria Garcia", "David Kim", "Emma Wilson"]
    positions = []
    table_radius = 1.8

    for i, name in enumerate(names):
        angle = (2 * math.pi * i) / len(names)
        positions.append({
            "user_id": f"user_{i+1}",
            "user_name": name,
            "x": round(table_radius * math.cos(angle), 2),
            "y": round(0.1 * random.uniform(-1, 1), 2),
            "z": round(table_radius * math.sin(angle) + 2.5, 2),
            "yaw": round(math.degrees(angle + math.pi) % 360, 1),
            "pitch": round(random.uniform(-5, 5), 1),
            "face_confidence": round(random.uniform(0.88, 0.99), 2),
            "is_remote": i >= 3
        })
    return positions


def _generate_simulated_headshots(width: int, height: int) -> list:
    """Generate realistic headshot regions from a simulated panoramic feed."""
    names = ["Alex Chen", "Sarah Miller", "James Park", "Maria Garcia", "David Kim", "Emma Wilson"]
    headshots = []
    spacing = width // (len(names) + 1)

    for i, name in enumerate(names):
        cx = spacing * (i + 1)
        face_w = int(width * 0.08)
        face_h = int(height * 0.45)

        headshots.append({
            "user_id": f"user_{i+1}",
            "user_name": name,
            "crop_region": {
                "x": cx - face_w,
                "y": int(height * 0.15),
                "width": face_w * 2,
                "height": face_h
            },
            "quality_score": round(random.uniform(0.85, 0.98), 2),
            "gaze_direction": round(random.uniform(-15, 15), 1),
            "is_speaking": i == 2,
            "seat_position": i + 1
        })
    return headshots
