"""
Enhanced Real-Time Sentiment Dashboard API
Advanced engagement heatmap, non-verbal cue indicators, and AI recommendations.
Also includes Multiplayer AI Copilots with cross-meeting context memory.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import os
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/sentiment-dash", tags=["Enhanced Sentiment Dashboard"])


class ParticipantSentiment(BaseModel):
    user_id: str
    user_name: str
    attention_score: float = 5.0  # 1-10
    confusion_level: float = 0.0  # 0-1
    engagement_level: float = 5.0  # 1-10
    energy: str = "neutral"  # high, neutral, low


class SentimentBatchUpdate(BaseModel):
    meeting_id: str
    participants: List[ParticipantSentiment]


class CopilotQuery(BaseModel):
    meeting_id: str
    question: str
    include_past_meetings: bool = True
    context_window: int = 5  # how many past meetings to reference


@router.post("/update")
async def update_sentiment_batch(data: SentimentBatchUpdate, user=Depends(require_auth)):
    """Batch update sentiment data for all participants in a meeting."""
    now = datetime.now(timezone.utc).isoformat()

    for p in data.participants:
        await db.sentiment_heatmap.update_one(
            {"meeting_id": data.meeting_id, "user_id": p.user_id},
            {"$set": {
                "user_name": p.user_name,
                "attention_score": p.attention_score,
                "confusion_level": p.confusion_level,
                "engagement_level": p.engagement_level,
                "energy": p.energy,
                "updated_at": now
            },
            "$push": {
                "history": {
                    "$each": [{
                        "attention": p.attention_score,
                        "confusion": p.confusion_level,
                        "engagement": p.engagement_level,
                        "energy": p.energy,
                        "ts": now
                    }],
                    "$slice": -30  # Keep last 30 data points
                }
            }},
            upsert=True
        )

    return {"success": True, "updated": len(data.participants)}


@router.get("/heatmap/{meeting_id}")
async def get_sentiment_heatmap(meeting_id: str, user=Depends(require_auth)):
    """Get real-time sentiment heatmap for all participants."""
    entries = await db.sentiment_heatmap.find(
        {"meeting_id": meeting_id},
        {"_id": 0, "user_id": 1, "user_name": 1, "attention_score": 1,
         "confusion_level": 1, "engagement_level": 1, "energy": 1,
         "updated_at": 1, "history": 1}
    ).to_list(100)

    # Calculate aggregate metrics
    if entries:
        avg_attention = sum(e.get("attention_score", 5) for e in entries) / len(entries)
        avg_engagement = sum(e.get("engagement_level", 5) for e in entries) / len(entries)
        avg_confusion = sum(e.get("confusion_level", 0) for e in entries) / len(entries)
        energy_counts = {}
        for e in entries:
            en = e.get("energy", "neutral")
            energy_counts[en] = energy_counts.get(en, 0) + 1
    else:
        avg_attention = avg_engagement = 5.0
        avg_confusion = 0.0
        energy_counts = {"neutral": 1}

    # Generate AI recommendations
    recommendations = []
    if avg_confusion > 0.5:
        recommendations.append({
            "type": "clarify",
            "priority": "high",
            "message": "High confusion detected. Consider pausing to clarify the current topic."
        })
    if avg_engagement < 4.0:
        recommendations.append({
            "type": "engage",
            "priority": "high",
            "message": "Engagement is dropping. Try asking a question or launching a quick poll."
        })
    if avg_attention < 3.5:
        recommendations.append({
            "type": "break",
            "priority": "medium",
            "message": "Attention levels are low. Consider a 2-minute break."
        })
    dominant_energy = max(energy_counts, key=energy_counts.get) if energy_counts else "neutral"
    if dominant_energy == "low":
        recommendations.append({
            "type": "energize",
            "priority": "medium",
            "message": "Room energy is low. Try switching to a more interactive format."
        })

    return {
        "meeting_id": meeting_id,
        "participants": entries,
        "aggregate": {
            "avg_attention": round(avg_attention, 1),
            "avg_engagement": round(avg_engagement, 1),
            "avg_confusion": round(avg_confusion, 2),
            "dominant_energy": dominant_energy,
            "energy_breakdown": energy_counts,
            "participant_count": len(entries)
        },
        "recommendations": recommendations
    }


# ========== Multiplayer AI Copilots ==========

@router.post("/copilot/query")
async def copilot_query(data: CopilotQuery, user=Depends(require_auth)):
    """AI Copilot that can cross-reference context from previous meetings."""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        api_key = os.environ.get("EMERGENT_LLM_KEY")
        if not api_key:
            raise HTTPException(500, "LLM key not configured")

        # Gather cross-meeting context
        context_parts = []

        # 1. Current meeting context
        current_summaries = await db.meeting_summaries.find(
            {"meeting_id": data.meeting_id}, {"_id": 0, "summary": 1, "action_items": 1, "key_decisions": 1}
        ).to_list(5)
        if current_summaries:
            context_parts.append("CURRENT MEETING CONTEXT:")
            for s in current_summaries:
                context_parts.append(f"Summary: {s.get('summary', '')[:500]}")
                if s.get("action_items"):
                    context_parts.append(f"Action Items: {', '.join(s['action_items'][:5])}")

        # 2. Past meeting context (if requested)
        if data.include_past_meetings:
            past_summaries = await db.meeting_summaries.find(
                {"meeting_id": {"$ne": data.meeting_id}},
                {"_id": 0, "meeting_id": 1, "meeting_title": 1, "summary": 1,
                 "action_items": 1, "key_decisions": 1, "created_at": 1}
            ).sort("created_at", -1).limit(data.context_window).to_list(data.context_window)

            if past_summaries:
                context_parts.append("\nPREVIOUS MEETINGS CONTEXT:")
                for ps in past_summaries:
                    context_parts.append(f"Meeting: {ps.get('meeting_title', 'Untitled')} ({ps.get('created_at', '')})")
                    context_parts.append(f"  Summary: {ps.get('summary', '')[:300]}")
                    if ps.get("action_items"):
                        context_parts.append(f"  Pending Actions: {', '.join(ps['action_items'][:3])}")
                    if ps.get("key_decisions"):
                        context_parts.append(f"  Decisions: {', '.join(ps['key_decisions'][:3])}")

        # 3. Shared documents context
        docs = await db.webinar_documents.find(
            {"webinar_id": data.meeting_id},
            {"_id": 0, "name": 1, "privacy_level": 1}
        ).to_list(10)
        if docs:
            context_parts.append(f"\nSHARED DOCUMENTS: {', '.join(d.get('name', '') for d in docs)}")

        context_text = "\n".join(context_parts) if context_parts else "No previous meeting context available."

        chat = LlmChat(
            api_key=api_key,
            session_id=f"copilot-{data.meeting_id}-{user['user_id']}",
            system_message=f"""You are an AI Meeting Copilot for the executive communication platform AI KARAU.
