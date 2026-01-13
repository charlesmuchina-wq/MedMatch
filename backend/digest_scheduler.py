#!/usr/bin/env python3
"""
MedMatch Daily Digest Scheduler
This script runs as a cron job to send daily digest emails to all subscribers.
"""
import os
import sys
import requests
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/digest_cron.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.environ.get('BACKEND_URL', 'http://localhost:8001')
API_ENDPOINT = f"{BACKEND_URL}/api/digest/run-scheduled"

def run_scheduled_digest():
    """Trigger the scheduled digest endpoint"""
    logger.info(f"Starting scheduled digest at {datetime.now().isoformat()}")
    
    try:
        response = requests.post(API_ENDPOINT, timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Digest completed successfully:")
            logger.info(f"  - Total subscribers: {result.get('total_subscribers', 0)}")
            logger.info(f"  - Emails sent: {result.get('sent_count', 0)}")
            logger.info(f"  - Jobs found: {result.get('total_jobs_found', 0)}")
            
            # Log individual results
            for r in result.get('results', []):
                logger.info(f"  - {r.get('email')}: {r.get('status')} ({r.get('jobs_count', 0)} jobs)")
            
            return True
        else:
            logger.error(f"Digest failed with status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("Digest request timed out after 5 minutes")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs('/app/logs', exist_ok=True)
    
    success = run_scheduled_digest()
    sys.exit(0 if success else 1)
