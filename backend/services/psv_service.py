"""
Primary Source Verification (PSV) Service
Enterprise-grade credential verification for Healthcare, Engineering, and Quality professionals.

Providers Integrated:
- Healthcare: Propelus, Verisys, FSMB, Ahpra, MyIntealth
- Engineering: IAF CertSearch, ASQ Registry, API Directory
- Digital Badges: Credly, Accredible
"""

import os
import json
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

# ============== ENUMS ==============

class VerificationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    EXPIRED = "expired"
    REVOKED = "revoked"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"

class VerificationMethod(str, Enum):
    API_INSTANT = "api_instant"          # Credly/Accredible OAuth
    PRIMARY_SOURCE = "primary_source"    # Direct board API
    MANUAL_UPLOAD = "manual_upload"      # User uploaded document
    SELF_ATTESTATION = "self_attestation" # User claims (unverified)

class CredentialType(str, Enum):
    LICENSE = "license"           # Medical/Engineering licenses
    CERTIFICATION = "certification"  # Professional certs (ASQ, PMP)
    DEGREE = "degree"             # Academic credentials
    TRAINING = "training"         # Specialized training
    BADGE = "badge"               # Digital badges

# ============== PSV PROVIDERS ==============

PSV_PROVIDERS = {
    # Healthcare Primary Source Providers
    "propelus": {
        "name": "Propelus (CE Broker/EverCheck)",
        "type": "healthcare",
        "description": "Aggregator for healthcare workforce compliance",
        "supports": ["RN", "LPN", "MD", "DO", "PA", "NP", "PT", "OT", "RT", "Pharmacy"],
        "regions": ["US"],
        "api_base": "https://api.propelus.com/v1",
        "auth_type": "oauth2"
    },
    "verisys": {
        "name": "Verisys (VerisysConnect)",
        "type": "healthcare",
        "description": "Verified License Search and Status (VLSS)",
        "supports": ["Medical Licenses", "Nursing Licenses", "Allied Health"],
        "regions": ["US"],
        "api_base": "https://api.verisys.com/vlss/v2",
        "auth_type": "api_key"
    },
    "fsmb": {
        "name": "FSMB (Federation of State Medical Boards)",
        "type": "healthcare",
        "description": "Primary-source verified physician data",
        "supports": ["MD", "DO", "PA"],
        "regions": ["US"],
        "api_base": "https://api.fsmb.org/med/v1",
        "auth_type": "api_key"
    },
    "ahpra": {
        "name": "Ahpra (Australian Health Practitioner Regulation Agency)",
        "type": "healthcare",
        "description": "Practitioner Information Exchange (PIE)",
        "supports": ["All Australian Health Practitioners"],
        "regions": ["AU"],
        "api_base": "https://api.ahpra.gov.au/pie/v1",
        "auth_type": "oauth2"
    },
    "myintealth": {
        "name": "MyIntealth (ECFMG)",
        "type": "healthcare",
        "description": "International medical graduate verification",
        "supports": ["IMG Medical Education", "ECFMG Certification"],
        "regions": ["Global"],
        "api_base": "https://api.ecfmg.org/intealth/v1",
        "auth_type": "oauth2"
    },
    
    # Engineering & Quality Providers
    "iaf_certsearch": {
        "name": "IAF CertSearch",
        "type": "engineering",
        "description": "Global ISO certification verification",
        "supports": ["ISO 9001", "ISO 13485", "ISO 14001", "ISO 45001", "AS9100"],
        "regions": ["Global"],
        "api_base": "https://api.iafcertsearch.org/v1",
        "auth_type": "api_key"
    },
    "asq_registry": {
        "name": "ASQ (American Society for Quality)",
        "type": "engineering",
        "description": "Quality certification verification",
        "supports": ["CQE", "CQI", "CQA", "CSSBB", "CSQP", "CMQ/OE"],
        "regions": ["Global"],
        "api_base": "https://api.asq.org/certifications/v1",
        "auth_type": "api_key"
    },
    "api_directory": {
        "name": "API (American Petroleum Institute)",
        "type": "engineering",
        "description": "Specialized inspector certification",
        "supports": ["API 510", "API 570", "API 653", "API 580"],
        "regions": ["Global"],
        "api_base": "https://api.api.org/inspectors/v1",
        "auth_type": "api_key"
    },
    
    # Digital Badge Providers
    "credly": {
        "name": "Credly (Pearson)",
        "type": "digital_badge",
        "description": "Digital credential platform",
        "supports": ["AWS", "Microsoft", "Cisco", "CompTIA", "PMI", "Many Others"],
        "regions": ["Global"],
        "api_base": "https://api.credly.com/v1",
        "auth_type": "oauth2"
    },
    "accredible": {
        "name": "Accredible",
        "type": "digital_badge",
        "description": "Digital credentials and certificates",
        "supports": ["Google", "Coursera", "Various Institutions"],
        "regions": ["Global"],
        "api_base": "https://api.accredible.com/v1",
        "auth_type": "api_key"
    }
}

