"""
Meeting Analytics & Engagement API
Gap assessment features based on 2024/25 user surveys:
- Meeting effectiveness scoring
- Participation analytics
- Engagement metrics
- Gamification (meeting streaks, points)
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone, timedelta
import os

from utils.database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/karau/analytics", tags=["Meeting Analytics"])

db = get_db()


class MeetingEffectivenessResponse(BaseModel):
    overall_score: int  # 0-100
    avg_duration_minutes: float
    avg_participants: float
    meetings_with_notes: int
    meetings_with_action_items: int
    total_meetings: int
    on_time_rate: int  # percentage
    engagement_level: str  # "High", "Medium", "Low"
    tip: str


class ParticipationStats(BaseModel):
    total_meetings_attended: int
    total_meetings_hosted: int
    total_hours: float
    avg_meeting_duration: float
    busiest_day: str
    busiest_hour: int
    meetings_by_day: Dict[str, int]
    weekly_trend: List[int]


class GamificationProfile(BaseModel):
    level: int
    xp: int
    xp_to_next: int
    streak_days: int
    badges: List[Dict]
    rank_title: str
    total_meetings: int
    total_hours: float


@router.get("/effectiveness", response_model=MeetingEffectivenessResponse)
async def get_meeting_effectiveness(user=Depends(get_current_user)):
    """AI-analyzed meeting effectiveness score."""
    meetings = list(db.meetings.find(
        {"host_id": user["user_id"]},
        {"_id": 0, "duration": 1, "participants": 1, "ai_notes": 1,
         "scheduled_time": 1, "started_at": 1, "created_at": 1}
    ).sort("created_at", -1).limit(50))

    total = len(meetings)
    if total == 0:
        return MeetingEffectivenessResponse(
            overall_score=0, avg_duration_minutes=0, avg_participants=0,
            meetings_with_notes=0, meetings_with_action_items=0,
            total_meetings=0, on_time_rate=0, engagement_level="Low",
            tip="Host your first meeting to see analytics!"
        )

    total_duration = sum(m.get("duration", 0) for m in meetings)
    total_participants = sum(len(m.get("participants", [])) for m in meetings)
    with_notes = sum(1 for m in meetings if m.get("ai_notes"))
    with_actions = sum(1 for m in meetings if m.get("ai_notes", {}).get("action_items"))
    on_time = sum(1 for m in meetings if m.get("scheduled_time") and m.get("started_at"))

    avg_dur = (total_duration / total / 60) if total > 0 else 0
    avg_part = total_participants / total if total > 0 else 0
    on_time_rate = int((on_time / total) * 100) if total > 0 else 100

    # Calculate effectiveness score
    score = 50  # base
    if avg_part >= 2: score += 10
    if avg_dur >= 15 and avg_dur <= 60: score += 15
    elif avg_dur > 60: score -= 5
    if with_notes > total * 0.5: score += 15
    if with_actions > total * 0.3: score += 10
    score = max(0, min(100, score))

    if score >= 75: engagement = "High"
    elif score >= 50: engagement = "Medium"
    else: engagement = "Low"

    tips = {
        "High": "Excellent! Your meetings are productive and well-documented.",
        "Medium": "Good progress! Try enabling AI notes for better documentation.",
        "Low": "Consider setting agendas and using AI assistant for better outcomes."
    }

    return MeetingEffectivenessResponse(
        overall_score=score,
        avg_duration_minutes=round(avg_dur, 1),
        avg_participants=round(avg_part, 1),
        meetings_with_notes=with_notes,
        meetings_with_action_items=with_actions,
        total_meetings=total,
        on_time_rate=on_time_rate,
        engagement_level=engagement,
        tip=tips[engagement]
    )


@router.get("/participation", response_model=ParticipationStats)
async def get_participation_stats(user=Depends(get_current_user)):
    """Detailed participation breakdown."""
    user_id = user["user_id"]

    hosted = list(db.meetings.find(
        {"host_id": user_id}, {"_id": 0, "created_at": 1, "duration": 1}
    ))
    attended = list(db.meetings.find(
        {"participants": user_id}, {"_id": 0, "created_at": 1, "duration": 1}
    ))

    all_meetings = hosted + attended
    total_hours = sum(m.get("duration", 0) for m in all_meetings) / 3600

    # Meetings by day of week
    days = {"Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0, "Sun": 0}
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = [0] * 24

    for m in all_meetings:
        created = m.get("created_at")
        if isinstance(created, str):
            try:
                created = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except:
                continue
        if created:
            days[day_names[created.weekday()]] += 1
            hours[created.hour] += 1

    busiest_day = max(days, key=days.get) if days else "Mon"
    busiest_hour = hours.index(max(hours)) if hours else 9

    # Weekly trend (last 8 weeks)
    now = datetime.now(timezone.utc)
    weekly = []
    for w in range(7, -1, -1):
        week_start = now - timedelta(weeks=w+1)
        week_end = now - timedelta(weeks=w)
        count = sum(1 for m in all_meetings
                    if m.get("created_at") and
                    ((isinstance(m["created_at"], datetime) and week_start <= m["created_at"] <= week_end) or
                     (isinstance(m["created_at"], str))))
        weekly.append(count)

    return ParticipationStats(
        total_meetings_attended=len(attended),
        total_meetings_hosted=len(hosted),
        total_hours=round(total_hours, 1),
        avg_meeting_duration=round(sum(m.get("duration", 0) for m in all_meetings) / max(len(all_meetings), 1) / 60, 1),
        busiest_day=busiest_day,
        busiest_hour=busiest_hour,
        meetings_by_day=days,
        weekly_trend=weekly
    )


@router.get("/gamification", response_model=GamificationProfile)
async def get_gamification(user=Depends(get_current_user)):
    """Meeting gamification - XP, levels, badges, streaks."""
    user_id = user["user_id"]

    meetings = list(db.meetings.find(
        {"$or": [{"host_id": user_id}, {"participants": user_id}]},
        {"_id": 0, "created_at": 1, "duration": 1, "ai_notes": 1, "host_id": 1, "participants": 1}
    ))

    total = len(meetings)
    total_hours = sum(m.get("duration", 0) for m in meetings) / 3600
    hosted = sum(1 for m in meetings if m.get("host_id") == user_id)
    with_notes = sum(1 for m in meetings if m.get("ai_notes"))

    # Calculate XP
    xp = total * 50  # 50 XP per meeting
    xp += hosted * 25  # bonus for hosting
    xp += with_notes * 30  # bonus for using AI notes
    xp += int(total_hours * 10)  # 10 XP per hour

    # Level calculation (100 XP per level, scaling)
    level = 1
    xp_needed = 100
    remaining_xp = xp
    while remaining_xp >= xp_needed:
        remaining_xp -= xp_needed
        level += 1
        xp_needed = int(100 * (1.2 ** (level - 1)))

    # Calculate streak (consecutive days with meetings)
    now = datetime.now(timezone.utc)
    streak = 0
    for d in range(30):
        day = now - timedelta(days=d)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day.replace(hour=23, minute=59, second=59)
        has_meeting = any(
            m.get("created_at") and isinstance(m["created_at"], datetime)
            and day_start <= m["created_at"] <= day_end
            for m in meetings
        )
        if has_meeting:
            streak += 1
        elif d > 0:
            break

    # Badges
    badges = []
    if total >= 1: badges.append({"id": "first_meeting", "name": "First Steps", "icon": "rocket", "earned": True})
    if total >= 10: badges.append({"id": "10_meetings", "name": "Regular", "icon": "calendar", "earned": True})
    if total >= 50: badges.append({"id": "50_meetings", "name": "Power User", "icon": "zap", "earned": True})
    if hosted >= 5: badges.append({"id": "host_5", "name": "Meeting Leader", "icon": "crown", "earned": True})
    if with_notes >= 5: badges.append({"id": "ai_5", "name": "AI Enthusiast", "icon": "sparkles", "earned": True})
    if streak >= 3: badges.append({"id": "streak_3", "name": "On a Roll", "icon": "flame", "earned": True})
    if streak >= 7: badges.append({"id": "streak_7", "name": "Unstoppable", "icon": "trophy", "earned": True})
    if total_hours >= 10: badges.append({"id": "10_hours", "name": "Time Well Spent", "icon": "clock", "earned": True})

    # Rank title
    ranks = {1: "Newcomer", 3: "Participant", 5: "Contributor", 8: "Collaborator",
             12: "Meeting Pro", 15: "Team Leader", 20: "Meeting Master"}
    rank_title = "Newcomer"
    for lvl, title in sorted(ranks.items()):
        if level >= lvl:
            rank_title = title

    return GamificationProfile(
        level=level,
        xp=xp,
        xp_to_next=xp_needed - remaining_xp,
        streak_days=streak,
        badges=badges,
        rank_title=rank_title,
        total_meetings=total,
        total_hours=round(total_hours, 1)
    )
