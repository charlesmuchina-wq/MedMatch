"""
ENZI AI Auto-Responses & Conversation Summaries
- Smart auto-reply suggestions based on message bucket category
- AI-generated conversation summaries for long threads
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import logging

from emergentintegrations.llm.chat import LlmChat, UserMessage
from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/ai", tags=["ENZI AI Features"])
logger = logging.getLogger(__name__)

BUCKET_QUICK_REPLIES = {
    "urgent": ["I'm on it!", "Acknowledged, handling now", "Will prioritize this immediately", "Got it, addressing now"],
    "action_required": ["On it!", "Will take care of this", "I'll handle this today", "Thanks, working on it"],
    "meeting_request": ["I'll join the meeting", "Count me in", "I'll be there", "Can we reschedule?"],
    "fyi": ["Thanks for the update", "Noted, thanks!", "Good to know", "Appreciate the heads up"],
    "social": ["Thanks!", "Sounds great!", "Awesome!", "Love it!"],
}


class AutoReplyRequest(BaseModel):
    message_id: str
    channel_id: str
    message_content: str
    bucket_category: Optional[str] = None


class SummarizeRequest(BaseModel):
    channel_id: str
    message_count: Optional[int] = 50


@router.post("/auto-reply/suggestions")
async def get_auto_reply_suggestions(req: AutoReplyRequest, request: Request):
    """Get smart auto-reply suggestions based on message content and bucket category"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Quick replies from bucket category
    quick_replies = BUCKET_QUICK_REPLIES.get(req.bucket_category, BUCKET_QUICK_REPLIES["fyi"])

    # AI-generated contextual reply if LLM key available
    ai_reply = None
    if EMERGENT_LLM_KEY and req.message_content:
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                system_message="You are ENZI, an AI assistant. Generate ONE short, professional reply (under 20 words) to this message. Be helpful and direct. No quotes or explanations."
            ).with_model("openai", "gpt-4.1-mini")
            resp = await chat.send_message_async(UserMessage(content=f"Reply to: {req.message_content[:200]}"))
            ai_reply = resp.text.strip().strip('"').strip("'")
        except Exception as e:
            logger.error(f"AI auto-reply failed: {e}")

    suggestions = quick_replies[:3]
    if ai_reply:
        suggestions = [ai_reply] + suggestions[:2]

    return {"suggestions": suggestions, "category": req.bucket_category}


@router.post("/summarize")
async def summarize_conversation(req: SummarizeRequest, request: Request):
    """Generate an AI summary of recent messages in a channel"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="AI service unavailable")

    # Fetch recent messages
    messages = await db.lumi_messages.find(
        {"channel_id": req.channel_id},
        {"_id": 0, "content": 1, "sender_name": 1, "created_at": 1}
    ).sort("created_at", -1).limit(req.message_count).to_list(req.message_count)

    if not messages:
        return {"summary": "No messages to summarize.", "message_count": 0}

    messages.reverse()
    transcript = "\n".join([
        f"{m.get('sender_name', 'User')}: {m.get('content', '')}"
        for m in messages if m.get('content')
    ])

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            system_message="""You are ENZI, an AI assistant. Summarize this conversation concisely:
- Key decisions made
- Action items assigned
- Important updates shared
- Any unresolved questions
Keep it under 150 words. Use bullet points. Be specific about who said what."""
        ).with_model("openai", "gpt-4.1-mini")
        resp = await chat.send_message_async(UserMessage(content=f"Summarize this conversation ({len(messages)} messages):\n\n{transcript[:3000]}"))
        return {"summary": resp.text.strip(), "message_count": len(messages)}
    except Exception as e:
        logger.error(f"Summarize failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")
