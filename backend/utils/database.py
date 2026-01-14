"""
Database Configuration and Connection
"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Export collections for easy access
users = db.users
jobs = db.jobs
applications = db.applications
resumes = db.resumes
saved_jobs = db.saved_jobs
alerts = db.alerts
digest_settings = db.digest_settings
cover_letters = db.cover_letters
predictions = db.predictions
interview_questions = db.interview_questions
resume_profiles = db.resume_profiles
video_recordings = db.video_recordings
recruiter_jobs = db.recruiter_jobs
sessions = db.sessions
digest_history = db.digest_history
