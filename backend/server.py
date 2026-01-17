"""
MedMatch API Server
Clean, modular FastAPI application with route organization
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

# APScheduler for automated daily digest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize FastAPI app
app = FastAPI(
    title="MedMatch API",
    description="AI-Powered Job Search Platform",
    version="2.0.0"
)

# ============== Import and Register Routes ==============
from routes import (
    auth_router,
    jobs_router,
    resume_router,
    interview_router,
    ai_features_router,
    analytics_router,
    digest_router,
    messages_router,
    recruiter_router,
    cloud_router,
    companies_router,
    skills_router,
    payments_router,
    membership_router,
    scheduling_router,
    notifications_router,
    push_router,
    dragon_router,
    translation_router,
    biometric_router
)

# Register all routers with /api prefix
app.include_router(auth_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(resume_router, prefix="/api")
app.include_router(interview_router, prefix="/api")
app.include_router(ai_features_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(digest_router, prefix="/api")
app.include_router(messages_router, prefix="/api")
app.include_router(recruiter_router, prefix="/api")
app.include_router(cloud_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(skills_router, prefix="/api")
app.include_router(payments_router, prefix="/api")
app.include_router(membership_router, prefix="/api")
app.include_router(scheduling_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(push_router, prefix="/api")
app.include_router(dragon_router, prefix="/api")
app.include_router(translation_router, prefix="/api")
app.include_router(biometric_router, prefix="/api")

# ============== CORS Configuration ==============
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Logging Configuration ==============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============== Root Endpoint ==============
@app.get("/")
async def root():
    """Root endpoint - redirect to API docs"""
    return RedirectResponse(url="/docs")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MedMatch API",
        "version": "2.0.0"
    }

# ============== Scheduled Tasks ==============
scheduler = AsyncIOScheduler()

async def scheduled_digest_task():
    """Background task that runs the daily digest for all subscribers"""
    from routes.digest import send_single_digest, generate_digest_email_html, send_email_gmail, filter_new_jobs
    from routes.jobs import fetch_remoteok_jobs, fetch_remotive_jobs
    
    logger.info("🕐 Running scheduled daily digest...")
    
    try:
        # Get all active digest subscribers
        subscribers = await db.digest_settings.find({"is_active": True}, {"_id": 0}).to_list(100)
        
        if not subscribers:
            logger.info("No active digest subscribers")
            return
        
        sent_count = 0
        
        for subscriber in subscribers:
            email = subscriber.get("email")
            search_queries = subscriber.get("search_queries", ["remote", "quality"])
            user_name = subscriber.get("user_name", "Job Seeker")
            
            if not email:
                continue
            
            try:
                # Fetch jobs
                all_jobs = []
                for query in search_queries[:3]:
                    jobs = await fetch_remoteok_jobs(query)
                    all_jobs.extend(jobs)
                    jobs = await fetch_remotive_jobs(query)
                    all_jobs.extend(jobs)
                
                # Deduplicate
                seen_urls = set()
                unique_jobs = []
                for job in all_jobs:
                    url = job.get("url", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        unique_jobs.append(job)
                
                # Filter out already-emailed jobs
                new_jobs = await filter_new_jobs(unique_jobs, email)
                
                if not new_jobs:
                    logger.info(f"No new jobs for {email}")
                    continue
                
                # Generate and send email
                query_summary = ", ".join(search_queries[:3])
                html_content = generate_digest_email_html(new_jobs[:20], user_name, query_summary)
                
                # Mark jobs as emailed
                from routes.digest import mark_job_emailed
                for job in new_jobs[:20]:
                    await mark_job_emailed(job, email)
                
                success = send_email_gmail(
                    email,
                    f"🎯 MedMatch Daily Digest: {len(new_jobs[:20])} New Quality Jobs",
                    html_content
                )
                
                if success:
                    sent_count += 1
                    await db.digest_settings.update_one(
                        {"email": email},
                        {"$set": {"last_sent": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()}}
                    )
                    logger.info(f"✅ Sent digest to {email} ({len(new_jobs[:20])} jobs)")
                else:
                    logger.error(f"❌ Failed to send digest to {email}")
                    
            except Exception as e:
                logger.error(f"Error processing digest for {email}: {e}")
        
        logger.info(f"📧 Scheduled digest complete: {sent_count}/{len(subscribers)} emails sent")
        
    except Exception as e:
        logger.error(f"Scheduled digest error: {e}")

# ============== Lifecycle Events ==============
@app.on_event("startup")
async def startup_event():
    """Start the scheduler when the app starts"""
    # Schedule daily digest at 8:00 AM UTC
    scheduler.add_job(
        scheduled_digest_task,
        CronTrigger(hour=8, minute=0),
        id="daily_digest",
        replace_existing=True
    )
    scheduler.start()
    logger.info("📅 Daily digest scheduler started - runs at 8:00 AM UTC")
    logger.info("🚀 MedMatch API server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    scheduler.shutdown()
    client.close()
    logger.info("👋 MedMatch API server shutdown complete")