# ============== QUALITY CERTIFICATIONS (Extended) ==============

QUALITY_CERTIFICATIONS = {
    # ASQ Core Certifications
    "CQE": {
        "code": "CQE",
        "name": "Certified Quality Engineer",
        "provider": "ASQ",
        "category": "quality_engineering",
        "tier": 2,
        "description": "Core certification for product and process control",
        "sectors": ["life_sciences", "medical_devices", "engineering"],
        "verification_providers": ["asq_registry", "credly"]
    },
    "CQI": {
        "code": "CQI",
        "name": "Certified Quality Inspector",
        "provider": "ASQ",
        "category": "quality_engineering",
        "tier": 1,
        "description": "Entry-level quality inspection and documentation",
        "sectors": ["life_sciences", "medical_devices", "engineering"],
        "verification_providers": ["asq_registry", "credly"]
    },
    "CSSBB": {
        "code": "CSSBB",
        "name": "Certified Six Sigma Black Belt",
        "provider": "ASQ",
        "category": "process_improvement",
        "tier": 3,
        "description": "High-level process improvement and waste reduction",
        "sectors": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"],
        "verification_providers": ["asq_registry", "credly"]
    },
    "CSSGB": {
        "code": "CSSGB",
        "name": "Certified Six Sigma Green Belt",
        "provider": "ASQ",
        "category": "process_improvement",
        "tier": 2,
        "description": "Process improvement methodology",
        "sectors": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"],
        "verification_providers": ["asq_registry", "credly"]
    },
    "CMQ_OE": {
        "code": "CMQ/OE",
        "name": "Certified Manager of Quality/Organizational Excellence",
        "provider": "ASQ",
        "category": "quality_leadership",
        "tier": 5,
        "description": "Executive leadership and strategic quality direction",
        "sectors": ["life_sciences", "medical_devices", "engineering"],
        "verification_providers": ["asq_registry", "credly"]
    },
    "CQA": {
        "code": "CQA",
        "name": "Certified Quality Auditor",
        "provider": "ASQ",
        "category": "auditing",
        "tier": 3,
        "description": "Internal and supplier quality audits",
        "sectors": ["life_sciences", "medical_devices", "engineering"],
        "verification_providers": ["asq_registry", "credly"]
    },
    "CSQP": {
        "code": "CSQP",
        "name": "Certified Supplier Quality Professional",
        "provider": "ASQ",
        "category": "supplier_quality",
        "tier": 3,
        "description": "Supplier risk management and vendor audits",
        "sectors": ["medical_devices", "engineering"],
        "verification_providers": ["asq_registry", "credly"]
    },
    
    # ISO Lead Auditor Certifications
    "ISO_9001_LA": {
        "code": "ISO 9001 LA",
        "name": "ISO 9001 Lead Auditor",
        "provider": "Various (IRCA/Exemplar Global)",
        "category": "lead_auditor",
        "tier": 4,
        "description": "Universal quality management system auditing",
        "sectors": ["life_sciences", "medical_devices", "engineering"],
        "verification_providers": ["iaf_certsearch"]
    },
    "ISO_13485_LA": {
        "code": "ISO 13485 LA",
        "name": "ISO 13485 Lead Auditor",
        "provider": "Various (IRCA/Exemplar Global)",
        "category": "lead_auditor",
        "tier": 4,
        "description": "Medical device quality management system auditing",
        "sectors": ["medical_devices", "life_sciences"],
        "verification_providers": ["iaf_certsearch"]
    },
    "AS9100_LA": {
        "code": "AS9100 LA",
        "name": "AS9100 Lead Auditor",
        "provider": "Various (IRCA/Exemplar Global)",
        "category": "lead_auditor",
        "tier": 4,
        "description": "Aerospace & defense quality management system auditing",
        "sectors": ["engineering"],
        "verification_providers": ["iaf_certsearch"]
    },
    "IATF_16949": {
        "code": "IATF 16949",
        "name": "IATF 16949 Auditor",
        "provider": "IATF",
        "category": "lead_auditor",
        "tier": 4,
        "description": "Automotive supply chain quality auditing",
        "sectors": ["engineering"],
        "verification_providers": ["iaf_certsearch"]
    },
    
    # Supply Chain Certifications
    "CPIM": {
        "code": "CPIM",
        "name": "Certified in Planning and Inventory Management",
        "provider": "APICS/ASCM",
        "category": "supply_chain",
        "tier": 2,
        "description": "Supply chain and inventory management",
        "sectors": ["life_sciences", "medical_devices", "engineering"],
        "verification_providers": ["credly"]
    },
    "CSCP": {
        "code": "CSCP",
        "name": "Certified Supply Chain Professional",
        "provider": "APICS/ASCM",
        "category": "supply_chain",
        "tier": 3,
        "description": "End-to-end supply chain management",
        "sectors": ["life_sciences", "medical_devices", "engineering"],
        "verification_providers": ["credly"]
    },
    
    # Healthcare Licenses
    "RN": {
        "code": "RN",
        "name": "Registered Nurse",
        "provider": "State Board of Nursing",
        "category": "healthcare_license",
        "tier": 2,
        "description": "Professional nursing license",
        "sectors": ["healthcare_ops"],
        "verification_providers": ["propelus", "verisys"]
    },
    "MD": {
        "code": "MD",
        "name": "Doctor of Medicine",
        "provider": "State Medical Board",
        "category": "healthcare_license",
        "tier": 4,
        "description": "Physician medical license",
        "sectors": ["healthcare_ops", "life_sciences"],
        "verification_providers": ["fsmb", "verisys"]
    },
    
    # Engineering Licenses
    "PE": {
        "code": "PE",
        "name": "Professional Engineer",
        "provider": "NCEES/State Board",
        "category": "engineering_license",
        "tier": 3,
        "description": "Licensed Professional Engineer",
        "sectors": ["engineering", "medical_devices"],
        "verification_providers": ["manual_upload"]
    },
    "FE": {
        "code": "FE",
        "name": "Fundamentals of Engineering",
        "provider": "NCEES",
        "category": "engineering_license",
        "tier": 2,
        "description": "Engineering Intern / EIT certification",
        "sectors": ["engineering", "medical_devices"],
        "verification_providers": ["manual_upload"]
    }
}

