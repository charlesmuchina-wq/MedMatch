"""
MedMatch Global Talent Taxonomy
Complete sector, role, certification, and skill definitions for Life Sciences & Engineering ecosystem.
"""

# ============== SECTOR TAXONOMY ==============

SECTORS = {
    "life_sciences": {
        "id": "life_sciences",
        "name": "Life Sciences & Research",
        "description": "Pharma, Biotech - Discovery, testing, and mass production of medicine",
        "icon": "flask",
        "color": "#10B981",
        "subsectors": {
            "entry_lab": {
                "name": "Entry/Lab Support",
                "roles": ["Lab Assistant", "Clinical Trial Assistant (CTA)", "Manufacturing Technician", "Documentation Specialist"]
            },
            "scientific_rd": {
                "name": "Scientific & R&D",
                "roles": ["Formulation Scientist", "Pharmacologist", "Microbiologist", "Clinical Research Associate (CRA)", "Biostatistician"]
            },
            "quality_safety": {
                "name": "Quality & Safety",
                "roles": ["Drug Safety Officer (Pharmacovigilance)", "Quality Control (QC) Analyst", "Validation Engineer"]
            },
            "leadership": {
                "name": "Leadership",
                "roles": ["Head of Clinical Operations", "Chief Scientific Officer (CSO)", "Medical Science Liaison (MSL)"]
            }
        }
    },
    "medical_devices": {
        "id": "medical_devices",
        "name": "Medical Device & Biomedical Engineering",
        "description": "The intersection of engineering and human biology",
        "icon": "heart-pulse",
        "color": "#EF4444",
        "subsectors": {
            "product_dev": {
                "name": "Product Development",
                "roles": ["Biomedical Engineer", "R&D Engineer", "Embedded Systems Developer", "Industrial Designer"]
            },
            "operations_quality": {
                "name": "Operations & Quality",
                "roles": ["Design Assurance Engineer", "Sterilization Specialist", "Field Clinical Engineer", "CAPA Specialist"]
            },
            "regulatory_commercial": {
                "name": "Regulatory & Commercial",
                "roles": ["Regulatory Affairs Manager (FDA/EU MDR)", "Product Manager", "Medical Device Sales Rep"]
            }
        }
    },
    "engineering": {
        "id": "engineering",
        "name": "Multi-Sector Engineering",
        "description": "Aerospace, Automotive, Energy, Infrastructure - The Industrial Core",
        "icon": "cog",
        "color": "#3B82F6",
        "subsectors": {
            "aerospace_defense": {
                "name": "Aerospace & Defense",
                "roles": ["Avionics Engineer", "Propulsion Engineer", "Satellite Systems Engineer", "Flight Test Engineer"]
            },
            "automotive": {
                "name": "Automotive",
                "roles": ["EV Battery Engineer", "Autonomous Systems Engineer", "Powertrain Engineer", "Vehicle Dynamics Engineer"]
            },
            "energy": {
                "name": "Energy",
                "roles": ["Renewable Energy Engineer", "Nuclear Engineer", "Power Grid Engineer", "Petroleum Engineer"]
            },
            "infrastructure": {
                "name": "Infrastructure",
                "roles": ["Civil Engineer", "Structural Engineer", "Environmental Engineer", "Urban Planner"]
            }
        }
    },
    "healthcare_ops": {
        "id": "healthcare_ops",
        "name": "Healthcare & Hospital Operations",
        "description": "Clinical care, administration, and hospital management",
        "icon": "hospital",
        "color": "#8B5CF6",
        "subsectors": {
            "clerical_support": {
                "name": "Clerical/Support",
                "roles": ["Patient Access Representative", "Medical Billing Specialist", "Records Manager", "Medical Secretary"]
            },
            "clinical": {
                "name": "Clinical",
                "roles": ["Certified Nursing Assistant (CNA)", "Registered Nurse (RN)", "Nurse Practitioner (NP)", "Physician", "Radiology Technician", "Respiratory Therapist"]
            },
            "administration": {
                "name": "Administration",
                "roles": ["Hospital COO", "Risk Manager", "Department Head", "Patient Experience Director"]
            }
        }
    },
    "technology": {
        "id": "technology",
        "name": "Technology & Digital Infrastructure",
        "description": "Health IT, Software Engineering, and Digital Solutions",
        "icon": "cpu",
        "color": "#F59E0B",
        "subsectors": {
            "health_it": {
                "name": "Health IT & Data",
                "roles": ["Bioinformatics Specialist", "Healthcare Cybersecurity Analyst", "EHR Administrator", "AI/ML Engineer (Healthcare)"]
            },
            "software": {
                "name": "Software Engineering",
                "roles": ["Full-Stack Developer", "Mobile App Developer", "Cloud Architect", "DevOps Engineer"]
            }
        }
    }
}

