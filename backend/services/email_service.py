"""
Email Notification Service
Handles email notifications to job seekers for application status updates
Can be configured with SendGrid, Resend, or SMTP
"""
import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from utils.database import db

logger = logging.getLogger(__name__)

# Email configuration - can be set via environment variables
EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "mock")  # mock, sendgrid, resend, smtp
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = os.environ.get("SMTP_PORT", "587")
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "noreply@medmatch.com")
FROM_NAME = os.environ.get("FROM_NAME", "MedMatch")

# Application status configurations
APPLICATION_STATUSES = {
    "received": {
        "label": "Application Received",
        "emoji": "📩",
        "description": "Your application has been received and is being processed.",
        "color": "#3B82F6"  # Blue
    },
    "under_review": {
        "label": "Under Review",
        "emoji": "👀",
        "description": "The hiring team is currently reviewing your application.",
        "color": "#8B5CF6"  # Purple
    },
    "shortlisted": {
        "label": "Shortlisted",
        "emoji": "⭐",
        "description": "Congratulations! You've been shortlisted for this position.",
        "color": "#10B981"  # Green
    },
    "interview_scheduled": {
        "label": "Interview Scheduled",
        "emoji": "📅",
        "description": "An interview has been scheduled. Please check the details below.",
        "color": "#F59E0B"  # Amber
    },
    "interview_completed": {
        "label": "Interview Completed",
        "emoji": "✅",
        "description": "Thank you for completing your interview. We'll be in touch soon.",
        "color": "#6366F1"  # Indigo
    },
    "offer_extended": {
        "label": "Offer Extended",
        "emoji": "🎉",
        "description": "Congratulations! An offer has been extended to you.",
        "color": "#22C55E"  # Bright Green
    },
    "hired": {
        "label": "Hired",
        "emoji": "🏆",
        "description": "Welcome aboard! You've been officially hired.",
        "color": "#14B8A6"  # Teal
    },
    "application_deferred": {
        "label": "Application Deferred",
        "emoji": "⏸️",
        "description": "Your application has been deferred for future consideration.",
        "color": "#F97316"  # Orange
    },
    "not_selected": {
        "label": "Not Selected",
        "emoji": "📋",
        "description": "After careful consideration, we've decided not to move forward at this time.",
        "color": "#64748B"  # Slate
    },
    "position_closed": {
        "label": "Position Closed",
        "emoji": "🔒",
        "description": "This position has been closed. Thank you for your interest.",
        "color": "#94A3B8"  # Light Slate
    },
    "withdrawn": {
        "label": "Withdrawn",
        "emoji": "↩️",
        "description": "Your application has been withdrawn as requested.",
        "color": "#6B7280"  # Gray
    }
}

