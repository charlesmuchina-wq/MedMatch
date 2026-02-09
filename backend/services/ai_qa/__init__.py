"""
AI QA Compliance System - Main Module

A comprehensive AI Quality Assurance and Compliance system for MedMatch,
implementing 2026 EU AI Act, GDPR, and regional regulatory requirements.

Components:
- Core Service: AI Decision Logging, Crypto-Shredding, Bias Detection
- Audit Service: Scheduled Audits, Compliance Checklists, Report Generation
- Oversight Service: Human-in-the-Loop Protocol, Override Management
- Transparency Service: Dashboard, DSAR Management, Real-time Monitoring
"""

from .core_service import (
    crypto_shredding,
    ai_decision_logger,
    bias_auditor,
    CryptoShredding,
    AIDecisionLogger,
    BiasAuditor
)

from .audit_service import (
    audit_scheduler,
    compliance_checker,
    report_generator,
    AuditScheduler,
    ComplianceChecker,
    AuditReportGenerator,
    AuditType,
    ComplianceRegion
)

from .oversight_service import (
    human_oversight,
    HumanOversightProtocol
)

from .transparency_service import (
    dsar_manager,
    transparency_dashboard,
    DSARManager,
    TransparencyDashboard
)

__all__ = [
    # Core Services
    'crypto_shredding',
    'ai_decision_logger',
    'bias_auditor',
    'CryptoShredding',
    'AIDecisionLogger',
    'BiasAuditor',
    
    # Audit Services
    'audit_scheduler',
    'compliance_checker',
    'report_generator',
    'AuditScheduler',
    'ComplianceChecker',
    'AuditReportGenerator',
    'AuditType',
    'ComplianceRegion',
    
    # Oversight Services
    'human_oversight',
    'HumanOversightProtocol',
    
    # Transparency Services
    'dsar_manager',
    'transparency_dashboard',
    'DSARManager',
    'TransparencyDashboard'
]


def get_system_status() -> dict:
    """Get overall AI QA system status."""
    return {
        "ai_qa_version": "2026.Q1",
        "compliance_frameworks": ["EU_AI_Act", "GDPR", "PIPL", "APPI", "CCPA"],
        "crypto_shredding": "active",
        "decision_logging": "active",
        "human_oversight": human_oversight.get_oversight_stats()["system_status"],
        "bias_monitoring": bias_auditor.get_fairness_summary()["status"] if bias_auditor.get_fairness_summary().get("status") != "no_audits" else "ready"
    }