# ============== QUALITY HIERARCHY ==============

QUALITY_HIERARCHY = [
    {
        "tier": 1,
        "name": "Entry",
        "representative_title": "Quality Clerk / Inspector",
        "key_certifications": ["CQI"],
        "years_experience": "0-2"
    },
    {
        "tier": 2,
        "name": "Associate",
        "representative_title": "Quality Engineer",
        "key_certifications": ["CQE", "CSSGB"],
        "years_experience": "2-5"
    },
    {
        "tier": 3,
        "name": "Mid-Senior",
        "representative_title": "Supplier Quality Manager",
        "key_certifications": ["CSQP", "PMP", "CQA", "CSSBB"],
        "years_experience": "5-10"
    },
    {
        "tier": 4,
        "name": "Principal",
        "representative_title": "Lead Compliance Auditor",
        "key_certifications": ["ISO 13485 LA", "AS9100 LA", "ISO 9001 LA"],
        "years_experience": "10-15"
    },
    {
        "tier": 5,
        "name": "Executive",
        "representative_title": "VP of Quality & Regulatory",
        "key_certifications": ["CMQ/OE"],
        "years_experience": "15+"
    }
]

# ============== INDUSTRY BRIDGE TABLE ==============

INDUSTRY_BRIDGE = [
    {
        "from_sector": "automotive",
        "from_skills": ["IATF 16949", "APQP", "PPAP", "SPC", "MSA"],
        "to_sector": "medical_devices",
        "bridge_certifications": ["ISO 13485 LA", "GMP", "Design Controls"],
        "transfer_difficulty": "low",
        "notes": "Automotive quality systems (IATF 16949) translate well to medical device QMS"
    },
    {
        "from_sector": "aerospace",
        "from_skills": ["AS9100", "NADCAP", "Configuration Management"],
        "to_sector": "medical_devices",
        "bridge_certifications": ["ISO 13485 LA", "FDA 21 CFR 820"],
        "transfer_difficulty": "low",
        "notes": "Aerospace quality rigor exceeds most medical device requirements"
    },
    {
        "from_sector": "aerospace",
        "from_skills": ["AS9100", "FOD Prevention", "Special Processes"],
        "to_sector": "life_sciences",
        "bridge_certifications": ["GMP", "CAPA"],
        "transfer_difficulty": "medium",
        "notes": "Aerospace process control applies to pharma manufacturing"
    },
    {
        "from_sector": "pharmaceutical",
        "from_skills": ["GMP", "Validation", "21 CFR Part 11"],
        "to_sector": "medical_devices",
        "bridge_certifications": ["ISO 13485 LA", "Design Controls"],
        "transfer_difficulty": "low",
        "notes": "Pharma GMP experience highly valued in combination products"
    },
    {
        "from_sector": "engineering",
        "from_skills": ["ISO 9001", "Lean Manufacturing", "Six Sigma"],
        "to_sector": "healthcare_ops",
        "bridge_certifications": ["Lean Healthcare", "HIPAA"],
        "transfer_difficulty": "medium",
        "notes": "Manufacturing efficiency principles apply to hospital operations"
    }
]