def get_email_template(
    candidate_name: str,
    job_title: str,
    company_name: str,
    status: str,
    recruiter_message: Optional[str] = None,
    interview_details: Optional[Dict] = None,
    application_link: Optional[str] = None
) -> Dict[str, str]:
    """Generate HTML and text email templates for application status updates"""
    
    status_config = APPLICATION_STATUSES.get(status, APPLICATION_STATUSES["received"])
    
    # Interview details section
    interview_html = ""
    interview_text = ""
    if interview_details:
        interview_html = f"""
        <div style="background-color: #F3F4F6; border-radius: 8px; padding: 16px; margin: 16px 0;">
            <h3 style="margin: 0 0 12px 0; color: #1F2937;">📅 Interview Details</h3>
            <p style="margin: 4px 0;"><strong>Date:</strong> {interview_details.get('date', 'TBD')}</p>
            <p style="margin: 4px 0;"><strong>Time:</strong> {interview_details.get('time', 'TBD')}</p>
            <p style="margin: 4px 0;"><strong>Type:</strong> {interview_details.get('type', 'Video Call')}</p>
            {f'<p style="margin: 4px 0;"><strong>Location/Link:</strong> {interview_details.get("location", "")}</p>' if interview_details.get('location') else ''}
        </div>
        """
        interview_text = f"""
Interview Details:
- Date: {interview_details.get('date', 'TBD')}
- Time: {interview_details.get('time', 'TBD')}
- Type: {interview_details.get('type', 'Video Call')}
{f"- Location/Link: {interview_details.get('location', '')}" if interview_details.get('location') else ''}
"""
    
    # Recruiter message section
    message_html = ""
    message_text = ""
    if recruiter_message:
        message_html = f"""
        <div style="background-color: #FEF3C7; border-left: 4px solid #F59E0B; padding: 12px 16px; margin: 16px 0;">
            <p style="margin: 0; color: #92400E;"><strong>Message from Recruiter:</strong></p>
            <p style="margin: 8px 0 0 0; color: #78350F;">{recruiter_message}</p>
        </div>
        """
        message_text = f"\n\nMessage from Recruiter:\n{recruiter_message}\n"
    
    # Application tracking link
    tracking_html = ""
    tracking_text = ""
    if application_link:
        tracking_html = f"""
        <div style="text-align: center; margin: 24px 0;">
            <a href="{application_link}" style="background-color: #00CED1; color: white; padding: 12px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; display: inline-block;">
                View Application Status
            </a>
        </div>
        """
        tracking_text = f"\n\nTrack your application: {application_link}\n"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #F9FAFB; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #00CED1, #008B8B); padding: 32px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">MedMatch</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0;">Application Status Update</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px;">
                <p style="color: #374151; font-size: 16px; margin: 0 0 24px 0;">
                    Hi {candidate_name},
                </p>
                
                <!-- Status Badge -->
                <div style="background-color: {status_config['color']}15; border: 2px solid {status_config['color']}; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 24px;">
                    <div style="font-size: 48px; margin-bottom: 8px;">{status_config['emoji']}</div>
                    <h2 style="color: {status_config['color']}; margin: 0; font-size: 20px;">{status_config['label']}</h2>
                </div>
                
                <p style="color: #4B5563; font-size: 15px; line-height: 1.6;">
                    {status_config['description']}
                </p>
                
                <!-- Job Details -->
                <div style="background-color: #F9FAFB; border-radius: 8px; padding: 16px; margin: 16px 0;">
                    <p style="margin: 0; color: #6B7280; font-size: 14px;">Position Applied For:</p>
                    <p style="margin: 4px 0 0 0; color: #1F2937; font-size: 18px; font-weight: 600;">{job_title}</p>
                    <p style="margin: 4px 0 0 0; color: #6B7280; font-size: 14px;">at {company_name}</p>
                </div>
                
                {interview_html}
                {message_html}
                {tracking_html}
                
                <p style="color: #6B7280; font-size: 14px; margin-top: 24px;">
                    If you have any questions, please don't hesitate to reach out through our platform.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #F9FAFB; padding: 24px; text-align: center; border-top: 1px solid #E5E7EB;">
                <p style="color: #9CA3AF; font-size: 12px; margin: 0;">
                    © {datetime.now().year} MedMatch. All rights reserved.
                </p>
                <p style="color: #9CA3AF; font-size: 12px; margin: 8px 0 0 0;">
                    Life Sciences & Engineering Talent Ecosystem
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
Hi {candidate_name},

{status_config['emoji']} {status_config['label']}

{status_config['description']}

Position: {job_title}
Company: {company_name}
{interview_text}
{message_text}
{tracking_text}

If you have any questions, please don't hesitate to reach out through our platform.

Best regards,
The MedMatch Team

© {datetime.now().year} MedMatch - Life Sciences & Engineering Talent Ecosystem
    """
    
    return {
        "subject": f"{status_config['emoji']} Application Update: {status_config['label']} - {job_title}",
        "html": html_content,
        "text": text_content
    }


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str
) -> Dict[str, Any]:
    """
    Send email using configured provider
    Returns dict with success status and details
    """
    result = {
        "success": False,
        "provider": EMAIL_PROVIDER,
        "to": to_email,
        "subject": subject,
        "sent_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        if EMAIL_PROVIDER == "mock":
            # Mock provider - log and store in database for testing
            logger.info(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            await db.email_logs.insert_one({
                "to": to_email,
                "subject": subject,
                "html": html_content,
                "text": text_content,
                "provider": "mock",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "status": "delivered"
            })
            result["success"] = True
            result["message"] = "Email logged (mock mode)"
            
        elif EMAIL_PROVIDER == "sendgrid" and SENDGRID_API_KEY:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
            message = Mail(
                from_email=Email(FROM_EMAIL, FROM_NAME),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            response = sg.send(message)
            result["success"] = response.status_code in [200, 202]
            result["status_code"] = response.status_code
            
        elif EMAIL_PROVIDER == "resend" and RESEND_API_KEY:
            import resend
            resend.api_key = RESEND_API_KEY
            
            response = resend.Emails.send({
                "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            })
            result["success"] = True
            result["email_id"] = response.get("id")
            
        elif EMAIL_PROVIDER == "smtp":
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg["To"] = to_email
            
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(SMTP_HOST, int(SMTP_PORT)) as server:
                server.starttls()
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, to_email, msg.as_string())
            
            result["success"] = True
            
        else:
            result["message"] = f"Email provider '{EMAIL_PROVIDER}' not configured"
            logger.warning(result["message"])
            
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        result["error"] = str(e)
    
    # Log all email attempts
    await db.email_logs.insert_one({
        **result,
        "logged_at": datetime.now(timezone.utc).isoformat()
    })
    
    return result


async def send_application_status_email(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company_name: str,
    status: str,
    recruiter_message: Optional[str] = None,
    interview_details: Optional[Dict] = None,
    application_id: Optional[str] = None,
    tracking_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send application status update email to candidate
    """
    # Generate application tracking link if token provided
    app_url = os.environ.get("APP_URL", "https://liquid-glass-chat-5.preview.emergentagent.com")
    application_link = None
    if application_id and tracking_token:
        application_link = f"{app_url}/track-application/{application_id}?token={tracking_token}"
    elif application_id:
        application_link = f"{app_url}/applications/{application_id}"
    
    # Generate email content
    email_content = get_email_template(
        candidate_name=candidate_name,
        job_title=job_title,
        company_name=company_name,
        status=status,
        recruiter_message=recruiter_message,
        interview_details=interview_details,
        application_link=application_link
    )
    
    # Send the email
    return await send_email(
        to_email=candidate_email,
        subject=email_content["subject"],
        html_content=email_content["html"],
        text_content=email_content["text"]
    )


