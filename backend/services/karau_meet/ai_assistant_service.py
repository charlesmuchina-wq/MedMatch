"""
AI Meeting Assistant - Full-featured AI agent that provides
real-time insights, answers questions, generates summaries,
extracts action items, and offers smart follow-ups during meetings.
"""
import os
import json
import asyncio
from datetime import datetime, timezone
from typing import Optional, List
from utils.config import EMERGENT_LLM_KEY
from utils.database import db


# ===== Conversation History Store (in-memory, per meeting) =====
_conversation_histories = {}

def _get_history(meeting_id: str) -> list:
    if meeting_id not in _conversation_histories:
        _conversation_histories[meeting_id] = []
    return _conversation_histories[meeting_id]

def _add_to_history(meeting_id: str, role: str, content: str):
    hist = _get_history(meeting_id)
    hist.append({"role": role, "content": content})
    if len(hist) > 20:
        _conversation_histories[meeting_id] = hist[-20:]


def _make_chat(session_id: str, system_message: str):
    """Create LlmChat with the current API."""
    from emergentintegrations.llm.chat import LlmChat
    return LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o-mini")


async def process_transcript_segment(meeting_id: str, segment: str, speaker: str = "Unknown") -> dict:
    """Process a transcript segment and extract insights."""
    if not EMERGENT_LLM_KEY or not segment.strip():
        return {}

    try:
        from emergentintegrations.llm.chat import UserMessage

        chat = _make_chat(
            f"segment-{meeting_id}",
            "You are an AI that extracts action items and key points from meeting transcript segments. Always return valid JSON."
        )

        prompt = f"""Analyze this meeting transcript segment and extract any action items or key decisions.
Speaker: {speaker}
Segment: "{segment}"

Return a JSON object with:
- "has_action_item": boolean
- "action_item": string (if has_action_item is true)
- "is_key_point": boolean  
- "key_point": string (if is_key_point is true)
- "topic": string (brief topic label)
- "sentiment": string (one of: "positive", "neutral", "concern")

Return ONLY valid JSON."""

        result = await chat.send_message(
            UserMessage(text=prompt)
        )

        try:
            parsed = json.loads(result.strip().strip("```json").strip("```"))
            if parsed.get("has_action_item") and parsed.get("action_item"):
                await db.karau_meetings.update_one(
                    {"meeting_id": meeting_id},
                    {"$push": {"ai_notes": {
                        "type": "action_item",
                        "content": parsed["action_item"],
                        "speaker": speaker,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "auto_generated": True
                    }}}
                )
            if parsed.get("is_key_point") and parsed.get("key_point"):
                await db.karau_meetings.update_one(
                    {"meeting_id": meeting_id},
                    {"$push": {"ai_notes": {
                        "type": "highlight",
                        "content": parsed["key_point"],
                        "speaker": speaker,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "auto_generated": True
                    }}}
                )
            return parsed
        except json.JSONDecodeError:
            return {}
    except Exception as e:
        print(f"AI assistant error: {e}")
        return {}


async def generate_meeting_summary(meeting_id: str) -> Optional[str]:
    """Generate a comprehensive meeting summary."""
    if not EMERGENT_LLM_KEY:
        return None

    meeting = await db.karau_meetings.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not meeting:
        return None

    ai_notes = meeting.get("ai_notes", [])
    highlights = [n["content"] for n in ai_notes if n.get("type") in ("highlight", "transcription")]
    action_items = [n["content"] for n in ai_notes if n.get("type") == "action_item"]

    if not highlights and not action_items:
        return "No content available for summary generation. Enable captions to start capturing meeting content."

    try:
        from emergentintegrations.llm.chat import UserMessage

        context = ""
        if highlights:
            context += "Discussion highlights:\n" + "\n".join(f"- {h}" for h in highlights[-30:])
        if action_items:
            context += "\n\nAction items:\n" + "\n".join(f"- {a}" for a in action_items)

        chat = _make_chat(
            f"summary-{meeting_id}",
            "You are a professional meeting summarizer. Generate clear, concise meeting summaries."
        )

        prompt = f"""Generate a concise meeting summary for "{meeting.get('title', 'Meeting')}".

{context}

Format the summary with:
1. Key Takeaways (3-5 bullet points)
2. Decisions Made
3. Action Items with owners (if identifiable)
4. Next Steps

Keep it concise and professional."""

        result = await chat.send_message(
            UserMessage(text=prompt)
        )

        summary = result.strip()

        await db.karau_meetings.update_one(
            {"meeting_id": meeting_id},
            {"$push": {"ai_notes": {
                "type": "summary",
                "content": summary,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "auto_generated": True
            }}}
        )

        return summary
    except Exception as e:
        print(f"Summary generation error: {e}")
        return None


