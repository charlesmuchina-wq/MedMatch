"""
ENZI Sentiment Analysis
- Analyze message tone/sentiment
- Return tone badge (positive/neutral/urgent/negative)
- Channel mood trends
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import logging

from emergentintegrations.llm.chat import LlmChat, UserMessage
from utils.config import EMERGENT_LLM_KEY
from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/sentiment", tags=["ENZI Sentiment"])
logger = logging.getLogger(__name__)


class SentimentRequest(BaseModel):
    message_content: str
    channel_id: Optional[str] = None


@router.post("/analyze")
async def analyze_sentiment(req: SentimentRequest, request: Request):
    """Analyze sentiment of a message"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if not EMERGENT_LLM_KEY:
        # Fallback: simple keyword-based sentiment
        text = req.message_content.lower()
        if any(w in text for w in ['urgent', 'asap', 'critical', 'emergency', 'immediately']):
            return {"tone": "urgent", "confidence": 0.8}
        if any(w in text for w in ['great', 'thanks', 'awesome', 'love', 'excellent', 'amazing', 'good job']):
            return {"tone": "positive", "confidence": 0.7}
        if any(w in text for w in ['issue', 'problem', 'bug', 'fail', 'wrong', 'broken', 'disappointed']):
            return {"tone": "negative", "confidence": 0.7}
        return {"tone": "neutral", "confidence": 0.6}

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            system_message="Classify this message's tone as exactly one of: positive, neutral, urgent, negative. Reply with ONLY the tone word, nothing else."
        ).with_model("openai", "gpt-4.1-mini")
        resp = await chat.send_message_async(UserMessage(content=req.message_content[:300]))
        tone = resp.text.strip().lower()
        if tone not in ("positive", "neutral", "urgent", "negative"):
            tone = "neutral"
        return {"tone": tone, "confidence": 0.9}
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        # Fallback to keyword-based
        text = req.message_content.lower()
        if any(w in text for w in ['urgent', 'asap', 'critical', 'emergency', 'immediately']):
            return {"tone": "urgent", "confidence": 0.7}
        if any(w in text for w in ['great', 'thanks', 'awesome', 'love', 'excellent', 'amazing', 'good job']):
            return {"tone": "positive", "confidence": 0.6}
        if any(w in text for w in ['issue', 'problem', 'bug', 'fail', 'wrong', 'broken', 'disappointed']):
            return {"tone": "negative", "confidence": 0.6}
        return {"tone": "neutral", "confidence": 0.5}


@router.get("/channel/{channel_id}/mood")
async def get_channel_mood(channel_id: str, request: Request):
    """Get mood trend for a channel based on recent messages"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    messages = await db.lumi_messages.find(
        {"channel_id": channel_id},
        {"_id": 0, "content": 1}
    ).sort("created_at", -1).limit(20).to_list(20)

    if not messages:
        return {"mood": "neutral", "distribution": {"positive": 0, "neutral": 100, "urgent": 0, "negative": 0}}

    # Simple keyword-based bulk analysis for speed
    dist = {"positive": 0, "neutral": 0, "urgent": 0, "negative": 0}
    for m in messages:
        text = (m.get("content") or "").lower()
        if any(w in text for w in ['urgent', 'asap', 'critical', 'emergency']):
            dist["urgent"] += 1
        elif any(w in text for w in ['great', 'thanks', 'awesome', 'love', 'good']):
            dist["positive"] += 1
        elif any(w in text for w in ['issue', 'problem', 'bug', 'fail', 'wrong']):
            dist["negative"] += 1
        else:
            dist["neutral"] += 1

    total = sum(dist.values()) or 1
    pct = {k: round(v / total * 100) for k, v in dist.items()}

    dominant = max(dist, key=dist.get)
    return {"mood": dominant, "distribution": pct, "message_count": len(messages)}
