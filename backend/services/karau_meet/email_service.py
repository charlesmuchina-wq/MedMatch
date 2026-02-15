"""
AI KARAU Meeting - Email Service using Resend
Sends verification codes, meeting invites, and notifications
"""

import os
import asyncio
import logging
import resend
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize Resend with API key
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "onboarding@resend.dev")

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
    logger.info("Resend email service initialized")
else:
    logger.warning("RESEND_API_KEY not configured - emails will be mocked")


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: Optional[str] = None
) -> dict:
    """
    Send an email using Resend API
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML email body
        from_email: Optional sender email (defaults to SENDER_EMAIL)
    
    Returns:
        dict with success status and email_id or error
    """
    if not RESEND_API_KEY:
        logger.warning(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
        return {
            "success": True,
            "mock_mode": True,
            "message": f"Email would be sent to {to_email}"
        }
    
    params = {
        "from": from_email or SENDER_EMAIL,
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    try:
        # Run sync SDK in thread to keep FastAPI non-blocking
        email = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Email sent to {to_email}: {email.get('id')}")
        return {
            "success": True,
            "email_id": email.get("id"),
            "message": f"Email sent to {to_email}"
        }
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def send_verification_code(
    to_email: str,
    code: str,
    user_name: str = "User"
) -> dict:
    """Send a verification code email"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; margin: 0; padding: 40px 20px;">
        <div style="max-width: 480px; margin: 0 auto; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; border: 1px solid #334155; overflow: hidden;">
            <!-- Header -->
            <div style="background: linear-gradient(90deg, #14b8a6 0%, #06b6d4 100%); padding: 24px; text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700;">AI KARAU Meeting</h1>
                <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">The Meeting Place</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px;">
                <p style="color: #e2e8f0; font-size: 16px; margin: 0 0 16px;">Hi {user_name},</p>
                <p style="color: #94a3b8; font-size: 14px; line-height: 1.6; margin: 0 0 24px;">
                    Your verification code for AI KARAU Meeting is:
                </p>
                
                <!-- Code Box -->
                <div style="background: #0f172a; border: 2px solid #14b8a6; border-radius: 12px; padding: 24px; text-align: center; margin: 0 0 24px;">
                    <span style="font-family: 'Courier New', monospace; font-size: 36px; font-weight: 700; letter-spacing: 8px; color: #14b8a6;">
                        {code}
                    </span>
                </div>
                
                <p style="color: #94a3b8; font-size: 13px; line-height: 1.6; margin: 0 0 8px;">
                    This code expires in <strong style="color: #e2e8f0;">10 minutes</strong>.
                </p>
                <p style="color: #64748b; font-size: 12px; line-height: 1.6; margin: 0;">
                    If you didn't request this code, you can safely ignore this email.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background: #1e293b; padding: 20px; text-align: center; border-top: 1px solid #334155;">
                <p style="color: #64748b; font-size: 12px; margin: 0;">
                    Secure • AI-Powered • E2E Encrypted
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=to_email,
        subject=f"Your AI KARAU verification code: {code}",
        html_content=html_content
    )


async def send_meeting_invite(
    to_email: str,
    meeting_title: str,
    meeting_id: str,
    meeting_url: str,
    host_name: str,
    scheduled_time: Optional[str] = None
) -> dict:
    """Send a meeting invitation email"""
    
    time_section = ""
    if scheduled_time:
        time_section = f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #334155;">
                <span style="color: #64748b; font-size: 13px;">Scheduled for:</span>
                <div style="color: #e2e8f0; font-size: 15px; margin-top: 4px;">{scheduled_time}</div>
            </td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; margin: 0; padding: 40px 20px;">
        <div style="max-width: 480px; margin: 0 auto; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; border: 1px solid #334155; overflow: hidden;">
            <!-- Header -->
            <div style="background: linear-gradient(90deg, #8b5cf6 0%, #a855f7 100%); padding: 24px; text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700;">Meeting Invitation</h1>
                <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">AI KARAU Meeting</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px;">
                <p style="color: #e2e8f0; font-size: 16px; margin: 0 0 24px;">
                    <strong>{host_name}</strong> has invited you to a meeting.
                </p>
                
                <!-- Meeting Details -->
                <table style="width: 100%; border-collapse: collapse; margin: 0 0 24px;">
                    <tr>
                        <td style="padding: 12px 0; border-bottom: 1px solid #334155;">
                            <span style="color: #64748b; font-size: 13px;">Meeting:</span>
                            <div style="color: #e2e8f0; font-size: 15px; font-weight: 600; margin-top: 4px;">{meeting_title}</div>
                        </td>
                    </tr>
                    {time_section}
                    <tr>
                        <td style="padding: 12px 0;">
                            <span style="color: #64748b; font-size: 13px;">Meeting ID:</span>
                            <div style="color: #14b8a6; font-size: 15px; font-family: monospace; margin-top: 4px;">{meeting_id}</div>
                        </td>
                    </tr>
                </table>
                
                <!-- Join Button -->
                <a href="{meeting_url}" style="display: block; background: linear-gradient(90deg, #14b8a6 0%, #06b6d4 100%); color: white; text-decoration: none; text-align: center; padding: 16px 24px; border-radius: 12px; font-size: 16px; font-weight: 600;">
                    Join Meeting
                </a>
            </div>
            
            <!-- Footer -->
            <div style="background: #1e293b; padding: 20px; text-align: center; border-top: 1px solid #334155;">
                <p style="color: #64748b; font-size: 12px; margin: 0;">
                    Secure • AI-Powered • E2E Encrypted
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=to_email,
        subject=f"Meeting Invitation: {meeting_title}",
        html_content=html_content
    )


async def send_meeting_summary(
    to_email: str,
    meeting_title: str,
    summary: str,
    key_points: list,
    action_items: list,
    user_name: str = "User"
) -> dict:
    """Send meeting summary email after a meeting ends"""
    
    key_points_html = ""
    if key_points:
        points_list = "".join([f'<li style="color: #e2e8f0; margin-bottom: 8px;">{point}</li>' for point in key_points[:5]])
        key_points_html = f"""
        <div style="margin: 24px 0;">
            <h3 style="color: #14b8a6; font-size: 14px; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px;">Key Points</h3>
            <ul style="margin: 0; padding-left: 20px;">{points_list}</ul>
        </div>
        """
    
    action_items_html = ""
    if action_items:
        items_list = "".join([
            f'<li style="color: #e2e8f0; margin-bottom: 8px;"><strong>{item.get("task", "Task")}</strong> - {item.get("assignee", "TBD")}</li>'
            for item in action_items[:5]
        ])
        action_items_html = f"""
        <div style="margin: 24px 0;">
            <h3 style="color: #f59e0b; font-size: 14px; margin: 0 0 12px; text-transform: uppercase; letter-spacing: 1px;">Action Items</h3>
            <ul style="margin: 0; padding-left: 20px;">{items_list}</ul>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; margin: 0; padding: 40px 20px;">
        <div style="max-width: 560px; margin: 0 auto; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border-radius: 16px; border: 1px solid #334155; overflow: hidden;">
            <!-- Header -->
            <div style="background: linear-gradient(90deg, #14b8a6 0%, #06b6d4 100%); padding: 24px; text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 700;">Meeting Summary</h1>
                <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 14px;">{meeting_title}</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px;">
                <p style="color: #e2e8f0; font-size: 16px; margin: 0 0 16px;">Hi {user_name},</p>
                <p style="color: #94a3b8; font-size: 14px; line-height: 1.6; margin: 0 0 24px;">
                    Here's the AI-generated summary of your meeting:
                </p>
                
                <!-- Summary -->
                <div style="background: #0f172a; border-left: 4px solid #14b8a6; padding: 16px; border-radius: 0 8px 8px 0; margin: 0 0 24px;">
                    <p style="color: #e2e8f0; font-size: 14px; line-height: 1.7; margin: 0;">
                        {summary[:500]}{'...' if len(summary) > 500 else ''}
                    </p>
                </div>
                
                {key_points_html}
                {action_items_html}
            </div>
            
            <!-- Footer -->
            <div style="background: #1e293b; padding: 20px; text-align: center; border-top: 1px solid #334155;">
                <p style="color: #64748b; font-size: 12px; margin: 0;">
                    Generated by AI KARAU Meeting • Powered by AI
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=to_email,
        subject=f"Meeting Summary: {meeting_title}",
        html_content=html_content
    )
