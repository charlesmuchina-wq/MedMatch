"""
AI-Powered Career Pivot Matching Service
Uses the taxonomy to suggest cross-industry career pivots based on transferable skills.
"""
from typing import Dict, List, Optional, Tuple
import logging
from services.taxonomy import SECTORS, SKILLS, CROSS_POLLINATION

logger = logging.getLogger(__name__)

# Skill transferability matrix - which skills transfer between sectors
SKILL_TRANSFER_WEIGHTS = {
    # Technical skills that transfer well
    "quality_management": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"],
    "regulatory_compliance": ["life_sciences", "medical_devices", "engineering"],
    "data_analysis": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"],
    "project_management": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"],
    "process_improvement": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"],
    "risk_management": ["life_sciences", "medical_devices", "engineering"],
    "validation": ["life_sciences", "medical_devices", "engineering"],
    "documentation": ["life_sciences", "medical_devices", "engineering", "healthcare_ops"],
    "capa": ["life_sciences", "medical_devices", "engineering"],
    "gmp": ["life_sciences", "medical_devices"],
    
    # Engineering skills
    "cad": ["medical_devices", "engineering"],
    "embedded_systems": ["medical_devices", "engineering"],
    "systems_engineering": ["medical_devices", "engineering"],
    "simulation": ["medical_devices", "engineering"],
    "robotics": ["medical_devices", "engineering"],
    
    # Life sciences skills
    "clinical_trials": ["life_sciences", "medical_devices"],
    "biostatistics": ["life_sciences", "medical_devices"],
    "pharmacology": ["life_sciences"],
    "cell_culture": ["life_sciences", "medical_devices"],
}

# Role mapping for cross-industry pivots
ROLE_PIVOT_MAP = {
    # Aerospace to Medical Devices
    "Avionics Engineer": [
        {"target": "Embedded Systems Developer", "sector": "medical_devices", "match": 85, "reason": "Embedded systems expertise directly applicable"},
        {"target": "R&D Engineer", "sector": "medical_devices", "match": 75, "reason": "Design and testing methodologies transfer well"},
    ],
    "Propulsion Engineer": [
        {"target": "Biomedical Engineer", "sector": "medical_devices", "match": 65, "reason": "Fluid dynamics applicable to drug delivery systems"},
    ],
    "Flight Test Engineer": [
        {"target": "Field Clinical Engineer", "sector": "medical_devices", "match": 80, "reason": "Testing protocols and field operations expertise"},
        {"target": "Validation Engineer", "sector": "life_sciences", "match": 75, "reason": "V&V experience directly applicable"},
    ],
    "Satellite Systems Engineer": [
        {"target": "Systems Engineer", "sector": "medical_devices", "match": 80, "reason": "Complex systems design skills transfer directly"},
    ],
    
    # Automotive to Medical Devices
    "EV Battery Engineer": [
        {"target": "R&D Engineer", "sector": "medical_devices", "match": 70, "reason": "Battery expertise relevant for implantables"},
    ],
    "Autonomous Systems Engineer": [
        {"target": "R&D Engineer", "sector": "medical_devices", "match": 85, "reason": "AI/ML and sensors directly applicable to surgical robotics"},
    ],
    
    # Life Sciences to Medical Devices
    "Quality Control (QC) Analyst": [
        {"target": "Design Assurance Engineer", "sector": "medical_devices", "match": 80, "reason": "QC methodologies transfer to device quality"},
    ],
    "Validation Engineer": [
        {"target": "Design Assurance Engineer", "sector": "medical_devices", "match": 90, "reason": "Validation expertise directly applicable"},
        {"target": "CAPA Specialist", "sector": "medical_devices", "match": 85, "reason": "Root cause analysis skills transfer"},
    ],
    "Clinical Research Associate (CRA)": [
        {"target": "Field Clinical Engineer", "sector": "medical_devices", "match": 75, "reason": "Clinical trial management applicable to device trials"},
    ],
    
    # Medical Devices to Life Sciences
    "Biomedical Engineer": [
        {"target": "Formulation Scientist", "sector": "life_sciences", "match": 60, "reason": "Some overlap in drug delivery systems"},
        {"target": "Manufacturing Technician", "sector": "life_sciences", "match": 70, "reason": "Process engineering applicable"},
    ],
    "CAPA Specialist": [
        {"target": "Quality Control (QC) Analyst", "sector": "life_sciences", "match": 85, "reason": "CAPA expertise valued in pharma"},
        {"target": "Validation Engineer", "sector": "life_sciences", "match": 80, "reason": "Root cause analysis transfers"},
    ],
    
    # Healthcare Ops crossovers
    "Clinical Nurse Manager": [
        {"target": "Head of Clinical Operations", "sector": "life_sciences", "match": 70, "reason": "Clinical operations leadership"},
    ],
}