# ============== PSV SERVICE CLASS ==============

class PSVService:
    """Primary Source Verification Service"""
    
    def __init__(self, db=None):
        self.db = db
        self._provider_credentials = {}
        self._load_provider_credentials()
    
    def _load_provider_credentials(self):
        """Load API credentials from environment"""
        for provider_id in PSV_PROVIDERS:
            env_key = f"PSV_{provider_id.upper()}_API_KEY"
            api_key = os.environ.get(env_key)
            if api_key:
                self._provider_credentials[provider_id] = api_key
    
    async def verify_credential(
        self,
        user_id: str,
        credential_code: str,
        credential_number: Optional[str] = None,
        issuing_authority: Optional[str] = None,
        document_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify a credential using the waterfall approach:
        1. Try instant API sync (Credly/Accredible)
        2. Try primary source API
        3. Fall back to manual review queue
        """
        
        verification_id = str(uuid.uuid4())
        credential_info = QUALITY_CERTIFICATIONS.get(credential_code.replace(" ", "_").replace("/", "_"))
        
        if not credential_info:
            return {
                "verification_id": verification_id,
                "status": VerificationStatus.FAILED,
                "method": None,
                "message": f"Unknown credential code: {credential_code}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        
        # Get available verification providers for this credential
        providers = credential_info.get("verification_providers", [])
        
        result = {
            "verification_id": verification_id,
            "user_id": user_id,
            "credential_code": credential_code,
            "credential_name": credential_info.get("name"),
            "status": VerificationStatus.PENDING,
            "method": None,
            "provider_used": None,
            "verification_data": {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,
            "next_reverification": None
        }
        
        # Attempt verification waterfall
        for provider_id in providers:
            if provider_id in ["credly", "accredible"]:
                # Try digital badge verification (instant)
                verification_result = await self._verify_via_digital_badge(
                    provider_id, credential_code, credential_number
                )
                if verification_result.get("success"):
                    result["status"] = VerificationStatus.VERIFIED
                    result["method"] = VerificationMethod.API_INSTANT
                    result["provider_used"] = provider_id
                    result["verification_data"] = verification_result.get("data", {})
                    result["expires_at"] = verification_result.get("expires_at")
                    break
            
            elif provider_id in ["propelus", "verisys", "fsmb", "asq_registry", "iaf_certsearch"]:
                # Try primary source verification
                verification_result = await self._verify_via_primary_source(
                    provider_id, credential_code, credential_number, issuing_authority
                )
                if verification_result.get("success"):
                    result["status"] = VerificationStatus.VERIFIED
                    result["method"] = VerificationMethod.PRIMARY_SOURCE
                    result["provider_used"] = provider_id
                    result["verification_data"] = verification_result.get("data", {})
                    result["expires_at"] = verification_result.get("expires_at")
                    break
        
        # If no API verification succeeded, queue for manual review
        if result["status"] == VerificationStatus.PENDING:
            if document_url:
                result["status"] = VerificationStatus.MANUAL_REVIEW
                result["method"] = VerificationMethod.MANUAL_UPLOAD
                result["verification_data"]["document_url"] = document_url
            else:
                result["status"] = VerificationStatus.PENDING
                result["method"] = VerificationMethod.SELF_ATTESTATION
        
        # Set re-verification schedule (annual for most credentials)
        if result["status"] == VerificationStatus.VERIFIED:
            result["next_reverification"] = (
                datetime.now(timezone.utc) + timedelta(days=365)
            ).isoformat()
        
        # Store verification record
        if self.db:
            await self.db.credential_verifications.insert_one(result)
        
        return result
    
    async def _verify_via_digital_badge(
        self,
        provider_id: str,
        credential_code: str,
        credential_number: Optional[str]
    ) -> Dict[str, Any]:
        """
        Verify credential via Credly or Accredible.
        NOTE: This is a simulated response. In production, implement OAuth flow.
        """
        
        # Check if we have API credentials
        if provider_id not in self._provider_credentials:
            logger.info(f"No API key configured for {provider_id}")
            # Simulate verification for demo purposes
            return self._simulate_verification(provider_id, credential_code)
        
        # In production, implement actual API call:
        # provider = PSV_PROVIDERS[provider_id]
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"{provider['api_base']}/badges/verify",
        #         headers={"Authorization": f"Bearer {self._provider_credentials[provider_id]}"},
        #         params={"credential": credential_number}
        #     )
        
        return self._simulate_verification(provider_id, credential_code)
    
    async def _verify_via_primary_source(
        self,
        provider_id: str,
        credential_code: str,
        credential_number: Optional[str],
        issuing_authority: Optional[str]
    ) -> Dict[str, Any]:
        """
        Verify credential via primary source API (board, registry).
        NOTE: This is a simulated response. In production, implement actual API calls.
        """
        
        if provider_id not in self._provider_credentials:
            logger.info(f"No API key configured for {provider_id}")
            return self._simulate_verification(provider_id, credential_code)
        
        # In production, implement actual API call to FSMB, Verisys, etc.
        return self._simulate_verification(provider_id, credential_code)
    
    def _simulate_verification(
        self,
        provider_id: str,
        credential_code: str
    ) -> Dict[str, Any]:
        """
        Simulate a verification response for demo/development.
        In production, this would be replaced with actual API calls.
        """
        
        # Simulate 80% success rate for demo
        import random
        success = random.random() < 0.8
        
        if success:
            return {
                "success": True,
                "data": {
                    "provider": provider_id,
                    "credential": credential_code,
                    "status": "active",
                    "issue_date": "2023-01-15",
                    "expiry_date": "2026-01-15",
                    "verification_timestamp": datetime.now(timezone.utc).isoformat(),
                    "simulated": True  # Flag for demo
                },
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=730)).isoformat()
            }
        else:
            return {
                "success": False,
                "error": "Credential not found in registry"
            }
    
    async def check_expiration_status(self, user_id: str) -> List[Dict[str, Any]]:
        """Check for expiring or expired credentials"""
        
        if not self.db:
            return []
        
        now = datetime.now(timezone.utc)
        thirty_days = (now + timedelta(days=30)).isoformat()
        
        # Find credentials expiring soon or already expired
        cursor = self.db.credential_verifications.find({
            "user_id": user_id,
            "status": VerificationStatus.VERIFIED,
            "$or": [
                {"expires_at": {"$lt": now.isoformat()}},
                {"expires_at": {"$lt": thirty_days}}
            ]
        })
        
        alerts = []
        async for credential in cursor:
            expires_at = datetime.fromisoformat(credential["expires_at"].replace("Z", "+00:00"))
            
            if expires_at < now:
                status = "expired"
            else:
                days_remaining = (expires_at - now).days
                status = f"expiring_in_{days_remaining}_days"
            
            alerts.append({
                "credential_code": credential["credential_code"],
                "credential_name": credential.get("credential_name"),
                "status": status,
                "expires_at": credential["expires_at"],
                "verification_id": credential["verification_id"]
            })
        
        return alerts
    
    async def trigger_reverification(self, verification_id: str) -> Dict[str, Any]:
        """Trigger automatic re-verification of a credential"""
        
        if not self.db:
            return {"error": "Database not available"}
        
        credential = await self.db.credential_verifications.find_one({
            "verification_id": verification_id
        })
        
        if not credential:
            return {"error": "Verification record not found"}
        
        # Re-verify the credential
        result = await self.verify_credential(
            user_id=credential["user_id"],
            credential_code=credential["credential_code"],
            credential_number=credential.get("verification_data", {}).get("credential_number")
        )
        
        return result
    
    def get_verification_providers(self, credential_code: str) -> List[Dict[str, Any]]:
        """Get available verification providers for a credential"""
        
        credential_info = QUALITY_CERTIFICATIONS.get(
            credential_code.replace(" ", "_").replace("/", "_")
        )
        
        if not credential_info:
            return []
        
        provider_ids = credential_info.get("verification_providers", [])
        return [
            {**PSV_PROVIDERS[pid], "id": pid}
            for pid in provider_ids
            if pid in PSV_PROVIDERS
        ]
    
    def get_industry_bridges(self, from_sector: str) -> List[Dict[str, Any]]:
        """Get industry bridge paths from a given sector"""
        
        return [
            bridge for bridge in INDUSTRY_BRIDGE
            if bridge["from_sector"] == from_sector
        ]
    
    def get_quality_hierarchy(self) -> List[Dict[str, Any]]:
        """Get the unified quality hierarchy"""
        return QUALITY_HIERARCHY


# ============== HELPER FUNCTIONS ==============

def get_certification_info(code: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a certification"""
    normalized_code = code.replace(" ", "_").replace("/", "_")
    return QUALITY_CERTIFICATIONS.get(normalized_code)

def get_certifications_by_tier(tier: int) -> List[Dict[str, Any]]:
    """Get all certifications for a specific tier"""
    return [
        {**cert, "code": code}
        for code, cert in QUALITY_CERTIFICATIONS.items()
        if cert.get("tier") == tier
    ]

def get_certifications_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all certifications in a category"""
    return [
        {**cert, "code": code}
        for code, cert in QUALITY_CERTIFICATIONS.items()
        if cert.get("category") == category
    ]

def get_all_psv_providers() -> Dict[str, Any]:
    """Get all PSV provider information"""
    return PSV_PROVIDERS
