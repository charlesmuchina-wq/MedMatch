"""
IoT Room Environmental Control API
Voice-activated control panel for room devices (lights, temperature, shades, displays).
REST API layer ready for actual IoT hardware integration.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/iot", tags=["IoT Room Control"])


class DeviceState(BaseModel):
    device_type: str  # lights, temperature, shades, display, speaker_volume
    value: float  # 0-100 for most, temperature in celsius
    zone: str = "main"  # main, presentation, ambient


class RoomPreset(BaseModel):
    name: str  # presentation, discussion, break, focus
    devices: List[DeviceState] = []


class VoiceControlCommand(BaseModel):
    command: str  # natural language command
    meeting_id: str


PRESETS = {
    "presentation": {
        "lights_main": 30, "lights_presentation": 80, "lights_ambient": 15,
        "shades": 90, "display_brightness": 85, "temperature": 22, "speaker_volume": 70
    },
    "discussion": {
        "lights_main": 70, "lights_presentation": 40, "lights_ambient": 50,
        "shades": 50, "display_brightness": 60, "temperature": 22, "speaker_volume": 55
    },
    "break": {
        "lights_main": 80, "lights_presentation": 20, "lights_ambient": 60,
        "shades": 30, "display_brightness": 30, "temperature": 23, "speaker_volume": 40
    },
    "focus": {
        "lights_main": 50, "lights_presentation": 60, "lights_ambient": 30,
        "shades": 80, "display_brightness": 70, "temperature": 21, "speaker_volume": 50
    }
}


@router.get("/{meeting_id}/state")
async def get_room_state(meeting_id: str, user=Depends(require_auth)):
    """Get current state of all IoT devices in the meeting room."""
    state = await db.iot_room_states.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not state:
        state = _get_default_room_state(meeting_id)
    return state


@router.post("/{meeting_id}/device")
async def control_device(meeting_id: str, data: DeviceState, user=Depends(require_auth)):
    """Control a specific IoT device in the room."""
    key = f"{data.device_type}_{data.zone}"
    now = datetime.now(timezone.utc).isoformat()

    await db.iot_room_states.update_one(
        {"meeting_id": meeting_id},
        {
            "$set": {
                f"devices.{key}": {
                    "type": data.device_type,
                    "zone": data.zone,
                    "value": data.value,
                    "updated_at": now,
                    "updated_by": user["user_id"]
                },
                "updated_at": now
            },
            "$setOnInsert": {"meeting_id": meeting_id, "created_at": now}
        },
        upsert=True
    )

    # Log the change
    await db.iot_control_log.insert_one({
        "meeting_id": meeting_id,
        "device": key,
        "value": data.value,
        "changed_by": user["user_id"],
        "timestamp": now
    })

    return {
        "success": True,
        "device": key,
        "value": data.value,
        "status": "applied"
    }


@router.post("/{meeting_id}/preset")
async def apply_preset(meeting_id: str, preset_name: str, user=Depends(require_auth)):
    """Apply a room preset (presentation, discussion, break, focus)."""
    if preset_name not in PRESETS:
        raise HTTPException(400, f"Invalid preset. Available: {list(PRESETS.keys())}")

    preset = PRESETS[preset_name]
    now = datetime.now(timezone.utc).isoformat()
    devices = {}

    for key, value in preset.items():
        parts = key.rsplit("_", 1)
        device_type = parts[0] if len(parts) == 2 else key
        zone = parts[1] if len(parts) == 2 else "main"
        devices[key] = {
            "type": device_type,
            "zone": zone,
            "value": value,
            "updated_at": now,
            "updated_by": user["user_id"]
        }

    await db.iot_room_states.update_one(
        {"meeting_id": meeting_id},
        {"$set": {
            "meeting_id": meeting_id,
            "devices": devices,
            "active_preset": preset_name,
            "updated_at": now
        }},
        upsert=True
    )

    return {
        "success": True,
        "preset": preset_name,
        "devices_updated": len(devices),
        "status": "applied"
    }


@router.post("/{meeting_id}/voice-control")
async def voice_room_control(meeting_id: str, data: VoiceControlCommand, user=Depends(require_auth)):
    """Parse a natural language command and control room devices."""
    cmd = data.command.lower().strip()

    actions = []

    # Parse lighting commands
    if "lights" in cmd or "light" in cmd or "dim" in cmd or "bright" in cmd:
        if "off" in cmd or "dim" in cmd:
            actions.append({"device": "lights_main", "value": 10, "label": "Lights dimmed"})
        elif "up" in cmd or "bright" in cmd or "on" in cmd:
            actions.append({"device": "lights_main", "value": 80, "label": "Lights brightened"})
        elif "half" in cmd or "50" in cmd:
            actions.append({"device": "lights_main", "value": 50, "label": "Lights set to 50%"})

    # Parse temperature commands
    if "temperature" in cmd or "temp" in cmd or "warm" in cmd or "cool" in cmd or "cold" in cmd:
        if "warm" in cmd or "up" in cmd:
            actions.append({"device": "temperature_main", "value": 24, "label": "Temperature raised to 24C"})
        elif "cool" in cmd or "cold" in cmd or "down" in cmd:
            actions.append({"device": "temperature_main", "value": 20, "label": "Temperature lowered to 20C"})

    # Parse shades/blinds commands
    if "shade" in cmd or "blind" in cmd or "curtain" in cmd:
        if "open" in cmd or "up" in cmd:
            actions.append({"device": "shades_main", "value": 10, "label": "Shades opened"})
        elif "close" in cmd or "down" in cmd:
            actions.append({"device": "shades_main", "value": 95, "label": "Shades closed"})

    # Parse display commands
    if "display" in cmd or "screen" in cmd or "projector" in cmd:
        if "off" in cmd:
            actions.append({"device": "display_main", "value": 0, "label": "Display turned off"})
        elif "on" in cmd:
            actions.append({"device": "display_main", "value": 80, "label": "Display turned on"})

    # Parse volume commands
    if "volume" in cmd or "speaker" in cmd or "loud" in cmd or "quiet" in cmd:
        if "up" in cmd or "loud" in cmd:
            actions.append({"device": "speaker_volume_main", "value": 80, "label": "Volume increased"})
        elif "down" in cmd or "quiet" in cmd or "mute" in cmd:
            actions.append({"device": "speaker_volume_main", "value": 15, "label": "Volume decreased"})

    # Parse presets
    for preset_name in PRESETS:
        if preset_name in cmd:
            actions.append({"device": "preset", "value": preset_name, "label": f"{preset_name.title()} mode activated"})

    # Apply actions
    now = datetime.now(timezone.utc).isoformat()
    for action in actions:
        if action["device"] == "preset":
            continue  # Handled separately
        await db.iot_room_states.update_one(
            {"meeting_id": meeting_id},
            {"$set": {
                f"devices.{action['device']}": {
                    "value": action["value"],
                    "updated_at": now,
                    "updated_by": user["user_id"]
                }
            }},
            upsert=True
        )

    return {
        "command": data.command,
        "actions_taken": len(actions),
        "actions": actions,
        "unrecognized": len(actions) == 0,
        "suggestion": "Try: 'dim the lights', 'raise temperature', 'close shades', 'presentation mode'" if not actions else None
    }


@router.get("/{meeting_id}/log")
async def get_control_log(meeting_id: str, user=Depends(require_auth)):
    """Get recent IoT control log for the meeting room."""
    logs = await db.iot_control_log.find(
        {"meeting_id": meeting_id}, {"_id": 0}
    ).sort("timestamp", -1).to_list(20)
    return {"logs": logs}


def _get_default_room_state(meeting_id: str) -> dict:
    """Return a realistic default room state."""
    return {
        "meeting_id": meeting_id,
        "devices": {
            "lights_main": {"type": "lights", "zone": "main", "value": 65},
            "lights_presentation": {"type": "lights", "zone": "presentation", "value": 40},
            "lights_ambient": {"type": "lights", "zone": "ambient", "value": 35},
            "temperature_main": {"type": "temperature", "zone": "main", "value": 22},
            "shades_main": {"type": "shades", "zone": "main", "value": 50},
            "display_main": {"type": "display", "zone": "main", "value": 75},
            "speaker_volume_main": {"type": "speaker_volume", "zone": "main", "value": 55}
        },
        "active_preset": None,
        "hub_connected": True,
        "hub_type": "AI KARAU IoT Bridge",
        "status": "simulated"
    }
