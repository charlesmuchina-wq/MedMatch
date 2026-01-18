"""
MedMatch API Server
Clean, modular FastAPI application with route organization
Production-ready with caching, connection pooling, and optimizations
"""
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from contextlib import asynccontextmanager
from typing import Optional
import hashlib
import json
from datetime import datetime, timezone

# APScheduler for automated daily digest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ============== Production Configuration ==============
MONGO_POOL_SIZE = int(os.environ.get('MONGO_POOL_SIZE', '50'))
MONGO_MIN_POOL_SIZE = int(os.environ.get('MONGO_MIN_POOL_SIZE', '10'))
CACHE_EXPIRE_SECONDS = int(os.environ.get('CACHE_EXPIRE_SECONDS', '300'))

# ============== MongoDB Connection with Optimized Pooling ==============
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(
    mongo_url,
    maxPoolSize=MONGO_POOL_SIZE,
    minPoolSize=MONGO_MIN_POOL_SIZE,
    maxIdleTimeMS=30000,  # Close idle connections after 30s
    waitQueueTimeoutMS=10000,  # Timeout waiting for connection
    serverSelectionTimeoutMS=5000,  # Timeout for server selection
    connectTimeoutMS=5000,  # Connection timeout
    retryWrites=True,
    retryReads=True
)
db = client[os.environ['DB_NAME']]

# ============== Logging Configuration ==============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============== In-Memory Cache for Frequently Accessed Data ==============
class ResponseCache:
    """Simple in-memory cache for API responses"""
    def __init__(self, max_size: int = 1000):
        self._cache = {}
        self._timestamps = {}
        self._max_size = max_size
    
    def _make_key(self, path: str, params: dict = None) -> str:
        key_data = f"{path}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, path: str, params: dict = None, ttl: int = 300) -> Optional[dict]:
        key = self._make_key(path, params)
        if key in self._cache:
            timestamp = self._timestamps.get(key, 0)
            if (datetime.now(timezone.utc).timestamp() - timestamp) < ttl:
                return self._cache[key]
            else:
                # Expired, remove
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, path: str, data: dict, params: dict = None):
        key = self._make_key(path, params)
        
        # Evict oldest if at capacity
        if len(self._cache) >= self._max_size:
            oldest_key = min(self._timestamps, key=self._timestamps.get)
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
        
        self._cache[key] = data
        self._timestamps[key] = datetime.now(timezone.utc).timestamp()
    
    def clear(self):
        self._cache.clear()
        self._timestamps.clear()
    
    def stats(self) -> dict:
        return {
            "size": len(self._cache),
            "max_size": self._max_size
        }

response_cache = ResponseCache(max_size=500)

# ============== Scheduler ==============
scheduler = AsyncIOScheduler()

# ============== Lifespan Context Manager ==============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("🚀 Starting MedMatch API server...")
    
    # Initialize in-memory cache backend
    FastAPICache.init(InMemoryBackend(), prefix="medmatch-cache")
    logger.info("✅ Cache initialized (in-memory)")
    
    # Test MongoDB connection
    try:
        await client.admin.command('ping')
        logger.info(f"✅ MongoDB connected (pool: {MONGO_MIN_POOL_SIZE}-{MONGO_POOL_SIZE})")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
    
    # Start scheduler
    scheduler.add_job(
        scheduled_digest_task,
        CronTrigger(hour=8, minute=0),
        id="daily_digest",
        replace_existing=True
    )
    scheduler.start()
    logger.info("📅 Daily digest scheduler started - runs at 8:00 AM UTC")
    
    logger.info("🚀 MedMatch API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down MedMatch API server...")
    scheduler.shutdown()
    client.close()
    response_cache.clear()
    logger.info("👋 MedMatch API server shutdown complete")

# ============== Initialize FastAPI App ==============
app = FastAPI(
    title="MedMatch API",
    description="AI-Powered Job Search Platform",
    version="2.1.0",
    lifespan=lifespan
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
    biometric_router,
    qa_practice_router,
    video_interview_router,
    push_notifications_router,
    id_verification_router
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
app.include_router(qa_practice_router, prefix="/api")
app.include_router(video_interview_router, prefix="/api")
app.include_router(push_notifications_router, prefix="/api")
app.include_router(id_verification_router, prefix="/api")

# ============== CORS Configuration ==============
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Request Tracking Middleware ==============
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header for monitoring"""
    import time
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response

# ============== Root Endpoint ==============
@app.get("/")
async def root():
    """Root endpoint - redirect to API docs"""
    return RedirectResponse(url="/docs")

# ============== Health & Status Endpoints ==============
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MedMatch API",
        "version": "2.1.0",
        "cache_stats": response_cache.stats()
    }

@app.get("/api/status")
async def system_status():
    """Detailed system status"""
    try:
        # Check MongoDB
        await client.admin.command('ping')
        mongo_status = "connected"
    except:
        mongo_status = "disconnected"
    
    return {
        "status": "operational",
        "version": "2.1.0",
        "mongodb": {
            "status": mongo_status,
            "pool_size": f"{MONGO_MIN_POOL_SIZE}-{MONGO_POOL_SIZE}"
        },
        "cache": {
            "type": "in-memory",
            "stats": response_cache.stats(),
            "ttl_seconds": CACHE_EXPIRE_SECONDS
        },
        "scheduler": {
            "running": scheduler.running,
            "jobs": len(scheduler.get_jobs())
        }
    }

# ============== Cached Endpoints ==============
@app.get("/api/cached/languages")
@cache(expire=3600)  # Cache for 1 hour
async def get_cached_languages():
    """Get supported languages (cached)"""
    from routes.translation import SUPPORTED_LANGUAGES
    return {"languages": SUPPORTED_LANGUAGES, "cached": True}

@app.get("/api/cached/id-levels")
@cache(expire=3600)  # Cache for 1 hour
async def get_cached_id_levels():
    """Get ID verification levels (cached)"""
    from routes.id_verification import VERIFICATION_LEVELS
    return {"levels": VERIFICATION_LEVELS, "cached": True}

# ============== Scheduled Tasks ==============
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
                        {"$set": {"last_sent": datetime.now(timezone.utc).isoformat()}}
                    )
                    logger.info(f"✅ Sent digest to {email} ({len(new_jobs[:20])} jobs)")
                else:
                    logger.error(f"❌ Failed to send digest to {email}")
                    
            except Exception as e:
                logger.error(f"Error processing digest for {email}: {e}")
        
        logger.info(f"📧 Scheduled digest complete: {sent_count}/{len(subscribers)} emails sent")
        
    except Exception as e:
        logger.error(f"Scheduled digest error: {e}")

# Export cache for use in routes
__all__ = ['app', 'db', 'client', 'response_cache', 'CACHE_EXPIRE_SECONDS']