# Certification bridges - which certifications help with pivots
CERT_BRIDGES = {
    "ASQ_CQE": {"from": ["engineering"], "to": ["life_sciences", "medical_devices"], "boost": 15},
    "ASQ_CQA": {"from": ["engineering", "life_sciences"], "to": ["medical_devices"], "boost": 15},
    "ASQ_CSQP": {"from": ["engineering"], "to": ["life_sciences", "medical_devices"], "boost": 10},
    "PMI_PMP": {"from": ["engineering"], "to": ["life_sciences", "medical_devices", "healthcare_ops"], "boost": 10},
    "PMI_CAPM": {"from": ["any"], "to": ["any"], "boost": 5},
    "RAPS_RAC": {"from": ["life_sciences"], "to": ["medical_devices"], "boost": 20},
    "ISO_13485": {"from": ["engineering"], "to": ["medical_devices"], "boost": 15},
    "ISO_9001": {"from": ["any"], "to": ["any"], "boost": 5},
}


class CareerPivotMatcher:
    """
    AI-powered career pivot matching engine.
    Analyzes candidate skills, experience, and certifications to suggest
    cross-industry career transitions with match scores.
    """
    
    def __init__(self, db=None):
        self.db = db
    
    def analyze_candidate_for_pivots(
        self,
        current_role: str,
        current_sector: str,
        skills: List[str],
        certifications: List[str] = None,
        experience_years: int = 0,
        target_sectors: List[str] = None
    ) -> Dict:
        """
        Analyze a candidate's profile and generate pivot recommendations.
        
        Args:
            current_role: Current job title
            current_sector: Current industry sector
            skills: List of skills
            certifications: List of certification codes
            experience_years: Years of experience
            target_sectors: Optional list of target sectors to consider
            
        Returns:
            Dict with pivot recommendations and analysis
        """
        certifications = certifications or []
        target_sectors = target_sectors or list(SECTORS.keys())
        
        # Remove current sector from targets if present
        target_sectors = [s for s in target_sectors if s != current_sector]
        
        recommendations = []
        
        # 1. Check direct role pivots from mapping
        if current_role in ROLE_PIVOT_MAP:
            for pivot in ROLE_PIVOT_MAP[current_role]:
                if pivot["sector"] in target_sectors:
                    rec = self._create_recommendation(
                        pivot["target"],
                        pivot["sector"],
                        pivot["match"],
                        pivot["reason"],
                        skills,
                        certifications
                    )
                    recommendations.append(rec)
        
        # 2. Analyze transferable skills for sector pivots
        skill_matches = self._analyze_skill_transferability(skills, current_sector, target_sectors)
        for sector, match_data in skill_matches.items():
            if match_data["score"] >= 50:  # Only suggest if 50%+ skill match
                # Find matching roles in target sector
                matching_roles = self._find_matching_roles(skills, sector, match_data["matching_skills"])
                for role_match in matching_roles[:3]:  # Top 3 per sector
                    rec = self._create_recommendation(
                        role_match["role"],
                        sector,
                        role_match["score"],
                        f"Skills match: {', '.join(match_data['matching_skills'][:3])}",
                        skills,
                        certifications
                    )
                    # Avoid duplicates
                    if not any(r["target_role"] == rec["target_role"] and r["target_sector"] == rec["target_sector"] 
                              for r in recommendations):
                        recommendations.append(rec)
        
        # 3. Apply certification boosts
        for rec in recommendations:
            cert_boost = self._calculate_cert_boost(certifications, current_sector, rec["target_sector"])
            rec["match_score"] = min(100, rec["match_score"] + cert_boost)
            if cert_boost > 0:
                rec["cert_boost"] = cert_boost
                rec["helpful_certs"] = self._get_helpful_certs(current_sector, rec["target_sector"])
        
        # 4. Apply experience modifiers
        for rec in recommendations:
            if experience_years >= 5:
                rec["match_score"] = min(100, rec["match_score"] + 5)
                rec["experience_bonus"] = True
            elif experience_years < 2:
                rec["match_score"] = max(0, rec["match_score"] - 5)
        
        # Sort by match score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        
        # Generate summary
        summary = self._generate_pivot_summary(current_role, current_sector, recommendations, skills, certifications)
        
        return {
            "current_profile": {
                "role": current_role,
                "sector": current_sector,
                "skills_count": len(skills),
                "certifications_count": len(certifications),
                "experience_years": experience_years
            },
            "recommendations": recommendations[:10],  # Top 10
            "summary": summary,
            "skill_analysis": self._analyze_skill_gaps(skills, recommendations[:5])
        }
    
    def _create_recommendation(
        self, 
        target_role: str, 
        target_sector: str, 
        base_score: int,
        reason: str,
        skills: List[str],
        certifications: List[str]
    ) -> Dict:
        """Create a pivot recommendation with details"""
        sector_info = SECTORS.get(target_sector, {})
        
        return {
            "target_role": target_role,
            "target_sector": target_sector,
            "target_sector_name": sector_info.get("name", target_sector),
            "match_score": base_score,
            "reasoning": reason,
            "difficulty": self._assess_difficulty(base_score),
            "time_estimate": self._estimate_transition_time(base_score),
            "sector_color": sector_info.get("color", "#6B7280"),
            "sector_icon": sector_info.get("icon", "briefcase"),
        }
    
    def _analyze_skill_transferability(
        self, 
        skills: List[str], 
        current_sector: str,
        target_sectors: List[str]
    ) -> Dict[str, Dict]:
        """Analyze how well skills transfer to target sectors"""
        results = {}
        skills_lower = [s.lower().replace(" ", "_") for s in skills]
        
        for sector in target_sectors:
            matching = []
            for skill in skills_lower:
                if skill in SKILL_TRANSFER_WEIGHTS:
                    if sector in SKILL_TRANSFER_WEIGHTS[skill]:
                        matching.append(skill.replace("_", " ").title())
            
            if matching:
                results[sector] = {
                    "score": min(100, len(matching) * 15),
                    "matching_skills": matching,
                    "total_transferable": len(matching)
                }
        
        return results
    
    def _find_matching_roles(
        self, 
        skills: List[str], 
        target_sector: str,
        transferable_skills: List[str]
    ) -> List[Dict]:
        """Find roles in target sector that match candidate skills"""
        sector_data = SECTORS.get(target_sector, {})
        subsectors = sector_data.get("subsectors", {})
        
        role_matches = []
        for subsector_id, subsector in subsectors.items():
            for role in subsector.get("roles", []):
                # Simple scoring based on role name and skill overlap
                score = 50  # Base score
                
                # Boost for skills mentioned in role name
                for skill in transferable_skills:
                    if skill.lower() in role.lower():
                        score += 20
                
                # Boost for quality/regulatory roles if candidate has those skills
                if any(s in role.lower() for s in ["quality", "validation", "regulatory", "compliance"]):
                    if any(s in [sk.lower() for sk in transferable_skills] 
                           for s in ["quality", "validation", "regulatory", "compliance"]):
                        score += 15
                
                role_matches.append({
                    "role": role,
                    "subsector": subsector.get("name", subsector_id),
                    "score": min(100, score)
                })
        
        # Sort by score and return top matches
        role_matches.sort(key=lambda x: x["score"], reverse=True)
        return role_matches
    
    def _calculate_cert_boost(
        self, 
        certifications: List[str], 
        from_sector: str, 
        to_sector: str
    ) -> int:
        """Calculate certification boost for the pivot"""
        total_boost = 0
        
        for cert in certifications:
            cert_upper = cert.upper().replace("-", "_").replace(" ", "_")
            
            for cert_code, bridge in CERT_BRIDGES.items():
                if cert_code in cert_upper or cert_upper in cert_code:
                    from_match = "any" in bridge["from"] or from_sector in bridge["from"]
                    to_match = "any" in bridge["to"] or to_sector in bridge["to"]
                    
                    if from_match and to_match:
                        total_boost += bridge["boost"]
        
        return min(30, total_boost)  # Cap at 30 points
    
    def _get_helpful_certs(self, from_sector: str, to_sector: str) -> List[Dict]:
        """Get certifications that would help with this pivot"""
        helpful = []
        
        for cert_code, bridge in CERT_BRIDGES.items():
            from_match = "any" in bridge["from"] or from_sector in bridge["from"]
            to_match = "any" in bridge["to"] or to_sector in bridge["to"]
            
            if from_match and to_match:
                helpful.append({
                    "code": cert_code,
                    "boost": bridge["boost"],
                    "description": self._get_cert_description(cert_code)
                })
        
        return helpful[:3]  # Top 3
    
    def _get_cert_description(self, cert_code: str) -> str:
        """Get certification description"""
        descriptions = {
            "ASQ_CQE": "ASQ Certified Quality Engineer",
            "ASQ_CQA": "ASQ Certified Quality Auditor",
            "ASQ_CSQP": "ASQ Certified Supplier Quality Professional",
            "PMI_PMP": "Project Management Professional",
            "PMI_CAPM": "Certified Associate in Project Management",
            "RAPS_RAC": "Regulatory Affairs Certification",
            "ISO_13485": "ISO 13485 Medical Devices QMS Lead Auditor",
            "ISO_9001": "ISO 9001 Quality Management Systems",
        }
        return descriptions.get(cert_code, cert_code)
    
    def _assess_difficulty(self, match_score: int) -> str:
        """Assess transition difficulty based on match score"""
        if match_score >= 80:
            return "Easy"
        elif match_score >= 65:
            return "Moderate"
        elif match_score >= 50:
            return "Challenging"
        else:
            return "Difficult"
    
    def _estimate_transition_time(self, match_score: int) -> str:
        """Estimate time needed for transition"""
        if match_score >= 80:
            return "1-3 months"
        elif match_score >= 65:
            return "3-6 months"
        elif match_score >= 50:
            return "6-12 months"
        else:
            return "12+ months"
    
    def _analyze_skill_gaps(
        self, 
        current_skills: List[str], 
        top_recommendations: List[Dict]
    ) -> Dict:
        """Analyze skill gaps for top recommendations"""
        gaps = {}
        current_skills_lower = {s.lower() for s in current_skills}
        
        # Common skills needed per sector
        sector_skills = {
            "life_sciences": ["GMP", "Clinical Trials", "Pharmacovigilance", "Biostatistics", "cGMP Documentation"],
            "medical_devices": ["FDA 510(k)", "EU MDR", "Design Controls", "Risk Analysis", "ISO 13485"],
            "engineering": ["CAD/CAM", "FEA/CFD", "Systems Engineering", "DFMEA", "Six Sigma"],
            "healthcare_ops": ["EHR Systems", "HIPAA Compliance", "Patient Safety", "Healthcare Analytics"],
        }
        
        for rec in top_recommendations:
            sector = rec["target_sector"]
            needed = sector_skills.get(sector, [])
            missing = [s for s in needed if s.lower() not in current_skills_lower]
            
            if missing:
                gaps[rec["target_role"]] = {
                    "sector": sector,
                    "skills_to_acquire": missing[:5],
                    "current_relevant": len([s for s in needed if s.lower() in current_skills_lower])
                }
        
        return gaps
    
    def _generate_pivot_summary(
        self,
        current_role: str,
        current_sector: str,
        recommendations: List[Dict],
        skills: List[str],
        certifications: List[str]
    ) -> Dict:
        """Generate a summary of pivot opportunities"""
        if not recommendations:
            return {
                "headline": "Limited pivot options found",
                "insight": "Consider building more transferable skills",
                "top_opportunity": None
            }
        
        top = recommendations[0]
        easy_pivots = [r for r in recommendations if r["difficulty"] == "Easy"]
        
        return {
            "headline": f"Found {len(recommendations)} career pivot opportunities",
            "insight": f"Your strongest path is to {top['target_role']} in {top['target_sector_name']} ({top['match_score']}% match)",
            "top_opportunity": top["target_role"],
            "easy_pivots_count": len(easy_pivots),
            "sectors_available": list(set(r["target_sector"] for r in recommendations)),
            "strongest_transferable_skills": skills[:5] if skills else [],
            "certification_advantage": len(certifications) > 0
        }


def get_career_pivot_matcher(db=None):
    """Factory function to get CareerPivotMatcher instance"""
    return CareerPivotMatcher(db)
