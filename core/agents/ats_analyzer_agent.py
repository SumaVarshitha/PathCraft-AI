import os
import re
from typing import Dict, Any, List, Optional
from google.genai import types
from pydantic import BaseModel, Field
import config
from core.adk_agent import ADKAgent

class OptimizedBullet(BaseModel):
    original: str = Field(description="Exact original bullet point copied from the candidate's resume")
    improved: str = Field(description="High-impact ATS power bullet rewritten using Google XYZ formula: Accomplished [X] as measured by [Y], by doing [Z]")
    rationale: str = Field(description="Explanation of why this rewrite scores higher with ATS and recruiters")

class ATSAuditResult(BaseModel):
    ats_score: int = Field(description="Overall ATS resume compatibility score 0–100")
    formatting_score: int = Field(description="Structure, headings, section order, readability — score out of 25")
    keyword_score: int = Field(description="Target role keyword coverage and density — score out of 35")
    impact_score: int = Field(description="Action verbs, quantified metrics, and measurable outcomes — score out of 25")
    completeness_score: int = Field(description="Section completeness: summary, experience, projects, education, skills — score out of 15")
    strengths: List[str] = Field(description="Specific strengths found in this resume (3–5 items)")
    critical_fixes: List[str] = Field(description="Specific critical issues to fix before applying (3–5 items)")
    missing_ats_keywords: List[str] = Field(description="High-priority keywords missing from the resume that ATS systems look for")
    power_bullet_rewrites: List[OptimizedBullet] = Field(description="2–4 real bullets from THIS resume rewritten with measurable impact")

