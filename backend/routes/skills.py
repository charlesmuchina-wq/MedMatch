"""
Skill Assessment Routes
Handles: Skill verification tests, certifications, badges
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone, timedelta
import uuid
import logging
import json

from utils.database import db
from utils.config import EMERGENT_LLM_KEY
from routes.auth import get_current_user

router = APIRouter(prefix="/skills", tags=["Skill Assessments"])

# ============== Models ==============

class StartAssessmentRequest(BaseModel):
    skill_name: str
    difficulty: str = "intermediate"  # beginner, intermediate, advanced

class SubmitAnswerRequest(BaseModel):
    assessment_id: str
    question_index: int
    answer: str

class SubmitAssessmentRequest(BaseModel):
    assessment_id: str
    answers: List[dict]  # [{question_index: 0, answer: "A"}, ...]

# ============== Available Assessments ==============

SKILL_ASSESSMENTS = {
    # ============== Quality Engineering ==============
    "Supplier Quality Management": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🏭",
        "badge_color": "#1E88E5",
        "description": "Supplier audits, PPAP, supplier scorecards, corrective actions, supplier development"
    },
    "Manufacturing Quality": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "⚙️",
        "badge_color": "#43A047",
        "description": "Process control, defect prevention, quality control plans, inspection methods"
    },
    "ISO 13485 (Medical Devices)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 35,
        "passing_score": 80,
        "badge_icon": "🏥",
        "badge_color": "#E53935",
        "description": "Medical device QMS, design controls, risk management, regulatory compliance"
    },
    "ISO 9001": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "✅",
        "badge_color": "#00897B",
        "description": "Quality management systems, process approach, continual improvement"
    },
    "FDA 21 CFR Part 820": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 35,
        "passing_score": 80,
        "badge_icon": "📜",
        "badge_color": "#5E35B1",
        "description": "FDA QSR, design controls, CAPA, DHF/DMR/DHR, complaint handling"
    },
    "Six Sigma (Green Belt)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📈",
        "badge_color": "#00ACC1",
        "description": "DMAIC, statistical analysis, process improvement, variation reduction"
    },
    "Six Sigma (Black Belt)": {
        "category": "Quality Engineering",
        "questions": 20,
        "time_limit": 45,
        "passing_score": 80,
        "badge_icon": "🎯",
        "badge_color": "#212121",
        "description": "Advanced statistics, DOE, hypothesis testing, project leadership"
    },
    "Root Cause Analysis": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🔍",
        "badge_color": "#FF7043",
        "description": "8D, 5 Whys, fishbone diagrams, fault tree analysis, CAPA"
    },
    "Statistical Process Control (SPC)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📉",
        "badge_color": "#7B1FA2",
        "description": "Control charts, Cp/Cpk, process capability, variation analysis"
    },
    "Measurement System Analysis (MSA)": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📏",
        "badge_color": "#0288D1",
        "description": "Gage R&R, bias studies, linearity, stability, measurement uncertainty"
    },
    "FMEA (Failure Mode Effects Analysis)": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "⚠️",
        "badge_color": "#FFA000",
        "description": "Design FMEA, Process FMEA, risk prioritization, severity/occurrence/detection"
    },
    "APQP/PPAP": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📋",
        "badge_color": "#0D47A1",
        "description": "Advanced Product Quality Planning, Production Part Approval Process, control plans"
    },
    "Auditing (Lead Auditor)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🔎",
        "badge_color": "#37474F",
        "description": "Internal/external audits, audit planning, nonconformance documentation, audit reporting"
    },
    "GD&T (Geometric Dimensioning & Tolerancing)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📐",
        "badge_color": "#546E7A",
        "description": "ASME Y14.5, datums, feature control frames, tolerances, MMC/LMC"
    },
    "Lean Manufacturing": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🔧",
        "badge_color": "#689F38",
        "description": "Waste elimination, value stream mapping, 5S, Kaizen, continuous flow"
    },
    "CAPA Management": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🛠️",
        "badge_color": "#D84315",
        "description": "Corrective and Preventive Actions, effectiveness verification, trending"
    },
    "Risk Management (ISO 14971)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "⚖️",
        "badge_color": "#C62828",
        "description": "Risk analysis, risk evaluation, risk control, benefit-risk analysis"
    },
    "Metrology & Calibration": {
        "category": "Quality Engineering",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🔬",
        "badge_color": "#1565C0",
        "description": "Calibration standards, traceability, measurement uncertainty, ISO 17025"
    },
    "AS9100 (Aerospace Quality)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "✈️",
        "badge_color": "#283593",
        "description": "Aerospace QMS, configuration management, first article inspection, special processes"
    },
    "IATF 16949 (Automotive Quality)": {
        "category": "Quality Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🚗",
        "badge_color": "#4527A0",
        "description": "Automotive QMS, core tools, customer-specific requirements, warranty management"
    },
    
    # ============== Aerospace ==============
    "AS9100D Fundamentals": {
        "category": "Aerospace",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "✈️",
        "badge_color": "#1565C0",
        "description": "Aerospace QMS requirements, risk-based thinking, documented information"
    },
    "AS9102 First Article Inspection": {
        "category": "Aerospace",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📋",
        "badge_color": "#0D47A1",
        "description": "FAI forms, balloon drawings, partial/full FAI, delta FAI requirements"
    },
    "AS9145 APQP & PPAP (Aerospace)": {
        "category": "Aerospace",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📊",
        "badge_color": "#1976D2",
        "description": "Advanced Product Quality Planning for aerospace, production readiness reviews"
    },
    "NADCAP": {
        "category": "Aerospace",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🏅",
        "badge_color": "#283593",
        "description": "Special processes accreditation, heat treat, NDT, welding, coatings"
    },
    "Aerospace Configuration Management": {
        "category": "Aerospace",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "⚙️",
        "badge_color": "#303F9F",
        "description": "Configuration identification, control, status accounting, audits"
    },
    "Special Processes (Aerospace)": {
        "category": "Aerospace",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🔥",
        "badge_color": "#FF5722",
        "description": "Heat treatment, NDT, welding, surface treatment, composite processing"
    },
    "Counterfeit Parts Prevention": {
        "category": "Aerospace",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🔒",
        "badge_color": "#455A64",
        "description": "AS6174, suspect/counterfeit detection, supply chain risk mitigation"
    },
    "Aerospace NDT (Non-Destructive Testing)": {
        "category": "Aerospace",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🔍",
        "badge_color": "#00796B",
        "description": "RT, UT, MT, PT, ET methods, NAS 410/EN 4179 certification levels"
    },
    "Flight Safety Parts": {
        "category": "Aerospace",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 85,
        "badge_icon": "🛡️",
        "badge_color": "#B71C1C",
        "description": "Critical safety items, traceability, documentation requirements"
    },
    "Aerospace Materials & Specifications": {
        "category": "Aerospace",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🧪",
        "badge_color": "#6A1B9A",
        "description": "AMS, MIL-SPEC, material certifications, shelf life management"
    },
    
    # ============== Automotive ==============
    "IATF 16949 Fundamentals": {
        "category": "Automotive",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🚗",
        "badge_color": "#1565C0",
        "description": "Automotive QMS, customer-specific requirements, process approach"
    },
    "Automotive Core Tools (APQP)": {
        "category": "Automotive",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📐",
        "badge_color": "#0D47A1",
        "description": "Advanced Product Quality Planning phases, deliverables, milestones"
    },
    "Automotive Core Tools (PPAP)": {
        "category": "Automotive",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📦",
        "badge_color": "#1976D2",
        "description": "18 PPAP elements, submission levels, PSW, customer approval"
    },
    "Automotive Core Tools (FMEA)": {
        "category": "Automotive",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "⚠️",
        "badge_color": "#F57C00",
        "description": "AIAG-VDA FMEA, action priority, 7-step approach, linking D-FMEA to P-FMEA"
    },
    "Automotive Core Tools (SPC)": {
        "category": "Automotive",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📈",
        "badge_color": "#388E3C",
        "description": "Control charts, process capability, Cpk/Ppk, special vs common causes"
    },
    "Automotive Core Tools (MSA)": {
        "category": "Automotive",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📏",
        "badge_color": "#7B1FA2",
        "description": "Gage R&R, bias, linearity, stability studies, attribute MSA"
    },
    "VDA 6.3 Process Audit": {
        "category": "Automotive",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🔎",
        "badge_color": "#C62828",
        "description": "German automotive process audit standard, P-elements, scoring methodology"
    },
    "CQI Standards": {
        "category": "Automotive",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📘",
        "badge_color": "#00838F",
        "description": "CQI-9 Heat Treat, CQI-11 Plating, CQI-12 Coating, special process assessments"
    },
    "Automotive Problem Solving (8D)": {
        "category": "Automotive",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🎯",
        "badge_color": "#AD1457",
        "description": "Global 8D, containment, root cause analysis, verification of effectiveness"
    },
    "Automotive Warranty Management": {
        "category": "Automotive",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "💰",
        "badge_color": "#6D4C41",
        "description": "Warranty data analysis, NTF management, field return analysis"
    },
    
    # ============== Industrial/Manufacturing ==============
    "Industrial Safety (OSHA)": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "⛑️",
        "badge_color": "#FF6F00",
        "description": "OSHA regulations, hazard identification, PPE, lockout/tagout, ergonomics"
    },
    "ISO 45001 (Occupational Health & Safety)": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🦺",
        "badge_color": "#E65100",
        "description": "OH&S management system, hazard identification, risk assessment, worker participation"
    },
    "ISO 14001 (Environmental Management)": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🌿",
        "badge_color": "#2E7D32",
        "description": "Environmental management system, aspects/impacts, compliance obligations"
    },
    "Industrial Maintenance (TPM)": {
        "category": "Industrial",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🔧",
        "badge_color": "#5D4037",
        "description": "Total Productive Maintenance, OEE, autonomous maintenance, planned maintenance"
    },
    "Production Planning & Control": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📅",
        "badge_color": "#0277BD",
        "description": "MRP, MPS, capacity planning, scheduling, inventory management"
    },
    "Industrial Engineering": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "⚡",
        "badge_color": "#7B1FA2",
        "description": "Time studies, line balancing, work measurement, facility layout"
    },
    "Welding Inspection (CWI)": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🔥",
        "badge_color": "#BF360C",
        "description": "AWS D1.1, weld symbols, visual inspection, discontinuities, WPS/PQR"
    },
    "Industrial Automation & PLC": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🤖",
        "badge_color": "#37474F",
        "description": "PLC programming, ladder logic, HMI, sensors, industrial networks"
    },
    "Material Handling & Logistics": {
        "category": "Industrial",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📦",
        "badge_color": "#4E342E",
        "description": "Warehouse management, FIFO, inventory control, forklift safety"
    },
    "Industrial Quality Control": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "✅",
        "badge_color": "#1B5E20",
        "description": "Incoming inspection, in-process control, final inspection, sampling plans"
    },
    "Lean Six Sigma (Industrial)": {
        "category": "Industrial",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🎯",
        "badge_color": "#311B92",
        "description": "VSM, Kaizen events, SMED, Poka-Yoke, standard work"
    },
    "ESD Control (Electronics)": {
        "category": "Industrial",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "⚡",
        "badge_color": "#FFC107",
        "description": "ANSI/ESD S20.20, EPA requirements, grounding, ionization, packaging"
    },
    
    # ============== Pharmaceuticals ==============
    "cGMP (Current Good Manufacturing Practice)": {
        "category": "Pharmaceuticals",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "💊",
        "badge_color": "#1565C0",
        "description": "FDA 21 CFR Parts 210/211, manufacturing controls, documentation"
    },
    "FDA 21 CFR Part 11": {
        "category": "Pharmaceuticals",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 80,
        "badge_icon": "💻",
        "badge_color": "#0D47A1",
        "description": "Electronic records, electronic signatures, audit trails, validation"
    },
    "Pharmaceutical Validation (IQ/OQ/PQ)": {
        "category": "Pharmaceuticals",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "✓",
        "badge_color": "#1976D2",
        "description": "Equipment qualification, process validation, cleaning validation"
    },
    "Sterile Manufacturing": {
        "category": "Pharmaceuticals",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 85,
        "badge_icon": "🧫",
        "badge_color": "#00897B",
        "description": "Aseptic processing, cleanroom operations, media fills, environmental monitoring"
    },
    "Pharmaceutical Quality Control": {
        "category": "Pharmaceuticals",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🔬",
        "badge_color": "#7B1FA2",
        "description": "Analytical testing, release testing, stability studies, OOS investigations"
    },
    "GxP Compliance": {
        "category": "Pharmaceuticals",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "📋",
        "badge_color": "#C62828",
        "description": "GLP, GCP, GDP, GMP fundamentals, regulatory inspections"
    },
    "Pharmaceutical Packaging": {
        "category": "Pharmaceuticals",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📦",
        "badge_color": "#5D4037",
        "description": "Primary/secondary packaging, serialization, anti-counterfeiting, labeling"
    },
    "Drug Product Development": {
        "category": "Pharmaceuticals",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🧪",
        "badge_color": "#6A1B9A",
        "description": "Formulation development, scale-up, tech transfer, CMC documentation"
    },
    "Pharmacovigilance": {
        "category": "Pharmaceuticals",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 80,
        "badge_icon": "⚠️",
        "badge_color": "#E65100",
        "description": "Adverse event reporting, signal detection, risk management, PSUR/PBRER"
    },
    "Data Integrity (ALCOA+)": {
        "category": "Pharmaceuticals",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 85,
        "badge_icon": "🔒",
        "badge_color": "#37474F",
        "description": "Attributable, Legible, Contemporaneous, Original, Accurate principles"
    },
    
    # ============== Medical Devices ==============
    "ISO 13485 QMS": {
        "category": "Medical Devices",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🏥",
        "badge_color": "#1565C0",
        "description": "Medical device quality management system requirements"
    },
    "FDA 21 CFR Part 820 (QSR)": {
        "category": "Medical Devices",
        "questions": 15,
        "time_limit": 35,
        "passing_score": 80,
        "badge_icon": "📜",
        "badge_color": "#0D47A1",
        "description": "Quality System Regulation, design controls, production controls"
    },
    "Medical Device Design Controls": {
        "category": "Medical Devices",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "📐",
        "badge_color": "#1976D2",
        "description": "Design inputs/outputs, verification, validation, design transfer"
    },
    "ISO 14971 Risk Management": {
        "category": "Medical Devices",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "⚖️",
        "badge_color": "#C62828",
        "description": "Risk analysis, risk evaluation, risk control, residual risk"
    },
    "IEC 62304 (Software Lifecycle)": {
        "category": "Medical Devices",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "💻",
        "badge_color": "#7B1FA2",
        "description": "Medical device software development, safety classification, maintenance"
    },
    "EU MDR (Medical Device Regulation)": {
        "category": "Medical Devices",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🇪🇺",
        "badge_color": "#283593",
        "description": "European medical device regulation, clinical evaluation, UDI, EUDAMED"
    },
    "510(k) & PMA Submissions": {
        "category": "Medical Devices",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📄",
        "badge_color": "#00838F",
        "description": "FDA premarket submissions, substantial equivalence, clinical data"
    },
    "Medical Device Sterilization": {
        "category": "Medical Devices",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 80,
        "badge_icon": "☢️",
        "badge_color": "#FF6F00",
        "description": "EtO, gamma, steam sterilization, sterility assurance level, validation"
    },
    "Biocompatibility (ISO 10993)": {
        "category": "Medical Devices",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 80,
        "badge_icon": "🧬",
        "badge_color": "#2E7D32",
        "description": "Biological evaluation, cytotoxicity, sensitization, implantation testing"
    },
    "Medical Device CAPA": {
        "category": "Medical Devices",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 80,
        "badge_icon": "🛠️",
        "badge_color": "#D84315",
        "description": "Corrective and preventive actions, root cause, effectiveness verification"
    },
    "Post-Market Surveillance": {
        "category": "Medical Devices",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 80,
        "badge_icon": "📊",
        "badge_color": "#5D4037",
        "description": "Complaint handling, MDR/MAUDE reporting, field actions, trending"
    },
    "Clinical Evaluation Reports": {
        "category": "Medical Devices",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📝",
        "badge_color": "#455A64",
        "description": "Literature review, clinical data, benefit-risk analysis, PMCF"
    },
    
    # ============== Biologics ==============
    "Biologics Manufacturing": {
        "category": "Biologics",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🧬",
        "badge_color": "#1565C0",
        "description": "Cell culture, fermentation, purification, formulation, fill-finish"
    },
    "Cell & Gene Therapy": {
        "category": "Biologics",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🔬",
        "badge_color": "#7B1FA2",
        "description": "CAR-T, gene therapy manufacturing, viral vectors, chain of custody"
    },
    "Vaccine Manufacturing": {
        "category": "Biologics",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "💉",
        "badge_color": "#00897B",
        "description": "Antigen production, adjuvants, cold chain, potency testing"
    },
    "Monoclonal Antibodies": {
        "category": "Biologics",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "🧪",
        "badge_color": "#C62828",
        "description": "mAb development, CHO cell culture, downstream processing, characterization"
    },
    "Biosimilars Development": {
        "category": "Biologics",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🔄",
        "badge_color": "#0D47A1",
        "description": "Analytical similarity, PK/PD studies, immunogenicity, regulatory pathway"
    },
    "Biologic Analytical Testing": {
        "category": "Biologics",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 80,
        "badge_icon": "📊",
        "badge_color": "#6A1B9A",
        "description": "Potency assays, identity testing, purity, glycan analysis, mass spec"
    },
    "Upstream Processing": {
        "category": "Biologics",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🏭",
        "badge_color": "#2E7D32",
        "description": "Cell banking, bioreactor operation, fed-batch, perfusion, scale-up"
    },
    "Downstream Processing": {
        "category": "Biologics",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "⚗️",
        "badge_color": "#E65100",
        "description": "Chromatography, filtration, viral clearance, buffer preparation"
    },
    "Biologics Cold Chain": {
        "category": "Biologics",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 80,
        "badge_icon": "❄️",
        "badge_color": "#0277BD",
        "description": "Temperature control, shipping validation, excursion management"
    },
    
    # ============== Biotech ==============
    "Biotechnology Fundamentals": {
        "category": "Biotech",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🧬",
        "badge_color": "#1565C0",
        "description": "Molecular biology, genetics, protein expression, recombinant DNA"
    },
    "CRISPR & Gene Editing": {
        "category": "Biotech",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "✂️",
        "badge_color": "#7B1FA2",
        "description": "Gene editing technologies, guide RNA design, delivery methods, applications"
    },
    "PCR & Molecular Diagnostics": {
        "category": "Biotech",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🔬",
        "badge_color": "#C62828",
        "description": "qPCR, RT-PCR, digital PCR, assay development, validation"
    },
    "Next-Generation Sequencing": {
        "category": "Biotech",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📈",
        "badge_color": "#00897B",
        "description": "NGS platforms, library prep, data analysis, variant calling"
    },
    "Protein Engineering": {
        "category": "Biotech",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🔧",
        "badge_color": "#E65100",
        "description": "Protein design, directed evolution, expression optimization"
    },
    "Bioinformatics": {
        "category": "Biotech",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "💻",
        "badge_color": "#0D47A1",
        "description": "Sequence analysis, structural biology, genomics, proteomics"
    },
    "Bioprocess Development": {
        "category": "Biotech",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "⚙️",
        "badge_color": "#2E7D32",
        "description": "Process development, optimization, scale-up, tech transfer"
    },
    "Regulatory Affairs (Biotech)": {
        "category": "Biotech",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "📋",
        "badge_color": "#455A64",
        "description": "IND/BLA submissions, regulatory strategy, CMC documentation"
    },
    
    # ============== Software Engineering ==============
    "Software Development Lifecycle": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🔄",
        "badge_color": "#1565C0",
        "description": "SDLC methodologies, Agile, Waterfall, DevOps, CI/CD"
    },
    "Python Programming": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🐍",
        "badge_color": "#3776AB",
        "description": "Python syntax, data structures, OOP, libraries, best practices"
    },
    "JavaScript/TypeScript": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📜",
        "badge_color": "#F7DF1E",
        "description": "Modern JS, ES6+, TypeScript, async programming, Node.js"
    },
    "React Development": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "⚛️",
        "badge_color": "#61DAFB",
        "description": "React hooks, state management, component design, performance"
    },
    "Backend Development": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🖥️",
        "badge_color": "#68A063",
        "description": "REST APIs, databases, authentication, server architecture"
    },
    "Database Design (SQL)": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🗄️",
        "badge_color": "#336791",
        "description": "SQL, normalization, indexing, query optimization, transactions"
    },
    "Cloud Architecture (AWS)": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "☁️",
        "badge_color": "#FF9900",
        "description": "AWS services, EC2, S3, Lambda, architecture patterns"
    },
    "Cloud Architecture (Azure)": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "☁️",
        "badge_color": "#0078D4",
        "description": "Azure services, VMs, Blob Storage, Functions, DevOps"
    },
    "Docker & Kubernetes": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🐳",
        "badge_color": "#2496ED",
        "description": "Containerization, orchestration, microservices, deployment"
    },
    "Software Testing & QA": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🧪",
        "badge_color": "#4CAF50",
        "description": "Unit testing, integration testing, TDD, automation frameworks"
    },
    "System Design": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 35,
        "passing_score": 75,
        "badge_icon": "🏗️",
        "badge_color": "#795548",
        "description": "Scalability, distributed systems, caching, load balancing"
    },
    "Cybersecurity Fundamentals": {
        "category": "Software Engineering",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🔐",
        "badge_color": "#D32F2F",
        "description": "Security principles, OWASP, encryption, authentication, authorization"
    },
    
    # ============== AI & Machine Learning ==============
    "Machine Learning Fundamentals": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🤖",
        "badge_color": "#FF6F00",
        "description": "Supervised/unsupervised learning, algorithms, model evaluation"
    },
    "Deep Learning & Neural Networks": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🧠",
        "badge_color": "#7B1FA2",
        "description": "Neural networks, CNNs, RNNs, transformers, training techniques"
    },
    "Natural Language Processing": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "💬",
        "badge_color": "#1976D2",
        "description": "Text processing, embeddings, transformers, LLMs, sentiment analysis"
    },
    "Computer Vision": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "👁️",
        "badge_color": "#00897B",
        "description": "Image classification, object detection, segmentation, GANs"
    },
    "Data Science & Analytics": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "📊",
        "badge_color": "#4B8BBE",
        "description": "Data analysis, visualization, statistics, feature engineering"
    },
    "MLOps & Model Deployment": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🚀",
        "badge_color": "#E65100",
        "description": "Model serving, monitoring, versioning, A/B testing, pipelines"
    },
    "TensorFlow & PyTorch": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "🔥",
        "badge_color": "#FF6F00",
        "description": "Deep learning frameworks, model building, training, optimization"
    },
    "Generative AI & LLMs": {
        "category": "AI & Machine Learning",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 75,
        "badge_icon": "✨",
        "badge_color": "#6A1B9A",
        "description": "GPT, BERT, prompt engineering, fine-tuning, RAG, embeddings"
    },
    "AI Ethics & Responsible AI": {
        "category": "AI & Machine Learning",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "⚖️",
        "badge_color": "#37474F",
        "description": "Bias detection, fairness, explainability, privacy, governance"
    },
    "Reinforcement Learning": {
        "category": "AI & Machine Learning",
        "questions": 12,
        "time_limit": 25,
        "passing_score": 75,
        "badge_icon": "🎮",
        "badge_color": "#C62828",
        "description": "RL algorithms, policy gradients, Q-learning, multi-agent systems"
    },
    
    # ============== Programming ==============
    "Python": {
        "category": "Programming",
        "questions": 15,
        "time_limit": 25,
        "passing_score": 70,
        "badge_icon": "🐍",
        "badge_color": "#3776AB"
    },
    "JavaScript": {
        "category": "Programming",
        "questions": 15,
        "time_limit": 25,
        "passing_score": 70,
        "badge_icon": "⚡",
        "badge_color": "#F7DF1E"
    },
    "React": {
        "category": "Frontend",
        "questions": 15,
        "time_limit": 25,
        "passing_score": 70,
        "badge_icon": "⚛️",
        "badge_color": "#61DAFB"
    },
    "SQL": {
        "category": "Database",
        "questions": 12,
        "time_limit": 20,
        "passing_score": 70,
        "badge_icon": "🗄️",
        "badge_color": "#336791"
    },
    "AWS": {
        "category": "Cloud",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 70,
        "badge_icon": "☁️",
        "badge_color": "#FF9900"
    },
    "Machine Learning": {
        "category": "AI/ML",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 70,
        "badge_icon": "🤖",
        "badge_color": "#FF6F00"
    },
    "Data Science": {
        "category": "AI/ML",
        "questions": 15,
        "time_limit": 30,
        "passing_score": 70,
        "badge_icon": "📊",
        "badge_color": "#4B8BBE"
    },
    "Project Management": {
        "category": "Business",
        "questions": 12,
        "time_limit": 20,
        "passing_score": 70,
        "badge_icon": "📋",
        "badge_color": "#00A36C"
    },
    "Agile/Scrum": {
        "category": "Business",
        "questions": 12,
        "time_limit": 20,
        "passing_score": 70,
        "badge_icon": "🔄",
        "badge_color": "#6495ED"
    },
    "Communication": {
        "category": "Soft Skills",
        "questions": 10,
        "time_limit": 15,
        "passing_score": 70,
        "badge_icon": "💬",
        "badge_color": "#9B59B6"
    }
}

# ============== Routes ==============

@router.get("/categories")
async def get_skill_categories():
    """Get list of all skill assessment categories"""
    categories = {}
    for skill, config in SKILL_ASSESSMENTS.items():
        cat = config["category"]
        if cat not in categories:
            categories[cat] = {
                "name": cat,
                "skills": [],
                "total_assessments": 0
            }
        categories[cat]["skills"].append({
            "skill_name": skill,
            "badge_icon": config["badge_icon"],
            "badge_color": config["badge_color"]
        })
        categories[cat]["total_assessments"] += 1
    
    return {
        "categories": list(categories.values()),
        "total_categories": len(categories)
    }

@router.get("/available")
async def get_available_assessments():
    """Get list of available skill assessments"""
    assessments = []
    for skill, config in SKILL_ASSESSMENTS.items():
        assessments.append({
            "skill_name": skill,
            "category": config["category"],
            "questions": config["questions"],
            "time_limit": config["time_limit"],
            "passing_score": config["passing_score"],
            "badge_icon": config["badge_icon"],
            "badge_color": config["badge_color"]
        })
    
    # Group by category
    categories = {}
    for a in assessments:
        cat = a["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(a)
    
    return {"assessments": assessments, "by_category": categories}

@router.get("/my-badges")
async def get_my_badges(request: Request):
    """Get all badges earned by current user"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    badges = await db.skill_badges.find(
        {"user_id": user["user_id"]},
        {"_id": 0}
    ).sort("earned_at", -1).to_list(100)
    
    return {"badges": badges, "total": len(badges)}

