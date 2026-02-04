"""
Credly OAuth Integration Service
Enables automatic import of digital badges from Credly platform.
Supports badges from AWS, Microsoft, Cisco, CompTIA, PMI, and many others.
"""

import os
import httpx
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
import uuid

logger = logging.getLogger(__name__)

# Environment variables
CREDLY_CLIENT_ID = os.environ.get("CREDLY_CLIENT_ID", "")
CREDLY_CLIENT_SECRET = os.environ.get("CREDLY_CLIENT_SECRET", "")
CREDLY_REDIRECT_URI = os.environ.get("CREDLY_REDIRECT_URI", "")

# Credly API endpoints
CREDLY_AUTH_URL = "https://www.credly.com/oauth/authorize"
CREDLY_TOKEN_URL = "https://www.credly.com/oauth/token"
CREDLY_API_BASE = "https://api.credly.com/v1"


class CredlyOAuthService:
    """Service for Credly OAuth 2.0 authentication and badge import."""
    
    def __init__(self, db=None):
        self.db = db
        self.client_id = CREDLY_CLIENT_ID
        self.client_secret = CREDLY_CLIENT_SECRET
        self.redirect_uri = CREDLY_REDIRECT_URI
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate the Credly authorization URL for OAuth flow initiation.
        Users are redirected to this URL to authenticate and grant permissions.
        """
        if not self.client_id:
            # Return a placeholder for demo if no client ID configured
            return f"https://www.credly.com/oauth/authorize?client_id=DEMO_CLIENT&response_type=code&redirect_uri={self.redirect_uri}&scope=issued_badges%20badge_templates&state={state or 'demo'}"
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "issued_badges badge_templates",
            "state": state or str(uuid.uuid4())
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{CREDLY_AUTH_URL}?{query_string}"
    
    async def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        """
        if not self.client_id or not self.client_secret:
            # Simulate token exchange for demo
            logger.info("Credly credentials not configured - simulating token exchange")
            return self._simulate_token_response()
        
        payload = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    CREDLY_TOKEN_URL,
                    data=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                token_data = response.json()
                
                logger.info("Successfully exchanged authorization code for tokens")
                return {
                    "access_token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in", 3600),
                    "token_type": token_data.get("token_type", "Bearer"),
                }
        except httpx.HTTPError as e:
            logger.error(f"Failed to exchange authorization code: {str(e)}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token using the refresh token.
        """
        if not self.client_id or not self.client_secret:
            return self._simulate_token_response()
        
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    CREDLY_TOKEN_URL,
                    data=payload,
                    timeout=10.0,
                )
                response.raise_for_status()
                token_data = response.json()
                
                return {
                    "access_token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token"),
                    "expires_in": token_data.get("expires_in", 3600),
                }
        except httpx.HTTPError as e:
            logger.error(f"Failed to refresh access token: {str(e)}")
            raise
    
    async def fetch_user_badges(self, access_token: str) -> List[Dict[str, Any]]:
        """
        Fetch all badges for the authenticated user from Credly.
        """
        if not self.client_id:
            # Return simulated badges for demo
            return self._simulate_badges()
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        all_badges = []
        page = 1
        
        try:
            while True:
                url = f"{CREDLY_API_BASE}/users/me/badges?page={page}&per_page=50"
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(url, headers=headers, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()
                    
                    badges = data.get("data", [])
                    all_badges.extend(badges)
                    
                    metadata = data.get("metadata", {})
                    if page >= metadata.get("total_pages", 1):
                        break
                    
                    page += 1
            
            logger.info(f"Fetched {len(all_badges)} badges from Credly")
            return all_badges
            
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch badges from Credly: {str(e)}")
            raise
    
    def transform_badge(self, credly_badge: Dict, user_id: str) -> Dict[str, Any]:
        """
        Transform Credly badge response to MedMatch credential format.
        """
        try:
            issued_date = datetime.fromisoformat(
                credly_badge.get("issued_at", "").replace("Z", "+00:00")
            )
        except (ValueError, AttributeError):
            issued_date = datetime.now(timezone.utc)
        
        expires_date = None
        if credly_badge.get("expires_at"):
            try:
                expires_date = datetime.fromisoformat(
                    credly_badge.get("expires_at").replace("Z", "+00:00")
                )
            except (ValueError, AttributeError):
                pass
        
        badge_template = credly_badge.get("badge_template", {})
        issuer = badge_template.get("issuer", {})
        
        return {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "credential_code": f"CREDLY_{badge_template.get('id', '')[:8]}",
            "credential_name": badge_template.get("name", "Unknown Badge"),
            "credential_number": credly_badge.get("id"),
            "issuing_authority": issuer.get("name", "Unknown Issuer"),
            "issue_date": issued_date.isoformat(),
            "expiry_date": expires_date.isoformat() if expires_date else None,
            "badge_image_url": badge_template.get("image_url", ""),
            "badge_url": credly_badge.get("url", ""),
            "description": badge_template.get("description", ""),
            "skills": badge_template.get("tags", []),
            "criteria_url": badge_template.get("criteria_url", ""),
            "status": "verified",
            "method": "credly_oauth",
            "source": "credly",
            "credly_badge_id": credly_badge.get("id"),
            "credly_template_id": badge_template.get("id"),
            "imported_at": datetime.now(timezone.utc).isoformat(),
            "last_synced": datetime.now(timezone.utc).isoformat()
        }
    
    def _simulate_token_response(self) -> Dict[str, Any]:
        """Simulate token response for demo when credentials not configured."""
        return {
            "access_token": f"simulated_access_{uuid.uuid4()}",
            "refresh_token": f"simulated_refresh_{uuid.uuid4()}",
            "expires_in": 3600,
            "token_type": "Bearer",
            "simulated": True
        }
    
    def _simulate_badges(self) -> List[Dict[str, Any]]:
        """Return simulated badges for demo purposes."""
        return [
            {
                "id": "badge_aws_cloud_practitioner",
                "issued_at": "2024-06-15T10:30:00Z",
                "expires_at": "2027-06-15T10:30:00Z",
                "url": "https://www.credly.com/badges/demo-aws-cloud",
                "badge_template": {
                    "id": "tmpl_aws_clf",
                    "name": "AWS Certified Cloud Practitioner",
                    "description": "Earners of this certification have a fundamental understanding of IT services and their uses in the AWS Cloud.",
                    "image_url": "https://images.credly.com/size/340x340/images/00634f82-b07f-4bbd-a6bb-53de397fc3a6/image.png",
                    "criteria_url": "https://aws.amazon.com/certification/certified-cloud-practitioner/",
                    "issuer": {"name": "Amazon Web Services"},
                    "tags": ["AWS", "Cloud", "Cloud Computing", "Foundational"]
                }
            },
            {
                "id": "badge_ms_azure_fundamentals",
                "issued_at": "2024-08-20T14:00:00Z",
                "expires_at": None,
                "url": "https://www.credly.com/badges/demo-azure",
                "badge_template": {
                    "id": "tmpl_az_900",
                    "name": "Microsoft Certified: Azure Fundamentals",
                    "description": "Earners of the Azure Fundamentals certification have demonstrated foundational level knowledge of cloud services.",
                    "image_url": "https://images.credly.com/size/340x340/images/be8fcaeb-c769-4858-b567-ffaaa73ce8cf/image.png",
                    "criteria_url": "https://learn.microsoft.com/en-us/certifications/azure-fundamentals/",
                    "issuer": {"name": "Microsoft"},
                    "tags": ["Azure", "Cloud", "Microsoft", "Cloud Fundamentals"]
                }
            },
            {
                "id": "badge_pmp",
                "issued_at": "2023-11-10T09:00:00Z",
                "expires_at": "2026-11-10T09:00:00Z",
                "url": "https://www.credly.com/badges/demo-pmp",
                "badge_template": {
                    "id": "tmpl_pmp",
                    "name": "Project Management Professional (PMP)",
                    "description": "The PMP certification demonstrates competence to lead and direct projects within any organization.",
                    "image_url": "https://images.credly.com/size/340x340/images/260e36dc-d100-45c3-852f-9d8063fa71e6/pmp-600px.png",
                    "criteria_url": "https://www.pmi.org/certifications/project-management-pmp",
                    "issuer": {"name": "Project Management Institute"},
                    "tags": ["Project Management", "Leadership", "PMI", "PMP"]
                }
            },
            {
                "id": "badge_comptia_security",
                "issued_at": "2024-03-05T11:30:00Z",
                "expires_at": "2027-03-05T11:30:00Z",
                "url": "https://www.credly.com/badges/demo-security-plus",
                "badge_template": {
                    "id": "tmpl_sec_plus",
                    "name": "CompTIA Security+",
                    "description": "CompTIA Security+ certified professionals have demonstrated baseline cybersecurity skills.",
                    "image_url": "https://images.credly.com/size/340x340/images/74790a75-8451-400a-8536-92d792c5184a/CompTIA_Security_2Bce.png",
                    "criteria_url": "https://www.comptia.org/certifications/security",
                    "issuer": {"name": "CompTIA"},
                    "tags": ["Cybersecurity", "Security", "CompTIA", "IT Security"]
                }
            },
            {
                "id": "badge_google_cloud",
                "issued_at": "2024-09-01T16:00:00Z",
                "expires_at": "2026-09-01T16:00:00Z",
                "url": "https://www.credly.com/badges/demo-gcp",
                "badge_template": {
                    "id": "tmpl_gcp_ace",
                    "name": "Google Cloud Associate Cloud Engineer",
                    "description": "An Associate Cloud Engineer deploys applications, monitors operations, and manages enterprise solutions.",
                    "image_url": "https://images.credly.com/size/340x340/images/08096465-cbfc-4c3e-93e5-93c5aa61f23e/image.png",
                    "criteria_url": "https://cloud.google.com/certification/cloud-engineer",
                    "issuer": {"name": "Google Cloud"},
                    "tags": ["Google Cloud", "Cloud", "GCP", "Cloud Engineering"]
                }
            }
        ]


# Supported badge issuers for reference
SUPPORTED_BADGE_ISSUERS = [
    {"name": "Amazon Web Services", "badges": ["Cloud Practitioner", "Solutions Architect", "Developer", "SysOps Administrator"]},
    {"name": "Microsoft", "badges": ["Azure Fundamentals", "Azure Administrator", "Azure Developer", "Power Platform"]},
    {"name": "Google Cloud", "badges": ["Associate Cloud Engineer", "Professional Cloud Architect", "Data Engineer"]},
    {"name": "Cisco", "badges": ["CCNA", "CCNP", "DevNet", "CyberOps"]},
    {"name": "CompTIA", "badges": ["A+", "Network+", "Security+", "Cloud+", "CySA+"]},
    {"name": "Project Management Institute", "badges": ["PMP", "CAPM", "PMI-ACP", "PgMP"]},
    {"name": "ISACA", "badges": ["CISA", "CISM", "CRISC", "CGEIT"]},
    {"name": "Salesforce", "badges": ["Administrator", "Developer", "Platform App Builder"]},
    {"name": "Docker", "badges": ["Docker Certified Associate"]},
    {"name": "Kubernetes", "badges": ["CKA", "CKAD", "CKS"]},
    {"name": "HashiCorp", "badges": ["Terraform Associate", "Vault Associate", "Consul Associate"]},
]
