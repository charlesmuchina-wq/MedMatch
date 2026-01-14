"""
Configuration and Environment Variables
"""
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

# Core Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
GMAIL_ADDRESS = os.environ.get('GMAIL_ADDRESS')
GMAIL_APP_PASSWORD = os.environ.get('GMAIL_APP_PASSWORD')
ALERT_RECIPIENT = os.environ.get('ALERT_RECIPIENT')

# Authentication Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'medmatch_default_secret_key_change_in_production')
APPLE_TEAM_ID = os.environ.get('APPLE_TEAM_ID')
APPLE_KEY_ID = os.environ.get('APPLE_KEY_ID')
APPLE_SERVICE_ID = os.environ.get('APPLE_SERVICE_ID')
APPLE_PRIVATE_KEY = os.environ.get('APPLE_PRIVATE_KEY')

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_VERIFY_SERVICE = os.environ.get('TWILIO_VERIFY_SERVICE')

# Google Configuration
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.environ.get('GOOGLE_CSE_ID')

# Stripe Configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
STRIPE_PRICE_ID = os.environ.get('STRIPE_PRICE_ID', 'price_1QcnLuFQ3WZ6r4R5E')

# PayPal Configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')

# Application Settings
LIFETIME_PRICE = 1.00  # $1 lifetime membership
TRIAL_DAYS = 15
