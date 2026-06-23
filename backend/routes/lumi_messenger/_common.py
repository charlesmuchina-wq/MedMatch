"""
LUMI Messenger - Real-time Channel-based Messaging
Standalone messaging platform integrated with KARAU auth
Features: Domain privacy, threads, presence, retention, voice calls
"""

# Auto-split shared module. Imports, models, constants, helpers, singletons.

from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect

from pydantic import BaseModel

from typing import Optional, List

from datetime import datetime, timezone, timedelta

import uuid

import json

import asyncio

from utils.database import db

from routes.auth import get_current_user

class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    is_private: bool = False
    channel_type: str = "group"  # group, project, announcement, domain
    invite_emails: Optional[List[str]] = []  # Emails to invite on creation
    requires_approval: bool = False  # Require admin approval to join

class ChannelInvite(BaseModel):
    emails: List[str]  # Emails to invite

class InviteAction(BaseModel):
    action: str  # "accept" or "decline"

class ThreadReply(BaseModel):
    content: str

class PresenceUpdate(BaseModel):
    status: str  # available, busy, in_meeting, ooo, vacation

class RetentionConfig(BaseModel):
    days: int = 90

class MessageSend(BaseModel):
    content: str
    reply_to: Optional[str] = None

class DMCreate(BaseModel):
    recipient_id: str

class ChannelNotifPrefs(BaseModel):
    channel_id: str
    mute: bool = False
    level: str = "all"  # all, mentions, none

class UserTheme(BaseModel):
    accent_color: str  # hex color

class RetentionPolicy(BaseModel):
    channel_id: str
    auto_delete_days: int = 0  # 0 = no auto-delete
    enabled: bool = True

class HoldPolicy(BaseModel):
    channel_id: str
    hold_type: str  # "contractual" or "legal"
    reason: str = ""
    duration_days: int = 0  # 0 = indefinite (for legal hold)
    active: bool = True

class OrgAdminSettings(BaseModel):
    it_admin_name: str = ""
    it_admin_email: str = ""
    manager_name: str = ""
    manager_email: str = ""
    department: str = ""
    compliance_officer: str = ""

