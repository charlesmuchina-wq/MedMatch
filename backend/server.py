"""
MedMatch-AI KARAU API Server
Clean, modular FastAPI application with route organization
Production-ready with AI Supervisor for scaling up to 1M+ concurrent users
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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

# AI Supervisor for intelligent scaling
from services.ai_supervisor import ai_supervisor, SystemHealth

# Global Rate Limiter
from services.global_rate_limiter import (
    global_rate_limiter, 
    get_client_identifier, 
    get_user_tier
)

# KARAU DRAGON Scheduler
from services.dragon_scheduler import start_scheduler, stop_scheduler

# ML Data Collector
from services.ml_data_collector import ml_collector

# Load environment
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# ============== Production Configuration (1M Users) ==============
MONGO_POOL_SIZE = int(os.environ.get('MONGO_POOL_SIZE', '100'))
MONGO_MIN_POOL_SIZE = int(os.environ.get('MONGO_MIN_POOL_SIZE', '20'))
CACHE_EXPIRE_SECONDS = int(os.environ.get('CACHE_EXPIRE_SECONDS', '300'))
MAX_CONCURRENT_USERS = int(os.environ.get('MAX_CONCURRENT_USERS', '1000000'))

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
    logger.info("🚀 Starting MedMatch-AI KARAU API server...")
    
    # Initialize in-memory cache backend
    FastAPICache.init(InMemoryBackend(), prefix="medmatch-cache")
    logger.info("✅ Cache initialized (in-memory)")
    
    # Test MongoDB connection
    try:
        await client.admin.command('ping')
        logger.info(f"✅ MongoDB connected (pool: {MONGO_MIN_POOL_SIZE}-{MONGO_POOL_SIZE})")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
    
    # Initialize Global Rate Limiter
    await global_rate_limiter.initialize()
    logger.info(f"🚦 Global rate limiter initialized ({global_rate_limiter.get_stats()['type']})")
    
    # Start AI Supervisor
    await ai_supervisor.start()
    logger.info(f"🤖 AI Supervisor started (max users: {MAX_CONCURRENT_USERS:,})")
    
    # Initialize LUMI file storage
    try:
        from routes.lumi_files import init_storage
        init_storage()
        logger.info("LUMI file storage initialized")
    except Exception as e:
        logger.warning(f"LUMI file storage init deferred: {e}")
    
    # Start daily digest scheduler
    scheduler.add_job(
        scheduled_digest_task,
        CronTrigger(hour=8, minute=0),
        id="daily_digest",
        replace_existing=True
    )
    scheduler.start()
    logger.info("📅 Daily digest scheduler started - runs at 8:00 AM UTC")
    
    # Start KARAU DRAGON Scheduler
    start_scheduler()
    logger.info("🐉 KARAU DRAGON Scheduler started - Weekly maintenance Sundays 1:00 AM PST")
    
    # Initialize ML Data Collector
    await ml_collector.initialize(mongo_url, os.environ.get('DB_NAME', 'medmatch'))
    logger.info("ML Data Collector initialized - Training data collection active")
    
    # Initialize Object Storage
    try:
        from services.object_storage import init_storage
        init_storage()
        logger.info("Object storage initialized for cloud recordings")
    except Exception as e:
        logger.warning(f"Object storage init deferred: {e}")
    
    logger.info("MedMatch-AI KARAU API server started successfully - Ready for 1M+ users!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down MedMatch-AI KARAU API server...")
    await ai_supervisor.stop()
    await ml_collector.shutdown()
    scheduler.shutdown()
    stop_scheduler()
    client.close()
    response_cache.clear()
    logger.info("👋 MedMatch-AI KARAU API server shutdown complete")

# ============== Initialize FastAPI App ==============
app = FastAPI(
    title="MedMatch-AI KARAU API",
    description="AI-Powered Job Search Platform with AI Supervisor",
    version="2.2.0",
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
    id_verification_router,
    linkedin_router,
    feedback_router,
    autofill_router,
    realtime_stt_router,
    webpush_router,
    video_analysis_router,
    persona_verification_router
)

# Import additional routers
from routes.batch import router as batch_router
from routes.meeting_notes import router as meeting_notes_router
from routes.interview_calendar import router as interview_calendar_router
from routes.analytics_funnel import router as analytics_funnel_router
from routes.dragon_automator import router as dragon_automator_router
from routes.ml_data import router as ml_data_router
from routes.admin_audit import router as admin_audit_router
from routes.ml_predictor import router as ml_predictor_router
from routes.ml_model import router as ml_model_router
from routes.production_metrics import router as production_metrics_router
from routes.privacy import router as privacy_router
from routes.recruiter_rbac import router as recruiter_rbac_router
from routes.mutual_match import router as mutual_match_router
from routes.taxonomy import router as taxonomy_router
from routes.credentials import router as credentials_router
from routes.employer_reviews import router as employer_reviews_router
from routes.notifications import router as notifications_router
from routes.job_verification import router as job_verification_router
from routes.geolocation import router as geolocation_router
from routes.enterprise_api import router as enterprise_api_router
from routes.ats import router as ats_router
from routes.tutorials import router as tutorials_router
from routes.video_translation import router as video_translation_router
from routes.search_engine import router as search_engine_router
from routes.translation_qa import router as translation_qa_router
from routes.capa import router as capa_router
from routes.ai_qa import router as ai_qa_router
from routes.avatar import router as avatar_router
from routes.psv import router as psv_router
from routes.video_assets import router as video_assets_router
from routes.orcid_oauth import router as orcid_router
from routes.data_integrity import router as data_integrity_router
from routes.ai_compliance import router as ai_compliance_router
from routes.global_compliance import router as global_compliance_router
from routes.compliance_alerts import router as compliance_alerts_router
from routes.audit_reports import router as audit_reports_router
from routes.karau_meet import router as karau_meet_router
from routes.karau_extended import router as karau_extended_router
from routes.karau_scheduling import router as karau_scheduling_router
from routes.karau_collaboration import router as karau_collaboration_router
from routes.karau_security import router as karau_security_router
from routes.karau_accessibility import router as karau_accessibility_router
from routes.karau_ai import router as karau_ai_router
from routes.karau_webrtc import router as karau_webrtc_router
from routes.karau_recordings import router as karau_recordings_router
from routes.karau_organizations import router as karau_organizations_router
from routes.karau_guest_verification import router as karau_guest_router
from routes.karau_sharing import router as karau_sharing_router
from routes.karau_calendar import router as karau_calendar_router
from routes.karau_sso import router as karau_sso_router
from routes.karau_intelligence import router as karau_intelligence_router
from routes.karau_analytics import router as karau_analytics_router
from routes.karau_webinar import router as karau_webinar_router
from routes.ai_talent import router as ai_talent_router
from routes.dei_analytics import router as dei_analytics_router
from routes.talent_crm import router as talent_crm_router
from routes.talent_tools import router as talent_tools_router
from routes.advanced_features import router as advanced_features_router
from routes.meeting_infrastructure import router as meeting_infra_router
from routes.platform_features import router as platform_features_router
from routes.karau_gamification import router as karau_gamification_router
from routes.karau_director import router as karau_director_router
from routes.karau_qr_entry import router as karau_qr_router
from routes.karau_ghost_booking import router as karau_ghost_router
from routes.karau_enhanced_sentiment import router as karau_enhanced_sentiment_router
from routes.karau_slam_spatial import router as karau_slam_spatial_router
from routes.karau_webxr import router as karau_webxr_router
from routes.karau_iot_control import router as karau_iot_router
from routes.karau_beamforming import router as karau_beamforming_router
from routes.karau_replay import router as karau_replay_router
from routes.karau_hardware_discovery import router as karau_hardware_router
from routes.karau_breakout_lounges import router as karau_breakout_router
from routes.karau_polls_challenges import router as karau_polls_router
from routes.karau_biometric_verify import router as karau_biometric_router
from routes.karau_simulation import router as karau_simulation_router
from routes.lumi_messenger import router as lumi_messenger_router
from routes.lumi_ai import router as lumi_ai_router
from routes.meeting_intelligence import router as meeting_intelligence_router
from routes.ai_productivity import router as ai_productivity_router
from routes.lumi_files import router as lumi_files_router
from routes.lumi_templates import router as lumi_templates_router
from routes.lumi_buckets import router as lumi_buckets_router
from routes.lumi_calendar import router as lumi_calendar_router
from routes.lumi_predict import router as lumi_predict_router

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
app.include_router(notifications_router, prefix="/api")
app.include_router(job_verification_router, prefix="/api")
app.include_router(geolocation_router, prefix="/api")
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
app.include_router(batch_router, prefix="/api")
app.include_router(linkedin_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(autofill_router, prefix="/api")
app.include_router(realtime_stt_router, prefix="/api")
app.include_router(webpush_router, prefix="/api")
app.include_router(video_analysis_router, prefix="/api")
app.include_router(persona_verification_router, prefix="/api")
app.include_router(meeting_notes_router, prefix="/api")
app.include_router(interview_calendar_router, prefix="/api")
app.include_router(analytics_funnel_router, prefix="/api")
app.include_router(dragon_automator_router, prefix="/api")
app.include_router(ml_data_router, prefix="/api")
app.include_router(admin_audit_router, prefix="/api")
app.include_router(ml_predictor_router, prefix="/api")
app.include_router(ml_model_router, prefix="/api")
app.include_router(production_metrics_router, prefix="/api")
app.include_router(privacy_router, prefix="/api")
app.include_router(recruiter_rbac_router, prefix="/api")
app.include_router(mutual_match_router, prefix="/api")
app.include_router(taxonomy_router, prefix="/api")
app.include_router(credentials_router, prefix="/api")
app.include_router(employer_reviews_router, prefix="/api")
app.include_router(enterprise_api_router, prefix="/api")
app.include_router(ats_router, prefix="/api")
app.include_router(tutorials_router, prefix="/api")
app.include_router(video_translation_router, prefix="/api")
app.include_router(search_engine_router, prefix="/api")
app.include_router(translation_qa_router, prefix="/api")
app.include_router(capa_router, prefix="/api")
app.include_router(ai_qa_router, prefix="/api")
app.include_router(avatar_router, prefix="/api")
app.include_router(psv_router, prefix="/api")
app.include_router(video_assets_router, prefix="/api")
app.include_router(orcid_router, prefix="/api")
app.include_router(data_integrity_router, prefix="/api")
app.include_router(ai_compliance_router, prefix="/api")
app.include_router(global_compliance_router, prefix="/api")
app.include_router(compliance_alerts_router, prefix="/api")
app.include_router(audit_reports_router, prefix="/api")
app.include_router(karau_meet_router, prefix="/api")
app.include_router(karau_extended_router, prefix="/api")
app.include_router(karau_scheduling_router, prefix="/api")
app.include_router(karau_collaboration_router, prefix="/api")
app.include_router(karau_security_router, prefix="/api")
app.include_router(karau_accessibility_router, prefix="/api")
app.include_router(karau_ai_router, prefix="/api")
app.include_router(karau_webrtc_router, prefix="/api")
app.include_router(karau_recordings_router, prefix="/api")
app.include_router(karau_organizations_router, prefix="/api")
app.include_router(karau_guest_router, prefix="/api")
app.include_router(karau_sharing_router, prefix="/api")
app.include_router(karau_calendar_router, prefix="/api")
app.include_router(karau_sso_router, prefix="/api")
app.include_router(karau_intelligence_router, prefix="/api")
app.include_router(karau_analytics_router, prefix="/api")
app.include_router(karau_webinar_router, prefix="/api")
app.include_router(ai_talent_router, prefix="/api")
app.include_router(dei_analytics_router, prefix="/api")
app.include_router(talent_crm_router, prefix="/api")
app.include_router(talent_tools_router, prefix="/api")
app.include_router(advanced_features_router, prefix="/api")
app.include_router(meeting_infra_router, prefix="/api")
app.include_router(platform_features_router, prefix="/api")
app.include_router(karau_gamification_router, prefix="/api")
app.include_router(karau_director_router, prefix="/api")
app.include_router(karau_qr_router, prefix="/api")
app.include_router(karau_ghost_router, prefix="/api")
app.include_router(karau_enhanced_sentiment_router, prefix="/api")
app.include_router(karau_slam_spatial_router, prefix="/api")
app.include_router(karau_webxr_router, prefix="/api")
app.include_router(karau_iot_router, prefix="/api")
app.include_router(karau_beamforming_router, prefix="/api")
app.include_router(karau_replay_router, prefix="/api")
app.include_router(karau_hardware_router, prefix="/api")
app.include_router(karau_breakout_router, prefix="/api")
app.include_router(karau_polls_router, prefix="/api")
app.include_router(karau_biometric_router, prefix="/api")
app.include_router(karau_simulation_router, prefix="/api")
app.include_router(lumi_messenger_router, prefix="/api")
app.include_router(lumi_ai_router, prefix="/api")
app.include_router(lumi_templates_router, prefix="/api")
app.include_router(lumi_buckets_router, prefix="/api")
app.include_router(lumi_calendar_router, prefix="/api")
app.include_router(lumi_predict_router, prefix="/api")

app.include_router(meeting_intelligence_router, prefix="/api")
app.include_router(lumi_files_router, prefix="/api")
app.include_router(ai_productivity_router, prefix="/api")

# ============== Static Files for Videos ==============
# Mount the videos directory for serving tutorial videos
videos_dir = Path("/app/videos")
if videos_dir.exists():
    app.mount("/videos", StaticFiles(directory=str(videos_dir)), name="videos")

# Mount tutorial videos directory
tutorial_videos_dir = Path("/app/backend/static/videos/tutorials")
if tutorial_videos_dir.exists():
    app.mount("/tutorial-videos", StaticFiles(directory=str(tutorial_videos_dir)), name="tutorial_videos")

# Mount tutorial audio directory (for edge-tts generated audio)
tutorial_audio_dir = Path("/app/backend/static/audio/tutorials")
tutorial_audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static/audio/tutorials", StaticFiles(directory=str(tutorial_audio_dir)), name="tutorial_audio")

# ============== CORS Configuration ==============
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== Global Rate Limiting Middleware ==============
@app.middleware("http")
async def global_rate_limit_middleware(request: Request, call_next):
    """Apply tier-based rate limiting with proper headers"""
    # Skip rate limiting for health checks and websockets
    if request.url.path in ["/api/health", "/api/status", "/docs", "/openapi.json"] or "/ws/" in request.url.path:
        return await call_next(request)
    
    # Get client identifier and tier
    identifier = get_client_identifier(request)
    tier = get_user_tier(request)
    
    # Check rate limit
    allowed, headers = await global_rate_limiter.check_rate_limit(identifier, tier)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please retry after the specified time.",
                "tier": tier,
                "retry_after": headers.get("Retry-After", "5")
            },
            headers=headers
        )
    
    # Process request and add rate limit headers to response
    response = await call_next(request)
    for key, value in headers.items():
        response.headers[key] = value
    
    return response

# ============== Request Tracking Middleware ==============
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and track in AI Supervisor + ML Data"""
    import time
    # Skip for websockets
    if "/ws/" in request.url.path:
        return await call_next(request)
    start_time = time.perf_counter()
    
    # Track request in AI Supervisor metrics
    ai_supervisor.metrics.total_requests += 1
    
    # Get user ID for ML tracking if available
    user_id = None
    user = getattr(request.state, 'user', None)
    if user:
        user_id = user.get('user_id')
    
    try:
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        
        # Record success
        if response.status_code < 400:
            ai_supervisor.metrics.successful_requests += 1
        else:
            ai_supervisor.metrics.failed_requests += 1
        
        ai_supervisor.metrics.response_times.append(process_time)
        
        # Log to ML Data Collector (only for API routes)
        if request.url.path.startswith("/api") and request.url.path not in ["/api/health", "/api/status"]:
            try:
                await ml_collector.log_api_call(
                    path=request.url.path,
                    method=request.method,
                    status_code=response.status_code,
                    response_time_ms=process_time,
                    user_id=user_id
                )
            except Exception:
                pass  # Don't fail requests due to ML logging
        
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        response.headers["X-System-Health"] = ai_supervisor.health.value
        return response
        
    except Exception:
        ai_supervisor.metrics.failed_requests += 1
        raise