class ATSAnalyzerADKAgent(ADKAgent):
    """
    Google ADK 2.0 ATS Resume Auditor & Bullet Point Optimizer Agent

    Scoring breakdown (total = 100):
      - Formatting & Structure  : 25 pts  (headings, order, readability, no tables/columns)
      - Keyword Coverage        : 35 pts  (target role keywords, density, placement)
      - Impact & Metrics        : 25 pts  (action verbs, quantified results, XYZ formula)
      - Section Completeness    : 15 pts  (summary, experience, projects, education, skills present)

    The offline fallback uses actual resume bullets — never fake placeholder text.
    """
    def __init__(self):
        instruction = """
        You are a veteran Silicon Valley Technical Recruiter and ATS Optimization Expert.
        Carefully read the ENTIRE candidate resume and target role. Then:

        1. Score the resume on 4 dimensions (total = 100):
           - formatting_score  : 0–25  (clear headings, reverse-chrono order, no tables/graphics that confuse parsers)
           - keyword_score     : 0–35  (target role keywords present, density, placement near top)
           - impact_score      : 0–25  (strong action verbs, quantified metrics like %, $, ms, volume)
           - completeness_score: 0–15  (summary/objective, work experience, projects, education, skills all present)
           - ats_score = sum of all four

        2. List 3–5 specific STRENGTHS found in THIS resume.
        3. List 3–5 CRITICAL FIXES that would meaningfully improve ATS ranking.
        4. List the most important missing ATS keywords for this target role.
        5. Pick 2–4 REAL bullet points from THIS resume (copy them exactly as 'original') and
           rewrite each into a high-impact power bullet using Google's XYZ formula:
           "Accomplished [X] as measured by [Y], by doing [Z]"
           with strong action verbs and quantified results.

        IMPORTANT: power_bullet_rewrites must use ACTUAL bullets from the resume, not invented examples.
        """
        super().__init__(
            name="ATSAnalyzerADKAgent",
            instruction=instruction,
            model=config.MODEL_FLASH,
            output_schema=ATSAuditResult,
            temperature=0.1
        )

    def _offline_ats_audit(self, resume_text: str, target_role: str, missing_skills: List[str]) -> Dict[str, Any]:
        """
        Heuristic ATS audit when Gemini API is unavailable.
        Uses actual resume content — never fake placeholder bullets.
        """
        text_lower = resume_text.lower()
        lines = [l.strip() for l in resume_text.split("\n") if l.strip()]

        # ── Formatting score (0–25)
        has_summary    = any(w in text_lower for w in ["summary", "profile", "objective"])
        has_skills_sec = any(w in text_lower for w in ["skills", "technologies", "tools"])
        has_education  = "education" in text_lower or "b.tech" in text_lower or "bachelor" in text_lower
        has_experience = any(w in text_lower for w in ["experience", "employment", "engineer", "developer"])
        section_count  = sum([has_summary, has_skills_sec, has_education, has_experience])
        format_score   = min(25, 5 + section_count * 4 + (3 if len(lines) > 20 else 0))

        # ── Keyword score (0–35)
        # Count how many missing skills are NOT in the resume (penalize for each gap)
        gaps_in_resume = sum(1 for sk in missing_skills if sk.lower() in text_lower)
        total_gaps     = len(missing_skills) if missing_skills else 1
        gap_ratio      = gaps_in_resume / total_gaps
        keyword_score  = min(35, int(12 + 23 * gap_ratio))

        # ── Impact score (0–25): quantified metrics, strong verbs
        metric_hits    = len(re.findall(r'\b\d+\s*[%kKmMbBx]\b|\b\d{2,}\b', resume_text))
        action_verbs   = ["designed", "built", "developed", "engineered", "architected", "implemented",
                          "deployed", "automated", "reduced", "improved", "led", "launched", "scaled",
                          "migrated", "optimized", "integrated", "delivered"]
        verb_hits      = sum(1 for v in action_verbs if v in text_lower)
        impact_score   = min(25, 5 + min(10, metric_hits) + min(10, verb_hits))

        # ── Completeness score (0–15)
        has_projects   = "project" in text_lower
        has_certs      = any(w in text_lower for w in ["certified", "certification", "certificate"])
        comp_score     = min(15, 3 + section_count * 2 + (2 if has_projects else 0) + (1 if has_certs else 0))

        total_ats = format_score + keyword_score + impact_score + comp_score

        # ── Strengths from actual content
        strengths = []
        if verb_hits >= 5:
            strengths.append("Uses strong action verbs across multiple experience entries.")
        if metric_hits >= 3:
            strengths.append("Contains quantified metrics — good signal for ATS impact scoring.")
        if has_projects:
            strengths.append("Dedicated projects section demonstrates hands-on technical depth.")
        if has_certs:
            strengths.append("Certifications listed — high-value differentiator for technical roles.")
        if section_count >= 4:
            strengths.append("All major resume sections present (summary, skills, experience, education).")
        if not strengths:
            strengths.append("Resume contains relevant technical vocabulary for the target role.")

        # ── Critical fixes
        fixes = []
        if not has_summary:
            fixes.append("Add a concise 2–3 sentence professional summary targeting this role at the top.")
        if metric_hits < 3:
            fixes.append("Add quantified metrics to at least 5 bullets (e.g. '40% latency reduction', 'processed 10M events/day').")
        if missing_skills:
            top_gaps = missing_skills[:4]
            fixes.append(f"Integrate missing target keywords naturally into experience bullets: {', '.join(top_gaps)}.")
        if not has_projects:
            fixes.append("Add a Projects section showcasing relevant technical work with tech stack listed.")
        if verb_hits < 3:
            fixes.append("Replace weak/passive phrases ('responsible for', 'worked on') with strong action verbs.")

        # ── Power bullet rewrites from ACTUAL resume bullets
        real_bullets = [l for l in lines if l.startswith(("- ", "• ", "* ")) and len(l) > 30]
        power_rewrites = []
        for bullet in real_bullets[:3]:
            content = bullet[2:].strip()
            # Simple heuristic upgrade: add a metric + XYZ structure if none present
            has_num = bool(re.search(r'\d+', content))
            if not has_num:
                improved = f"Engineered {content.lower().rstrip('.')}, achieving measurable improvements in system reliability and reducing operational overhead."
            else:
                # Already has numbers — emphasize scope
                improved = f"Led implementation of {content.lower().rstrip('.')}, directly contributing to {target_role} objectives and production-grade scalability."
            power_rewrites.append({
                "original": content,
                "improved": improved,
                "rationale": "Upgraded with stronger action verb and clearer production impact framing for ATS parsing."
            })

        if not power_rewrites:
            # No bullets found — use a generic note instead of fake examples
            power_rewrites.append({
                "original": "(No standard bullet points detected — plain paragraphs found)",
                "improved": "Consider reformatting experience entries as bullet points starting with strong verbs.",
                "rationale": "ATS parsers score bullet-formatted achievements higher than paragraph prose."
            })

        return {
            "ats_score": total_ats,
            "formatting_score": format_score,
            "keyword_score": keyword_score,
            "impact_score": impact_score,
            "completeness_score": comp_score,
            "strengths": strengths[:5],
            "critical_fixes": fixes[:5],
            "missing_ats_keywords": missing_skills[:8] if missing_skills else [],
            "power_bullet_rewrites": power_rewrites
        }

    def audit(self, resume_text: str, target_role: str, missing_skills: List[str]) -> Dict[str, Any]:
        """Audits resume for ATS compatibility and generates power bullet rewrites."""
        if not self.client or not resume_text:
            return self._offline_ats_audit(resume_text or "", target_role, missing_skills)

        try:
            prompt = f"""
Target Role: '{target_role}'
Skill gaps identified for this role (keywords to look for in resume): {missing_skills}

CANDIDATE RESUME (evaluate ONLY this text — do not invent content):
\"\"\"
{resume_text}
\"\"\"

Audit this resume and return an ATSAuditResult.
IMPORTANT: power_bullet_rewrites.original must be EXACT quotes from the resume above.
"""
            return self.execute(prompt_input=prompt)
        except Exception as e:
            print(f"[ATS Analyzer Notice]: ({e}). Using heuristic ATS audit.", flush=True)
            return self._offline_ats_audit(resume_text, target_role, missing_skills)