async def send_application_invitation_email(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company_name: str,
    recruiter_name: str,
    application_link: str,
    personal_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send invitation email to job seeker to apply for a position
    """
    message_html = ""
    message_text = ""
    if personal_message:
        message_html = f"""
        <div style="background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; margin: 16px 0;">
            <p style="margin: 0; color: #1E40AF;"><strong>Personal Message from {recruiter_name}:</strong></p>
            <p style="margin: 8px 0 0 0; color: #1E3A8A;">{personal_message}</p>
        </div>
        """
        message_text = f"\n\nPersonal Message from {recruiter_name}:\n{personal_message}\n"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #F9FAFB; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #00CED1, #008B8B); padding: 32px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px;">MedMatch</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0;">You've Been Invited to Apply!</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 32px;">
                <p style="color: #374151; font-size: 16px; margin: 0 0 24px 0;">
                    Hi {candidate_name or 'there'},
                </p>
                
                <!-- Invitation Banner -->
                <div style="background: linear-gradient(135deg, #00CED1, #20B2AA); border-radius: 12px; padding: 24px; text-align: center; margin-bottom: 24px;">
                    <div style="font-size: 48px; margin-bottom: 8px;">🎯</div>
                    <h2 style="color: white; margin: 0; font-size: 20px;">You're Invited!</h2>
                    <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0;">A recruiter thinks you'd be a great fit</p>
                </div>
                
                <p style="color: #4B5563; font-size: 15px; line-height: 1.6;">
                    {recruiter_name} from <strong>{company_name}</strong> has invited you to apply for the following position:
                </p>
                
                <!-- Job Details -->
                <div style="background-color: #F9FAFB; border-radius: 8px; padding: 20px; margin: 16px 0; text-align: center;">
                    <p style="margin: 0; color: #6B7280; font-size: 14px;">Position</p>
                    <p style="margin: 8px 0 0 0; color: #1F2937; font-size: 22px; font-weight: 700;">{job_title}</p>
                    <p style="margin: 8px 0 0 0; color: #00CED1; font-size: 16px; font-weight: 500;">{company_name}</p>
                </div>
                
                {message_html}
                
                <!-- Apply Button -->
                <div style="text-align: center; margin: 32px 0;">
                    <a href="{application_link}" style="background-color: #00CED1; color: white; padding: 16px 48px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px rgba(0, 206, 209, 0.3);">
                        Apply Now
                    </a>
                </div>
                
                <p style="color: #6B7280; font-size: 14px; text-align: center;">
                    This link will take you directly to the application form on MedMatch.
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #F9FAFB; padding: 24px; text-align: center; border-top: 1px solid #E5E7EB;">
                <p style="color: #9CA3AF; font-size: 12px; margin: 0;">
                    © {datetime.now().year} MedMatch. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
Hi {candidate_name or 'there'},

🎯 You're Invited to Apply!

{recruiter_name} from {company_name} has invited you to apply for:

Position: {job_title}
Company: {company_name}
{message_text}

Apply now: {application_link}

Best regards,
The MedMatch Team

© {datetime.now().year} MedMatch - Life Sciences & Engineering Talent Ecosystem
    """
    
    return await send_email(
        to_email=candidate_email,
        subject=f"🎯 You're Invited: {job_title} at {company_name}",
        html_content=html_content,
        text_content=text_content
    )