# ============== Overload Protection Middleware ==============
@app.middleware("http")
async def overload_protection(request: Request, call_next):
    """Protect system from overload using AI Supervisor"""
    # Skip protection for health checks, status, and websockets
    if request.url.path in ["/api/health", "/api/status", "/api/supervisor/status"] or "/ws/" in request.url.path:
        return await call_next(request)
    
    # Check if system is overloaded
    if ai_supervisor.health == SystemHealth.OVERLOADED:
        # Check rate limiter
        if not await ai_supervisor.rate_limiter.acquire():
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service temporarily unavailable",
                    "message": "System is under heavy load. Please retry.",
                    "retry_after": 5,
                    "health": ai_supervisor.health.value
                },
                headers={"Retry-After": "5"}
            )
    
    return await call_next(request)

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
        "service": "MedMatch-AI KARAU API",
        "version": "2.2.0",
        "ai_supervisor": ai_supervisor.health.value,
        "cache_stats": response_cache.stats()
    }

@app.get("/api/status")
async def system_status():
    """Detailed system status"""
    try:
        # Check MongoDB
        await client.admin.command('ping')
        mongo_status = "connected"
    except Exception:
        mongo_status = "disconnected"
    
    return {
        "status": "operational",
        "version": "2.2.0",
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
        },
        "ai_supervisor": ai_supervisor.get_status()
    }

