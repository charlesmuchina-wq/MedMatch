"""
Hardware Discovery Dashboard API
Auto-detect connected devices, manage device registry, toggle live/simulation modes.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/hardware", tags=["Hardware Discovery"])

DEVICE_TYPES = ["camera_360", "mic_array", "iot_hub", "xr_headset", "display", "speaker_array"]


class DeviceRegister(BaseModel):
    device_id: str
    device_type: str  # camera_360, mic_array, iot_hub, xr_headset, display, speaker_array
    name: str
    manufacturer: Optional[str] = ""
    model: Optional[str] = ""
    firmware: Optional[str] = ""
    connection_type: str = "usb"  # usb, bluetooth, wifi, ethernet
    capabilities: List[str] = []


class DeviceStatusUpdate(BaseModel):
    device_id: str
    status: str = "online"  # online, offline, error, standby
    battery_percent: Optional[float] = None
    signal_strength: Optional[float] = None
    mode: str = "live"  # live, simulation


@router.post("/{meeting_id}/register")
async def register_device(meeting_id: str, data: DeviceRegister, user=Depends(require_auth)):
    """Register a discovered hardware device for a meeting room."""
    if data.device_type not in DEVICE_TYPES:
        raise HTTPException(400, f"Invalid device type. Valid: {DEVICE_TYPES}")

    now = datetime.now(timezone.utc).isoformat()
    doc = {
        "meeting_id": meeting_id,
        "device_id": data.device_id,
        "device_type": data.device_type,
        "name": data.name,
        "manufacturer": data.manufacturer,
        "model": data.model,
        "firmware": data.firmware,
        "connection_type": data.connection_type,
        "capabilities": data.capabilities,
        "status": "online",
        "mode": "live",
        "registered_by": user["user_id"],
        "registered_at": now,
        "last_seen": now
    }

    await db.hardware_devices.update_one(
        {"meeting_id": meeting_id, "device_id": data.device_id},
        {"$set": doc},
        upsert=True
    )

    return {"success": True, "device_id": data.device_id, "status": "registered"}


@router.get("/{meeting_id}/devices")
async def list_devices(meeting_id: str, user=Depends(require_auth)):
    """List all registered hardware devices for a meeting room."""
    devices = await db.hardware_devices.find(
        {"meeting_id": meeting_id}, {"_id": 0}
    ).to_list(50)

    if not devices:
        devices = _get_simulated_devices(meeting_id)

    # Group by type
    by_type = {}
    for d in devices:
        t = d.get("device_type", "unknown")
        by_type.setdefault(t, []).append(d)

    online = sum(1 for d in devices if d.get("status") == "online")
    live = sum(1 for d in devices if d.get("mode") == "live")

    return {
        "meeting_id": meeting_id,
        "devices": devices,
        "by_type": by_type,
        "total": len(devices),
        "online": online,
        "live_mode": live,
        "simulation_mode": len(devices) - live
    }


@router.post("/{meeting_id}/status")
async def update_device_status(meeting_id: str, data: DeviceStatusUpdate, user=Depends(require_auth)):
    """Update device status (online/offline) and mode (live/simulation)."""
    result = await db.hardware_devices.update_one(
        {"meeting_id": meeting_id, "device_id": data.device_id},
        {"$set": {
            "status": data.status,
            "mode": data.mode,
            "battery_percent": data.battery_percent,
            "signal_strength": data.signal_strength,
            "last_seen": datetime.now(timezone.utc).isoformat()
        }}
    )

    return {"success": True, "device_id": data.device_id, "status": data.status, "mode": data.mode}


@router.post("/{meeting_id}/scan")
async def scan_for_devices(meeting_id: str, user=Depends(require_auth)):
    """Trigger a hardware scan (simulates discovering nearby devices)."""
    discovered = _get_simulated_devices(meeting_id)

    for d in discovered:
        await db.hardware_devices.update_one(
            {"meeting_id": meeting_id, "device_id": d["device_id"]},
            {"$set": d},
            upsert=True
        )

    return {
        "scan_complete": True,
        "discovered": len(discovered),
        "devices": discovered
    }


@router.delete("/{meeting_id}/{device_id}")
async def remove_device(meeting_id: str, device_id: str, user=Depends(require_auth)):
    """Remove a device from the registry."""
    await db.hardware_devices.delete_one({"meeting_id": meeting_id, "device_id": device_id})
    return {"success": True, "removed": device_id}


def _get_simulated_devices(meeting_id: str) -> list:
    """Return realistic simulated device discovery results."""
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "meeting_id": meeting_id, "device_id": "owl-360-001",
            "device_type": "camera_360", "name": "Meeting Owl 3",
            "manufacturer": "Owl Labs", "model": "MTW300", "firmware": "v5.4.2",
            "connection_type": "usb", "status": "online", "mode": "simulation",
            "capabilities": ["360_video", "auto_focus", "speaker_tracking", "1080p"],
            "battery_percent": None, "signal_strength": None, "last_seen": now
        },
        {
            "meeting_id": meeting_id, "device_id": "mic-array-001",
            "device_type": "mic_array", "name": "Shure MXA920",
            "manufacturer": "Shure", "model": "MXA920-C", "firmware": "v3.1.0",
            "connection_type": "ethernet", "status": "online", "mode": "simulation",
            "capabilities": ["beamforming", "8_channels", "aec", "noise_reduction"],
            "battery_percent": None, "signal_strength": 0.95, "last_seen": now
        },
        {
            "meeting_id": meeting_id, "device_id": "iot-hub-001",
            "device_type": "iot_hub", "name": "Crestron CP4-R",
            "manufacturer": "Crestron", "model": "CP4-R", "firmware": "v2.8.1",
            "connection_type": "ethernet", "status": "online", "mode": "simulation",
            "capabilities": ["lighting", "shades", "hvac", "display_control", "scheduling"],
            "battery_percent": None, "signal_strength": None, "last_seen": now
        },
        {
            "meeting_id": meeting_id, "device_id": "xr-vp-001",
            "device_type": "xr_headset", "name": "Apple Vision Pro",
            "manufacturer": "Apple", "model": "A2117", "firmware": "visionOS 2.2",
            "connection_type": "wifi", "status": "standby", "mode": "simulation",
            "capabilities": ["spatial_video", "hand_tracking", "eye_tracking", "spatial_audio", "passthrough"],
            "battery_percent": 78, "signal_strength": 0.88, "last_seen": now
        },
        {
            "meeting_id": meeting_id, "device_id": "display-001",
            "device_type": "display", "name": "Samsung Flip Pro 85",
            "manufacturer": "Samsung", "model": "WM85B", "firmware": "v1.5.3",
            "connection_type": "wifi", "status": "online", "mode": "simulation",
            "capabilities": ["4k", "touch", "whiteboard", "wireless_share", "split_screen"],
            "battery_percent": None, "signal_strength": 0.92, "last_seen": now
        },
        {
            "meeting_id": meeting_id, "device_id": "speaker-001",
            "device_type": "speaker_array", "name": "Bose ES1 Ceiling",
            "manufacturer": "Bose", "model": "ES1", "firmware": "v4.0.1",
            "connection_type": "ethernet", "status": "online", "mode": "simulation",
            "capabilities": ["spatial_audio", "zone_control", "auto_level", "dante"],
            "battery_percent": None, "signal_strength": None, "last_seen": now
        }
    ]