class HoldRequestAction(BaseModel):
    action: str  # "approve" or "reject"
    note: str = ""

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.user_channels: dict[str, set] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        # Update presence
        await db.lumi_presence.update_one(
            {"user_id": user_id},
            {"$set": {"status": "online", "last_seen": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        asyncio.create_task(self._set_offline(user_id))

    async def _set_offline(self, user_id: str):
        await db.lumi_presence.update_one(
            {"user_id": user_id},
            {"$set": {"status": "offline", "last_seen": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )

    async def send_to_channel(self, channel_id: str, message: dict):
        channel = await db.lumi_channels.find_one({"id": channel_id}, {"_id": 0, "members": 1})
        if not channel:
            return
        for member in channel.get("members", []):
            member_id = member.get("user_id")
            if member_id in self.active_connections:
                try:
                    await self.active_connections[member_id].send_json(message)
                except Exception:
                    pass

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
            except Exception:
                pass

    def get_online_users(self) -> list:
        return list(self.active_connections.keys())

manager = ConnectionManager()

class ReactionAdd(BaseModel):
    emoji: str

class MessageEdit(BaseModel):
    content: str

EDIT_WINDOW_MINUTES = 15

AI_CAPABILITIES = [
    {"id": "sentiment", "name": "Sentiment Analysis", "description": "Analyze team morale and mood from channel conversations", "category": "Productivity AI"},
    {"id": "tasks", "name": "Task Extraction", "description": "AI extracts action items and tasks from chat messages", "category": "Productivity AI"},
    {"id": "reports", "name": "Weekly Reports", "description": "Auto-generate channel activity and progress reports", "category": "Productivity AI"},
    {"id": "ask_ai", "name": "Ask LUMI AI", "description": "Conversational AI to query projects, tasks, and meetings", "category": "Actionable Intelligence"},
    {"id": "decision_cards", "name": "Decision Cards", "description": "AI-generated interactive cards for quick team decisions", "category": "Actionable Intelligence"},
    {"id": "anomaly_alerts", "name": "Anomaly Alerts", "description": "Proactive alerts when unusual patterns are detected", "category": "Actionable Intelligence"},
    {"id": "knowledge_graph", "name": "Knowledge Graph", "description": "Visualize relationships between people, tasks, and projects", "category": "Graph Intelligence"},
    {"id": "bottleneck_detection", "name": "Bottleneck Detection", "description": "Identify workload imbalances and project blockers", "category": "Graph Intelligence"},
    {"id": "what_if", "name": "What-If Simulator", "description": "Simulate project scenarios and predict outcomes", "category": "Advanced Collaboration"},
    {"id": "smart_notifications", "name": "Smart Notifications", "description": "AI-prioritized alerts based on urgency and relevance", "category": "Advanced Collaboration"},
    {"id": "translation", "name": "Real-time Translation", "description": "Translate messages into 20+ languages instantly", "category": "Communication"},
    {"id": "command_bar", "name": "Command Bar (Ctrl+K)", "description": "Quick search and AI queries from anywhere", "category": "Navigation"},
    {"id": "threading", "name": "Message Threading", "description": "Organize conversations with threaded replies", "category": "Core"},
    {"id": "file_sharing", "name": "File Sharing", "description": "Share images, documents, and files securely", "category": "Core"},
    {"id": "reactions", "name": "Reactions", "description": "React to messages with emoji reactions", "category": "Core"},
]

GLOBAL_RETENTION_DAYS = 90  # Automatic 90-day retention for all channels

async def log_audit(user_id: str, user_name: str, action: str, category: str, details: dict = None):
    """Log an admin action to the audit log"""
    await db.lumi_audit_log.insert_one({
        "id": f"audit_{uuid.uuid4().hex[:10]}",
        "user_id": user_id,
        "user_name": user_name,
        "action": action,
        "category": category,
        "details": details or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

import random

BLOCKED_PATTERNS = [
    # Slurs and hate speech patterns
    r'\b(slur|hate\s*speech|racial\s*epithet)\b',
]

import re

INAPPROPRIATE_WORDS = set([
    "fuck", "shit", "damn", "ass", "bitch", "bastard", "dick", "crap",
    "piss", "cunt", "cock", "whore", "slut", "nigger", "nigga", "faggot",
    "retard", "retarded"
])

def moderate_content(text: str) -> dict:
    """
    Professional environment content filter.
    Returns: {"clean": bool, "filtered_text": str, "flags": list}
    """
    if not text:
        return {"clean": True, "filtered_text": text, "flags": []}

    flags = []
    words = text.split()
    filtered_words = []

    for word in words:
        clean_word = re.sub(r'[^a-zA-Z]', '', word).lower()
        if clean_word in INAPPROPRIATE_WORDS:
            flags.append({"type": "profanity", "word": clean_word})
            filtered_words.append("*" * len(word))
        else:
            filtered_words.append(word)

    # Check for excessive caps (shouting)
    if len(text) > 10 and sum(1 for c in text if c.isupper()) / max(len(text.replace(" ", "")), 1) > 0.7:
        flags.append({"type": "excessive_caps", "word": ""})

    filtered_text = " ".join(filtered_words) if flags else text
    return {"clean": len(flags) == 0, "filtered_text": filtered_text, "flags": flags}

COMPLIANCE_FRAMEWORKS = {
    "hipaa": {
        "name": "HIPAA (US)",
        "region": "United States",
        "description": "Health Insurance Portability and Accountability Act",
        "requirements": [
            "PHI (Protected Health Information) must be encrypted at rest and in transit",
            "Access controls with unique user identification",
            "Audit trails for all data access",
            "Automatic logoff after inactivity",
            "Message retention per organizational policy",
            "Business Associate Agreements (BAA) required",
            "Breach notification within 60 days",
        ],
        "controls": {
            "encryption_at_rest": True,
            "encryption_in_transit": True,
            "audit_logging": True,
            "access_controls": True,
            "data_retention": True,
            "breach_notification": True,
        }
    },
    "gdpr": {
        "name": "GDPR (EU)",
        "region": "European Union",
        "description": "General Data Protection Regulation",
        "requirements": [
            "Lawful basis for processing personal data",
            "Right to access, rectification, and erasure",
            "Data portability rights",
            "Privacy by design and by default",
            "Data Protection Impact Assessments (DPIA)",
            "72-hour breach notification to supervisory authority",
            "Data Processing Agreements (DPA) required",
            "Consent management for data processing",
        ],
        "controls": {
            "data_minimization": True,
            "right_to_erasure": True,
            "data_portability": True,
            "consent_management": True,
            "dpia": True,
            "breach_notification_72h": True,
        }
    },
    "uk_dpa": {
        "name": "UK Data Protection Act 2018",
        "region": "United Kingdom",
        "description": "UK's implementation of data protection standards post-Brexit",
        "requirements": [
            "Lawful processing principles aligned with UK GDPR",
            "ICO (Information Commissioner's Office) registration",
            "Data Protection Officer appointment where required",
            "International transfer mechanisms (adequacy decisions, SCCs)",
            "Subject Access Request (SAR) fulfillment within 30 days",
            "Criminal offense for unlawful data obtaining",
        ],
        "controls": {
            "ico_registration": True,
            "dpo_appointment": True,
            "sar_process": True,
            "transfer_mechanisms": True,
        }
    },
    "australia_privacy": {
        "name": "Australian Privacy Act 1988 + APPs",
        "region": "Australia",
        "description": "Australian Privacy Principles governing personal information",
        "requirements": [
            "13 Australian Privacy Principles (APPs) compliance",
            "Notifiable Data Breaches (NDB) scheme — report within 30 days",
            "APP 11: Security of personal information",
            "APP 6: Use and disclosure limitations",
            "Privacy Impact Assessments for high-risk activities",
            "OAIC (Office of the Australian Information Commissioner) oversight",
        ],
        "controls": {
            "app_compliance": True,
            "ndb_scheme": True,
            "security_measures": True,
            "use_limitations": True,
        }
    },
    "china_pipl": {
        "name": "PIPL (China)",
        "region": "China",
        "description": "Personal Information Protection Law of the People's Republic of China",
        "requirements": [
            "Separate consent for sensitive personal information",
            "Data localization — store Chinese citizens' data in China",
            "Cross-border transfer requires security assessment by CAC",
            "Personal Information Protection Impact Assessments",
            "Designated person responsible for PI protection",
            "Incident notification to authorities and individuals",
            "Right to deletion, correction, and data portability",
        ],
        "controls": {
            "data_localization": True,
            "cross_border_assessment": True,
            "impact_assessment": True,
            "designated_person": True,
        }
    },
    "japan_appi": {
        "name": "APPI (Japan)",
        "region": "Japan",
        "description": "Act on the Protection of Personal Information",
        "requirements": [
            "Purpose specification and use limitation",
            "Proper acquisition of personal information",
            "Security control actions for personal data",
            "Restrictions on third-party provision",
            "Cross-border transfer with consent or adequacy recognition",
            "PPC (Personal Information Protection Commission) oversight",
            "Pseudonymized and anonymized processing frameworks",
        ],
        "controls": {
            "purpose_limitation": True,
            "security_controls": True,
            "third_party_restrictions": True,
            "ppc_oversight": True,
        }
    },
}