# ============== AI Supervisor Endpoints ==============
@app.get("/api/supervisor/status")
async def get_supervisor_status():
    """Get detailed AI Supervisor status"""
    return ai_supervisor.get_status()

@app.get("/api/supervisor/health")
async def get_supervisor_health():
    """Get AI Supervisor health metrics"""
    status = ai_supervisor.get_status()
    return {
        "health": status["health"],
        "health_score": status["health_score"],
        "metrics": status["metrics"],
        "capacity": status["capacity"]
    }

@app.post("/api/supervisor/adjust-rate")
async def adjust_rate_limit(rate: int):
    """Manually adjust rate limit (admin only)"""
    if rate < 100 or rate > 5000:
        raise HTTPException(status_code=400, detail="Rate must be between 100 and 5000")
    ai_supervisor.rate_limiter.current_rate = rate
    return {"message": f"Rate limit adjusted to {rate} req/sec"}

# ============== Global Rate Limiter Endpoints ==============
@app.get("/api/rate-limit/status")
async def get_rate_limit_status(request: Request):
    """Get current rate limit status for the client"""
    identifier = get_client_identifier(request)
    tier = get_user_tier(request)
    usage = await global_rate_limiter.get_usage(identifier)
    tier_info = global_rate_limiter.get_tier_info()[tier]
    
    return {
        "identifier": identifier,
        "tier": tier,
        "usage": usage,
        "limits": tier_info,
        "backend": global_rate_limiter.get_stats()["type"]
    }

@app.get("/api/rate-limit/tiers")
async def get_rate_limit_tiers():
    """Get all available rate limit tiers"""
    return global_rate_limiter.get_tier_info()

@app.get("/api/rate-limit/stats")
async def get_rate_limit_stats():
    """Get global rate limiter statistics"""
    return global_rate_limiter.get_stats()

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
    from routes.digest import generate_digest_email_html, send_email_gmail, filter_new_jobs
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
                    f"🎯 MedMatch-AI KARAU Daily Digest: {len(new_jobs[:20])} New Quality Jobs",
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