@router.post("/start")
async def start_assessment(req: StartAssessmentRequest, request: Request):
    """Start a skill assessment - uses pre-generated questions for instant start, falls back to AI if needed"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if req.skill_name not in SKILL_ASSESSMENTS:
        raise HTTPException(status_code=400, detail=f"Assessment not available for {req.skill_name}")
    
    config = SKILL_ASSESSMENTS[req.skill_name]
    
    # Check for cooldown (can't retake for 24 hours if failed)
    recent_attempt = await db.skill_assessments.find_one({
        "user_id": user["user_id"],
        "skill_name": req.skill_name,
        "status": "failed",
        "completed_at": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()}
    })
    
    if recent_attempt:
        raise HTTPException(status_code=400, detail="Please wait 24 hours before retaking this assessment")
    
    # Try to get questions from pre-generated bank first (INSTANT - no wait!)
    from services.question_bank import get_questions_from_bank, has_questions_for_skill
    
    questions = []
    use_ai_fallback = False
    
    if has_questions_for_skill(req.skill_name):
        questions = get_questions_from_bank(req.skill_name, req.difficulty, config['questions'])
        logging.info(f"Using pre-generated questions for {req.skill_name} ({len(questions)} questions)")
    
    # Fall back to AI generation only if no pre-generated questions
    if not questions:
        use_ai_fallback = True
        logging.info(f"No pre-generated questions for {req.skill_name}, using AI generation")
        
        if not EMERGENT_LLM_KEY:
            raise HTTPException(status_code=500, detail="AI features not configured")
        
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=f"""You are an expert assessment creator for {req.skill_name}. 
Generate {config['questions']} multiple choice questions to test {req.difficulty} level knowledge.

