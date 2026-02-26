"""
KARAU Enterprise SSO/SAML Integration
Handles: SAML 2.0 configuration, SSO login flow, IdP metadata
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timezone
import uuid
import base64
import zlib
import logging
import urllib.parse
import xml.etree.ElementTree as ET

from utils.database import db
from routes.auth import require_auth, create_session_token, create_session, get_or_create_user

router = APIRouter(prefix="/karau-meet/sso", tags=["KARAU Enterprise SSO"])
logger = logging.getLogger(__name__)


class SAMLConfigRequest(BaseModel):
    org_id: str
    idp_entity_id: str
    idp_sso_url: str
    idp_slo_url: Optional[str] = ""
    idp_certificate: str
    attribute_mapping: Optional[Dict[str, str]] = None  # {email: "...", name: "...", department: "..."}
    enforce_sso: bool = False
    auto_provision: bool = True
    default_role: str = "employee"


class SAMLConfigUpdateRequest(BaseModel):
    idp_entity_id: Optional[str] = None
    idp_sso_url: Optional[str] = None
    idp_slo_url: Optional[str] = None
    idp_certificate: Optional[str] = None
    attribute_mapping: Optional[Dict[str, str]] = None
    enforce_sso: Optional[bool] = None
    auto_provision: Optional[bool] = None
    default_role: Optional[str] = None
    enabled: Optional[bool] = None


SP_ENTITY_ID = "https://aikarau.com/saml/metadata"


# ============ ADMIN: CONFIGURE SSO ============

@router.post("/configure")
async def configure_sso(config: SAMLConfigRequest, user=Depends(require_auth)):
    """Configure SAML SSO for an organization (admin only)."""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    org = await db.karau_organizations.find_one({"org_id": config.org_id})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    sso_config = {
        "org_id": config.org_id,
        "idp_entity_id": config.idp_entity_id,
        "idp_sso_url": config.idp_sso_url,
        "idp_slo_url": config.idp_slo_url,
        "idp_certificate": config.idp_certificate,
        "sp_entity_id": SP_ENTITY_ID,
        "sp_acs_url": f"https://aikarau.com/api/karau-meet/sso/acs",
        "attribute_mapping": config.attribute_mapping or {
            "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
            "name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
            "department": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/department",
        },
        "enforce_sso": config.enforce_sso,
        "auto_provision": config.auto_provision,
        "default_role": config.default_role,
        "enabled": True,
        "configured_by": user["user_id"],
        "configured_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.karau_sso_configs.update_one(
        {"org_id": config.org_id},
        {"$set": sso_config},
        upsert=True,
    )

    return {
        "success": True,
        "message": "SSO configured successfully",
        "sp_metadata": {
            "entity_id": SP_ENTITY_ID,
            "acs_url": sso_config["sp_acs_url"],
            "slo_url": f"https://aikarau.com/api/karau-meet/sso/slo",
        },
    }


@router.get("/config/{org_id}")
async def get_sso_config(org_id: str, user=Depends(require_auth)):
    """Get SSO configuration for an organization."""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    config = await db.karau_sso_configs.find_one(
        {"org_id": org_id},
        {"_id": 0, "idp_certificate": 0}  # Don't expose cert in API
    )
    if not config:
        return {"configured": False}

    config["configured"] = True
    return config


@router.put("/config/{org_id}")
async def update_sso_config(org_id: str, update: SAMLConfigUpdateRequest, user=Depends(require_auth)):
    """Update SSO configuration."""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    updates = {k: v for k, v in update.dict().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided")

    updates["updated_at"] = datetime.now(timezone.utc).isoformat()

    result = await db.karau_sso_configs.update_one(
        {"org_id": org_id},
        {"$set": updates},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="SSO not configured for this organization")

    return {"success": True, "message": "SSO configuration updated"}


@router.delete("/config/{org_id}")
async def delete_sso_config(org_id: str, user=Depends(require_auth)):
    """Remove SSO configuration."""
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    await db.karau_sso_configs.delete_one({"org_id": org_id})
    return {"success": True, "message": "SSO configuration removed"}


# ============ SAML LOGIN FLOW ============

@router.get("/login/{org_id}")
async def saml_login(org_id: str):
    """Initiate SAML SSO login - redirects to IdP."""
    config = await db.karau_sso_configs.find_one({"org_id": org_id})
    if not config or not config.get("enabled"):
        raise HTTPException(status_code=404, detail="SSO not configured for this organization")

    # Create SAML AuthnRequest
    request_id = f"_karau_{uuid.uuid4().hex}"
    issue_instant = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    authn_request = f"""<samlp:AuthnRequest
        xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
        xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
        ID="{request_id}"
        Version="2.0"
        IssueInstant="{issue_instant}"
        Destination="{config['idp_sso_url']}"
        AssertionConsumerServiceURL="{config['sp_acs_url']}"
        ProtocolBinding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST">
        <saml:Issuer>{SP_ENTITY_ID}</saml:Issuer>
        <samlp:NameIDPolicy Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress" AllowCreate="true"/>
    </samlp:AuthnRequest>"""

    # Store request for validation
    await db.karau_saml_requests.update_one(
        {"request_id": request_id},
        {"$set": {
            "request_id": request_id,
            "org_id": org_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True,
    )

    # Encode for redirect binding
    compressed = zlib.compress(authn_request.encode("utf-8"))[2:-4]
    encoded = base64.b64encode(compressed).decode("utf-8")
    saml_request = urllib.parse.quote(encoded)

    redirect_url = f"{config['idp_sso_url']}?SAMLRequest={saml_request}&RelayState={org_id}"
    return {"redirect_url": redirect_url}


@router.post("/acs")
async def saml_acs(request: Request):
    """SAML Assertion Consumer Service - handles IdP response."""
    form = await request.form()
    saml_response_b64 = form.get("SAMLResponse", "")
    relay_state = form.get("RelayState", "")

    if not saml_response_b64:
        raise HTTPException(status_code=400, detail="No SAML response received")

    org_id = relay_state
    config = await db.karau_sso_configs.find_one({"org_id": org_id})
    if not config:
        raise HTTPException(status_code=400, detail="Invalid SSO configuration")

    try:
        saml_xml = base64.b64decode(saml_response_b64).decode("utf-8")
        # Parse SAML response (simplified - production should use python3-saml or pysaml2)
        root = ET.fromstring(saml_xml)
        ns = {
            "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
            "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
        }

        # Extract attributes
        attrs = {}
        for attr_stmt in root.findall(".//saml:AttributeStatement/saml:Attribute", ns):
            attr_name = attr_stmt.get("Name", "")
            values = attr_stmt.findall("saml:AttributeValue", ns)
            if values:
                attrs[attr_name] = values[0].text

        # Map attributes
        mapping = config.get("attribute_mapping", {})
        email = attrs.get(mapping.get("email", ""), "")
        name = attrs.get(mapping.get("name", ""), "")
        department = attrs.get(mapping.get("department", ""), "")

        # Also try NameID as fallback for email
        if not email:
            name_id = root.find(".//saml:Subject/saml:NameID", ns)
            if name_id is not None:
                email = name_id.text or ""

        if not email:
            raise HTTPException(status_code=400, detail="No email found in SAML response")

    except ET.ParseError as e:
        logger.error(f"SAML parse error: {e}")
        raise HTTPException(status_code=400, detail="Invalid SAML response format")

    # Auto-provision or find user
    user = await db.users.find_one({"email": email}, {"_id": 0})
    if not user and config.get("auto_provision"):
        user = await get_or_create_user(
            email=email,
            name=name or email.split("@")[0],
            auth_method="saml_sso",
        )
        # Set organization
        await db.users.update_one(
            {"email": email},
            {"$set": {
                "organization_id": org_id,
                "department": department,
                "sso_provider": "saml",
                "role": config.get("default_role", "employee"),
            }},
        )
    elif not user:
        raise HTTPException(status_code=403, detail="User not provisioned. Contact your administrator.")

    # Create session
    token = create_session_token()
    await create_session(user["user_id"], token)

    # Log SSO login
    await db.karau_sso_logins.insert_one({
        "user_id": user["user_id"],
        "email": email,
        "org_id": org_id,
        "provider": "saml",
        "logged_in_at": datetime.now(timezone.utc).isoformat(),
    })

    # Redirect to frontend with token
    frontend_url = f"/karau-meet?sso_token={token}&sso_user={urllib.parse.quote(user.get('name', email))}"
    return RedirectResponse(url=frontend_url, status_code=303)


# ============ SP METADATA ============

@router.get("/metadata")
async def sp_metadata():
    """Return SP metadata XML for IdP configuration."""
    metadata = f"""<?xml version="1.0" encoding="UTF-8"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    entityID="{SP_ENTITY_ID}">
    <md:SPSSODescriptor
        AuthnRequestsSigned="false"
        WantAssertionsSigned="true"
        protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:NameIDFormat>urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress</md:NameIDFormat>
        <md:AssertionConsumerService
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="https://aikarau.com/api/karau-meet/sso/acs"
            index="1" />
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""
    return HTMLResponse(content=metadata, media_type="application/xml")


# ============ SSO DISCOVERY ============

@router.get("/discover")
async def discover_sso(email: str):
    """Check if an email domain has SSO configured."""
    domain = email.split("@")[-1] if "@" in email else ""
    if not domain:
        return {"sso_available": False}

    # Find org with this verified domain
    org = await db.karau_organizations.find_one(
        {"settings.verified_domains": domain},
        {"_id": 0, "org_id": 1, "name": 1},
    )
    if not org:
        return {"sso_available": False}

    # Check if SSO is configured
    sso = await db.karau_sso_configs.find_one(
        {"org_id": org["org_id"], "enabled": True},
        {"_id": 0, "org_id": 1},
    )
    if not sso:
        return {"sso_available": False}

    return {
        "sso_available": True,
        "org_id": org["org_id"],
        "org_name": org.get("name", ""),
        "login_url": f"/api/karau-meet/sso/login/{org['org_id']}",
    }
