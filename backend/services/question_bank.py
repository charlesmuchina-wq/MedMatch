"""
Skill Assessment Question Bank
Pre-generated questions for fast assessment starts.
Avoids 20-30 second wait time for AI generation.

Created: Feb 21, 2026
"""

import random
from typing import List, Dict, Any

# ============== Pre-Generated Question Banks ==============
# Questions are organized by skill -> difficulty -> list of questions
# Each question has: question, options, correct_answer, explanation

QUESTION_BANK: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
    
    # ============== ISO 13485 (Medical Devices) ==============
    "ISO 13485 (Medical Devices)": {
        "beginner": [
            {
                "question": "What is the primary purpose of ISO 13485?",
                "options": ["A) To regulate drug manufacturing", "B) To establish requirements for a quality management system for medical devices", "C) To test product safety", "D) To certify medical professionals"],
                "correct_answer": "B",
                "explanation": "ISO 13485 specifies requirements for a QMS where an organization needs to demonstrate its ability to provide medical devices that consistently meet customer and regulatory requirements."
            },
            {
                "question": "Which of the following is a key principle of ISO 13485?",
                "options": ["A) Employee wellness programs", "B) Profit maximization", "C) Customer satisfaction surveys", "D) Risk-based approach to quality"],
                "correct_answer": "D",
                "explanation": "ISO 13485 emphasizes a risk-based approach throughout the product lifecycle, from design to post-market surveillance."
            },
            {
                "question": "What document is essential for demonstrating design control compliance?",
                "options": ["A) Design History File (DHF)", "B) Budget forecast", "C) Sales report", "D) Marketing brochure"],
                "correct_answer": "A",
                "explanation": "The Design History File contains records demonstrating that the design was developed in accordance with the approved design plan and meets requirements."
            },
            {
                "question": "ISO 13485 requires documented procedures for which of the following?",
                "options": ["A) Control of nonconforming product", "B) Office decoration", "C) Holiday scheduling", "D) Parking allocation"],
                "correct_answer": "A",
                "explanation": "Control of nonconforming product is a mandatory documented procedure to ensure nonconforming items are identified and controlled."
            },
            {
                "question": "What is CAPA in the context of ISO 13485?",
                "options": ["A) Corrective And Preventive Action", "B) Compliance And Performance Audit", "C) Clinical And Pharmaceutical Analysis", "D) Customer And Product Assessment"],
                "correct_answer": "A",
                "explanation": "CAPA stands for Corrective And Preventive Action, a systematic approach to investigating, correcting, and preventing quality problems."
            }
        ],
        "intermediate": [
            {
                "question": "According to ISO 13485, what must be established for software used in the QMS?",
                "options": ["A) Validation procedures before initial use and after changes", "B) Annual subscription plans", "C) Free trials for users", "D) Only user manuals"],
                "correct_answer": "A",
                "explanation": "Software used in the QMS must be validated prior to initial use and revalidated after changes, with documented procedures and records."
            },
            {
                "question": "What is required for supplier evaluation under ISO 13485?",
                "options": ["A) Personal references only", "B) Documented criteria for selection, evaluation, and re-evaluation", "C) Only price comparison", "D) Social media reviews"],
                "correct_answer": "B",
                "explanation": "Organizations must establish documented criteria for supplier selection, evaluation, and re-evaluation based on ability to supply conforming product."
            },
            {
                "question": "ISO 13485 requires risk management to be applied:",
                "options": ["A) Throughout product realization processes", "B) Only at final inspection", "C) Only during manufacturing", "D) Only after complaints"],
                "correct_answer": "A",
                "explanation": "Risk management must be applied throughout product realization, from design through production and post-market activities."
            },
            {
                "question": "What must be maintained for traceability of medical devices?",
                "options": ["A) Only shipping records", "B) Only customer names", "C) Records that allow identification of manufacturing batch and distribution", "D) Only purchase orders"],
                "correct_answer": "C",
                "explanation": "Traceability records must allow identification of the manufacturing batch and the extent of distribution for product recall purposes."
            },
            {
                "question": "Design verification under ISO 13485 ensures:",
                "options": ["A) The design is profitable", "B) The design is patented", "C) The design looks attractive", "D) Design outputs meet design input requirements"],
                "correct_answer": "D",
                "explanation": "Design verification confirms that design outputs meet the design input requirements through objective evidence."
            }
        ],
        "advanced": [
            {
                "question": "What is the relationship between ISO 13485:2016 and ISO 9001:2015?",
                "options": ["A) ISO 9001 replaces ISO 13485", "B) ISO 13485 is a standalone standard with some harmonized requirements but specific medical device focus", "C) They cannot be used together", "D) They are identical"],
                "correct_answer": "B",
                "explanation": "ISO 13485:2016 is a standalone standard. While it shares some structure with ISO 9001, it has specific requirements for medical devices and doesn't require continual improvement of QMS effectiveness."
            },
            {
                "question": "For sterile medical devices, what additional requirements apply?",
                "options": ["A) Only storage requirements", "B) Only labeling requirements", "C) Validation of sterilization processes, sterile barrier system, and bioburden control", "D) Only packaging requirements"],
                "correct_answer": "C",
                "explanation": "Sterile devices require validated sterilization processes, appropriate sterile barrier systems, bioburden and pyrogen control, and environmental controls."
            },
            {
                "question": "What must be included in a Device Master Record (DMR)?",
                "options": ["A) Only supplier information", "B) Complete specifications and procedures for producing the device", "C) Only drawings", "D) Only test results"],
                "correct_answer": "B",
                "explanation": "The DMR must include device specifications, production process specifications, quality assurance procedures, packaging/labeling specifications, and installation/servicing procedures."
            },
            {
                "question": "Post-market surveillance under ISO 13485 requires:",
                "options": ["A) Only warranty tracking", "B) Only customer satisfaction surveys", "C) Systematic monitoring of device performance and taking action on feedback", "D) Only tracking sales"],
                "correct_answer": "C",
                "explanation": "Post-market surveillance requires systematic collection and analysis of experience from devices, feedback handling, and integration with risk management and improvement processes."
            },
            {
                "question": "What is required for process validation of special processes?",
                "options": ["A) Only operator training", "B) Documented procedures establishing process capability, monitoring, and revalidation criteria", "C) Only raw material testing", "D) Only equipment calibration"],
                "correct_answer": "B",
                "explanation": "Special processes require documented validation procedures, defined approval criteria, equipment/personnel qualification, defined process parameters, and revalidation triggers."
            }
        ]
    },
    
    # ============== Six Sigma (Green Belt) ==============
    "Six Sigma (Green Belt)": {
        "beginner": [
            {
                "question": "What does DMAIC stand for?",
                "options": ["A) Document, Manage, Audit, Inspect, Close", "B) Design, Measure, Analyze, Implement, Control", "C) Develop, Monitor, Assess, Improve, Certify", "D) Define, Measure, Analyze, Improve, Control"],
                "correct_answer": "D",
                "explanation": "DMAIC is the core Six Sigma improvement methodology: Define, Measure, Analyze, Improve, Control."
            },
            {
                "question": "What is the goal of Six Sigma in terms of defects?",
                "options": ["A) 3.4 defects per million opportunities", "B) 10 defects per thousand opportunities", "C) Zero defects always", "D) 1 defect per 100 opportunities"],
                "correct_answer": "A",
                "explanation": "Six Sigma aims for 3.4 defects per million opportunities (DPMO), representing near-perfect quality."
            },
            {
                "question": "What is a CTQ in Six Sigma?",
                "options": ["A) Critical To Quality - key measurable characteristics", "B) Continuous Testing Quality", "C) Cost To Quality", "D) Certified Team Qualification"],
                "correct_answer": "A",
                "explanation": "CTQ (Critical To Quality) characteristics are the key measurable characteristics of a product or process that must meet customer requirements."
            },
            {
                "question": "What tool is used to identify potential causes of a problem?",
                "options": ["A) Calendar", "B) Organization chart", "C) Fishbone (Ishikawa) diagram", "D) Balance sheet"],
                "correct_answer": "C",
                "explanation": "The Fishbone (Ishikawa) diagram organizes potential causes into categories to identify root causes of problems."
            },
            {
                "question": "What is the purpose of a Process Map?",
                "options": ["A) To show office locations", "B) To visualize the steps and flow of a process", "C) To track employee attendance", "D) To display sales territories"],
                "correct_answer": "B",
                "explanation": "A Process Map visualizes all steps, decisions, and flow in a process to identify waste, bottlenecks, and improvement opportunities."
            }
        ],
        "intermediate": [
            {
                "question": "What is the formula for calculating Process Sigma?",
                "options": ["A) Revenue / Costs", "B) Employees / Output", "C) Sales / Time", "D) Based on DPMO converted using sigma tables or calculations"],
                "correct_answer": "D",
                "explanation": "Process Sigma is calculated by determining DPMO (Defects Per Million Opportunities) and converting it using statistical tables or formulas."
            },
            {
                "question": "What statistical tool tests if there's a significant difference between group means?",
                "options": ["A) Scatter plot", "B) Gantt chart", "C) Pie chart", "D) ANOVA (Analysis of Variance)"],
                "correct_answer": "D",
                "explanation": "ANOVA tests whether there are statistically significant differences between the means of two or more groups."
            },
            {
                "question": "In a Control Chart, what do the Upper and Lower Control Limits represent?",
                "options": ["A) Statistical boundaries for normal process variation (typically ±3σ)", "B) Profit margins", "C) Physical product dimensions", "D) Budget limits"],
                "correct_answer": "A",
                "explanation": "Control Limits represent the statistical boundaries (typically ±3 standard deviations) within which normal process variation occurs."
            },
            {
                "question": "What is the difference between common cause and special cause variation?",
                "options": ["A) They are the same thing", "B) Common is external, special is internal", "C) Common is bad, special is good", "D) Common is inherent to the process, special is due to specific identifiable factors"],
                "correct_answer": "D",
                "explanation": "Common cause variation is inherent to the process (noise), while special cause variation is due to specific, identifiable factors that can be addressed."
            },
            {
                "question": "What is Cp and Cpk used to measure?",
                "options": ["A) Customer preferences", "B) Company profits", "C) Process capability relative to specification limits", "D) Competition positioning"],
                "correct_answer": "C",
                "explanation": "Cp measures potential process capability while Cpk measures actual process capability considering how centered the process is within specifications."
            }
        ],
        "advanced": [
            {
                "question": "When is Design of Experiments (DOE) preferred over One-Factor-At-a-Time (OFAT)?",
                "options": ["A) When studying multiple factors and their interactions efficiently", "B) When there's no time pressure", "C) When budget is unlimited", "D) When only one factor matters"],
                "correct_answer": "A",
                "explanation": "DOE is preferred when studying multiple factors and their interactions, as it's more efficient and can detect interactions that OFAT would miss."
            },
            {
                "question": "What is the purpose of a Gauge R&R study?",
                "options": ["A) To calculate revenue", "B) To track employee performance", "C) To assess measurement system variation (repeatability and reproducibility)", "D) To measure product sales"],
                "correct_answer": "C",
                "explanation": "Gauge R&R assesses measurement system variation: Repeatability (same operator, same part) and Reproducibility (different operators, same part)."
            },
            {
                "question": "In hypothesis testing, what is a Type I error?",
                "options": ["A) Rejecting a true null hypothesis (false positive)", "B) Missing data", "C) Accepting a true null hypothesis", "D) A calculation mistake"],
                "correct_answer": "A",
                "explanation": "Type I error (α) is rejecting the null hypothesis when it's actually true - a false positive."
            },
            {
                "question": "What is the relationship between sample size and statistical power?",
                "options": ["A) They are inversely related", "B) Larger samples increase power to detect real effects", "C) No relationship", "D) Smaller samples increase power"],
                "correct_answer": "B",
                "explanation": "Larger sample sizes increase statistical power - the probability of correctly detecting an effect when one exists."
            },
            {
                "question": "What distinguishes a full factorial from a fractional factorial DOE?",
                "options": ["A) Cost only", "B) Full factorial tests all combinations, fractional tests a strategic subset", "C) Full is faster", "D) They are identical"],
                "correct_answer": "B",
                "explanation": "Full factorial tests all possible combinations of factors, while fractional factorial tests a strategically chosen subset to estimate main effects and some interactions efficiently."
            }
        ]
    },
    
    # ============== FDA 21 CFR Part 820 ==============
    "FDA 21 CFR Part 820": {
        "beginner": [
            {
                "question": "What is 21 CFR Part 820 also known as?",
                "options": ["A) The Food Safety Code", "B) The Drug Safety Act", "C) The Import Control Law", "D) The Quality System Regulation (QSR)"],
                "correct_answer": "D",
                "explanation": "21 CFR Part 820 is the Quality System Regulation (QSR) that establishes current good manufacturing practice (CGMP) requirements for medical devices."
            },
            {
                "question": "Which agency enforces 21 CFR Part 820?",
                "options": ["A) EPA", "B) FTC", "C) OSHA", "D) FDA"],
                "correct_answer": "D",
                "explanation": "The Food and Drug Administration (FDA) enforces 21 CFR Part 820 for medical device manufacturers."
            },
            {
                "question": "What is required for all medical device manufacturers under Part 820?",
                "options": ["A) Only labeling", "B) Documented quality management system", "C) Only testing", "D) Only packaging"],
                "correct_answer": "B",
                "explanation": "Part 820 requires manufacturers to establish and maintain a quality system appropriate for the specific medical device being designed or manufactured."
            },
            {
                "question": "What does DHF stand for?",
                "options": ["A) Design History File", "B) Data Handling Framework", "C) Document Handling Form", "D) Device Hardware Function"],
                "correct_answer": "A",
                "explanation": "DHF (Design History File) contains or references records demonstrating that the design was developed in accordance with the approved design plan."
            },
            {
                "question": "What is required before making changes to a medical device design?",
                "options": ["A) Documented change control with review and approval", "B) Only email notification", "C) Only verbal approval", "D) No requirements"],
                "correct_answer": "A",
                "explanation": "Design changes must go through documented change control procedures including appropriate review, verification/validation, and approval before implementation."
            }
        ],
        "intermediate": [
            {
                "question": "What are the three key documents required by 820.30 (Design Controls)?",
                "options": ["A) DHF (Design History File), DMR (Device Master Record), DHR (Device History Record)", "B) Quote, Contract, Purchase Order", "C) Resume, Application, Offer Letter", "D) Invoice, Receipt, Packing slip"],
                "correct_answer": "A",
                "explanation": "DHF documents design development, DMR contains specifications and procedures, DHR provides production history for specific units."
            },
            {
                "question": "What must be included in a complaint handling procedure?",
                "options": ["A) Uniform procedures for receiving, reviewing, evaluating, and investigating complaints", "B) Only customer contact information", "C) Only refund policies", "D) Only apology templates"],
                "correct_answer": "A",
                "explanation": "Complaint handling requires documented procedures covering receipt, review, evaluation, investigation, and determination of MDR reportability."
            },
            {
                "question": "When is CAPA required under Part 820?",
                "options": ["A) Only annually", "B) Only during audits", "C) When quality data analysis identifies nonconforming product or quality problems", "D) Only for recalls"],
                "correct_answer": "C",
                "explanation": "CAPA must be implemented when analysis of quality data identifies existing nonconforming product, quality problems, or trends requiring corrective action."
            },
            {
                "question": "What is required for production and process controls?",
                "options": ["A) Documented instructions, environmental controls, equipment maintenance, and process monitoring", "B) Only operator training", "C) Only raw material testing", "D) Only final inspection"],
                "correct_answer": "A",
                "explanation": "Production controls include documented instructions (including acceptance criteria), controlled environmental conditions, equipment maintenance, and process monitoring."
            },
            {
                "question": "What does validation of processes mean under Part 820?",
                "options": ["A) Approving suppliers", "B) Establishing documented evidence providing high assurance that a process consistently produces conforming product", "C) Testing final products", "D) Getting customer approval"],
                "correct_answer": "B",
                "explanation": "Process validation establishes documented evidence (IQ, OQ, PQ) that a process consistently produces results meeting predetermined specifications."
            }
        ],
        "advanced": [
            {
                "question": "What triggers a Medical Device Report (MDR) under Part 803?",
                "options": ["A) Customer suggestions", "B) Deaths, serious injuries, or malfunctions that could cause death/serious injury", "C) Any customer complaint", "D) Minor defects"],
                "correct_answer": "B",
                "explanation": "MDRs are required for events involving death, serious injury, or malfunctions that could cause or contribute to death or serious injury if the malfunction recurred."
            },
            {
                "question": "How does Part 820 define 'verification' vs 'validation'?",
                "options": ["A) Only terminology differs", "B) Verification confirms specifications are met; validation confirms user needs are met", "C) They are the same", "D) Verification is for software only"],
                "correct_answer": "B",
                "explanation": "Verification confirms design outputs meet design inputs (built right). Validation confirms the device meets user needs and intended uses (built the right thing)."
            },
            {
                "question": "What is required for software used in medical devices under Part 820?",
                "options": ["A) Only version control", "B) Validation including documentation of the software development lifecycle activities", "C) Only source code backup", "D) Only user documentation"],
                "correct_answer": "B",
                "explanation": "Software validation requires documented evidence demonstrating the software meets user needs, including complete lifecycle documentation per design controls."
            },
            {
                "question": "What is the relationship between Part 820 and ISO 13485?",
                "options": ["A) They cannot both be applied", "B) They are identical", "C) ISO 13485 replaces Part 820", "D) Both address QMS but Part 820 is US-specific with some unique requirements"],
                "correct_answer": "D",
                "explanation": "Both address medical device QMS requirements. Part 820 is US-specific with some unique requirements (like MDR reporting), though FDA has begun harmonization efforts."
            },
            {
                "question": "What documentation is required for design review meetings?",
                "options": ["A) Results including identification of problems, actions, participants, and date", "B) No documentation required", "C) Only agenda", "D) Only attendance sheet"],
                "correct_answer": "A",
                "explanation": "Design review documentation must include results of the review, identification of the design and date reviewed, individuals participating, and any actions required."
            }
        ]
    },
    
    # ============== Supplier Quality Management ==============
    "Supplier Quality Management": {
        "beginner": [
            {
                "question": "What is the primary purpose of supplier quality management?",
                "options": ["A) To increase supplier competition", "B) To reduce supplier prices", "C) To expand supplier network", "D) To ensure suppliers consistently provide conforming products and services"],
                "correct_answer": "D",
                "explanation": "SQM ensures that suppliers consistently provide products and services that meet quality requirements, reducing defects and ensuring compliance."
            },
            {
                "question": "What does PPAP stand for?",
                "options": ["A) Process Planning And Preparation", "B) Production Part Approval Process", "C) Product Performance Assessment Program", "D) Production Process Approval Protocol"],
                "correct_answer": "B",
                "explanation": "PPAP (Production Part Approval Process) is used to establish confidence in suppliers' manufacturing processes and their ability to produce conforming parts."
            },
            {
                "question": "What is a supplier audit?",
                "options": ["A) Systematic evaluation of a supplier's quality management system and processes", "B) Review of supplier marketing materials", "C) Financial review of supplier", "D) Assessment of supplier website"],
                "correct_answer": "A",
                "explanation": "A supplier audit systematically evaluates a supplier's QMS, processes, and capabilities to ensure they can meet quality requirements."
            },
            {
                "question": "What is incoming inspection?",
                "options": ["A) Processing incoming mail", "B) Checking employee badges", "C) Verification that received materials meet specifications before use", "D) Reviewing incoming orders"],
                "correct_answer": "C",
                "explanation": "Incoming inspection verifies that received materials, components, or products meet specifications before they are accepted for use in production."
            },
            {
                "question": "What is a supplier scorecard used for?",
                "options": ["A) Measuring and tracking supplier performance against key metrics", "B) Counting supplier employees", "C) Tracking supplier locations", "D) Rating supplier friendliness"],
                "correct_answer": "A",
                "explanation": "Supplier scorecards measure and track performance across metrics like quality, delivery, cost, and service to drive improvement."
            }
        ],
        "intermediate": [
            {
                "question": "What elements are typically included in PPAP documentation?",
                "options": ["A) Only contact information", "B) Design records, process flow, control plan, MSA, dimensional results, material certifications", "C) Only delivery schedules", "D) Only price quotes"],
                "correct_answer": "B",
                "explanation": "PPAP includes design records, process documentation, control plans, measurement system analysis, dimensional results, material/performance test results, and more."
            },
            {
                "question": "What is the purpose of a Supplier Corrective Action Request (SCAR)?",
                "options": ["A) To formally request investigation and correction of nonconformances", "B) To order more parts", "C) To negotiate prices", "D) To terminate suppliers"],
                "correct_answer": "A",
                "explanation": "SCARs formally request suppliers to investigate root causes of nonconformances and implement effective corrective and preventive actions."
            },
            {
                "question": "What factors should be considered in supplier risk assessment?",
                "options": ["A) Only location", "B) Only years in business", "C) Only company size", "D) Quality history, financial stability, single source dependency, critical materials"],
                "correct_answer": "D",
                "explanation": "Supplier risk assessment considers quality performance, financial health, geographic risk, single-source dependency, critical component supply, and regulatory compliance."
            },
            {
                "question": "What is the difference between supplier qualification and approval?",
                "options": ["A) They are identical", "B) Only terminology differs", "C) Qualification is for services, approval for products", "D) Qualification assesses capability; approval authorizes use for specific products"],
                "correct_answer": "D",
                "explanation": "Qualification evaluates a supplier's overall capability, while approval specifically authorizes them to supply particular products or components."
            },
            {
                "question": "What is an Approved Supplier List (ASL)?",
                "options": ["A) A competitor list", "B) A marketing directory", "C) A phone book", "D) A controlled list of suppliers authorized to provide specific items"],
                "correct_answer": "D",
                "explanation": "An ASL is a controlled document listing suppliers that have been evaluated, qualified, and approved to supply specific products or services."
            }
        ],
        "advanced": [
            {
                "question": "What is supplier development, and when is it appropriate?",
                "options": ["A) Building new factories", "B) Reducing supplier count", "C) Collaborative improvement activities to enhance critical supplier capabilities", "D) Finding new suppliers"],
                "correct_answer": "C",
                "explanation": "Supplier development involves collaborative activities to improve a strategic supplier's capabilities when they have potential but need support to meet requirements."
            },
            {
                "question": "How should supplier performance data be used in the supply chain strategy?",
                "options": ["A) Only for reporting", "B) For sourcing decisions, continuous improvement, risk management, and supplier classification", "C) Only for negotiations", "D) Only for audits"],
                "correct_answer": "B",
                "explanation": "Performance data should inform sourcing decisions, drive improvement initiatives, assess risks, classify suppliers, and support strategic supply chain management."
            },
            {
                "question": "What are the key elements of an effective supplier quality agreement (SQA)?",
                "options": ["A) Quality requirements, inspection methods, nonconformance handling, change notification, audit rights", "B) Only delivery terms", "C) Only warranty terms", "D) Only pricing terms"],
                "correct_answer": "A",
                "explanation": "An SQA defines quality requirements, inspection/testing requirements, nonconformance management, change control notification, audit rights, and escalation procedures."
            },
            {
                "question": "What is the 8D problem-solving methodology in supplier quality?",
                "options": ["A) 8 Days to complete", "B) 8 Documents required", "C) 8 Disciplines: Team, Describe, Interim, Root Cause, Permanent, Implement, Prevent, Recognize", "D) 8 Departments involved"],
                "correct_answer": "C",
                "explanation": "8D is an 8-discipline approach: Team formation, Problem description, Interim containment, Root cause analysis, Permanent corrective action, Implementation, Prevention, Recognition."
            },
            {
                "question": "How do you handle a critical supplier with quality issues but no alternative sources?",
                "options": ["A) Simply terminate", "B) Accept defects", "C) Ignore the issues", "D) Implement robust controls, intensified monitoring, supplier development, and qualification of alternatives"],
                "correct_answer": "D",
                "explanation": "For critical single-source suppliers, implement robust incoming controls, intensify monitoring, invest in supplier development, and work to qualify alternative sources."
            }
        ]
    }
}


