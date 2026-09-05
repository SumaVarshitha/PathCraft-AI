import os
import re
from typing import Dict, Any, List, Optional
from google.genai import types
from pydantic import BaseModel, Field
import config
from core.adk_agent import ADKAgent

class OptimizedBullet(BaseModel):
    original: str = Field(description="Original bullet point from resume")
    improved: str = Field(description="High-impact ATS power bullet rewritten using XYZ formula")
    rationale: str = Field(description="Explanation of why this rewrite scores higher with recruiters")

class ATSAuditResult(BaseModel):
    ats_score: int = Field(description="Overall ATS resume compatibility score between 0 and 100")
    formatting_score: int = Field(description="Structure, headings, and readability score out of 25")
    keyword_score: int = Field(description="Target role keyword optimization score out of 35")
    impact_score: int = Field(description="Action verbs and quantified metrics score out of 25")
    completeness_score: int = Field(description="Section completeness score out of 15")
    strengths: List[str] = Field(description="Key strengths identified in the resume")
    critical_fixes: List[str] = Field(description="Critical issues to fix before applying")
    missing_ats_keywords: List[str] = Field(description="High-priority keywords missing from resume")
    power_bullet_rewrites: List[OptimizedBullet] = Field(description="AI-rewritten bullet points with measurable impact")

class ATSAnalyzerADKAgent(ADKAgent):
    """
    Google ADK 2.0 ATS Resume Auditor & Bullet Point Optimizer Agent
    Analyzes resume structure, action verbs, quantified metrics, keyword density,
    and rewrites bullet points into high-impact ATS power bullets.
    """
    def __init__(self):
        instruction = """
        You are a veteran Silicon Valley Technical Recruiter and ATS Optimization Expert.
        Evaluate the candidate's resume against the target role requirements:
        1. Calculate realistic ATS Compatibility score out of 100 (broken into Formatting, Keyword, Impact, Completeness).
        2. Identify specific strengths and critical red flags.
        3. Identify high-priority missing ATS keywords.
        4. Select 2 to 4 bullet points from the resume and rewrite them into high-impact power bullets using Google's XYZ formula:
           'Accomplished [X] as measured by [Y], by doing [Z]' with strong action verbs and quantified results.
        """
        super().__init__(
            name="ATSAnalyzerADKAgent",
            instruction=instruction,
            model=config.MODEL_FLASH,
            output_schema=ATSAuditResult,
            temperature=0.2
        )

    def _offline_ats_audit(self, resume_text: str, target_role: str, missing_skills: List[str]) -> Dict[str, Any]:
        """Provides heuristic ATS audit when offline."""
        text_lower = resume_text.lower()
        
        # Check metrics / numbers
        has_metrics = len(re.findall(r'\b\d+[%kKmMbB]?\b', resume_text)) > 3
        has_projects = "project" in text_lower
        has_summary = "summary" in text_lower or "profile" in text_lower
        has_skills = "skill" in text_lower

        format_score = 22 if (has_summary and has_skills) else 14
        impact_score = 21 if has_metrics else 12
        keyword_score = 28 if len(missing_skills) < 4 else 18
        comp_score = 14 if has_projects else 9
        total_ats = format_score + impact_score + keyword_score + comp_score

        strengths = [
            "Clear technical skill headings and category breakdown.",
            "Includes dedicated section for featured projects." if has_projects else "Clean linear chronological structure."
        ]

        fixes = []
        if not has_metrics:
            fixes.append("Add quantified metrics (e.g. % performance increase, latency reduction, volume processed) to work bullets.")
        if missing_skills:
            fixes.append(f"Incorporate missing target role keywords: {', '.join(missing_skills[:4])}.")

        rewrites = [
            {
                "original": f"Worked on {target_role} pipelines and application scripts.",
                "improved": f"Architected high-throughput {target_role} infrastructure, processing 50M+ daily events and reducing query latency by 35%.",
                "rationale": "Applies Google XYZ formula with concrete scale and quantified latency reduction."
            },
            {
                "original": "Built backend services and managed database queries.",
                "improved": "Engineered containerized microservice APIs in Docker/Kubernetes, achieving 99.99% service availability.",
                "rationale": "Replaces passive verbs with strong action verbs and explicit reliability metrics."
            }
        ]

        return {
            "ats_score": total_ats,
            "formatting_score": format_score,
            "keyword_score": keyword_score,
            "impact_score": impact_score,
            "completeness_score": comp_score,
            "strengths": strengths,
            "critical_fixes": fixes,
            "missing_ats_keywords": missing_skills[:6] if missing_skills else ["System Architecture", "Performance Tuning"],
            "power_bullet_rewrites": rewrites
        }

    def audit(self, resume_text: str, target_role: str, missing_skills: List[str]) -> Dict[str, Any]:
        """Audits resume for ATS compatibility and generates power bullet rewrites."""
        if not self.client or not resume_text:
            return self._offline_ats_audit(resume_text or "", target_role, missing_skills)

        try:
            prompt = f"""
            Audit this candidate's resume for the target role: '{target_role}'.
            Missing technical skills identified for this role: {missing_skills}.
            
            Resume Text:
            {resume_text}
            
            Return the audit and power bullet point rewrites in the ATSAuditResult format.
            """
            return self.execute(prompt_input=prompt)
        except Exception as e:
            print(f"[ATS Analyzer Notice]: ({e}). Using heuristic ATS audit.", flush=True)
            return self._offline_ats_audit(resume_text, target_role, missing_skills)
