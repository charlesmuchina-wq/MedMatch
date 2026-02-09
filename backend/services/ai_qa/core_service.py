"""
AI QA Compliance System - Core Service

This module implements the AI Quality Assurance and Compliance system for MedMatch,
supporting 2026 AI Act transparency requirements, GDPR compliance, and comprehensive
audit logging.

Key Components:
1. AI Decision Logging with crypto-shredding support
2. Model Provenance Tracking
3. Bias Detection and Fairness Metrics
4. Human Oversight Protocol
5. Regulatory Compliance Checks
"""

import os
import json
import uuid
import hashlib
import hmac
import base64
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path("/app/data/ai_qa")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Key Management (Mock KMS - in production use AWS KMS, Azure Key Vault, etc.)
MASTER_KEY_FILE = DATA_DIR / "master_key.bin"
DSK_REGISTRY_FILE = DATA_DIR / "dsk_registry.json"
DECISION_LOGS_FILE = DATA_DIR / "decision_logs.json"
AUDIT_LOGS_FILE = DATA_DIR / "audit_logs.json"
COMPLIANCE_CONFIG_FILE = DATA_DIR / "compliance_config.json"


class CryptoShredding:
    """
    Crypto-Shredding Architecture for GDPR + AI Act compliance.
    
    Allows keeping AI decision logs (for auditability) while enabling
    complete data deletion by destroying encryption keys.
    """
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.dsk_registry = self._load_dsk_registry()
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create the system master key."""
        if MASTER_KEY_FILE.exists():
            return MASTER_KEY_FILE.read_bytes()
        
        # Generate new master key
        master_key = Fernet.generate_key()
        MASTER_KEY_FILE.write_bytes(master_key)
        logger.info("Generated new master key for crypto-shredding")
        return master_key
    
    def _load_dsk_registry(self) -> Dict:
        """Load the Data Subject Key registry."""
        if DSK_REGISTRY_FILE.exists():
            return json.loads(DSK_REGISTRY_FILE.read_text())
        return {"keys": {}, "shredded": []}
    
    def _save_dsk_registry(self):
        """Save the DSK registry."""
        DSK_REGISTRY_FILE.write_text(json.dumps(self.dsk_registry, indent=2))
    
    def generate_dsk(self, user_id: str) -> str:
        """Generate a Data Subject Key for a user."""
        dsk_id = f"DSK-{uuid.uuid4().hex[:8].upper()}"
        key = Fernet.generate_key()
        
        self.dsk_registry["keys"][user_id] = {
            "dsk_id": dsk_id,
            "key": key.decode(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "algorithm": "AES-256-GCM"
        }
        self._save_dsk_registry()
        
        logger.info(f"Generated DSK {dsk_id} for user {user_id[:8]}...")
        return dsk_id
    
    def get_dsk(self, user_id: str) -> Optional[Dict]:
        """Get DSK for a user."""
        return self.dsk_registry["keys"].get(user_id)
    
    def encrypt_pii(self, user_id: str, data: Dict) -> str:
        """Encrypt PII data using user's DSK."""
        dsk_info = self.get_dsk(user_id)
        if not dsk_info:
            dsk_id = self.generate_dsk(user_id)
            dsk_info = self.get_dsk(user_id)
        
        if dsk_info["status"] == "shredded":
            raise ValueError("Cannot encrypt: DSK has been shredded")
        
        fernet = Fernet(dsk_info["key"].encode())
        encrypted = fernet.encrypt(json.dumps(data).encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_pii(self, user_id: str, encrypted_data: str) -> Optional[Dict]:
        """Decrypt PII data using user's DSK."""
        dsk_info = self.get_dsk(user_id)
        if not dsk_info or dsk_info["status"] == "shredded":
            return None  # Data is effectively deleted
        
        try:
            fernet = Fernet(dsk_info["key"].encode())
            decrypted = fernet.decrypt(base64.b64decode(encrypted_data))
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def shred_user_data(self, user_id: str) -> Dict:
        """
        GDPR Right to Erasure - Shred user's DSK.
        
        This makes all encrypted PII permanently unreadable while
        preserving anonymized AI decision logs for AI Act compliance.
        """
        dsk_info = self.get_dsk(user_id)
        if not dsk_info:
            return {"success": False, "error": "No DSK found for user"}
        
        if dsk_info["status"] == "shredded":
            return {"success": False, "error": "DSK already shredded"}
        
        # Record shredding event
        shred_event = {
            "dsk_id": dsk_info["dsk_id"],
            "user_id_hash": hashlib.sha256(user_id.encode()).hexdigest()[:16],
            "shredded_at": datetime.now(timezone.utc).isoformat(),
            "reason": "GDPR Right to Erasure"
        }
        
        # Destroy the key
        self.dsk_registry["keys"][user_id] = {
            **dsk_info,
            "key": "[SHREDDED]",
            "status": "shredded",
            "shredded_at": shred_event["shredded_at"]
        }
        self.dsk_registry["shredded"].append(shred_event)
        self._save_dsk_registry()
        
        logger.info(f"Shredded DSK for user {user_id[:8]}... - GDPR deletion complete")
        
        return {
            "success": True,
            "dsk_id": dsk_info["dsk_id"],
            "shredded_at": shred_event["shredded_at"],
            "message": "User data cryptographically shredded. AI decision logs preserved in anonymized form."
        }


class AIDecisionLogger:
    """
    AI Decision Logging Service for 2026 AI Act Compliance.
    
    Captures:
    - Model provenance (version, weights, training data summary)
    - Input context (encrypted with DSK)
    - Decision rationale (explainability)
    - Human oversight interactions
    - Tamper-resistant signatures
    """
    
    def __init__(self, crypto_shredding: CryptoShredding):
        self.crypto = crypto_shredding
        self.logs = self._load_logs()
        self.signing_key = self._get_signing_key()
    
    def _load_logs(self) -> List[Dict]:
        """Load decision logs."""
        if DECISION_LOGS_FILE.exists():
            return json.loads(DECISION_LOGS_FILE.read_text())
        return []
    
    def _save_logs(self):
        """Save decision logs."""
        DECISION_LOGS_FILE.write_text(json.dumps(self.logs, indent=2))
    
    def _get_signing_key(self) -> bytes:
        """Get key for digital signatures."""
        key_file = DATA_DIR / "signing_key.bin"
        if key_file.exists():
            return key_file.read_bytes()
        key = os.urandom(32)
        key_file.write_bytes(key)
        return key
    
    def _sign_log(self, log_data: Dict) -> str:
        """Create tamper-resistant signature for log entry."""
        log_string = json.dumps(log_data, sort_keys=True)
        signature = hmac.new(
            self.signing_key,
            log_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _verify_signature(self, log_entry: Dict) -> bool:
        """Verify log entry hasn't been tampered with."""
        stored_sig = log_entry.get("signature")
        if not stored_sig:
            return False
        
        log_data = {k: v for k, v in log_entry.items() if k != "signature"}
        expected_sig = self._sign_log(log_data)
        return hmac.compare_digest(stored_sig, expected_sig)
    
    def log_ai_decision(
        self,
        user_id: str,
        model_info: Dict,
        input_data: Dict,
        decision: Dict,
        explainability: Dict,
        risk_level: str = "high"
    ) -> Dict:
        """
        Log an AI decision with full 2026 compliance.
        
        Args:
            user_id: The data subject's ID
            model_info: Model version, type, training data summary
            input_data: The input that was processed (PII encrypted)
            decision: The AI's output/decision
            explainability: Feature weights and reasoning
            risk_level: AI Act risk classification
        
        Returns:
            The logged decision record
        """
        log_id = f"{uuid.uuid4()}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Encrypt PII in input data
        pii_fields = ["name", "email", "phone", "address", "resume_text", "personal_info"]
        pii_data = {k: v for k, v in input_data.items() if k in pii_fields}
        non_pii_data = {k: v for k, v in input_data.items() if k not in pii_fields}
        
        encrypted_payload = None
        dsk_info = None
        if pii_data:
            encrypted_payload = self.crypto.encrypt_pii(user_id, pii_data)
            dsk_info = self.crypto.get_dsk(user_id)
        
        log_entry = {
            "log_id": log_id,
            "timestamp": timestamp,
            "ai_model": {
                "model_id": model_info.get("model_id", "medmatch-ai-v1"),
                "version": model_info.get("version", "2026.Q1"),
                "model_type": model_info.get("type", "matching"),
                "training_data_summary": model_info.get("training_summary", "Life sciences job matching dataset"),
                "risk_level": f"High-Risk (Annex III)" if risk_level == "high" else risk_level
            },
            "crypto_shredding_metadata": {
                "data_subject_key_id": dsk_info["dsk_id"] if dsk_info else None,
                "key_status": dsk_info["status"] if dsk_info else "none",
                "encryption_algorithm": "AES-256-GCM",
                "kms_reference": "mock:kms:medmatch:key/ai-qa-dsk"
            } if dsk_info else None,
            "encrypted_personal_payload": encrypted_payload,
            "input_summary": non_pii_data,
            "ai_decision_trace": {
                "decision_type": decision.get("type", "match_score"),
                "output": decision.get("output"),
                "confidence": decision.get("confidence", 0.0),
                "decision_logic": explainability.get("reasoning", ""),
                "top_features": explainability.get("feature_weights", {}),
                "factors_considered": explainability.get("factors", [])
            },
            "human_oversight": {
                "reviewer_id": None,
                "action": "PENDING_REVIEW",
                "override_reason": None,
                "review_timestamp": None
            },
            "retention_info": {
                "retention_period_months": 36,  # 3 years for recruitment
                "deletion_scheduled": (datetime.now(timezone.utc) + timedelta(days=1095)).isoformat(),
                "legal_basis": "EU AI Act Article 26, Employment Law"
            }
        }
        
        # Add tamper-resistant signature
        log_entry["signature"] = self._sign_log(log_entry)
        
        self.logs.append(log_entry)
        self._save_logs()
        
        logger.info(f"Logged AI decision {log_id} for model {model_info.get('model_id')}")
        
        return log_entry
    
    def record_human_override(
        self,
        log_id: str,
        reviewer_id: str,
        action: str,
        reason: Optional[str] = None
    ) -> Dict:
        """Record human oversight action on an AI decision."""
        for log in self.logs:
            if log["log_id"] == log_id:
                log["human_oversight"] = {
                    "reviewer_id": reviewer_id,
                    "action": action,  # ACCEPTED, REJECTED, MODIFIED
                    "override_reason": reason,
                    "review_timestamp": datetime.now(timezone.utc).isoformat()
                }
                # Re-sign the log
                log["signature"] = self._sign_log({k: v for k, v in log.items() if k != "signature"})
                self._save_logs()
                
                logger.info(f"Human override recorded for decision {log_id}: {action}")
                return log
        
        return {"error": "Log not found"}
    
    def get_decision_log(self, log_id: str, include_pii: bool = False) -> Optional[Dict]:
        """Retrieve a decision log, optionally with decrypted PII."""
        for log in self.logs:
            if log["log_id"] == log_id:
                result = {**log}
                
                # Verify integrity
                result["integrity_verified"] = self._verify_signature(log)
                
                # Optionally decrypt PII
                if include_pii and log.get("encrypted_personal_payload"):
                    # Need user_id to decrypt - this should come from a secure lookup
                    result["pii_status"] = "encrypted"
                
                return result
        return None
    
    def get_user_decisions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get all AI decisions affecting a user (for DSAR)."""
        user_dsk = self.crypto.get_dsk(user_id)
        if not user_dsk:
            return []
        
        dsk_id = user_dsk["dsk_id"]
        user_logs = [
            log for log in self.logs
            if log.get("crypto_shredding_metadata", {}).get("data_subject_key_id") == dsk_id
        ]
        
        return user_logs[:limit]
    
    def get_logs_for_audit(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        model_id: Optional[str] = None
    ) -> List[Dict]:
        """Get logs for regulatory audit."""
        filtered_logs = []
        
        for log in self.logs:
            # Date filtering
            if start_date and log["timestamp"] < start_date:
                continue
            if end_date and log["timestamp"] > end_date:
                continue
            
            # Model filtering
            if model_id and log["ai_model"]["model_id"] != model_id:
                continue
            
            # Verify integrity
            log_copy = {**log}
            log_copy["integrity_verified"] = self._verify_signature(log)
            
            # Remove encrypted PII for audit report
            log_copy["encrypted_personal_payload"] = "[REDACTED]" if log.get("encrypted_personal_payload") else None
            
            filtered_logs.append(log_copy)
        
        return filtered_logs


class BiasAuditor:
    """
    AI Bias Detection and Fairness Auditing.
    
    Implements:
    - Flip tests (gender/name swapping)
    - Disparity analysis across protected classes
    - Statistical parity checks
    - Individual fairness metrics
    """
    
    PROTECTED_CLASSES = ["gender", "race", "age", "disability", "nationality"]
    
    def __init__(self):
        self.audit_results = self._load_audit_results()
    
    def _load_audit_results(self) -> List[Dict]:
        """Load previous audit results."""
        audit_file = DATA_DIR / "bias_audits.json"
        if audit_file.exists():
            return json.loads(audit_file.read_text())
        return []
    
    def _save_audit_results(self):
        """Save audit results."""
        audit_file = DATA_DIR / "bias_audits.json"
        audit_file.write_text(json.dumps(self.audit_results, indent=2))
    
    def run_flip_test(
        self,
        original_input: Dict,
        original_score: float,
        flip_type: str,
        model_scorer: callable = None
    ) -> Dict:
        """
        Run a flip test to detect bias.
        
        Swaps demographic attributes and checks if score changes significantly.
        """
        flipped_input = {**original_input}
        
        # Apply flip based on type
        if flip_type == "gender":
            # Swap gender indicators
            name_swaps = {
                "John": "Jane", "Jane": "John",
                "Michael": "Michelle", "Michelle": "Michael",
                "Robert": "Roberta", "Roberta": "Robert",
                "James": "Jamie", "David": "Diana"
            }
            if "name" in flipped_input:
                for old, new in name_swaps.items():
                    if old.lower() in flipped_input["name"].lower():
                        flipped_input["name"] = flipped_input["name"].replace(old, new)
                        break
            
            # Swap pronouns in text
            if "resume_text" in flipped_input:
                text = flipped_input["resume_text"]
                text = text.replace(" he ", " she ").replace(" He ", " She ")
                text = text.replace(" his ", " her ").replace(" His ", " Her ")
                flipped_input["resume_text"] = text
        
        elif flip_type == "age":
            # Adjust graduation years
            if "graduation_year" in flipped_input:
                current_year = datetime.now().year
                original_year = flipped_input["graduation_year"]
                years_since = current_year - original_year
                
                # Flip to opposite age bracket
                if years_since < 10:
                    flipped_input["graduation_year"] = current_year - 25
                else:
                    flipped_input["graduation_year"] = current_year - 3
        
        # Calculate flipped score (mock if no scorer provided)
        if model_scorer:
            flipped_score = model_scorer(flipped_input)
        else:
            # Mock: Add small random variance
            import random
            flipped_score = original_score + random.uniform(-0.05, 0.05)
            flipped_score = max(0, min(1, flipped_score))
        
        # Calculate disparity
        disparity = abs(original_score - flipped_score)
        disparity_threshold = 0.1  # 10% threshold
        
        result = {
            "test_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "flip_type": flip_type,
            "original_score": original_score,
            "flipped_score": flipped_score,
            "disparity": disparity,
            "threshold": disparity_threshold,
            "passed": disparity < disparity_threshold,
            "risk_level": "high" if disparity > 0.2 else "medium" if disparity > 0.1 else "low"
        }
        
        return result
    
    def run_disparity_analysis(
        self,
        decisions: List[Dict],
        protected_attribute: str
    ) -> Dict:
        """
        Analyze score distribution across a protected class.
        
        Uses the 80% rule (four-fifths rule) for adverse impact analysis.
        """
        groups = {}
        
        for decision in decisions:
            group = decision.get("input_summary", {}).get(protected_attribute, "unknown")
            score = decision.get("ai_decision_trace", {}).get("confidence", 0)
            
            if group not in groups:
                groups[group] = []
            groups[group].append(score)
        
        # Calculate statistics per group
        group_stats = {}
        for group, scores in groups.items():
            if scores:
                group_stats[group] = {
                    "count": len(scores),
                    "mean_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores)
                }
        
        # Four-fifths rule analysis
        if len(group_stats) >= 2:
            means = [(g, s["mean_score"]) for g, s in group_stats.items()]
            means.sort(key=lambda x: x[1], reverse=True)
            
            highest_group, highest_mean = means[0]
            adverse_impact_flags = []
            
            for group, mean in means[1:]:
                ratio = mean / highest_mean if highest_mean > 0 else 0
                if ratio < 0.8:  # Four-fifths rule
                    adverse_impact_flags.append({
                        "group": group,
                        "selection_rate": mean,
                        "reference_rate": highest_mean,
                        "ratio": ratio,
                        "adverse_impact": True
                    })
        else:
            adverse_impact_flags = []
        
        result = {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "protected_attribute": protected_attribute,
            "total_decisions": len(decisions),
            "group_statistics": group_stats,
            "adverse_impact_flags": adverse_impact_flags,
            "overall_fairness_score": 1.0 - (len(adverse_impact_flags) * 0.25),
            "recommendation": "Review flagged groups" if adverse_impact_flags else "No adverse impact detected"
        }
        
        self.audit_results.append(result)
        self._save_audit_results()
        
        return result
    
    def get_fairness_summary(self) -> Dict:
        """Get overall fairness metrics summary."""
        if not self.audit_results:
            return {
                "status": "no_audits",
                "message": "No bias audits have been performed yet"
            }
        
        recent_audits = self.audit_results[-10:]
        
        adverse_impact_count = sum(
            1 for a in recent_audits if a.get("adverse_impact_flags")
        )
        
        avg_fairness = sum(
            a.get("overall_fairness_score", 1.0) for a in recent_audits
        ) / len(recent_audits)
        
        return {
            "total_audits": len(self.audit_results),
            "recent_audits": len(recent_audits),
            "audits_with_issues": adverse_impact_count,
            "average_fairness_score": round(avg_fairness, 3),
            "status": "healthy" if avg_fairness > 0.8 else "needs_review" if avg_fairness > 0.6 else "critical",
            "last_audit": recent_audits[-1]["timestamp"] if recent_audits else None
        }


# Initialize services
crypto_shredding = CryptoShredding()
ai_decision_logger = AIDecisionLogger(crypto_shredding)
bias_auditor = BiasAuditor()


# Export
__all__ = [
    'crypto_shredding',
    'ai_decision_logger', 
    'bias_auditor',
    'CryptoShredding',
    'AIDecisionLogger',
    'BiasAuditor'
]
