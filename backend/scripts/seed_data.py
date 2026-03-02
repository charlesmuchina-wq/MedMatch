"""
Seed script: Populate MongoDB with sample meetings and webinars.
Usage: python scripts/seed_data.py
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.environ.get('MONGO_URL')
DB_NAME = os.environ.get('DB_NAME', 'MedMatch').strip('"')

ADMIN_USER_ID = None  # Will be looked up from DB

MEETING_TITLES_PAST = [
    "Q4 Revenue Strategy Review",
    "Product Design Sprint Retro",
    "AI Ethics Board Meeting",
    "Cross-Team Alignment Sync",
    "Customer Success Deep Dive",
]

MEETING_TITLES_UPCOMING = [
    "Q1 Kickoff: Growth Roadmap",
    "Engineering Architecture Review",
    "Partnership Exploration Call",
    "Weekly Team Standup",
    "Board Advisory Session",
]

WEBINAR_TITLES_PAST = [
    "AI in Healthcare: 2026 Trends",
    "Building Scalable Video Platforms",
    "Remote-First Culture Workshop",
    "Zero-Trust Security Masterclass",
    "The Future of Spatial Computing",
]

WEBINAR_TITLES_UPCOMING = [
    "Distance Zero: Next-Gen Communication",
    "AI Meeting Intelligence Demo Day",
    "Enterprise Collaboration Summit",
    "Developer Experience Workshop",
    "Global Hybrid Work Strategies",
]

PARTICIPANT_NAMES = [
    ("Alice Chen", "alice@example.com"),
    ("David Kim", "david@example.com"),
    ("Maria Lopez", "maria@example.com"),
    ("James Wright", "james@example.com"),
    ("Priya Patel", "priya@example.com"),
    ("Yuki Tanaka", "yuki@example.com"),
    ("Omar Hassan", "omar@example.com"),
    ("Sophie Dubois", "sophie@example.com"),
]


def gen_meeting_id():
    return str(uuid.uuid4())[:8].upper()


def gen_webinar_id():
    return f"WEB-{uuid.uuid4().hex[:8].upper()}"


async def seed():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Find admin user
    admin = await db.users.find_one({"email": "admin@medmatch.com"}, {"_id": 0})
    if not admin:
        print("Admin user not found. Creating a fallback host identity.")
        host_id = "admin_seed"
        host_name = "Admin"
        host_email = "admin@medmatch.com"
    else:
        host_id = admin.get("user_id", "admin_seed")
        host_name = admin.get("name", "Admin")
        host_email = admin.get("email", "admin@medmatch.com")

    now = datetime.now(timezone.utc)

    # ---- PAST MEETINGS ----
    past_meetings = []
    for i, title in enumerate(MEETING_TITLES_PAST):
        days_ago = (i + 1) * 3 + i  # stagger: 4, 7, 12, 16, 21 days ago
        started = now - timedelta(days=days_ago, hours=2)
        ended = started + timedelta(minutes=45 + i * 10)
        mid = gen_meeting_id()

        participants = [
            {"user_id": host_id, "name": host_name, "role": "host", "joined_at": started.isoformat()},
        ]
        for j in range(min(3 + i, len(PARTICIPANT_NAMES))):
            pname, pemail = PARTICIPANT_NAMES[j]
            participants.append({
                "user_id": f"seed_user_{j}",
                "name": pname,
                "email": pemail,
                "role": "participant",
                "joined_at": (started + timedelta(minutes=j)).isoformat(),
            })

        meeting = {
            "meeting_id": mid,
            "title": title,
            "host_id": host_id,
            "host_name": host_name,
            "status": "ended",
            "created_at": (started - timedelta(minutes=10)).isoformat(),
            "scheduled_time": started.isoformat(),
            "started_at": started.isoformat(),
            "ended_at": ended.isoformat(),
            "settings": {
                "video_enabled": True, "audio_enabled": True, "screen_share_enabled": True,
                "chat_enabled": True, "recording_enabled": True, "ai_notes_enabled": True,
                "breakout_rooms_enabled": True, "waiting_room_enabled": True,
                "mute_on_entry": True, "allow_participants_unmute": True,
                "lock_meeting": False, "max_participants": 100, "e2e_encryption": True,
            },
            "participants": participants,
            "chat_messages": [
                {"user_id": host_id, "name": host_name, "message": f"Welcome to {title}", "timestamp": started.isoformat()},
            ],
            "ai_notes": [
                {"type": "summary", "content": f"Key discussion points from {title}. Action items assigned to team leads.", "timestamp": ended.isoformat()},
            ],
            "recordings": [{"recording_id": f"rec_{mid}", "duration": (ended - started).seconds, "status": "available"}] if i < 3 else [],
            "breakout_rooms": [],
            "waiting_room": [],
        }
        past_meetings.append(meeting)

    # ---- UPCOMING MEETINGS ----
    upcoming_meetings = []
    for i, title in enumerate(MEETING_TITLES_UPCOMING):
        days_ahead = (i + 1) * 2  # 2, 4, 6, 8, 10 days ahead
        scheduled = now + timedelta(days=days_ahead, hours=10)
        mid = gen_meeting_id()

        meeting = {
            "meeting_id": mid,
            "title": title,
            "host_id": host_id,
            "host_name": host_name,
            "status": "waiting",
            "created_at": now.isoformat(),
            "scheduled_time": scheduled.isoformat(),
            "started_at": None,
            "ended_at": None,
            "settings": {
                "video_enabled": True, "audio_enabled": True, "screen_share_enabled": True,
                "chat_enabled": True, "recording_enabled": True, "ai_notes_enabled": True,
                "breakout_rooms_enabled": True, "waiting_room_enabled": True,
                "mute_on_entry": True, "allow_participants_unmute": True,
                "lock_meeting": False, "max_participants": 100, "e2e_encryption": True,
            },
            "participants": [],
            "chat_messages": [],
            "ai_notes": [],
            "recordings": [],
            "breakout_rooms": [],
            "waiting_room": [],
        }
        upcoming_meetings.append(meeting)

    # ---- PAST WEBINARS ----
    past_webinars = []
    for i, title in enumerate(WEBINAR_TITLES_PAST):
        days_ago = (i + 1) * 4 + 2
        started = now - timedelta(days=days_ago, hours=3)
        ended = started + timedelta(hours=1, minutes=30)
        wid = gen_webinar_id()

        registrations = []
        attendees = []
        for j in range(min(5 + i * 2, len(PARTICIPANT_NAMES))):
            pname, pemail = PARTICIPANT_NAMES[j]
            registrations.append({
                "name": pname, "email": pemail, "organization": "Tech Corp",
                "role": "attendee", "registered_at": (started - timedelta(days=3)).isoformat(),
            })
            attendees.append({
                "user_id": f"seed_user_{j}", "name": pname, "email": pemail,
                "joined_at": (started + timedelta(minutes=j * 2)).isoformat(),
            })

        webinar = {
            "webinar_id": wid,
            "title": title,
            "description": f"A comprehensive session on {title.lower()}. Featuring industry experts and live Q&A.",
            "host_id": host_id,
            "host_name": host_name,
            "host_email": host_email,
            "scheduled_time": started.isoformat(),
            "max_attendees": 500,
            "status": "ended",
            "registration_required": True,
            "settings": {
                "auto_record": True, "q_and_a_enabled": True, "chat_enabled": True,
                "attendee_video": False, "attendee_audio": False, "practice_session": False,
            },
            "org_privacy": {"org_domains": [], "internal_only_docs": True, "external_download_blocked": True},
            "guest_permissions": {},
            "panelists": [{"email": PARTICIPANT_NAMES[0][1], "role": "panelist"}],
            "coordinators": [],
            "active_roles": {},
            "hand_raises": [],
            "practice_mode": False,
            "registrations": registrations,
            "attendees": attendees,
            "questions": [
                {"question_id": f"q_{wid}_1", "user_id": f"seed_user_1", "user_name": PARTICIPANT_NAMES[1][0],
                 "question": "How does this apply to small teams?", "upvotes": 5, "status": "answered",
                 "answer": "Great question! It scales naturally.", "timestamp": started.isoformat()},
            ],
            "polls": [],
            "analytics": {
                "peak_attendees": len(attendees),
                "avg_watch_time": 75,
                "questions_asked": 3 + i,
                "engagement_score": 72 + i * 5,
            },
            "created_at": (started - timedelta(days=7)).isoformat(),
        }
        past_webinars.append(webinar)

    # ---- UPCOMING WEBINARS ----
    upcoming_webinars = []
    for i, title in enumerate(WEBINAR_TITLES_UPCOMING):
        days_ahead = (i + 1) * 3 + 1
        scheduled = now + timedelta(days=days_ahead, hours=14)
        wid = gen_webinar_id()

        registrations = []
        for j in range(min(3 + i, len(PARTICIPANT_NAMES))):
            pname, pemail = PARTICIPANT_NAMES[j]
            registrations.append({
                "name": pname, "email": pemail, "organization": "Tech Corp",
                "role": "attendee", "registered_at": now.isoformat(),
            })

        webinar = {
            "webinar_id": wid,
            "title": title,
            "description": f"Join us for {title.lower()}. Interactive session with live demos and expert panels.",
            "host_id": host_id,
            "host_name": host_name,
            "host_email": host_email,
            "scheduled_time": scheduled.isoformat(),
            "max_attendees": 1000,
            "status": "scheduled",
            "registration_required": True,
            "settings": {
                "auto_record": True, "q_and_a_enabled": True, "chat_enabled": True,
                "attendee_video": False, "attendee_audio": False, "practice_session": True,
            },
            "org_privacy": {"org_domains": [], "internal_only_docs": True, "external_download_blocked": True},
            "guest_permissions": {},
            "panelists": [{"email": PARTICIPANT_NAMES[0][1], "role": "panelist"}],
            "coordinators": [],
            "active_roles": {},
            "hand_raises": [],
            "practice_mode": False,
            "registrations": registrations,
            "attendees": [],
            "questions": [],
            "polls": [],
            "analytics": {
                "peak_attendees": 0,
                "avg_watch_time": 0,
                "questions_asked": 0,
                "engagement_score": 0,
            },
            "created_at": now.isoformat(),
        }
        upcoming_webinars.append(webinar)

    # ---- INSERT ----
    all_meetings = past_meetings + upcoming_meetings
    all_webinars = past_webinars + upcoming_webinars

    # Clear old seed data (optional - use tag to identify)
    await db.karau_meetings.delete_many({"title": {"$in": MEETING_TITLES_PAST + MEETING_TITLES_UPCOMING}})
    await db.webinars.delete_many({"title": {"$in": WEBINAR_TITLES_PAST + WEBINAR_TITLES_UPCOMING}})

    if all_meetings:
        await db.karau_meetings.insert_many(all_meetings)
        print(f"Inserted {len(all_meetings)} meetings ({len(past_meetings)} past, {len(upcoming_meetings)} upcoming)")

    if all_webinars:
        await db.webinars.insert_many(all_webinars)
        print(f"Inserted {len(all_webinars)} webinars ({len(past_webinars)} past, {len(upcoming_webinars)} upcoming)")

    # Also seed some activity feed data
    activities = []
    for i, m in enumerate(past_meetings):
        activities.append({
            "user_id": host_id,
            "type": "meeting_started",
            "text": f"Meeting '{m['title']}' completed with {len(m['participants'])} participants",
            "icon": "video",
            "meeting_id": m["meeting_id"],
            "timestamp": m["ended_at"],
        })
        if m["ai_notes"]:
            activities.append({
                "user_id": host_id,
                "type": "ai_insight",
                "text": f"AI generated summary for '{m['title']}'",
                "icon": "sparkles",
                "meeting_id": m["meeting_id"],
                "timestamp": m["ended_at"],
            })

    if activities:
        await db.karau_activities.delete_many({"user_id": host_id, "type": {"$in": ["meeting_started", "ai_insight"]}})
        await db.karau_activities.insert_many(activities)
        print(f"Inserted {len(activities)} activity feed items")

    print("\nSeed data complete!")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
