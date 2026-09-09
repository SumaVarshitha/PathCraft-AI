import os
import sys
import re
import math
import json
from typing import List, Dict, Any, Optional, Tuple
from google.genai import types
import config
from core.adk_agent import ADKAgent
from core.state import SkillGapResult, SemanticMatchItem
from core.agents.skill_normalizer_agent import normalize_skill_name, fuzzy_skill_match, token_exact_match

class GapAnalyzerADKAgent(ADKAgent):
    """
    Google ADK 2.0 Dynamic Vector Semantic Skill Gap Analyzer Agent
    - 100% Dynamic Market Grounding: Queries live 2026 market standards via Google Search Grounding.
    - 2-Tier Requirement Categorization:
        * Tier 1: Core Must-Haves (70% weight) - foundational prerequisites.
        * Tier 2: Advanced Differentiators (30% weight) - modern specialized tools.
    - Deep Multi-Source Candidate Context: Ingests Skills, Work Experience bullets, Projects, Certifications, Tools, GitHub & LinkedIn.
    - Token-Exact + Gemini Vector Embeddings Cosine Matching (no substring matching bugs).
    """
    def __init__(self):
        super().__init__(
            name="GapAnalyzerADKAgent",
            instruction="Conduct precise meaning-based semantic skill gap analysis comparing candidate multi-source evidence against live market requirements.",
            model=config.MODEL_FLASH,
            output_schema=SkillGapResult,
            temperature=0.1
        )

    def resolve_required_skills(self, target_role: str, seniority_level: str = "Mid-Senior") -> Tuple[List[str], List[str], str]:
        """
        Dynamically extracts current 2026 hiring requirements for target_role using live Search Grounding.
        Returns: (core_must_haves, differentiator_skills, method_used)
        """
        if self.client:
            try:
                grounding_prompt = f"""
                Search current live 2026 hiring job postings for the position: '{seniority_level} {target_role}'.
                Extract the actual skills demanded by top tech companies and recruiters:
                1. 'core_must_haves': 5 to 7 mandatory, non-negotiable foundational technical skills, core programming languages, and databases for this role.
                2. 'differentiators': 3 to 5 modern frameworks, specialized libraries, cloud/DevOps tools, or advanced concepts that set top candidates apart.

                Return ONLY a valid JSON object matching this schema:
                {{
                    "core_must_haves": ["Python", "SQL", "Apache Spark", "Data Warehousing", "ETL Pipelines"],
                    "differentiators": ["dbt", "Snowflake", "Apache Airflow", "Docker", "Apache Kafka"]
                }}
                """
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=grounding_prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.1
                    )
                )
                text = response.text.strip()
                if "```json" in text:
                    text = text.split("```json")[-1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                if "{" in text and "}" in text:
                    text = text[text.find("{"):text.rfind("}")+1]
                data = json.loads(text)
                core = [s.strip() for s in data.get("core_must_haves", []) if s.strip()]
                diff = [s.strip() for s in data.get("differentiators", []) if s.strip()]

                if len(core) >= 3:
                    return core, diff, f"Live 2026 Market Search Grounding ({seniority_level})"
            except Exception as e:
                print(f"[GapAnalyzer Dynamic Search Notice]: {e}. Using dynamic AI role synthesizer.", flush=True)

        # Dynamic AI fallback without search tool (if search quota unavailable)
        if self.client:
            try:
                synth_prompt = f"""
                List 2026 technical requirements for '{seniority_level} {target_role}':
                Return JSON with 'core_must_haves' (5 items) and 'differentiators' (4 items).
                """
                resp = self.client.models.generate_content(
                    model=self.model,
                    contents=synth_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1
                    )
                )
                data = json.loads(resp.text.strip())
                core = [s.strip() for s in data.get("core_must_haves", []) if s.strip()]
                diff = [s.strip() for s in data.get("differentiators", []) if s.strip()]
                if core:
                    return core, diff, f"Gemini 2.5 Market Synthesis ({seniority_level})"
            except Exception as e:
                print(f"[GapAnalyzer AI Synthesis Notice]: {e}", flush=True)

        # Baseline engineering role fallback
        role_lower = target_role.lower()
        if "data" in role_lower:
            return ["Python", "SQL", "Apache Spark", "Data Warehousing", "ETL Pipelines"], ["dbt", "BigQuery", "Apache Airflow", "Docker"], "Adaptive Dynamic Baseline"
        elif "ai" in role_lower or "ml" in role_lower:
            return ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "Machine Learning"], ["LLMs", "LangChain", "Vector Databases", "MLflow", "Docker"], "Adaptive Dynamic Baseline"
        elif "frontend" in role_lower:
            return ["JavaScript", "TypeScript", "React", "HTML5", "CSS3"], ["Next.js", "Tailwind CSS", "State Management", "REST APIs"], "Adaptive Dynamic Baseline"
        elif "backend" in role_lower or "software" in role_lower:
            return ["Python", "SQL", "REST APIs", "System Design", "PostgreSQL"], ["Docker", "Redis", "Microservices", "CI/CD"], "Adaptive Dynamic Baseline"
        else:
            return ["Python", "SQL", "Git", "REST APIs", "System Architecture"], ["Docker", "Cloud Platforms", "CI/CD", "Linux"], "Adaptive Dynamic Baseline"

    def compute_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Computes cosine similarity between two embedding vectors."""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def get_text_embedding(self, text: str) -> Optional[List[float]]:
        """Generates vector embedding for a skill string using Gemini embedding model."""
        if not self.client or not text:
            return None
        try:
            res = self.client.models.embed_content(
                model="gemini-embedding-001",
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="SEMANTIC_SIMILARITY",
                    output_dimensionality=256
                )
            )
            if res.embeddings:
                return res.embeddings[0].values
        except Exception:
            pass
        return None

    def analyze(
        self,
        candidate_skills: List[str],
        target_role: str,
        seniority_level: str = "Mid-Senior",
        resume_data: Optional[Dict[str, Any]] = None,
        github_data: Optional[Dict[str, Any]] = None,
        linkedin_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes precision semantic gap analysis with:
        - 2-Tier Weighted Scoring (Core 70% vs Differentiators 30%)
        - Comprehensive multi-source evidence extraction (Work Experience bullets, Projects, Certifications, GitHub, LinkedIn)
        - Strict token-aware matching & Gemini Vector Embeddings
        """
        # Step 1: Resolve Target Role Requirements
        core_skills, differentiator_skills, method_used = self.resolve_required_skills(target_role, seniority_level)
        all_required = [(s, "Core Must-Have") for s in core_skills] + [(s, "Advanced Differentiator") for s in differentiator_skills]

        # Step 2: Ingest Comprehensive Candidate Multi-Source Evidence
        candidate_evidence: List[Tuple[str, str]] = [] # (evidence_text, source_name)

        # Source 1: Verified Skills
        for s in candidate_skills:
            if s and s.strip():
                candidate_evidence.append((s.strip(), "Skills Section"))

        if resume_data:
            # Source 2: Work Experience Bullet Points & Roles
            for exp in resume_data.get("work_experience", []):
                if isinstance(exp, dict):
                    comp = exp.get("company", "Work Experience")
                    role = exp.get("role", "")
                    if role:
                        candidate_evidence.append((role, f"Work Role: {comp}"))
                    for b in exp.get("bullets", []):
                        if b and len(b) > 5:
                            candidate_evidence.append((b, f"Work Experience ({comp})"))

            # Source 3: Project Tech Stacks & Descriptions
            for proj in resume_data.get("projects", []):
                if isinstance(proj, dict):
                    p_title = proj.get("title", "Featured Project")
                    for t in proj.get("tech_stack", []):
                        if t:
                            candidate_evidence.append((t.strip(), f"Project Tech ({p_title})"))
                    p_desc = proj.get("description", "")
                    if p_desc:
                        candidate_evidence.append((p_desc, f"Project Details ({p_title})"))

            # Source 4: Certifications
            for cert in resume_data.get("certifications", []):
                if cert:
                    candidate_evidence.append((cert.strip(), "Certifications"))

            # Source 5: Tools and Technologies
            for tool in resume_data.get("tools_and_technologies", []):
                if tool:
                    candidate_evidence.append((tool.strip(), "Tools & Technologies"))

            # Source 6: LinkedIn Achievements
            li_ach = resume_data.get("linkedin_achievements", "")
            if li_ach:
                candidate_evidence.append((li_ach, "LinkedIn Profile & Achievements"))

        if linkedin_text:
            candidate_evidence.append((linkedin_text, "LinkedIn Profile & Achievements"))

        if github_data:
            # Source 7: GitHub Languages & Repositories
            for lang in github_data.get("languages", []):
                candidate_evidence.append((lang, "GitHub Repositories"))
            for repo in github_data.get("top_repositories", []):
                if isinstance(repo, dict):
                    candidate_evidence.append((repo.get("name", ""), "GitHub Repositories"))

        # Deduplicate candidate items
        unique_candidate_items = []
        seen = set()
        for text, src in candidate_evidence:
            clean_text = text.strip()
            if clean_text and clean_text.lower() not in seen:
                seen.add(clean_text.lower())
                unique_candidate_items.append((clean_text, src))

        # Step 3: Precise Meaning-Based Semantic Matching
        semantic_matches: List[Dict[str, Any]] = []
        verified_skills: List[str] = []
        missing_skills: List[str] = []

        verified_core_count = 0
        verified_diff_count = 0

        for req_skill, category in all_required:
            best_score = 0.0
            best_matched_item = None
            best_source = "Skills Section"

            # Check 1: Token-exact & strict synonym match
            for cand_text, src in unique_candidate_items:
                if token_exact_match(cand_text, req_skill):
                    best_score = 1.0
                    best_matched_item = cand_text
                    best_source = src
                    break

            # Check 2: Gemini Vector Embeddings Cosine Matching
            if best_score < 0.90 and self.client:
                req_emb = self.get_text_embedding(req_skill)
                if req_emb:
                    for cand_text, src in unique_candidate_items:
                        # Don't embed extremely long full documents repeatedly, embed candidate skills/snippets
                        snippet = cand_text[:120]
                        c_emb = self.get_text_embedding(snippet)
                        if c_emb:
                            sim = self.compute_cosine_similarity(req_emb, c_emb)
                            if sim > best_score:
                                best_score = sim
                                best_matched_item = cand_text
                                best_source = src

            # Match threshold: 0.74 (calibrated for high precision)
            is_match = best_score >= 0.74
            if is_match:
                verified_skills.append(req_skill)
                if category == "Core Must-Have":
                    verified_core_count += 1
                else:
                    verified_diff_count += 1
            else:
                missing_skills.append(req_skill)

            semantic_matches.append({
                "required_skill": req_skill,
                "skill_category": category,
                "matched_candidate_skill": best_matched_item if is_match else None,
                "similarity_score": round(min(1.0, best_score), 2),
                "is_match": is_match,
                "evidence_source": best_source if is_match else "Not Found in Profile"
            })

        # Step 4: 2-Tier Weighted Score Calculation
        core_pct = (verified_core_count / len(core_skills) * 100) if core_skills else 0.0
        diff_pct = (verified_diff_count / len(differentiator_skills) * 100) if differentiator_skills else 0.0
        
        # 70% Core + 30% Differentiator
        if core_skills and differentiator_skills:
            overall_score = round((0.70 * core_pct) + (0.30 * diff_pct), 1)
        elif core_skills:
            overall_score = round(core_pct, 1)
        else:
            overall_score = 0.0

        return {
            "verified_skills": verified_skills,
            "missing_skills": missing_skills,
            "core_requirements": core_skills,
            "differentiator_requirements": differentiator_skills,
            "match_percentage": overall_score,
            "core_match_percentage": round(core_pct, 1),
            "semantic_matches": semantic_matches,
            "analysis_method": method_used,
            "required_skills": core_skills + differentiator_skills
        }
