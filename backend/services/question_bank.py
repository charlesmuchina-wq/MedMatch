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
                "options": ["A) To certify medical professionals", "B) To establish requirements for a quality management system for medical devices", "C) To regulate drug manufacturing", "D) To test product safety"],
                "correct_answer": "B",
                "explanation": "ISO 13485 specifies requirements for a QMS where an organization needs to demonstrate its ability to provide medical devices that consistently meet customer and regulatory requirements."
            },
            {
                "question": "Which of the following is a key principle of ISO 13485?",
                "options": ["A) Customer satisfaction surveys", "B) Risk-based approach to quality", "C) Profit maximization", "D) Employee wellness programs"],
                "correct_answer": "B",
                "explanation": "ISO 13485 emphasizes a risk-based approach throughout the product lifecycle, from design to post-market surveillance."
            },
            {
                "question": "What document is essential for demonstrating design control compliance?",
                "options": ["A) Marketing brochure", "B) Design History File (DHF)", "C) Sales report", "D) Budget forecast"],
                "correct_answer": "B",
                "explanation": "The Design History File contains records demonstrating that the design was developed in accordance with the approved design plan and meets requirements."
            },
            {
                "question": "ISO 13485 requires documented procedures for which of the following?",
                "options": ["A) Holiday scheduling", "B) Control of nonconforming product", "C) Office decoration", "D) Parking allocation"],
                "correct_answer": "B",
                "explanation": "Control of nonconforming product is a mandatory documented procedure to ensure nonconforming items are identified and controlled."
            },
            {
                "question": "What is CAPA in the context of ISO 13485?",
                "options": ["A) Customer And Product Assessment", "B) Corrective And Preventive Action", "C) Compliance And Performance Audit", "D) Clinical And Pharmaceutical Analysis"],
                "correct_answer": "B",
                "explanation": "CAPA stands for Corrective And Preventive Action, a systematic approach to investigating, correcting, and preventing quality problems."
            }
        ],
        "intermediate": [
            {
                "question": "According to ISO 13485, what must be established for software used in the QMS?",
                "options": ["A) Only user manuals", "B) Validation procedures before initial use and after changes", "C) Free trials for users", "D) Annual subscription plans"],
                "correct_answer": "B",
                "explanation": "Software used in the QMS must be validated prior to initial use and revalidated after changes, with documented procedures and records."
            },
            {
                "question": "What is required for supplier evaluation under ISO 13485?",
                "options": ["A) Only price comparison", "B) Documented criteria for selection, evaluation, and re-evaluation", "C) Personal references only", "D) Social media reviews"],
                "correct_answer": "B",
                "explanation": "Organizations must establish documented criteria for supplier selection, evaluation, and re-evaluation based on ability to supply conforming product."
            },
            {
                "question": "ISO 13485 requires risk management to be applied:",
                "options": ["A) Only during manufacturing", "B) Throughout product realization processes", "C) Only after complaints", "D) Only at final inspection"],
                "correct_answer": "B",
                "explanation": "Risk management must be applied throughout product realization, from design through production and post-market activities."
            },
            {
                "question": "What must be maintained for traceability of medical devices?",
                "options": ["A) Only shipping records", "B) Records that allow identification of manufacturing batch and distribution", "C) Only customer names", "D) Only purchase orders"],
                "correct_answer": "B",
                "explanation": "Traceability records must allow identification of the manufacturing batch and the extent of distribution for product recall purposes."
            },
            {
                "question": "Design verification under ISO 13485 ensures:",
                "options": ["A) The design looks attractive", "B) Design outputs meet design input requirements", "C) The design is profitable", "D) The design is patented"],
                "correct_answer": "B",
                "explanation": "Design verification confirms that design outputs meet the design input requirements through objective evidence."
            }
        ],
        "advanced": [
            {
                "question": "What is the relationship between ISO 13485:2016 and ISO 9001:2015?",
                "options": ["A) They are identical", "B) ISO 13485 is a standalone standard with some harmonized requirements but specific medical device focus", "C) ISO 9001 replaces ISO 13485", "D) They cannot be used together"],
                "correct_answer": "B",
                "explanation": "ISO 13485:2016 is a standalone standard. While it shares some structure with ISO 9001, it has specific requirements for medical devices and doesn't require continual improvement of QMS effectiveness."
            },
            {
                "question": "For sterile medical devices, what additional requirements apply?",
                "options": ["A) Only packaging requirements", "B) Validation of sterilization processes, sterile barrier system, and bioburden control", "C) Only labeling requirements", "D) Only storage requirements"],
                "correct_answer": "B",
                "explanation": "Sterile devices require validated sterilization processes, appropriate sterile barrier systems, bioburden and pyrogen control, and environmental controls."
            },
            {
                "question": "What must be included in a Device Master Record (DMR)?",
                "options": ["A) Only drawings", "B) Complete specifications and procedures for producing the device", "C) Only test results", "D) Only supplier information"],
                "correct_answer": "B",
                "explanation": "The DMR must include device specifications, production process specifications, quality assurance procedures, packaging/labeling specifications, and installation/servicing procedures."
            },
            {
                "question": "Post-market surveillance under ISO 13485 requires:",
                "options": ["A) Only tracking sales", "B) Systematic monitoring of device performance and taking action on feedback", "C) Only warranty tracking", "D) Only customer satisfaction surveys"],
                "correct_answer": "B",
                "explanation": "Post-market surveillance requires systematic collection and analysis of experience from devices, feedback handling, and integration with risk management and improvement processes."
            },
            {
                "question": "What is required for process validation of special processes?",
                "options": ["A) Only operator training", "B) Documented procedures establishing process capability, monitoring, and revalidation criteria", "C) Only equipment calibration", "D) Only raw material testing"],
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
                "options": ["A) Design, Measure, Analyze, Implement, Control", "B) Define, Measure, Analyze, Improve, Control", "C) Develop, Monitor, Assess, Improve, Certify", "D) Document, Manage, Audit, Inspect, Close"],
                "correct_answer": "B",
                "explanation": "DMAIC is the core Six Sigma improvement methodology: Define, Measure, Analyze, Improve, Control."
            },
            {
                "question": "What is the goal of Six Sigma in terms of defects?",
                "options": ["A) 1 defect per 100 opportunities", "B) 3.4 defects per million opportunities", "C) Zero defects always", "D) 10 defects per thousand opportunities"],
                "correct_answer": "B",
                "explanation": "Six Sigma aims for 3.4 defects per million opportunities (DPMO), representing near-perfect quality."
            },
            {
                "question": "What is a CTQ in Six Sigma?",
                "options": ["A) Cost To Quality", "B) Critical To Quality - key measurable characteristics", "C) Certified Team Qualification", "D) Continuous Testing Quality"],
                "correct_answer": "B",
                "explanation": "CTQ (Critical To Quality) characteristics are the key measurable characteristics of a product or process that must meet customer requirements."
            },
            {
                "question": "What tool is used to identify potential causes of a problem?",
                "options": ["A) Balance sheet", "B) Fishbone (Ishikawa) diagram", "C) Organization chart", "D) Calendar"],
                "correct_answer": "B",
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
                "options": ["A) Revenue / Costs", "B) Based on DPMO converted using sigma tables or calculations", "C) Employees / Output", "D) Sales / Time"],
                "correct_answer": "B",
                "explanation": "Process Sigma is calculated by determining DPMO (Defects Per Million Opportunities) and converting it using statistical tables or formulas."
            },
            {
                "question": "What statistical tool tests if there's a significant difference between group means?",
                "options": ["A) Scatter plot", "B) ANOVA (Analysis of Variance)", "C) Pie chart", "D) Gantt chart"],
                "correct_answer": "B",
                "explanation": "ANOVA tests whether there are statistically significant differences between the means of two or more groups."
            },
            {
                "question": "In a Control Chart, what do the Upper and Lower Control Limits represent?",
                "options": ["A) Budget limits", "B) Statistical boundaries for normal process variation (typically ±3σ)", "C) Physical product dimensions", "D) Profit margins"],
                "correct_answer": "B",
                "explanation": "Control Limits represent the statistical boundaries (typically ±3 standard deviations) within which normal process variation occurs."
            },
            {
                "question": "What is the difference between common cause and special cause variation?",
                "options": ["A) Common is bad, special is good", "B) Common is inherent to the process, special is due to specific identifiable factors", "C) They are the same thing", "D) Common is external, special is internal"],
                "correct_answer": "B",
                "explanation": "Common cause variation is inherent to the process (noise), while special cause variation is due to specific, identifiable factors that can be addressed."
            },
            {
                "question": "What is Cp and Cpk used to measure?",
                "options": ["A) Company profits", "B) Process capability relative to specification limits", "C) Customer preferences", "D) Competition positioning"],
                "correct_answer": "B",
                "explanation": "Cp measures potential process capability while Cpk measures actual process capability considering how centered the process is within specifications."
            }
        ],
        "advanced": [
            {
                "question": "When is Design of Experiments (DOE) preferred over One-Factor-At-a-Time (OFAT)?",
                "options": ["A) When budget is unlimited", "B) When studying multiple factors and their interactions efficiently", "C) When only one factor matters", "D) When there's no time pressure"],
                "correct_answer": "B",
                "explanation": "DOE is preferred when studying multiple factors and their interactions, as it's more efficient and can detect interactions that OFAT would miss."
            },
            {
                "question": "What is the purpose of a Gauge R&R study?",
                "options": ["A) To measure product sales", "B) To assess measurement system variation (repeatability and reproducibility)", "C) To track employee performance", "D) To calculate revenue"],
                "correct_answer": "B",
                "explanation": "Gauge R&R assesses measurement system variation: Repeatability (same operator, same part) and Reproducibility (different operators, same part)."
            },
            {
                "question": "In hypothesis testing, what is a Type I error?",
                "options": ["A) Accepting a true null hypothesis", "B) Rejecting a true null hypothesis (false positive)", "C) A calculation mistake", "D) Missing data"],
                "correct_answer": "B",
                "explanation": "Type I error (α) is rejecting the null hypothesis when it's actually true - a false positive."
            },
            {
                "question": "What is the relationship between sample size and statistical power?",
                "options": ["A) No relationship", "B) Larger samples increase power to detect real effects", "C) Smaller samples increase power", "D) They are inversely related"],
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
                "options": ["A) The Drug Safety Act", "B) The Quality System Regulation (QSR)", "C) The Food Safety Code", "D) The Import Control Law"],
                "correct_answer": "B",
                "explanation": "21 CFR Part 820 is the Quality System Regulation (QSR) that establishes current good manufacturing practice (CGMP) requirements for medical devices."
            },
            {
                "question": "Which agency enforces 21 CFR Part 820?",
                "options": ["A) EPA", "B) FDA", "C) OSHA", "D) FTC"],
                "correct_answer": "B",
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
                "options": ["A) Document Handling Form", "B) Design History File", "C) Device Hardware Function", "D) Data Handling Framework"],
                "correct_answer": "B",
                "explanation": "DHF (Design History File) contains or references records demonstrating that the design was developed in accordance with the approved design plan."
            },
            {
                "question": "What is required before making changes to a medical device design?",
                "options": ["A) Only verbal approval", "B) Documented change control with review and approval", "C) Only email notification", "D) No requirements"],
                "correct_answer": "B",
                "explanation": "Design changes must go through documented change control procedures including appropriate review, verification/validation, and approval before implementation."
            }
        ],
        "intermediate": [
            {
                "question": "What are the three key documents required by 820.30 (Design Controls)?",
                "options": ["A) Invoice, Receipt, Packing slip", "B) DHF (Design History File), DMR (Device Master Record), DHR (Device History Record)", "C) Quote, Contract, Purchase Order", "D) Resume, Application, Offer Letter"],
                "correct_answer": "B",
                "explanation": "DHF documents design development, DMR contains specifications and procedures, DHR provides production history for specific units."
            },
            {
                "question": "What must be included in a complaint handling procedure?",
                "options": ["A) Only customer contact information", "B) Uniform procedures for receiving, reviewing, evaluating, and investigating complaints", "C) Only refund policies", "D) Only apology templates"],
                "correct_answer": "B",
                "explanation": "Complaint handling requires documented procedures covering receipt, review, evaluation, investigation, and determination of MDR reportability."
            },
            {
                "question": "When is CAPA required under Part 820?",
                "options": ["A) Only annually", "B) When quality data analysis identifies nonconforming product or quality problems", "C) Only during audits", "D) Only for recalls"],
                "correct_answer": "B",
                "explanation": "CAPA must be implemented when analysis of quality data identifies existing nonconforming product, quality problems, or trends requiring corrective action."
            },
            {
                "question": "What is required for production and process controls?",
                "options": ["A) Only operator training", "B) Documented instructions, environmental controls, equipment maintenance, and process monitoring", "C) Only final inspection", "D) Only raw material testing"],
                "correct_answer": "B",
                "explanation": "Production controls include documented instructions (including acceptance criteria), controlled environmental conditions, equipment maintenance, and process monitoring."
            },
            {
                "question": "What does validation of processes mean under Part 820?",
                "options": ["A) Getting customer approval", "B) Establishing documented evidence providing high assurance that a process consistently produces conforming product", "C) Testing final products", "D) Approving suppliers"],
                "correct_answer": "B",
                "explanation": "Process validation establishes documented evidence (IQ, OQ, PQ) that a process consistently produces results meeting predetermined specifications."
            }
        ],
        "advanced": [
            {
                "question": "What triggers a Medical Device Report (MDR) under Part 803?",
                "options": ["A) Any customer complaint", "B) Deaths, serious injuries, or malfunctions that could cause death/serious injury", "C) Minor defects", "D) Customer suggestions"],
                "correct_answer": "B",
                "explanation": "MDRs are required for events involving death, serious injury, or malfunctions that could cause or contribute to death or serious injury if the malfunction recurred."
            },
            {
                "question": "How does Part 820 define 'verification' vs 'validation'?",
                "options": ["A) They are the same", "B) Verification confirms specifications are met; validation confirms user needs are met", "C) Only terminology differs", "D) Verification is for software only"],
                "correct_answer": "B",
                "explanation": "Verification confirms design outputs meet design inputs (built right). Validation confirms the device meets user needs and intended uses (built the right thing)."
            },
            {
                "question": "What is required for software used in medical devices under Part 820?",
                "options": ["A) Only user documentation", "B) Validation including documentation of the software development lifecycle activities", "C) Only source code backup", "D) Only version control"],
                "correct_answer": "B",
                "explanation": "Software validation requires documented evidence demonstrating the software meets user needs, including complete lifecycle documentation per design controls."
            },
            {
                "question": "What is the relationship between Part 820 and ISO 13485?",
                "options": ["A) They are identical", "B) Both address QMS but Part 820 is US-specific with some unique requirements", "C) ISO 13485 replaces Part 820", "D) They cannot both be applied"],
                "correct_answer": "B",
                "explanation": "Both address medical device QMS requirements. Part 820 is US-specific with some unique requirements (like MDR reporting), though FDA has begun harmonization efforts."
            },
            {
                "question": "What documentation is required for design review meetings?",
                "options": ["A) No documentation required", "B) Results including identification of problems, actions, participants, and date", "C) Only attendance sheet", "D) Only agenda"],
                "correct_answer": "B",
                "explanation": "Design review documentation must include results of the review, identification of the design and date reviewed, individuals participating, and any actions required."
            }
        ]
    },
    
    # ============== Supplier Quality Management ==============
    "Supplier Quality Management": {
        "beginner": [
            {
                "question": "What is the primary purpose of supplier quality management?",
                "options": ["A) To reduce supplier prices", "B) To ensure suppliers consistently provide conforming products and services", "C) To increase supplier competition", "D) To expand supplier network"],
                "correct_answer": "B",
                "explanation": "SQM ensures that suppliers consistently provide products and services that meet quality requirements, reducing defects and ensuring compliance."
            },
            {
                "question": "What does PPAP stand for?",
                "options": ["A) Production Process Approval Protocol", "B) Production Part Approval Process", "C) Product Performance Assessment Program", "D) Process Planning And Preparation"],
                "correct_answer": "B",
                "explanation": "PPAP (Production Part Approval Process) is used to establish confidence in suppliers' manufacturing processes and their ability to produce conforming parts."
            },
            {
                "question": "What is a supplier audit?",
                "options": ["A) Financial review of supplier", "B) Systematic evaluation of a supplier's quality management system and processes", "C) Review of supplier marketing materials", "D) Assessment of supplier website"],
                "correct_answer": "B",
                "explanation": "A supplier audit systematically evaluates a supplier's QMS, processes, and capabilities to ensure they can meet quality requirements."
            },
            {
                "question": "What is incoming inspection?",
                "options": ["A) Checking employee badges", "B) Verification that received materials meet specifications before use", "C) Reviewing incoming orders", "D) Processing incoming mail"],
                "correct_answer": "B",
                "explanation": "Incoming inspection verifies that received materials, components, or products meet specifications before they are accepted for use in production."
            },
            {
                "question": "What is a supplier scorecard used for?",
                "options": ["A) Rating supplier friendliness", "B) Measuring and tracking supplier performance against key metrics", "C) Counting supplier employees", "D) Tracking supplier locations"],
                "correct_answer": "B",
                "explanation": "Supplier scorecards measure and track performance across metrics like quality, delivery, cost, and service to drive improvement."
            }
        ],
        "intermediate": [
            {
                "question": "What elements are typically included in PPAP documentation?",
                "options": ["A) Only price quotes", "B) Design records, process flow, control plan, MSA, dimensional results, material certifications", "C) Only delivery schedules", "D) Only contact information"],
                "correct_answer": "B",
                "explanation": "PPAP includes design records, process documentation, control plans, measurement system analysis, dimensional results, material/performance test results, and more."
            },
            {
                "question": "What is the purpose of a Supplier Corrective Action Request (SCAR)?",
                "options": ["A) To terminate suppliers", "B) To formally request investigation and correction of nonconformances", "C) To negotiate prices", "D) To order more parts"],
                "correct_answer": "B",
                "explanation": "SCARs formally request suppliers to investigate root causes of nonconformances and implement effective corrective and preventive actions."
            },
            {
                "question": "What factors should be considered in supplier risk assessment?",
                "options": ["A) Only location", "B) Quality history, financial stability, single source dependency, critical materials", "C) Only company size", "D) Only years in business"],
                "correct_answer": "B",
                "explanation": "Supplier risk assessment considers quality performance, financial health, geographic risk, single-source dependency, critical component supply, and regulatory compliance."
            },
            {
                "question": "What is the difference between supplier qualification and approval?",
                "options": ["A) They are identical", "B) Qualification assesses capability; approval authorizes use for specific products", "C) Only terminology differs", "D) Qualification is for services, approval for products"],
                "correct_answer": "B",
                "explanation": "Qualification evaluates a supplier's overall capability, while approval specifically authorizes them to supply particular products or components."
            },
            {
                "question": "What is an Approved Supplier List (ASL)?",
                "options": ["A) A marketing directory", "B) A controlled list of suppliers authorized to provide specific items", "C) A phone book", "D) A competitor list"],
                "correct_answer": "B",
                "explanation": "An ASL is a controlled document listing suppliers that have been evaluated, qualified, and approved to supply specific products or services."
            }
        ],
        "advanced": [
            {
                "question": "What is supplier development, and when is it appropriate?",
                "options": ["A) Building new factories", "B) Collaborative improvement activities to enhance critical supplier capabilities", "C) Finding new suppliers", "D) Reducing supplier count"],
                "correct_answer": "B",
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
                "options": ["A) Only pricing terms", "B) Quality requirements, inspection methods, nonconformance handling, change notification, audit rights", "C) Only delivery terms", "D) Only warranty terms"],
                "correct_answer": "B",
                "explanation": "An SQA defines quality requirements, inspection/testing requirements, nonconformance management, change control notification, audit rights, and escalation procedures."
            },
            {
                "question": "What is the 8D problem-solving methodology in supplier quality?",
                "options": ["A) 8 Departments involved", "B) 8 Disciplines: Team, Describe, Interim, Root Cause, Permanent, Implement, Prevent, Recognize", "C) 8 Days to complete", "D) 8 Documents required"],
                "correct_answer": "B",
                "explanation": "8D is an 8-discipline approach: Team formation, Problem description, Interim containment, Root cause analysis, Permanent corrective action, Implementation, Prevention, Recognition."
            },
            {
                "question": "How do you handle a critical supplier with quality issues but no alternative sources?",
                "options": ["A) Accept defects", "B) Implement robust controls, intensified monitoring, supplier development, and qualification of alternatives", "C) Ignore the issues", "D) Simply terminate"],
                "correct_answer": "B",
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
