"""
Interactive Challenges & Polls API
In-meeting polls, timed quizzes, word clouds, leaderboard integration.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import logging

from utils.database import db
from routes.auth import require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/karau/polls", tags=["Polls & Challenges"])


class PollOption(BaseModel):
    text: str
    id: Optional[str] = None


class PollCreate(BaseModel):
    meeting_id: str
    question: str
    poll_type: str = "multiple_choice"  # multiple_choice, word_cloud, rating, quiz
    options: List[PollOption] = []
    correct_answer_id: Optional[str] = None  # for quiz type
    time_limit_seconds: int = 0  # 0 = unlimited
    anonymous: bool = False
    points: int = 5  # leaderboard points for participation


class VoteRequest(BaseModel):
    option_id: Optional[str] = None
    text_response: Optional[str] = None
    rating: Optional[int] = None


@router.post("/create")
async def create_poll(data: PollCreate, user=Depends(require_auth)):
    """Create a new poll or challenge."""
    now = datetime.now(timezone.utc).isoformat()
    poll_id = f"poll-{int(datetime.now(timezone.utc).timestamp() * 1000) % 100000}"

    options = []
    for i, opt in enumerate(data.options):
        options.append({
            "id": opt.id or f"opt-{i}",
            "text": opt.text,
            "votes": 0,
            "voters": []
        })

    doc = {
        "poll_id": poll_id,
        "meeting_id": data.meeting_id,
        "question": data.question,
        "poll_type": data.poll_type,
        "options": options,
        "correct_answer_id": data.correct_answer_id,
        "time_limit_seconds": data.time_limit_seconds,
        "anonymous": data.anonymous,
        "points": data.points,
        "created_by": user["user_id"],
        "created_at": now,
        "status": "active",
        "total_votes": 0,
        "word_cloud_responses": [],
        "ratings": []
    }

    if data.time_limit_seconds > 0:
        from datetime import timedelta
        doc["expires_at"] = (datetime.now(timezone.utc) + timedelta(seconds=data.time_limit_seconds)).isoformat()

    await db.meeting_polls.insert_one(doc)

    return {"success": True, "poll_id": poll_id, "question": data.question, "poll_type": data.poll_type}


@router.get("/{meeting_id}/active")
async def get_active_polls(meeting_id: str, user=Depends(require_auth)):
    """Get all active polls for a meeting."""
    polls = await db.meeting_polls.find(
        {"meeting_id": meeting_id, "status": "active"},
        {"_id": 0}
    ).sort("created_at", -1).to_list(20)

    # Strip voter identities if anonymous
    for p in polls:
        if p.get("anonymous"):
            for opt in p.get("options", []):
                opt["voters"] = []

    return {"meeting_id": meeting_id, "polls": polls}


@router.post("/{poll_id}/vote")
async def vote_on_poll(poll_id: str, data: VoteRequest, user=Depends(require_auth)):
    """Cast a vote on a poll."""
    poll = await db.meeting_polls.find_one({"poll_id": poll_id}, {"_id": 0})
    if not poll:
        raise HTTPException(404, "Poll not found")
    if poll.get("status") != "active":
        raise HTTPException(410, "Poll is closed")

    # Check expiry
    if poll.get("expires_at"):
        try:
            exp = datetime.fromisoformat(poll["expires_at"].replace('Z', '+00:00'))
            if exp < datetime.now(timezone.utc):
                await db.meeting_polls.update_one({"poll_id": poll_id}, {"$set": {"status": "expired"}})
                raise HTTPException(410, "Poll has expired")
        except (ValueError, TypeError):
            pass

    user_id = user["user_id"]
    user_name = user.get("name", user.get("email", "User"))
    now = datetime.now(timezone.utc).isoformat()
    is_correct = False
    points_earned = 0

    if poll["poll_type"] == "multiple_choice" or poll["poll_type"] == "quiz":
        if not data.option_id:
            raise HTTPException(400, "option_id required")

        # Check if already voted
        for opt in poll.get("options", []):
            if user_id in opt.get("voters", []):
                raise HTTPException(409, "Already voted")

        # Record vote
        await db.meeting_polls.update_one(
            {"poll_id": poll_id, "options.id": data.option_id},
            {"$inc": {"options.$.votes": 1, "total_votes": 1},
             "$push": {"options.$.voters": user_id}}
        )

        # Quiz scoring
        if poll["poll_type"] == "quiz" and poll.get("correct_answer_id"):
            is_correct = data.option_id == poll["correct_answer_id"]
            if is_correct:
                points_earned = poll.get("points", 5)

    elif poll["poll_type"] == "word_cloud":
        if not data.text_response:
            raise HTTPException(400, "text_response required")

        await db.meeting_polls.update_one(
            {"poll_id": poll_id},
            {"$push": {"word_cloud_responses": {
                "user_id": user_id, "text": data.text_response, "ts": now
            }}, "$inc": {"total_votes": 1}}
        )
        points_earned = poll.get("points", 5)

    elif poll["poll_type"] == "rating":
        if data.rating is None:
            raise HTTPException(400, "rating required (1-10)")

        await db.meeting_polls.update_one(
            {"poll_id": poll_id},
            {"$push": {"ratings": {
                "user_id": user_id, "rating": data.rating, "ts": now
            }}, "$inc": {"total_votes": 1}}
        )
        points_earned = poll.get("points", 5)

    # Award leaderboard points
    if points_earned > 0:
        await db.leaderboard.update_one(
            {"webinar_id": poll["meeting_id"], "user_id": user_id},
            {"$inc": {"polls": points_earned},
             "$set": {"user_name": user_name, "updated_at": now}},
            upsert=True
        )

    return {
        "success": True,
        "poll_id": poll_id,
        "is_correct": is_correct if poll["poll_type"] == "quiz" else None,
        "points_earned": points_earned
    }


@router.get("/{poll_id}/results")
async def get_poll_results(poll_id: str, user=Depends(require_auth)):
    """Get detailed results for a poll."""
    poll = await db.meeting_polls.find_one({"poll_id": poll_id}, {"_id": 0})
    if not poll:
        raise HTTPException(404, "Poll not found")

    results = {
        "poll_id": poll_id,
        "question": poll["question"],
        "poll_type": poll["poll_type"],
        "total_votes": poll.get("total_votes", 0),
        "status": poll.get("status", "active")
    }

    if poll["poll_type"] in ("multiple_choice", "quiz"):
        options = poll.get("options", [])
        total = max(poll.get("total_votes", 0), 1)
        results["options"] = [{
            "id": o["id"], "text": o["text"],
            "votes": o["votes"],
            "percentage": round(o["votes"] / total * 100, 1)
        } for o in options]
        if poll["poll_type"] == "quiz":
            results["correct_answer_id"] = poll.get("correct_answer_id")

    elif poll["poll_type"] == "word_cloud":
        responses = poll.get("word_cloud_responses", [])
        # Build word frequency
        words = {}
        for r in responses:
            for word in r.get("text", "").lower().split():
                word = word.strip(".,!?;:")
                if len(word) > 2:
                    words[word] = words.get(word, 0) + 1
        results["word_cloud"] = sorted(
            [{"word": w, "count": c} for w, c in words.items()],
            key=lambda x: -x["count"]
        )[:30]
        results["responses"] = len(responses)

    elif poll["poll_type"] == "rating":
        ratings = poll.get("ratings", [])
        if ratings:
            vals = [r["rating"] for r in ratings]
            results["average_rating"] = round(sum(vals) / len(vals), 1)
            results["rating_count"] = len(vals)
            results["distribution"] = {i: vals.count(i) for i in range(1, 11)}
        else:
            results["average_rating"] = 0
            results["rating_count"] = 0

    return results


@router.post("/{poll_id}/close")
async def close_poll(poll_id: str, user=Depends(require_auth)):
    """Close a poll."""
    await db.meeting_polls.update_one(
        {"poll_id": poll_id}, {"$set": {"status": "closed"}}
    )
    return {"success": True, "poll_id": poll_id, "status": "closed"}


@router.get("/{meeting_id}/history")
async def get_poll_history(meeting_id: str, user=Depends(require_auth)):
    """Get all polls (active and closed) for a meeting."""
    polls = await db.meeting_polls.find(
        {"meeting_id": meeting_id},
        {"_id": 0, "poll_id": 1, "question": 1, "poll_type": 1,
         "total_votes": 1, "status": 1, "created_at": 1}
    ).sort("created_at", -1).to_list(50)
    return {"polls": polls}