# ============== SENIORITY TIERS ==============

SENIORITY_TIERS = {
    "tier_1": {
        "level": 1,
        "name": "Support / Entry",
        "description": "Entry-level positions, support roles, internships",
        "examples": ["Clerk", "Technician", "Lab Assistant", "Intern"],
        "years_experience": "0-2"
    },
    "tier_2": {
        "level": 2,
        "name": "Professional",
        "description": "Individual contributor roles requiring specialized skills",
        "examples": ["Engineer", "Scientist", "RN", "Specialist"],
        "years_experience": "2-5"
    },
    "tier_3": {
        "level": 3,
        "name": "Management",
        "description": "Team leads, supervisors, project managers",
        "examples": ["Senior Engineer", "Project Manager", "Nursing Supervisor"],
        "years_experience": "5-10"
    },
    "tier_4": {
        "level": 4,
        "name": "Director",
        "description": "Department heads, principal-level roles",
        "examples": ["Head of R&D", "Principal Architect", "Clinical Director"],
        "years_experience": "10-15"
    },
    "tier_5": {
        "level": 5,
        "name": "Executive",
        "description": "C-Suite and VP-level leadership",
        "examples": ["CEO", "CTO", "Chief Medical Officer", "VP of Engineering"],
        "years_experience": "15+"
    }
}

# ============== CERTIFICATIONS ==============