async def get_ai_answer(meeting_id: str, question: str) -> dict:
    """Answer a question based on meeting context with follow-up suggestions."""
    if not EMERGENT_LLM_KEY:
        return {"answer": "AI assistant is not configured. Please set up the Emergent LLM key.", "follow_up_suggestions": []}

    # Handle general (non-meeting) context
    is_general = meeting_id == "general"
    context_items = []
    meeting_title = "General"

    if not is_general:
        meeting = await db.karau_meetings.find_one({"meeting_id": meeting_id}, {"_id": 0})
        if not meeting:
            return {"answer": "Meeting not found.", "follow_up_suggestions": []}
        meeting_title = meeting.get("title", "Meeting")
        ai_notes = meeting.get("ai_notes", [])
        context_items = [f"[{n.get('type','note')}] {n['content']}" for n in ai_notes if n.get("content")][-25:]

    # Build conversation history context
    conv_history = _get_history(meeting_id)
    history_text = ""
    if conv_history:
        history_text = "\nPrevious conversation:\n" + "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}" for m in conv_history[-6:]
        )

    try:
        from emergentintegrations.llm.chat import UserMessage

        context = "\n".join(f"- {item}" for item in context_items) if context_items else "(No meeting content captured yet)"

        system_msg = f"""You are KARAU AI, an intelligent meeting assistant for the AI KARAU platform.
Context: {meeting_title}
You help users with meetings, scheduling, productivity tips, and platform features.
Always respond in valid JSON with keys "answer" (string) and "follow_up_suggestions" (list of 2 strings).
Be concise but thorough."""

        chat = _make_chat(f"qa-{meeting_id}", system_msg)

        prompt = f"""Meeting context:
{context}
{history_text}

User question: {question}

Respond in JSON format:
{{"answer": "your answer", "follow_up_suggestions": ["suggestion 1", "suggestion 2"]}}"""

        result = await chat.send_message(
            UserMessage(text=prompt)
        )

        # Save conversation
        _add_to_history(meeting_id, "user", question)

        try:
            parsed = json.loads(result.strip().strip("```json").strip("```"))
            answer = parsed.get("answer", result.strip())
            suggestions = parsed.get("follow_up_suggestions", [])
            _add_to_history(meeting_id, "assistant", answer)
            return {"answer": answer, "follow_up_suggestions": suggestions[:3]}
        except json.JSONDecodeError:
            answer = result.strip()
            _add_to_history(meeting_id, "assistant", answer)
            return {"answer": answer, "follow_up_suggestions": []}
    except Exception as e:
        return {"answer": f"Sorry, I couldn't process that: {str(e)}", "follow_up_suggestions": []}


async def get_meeting_insights(meeting_id: str) -> dict:
    """Get a structured overview of meeting insights."""
    meeting = await db.karau_meetings.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not meeting:
        return {"action_items": [], "key_points": [], "topics": [], "total_insights": 0}

    ai_notes = meeting.get("ai_notes", [])
    action_items = [n for n in ai_notes if n.get("type") == "action_item"]
    key_points = [n for n in ai_notes if n.get("type") == "highlight"]
    topics = list(set(n.get("topic", "") for n in ai_notes if n.get("topic")))

    return {
        "action_items": [{"content": a["content"], "speaker": a.get("speaker", "Unknown"), "timestamp": a.get("timestamp")} for a in action_items],
        "key_points": [{"content": k["content"], "speaker": k.get("speaker", "Unknown"), "timestamp": k.get("timestamp")} for k in key_points],
        "topics": topics[:10],
        "total_insights": len(action_items) + len(key_points)
    }