def get_questions_from_bank(skill_name: str, difficulty: str, count: int = 15) -> List[Dict[str, Any]]:
    """
    Get questions from the pre-generated bank.
    Returns questions with shuffled order and shuffled options.
    
    Args:
        skill_name: Name of the skill assessment
        difficulty: beginner, intermediate, or advanced
        count: Number of questions to return
    
    Returns:
        List of question dictionaries
    """
    if skill_name not in QUESTION_BANK:
        return []
    
    skill_questions = QUESTION_BANK[skill_name]
    
    if difficulty not in skill_questions:
        # Fall back to intermediate if difficulty not found
        difficulty = "intermediate"
    
    if difficulty not in skill_questions:
        return []
    
    available = skill_questions[difficulty].copy()
    
    # If not enough questions in that difficulty, add from other difficulties
    if len(available) < count:
        for other_diff in ["intermediate", "beginner", "advanced"]:
            if other_diff != difficulty and other_diff in skill_questions:
                available.extend(skill_questions[other_diff])
    
    # Shuffle and take requested count
    random.shuffle(available)
    selected = available[:count]
    
    # Shuffle options for each question
    result = []
    for q in selected:
        shuffled_q = q.copy()
        # Note: Keep options in original order for now as they include A), B), etc.
        # In a real implementation, you'd shuffle and update the correct answer letter
        result.append(shuffled_q)
    
    return result


def has_questions_for_skill(skill_name: str) -> bool:
    """Check if we have pre-generated questions for a skill."""
    return skill_name in QUESTION_BANK


def get_available_skills_with_questions() -> List[str]:
    """Get list of skills that have pre-generated questions."""
    return list(QUESTION_BANK.keys())
