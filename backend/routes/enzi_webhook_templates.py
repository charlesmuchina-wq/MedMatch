"""
ENZI Webhook Templates
- Pre-configured webhook integrations for GitHub, Jira, CI/CD, Slack-compatible
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import os

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/lumi/automation/webhook-templates", tags=["ENZI Webhook Templates"])

APP_URL = os.environ.get("REACT_APP_BACKEND_URL", "")

WEBHOOK_TEMPLATES = {
    "github": {
        "name": "GitHub",
        "description": "Receive commit, PR, and issue notifications",
        "icon": "github",
        "events": ["push", "pull_request", "issues"],
        "format_help": "Add this URL as a webhook in your GitHub repo Settings → Webhooks",
        "sample_payload": '{"content": "New commit pushed to main", "username": "GitHub Bot"}'
    },
    "jira": {
        "name": "Jira",
        "description": "Receive ticket creation, updates, and status changes",
        "icon": "jira",
        "events": ["issue_created", "issue_updated", "sprint_started"],
        "format_help": "Add this URL in Jira → Settings → System → WebHooks",
        "sample_payload": '{"content": "PROJ-123: Bug fix deployed", "username": "Jira Bot"}'
    },
    "cicd": {
        "name": "CI/CD Pipeline",
        "description": "Build status, deployment, and test result notifications",
        "icon": "cicd",
        "events": ["build_success", "build_failure", "deploy"],
        "format_help": "Add this URL as a webhook in your CI/CD pipeline (GitHub Actions, Jenkins, etc.)",
        "sample_payload": '{"content": "Build #42 passed - deploying to production", "username": "CI Bot"}'
    },
    "slack": {
        "name": "Slack-Compatible",
        "description": "Accept Slack-formatted incoming webhook payloads",
        "icon": "slack",
        "events": ["message"],
        "format_help": "Use Slack incoming webhook format: {\"text\": \"message\"}",
        "sample_payload": '{"text": "Hello from Slack-compatible webhook"}'
    },
    "monitoring": {
        "name": "Monitoring & Alerts",
        "description": "Receive alerts from Datadog, PagerDuty, Grafana, etc.",
        "icon": "alert",
        "events": ["alert_triggered", "alert_resolved"],
        "format_help": "Add this URL as a webhook in your monitoring tool",
        "sample_payload": '{"content": "Alert: CPU usage > 90%", "username": "Monitor Bot"}'
    }
}


@router.get("/list")
async def list_webhook_templates():
    """List available webhook templates"""
    return {
        "templates": [
            {"id": k, **{key: v[key] for key in ["name", "description", "icon", "events", "format_help"]}}
            for k, v in WEBHOOK_TEMPLATES.items()
        ]
    }


class CreateWebhookFromTemplate(BaseModel):
    template_id: str
    channel_id: str


@router.post("/create")
async def create_webhook_from_template(req: CreateWebhookFromTemplate, request: Request):
    """Create a webhook from a template"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    template = WEBHOOK_TEMPLATES.get(req.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    webhook_id = str(uuid.uuid4())
    webhook_token = str(uuid.uuid4())

    await db.enzi_webhooks.insert_one({
        "id": webhook_id,
        "token": webhook_token,
        "channel_id": req.channel_id,
        "name": template["name"],
        "template_id": req.template_id,
        "events": template["events"],
        "created_by": user.get("user_id"),
        "is_active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    })

    webhook_url = f"{APP_URL}/api/lumi/automation/webhooks/{webhook_id}/send"

    return {
        "id": webhook_id,
        "name": template["name"],
        "url": webhook_url,
        "events": template["events"],
        "format_help": template["format_help"],
        "sample_payload": template["sample_payload"],
        "sample_curl": f'curl -X POST "{webhook_url}" -H "Content-Type: application/json" -d \'{template["sample_payload"]}\''
    }