Return ONLY valid JSON array with this structure:
[
    {{
        "question": "What is...",
        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
        "correct_answer": "A",
        "explanation": "Brief explanation of why A is correct",
        "difficulty": "{req.difficulty}"
    }}
]

Questions should cover practical, real-world scenarios and test genuine understanding.
Include a mix of conceptual and practical questions."""
        ).with_model("openai", "gpt-5.2")
        
        try:
            response = await chat.send_message(UserMessage(
                text=f"Generate {config['questions']} {req.difficulty} level assessment questions for {req.skill_name}."
            ))
            
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            
            questions = json.loads(clean_response)
            
        except Exception as e:
            logging.error(f"AI Assessment generation error: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate assessment questions")
    
    # Store assessment in database
    assessment = {
        "id": f"assess_{uuid.uuid4().hex[:12]}",
        "user_id": user["user_id"],
        "skill_name": req.skill_name,
        "difficulty": req.difficulty,
        "questions": questions,  # Full questions with answers (server-side only)
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "time_limit": config["time_limit"],
        "passing_score": config["passing_score"],
        "answers_submitted": [],
        "score": None,
        "used_ai_generation": use_ai_fallback
    }
    
    await db.skill_assessments.insert_one(assessment)
    
    # Return questions without correct answers
    client_questions = []
    for i, q in enumerate(questions):
        client_questions.append({
            "index": i,
            "question": q["question"],
            "options": q["options"]
        })
    
    return {
        "assessment_id": assessment["id"],
        "skill_name": req.skill_name,
        "questions": client_questions,
        "time_limit": config["time_limit"],
        "total_questions": len(questions),
        "instant_start": not use_ai_fallback  # Let frontend know if instant or AI-generated
    }


@router.post("/submit")
async def submit_assessment(submission: SubmitAssessmentRequest, request: Request):
    """Submit completed assessment and get results"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    assessment = await db.skill_assessments.find_one({
        "id": submission.assessment_id,
        "user_id": user["user_id"],
        "status": "in_progress"
    })
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found or already completed")
    
    # Calculate score
    questions = assessment["questions"]
    correct_count = 0
    results = []
    
    for answer in submission.answers:
        q_idx = answer.get("question_index", 0)
        user_answer = answer.get("answer", "")
        
        if q_idx < len(questions):
            correct = questions[q_idx]["correct_answer"]
            is_correct = user_answer.upper().startswith(correct.upper())
            if is_correct:
                correct_count += 1
            
            results.append({
                "question_index": q_idx,
                "question": questions[q_idx]["question"],
                "your_answer": user_answer,
                "correct_answer": correct,
                "is_correct": is_correct,
                "explanation": questions[q_idx].get("explanation", "")
            })
    
    score = round(correct_count / len(questions) * 100, 1) if questions else 0
    passed = score >= assessment["passing_score"]
    
    # Update assessment
    await db.skill_assessments.update_one(
        {"id": submission.assessment_id},
        {"$set": {
            "status": "passed" if passed else "failed",
            "score": score,
            "correct_count": correct_count,
            "total_questions": len(questions),
            "answers_submitted": submission.answers,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Award badge if passed
    badge = None
    if passed:
        config = SKILL_ASSESSMENTS.get(assessment["skill_name"], {})
        badge = {
            "id": f"badge_{uuid.uuid4().hex[:12]}",
            "user_id": user["user_id"],
            "skill_name": assessment["skill_name"],
            "difficulty": assessment["difficulty"],
            "score": score,
            "badge_icon": config.get("badge_icon", "🏆"),
            "badge_color": config.get("badge_color", "#4CAF50"),
            "earned_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": None,  # Badges don't expire
            "verified": True
        }
        
        await db.skill_badges.insert_one(badge)
        
        # Add skill to user's verified skills
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$addToSet": {"verified_skills": {
                "skill": assessment["skill_name"],
                "level": assessment["difficulty"],
                "score": score,
                "verified_at": datetime.now(timezone.utc).isoformat()
            }}}
        )
        
        # Update resume with verified badge
        await db.resumes.update_one(
            {"user_id": user["user_id"]},
            {"$addToSet": {"verified_skills": assessment["skill_name"]}}
        )
    
    return {
        "passed": passed,
        "score": score,
        "correct_count": correct_count,
        "total_questions": len(questions),
        "passing_score": assessment["passing_score"],
        "results": results,
        "badge": badge,
        "message": f"Congratulations! You earned the {assessment['skill_name']} badge!" if passed else f"You need {assessment['passing_score']}% to pass. Try again in 24 hours."
    }