CERTIFICATIONS = {
    "healthcare_admin": {
        "category": "Healthcare & Clinical Operations - Administrative",
        "certs": [
            {"code": "CHAA", "name": "Certified Healthcare Access Associate", "org": "NAHAM", "sector": ["healthcare_ops"]},
            {"code": "CPC", "name": "Certified Professional Coder", "org": "AAPC", "sector": ["healthcare_ops"]},
            {"code": "RHIA", "name": "Registered Health Information Administrator", "org": "AHIMA", "sector": ["healthcare_ops"]},
            {"code": "CRCR", "name": "Certified Revenue Cycle Representative", "org": "HFMA", "sector": ["healthcare_ops"]}
        ]
    },
    "healthcare_clinical": {
        "category": "Healthcare & Clinical Operations - Clinical",
        "certs": [
            {"code": "BLS", "name": "Basic Life Support", "org": "AHA", "sector": ["healthcare_ops", "life_sciences"]},
            {"code": "ACLS", "name": "Advanced Cardiac Life Support", "org": "AHA", "sector": ["healthcare_ops"]},
            {"code": "RN", "name": "Registered Nurse", "org": "State Board", "sector": ["healthcare_ops"]},
            {"code": "CCT", "name": "Certified Cardiographic Technician", "org": "CCI", "sector": ["healthcare_ops", "medical_devices"]},
            {"code": "RRT", "name": "Registered Respiratory Therapist", "org": "NBRC", "sector": ["healthcare_ops"]}
        ]
    },
    "quality_compliance": {
        "category": "Quality, Audit & Compliance",
        "certs": [
            {"code": "ASQ CQE", "name": "Certified Quality Engineer", "org": "ASQ", "sector": ["life_sciences", "medical_devices", "engineering"]},
            {"code": "ASQ CQI", "name": "Certified Quality Inspector", "org": "ASQ", "sector": ["life_sciences", "medical_devices", "engineering"]},
            {"code": "ASQ CQA", "name": "Certified Quality Auditor", "org": "ASQ", "sector": ["life_sciences", "medical_devices"]},
            {"code": "ASQ CSQP", "name": "Certified Supplier Quality Professional", "org": "ASQ", "sector": ["medical_devices", "engineering"]},
            {"code": "ISO 13485 LA", "name": "ISO 13485 Lead Auditor (Medical Devices)", "org": "Various", "sector": ["medical_devices"]},
            {"code": "AS9100 LA", "name": "AS9100 Lead Auditor (Aerospace)", "org": "Various", "sector": ["engineering"]},
            {"code": "IATF 16949 LA", "name": "IATF 16949 Lead Auditor (Automotive)", "org": "Various", "sector": ["engineering"]},
            {"code": "CPIM", "name": "Certified in Production and Inventory Management", "org": "APICS", "sector": ["life_sciences", "medical_devices", "engineering"]}
        ]
    },
    "medtech_pharma": {
        "category": "MedTech, Pharma & Biomedical",
        "certs": [
            {"code": "RAC", "name": "Regulatory Affairs Certification", "org": "RAPS", "sector": ["life_sciences", "medical_devices"]},
            {"code": "CCRP", "name": "Certified Clinical Research Professional", "org": "SOCRA", "sector": ["life_sciences"]},
            {"code": "GMP", "name": "Good Manufacturing Practice Certified", "org": "Various", "sector": ["life_sciences", "medical_devices"]},
            {"code": "GCP", "name": "Good Clinical Practice Certified", "org": "Various", "sector": ["life_sciences"]},
            {"code": "CCRC", "name": "Certified Clinical Research Coordinator", "org": "ACRP", "sector": ["life_sciences"]},
            {"code": "CCRA", "name": "Certified Clinical Research Associate", "org": "ACRP", "sector": ["life_sciences"]}
        ]
    },
    "engineering_core": {
        "category": "Heavy Engineering",
        "certs": [
            {"code": "FE", "name": "Fundamentals of Engineering", "org": "NCEES", "sector": ["engineering", "medical_devices"]},
            {"code": "PE", "name": "Professional Engineer", "org": "NCEES", "sector": ["engineering", "medical_devices"]},
            {"code": "FAA A&P", "name": "FAA Airframe & Powerplant", "org": "FAA", "sector": ["engineering"]},
            {"code": "ISO 26262", "name": "Automotive Functional Safety", "org": "Various", "sector": ["engineering"]},
            {"code": "CEM", "name": "Certified Energy Manager", "org": "AEE", "sector": ["engineering"]},
            {"code": "NABCEP", "name": "Solar PV Installation Professional", "org": "NABCEP", "sector": ["engineering"]},
            {"code": "CWI", "name": "Certified Welding Inspector", "org": "AWS", "sector": ["engineering", "medical_devices"]}
        ]
    },
    "technology_digital": {
        "category": "Technology & Management",
        "certs": [
            {"code": "CISSP", "name": "Certified Information Systems Security Professional", "org": "ISC2", "sector": ["technology", "healthcare_ops"]},
            {"code": "AWS-SAA", "name": "AWS Solutions Architect Associate", "org": "AWS", "sector": ["technology"]},
            {"code": "AWS-SAP", "name": "AWS Solutions Architect Professional", "org": "AWS", "sector": ["technology"]},
            {"code": "PMP", "name": "Project Management Professional", "org": "PMI", "sector": ["technology", "engineering", "life_sciences", "medical_devices", "healthcare_ops"]},
            {"code": "LSSBB", "name": "Lean Six Sigma Black Belt", "org": "Various", "sector": ["technology", "engineering", "life_sciences", "medical_devices", "healthcare_ops"]},
            {"code": "LSSGB", "name": "Lean Six Sigma Green Belt", "org": "Various", "sector": ["technology", "engineering", "life_sciences", "medical_devices", "healthcare_ops"]},
            {"code": "ASQ CMQ/OE", "name": "Certified Manager of Quality/Organizational Excellence", "org": "ASQ", "sector": ["technology", "engineering", "life_sciences", "medical_devices"]}
        ]
    }
}

