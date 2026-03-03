"""
Real-time Hardware Simulation Streams
Provides time-varying data for SLAM, 360 Camera, Beamforming, IoT, and Biometric modules.
Each endpoint returns data that naturally varies with time to simulate live hardware.
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
import math
import time
import random
import logging

from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/simulation", tags=["Hardware Simulation Streams"])

SPEAKERS = [
    {"id": "user_1", "name": "Alex Chen", "role": "Host", "color": "#f43f5e"},
    {"id": "user_2", "name": "Sarah Miller", "role": "CTO", "color": "#3b82f6"},
    {"id": "user_3", "name": "James Park", "role": "Designer", "color": "#f59e0b"},
    {"id": "user_4", "name": "Maria Garcia", "role": "PM", "color": "#10b981"},
    {"id": "user_5", "name": "David Kim", "role": "Engineer", "color": "#8b5cf6"},
    {"id": "user_6", "name": "Emma Wilson", "role": "Analyst", "color": "#ec4899"},
]


def _t():
    return time.time()


@router.get("/{meeting_id}/slam-stream")
async def slam_stream(meeting_id: str, user=Depends(require_auth)):
    """Real-time SLAM position stream with micro-drift."""
    t = _t()
    table_radius = 1.8
    positions = []
    active_speaker_idx = int(t / 8) % len(SPEAKERS)

    for i, sp in enumerate(SPEAKERS):
        base_angle = (2 * math.pi * i) / len(SPEAKERS)
        drift_x = 0.08 * math.sin(t * 0.3 + i * 1.7)
        drift_z = 0.06 * math.cos(t * 0.25 + i * 2.1)
        head_turn = 15 * math.sin(t * 0.4 + i * 1.3)
        is_speaking = i == active_speaker_idx
        lean = 0.15 if is_speaking else 0

        positions.append({
            "user_id": sp["id"],
            "user_name": sp["name"],
            "x": round(table_radius * math.cos(base_angle) + drift_x + lean * math.cos(base_angle), 3),
            "y": round(0.02 * math.sin(t * 0.5 + i), 3),
            "z": round(table_radius * math.sin(base_angle) + 2.5 + drift_z, 3),
            "yaw": round((math.degrees(base_angle + math.pi) + head_turn) % 360, 1),
            "pitch": round(3 * math.sin(t * 0.2 + i * 0.9), 1),
            "face_confidence": round(0.92 + 0.06 * math.sin(t * 0.15 + i), 2),
            "is_remote": i >= 3,
            "is_speaking": is_speaking,
            "gesture": "leaning_forward" if is_speaking else "neutral",
        })

    point_cloud_density = 2400 + int(200 * math.sin(t * 0.1))
    drift_alert = abs(math.sin(t * 0.05)) > 0.95

    return {
        "meeting_id": meeting_id,
        "positions": positions,
        "point_cloud": {"density": point_cloud_density, "coverage": round(0.92 + 0.05 * math.sin(t * 0.08), 2)},
        "drift_detected": drift_alert,
        "drift_mm": round(abs(2.5 * math.sin(t * 0.07)), 1) if drift_alert else 0,
        "tracking_fps": 30 + int(2 * math.sin(t * 0.3)),
        "depth_accuracy_mm": round(11 + 3 * math.sin(t * 0.12), 1),
        "room_lighting": {
            "quality": round(0.72 + 0.15 * math.sin(t * 0.04), 2),
            "lux": int(320 + 80 * math.sin(t * 0.06)),
            "recommendation": "optimal" if math.sin(t * 0.04) > -0.3 else "increase_lighting",
        },
        "frame_adjustments": [
            {
                "user_id": sp["id"],
                "crop_width": round(0.65 + 0.1 * math.sin(t * 0.2 + i), 3),
                "brightness_adjust": round(0.05 * math.sin(t * 0.15 + i), 3),
                "auto_framing_active": True,
            }
            for i, sp in enumerate(SPEAKERS)
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{meeting_id}/camera-stream")
async def camera_stream(meeting_id: str, user=Depends(require_auth)):
    """Real-time 360 camera stream with auto-tracking."""
    t = _t()
    active_idx = int(t / 6) % len(SPEAKERS)
    prev_idx = (int(t / 6) - 1) % len(SPEAKERS)

    headshots = []
    for i, sp in enumerate(SPEAKERS):
        is_speaking = i == active_idx
        was_speaking = i == prev_idx
        quality_base = 0.92 if is_speaking else 0.85
        gaze_drift = 8 * math.sin(t * 0.5 + i * 2.3)

        headshots.append({
            "user_id": sp["id"],
            "user_name": sp["name"],
            "crop_region": {"x": int(640 * (i + 1) / (len(SPEAKERS) + 1) * 6), "y": 160, "width": 320, "height": 480},
            "quality_score": round(quality_base + 0.05 * math.sin(t * 0.3 + i), 2),
            "gaze_direction": round(gaze_drift, 1),
            "is_speaking": is_speaking,
            "was_recently_speaking": was_speaking,
            "seat_position": i + 1,
            "tracking_lock": is_speaking,
            "zoom_level": round(1.4 if is_speaking else 1.0, 1),
        })

    fov_angle = 180 + 30 * math.sin(t * 0.08)

    return {
        "meeting_id": meeting_id,
        "headshots": headshots,
        "panoramic_status": "active",
        "camera_connected": True,
        "fov_degrees": round(fov_angle, 1),
        "auto_tracking": {"enabled": True, "target": SPEAKERS[active_idx]["name"], "confidence": round(0.94 + 0.04 * math.sin(t * 0.2), 2)},
        "frame_rate": 30,
        "resolution": "3840x1080",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{meeting_id}/audio-stream")
async def audio_stream(meeting_id: str, user=Depends(require_auth)):
    """Real-time beamforming audio stream with dynamic beam direction."""
    t = _t()
    active_idx = int(t / 8) % len(SPEAKERS[:4])
    beam_angle = (360 / 4) * active_idx + 15 * math.sin(t * 0.5)

    profiles = []
    noise_types = ["ambient", "hvac", "ambient", "keyboard", "ambient", "ambient"]
    for i, sp in enumerate(SPEAKERS[:4]):
        is_speaking = i == active_idx
        base_snr = 38 if is_speaking else 28
        snr = base_snr + 5 * math.sin(t * 0.4 + i * 1.5)
        noise_event = abs(math.sin(t * 0.1 + i * 3)) > 0.92
        profiles.append({
            "user_id": sp["id"],
            "user_name": sp["name"],
            "snr_db": round(snr, 1),
            "signal_level_db": round(-22 + 4 * math.sin(t * 0.3 + i), 1),
            "noise_floor_db": round(-60 + 8 * math.sin(t * 0.15 + i * 2), 1),
            "noise_type": "traffic" if noise_event else noise_types[i],
            "is_speaking": is_speaking,
            "voice_activity": round(0.9 if is_speaking else 0.1 + 0.1 * abs(math.sin(t * 0.6 + i)), 2),
        })

    avg_snr = sum(p["snr_db"] for p in profiles) / len(profiles)
    beam_width = 60 + 10 * math.sin(t * 0.2)

    beam_pattern = []
    for angle in range(0, 360, 5):
        diff = abs(angle - beam_angle) % 360
        if diff > 180:
            diff = 360 - diff
        gain = max(0.05, math.cos(math.radians(diff * 180 / beam_width)) ** 2) if diff < beam_width else 0.05
        beam_pattern.append({"angle": angle, "gain": round(gain, 3)})

    spectrum = []
    for freq in [63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]:
        base = -20 if 250 <= freq <= 4000 else -40
        level = base + 6 * math.sin(t * 0.5 + freq * 0.001)
        spectrum.append({"frequency": freq, "level_db": round(level, 1)})

    return {
        "meeting_id": meeting_id,
        "config": {"mode": "auto", "target_angle": round(beam_angle, 1), "beam_width": round(beam_width, 1)},
        "audio_profiles": profiles,
        "health": {
            "overall_snr_db": round(avg_snr, 1),
            "quality_rating": "excellent" if avg_snr > 35 else "good" if avg_snr > 25 else "fair",
            "processing_latency_ms": round(2.8 + 1.5 * abs(math.sin(t * 0.4)), 1),
            "sample_rate": 48000,
            "channels": 2,
        },
        "beam_pattern": beam_pattern,
        "spectrum": spectrum,
        "active_speaker": SPEAKERS[active_idx]["name"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{meeting_id}/iot-stream")
async def iot_stream(meeting_id: str, user=Depends(require_auth)):
    """Real-time IoT sensor readings with environmental drift."""
    t = _t()
    meeting_minutes = (t % 3600) / 60

    temp = 22.0 + 0.8 * math.sin(t * 0.005) + min(meeting_minutes * 0.03, 1.2)
    humidity = 42 + 8 * math.sin(t * 0.008) + min(meeting_minutes * 0.1, 5)
    co2 = 420 + min(meeting_minutes * 8, 350) + 30 * math.sin(t * 0.01)
    light_lux = 380 + 60 * math.sin(t * 0.003)
    noise_db = 38 + 8 * math.sin(t * 0.4) + 5 * abs(math.sin(t * 0.02))

    air_quality = "good" if co2 < 600 else "moderate" if co2 < 800 else "poor"
    ventilation_alert = co2 > 750
    comfort_score = max(0.4, 1.0 - abs(temp - 22) * 0.08 - max(0, co2 - 500) * 0.0005 - max(0, humidity - 55) * 0.01)

    return {
        "meeting_id": meeting_id,
        "sensors": {
            "temperature": {"value": round(temp, 1), "unit": "C", "trend": "rising" if math.sin(t * 0.005) > 0 else "falling"},
            "humidity": {"value": round(humidity, 1), "unit": "%", "trend": "stable"},
            "co2": {"value": int(co2), "unit": "ppm", "alert": ventilation_alert},
            "light": {"value": int(light_lux), "unit": "lux", "quality": "good" if light_lux > 300 else "dim"},
            "noise": {"value": round(noise_db, 1), "unit": "dBA", "quality": "quiet" if noise_db < 45 else "moderate"},
        },
        "air_quality": air_quality,
        "comfort_score": round(comfort_score, 2),
        "ventilation_alert": ventilation_alert,
        "occupancy": {"count": 6, "capacity": 12, "density": "comfortable"},
        "energy": {"consumption_watts": int(280 + 40 * math.sin(t * 0.01)), "efficiency": "A+"},
        "auto_adjustments": [
            {"device": "hvac", "action": "increase_ventilation", "reason": f"CO2 at {int(co2)}ppm"}
        ] if ventilation_alert else [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{meeting_id}/biometric-stream")
async def biometric_stream(meeting_id: str, user=Depends(require_auth)):
    """Real-time biometric verification stream with confidence fluctuations."""
    t = _t()
    cycle_period = 30
    cycle_progress = (t % cycle_period) / cycle_period

    participants = []
    for i, sp in enumerate(SPEAKERS):
        base_integrity = 0.96 if i < 4 else 0.88
        integrity = base_integrity + 0.03 * math.sin(t * 0.1 + i * 1.7)
        integrity = max(0.7, min(1.0, integrity))

        check_count = int((t % 300) / 15) + i * 2
        is_reverifying = abs(math.sin(t * 0.08 + i * 2.5)) > 0.93
        liveness_score = 0.95 + 0.04 * math.sin(t * 0.12 + i)

        trust_level = "high" if integrity > 0.92 else "medium" if integrity > 0.8 else "low"

        hash_segment = hex(int(abs(math.sin(t * 0.01 + i)) * 0xFFFF))[2:].zfill(4)

        participants.append({
            "user_id": sp["id"],
            "user_name": sp["name"],
            "integrity_score": round(integrity, 3),
            "trust_level": trust_level,
            "verified": integrity > 0.85,
            "check_count": check_count,
            "liveness_score": round(liveness_score, 3),
            "is_reverifying": is_reverifying,
            "last_check_ago": f"{int(t % 15)}s ago",
            "watermark_active": True,
            "visual_pattern": {
                "hash_preview": f"0x{hash_segment}...",
                "segments": [
                    {"size": 3 + int(2 * math.sin(t * 0.2 + i + j)), "color": sp["color"], "opacity": round(0.3 + 0.2 * math.sin(t * 0.1 + j), 2), "position": j}
                    for j in range(4)
                ],
            },
        })

    verified = sum(1 for p in participants if p["verified"])
    avg_integrity = sum(p["integrity_score"] for p in participants) / len(participants)
    overall = "high" if verified == len(participants) else "medium" if verified > len(participants) / 2 else "low"

    return {
        "meeting_id": meeting_id,
        "summary": {
            "overall_trust": overall,
            "verified": verified,
            "total": len(participants),
            "average_integrity": round(avg_integrity, 3),
            "scan_cycle": round(cycle_progress * 100),
        },
        "participants": participants,
        "next_full_scan": f"{int((1 - cycle_progress) * cycle_period)}s",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