@router.get("/history")
async def get_assessment_history(request: Request):
    """Get user's assessment history"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    assessments = await db.skill_assessments.find(
        {"user_id": user["user_id"], "status": {"$ne": "in_progress"}},
        {"_id": 0, "questions": 0, "answers_submitted": 0}  # Don't return questions/answers
    ).sort("completed_at", -1).to_list(50)
    
    return {"history": assessments}

@router.get("/leaderboard/{skill_name}")
async def get_skill_leaderboard(skill_name: str):
    """Get top scorers for a skill"""
    if skill_name not in SKILL_ASSESSMENTS:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    # Get top 10 scorers
    top_scores = await db.skill_assessments.aggregate([
        {"$match": {"skill_name": skill_name, "status": "passed"}},
        {"$sort": {"score": -1, "completed_at": 1}},
        {"$limit": 10},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "user"
        }},
        {"$project": {
            "_id": 0,
            "score": 1,
            "difficulty": 1,
            "completed_at": 1,
            "user_name": {"$arrayElemAt": ["$user.name", 0]}
        }}
    ]).to_list(10)
    
    # Add rank
    for i, score in enumerate(top_scores):
        score["rank"] = i + 1
        if not score.get("user_name"):
            score["user_name"] = "Anonymous"
    
    return {"skill_name": skill_name, "leaderboard": top_scores}

@router.get("/verify/{user_id}/{skill_name}")
async def verify_skill_badge(user_id: str, skill_name: str):
    """Public endpoint to verify a user's skill badge"""
    badge = await db.skill_badges.find_one(
        {"user_id": user_id, "skill_name": skill_name},
        {"_id": 0}
    )
    
    if not badge:
        return {"verified": False, "message": "Badge not found"}
    
    return {
        "verified": True,
        "skill_name": badge["skill_name"],
        "difficulty": badge["difficulty"],
        "score": badge["score"],
        "earned_at": badge["earned_at"],
        "badge_icon": badge["badge_icon"]
    }
