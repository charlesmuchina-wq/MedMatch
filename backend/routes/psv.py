"""
Primary Source Verification (PSV) Hub
Free self-service verification using public databases

Integrations:
- OIG LEIE (Office of Inspector General - List of Excluded Individuals/Entities)
- CMS NPI Registry (National Provider Identifier)
- ORCID Public API (Researcher identity & publications)
- Hipo University API (Global university search)
- Links to WHED, FSMB, NCEES, regional registries for manual verification
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from bson import ObjectId
import httpx
import logging
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/psv", tags=["Primary Source Verification"])

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "medmatch")

from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Collections
credentials_collection = db["psv_credentials"]
verification_logs_collection = db["psv_verification_logs"]


# ==================== MODELS ====================

class CredentialRecord(BaseModel):
    candidate_id: str
    candidate_name: str
    credential_type: str  # license, degree, certification, npi, orcid, etc.
    credential_number: Optional[str] = None
    issuing_authority: str
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    verification_status: str = "pending"  # pending, verified, expired, revoked, not_found
    last_verified: Optional[str] = None
    verification_source: Optional[str] = None
    notes: Optional[str] = None


class OIGSearchRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    npi: Optional[str] = None
    state: Optional[str] = None


class NPISearchRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    npi: Optional[str] = None
    state: Optional[str] = None
    taxonomy: Optional[str] = None
    organization_name: Optional[str] = None


class ORCIDSearchRequest(BaseModel):
    orcid_id: Optional[str] = None  # Format: 0000-0000-0000-0000
    family_name: Optional[str] = None
    given_names: Optional[str] = None
    affiliation: Optional[str] = None
    keyword: Optional[str] = None


class UniversitySearchRequest(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None


# ==================== VERIFICATION RESOURCES ====================

VERIFICATION_RESOURCES = {
    "medical_license": {
        "name": "Medical License Verification",
        "icon": "stethoscope",
        "sources": [
            {
                "name": "Federation of State Medical Boards (FSMB)",
                "url": "https://www.fsmb.org/physician-data-center/",
                "description": "Verify physician licenses across all US states",
                "cost": "Fee per search (paid by recruiter)",
                "region": "United States"
            },
            {
                "name": "State Medical Boards Directory",
                "url": "https://www.fsmb.org/contact-a-state-medical-board/",
                "description": "Direct links to individual state medical boards",
                "cost": "Free (varies by state)",
                "region": "United States"
            },
            {
                "name": "GMC Register (UK)",
                "url": "https://www.gmc-uk.org/registration-and-licensing/the-medical-register",
                "description": "General Medical Council - UK physician register",
                "cost": "Free",
                "region": "United Kingdom"
            }
        ]
    },
    "nursing_license": {
        "name": "Nursing License Verification",
        "icon": "heart-pulse",
        "sources": [
            {
                "name": "Nursys License Verification",
                "url": "https://www.nursys.com/",
                "description": "National database for RN and LPN/VN licenses",
                "cost": "Free quick confirm / Fee for detailed report",
                "region": "United States"
            }
        ]
    },
    "engineering_license": {
        "name": "Engineering License Verification",
        "icon": "cog",
        "sources": [
            {
                "name": "NCEES License Lookup",
                "url": "https://account.ncees.org/profile/verification",
                "description": "National Council of Examiners for Engineering and Surveying",
                "cost": "Free",
                "region": "United States"
            },
            {
                "name": "APEC Engineer Register",
                "url": "https://www.apec-engineers.org/",
                "description": "Professional engineers across Japan, Australia, and APEC nations",
                "cost": "Free",
                "region": "Asia-Pacific"
            },
            {
                "name": "Engineering Council (UK)",
                "url": "https://www.engc.org.uk/registrant-search/",
                "description": "UK Chartered Engineer (CEng) verification",
                "cost": "Free",
                "region": "United Kingdom"
            }
        ]
    },
    "pharmacy_license": {
        "name": "Pharmacy License Verification",
        "icon": "pill",
        "sources": [
            {
                "name": "NABP License Verification",
                "url": "https://nabp.pharmacy/",
                "description": "National Association of Boards of Pharmacy",
                "cost": "Varies by state",
                "region": "United States"
            },
            {
                "name": "DEA Registration Verification",
                "url": "https://apps.deadiversion.usdoj.gov/webforms2/spring/validationLogin",
                "description": "Verify DEA registration for controlled substances",
                "cost": "Free",
                "region": "United States"
            }
        ]
    },
    "degree_verification": {
        "name": "Education/Degree Verification",
        "icon": "graduation-cap",
        "sources": [
            {
                "name": "National Student Clearinghouse",
                "url": "https://www.studentclearinghouse.org/verifiers/",
                "description": "Verify degrees from 3,600+ participating US institutions",
                "cost": "Fee per verification",
                "region": "United States"
            },
            {
                "name": "WHED (World Higher Education Database)",
                "url": "https://www.whed.net/home.php",
                "description": "UNESCO/IAU database - 22,000+ accredited institutions globally",
                "cost": "Free portal",
                "region": "Global"
            },
            {
                "name": "ENIC-NARIC Network",
                "url": "https://www.enic-naric.net/",
                "description": "Official credential recognition bodies in 55+ countries",
                "cost": "Free directory",
                "region": "Europe"
            },
            {
                "name": "Europass Digital Credentials",
                "url": "https://europa.eu/europass/digital-credentials/",
                "description": "W3C Verifiable Credentials for EU degrees",
                "cost": "Free",
                "region": "European Union"
            }
        ]
    },
    "degree_regional": {
        "name": "Regional Degree Verification",
        "icon": "globe",
        "sources": [
            {
                "name": "China CHSI (学信网)",
                "url": "https://www.chsi.com.cn/en/",
                "description": "Official Chinese degree verification (MOE-authorized)",
                "cost": "Free verification code",
                "region": "China"
            },
            {
                "name": "Brazil e-MEC",
                "url": "https://emec.mec.gov.br/",
                "description": "Official Brazilian Ministry of Education registry",
                "cost": "Free",
                "region": "Brazil"
            },
            {
                "name": "Mexico Cédula Profesional",
                "url": "https://www.cedulaprofesional.sep.gob.mx/cedula/presidencia/indexAvanzada.action",
                "description": "Free professional license database",
                "cost": "Free",
                "region": "Mexico"
            },
            {
                "name": "Peru SUNEDU",
                "url": "https://www.sunedu.gob.pe/sibe/",
                "description": "Free university degree registry",
                "cost": "Free",
                "region": "Peru"
            },
            {
                "name": "Chile - Superintendencia de Salud",
                "url": "https://www.supersalud.gob.cl/consultas/571/w3-propertyvalue-4038.html",
                "description": "Health & lab professionals registry",
                "cost": "Free",
                "region": "Chile"
            }
        ]
    },
    "researcher_identity": {
        "name": "Researcher Identity & Publications",
        "icon": "flask",
        "sources": [
            {
                "name": "ORCID Registry",
                "url": "https://orcid.org/",
                "description": "Global researcher ID with verified education & publications - FREE API",
                "cost": "Free",
                "region": "Global",
                "api_available": True
            },
            {
                "name": "PubMed Author Search",
                "url": "https://pubmed.ncbi.nlm.nih.gov/",
                "description": "Verify life sciences publications",
                "cost": "Free",
                "region": "Global"
            },
            {
                "name": "DBCLS (Japan Life Science)",
                "url": "https://dbcls.rois.ac.jp/en/",
                "description": "Japanese life science database center",
                "cost": "Free",
                "region": "Japan"
            }
        ]
    },
    "exclusion_sanction": {
        "name": "Exclusion & Sanction Checks",
        "icon": "shield-exclamation",
        "sources": [
            {
                "name": "OIG LEIE Database",
                "url": "https://exclusions.oig.hhs.gov/",
                "description": "List of Excluded Individuals/Entities - FREE API",
                "cost": "Free",
                "region": "United States",
                "api_available": True
            },
            {
                "name": "SAM.gov Exclusions",
                "url": "https://sam.gov/content/exclusions",
                "description": "System for Award Management exclusions",
                "cost": "Free",
                "region": "United States"
            },
            {
                "name": "FDA Debarment List",
                "url": "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/fda-debarment-list-drug-product-applications",
                "description": "FDA debarred individuals and firms",
                "cost": "Free",
                "region": "United States"
            }
        ]
    },
    "npi_verification": {
        "name": "NPI Verification",
        "icon": "id-card",
        "sources": [
            {
                "name": "CMS NPI Registry",
                "url": "https://npiregistry.cms.hhs.gov/",
                "description": "National Provider Identifier lookup - FREE API",
                "cost": "Free",
                "region": "United States",
                "api_available": True
            }
        ]
    },
    "business_verification": {
        "name": "Business/Employer Verification",
        "icon": "building",
        "sources": [
            {
                "name": "Companies House (UK)",
                "url": "https://find-and-update.company-information.service.gov.uk/",
                "description": "Free API for UK business registration data",
                "cost": "Free API",
                "region": "United Kingdom",
                "api_available": True
            },
            {
                "name": "China NECIPS",
                "url": "https://www.gsxt.gov.cn/",
                "description": "National Enterprise Credit Information (Unified Social Credit Code)",
                "cost": "Free",
                "region": "China"
            },
            {
                "name": "SEC EDGAR (US)",
                "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany",
                "description": "US public company filings",
                "cost": "Free",
                "region": "United States"
            }
        ]
    },
    "certifications": {
        "name": "Professional Certifications",
        "icon": "certificate",
        "sources": [
            {
                "name": "Credential Engine Registry",
                "url": "https://credentialfinder.org/",
                "description": "Global registry of credentials, certifications, and licenses - FREE API",
                "cost": "Free",
                "region": "Global",
                "api_available": True
            },
            {
                "name": "Credly Verification",
                "url": "https://www.credly.com/",
                "description": "Digital badges and certifications",
                "cost": "Free verification",
                "region": "Global"
            }
        ]
    }
}


# ==================== OIG LEIE ENDPOINTS ====================

@router.post("/oig/search")
async def search_oig_leie(request: OIGSearchRequest):
    """
    Search the OIG LEIE (List of Excluded Individuals/Entities) database.
    This is a FREE public API for checking healthcare exclusions.
    
    An exclusion means the individual/entity cannot participate in 
    federal healthcare programs (Medicare, Medicaid, etc.)
    """
    try:
        # Build query parameters
        params = {}
        if request.first_name:
            params["firstname"] = request.first_name
        if request.last_name:
            params["lastname"] = request.last_name
        if request.npi:
            params["npi"] = request.npi
        if request.state:
            params["state"] = request.state
        
        if not params:
            raise HTTPException(status_code=400, detail="At least one search parameter required")
        
        # OIG LEIE REST API endpoint
        oig_api_url = "https://oig.hhs.gov/exclusions/rest/api"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                oig_api_url,
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Log the verification
                await verification_logs_collection.insert_one({
                    "type": "oig_leie",
                    "search_params": params,
                    "results_count": len(data) if isinstance(data, list) else 0,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "success"
                })
                
                return {
                    "success": True,
                    "source": "OIG LEIE Database",
                    "source_url": "https://exclusions.oig.hhs.gov/",
                    "search_params": params,
                    "results": data if isinstance(data, list) else [],
                    "results_count": len(data) if isinstance(data, list) else 0,
                    "exclusion_found": len(data) > 0 if isinstance(data, list) else False,
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                    "disclaimer": "This search queries the official OIG LEIE database. An exclusion means the individual cannot participate in federal healthcare programs."
                }
            else:
                # API might be down, return guidance
                return {
                    "success": False,
                    "error": f"OIG API returned status {response.status_code}",
                    "fallback_url": "https://exclusions.oig.hhs.gov/",
                    "instruction": "Please search manually on the OIG website"
                }
                
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "OIG API timeout",
            "fallback_url": "https://exclusions.oig.hhs.gov/",
            "instruction": "Please search manually on the OIG website"
        }
    except Exception as e:
        logger.error(f"OIG search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "fallback_url": "https://exclusions.oig.hhs.gov/",
            "instruction": "Please search manually on the OIG website"
        }


# ==================== NPI REGISTRY ENDPOINTS ====================

@router.post("/npi/search")
async def search_npi_registry(request: NPISearchRequest):
    """
    Search the CMS NPI Registry.
    This is a FREE public API for verifying healthcare provider identifiers.
    
    NPI (National Provider Identifier) is a unique 10-digit number 
    assigned to healthcare providers in the US.
    """
    try:
        # Build query parameters for NPPES API
        params = {"version": "2.1"}
        
        if request.npi:
            params["number"] = request.npi
        if request.first_name:
            params["first_name"] = request.first_name
        if request.last_name:
            params["last_name"] = request.last_name
        if request.state:
            params["state"] = request.state
        if request.taxonomy:
            params["taxonomy_description"] = request.taxonomy
        if request.organization_name:
            params["organization_name"] = request.organization_name
        
        if len(params) <= 1:  # Only version param
            raise HTTPException(status_code=400, detail="At least one search parameter required")
        
        # CMS NPPES NPI Registry API
        npi_api_url = "https://npiregistry.cms.hhs.gov/api/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                npi_api_url,
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # Parse results for cleaner output
                parsed_results = []
                for result in results[:20]:  # Limit to 20 results
                    basic = result.get("basic", {})
                    addresses = result.get("addresses", [])
                    taxonomies = result.get("taxonomies", [])
                    
                    # Get primary practice address
                    practice_address = None
                    for addr in addresses:
                        if addr.get("address_purpose") == "LOCATION":
                            practice_address = {
                                "address": f"{addr.get('address_1', '')} {addr.get('address_2', '')}".strip(),
                                "city": addr.get("city"),
                                "state": addr.get("state"),
                                "postal_code": addr.get("postal_code"),
                                "phone": addr.get("telephone_number")
                            }
                            break
                    
                    # Get primary taxonomy
                    primary_taxonomy = None
                    for tax in taxonomies:
                        if tax.get("primary"):
                            primary_taxonomy = {
                                "code": tax.get("code"),
                                "description": tax.get("desc"),
                                "license": tax.get("license"),
                                "state": tax.get("state")
                            }
                            break
                    
                    parsed_results.append({
                        "npi": result.get("number"),
                        "entity_type": "Individual" if result.get("enumeration_type") == "NPI-1" else "Organization",
                        "name": {
                            "first": basic.get("first_name"),
                            "last": basic.get("last_name"),
                            "credential": basic.get("credential"),
                            "organization": basic.get("organization_name")
                        },
                        "status": basic.get("status"),
                        "enumeration_date": basic.get("enumeration_date"),
                        "last_updated": basic.get("last_updated"),
                        "practice_address": practice_address,
                        "primary_taxonomy": primary_taxonomy
                    })
                
                # Log the verification
                await verification_logs_collection.insert_one({
                    "type": "npi_registry",
                    "search_params": {k: v for k, v in params.items() if k != "version"},
                    "results_count": len(parsed_results),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "status": "success"
                })
                
                return {
                    "success": True,
                    "source": "CMS NPI Registry",
                    "source_url": "https://npiregistry.cms.hhs.gov/",
                    "search_params": {k: v for k, v in params.items() if k != "version"},
                    "results": parsed_results,
                    "results_count": data.get("result_count", 0),
                    "checked_at": datetime.now(timezone.utc).isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"NPI Registry API returned status {response.status_code}",
                    "fallback_url": "https://npiregistry.cms.hhs.gov/",
                    "instruction": "Please search manually on the NPI Registry website"
                }
                
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "NPI Registry API timeout",
            "fallback_url": "https://npiregistry.cms.hhs.gov/",
            "instruction": "Please search manually on the NPI Registry website"
        }
    except Exception as e:
        logger.error(f"NPI search error: {e}")
        return {
            "success": False,
            "error": str(e),
            "fallback_url": "https://npiregistry.cms.hhs.gov/",
            "instruction": "Please search manually on the NPI Registry website"
        }


# ==================== VERIFICATION RESOURCES ENDPOINTS ====================

@router.get("/resources")
async def get_verification_resources():
    """Get all available verification resources organized by category."""
    return {
        "resources": VERIFICATION_RESOURCES,
        "free_apis": ["oig_leie", "npi_registry"],
        "description": "Self-service verification hub for primary source verification"
    }


@router.get("/resources/{category}")
async def get_resource_category(category: str):
    """Get verification resources for a specific category."""
    if category not in VERIFICATION_RESOURCES:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
    return VERIFICATION_RESOURCES[category]


# ==================== CREDENTIAL TRACKING ENDPOINTS ====================

@router.post("/credentials")
async def create_credential(credential: CredentialRecord):
    """Create a new credential record for tracking."""
    doc = credential.dict()
    doc["created_at"] = datetime.now(timezone.utc).isoformat()
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    result = await credentials_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    del doc["_id"] if "_id" in doc else None
    
    return {
        "success": True,
        "credential_id": str(result.inserted_id),
        "message": "Credential record created"
    }


@router.get("/credentials/{candidate_id}")
async def get_candidate_credentials(candidate_id: str):
    """Get all credentials for a candidate."""
    credentials = await credentials_collection.find(
        {"candidate_id": candidate_id}
    ).to_list(100)
    
    # Convert ObjectId to string
    for cred in credentials:
        cred["_id"] = str(cred["_id"])
    
    return {
        "candidate_id": candidate_id,
        "credentials": credentials,
        "count": len(credentials)
    }


@router.put("/credentials/{credential_id}")
async def update_credential(
    credential_id: str,
    verification_status: str = Body(...),
    verification_source: Optional[str] = Body(None),
    notes: Optional[str] = Body(None)
):
    """Update a credential's verification status."""
    update_doc = {
        "verification_status": verification_status,
        "last_verified": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if verification_source:
        update_doc["verification_source"] = verification_source
    if notes:
        update_doc["notes"] = notes
    
    result = await credentials_collection.update_one(
        {"_id": ObjectId(credential_id)},
        {"$set": update_doc}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    return {
        "success": True,
        "message": "Credential updated",
        "credential_id": credential_id
    }


@router.get("/credentials/expiring/soon")
async def get_expiring_credentials(days: int = Query(30, description="Days until expiration")):
    """Get credentials expiring within the specified number of days."""
    cutoff_date = (datetime.now(timezone.utc) + timedelta(days=days)).strftime("%Y-%m-%d")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Find credentials with expiration dates in the range
    expiring = await credentials_collection.find({
        "expiration_date": {"$gte": today, "$lte": cutoff_date},
        "verification_status": {"$ne": "expired"}
    }).to_list(100)
    
    for cred in expiring:
        cred["_id"] = str(cred["_id"])
    
    return {
        "expiring_within_days": days,
        "credentials": expiring,
        "count": len(expiring),
        "alert_date": cutoff_date
    }


# ==================== VERIFICATION LOGS ====================

@router.get("/logs")
async def get_verification_logs(
    limit: int = Query(50, le=200),
    type_filter: Optional[str] = Query(None, description="Filter by verification type")
):
    """Get verification activity logs."""
    query = {}
    if type_filter:
        query["type"] = type_filter
    
    logs = await verification_logs_collection.find(query).sort(
        "timestamp", -1
    ).limit(limit).to_list(limit)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return {
        "logs": logs,
        "count": len(logs)
    }


# ==================== DASHBOARD STATS ====================

@router.get("/dashboard/stats")
async def get_psv_dashboard_stats():
    """Get PSV dashboard statistics."""
    total_credentials = await credentials_collection.count_documents({})
    pending = await credentials_collection.count_documents({"verification_status": "pending"})
    verified = await credentials_collection.count_documents({"verification_status": "verified"})
    expired = await credentials_collection.count_documents({"verification_status": "expired"})
    revoked = await credentials_collection.count_documents({"verification_status": "revoked"})
    
    # Get expiring soon count (30 days)
    cutoff_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expiring_soon = await credentials_collection.count_documents({
        "expiration_date": {"$gte": today, "$lte": cutoff_date},
        "verification_status": {"$ne": "expired"}
    })
    
    # Get verification counts for today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0).isoformat()
    verifications_today = await verification_logs_collection.count_documents({
        "timestamp": {"$gte": today_start}
    })
    
    return {
        "total_credentials": total_credentials,
        "by_status": {
            "pending": pending,
            "verified": verified,
            "expired": expired,
            "revoked": revoked
        },
        "expiring_soon_30_days": expiring_soon,
        "verifications_today": verifications_today,
        "free_apis_available": ["OIG LEIE", "CMS NPI Registry"],
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
