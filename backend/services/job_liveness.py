"""
Job Liveness Verification Service
Verifies that job listings are still active and not "ghost jobs".

Verification Methods:
1. HTTP Head Checks - Check if URL returns 404 or redirects
2. AI Content Analysis - Detect "Position Filled" or "No longer accepting" text
3. User Feedback Loop - Track user reports of expired jobs
"""
import asyncio
import httpx
import logging
import re
from typing import Dict, Optional, List
from datetime import datetime, timezone, timedelta
from utils.database import db

logger = logging.getLogger(__name__)

# Phrases that indicate a job is no longer active
EXPIRED_PHRASES = [
    "position has been filled",
    "no longer accepting applications",
    "this job has expired",
    "job is no longer available",
    "position is closed",
    "applications closed",
    "listing has been removed",
    "job posting has ended",
    "this position has been filled",
    "requisition closed",
    "opportunity is no longer available",
    "we are no longer accepting",
    "this role has been filled",
    "posting expired",
    "job closed",
    "application deadline passed"
]

# HTTP status codes that indicate job is gone
DEAD_STATUS_CODES = [404, 410, 301, 302, 303, 307, 308]


class JobLivenessService:
    """
    Service to verify job listings are still active.
    """
    
    def __init__(self):
        self.client = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self.client is None:
            self.client = httpx.AsyncClient(
                timeout=15.0,
                follow_redirects=True,
                headers={"User-Agent": "MedMatch/2.0 JobVerifier"}
            )
        return self.client
    
    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def check_url_alive(self, url: str) -> Dict:
        """
        Check if a job URL is still active using HTTP HEAD request.
        Returns verification result with status.
        """
        try:
            client = await self.get_client()
            
            # First try HEAD request (faster)
            try:
                response = await client.head(url)
                status_code = response.status_code
            except:
                # Fallback to GET if HEAD fails
                response = await client.get(url)
                status_code = response.status_code
            
            # Check for redirect to job-not-found pages
            final_url = str(response.url) if response.url else url
            
            # Check status code
            if status_code == 200:
                # Check if redirected to a "job not found" page
                if any(kw in final_url.lower() for kw in ["not-found", "expired", "error", "404"]):
                    return {
                        "is_alive": False,
                        "status": "redirected_to_error",
                        "status_code": status_code,
                        "reason": "Redirected to error page",
                        "checked_at": datetime.now(timezone.utc).isoformat()
                    }
                return {
                    "is_alive": True,
                    "status": "active",
                    "status_code": status_code,
                    "reason": None,
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            
            elif status_code in DEAD_STATUS_CODES:
                return {
                    "is_alive": False,
                    "status": "dead",
                    "status_code": status_code,
                    "reason": f"HTTP {status_code}",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            
            else:
                return {
                    "is_alive": True,  # Assume alive for other codes
                    "status": "unknown",
                    "status_code": status_code,
                    "reason": f"HTTP {status_code}",
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
        
        except httpx.TimeoutException:
            return {
                "is_alive": True,  # Don't mark as dead on timeout
                "status": "timeout",
                "status_code": None,
                "reason": "Request timed out",
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"URL check error for {url}: {e}")
            return {
                "is_alive": True,  # Don't mark as dead on error
                "status": "error",
                "status_code": None,
                "reason": str(e)[:100],
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_content_expired(self, url: str) -> Dict:
        """
        Fetch page content and check for expired job indicators.
        """
        try:
            client = await self.get_client()
            response = await client.get(url)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for expired phrases
                for phrase in EXPIRED_PHRASES:
                    if phrase in content:
                        return {
                            "is_expired": True,
                            "reason": f"Found phrase: '{phrase}'",
                            "checked_at": datetime.now(timezone.utc).isoformat()
                        }
                
                # Check if "Apply" button is present
                has_apply = any(btn in content for btn in [
                    "apply now", "apply for this job", "submit application",
                    "apply today", "quick apply", "easy apply"
                ])
                
                if not has_apply:
                    # No apply button might indicate closed job
                    return {
                        "is_expired": False,  # Don't confirm expired, just flag
                        "warning": "No apply button found",
                        "reason": None,
                        "checked_at": datetime.now(timezone.utc).isoformat()
                    }
                
                return {
                    "is_expired": False,
                    "reason": None,
                    "has_apply_button": True,
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            
            return {
                "is_expired": False,
                "reason": f"HTTP {response.status_code}",
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
        
        except Exception as e:
            logger.error(f"Content check error for {url}: {e}")
            return {
                "is_expired": False,
                "reason": str(e)[:100],
                "checked_at": datetime.now(timezone.utc).isoformat()
            }
    
    async def verify_job(self, job_id: str, url: str) -> Dict:
        """
        Full verification of a job listing.
        Combines URL check and content analysis.
        """
        # Run URL check
        url_result = await self.check_url_alive(url)
        
        # If URL is dead, no need for content check
        if not url_result.get("is_alive"):
            verification = {
                "job_id": job_id,
                "url": url,
                "is_verified": False,
                "is_active": False,
                "verification_method": "url_check",
                "details": url_result,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store verification result
            await self._store_verification(verification)
            return verification
        
        # URL is alive, check content
        content_result = await self.check_content_expired(url)
        
        is_active = not content_result.get("is_expired", False)
        
        verification = {
            "job_id": job_id,
            "url": url,
            "is_verified": True,
            "is_active": is_active,
            "verification_method": "content_analysis" if content_result.get("is_expired") else "url_check",
            "details": {
                "url_check": url_result,
                "content_check": content_result
            },
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Store verification result
        await self._store_verification(verification)
        return verification
    
    async def _store_verification(self, verification: Dict):
        """Store verification result in database"""
        try:
            await db.job_verifications.update_one(
                {"job_id": verification["job_id"]},
                {"$set": verification},
                upsert=True
            )
        except Exception as e:
            logger.error(f"Failed to store verification: {e}")
    
    async def get_verification(self, job_id: str) -> Optional[Dict]:
        """Get stored verification for a job"""
        try:
            result = await db.job_verifications.find_one(
                {"job_id": job_id},
                {"_id": 0}
            )
            return result
        except Exception as e:
            logger.error(f"Failed to get verification: {e}")
            return None
    
    async def report_expired(self, job_id: str, user_id: str) -> Dict:
        """
        User reports a job as expired.
        If 2+ users report, job is hidden.
        """
        try:
            # Add report
            await db.job_reports.update_one(
                {"job_id": job_id},
                {
                    "$addToSet": {"reporters": user_id},
                    "$inc": {"report_count": 1},
                    "$set": {"last_reported": datetime.now(timezone.utc).isoformat()}
                },
                upsert=True
            )
            
            # Get report count
            report = await db.job_reports.find_one({"job_id": job_id}, {"_id": 0})
            report_count = report.get("report_count", 1) if report else 1
            
            # If 2+ reports, mark job as hidden
            if report_count >= 2:
                await db.job_verifications.update_one(
                    {"job_id": job_id},
                    {
                        "$set": {
                            "is_active": False,
                            "is_verified": True,
                            "verification_method": "user_reports",
                            "hidden_reason": f"Reported by {report_count} users",
                            "verified_at": datetime.now(timezone.utc).isoformat()
                        }
                    },
                    upsert=True
                )
                
                return {
                    "status": "job_hidden",
                    "message": "Job has been hidden due to multiple reports",
                    "report_count": report_count
                }
            
            return {
                "status": "report_recorded",
                "message": "Thank you for reporting. Job will be reviewed.",
                "report_count": report_count
            }
        
        except Exception as e:
            logger.error(f"Failed to record report: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_job_status(self, job_id: str) -> Dict:
        """
        Get the current verification status of a job.
        """
        verification = await self.get_verification(job_id)
        
        if not verification:
            return {
                "job_id": job_id,
                "status": "unverified",
                "is_active": True,  # Assume active if not verified
                "needs_verification": True
            }
        
        # Check if verification is stale (>24 hours old)
        verified_at = verification.get("verified_at")
        is_stale = False
        
        if verified_at:
            try:
                verified_time = datetime.fromisoformat(verified_at.replace('Z', '+00:00'))
                age = datetime.now(timezone.utc) - verified_time
                is_stale = age > timedelta(hours=24)
            except:
                pass
        
        return {
            "job_id": job_id,
            "status": "verified" if verification.get("is_verified") else "unverified",
            "is_active": verification.get("is_active", True),
            "verification_method": verification.get("verification_method"),
            "verified_at": verified_at,
            "needs_verification": is_stale,
            "hidden_reason": verification.get("hidden_reason")
        }
    
    async def batch_verify(self, jobs: List[Dict], max_concurrent: int = 5) -> List[Dict]:
        """
        Verify multiple jobs in batches with rate limiting.
        """
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def verify_with_limit(job):
            async with semaphore:
                job_id = job.get("id", "")
                url = job.get("url", "")
                
                if not url:
                    return None
                
                # Check if recently verified
                status = await self.get_job_status(job_id)
                if not status.get("needs_verification"):
                    return {**job, "verification_status": status}
                
                # Verify job
                verification = await self.verify_job(job_id, url)
                return {**job, "verification_status": verification}
        
        tasks = [verify_with_limit(job) for job in jobs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if r and not isinstance(r, Exception)]
    
    async def cleanup_expired_jobs(self, days_old: int = 30) -> int:
        """
        Remove jobs that have been marked as inactive for X days.
        """
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
            result = await db.job_verifications.delete_many({
                "is_active": False,
                "verified_at": {"$lt": cutoff.isoformat()}
            })
            return result.deleted_count
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            return 0


# Singleton instance
_liveness_service = None

def get_liveness_service() -> JobLivenessService:
    global _liveness_service
    if _liveness_service is None:
        _liveness_service = JobLivenessService()
    return _liveness_service
