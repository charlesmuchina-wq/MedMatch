"""
AI QA Compliance System - Human Oversight Protocol

Implements human-in-the-loop controls for AI decision making,
compliant with EU AI Act Article 14 requirements.
"""

import json
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DATA_DIR = Path("/app/data/ai_qa")
OVERSIGHT_CONFIG_FILE = DATA_DIR / "oversight_config.json"
OVERSIGHT_LOGS_FILE = DATA_DIR / "oversight_logs.json"
OVERSIGHT_TRAINING_FILE = DATA_DIR / "oversight_training.json"


class HumanOversightProtocol:
    """
    Human Oversight Protocol Implementation.
    
    Supports:
    - Designated overseer management
    - Override/intervention logging
    - Two-person confirmation for high-stakes decisions
    - AI literacy training tracking
    - Emergency stop functionality
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.logs = self._load_logs()
        self.training = self._load_training()
        self._ensure_default_config()
    
    def _load_config(self) -> Dict:
        """Load oversight configuration."""
        if OVERSIGHT_CONFIG_FILE.exists():
            return json.loads(OVERSIGHT_CONFIG_FILE.read_text())
        return {}
    
    def _save_config(self):
        """Save configuration."""
        OVERSIGHT_CONFIG_FILE.write_text(json.dumps(self.config, indent=2))
    
    def _load_logs(self) -> List[Dict]:
        """Load oversight logs."""
        if OVERSIGHT_LOGS_FILE.exists():
            return json.loads(OVERSIGHT_LOGS_FILE.read_text())
        return []
    
    def _save_logs(self):
        """Save logs."""
        OVERSIGHT_LOGS_FILE.write_text(json.dumps(self.logs, indent=2))
    
    def _load_training(self) -> Dict:
        """Load training records."""
        if OVERSIGHT_TRAINING_FILE.exists():
            return json.loads(OVERSIGHT_TRAINING_FILE.read_text())
        return {"users": {}, "courses": []}
    
    def _save_training(self):
        """Save training records."""
        OVERSIGHT_TRAINING_FILE.write_text(json.dumps(self.training, indent=2))
    
    def _ensure_default_config(self):
        """Ensure default configuration exists."""
        defaults = {
            "enabled": True,
            "system_status": "active",
            "emergency_stop": False,
            "emergency_stop_at": None,
            "emergency_stop_by": None,
            "settings": {
                "require_two_person_confirmation": True,
                "two_person_threshold": "final_selection",
                "manual_review_percentage": 10,
                "override_requires_reason": True,
                "ai_literacy_required": True
            },
            "roles": {
                "primary_overseer": {
                    "description": "Primary human overseer for AI decisions",
                    "permissions": ["view", "override", "stop", "configure"],
                    "required_training": ["ai_literacy_basic", "bias_awareness"]
                },
                "secondary_overseer": {
                    "description": "Secondary reviewer for two-person confirmation",
                    "permissions": ["view", "confirm", "escalate"],
                    "required_training": ["ai_literacy_basic"]
                },
                "auditor": {
                    "description": "Compliance auditor with read access",
                    "permissions": ["view", "export", "audit"],
                    "required_training": ["ai_literacy_basic", "compliance_overview"]
                }
            },
            "designated_overseers": []
        }
        
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
        
        self._save_config()
    
    def register_overseer(
        self,
        user_id: str,
        name: str,
        role: str,
        email: str,
        department: str = "Recruitment"
    ) -> Dict:
        """Register a designated human overseer."""
        if role not in self.config["roles"]:
            return {"error": f"Invalid role: {role}"}
        
        # Check if already registered
        existing = next(
            (o for o in self.config["designated_overseers"] if o["user_id"] == user_id),
            None
        )
        if existing:
            return {"error": "User already registered as overseer"}
        
        overseer = {
            "user_id": user_id,
            "name": name,
            "role": role,
            "email": email,
            "department": department,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "active": True,
            "training_complete": False,
            "completed_training": []
        }
        
        self.config["designated_overseers"].append(overseer)
        self._save_config()
        
        logger.info(f"Registered overseer: {name} ({role})")
        return overseer
    
    def get_overseers(self, role: Optional[str] = None, active_only: bool = True) -> List[Dict]:
        """Get designated overseers."""
        overseers = self.config.get("designated_overseers", [])
        
        if active_only:
            overseers = [o for o in overseers if o.get("active")]
        
        if role:
            overseers = [o for o in overseers if o["role"] == role]
        
        return overseers
    
    def record_override(
        self,
        decision_id: str,
        overseer_id: str,
        original_decision: Dict,
        action: str,
        reason: str,
        new_decision: Optional[Dict] = None
    ) -> Dict:
        """Record a human override of an AI decision."""
        # Validate overseer
        overseer = next(
            (o for o in self.config["designated_overseers"] if o["user_id"] == overseer_id),
            None
        )
        if not overseer:
            return {"error": "Overseer not registered"}
        
        if not overseer.get("active"):
            return {"error": "Overseer is not active"}
        
        # Check if reason required
        if self.config["settings"]["override_requires_reason"] and not reason:
            return {"error": "Override reason is required"}
        
        override_log = {
            "override_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision_id": decision_id,
            "overseer": {
                "user_id": overseer_id,
                "name": overseer["name"],
                "role": overseer["role"]
            },
            "action": action,  # ACCEPTED, REJECTED, MODIFIED, ESCALATED
            "reason": reason,
            "original_decision": {
                "type": original_decision.get("type"),
                "score": original_decision.get("score"),
                "recommendation": original_decision.get("recommendation")
            },
            "new_decision": new_decision,
            "requires_second_confirmation": self._requires_two_person(original_decision),
            "second_confirmation": None
        }
        
        self.logs.append(override_log)
        self._save_logs()
        
        logger.info(f"Override recorded: {override_log['override_id']} - {action}")
        return override_log
    
    def _requires_two_person(self, decision: Dict) -> bool:
        """Check if decision requires two-person confirmation."""
        if not self.config["settings"]["require_two_person_confirmation"]:
            return False
        
        threshold = self.config["settings"]["two_person_threshold"]
        
        # High-stakes decisions requiring two-person confirmation
        high_stakes_types = ["final_selection", "rejection", "hiring_decision"]
        
        return decision.get("type") in high_stakes_types or threshold == "all"
    
    def confirm_override(
        self,
        override_id: str,
        confirmer_id: str,
        confirmed: bool,
        notes: Optional[str] = None
    ) -> Dict:
        """Second person confirmation for an override."""
        # Find the override
        override = next(
            (log for log in self.logs if log.get("override_id") == override_id),
            None
        )
        if not override:
            return {"error": "Override not found"}
        
        if not override.get("requires_second_confirmation"):
            return {"error": "This override does not require second confirmation"}
        
        # Validate confirmer is different from original overseer
        if override["overseer"]["user_id"] == confirmer_id:
            return {"error": "Second confirmation must be from a different person"}
        
        # Validate confirmer is registered
        confirmer = next(
            (o for o in self.config["designated_overseers"] if o["user_id"] == confirmer_id),
            None
        )
        if not confirmer:
            return {"error": "Confirmer not registered as overseer"}
        
        override["second_confirmation"] = {
            "confirmed_by": confirmer_id,
            "confirmed_by_name": confirmer["name"],
            "confirmed": confirmed,
            "confirmed_at": datetime.now(timezone.utc).isoformat(),
            "notes": notes
        }
        
        self._save_logs()
        
        return override
    
    def emergency_stop(self, initiator_id: str, reason: str) -> Dict:
        """
        Emergency stop for AI system.
        
        Immediately halts all AI decision-making processes.
        Required by EU AI Act Article 14.
        """
        # Validate initiator has permission
        initiator = next(
            (o for o in self.config["designated_overseers"] 
             if o["user_id"] == initiator_id and "stop" in self.config["roles"].get(o["role"], {}).get("permissions", [])),
            None
        )
        if not initiator:
            return {"error": "User not authorized for emergency stop"}
        
        self.config["emergency_stop"] = True
        self.config["emergency_stop_at"] = datetime.now(timezone.utc).isoformat()
        self.config["emergency_stop_by"] = initiator_id
        self.config["emergency_stop_reason"] = reason
        self._save_config()
        
        # Log the emergency stop
        stop_log = {
            "event_type": "emergency_stop",
            "timestamp": self.config["emergency_stop_at"],
            "initiated_by": initiator_id,
            "initiator_name": initiator["name"],
            "reason": reason
        }
        self.logs.append(stop_log)
        self._save_logs()
        
        logger.critical(f"EMERGENCY STOP initiated by {initiator['name']}: {reason}")
        
        return {
            "success": True,
            "emergency_stop": True,
            "stopped_at": self.config["emergency_stop_at"],
            "stopped_by": initiator["name"],
            "reason": reason,
            "message": "AI decision-making has been halted. Manual restart required."
        }
    
    def resume_system(self, initiator_id: str, notes: str) -> Dict:
        """Resume AI system after emergency stop."""
        initiator = next(
            (o for o in self.config["designated_overseers"] 
             if o["user_id"] == initiator_id and "stop" in self.config["roles"].get(o["role"], {}).get("permissions", [])),
            None
        )
        if not initiator:
            return {"error": "User not authorized to resume system"}
        
        if not self.config.get("emergency_stop"):
            return {"error": "System is not in emergency stop state"}
        
        self.config["emergency_stop"] = False
        self.config["resumed_at"] = datetime.now(timezone.utc).isoformat()
        self.config["resumed_by"] = initiator_id
        self._save_config()
        
        # Log the resume
        resume_log = {
            "event_type": "system_resume",
            "timestamp": self.config["resumed_at"],
            "initiated_by": initiator_id,
            "initiator_name": initiator["name"],
            "notes": notes,
            "stop_duration_minutes": self._calculate_stop_duration()
        }
        self.logs.append(resume_log)
        self._save_logs()
        
        logger.info(f"System resumed by {initiator['name']}")
        
        return {
            "success": True,
            "emergency_stop": False,
            "resumed_at": self.config["resumed_at"],
            "resumed_by": initiator["name"]
        }
    
    def _calculate_stop_duration(self) -> float:
        """Calculate how long the system was stopped."""
        if not self.config.get("emergency_stop_at"):
            return 0
        
        stop_time = datetime.fromisoformat(self.config["emergency_stop_at"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - stop_time).total_seconds() / 60
    
    def record_training_completion(
        self,
        user_id: str,
        course_id: str,
        score: float,
        certificate_id: Optional[str] = None
    ) -> Dict:
        """Record AI literacy training completion."""
        if user_id not in self.training["users"]:
            self.training["users"][user_id] = {
                "completed_courses": [],
                "total_score": 0
            }
        
        completion = {
            "course_id": course_id,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "score": score,
            "certificate_id": certificate_id
        }
        
        self.training["users"][user_id]["completed_courses"].append(completion)
        self._save_training()
        
        # Update overseer record
        for overseer in self.config["designated_overseers"]:
            if overseer["user_id"] == user_id:
                overseer["completed_training"].append(course_id)
                
                # Check if all required training complete
                required = self.config["roles"].get(overseer["role"], {}).get("required_training", [])
                if all(t in overseer["completed_training"] for t in required):
                    overseer["training_complete"] = True
                
                self._save_config()
                break
        
        return completion
    
    def get_training_courses(self) -> List[Dict]:
        """Get available AI literacy training courses."""
        default_courses = [
            {
                "id": "ai_literacy_basic",
                "name": "AI Literacy Fundamentals",
                "description": "Basic understanding of AI systems, automation bias, and human oversight responsibilities",
                "duration_hours": 2,
                "required_for": ["primary_overseer", "secondary_overseer", "auditor"]
            },
            {
                "id": "bias_awareness",
                "name": "Bias Recognition & Mitigation",
                "description": "Identifying and mitigating AI bias in recruitment contexts",
                "duration_hours": 3,
                "required_for": ["primary_overseer"]
            },
            {
                "id": "compliance_overview",
                "name": "AI Regulatory Compliance",
                "description": "Overview of EU AI Act, GDPR, and regional compliance requirements",
                "duration_hours": 4,
                "required_for": ["auditor"]
            },
            {
                "id": "life_science_scoring",
                "name": "Life Science Skills Assessment",
                "description": "Understanding technical life-science scoring nuances in AI matching",
                "duration_hours": 2,
                "required_for": ["primary_overseer"]
            }
        ]
        
        if not self.training.get("courses"):
            self.training["courses"] = default_courses
            self._save_training()
        
        return self.training["courses"]
    
    def get_oversight_stats(self) -> Dict:
        """Get oversight statistics."""
        overrides = [log for log in self.logs if log.get("override_id")]
        
        return {
            "total_overseers": len(self.config.get("designated_overseers", [])),
            "active_overseers": len([o for o in self.config.get("designated_overseers", []) if o.get("active")]),
            "training_complete": len([o for o in self.config.get("designated_overseers", []) if o.get("training_complete")]),
            "total_overrides": len(overrides),
            "overrides_last_30_days": len([
                o for o in overrides
                if o.get("timestamp", "") > (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            ]),
            "override_actions": {
                "accepted": len([o for o in overrides if o.get("action") == "ACCEPTED"]),
                "rejected": len([o for o in overrides if o.get("action") == "REJECTED"]),
                "modified": len([o for o in overrides if o.get("action") == "MODIFIED"]),
                "escalated": len([o for o in overrides if o.get("action") == "ESCALATED"])
            },
            "emergency_stop_active": self.config.get("emergency_stop", False),
            "system_status": "stopped" if self.config.get("emergency_stop") else "active"
        }
    
    def get_override_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent override logs."""
        overrides = [log for log in self.logs if log.get("override_id")]
        return overrides[-limit:]


# Initialize service
human_oversight = HumanOversightProtocol()

__all__ = ['human_oversight', 'HumanOversightProtocol']