# ============== SKILLS ==============

SKILLS = {
    "healthcare_admin": {
        "category": "Healthcare Administrative",
        "skills": [
            {"name": "Medical Terminology", "sector": ["healthcare_ops", "life_sciences"]},
            {"name": "Electronic Health Records (EHR)", "sector": ["healthcare_ops", "technology"]},
            {"name": "Revenue Cycle Management (RCM)", "sector": ["healthcare_ops"]},
            {"name": "ICD-10 Coding", "sector": ["healthcare_ops"]},
            {"name": "CPT Coding", "sector": ["healthcare_ops"]},
            {"name": "HIPAA Compliance", "sector": ["healthcare_ops", "technology"]}
        ]
    },
    "healthcare_clinical": {
        "category": "Healthcare Clinical",
        "skills": [
            {"name": "Patient Triage", "sector": ["healthcare_ops"]},
            {"name": "Diagnostic Imaging", "sector": ["healthcare_ops", "medical_devices"]},
            {"name": "Pharmacology", "sector": ["healthcare_ops", "life_sciences"]},
            {"name": "Vital Signs Monitoring", "sector": ["healthcare_ops"]},
            {"name": "IV Administration", "sector": ["healthcare_ops"]},
            {"name": "Wound Care", "sector": ["healthcare_ops"]}
        ]
    },
    "quality_engineering": {
        "category": "Quality Engineering",
        "skills": [
            {"name": "Statistical Process Control (SPC)", "sector": ["life_sciences", "medical_devices", "engineering"]},
            {"name": "Root Cause Analysis (RCA)", "sector": ["life_sciences", "medical_devices", "engineering"]},
            {"name": "CAPA (Corrective and Preventive Action)", "sector": ["life_sciences", "medical_devices", "engineering"]},
            {"name": "FMEA (Failure Mode and Effects Analysis)", "sector": ["medical_devices", "engineering"]},
            {"name": "Design of Experiments (DOE)", "sector": ["life_sciences", "medical_devices", "engineering"]},
            {"name": "Process Validation", "sector": ["life_sciences", "medical_devices"]}
        ]
    },
    "regulatory_science": {
        "category": "Regulatory & Science",
        "skills": [
            {"name": "Clinical Trial Design", "sector": ["life_sciences"]},
            {"name": "Good Manufacturing Practice (GMP)", "sector": ["life_sciences", "medical_devices"]},
            {"name": "Toxicology", "sector": ["life_sciences"]},
            {"name": "Pharmacovigilance", "sector": ["life_sciences"]},
            {"name": "FDA 510(k) Submissions", "sector": ["medical_devices"]},
            {"name": "EU MDR Compliance", "sector": ["medical_devices"]},
            {"name": "ICH Guidelines", "sector": ["life_sciences"]}
        ]
    },
    "biomedical": {
        "category": "Biomedical Engineering",
        "skills": [
            {"name": "Biomechanics", "sector": ["medical_devices"]},
            {"name": "Biosignal Processing", "sector": ["medical_devices", "technology"]},
            {"name": "Human Factors Engineering", "sector": ["medical_devices"]},
            {"name": "Medical Device Design", "sector": ["medical_devices"]},
            {"name": "Biocompatibility Testing", "sector": ["medical_devices", "life_sciences"]},
            {"name": "Sterilization Validation", "sector": ["medical_devices"]}
        ]
    },
    "engineering_technical": {
        "category": "Engineering Technical",
        "skills": [
            {"name": "CAD/CAM Design", "sector": ["engineering", "medical_devices"]},
            {"name": "BIM (Building Information Modeling)", "sector": ["engineering"]},
            {"name": "Finite Element Analysis (FEA)", "sector": ["engineering", "medical_devices"]},
            {"name": "Embedded Systems Development", "sector": ["engineering", "medical_devices", "technology"]},
            {"name": "Power Grid Modeling", "sector": ["engineering"]},
            {"name": "CFD (Computational Fluid Dynamics)", "sector": ["engineering"]}
        ]
    },
    "sustainability": {
        "category": "Sustainability & Energy",
        "skills": [
            {"name": "Solar PV System Design", "sector": ["engineering"]},
            {"name": "Wind Turbine Engineering", "sector": ["engineering"]},
            {"name": "Hydrogen Fuel Cells", "sector": ["engineering"]},
            {"name": "Nuclear Safety", "sector": ["engineering"]},
            {"name": "Environmental Impact Assessment", "sector": ["engineering"]}
        ]
    },
    "technology_digital": {
        "category": "Technology & Digital",
        "skills": [
            {"name": "Bioinformatics", "sector": ["technology", "life_sciences"]},
            {"name": "Healthcare Cybersecurity", "sector": ["technology", "healthcare_ops"]},
            {"name": "AI/Machine Learning", "sector": ["technology", "medical_devices", "life_sciences"]},
            {"name": "Data Privacy (HIPAA/GDPR)", "sector": ["technology", "healthcare_ops"]},
            {"name": "Cloud Architecture (AWS/Azure/GCP)", "sector": ["technology"]},
            {"name": "DevOps/CI-CD", "sector": ["technology"]}
        ]
    },
    "leadership": {
        "category": "Leadership & Management",
        "skills": [
            {"name": "Agile Methodology", "sector": ["technology", "engineering"]},
            {"name": "Lean Six Sigma", "sector": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"]},
            {"name": "Strategic Planning", "sector": ["life_sciences", "medical_devices", "engineering", "healthcare_ops", "technology"]},
            {"name": "Change Management", "sector": ["life_sciences", "medical_devices", "engineering", "healthcare_ops", "technology"]},
            {"name": "Budget Management", "sector": ["life_sciences", "medical_devices", "engineering", "healthcare_ops", "technology"]}
        ]
    }
}

# ============== CAREER PIVOT PATHWAYS ==============

CAREER_PIVOTS = [
    {
        "from_sector": "engineering",
        "from_role": "Aerospace Systems Engineer",
        "to_sector": "medical_devices",
        "to_role": "Medical Robotics Engineer",
        "transferable_skills": ["Embedded Systems", "Control Systems", "FEA", "Quality Systems"],
        "bridge_certifications": ["ISO 13485 LA", "RAC"],
        "difficulty": "medium",
        "salary_change": "+10-20%"
    },
    {
        "from_sector": "engineering",
        "from_role": "Chemical Engineer (Energy)",
        "to_sector": "life_sciences",
        "to_role": "Pharmaceutical Manufacturing Engineer",
        "transferable_skills": ["Process Engineering", "Quality Control", "GMP", "Validation"],
        "bridge_certifications": ["GMP", "ASQ CQE"],
        "difficulty": "low",
        "salary_change": "+5-15%"
    },
    {
        "from_sector": "engineering",
        "from_role": "Automotive Data Analyst",
        "to_sector": "technology",
        "to_role": "Health Informatics Analyst",
        "transferable_skills": ["Data Analysis", "Statistical Modeling", "Python/R", "Visualization"],
        "bridge_certifications": ["HIPAA Training", "Healthcare Analytics Cert"],
        "difficulty": "low",
        "salary_change": "+10-25%"
    },
    {
        "from_sector": "engineering",
        "from_role": "Avionics Engineer",
        "to_sector": "medical_devices",
        "to_role": "Embedded Systems Developer (Wearables)",
        "transferable_skills": ["Firmware Development", "Signal Processing", "RF Engineering", "Safety-Critical Systems"],
        "bridge_certifications": ["ISO 13485 LA", "IEC 62304"],
        "difficulty": "medium",
        "salary_change": "+5-15%"
    },
    {
        "from_sector": "technology",
        "from_role": "Software Engineer",
        "to_sector": "medical_devices",
        "to_role": "Medical Software Developer",
        "transferable_skills": ["Software Development", "Testing", "Agile", "Documentation"],
        "bridge_certifications": ["IEC 62304", "FDA Software Validation"],
        "difficulty": "low",
        "salary_change": "+10-20%"
    },
    {
        "from_sector": "healthcare_ops",
        "from_role": "Clinical Nurse",
        "to_sector": "life_sciences",
        "to_role": "Clinical Research Coordinator",
        "transferable_skills": ["Patient Care", "Medical Terminology", "Protocol Adherence", "Documentation"],
        "bridge_certifications": ["CCRC", "GCP"],
        "difficulty": "low",
        "salary_change": "+15-30%"
    },
    {
        "from_sector": "healthcare_ops",
        "from_role": "Medical Coder",
        "to_sector": "technology",
        "to_role": "Healthcare Data Analyst",
        "transferable_skills": ["Medical Terminology", "ICD/CPT Codes", "Data Entry", "Attention to Detail"],
        "bridge_certifications": ["Healthcare Analytics", "SQL/Python"],
        "difficulty": "medium",
        "salary_change": "+20-40%"
    },
    {
        "from_sector": "engineering",
        "from_role": "Nuclear Engineer",
        "to_sector": "medical_devices",
        "to_role": "Radiation Therapy Equipment Engineer",
        "transferable_skills": ["Radiation Physics", "Safety Systems", "Regulatory Compliance", "Quality Assurance"],
        "bridge_certifications": ["ISO 13485 LA", "FDA QSR"],
        "difficulty": "medium",
        "salary_change": "+5-15%"
    },
    {
        "from_sector": "life_sciences",
        "from_role": "Lab Technician",
        "to_sector": "medical_devices",
        "to_role": "Quality Control Technician",
        "transferable_skills": ["Lab Techniques", "Documentation", "SOP Adherence", "Equipment Calibration"],
        "bridge_certifications": ["ASQ CQI", "ISO 13485"],
        "difficulty": "low",
        "salary_change": "+10-20%"
    },
    {
        "from_sector": "technology",
        "from_role": "DevOps Engineer",
        "to_sector": "life_sciences",
        "to_role": "Bioinformatics Engineer",
        "transferable_skills": ["Cloud Infrastructure", "Automation", "Python", "Data Pipelines"],
        "bridge_certifications": ["Bioinformatics Cert", "GxP for IT"],
        "difficulty": "medium",
        "salary_change": "+10-20%"
    }
]

# ============== SPECIALIZED JOB BOARDS ==============

JOB_BOARDS = {
    "life_sciences": [
        {"name": "BioSpace", "url": "https://www.biospace.com", "focus": "Biotech & Pharma"},
        {"name": "Science Careers", "url": "https://jobs.sciencecareers.org", "focus": "Scientific Research"},
        {"name": "Nature Careers", "url": "https://www.nature.com/naturecareers", "focus": "Academic & Research"},
        {"name": "ClinicalCrossing", "url": "https://www.clinicalcrossing.com", "focus": "Clinical Research"}
    ],
    "medical_devices": [
        {"name": "MedReps", "url": "https://www.medreps.com", "focus": "Medical Device Sales"},
        {"name": "DeviceTalent", "url": "https://www.devicetalent.com", "focus": "Medical Device Engineering"},
        {"name": "MedDevice Online Jobs", "url": "https://www.mdojobs.com", "focus": "Medical Device Industry"}
    ],
    "healthcare_ops": [
        {"name": "Health eCareers", "url": "https://www.healthecareers.com", "focus": "Healthcare Professionals"},
        {"name": "Nurse.com", "url": "https://www.nurse.com/jobs", "focus": "Nursing"},
        {"name": "PracticeLink", "url": "https://www.practicelink.com", "focus": "Physician Recruitment"}
    ],
    "engineering": [
        {"name": "Engineering.com Jobs", "url": "https://www.engineering.com/jobs", "focus": "All Engineering"},
        {"name": "AviationJobSearch", "url": "https://www.aviationjobsearch.com", "focus": "Aerospace"},
        {"name": "Rigzone", "url": "https://www.rigzone.com/jobs", "focus": "Energy/Oil & Gas"}
    ],
    "technology": [
        {"name": "HealthTech Jobs", "url": "https://www.healthtechjobs.com", "focus": "Health IT"},
        {"name": "Dice", "url": "https://www.dice.com", "focus": "Technology"},
        {"name": "Built In", "url": "https://builtin.com/jobs", "focus": "Tech Startups"}
    ]
}

# ============== HELPER FUNCTIONS ==============

def get_all_roles():
    """Get flattened list of all roles across all sectors"""
    roles = []
    for sector_id, sector in SECTORS.items():
        for subsector_id, subsector in sector["subsectors"].items():
            for role in subsector["roles"]:
                roles.append({
                    "role": role,
                    "sector_id": sector_id,
                    "sector_name": sector["name"],
                    "subsector_id": subsector_id,
                    "subsector_name": subsector["name"]
                })
    return roles

def get_all_certifications():
    """Get flattened list of all certifications"""
    certs = []
    for category_id, category in CERTIFICATIONS.items():
        for cert in category["certs"]:
            certs.append({
                **cert,
                "category_id": category_id,
                "category_name": category["category"]
            })
    return certs

def get_all_skills():
    """Get flattened list of all skills"""
    all_skills = []
    for category_id, category in SKILLS.items():
        for skill in category["skills"]:
            all_skills.append({
                **skill,
                "category_id": category_id,
                "category_name": category["category"]
            })
    return all_skills

def get_certifications_for_sector(sector_id):
    """Get certifications relevant to a specific sector"""
    relevant_certs = []
    for category in CERTIFICATIONS.values():
        for cert in category["certs"]:
            if sector_id in cert["sector"]:
                relevant_certs.append(cert)
    return relevant_certs

def get_skills_for_sector(sector_id):
    """Get skills relevant to a specific sector"""
    relevant_skills = []
    for category in SKILLS.values():
        for skill in category["skills"]:
            if sector_id in skill["sector"]:
                relevant_skills.append(skill)
    return relevant_skills

def get_career_pivots_from_sector(sector_id):
    """Get career pivot opportunities from a specific sector"""
    return [p for p in CAREER_PIVOTS if p["from_sector"] == sector_id]

def get_career_pivots_to_sector(sector_id):
    """Get career pivot opportunities to a specific sector"""
    return [p for p in CAREER_PIVOTS if p["to_sector"] == sector_id]

def match_role_to_sector(role_title):
    """Try to match a role title to a sector"""
    role_lower = role_title.lower()
    
    # Keywords mapping
    sector_keywords = {
        "life_sciences": ["pharma", "biotech", "clinical", "drug", "research scientist", "lab", "formulation", "pharmacologist"],
        "medical_devices": ["medical device", "biomedical", "fda", "510k", "implant", "surgical", "diagnostic"],
        "engineering": ["aerospace", "automotive", "energy", "civil", "structural", "mechanical", "electrical"],
        "healthcare_ops": ["nurse", "physician", "hospital", "patient", "clinical care", "medical billing"],
        "technology": ["software", "developer", "engineer", "data", "cloud", "devops", "cybersecurity"]
    }
    
    for sector_id, keywords in sector_keywords.items():
        for keyword in keywords:
            if keyword in role_lower:
                return sector_id
    
    return None

def estimate_seniority_tier(title):
    """Estimate seniority tier from job title"""
    title_lower = title.lower()
    
    if any(x in title_lower for x in ["ceo", "cto", "cfo", "cmo", "cso", "chief", "vp", "vice president", "president"]):
        return "tier_5"
    elif any(x in title_lower for x in ["director", "head of", "principal", "fellow"]):
        return "tier_4"
    elif any(x in title_lower for x in ["manager", "lead", "senior", "supervisor", "sr."]):
        return "tier_3"
    elif any(x in title_lower for x in ["engineer", "scientist", "analyst", "specialist", "developer", "nurse", "rn"]):
        return "tier_2"
    else:
        return "tier_1"