You have access to context from the current and previous meetings. Use this cross-meeting intelligence to provide insightful, actionable answers.

AVAILABLE CONTEXT:
{context_text}

Be concise, professional, and reference specific past decisions or action items when relevant.
If referencing a past meeting, mention which one."""
        )

        response = await chat.send_message(UserMessage(text=data.question))
        response_text = response if isinstance(response, str) else str(response)

        # Store copilot interaction
        await db.copilot_interactions.insert_one({
            "meeting_id": data.meeting_id,
            "user_id": user["user_id"],
            "question": data.question,
            "answer": response_text[:2000],
            "context_meetings_used": len(context_parts),
            "created_at": datetime.now(timezone.utc).isoformat()
        })

        return {
            "answer": response_text,
            "context_sources": len(context_parts),
            "past_meetings_referenced": data.context_window if data.include_past_meetings else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Copilot error: {e}")
        raise HTTPException(500, f"Copilot query failed: {str(e)}")


@router.get("/copilot/history/{meeting_id}")
async def get_copilot_history(meeting_id: str, user=Depends(require_auth)):
    """Get copilot interaction history for the current meeting."""
    interactions = await db.copilot_interactions.find(
        {"meeting_id": meeting_id},
        {"_id": 0, "question": 1, "answer": 1, "user_id": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(20)

    return {"interactions": interactions}
