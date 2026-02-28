"""
AI Meeting Assistant - Background service that automatically generates
notes, action items, and summaries during meetings.
"""
import os
import asyncio
from datetime import datetime, timezone
from typing import Optional
from utils.config import EMERGENT_LLM_KEY
from utils.database import db


async def process_transcript_segment(meeting_id: str, segment: str, speaker: str = "Unknown") -> dict:
    """Process a transcript segment and extract insights."""
    if not EMERGENT_LLM_KEY or not segment.strip():
        return {}

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            model_provider="openai",
            properties={}
        ).with_model("openai", "gpt-4o-mini")

        prompt = f"""Analyze this meeting transcript segment and extract any action items or key decisions.
Speaker: {speaker}
Segment: "{segment}"

Return a JSON object with:
- "has_action_item": boolean
- "action_item": string (if has_action_item is true)
- "is_key_point": boolean  
- "key_point": string (if is_key_point is true)
- "topic": string (brief topic label)

Return ONLY valid JSON."""

        result = await asyncio.to_thread(
            chat.send_message,
            UserMessage(content=prompt)
        )

        import json
        try:
            parsed = json.loads(result.content.strip().strip("```json").strip("```"))
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
        return "No content available for summary generation."

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            model_provider="openai",
            properties={}
        ).with_model("openai", "gpt-4o-mini")

        context = ""
        if highlights:
            context += "Discussion highlights:\n" + "\n".join(f"- {h}" for h in highlights[-30:])
        if action_items:
            context += "\n\nAction items:\n" + "\n".join(f"- {a}" for a in action_items)

        prompt = f"""Generate a concise meeting summary for "{meeting.get('title', 'Meeting')}".

{context}

Format the summary with:
1. Key Takeaways (3-5 bullet points)
2. Decisions Made
3. Action Items with owners (if identifiable)
4. Next Steps

Keep it concise and professional."""

        result = await asyncio.to_thread(
            chat.send_message,
            UserMessage(content=prompt)
        )

        summary = result.content.strip()

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


async def get_ai_answer(meeting_id: str, question: str) -> str:
    """Answer a question based on meeting context."""
    if not EMERGENT_LLM_KEY:
        return "AI assistant is not configured."

    meeting = await db.karau_meetings.find_one({"meeting_id": meeting_id}, {"_id": 0})
    if not meeting:
        return "Meeting not found."

    ai_notes = meeting.get("ai_notes", [])
    context_items = [n["content"] for n in ai_notes if n.get("content")][-20:]

    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage

        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            model_provider="openai",
            properties={}
        ).with_model("openai", "gpt-4o-mini")

        context = "\n".join(f"- {item}" for item in context_items)

        prompt = f"""You are an AI meeting assistant for "{meeting.get('title', 'Meeting')}".
Based on the meeting context below, answer the user's question concisely.

Meeting context:
{context}

User question: {question}

Answer concisely and helpfully."""

        result = await asyncio.to_thread(
            chat.send_message,
            UserMessage(content=prompt)
        )

        return result.content.strip()
    except Exception as e:
        return f"Sorry, I couldn't process that: {str(e)}"
