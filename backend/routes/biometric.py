"""
Biometric Authentication Routes
Handles: WebAuthn/FIDO2 passwordless authentication, bot prevention, fraud detection
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone, timedelta
import uuid
import logging
import base64
import os

from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    AuthenticatorAttachment,
    PublicKeyCredentialDescriptor,
    AttestationConveyancePreference,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from utils.database import db
from routes.auth import get_current_user

router = APIRouter(prefix="/biometric", tags=["Biometric Authentication"])

# ============== Configuration ==============
RP_ID = os.environ.get("WEBAUTHN_RP_ID", "localhost")
RP_NAME = os.environ.get("WEBAUTHN_RP_NAME", "MedMatch")
ORIGIN = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:3000")

# ============== Helper: Create Session Token ==============
def create_session_token(user_id: str, email: str) -> str:
    """Create a session token for the user"""
    import secrets
    return secrets.token_urlsafe(32)

# ============== Models ==============

class BiometricRegistrationStartRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=50)
    device_name: str = Field(default="My Device", max_length=100)

class BiometricRegistrationCompleteRequest(BaseModel):
    user_id: str
    credential_id: str
    raw_id: str
    response: dict
    type: str = "public-key"
    client_extension_results: Optional[dict] = None
    authenticator_attachment: Optional[str] = None

class BiometricAuthStartRequest(BaseModel):
    email: EmailStr

class BiometricAuthCompleteRequest(BaseModel):
    credential_id: str
    raw_id: str
    response: dict
    type: str = "public-key"
    client_extension_results: Optional[dict] = None
    authenticator_attachment: Optional[str] = None

class WebAuthnCredentialInfo(BaseModel):
    credential_id: str
    device_name: str
    device_type: Optional[str] = None
    created_at: datetime
    last_used: Optional[datetime] = None

# ============== Helper Functions ==============

def bytes_to_base64url(data: bytes) -> str:
    """Convert bytes to base64url encoding"""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_to_bytes(data: str) -> bytes:
    """Convert base64url encoding to bytes"""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data)

# ============== Routes ==============

@router.get("/supported")
async def check_webauthn_support():
    """Check if WebAuthn is supported and return configuration"""
    return {
        "supported": True,
        "rp_id": RP_ID,
        "rp_name": RP_NAME,
        "features": {
            "platform_authenticator": True,
            "cross_platform": True,
            "user_verification": True,
            "resident_key": True
        }
    }

@router.post("/register/start")
async def start_biometric_registration(request: BiometricRegistrationStartRequest, req: Request = None):
    """
    Start WebAuthn registration - generates challenge and options for the client.
    The client uses these to create a credential with the authenticator.
    """
    try:
        # Check if email already has biometric credentials
        existing_user = await db.users.find_one({"email": request.email})
        
        if existing_user:
            user_id = str(existing_user.get("user_id", existing_user.get("_id")))
            # Check if already has biometric credentials
            existing_creds = await db.webauthn_credentials.find_one({"user_id": user_id})
            if existing_creds:
                raise HTTPException(
                    status_code=400, 
                    detail="Biometric credentials already registered for this email. Use 'Add Device' to register another device."
                )
        else:
            # Create temporary user record for registration
            user_id = str(uuid.uuid4())
        
        # Generate unique challenge
        challenge = os.urandom(32)
        
        # Build registration options
        registration_options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=user_id.encode('utf-8'),
            user_name=request.email,
            user_display_name=request.username,
            attestation=AttestationConveyancePreference.NONE,  # Don't require attestation for privacy
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ECDSA_SHA_256,
                COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
            ],
            timeout=60000,
        )
        
        # Store challenge for verification
        challenge_doc = {
            "challenge_id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": request.email,
            "username": request.username,
            "device_name": request.device_name,
            "challenge": bytes_to_base64url(registration_options.challenge),
            "type": "registration",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
            "used": False
        }
        await db.webauthn_challenges.insert_one(challenge_doc)
        
        # Convert options to JSON-serializable format
        options_json = options_to_json(registration_options)
        
        return {
            "user_id": user_id,
            "options": options_json,
            "challenge_id": challenge_doc["challenge_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start registration")

@router.post("/register/complete")
async def complete_biometric_registration(request: BiometricRegistrationCompleteRequest, req: Request = None):
    """
    Complete WebAuthn registration - verifies the credential and stores it.
    """
    try:
        # Find the challenge
        challenge_doc = await db.webauthn_challenges.find_one({
            "user_id": request.user_id,
            "type": "registration",
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not challenge_doc:
            raise HTTPException(status_code=400, detail="Challenge not found or expired")
        
        # Prepare credential for verification
        from webauthn.helpers.structs import RegistrationCredential, AuthenticatorAttestationResponse
        
        credential = RegistrationCredential(
            id=request.credential_id,
            raw_id=base64url_to_bytes(request.raw_id),
            response=AuthenticatorAttestationResponse(
                client_data_json=base64url_to_bytes(request.response.get("clientDataJSON", "")),
                attestation_object=base64url_to_bytes(request.response.get("attestationObject", "")),
                transports=request.response.get("transports", []),
            ),
            authenticator_attachment=request.authenticator_attachment,
            client_extension_results={},
            type="public-key",
        )
        
        # Verify the registration
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=base64url_to_bytes(challenge_doc["challenge"]),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            require_user_verification=False,
        )
        
        if not verification.verified:
            raise HTTPException(status_code=400, detail="Registration verification failed")
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": challenge_doc["email"]})
        
        if not existing_user:
            # Create new user
            user_doc = {
                "user_id": request.user_id,
                "email": challenge_doc["email"],
                "name": challenge_doc["username"],
                "role": "job_seeker",
                "is_biometric_verified": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_login": datetime.now(timezone.utc).isoformat(),
                "auth_method": "biometric"
            }
            await db.users.insert_one(user_doc)
        else:
            # Update existing user
            await db.users.update_one(
                {"email": challenge_doc["email"]},
                {"$set": {
                    "is_biometric_verified": True,
                    "auth_method": "biometric",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        # Store the credential
        credential_doc = {
            "credential_id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "email": challenge_doc["email"],
            "webauthn_credential_id": bytes_to_base64url(verification.credential_id),
            "public_key": bytes_to_base64url(verification.credential_public_key),
            "sign_count": verification.sign_count,
            "device_name": challenge_doc.get("device_name", "Device"),
            "device_type": verification.credential_device_type if hasattr(verification, 'credential_device_type') else "platform",
            "transports": request.response.get("transports", []),
            "created_at": datetime.now(timezone.utc),
            "last_used": None
        }
        await db.webauthn_credentials.insert_one(credential_doc)
        
        # Mark challenge as used
        await db.webauthn_challenges.update_one(
            {"_id": challenge_doc["_id"]},
            {"$set": {"used": True}}
        )
        
        # Generate session token
        token = create_session_token(request.user_id, challenge_doc["email"])
        
        # Store session
        await db.user_sessions.insert_one({
            "session_id": token,
            "user_id": request.user_id,
            "email": challenge_doc["email"],
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "auth_method": "biometric"
        })
        
        return {
            "verified": True,
            "message": "Biometric registration successful",
            "user_id": request.user_id,
            "token": token,
            "user": {
                "user_id": request.user_id,
                "email": challenge_doc["email"],
                "name": challenge_doc["username"],
                "is_biometric_verified": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration complete error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete registration: {str(e)}")

@router.post("/authenticate/start")
async def start_biometric_authentication(request: BiometricAuthStartRequest, req: Request = None):
    """
    Start WebAuthn authentication - generates challenge for existing credential.
    """
    try:
        # Find user by email
        user = await db.users.find_one({"email": request.email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_id = str(user.get("user_id", user.get("_id")))
        
        # Find user's credentials
        credentials = await db.webauthn_credentials.find(
            {"email": request.email}
        ).to_list(length=10)
        
        if not credentials:
            raise HTTPException(status_code=400, detail="No biometric credentials found. Please register first.")
        
        # Build allowed credentials list
        allow_credentials = []
        for cred in credentials:
            try:
                cred_id_bytes = base64url_to_bytes(cred["webauthn_credential_id"])
                allow_credentials.append(
                    PublicKeyCredentialDescriptor(
                        id=cred_id_bytes,
                        transports=cred.get("transports", [])
                    )
                )
            except Exception as e:
                logging.warning(f"Skipping invalid credential: {e}")
                continue
        
        if not allow_credentials:
            raise HTTPException(status_code=400, detail="No valid credentials found")
        
        # Generate authentication options
        authentication_options = generate_authentication_options(
            rp_id=RP_ID,
            timeout=60000,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.PREFERRED,
        )
        
        # Store challenge
        challenge_doc = {
            "challenge_id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": request.email,
            "challenge": bytes_to_base64url(authentication_options.challenge),
            "type": "authentication",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
            "used": False
        }
        await db.webauthn_challenges.insert_one(challenge_doc)
        
        options_json = options_to_json(authentication_options)
        
        return {
            "options": options_json,
            "challenge_id": challenge_doc["challenge_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Authentication start error: {e}")
        raise HTTPException(status_code=500, detail="Failed to start authentication")

@router.post("/authenticate/complete")
async def complete_biometric_authentication(request: BiometricAuthCompleteRequest, req: Request = None):
    """
    Complete WebAuthn authentication - verifies the assertion and issues JWT.
    """
    try:
        # Find the credential
        credential_doc = await db.webauthn_credentials.find_one({
            "webauthn_credential_id": request.credential_id
        })
        
        if not credential_doc:
            raise HTTPException(status_code=400, detail="Credential not found")
        
        # Find the challenge
        challenge_doc = await db.webauthn_challenges.find_one({
            "email": credential_doc["email"],
            "type": "authentication",
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not challenge_doc:
            raise HTTPException(status_code=400, detail="Challenge not found or expired")
        
        # Prepare credential for verification
        from webauthn.helpers.structs import AuthenticationCredential, AuthenticatorAssertionResponse
        
        credential = AuthenticationCredential(
            id=request.credential_id,
            raw_id=base64url_to_bytes(request.raw_id),
            response=AuthenticatorAssertionResponse(
                client_data_json=base64url_to_bytes(request.response.get("clientDataJSON", "")),
                authenticator_data=base64url_to_bytes(request.response.get("authenticatorData", "")),
                signature=base64url_to_bytes(request.response.get("signature", "")),
                user_handle=base64url_to_bytes(request.response.get("userHandle", "")) if request.response.get("userHandle") else None,
            ),
            authenticator_attachment=request.authenticator_attachment,
            client_extension_results={},
            type="public-key",
        )
        
        # Verify the authentication
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=base64url_to_bytes(challenge_doc["challenge"]),
            expected_rp_id=RP_ID,
            expected_origin=ORIGIN,
            credential_public_key=base64url_to_bytes(credential_doc["public_key"]),
            credential_current_sign_count=credential_doc.get("sign_count", 0),
            require_user_verification=False,
        )
        
        if not verification.verified:
            # Log failed attempt
            await db.fraud_events.insert_one({
                "event_type": "biometric_auth_failure",
                "email": credential_doc["email"],
                "ip_address": req.client.host if req and hasattr(req, 'client') else "unknown",
                "timestamp": datetime.now(timezone.utc),
                "risk_score": 0.5
            })
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # Update sign count (prevents replay attacks)
        await db.webauthn_credentials.update_one(
            {"_id": credential_doc["_id"]},
            {"$set": {
                "sign_count": verification.new_sign_count,
                "last_used": datetime.now(timezone.utc)
            }}
        )
        
        # Mark challenge as used
        await db.webauthn_challenges.update_one(
            {"_id": challenge_doc["_id"]},
            {"$set": {"used": True}}
        )
        
        # Get user info
        user = await db.users.find_one({"email": credential_doc["email"]})
        user_id = str(user.get("user_id", user.get("_id")))
        
        # Update last login
        await db.users.update_one(
            {"email": credential_doc["email"]},
            {"$set": {"last_login": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Generate session token
        token = create_session_token(user_id, credential_doc["email"])
        
        # Store session
        await db.user_sessions.insert_one({
            "session_id": token,
            "user_id": user_id,
            "email": credential_doc["email"],
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
            "auth_method": "biometric"
        })
        
        return {
            "verified": True,
            "message": "Authentication successful",
            "token": token,
            "user": {
                "user_id": user_id,
                "email": user.get("email"),
                "name": user.get("name"),
                "role": user.get("role", "job_seeker"),
                "is_biometric_verified": True
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Authentication complete error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to complete authentication: {str(e)}")

@router.get("/credentials")
async def list_biometric_credentials(request: Request):
    """List all biometric credentials for the authenticated user."""
    try:
        user = await get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        credentials = await db.webauthn_credentials.find(
            {"email": user.get("email")},
            {"_id": 0, "public_key": 0}  # Exclude sensitive data
        ).to_list(length=10)
        
        return {
            "credentials": [
                {
                    "credential_id": c.get("credential_id"),
                    "device_name": c.get("device_name", "Unknown Device"),
                    "device_type": c.get("device_type"),
                    "created_at": c.get("created_at"),
                    "last_used": c.get("last_used")
                }
                for c in credentials
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"List credentials error: {e}")
        raise HTTPException(status_code=500, detail="Failed to list credentials")

@router.delete("/credentials/{credential_id}")
async def delete_biometric_credential(credential_id: str, request: Request):
    """Delete a biometric credential."""
    try:
        user = await get_current_user(request)
        if not user:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        result = await db.webauthn_credentials.delete_one({
            "credential_id": credential_id,
            "email": user.get("email")
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Credential not found")
        
        return {"message": "Credential deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Delete credential error: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete credential")

# ============== Bot Prevention Endpoints ==============

@router.get("/security/status")
async def get_security_status(request: Request):
    """Get security status and bot detection info for the current session."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    
    # Check for suspicious patterns
    suspicious_agents = ["bot", "crawler", "spider", "scraper", "curl", "wget"]
    is_suspicious = any(bot in user_agent.lower() for bot in suspicious_agents)
    
    # Check recent fraud events
    recent_events = await db.fraud_events.find({
        "ip_address": client_ip,
        "timestamp": {"$gt": datetime.now(timezone.utc) - timedelta(hours=1)}
    }).to_list(length=100)
    
    risk_score = min(len(recent_events) * 0.1, 1.0)
    if is_suspicious:
        risk_score = min(risk_score + 0.5, 1.0)
    
    return {
        "ip_address": client_ip,
        "is_suspicious": is_suspicious,
        "risk_score": risk_score,
        "recent_events": len(recent_events),
        "security_level": "high" if risk_score > 0.7 else "medium" if risk_score > 0.3 else "low"
    }
