"""
AI Meeting Notes Service.
Generates structured meeting notes from recording transcripts.
Presenter can send notes to meeting members.
"""
import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")


async def generate_meeting_notes(transcript_text: str, meeting_title: str, participants: list = None) -> dict:
    """Generate AI-powered meeting notes from transcript text."""
    if not transcript_text or not EMERGENT_KEY:
        return {"error": "No transcript or API key", "notes": ""}

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    prompt = f"""Analyze this meeting transcript and generate structured notes.

Meeting: {meeting_title}
Participants: {', '.join(participants or ['Unknown'])}

Transcript:
{transcript_text[:8000]}

Generate:
1. **Summary** (2-3 sentences)
2. **Key Discussion Points** (bullet points)
3. **Action Items** (with assignee if identifiable)
4. **Decisions Made**
5. **Follow-up Items**

Format as clean markdown."""

    try:
        chat = LlmChat(
            api_key=EMERGENT_KEY,
            session_id=f'notes-{datetime.now().strftime("%Y%m%d%H%M")}',
            system_message='You are a professional meeting notes assistant. Generate clear, actionable meeting notes in markdown format.'
        ).with_model('openai', 'gpt-4o-mini')

        response = await chat.send_message(UserMessage(text=prompt))
        notes_text = response if isinstance(response, str) else str(response)

        return {
            "notes": notes_text,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "meeting_title": meeting_title,
            "word_count": len(notes_text.split())
        }
    except Exception as e:
        logger.error(f"Meeting notes generation failed: {e}")
        return {"error": str(e), "notes": ""}
