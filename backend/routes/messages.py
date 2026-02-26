"""
Messaging Routes
Handles: In-app messaging between recruiters and job seekers
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

from utils.database import db
from routes.auth import get_current_user, require_auth
from utils.push_service import notify_new_message

router = APIRouter(prefix="/messages", tags=["Messaging"])

# ============== Models ==============

class MessageCreate(BaseModel):
    recipient_id: str
    subject: Optional[str] = None
    content: str
    job_id: Optional[str] = None

# ============== Routes ==============

@router.post("/send")
async def send_message(message: MessageCreate, request: Request, background_tasks: BackgroundTasks):
    """Send a message to another user"""
    user = await require_auth(request)
    
    # Verify recipient exists
    recipient = await db.users.find_one({"user_id": message.recipient_id}, {"_id": 0})
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Create or find existing conversation
    conversation_participants = sorted([user["user_id"], message.recipient_id])
    conversation_key = f"conv_{'_'.join(conversation_participants)}"
    
    existing_conv = await db.conversations.find_one({"conversation_key": conversation_key})
    
    if not existing_conv:
        # Create new conversation
        conversation = {
            "id": f"conv_{uuid.uuid4().hex[:12]}",
            "conversation_key": conversation_key,
            "participants": [
                {"user_id": user["user_id"], "name": user.get("name", ""), "email": user["email"]},
                {"user_id": recipient["user_id"], "name": recipient.get("name", ""), "email": recipient["email"]}
            ],
            "job_id": message.job_id,
            "subject": message.subject,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_message_at": datetime.now(timezone.utc).isoformat(),
            "unread_count": {message.recipient_id: 1, user["user_id"]: 0}
        }
        await db.conversations.insert_one(conversation)
        conv_id = conversation["id"]
    else:
        conv_id = existing_conv["id"]
        # Update unread count for recipient
        await db.conversations.update_one(
            {"id": conv_id},
            {
                "$inc": {f"unread_count.{message.recipient_id}": 1},
                "$set": {"last_message_at": datetime.now(timezone.utc).isoformat()}
            }
        )
    
    # Create the message
    msg = {
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "conversation_id": conv_id,
        "sender_id": user["user_id"],
        "sender_name": user.get("name", user["email"]),
        "recipient_id": message.recipient_id,
        "content": message.content,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "read": False
    }
    
    await db.messages.insert_one(msg)
    
    # Send push notification to recipient in background
    background_tasks.add_task(
        notify_new_message,
        user_id=message.recipient_id,
        sender_name=user.get("name", user["email"]),
        preview=message.content[:100],
        conversation_id=conv_id
    )
    
    return {"message": "Message sent", "message_id": msg["id"], "conversation_id": conv_id}

@router.get("/conversations")
async def get_conversations(request: Request):
    """Get all conversations for current user"""
    user = await require_auth(request)
    
    # Find all conversations where user is a participant
    conversations = await db.conversations.find(
        {"participants.user_id": user["user_id"]},
        {"_id": 0}
    ).sort("last_message_at", -1).to_list(100)
    
    # Get the last message for each conversation
    for conv in conversations:
        last_msg = await db.messages.find_one(
            {"conversation_id": conv["id"]},
            {"_id": 0}
        )
        conv["last_message"] = last_msg
        conv["unread"] = conv.get("unread_count", {}).get(user["user_id"], 0)
    
    return conversations

@router.get("/conversations/{conversation_id}")
async def get_conversation_messages(conversation_id: str, request: Request):
    """Get all messages in a conversation"""
    user = await require_auth(request)
    
    # Verify user is part of this conversation
    conversation = await db.conversations.find_one({
        "id": conversation_id,
        "participants.user_id": user["user_id"]
    }, {"_id": 0})
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    messages = await db.messages.find(
        {"conversation_id": conversation_id},
        {"_id": 0}
    ).sort("sent_at", 1).to_list(500)
    
    # Mark messages as read
    await db.messages.update_many(
        {"conversation_id": conversation_id, "recipient_id": user["user_id"], "read": False},
        {"$set": {"read": True}}
    )
    
    # Reset unread count
    await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {f"unread_count.{user['user_id']}": 0}}
    )
    
    return {
        "conversation": conversation,
        "messages": messages
    }

@router.get("/unread-count")
async def get_unread_count(request: Request):
    """Get total unread message count for current user"""
    user = await require_auth(request)
    
    # Count unread messages
    count = await db.messages.count_documents({
        "recipient_id": user["user_id"],
        "read": False
    })
    
    return {"unread_count": count}
