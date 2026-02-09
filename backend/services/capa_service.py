"""
CAPA (Corrective Action Preventive Action) System
Part of Karau Automator

A quality management system to investigate nonconformances through root cause analysis
and implement corrective/preventive actions with verification of effectiveness.

CAPA Lifecycle:
1. Initiation - Problem statement and initial assessment
2. Investigation - Root cause analysis (probable, eliminated, retained causes)
3. Containment - Immediate actions to prevent further occurrence
4. Resolution - Corrective and Preventive actions (if not closed at containment)
5. VOE - Verification of Effectiveness
6. Closure - Final review and closure
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from enum import Enum
from uuid import uuid4


class CAPAStatus(str, Enum):
    DRAFT = "draft"
    INVESTIGATION = "investigation"
    CONTAINMENT = "containment"
    RESOLUTION = "resolution"
    VOE_PENDING = "voe_pending"
    VOE_IN_PROGRESS = "voe_in_progress"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class CAPAType(str, Enum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"
    BOTH = "both"


class ActionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"


class RootCauseStatus(str, Enum):
    PROBABLE = "probable"
    ELIMINATED = "eliminated"
    RETAINED = "retained"


class CAPAService:
    """CAPA Management Service"""
    
    def __init__(self, storage_path: str = "/app/data/capa"):
        self.storage_path = storage_path
        self._ensure_storage()
        self.capas: Dict[str, Dict] = {}
        self._load_capas()
    
    def _ensure_storage(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    def _load_capas(self):
        """Load CAPAs from storage"""
        capa_file = f"{self.storage_path}/capas.json"
        if os.path.exists(capa_file):
            try:
                with open(capa_file, 'r') as f:
                    self.capas = json.load(f)
            except Exception:
                self.capas = {}
    
    def _save_capas(self):
        """Save CAPAs to storage"""
        capa_file = f"{self.storage_path}/capas.json"
        with open(capa_file, 'w') as f:
            json.dump(self.capas, f, indent=2, default=str)
    
    def create_capa(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new CAPA
        
        Required fields:
        - title: Brief title of the nonconformance
        - problem_statement: Detailed description of the issue
        - capa_type: corrective, preventive, or both
        - severity: critical, high, medium, low
        - source: Where the issue was identified (e.g., QA, audit, customer)
        """
        capa_id = f"CAPA-{datetime.now().strftime('%Y%m%d')}-{str(uuid4())[:8].upper()}"
        
        now = datetime.now(timezone.utc).isoformat()
        
        capa = {
            "id": capa_id,
            "title": data.get("title", ""),
            "problem_statement": data.get("problem_statement", ""),
            "capa_type": data.get("capa_type", CAPAType.BOTH.value),
            "severity": data.get("severity", "medium"),
            "source": data.get("source", ""),
            "status": CAPAStatus.DRAFT.value,
            "created_at": now,
            "updated_at": now,
            "created_by": data.get("created_by", "system"),
            "assigned_to": data.get("assigned_to", ""),
            
            # Investigation Phase
            "investigation": {
                "started_at": None,
                "completed_at": None,
                "investigation_method": data.get("investigation_method", "5 Whys"),
                "probable_causes": [],
                "eliminated_causes": [],
                "retained_causes": []
            },
            
            # Containment Phase
            "containment": {
                "started_at": None,
                "completed_at": None,
                "actions": [],
                "is_contained": False,
                "containment_verified": False,
                "close_at_containment": False
            },
            
            # Resolution Phase (if not closed at containment)
            "resolution": {
                "started_at": None,
                "completed_at": None,
                "corrective_actions": [],
                "preventive_actions": []
            },
            
            # Verification of Effectiveness (VOE)
            "voe": {
                "started_at": None,
                "completed_at": None,
                "verifications": [],
                "overall_effectiveness": None,
                "attestation": None
            },
            
            # Closure
            "closure": {
                "closed_at": None,
                "closed_by": None,
                "closure_notes": "",
                "lessons_learned": ""
            },
            
            # Audit trail
            "history": [
                {
                    "timestamp": now,
                    "action": "created",
                    "user": data.get("created_by", "system"),
                    "details": "CAPA initiated"
                }
            ],
            
            # Attachments and references
            "attachments": [],
            "related_capas": [],
            "impacted_processes": data.get("impacted_processes", []),
            "tags": data.get("tags", [])
        }
        
        self.capas[capa_id] = capa
        self._save_capas()
        
        return capa
    
    def get_capa(self, capa_id: str) -> Optional[Dict[str, Any]]:
        """Get a CAPA by ID"""
        return self.capas.get(capa_id)
    
    def list_capas(self, status: Optional[str] = None, 
                   capa_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all CAPAs with optional filters"""
        capas = list(self.capas.values())
        
        if status:
            capas = [c for c in capas if c["status"] == status]
        
        if capa_type:
            capas = [c for c in capas if c["capa_type"] == capa_type]
        
        # Sort by created_at descending
        capas.sort(key=lambda x: x["created_at"], reverse=True)
        
        return capas
    
    def update_status(self, capa_id: str, new_status: str, 
                      user: str = "system", notes: str = "") -> Dict[str, Any]:
        """Update CAPA status"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        now = datetime.now(timezone.utc).isoformat()
        old_status = capa["status"]
        capa["status"] = new_status
        capa["updated_at"] = now
        
        # Update phase timestamps
        if new_status == CAPAStatus.INVESTIGATION.value:
            capa["investigation"]["started_at"] = now
        elif new_status == CAPAStatus.CONTAINMENT.value:
            capa["investigation"]["completed_at"] = now
            capa["containment"]["started_at"] = now
        elif new_status == CAPAStatus.RESOLUTION.value:
            capa["containment"]["completed_at"] = now
            capa["resolution"]["started_at"] = now
        elif new_status == CAPAStatus.VOE_PENDING.value:
            capa["resolution"]["completed_at"] = now
        elif new_status == CAPAStatus.VOE_IN_PROGRESS.value:
            capa["voe"]["started_at"] = now
        elif new_status == CAPAStatus.CLOSED.value:
            capa["voe"]["completed_at"] = now
            capa["closure"]["closed_at"] = now
            capa["closure"]["closed_by"] = user
        
        capa["history"].append({
            "timestamp": now,
            "action": "status_change",
            "user": user,
            "details": f"Status changed from {old_status} to {new_status}. {notes}"
        })
        
        self._save_capas()
        return capa
    
    # === INVESTIGATION PHASE ===
    
    def add_probable_cause(self, capa_id: str, cause: Dict[str, Any]) -> Dict[str, Any]:
        """Add a probable root cause"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        cause_entry = {
            "id": str(uuid4())[:8],
            "description": cause.get("description", ""),
            "category": cause.get("category", ""),  # technical, process, human, environmental
            "evidence": cause.get("evidence", ""),
            "status": RootCauseStatus.PROBABLE.value,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "added_by": cause.get("added_by", "system")
        }
        
        capa["investigation"]["probable_causes"].append(cause_entry)
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return cause_entry
    
    def eliminate_cause(self, capa_id: str, cause_id: str, 
                        reason: str, user: str = "system") -> Dict[str, Any]:
        """Eliminate a probable cause with justification"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Find and move the cause
        for i, cause in enumerate(capa["investigation"]["probable_causes"]):
            if cause["id"] == cause_id:
                cause["status"] = RootCauseStatus.ELIMINATED.value
                cause["elimination_reason"] = reason
                cause["eliminated_at"] = datetime.now(timezone.utc).isoformat()
                cause["eliminated_by"] = user
                
                capa["investigation"]["eliminated_causes"].append(cause)
                capa["investigation"]["probable_causes"].pop(i)
                break
        
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return capa
    
    def retain_cause(self, capa_id: str, cause_id: str, 
                     justification: str, user: str = "system") -> Dict[str, Any]:
        """Retain a cause as confirmed root cause"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Find and move the cause
        for i, cause in enumerate(capa["investigation"]["probable_causes"]):
            if cause["id"] == cause_id:
                cause["status"] = RootCauseStatus.RETAINED.value
                cause["retention_justification"] = justification
                cause["retained_at"] = datetime.now(timezone.utc).isoformat()
                cause["retained_by"] = user
                cause["planned_actions"] = []  # Actions will be added
                
                capa["investigation"]["retained_causes"].append(cause)
                capa["investigation"]["probable_causes"].pop(i)
                break
        
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return capa
    
    # === CONTAINMENT PHASE ===
    
    def add_containment_action(self, capa_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Add a containment action"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        action_entry = {
            "id": str(uuid4())[:8],
            "description": action.get("description", ""),
            "action_type": "containment",
            "addresses_cause_id": action.get("addresses_cause_id"),
            "responsible": action.get("responsible", ""),
            "due_date": action.get("due_date"),
            "status": ActionStatus.PLANNED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "completion_notes": "",
            "verification": None
        }
        
        capa["containment"]["actions"].append(action_entry)
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return action_entry
    
    def complete_containment_action(self, capa_id: str, action_id: str,
                                    notes: str, user: str = "system") -> Dict[str, Any]:
        """Mark a containment action as completed"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        for action in capa["containment"]["actions"]:
            if action["id"] == action_id:
                action["status"] = ActionStatus.COMPLETED.value
                action["completed_at"] = datetime.now(timezone.utc).isoformat()
                action["completion_notes"] = notes
                action["completed_by"] = user
                break
        
        # Check if all containment actions are complete
        all_complete = all(
            a["status"] in [ActionStatus.COMPLETED.value, ActionStatus.VERIFIED.value]
            for a in capa["containment"]["actions"]
        )
        capa["containment"]["is_contained"] = all_complete
        
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return capa
    
    def close_at_containment(self, capa_id: str, justification: str,
                             user: str = "system") -> Dict[str, Any]:
        """Close CAPA at containment phase (if immediate correction resolved the issue)"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        if not capa["containment"]["is_contained"]:
            raise ValueError("Cannot close at containment - containment actions not complete")
        
        now = datetime.now(timezone.utc).isoformat()
        capa["containment"]["close_at_containment"] = True
        capa["containment"]["completed_at"] = now
        capa["closure"]["closed_at"] = now
        capa["closure"]["closed_by"] = user
        capa["closure"]["closure_notes"] = f"Closed at containment: {justification}"
        capa["status"] = CAPAStatus.CLOSED.value
        
        capa["history"].append({
            "timestamp": now,
            "action": "closed_at_containment",
            "user": user,
            "details": justification
        })
        
        self._save_capas()
        return capa
    
    # === RESOLUTION PHASE ===
    
    def add_corrective_action(self, capa_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Add a corrective action"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        action_entry = {
            "id": str(uuid4())[:8],
            "description": action.get("description", ""),
            "action_type": "corrective",
            "addresses_cause_id": action.get("addresses_cause_id"),
            "how_it_addresses_problem": action.get("how_it_addresses_problem", ""),
            "how_it_prevents_recurrence": action.get("how_it_prevents_recurrence", ""),
            "responsible": action.get("responsible", ""),
            "due_date": action.get("due_date"),
            "status": ActionStatus.PLANNED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "completion_notes": "",
            "verification": None
        }
        
        capa["resolution"]["corrective_actions"].append(action_entry)
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return action_entry
    
    def add_preventive_action(self, capa_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Add a preventive action (safeguard to prevent future occurrence)"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        action_entry = {
            "id": str(uuid4())[:8],
            "description": action.get("description", ""),
            "action_type": "preventive",
            "addresses_cause_id": action.get("addresses_cause_id"),
            "safeguard_type": action.get("safeguard_type", ""),  # technical, process, training
            "how_it_prevents_future": action.get("how_it_prevents_future", ""),
            "responsible": action.get("responsible", ""),
            "due_date": action.get("due_date"),
            "status": ActionStatus.PLANNED.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
            "completion_notes": "",
            "verification": None
        }
        
        capa["resolution"]["preventive_actions"].append(action_entry)
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return action_entry
    
    def complete_action(self, capa_id: str, action_id: str, action_type: str,
                        notes: str, user: str = "system") -> Dict[str, Any]:
        """Complete a corrective or preventive action"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        actions_list = (capa["resolution"]["corrective_actions"] 
                       if action_type == "corrective" 
                       else capa["resolution"]["preventive_actions"])
        
        for action in actions_list:
            if action["id"] == action_id:
                action["status"] = ActionStatus.COMPLETED.value
                action["completed_at"] = datetime.now(timezone.utc).isoformat()
                action["completion_notes"] = notes
                action["completed_by"] = user
                break
        
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return capa
    
    # === VOE (Verification of Effectiveness) ===
    
    def add_voe(self, capa_id: str, voe: Dict[str, Any]) -> Dict[str, Any]:
        """Add a Verification of Effectiveness entry"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        voe_entry = {
            "id": str(uuid4())[:8],
            "action_id": voe.get("action_id"),  # Which action is being verified
            "verification_method": voe.get("verification_method", ""),
            "acceptance_criteria": voe.get("acceptance_criteria", ""),
            "test_procedure": voe.get("test_procedure", ""),
            "impacted_process": voe.get("impacted_process", ""),
            "responsible": voe.get("responsible", ""),
            "due_date": voe.get("due_date"),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "executed_at": None,
            "result": None,  # pass, fail, partial
            "evidence": "",
            "notes": ""
        }
        
        capa["voe"]["verifications"].append(voe_entry)
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return voe_entry
    
    def execute_voe(self, capa_id: str, voe_id: str, result: str,
                    evidence: str, notes: str, user: str = "system") -> Dict[str, Any]:
        """Execute a VOE and record results"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        for voe in capa["voe"]["verifications"]:
            if voe["id"] == voe_id:
                voe["status"] = "completed"
                voe["executed_at"] = datetime.now(timezone.utc).isoformat()
                voe["result"] = result  # pass, fail, partial
                voe["evidence"] = evidence
                voe["notes"] = notes
                voe["executed_by"] = user
                break
        
        # Check overall effectiveness
        all_voes = capa["voe"]["verifications"]
        if all_voes and all(v["status"] == "completed" for v in all_voes):
            passed = sum(1 for v in all_voes if v["result"] == "pass")
            total = len(all_voes)
            
            if passed == total:
                capa["voe"]["overall_effectiveness"] = "effective"
            elif passed >= total * 0.8:
                capa["voe"]["overall_effectiveness"] = "partially_effective"
            else:
                capa["voe"]["overall_effectiveness"] = "ineffective"
        
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return capa
    
    def attest_voe(self, capa_id: str, attestation: str, 
                   attester: str) -> Dict[str, Any]:
        """Provide final attestation for VOE"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        capa["voe"]["attestation"] = {
            "statement": attestation,
            "attested_by": attester,
            "attested_at": datetime.now(timezone.utc).isoformat()
        }
        
        capa["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_capas()
        
        return capa
    
    # === CLOSURE ===
    
    def close_capa(self, capa_id: str, closure_notes: str,
                   lessons_learned: str, user: str = "system") -> Dict[str, Any]:
        """Close the CAPA after VOE completion"""
        capa = self.capas.get(capa_id)
        if not capa:
            raise ValueError(f"CAPA {capa_id} not found")
        
        # Verify all VOEs are complete
        all_voes_complete = all(
            v["status"] == "completed" 
            for v in capa["voe"]["verifications"]
        )
        
        if not all_voes_complete and capa["voe"]["verifications"]:
            raise ValueError("Cannot close CAPA - VOE not complete")
        
        now = datetime.now(timezone.utc).isoformat()
        capa["status"] = CAPAStatus.CLOSED.value
        capa["closure"]["closed_at"] = now
        capa["closure"]["closed_by"] = user
        capa["closure"]["closure_notes"] = closure_notes
        capa["closure"]["lessons_learned"] = lessons_learned
        capa["voe"]["completed_at"] = now
        
        capa["history"].append({
            "timestamp": now,
            "action": "closed",
            "user": user,
            "details": closure_notes
        })
        
        self._save_capas()
        return capa
    
    # === REPORTS ===
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary for dashboard display"""
        capas = list(self.capas.values())
        
        status_counts = {}
        for status in CAPAStatus:
            status_counts[status.value] = sum(1 for c in capas if c["status"] == status.value)
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for c in capas:
            if c["status"] != CAPAStatus.CLOSED.value:
                severity_counts[c.get("severity", "medium")] += 1
        
        # Calculate average time to close
        closed_capas = [c for c in capas if c["status"] == CAPAStatus.CLOSED.value]
        avg_days = 0
        if closed_capas:
            total_days = 0
            for c in closed_capas:
                created = datetime.fromisoformat(c["created_at"].replace('Z', '+00:00'))
                closed = datetime.fromisoformat(c["closure"]["closed_at"].replace('Z', '+00:00'))
                total_days += (closed - created).days
            avg_days = total_days / len(closed_capas)
        
        return {
            "total_capas": len(capas),
            "open_capas": len(capas) - status_counts.get(CAPAStatus.CLOSED.value, 0) - status_counts.get(CAPAStatus.CANCELLED.value, 0),
            "status_distribution": status_counts,
            "severity_distribution": severity_counts,
            "average_days_to_close": round(avg_days, 1),
            "recent_capas": sorted(capas, key=lambda x: x["created_at"], reverse=True)[:5]
        }


# Singleton instance
capa_service = CAPAService()
