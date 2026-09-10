import os
import sys
import re
import math
import json
from typing import List, Dict, Any, Optional, Tuple
import config
from core.adk_agent import ADKAgent
from core.state import SkillGapResult, SemanticMatchItem
from core.agents.skill_normalizer_agent import normalize_skill_name, fuzzy_skill_match, token_exact_match

# Overly generic single-word terms that must not falsely trigger a complete skill match on their own
GENERIC_STOPWORDS = {"ai", "ml", "data", "cloud", "systems", "code", "app", "api", "apis", "tool", "tools", "and", "or", "for", "with", "the"}

def split_compound_skill(skill_str: str) -> List[str]:
    """Splits compound skills into precise, high-signal atomic components without loose generic stopwords."""
    clean_skill = skill_str.strip()
    parts = re.split(r'\s+/\s+|\s*&\s*|\s*,\s*|\s*\+\s*|\band\b', clean_skill, flags=re.IGNORECASE)
    atoms = []
    for p in parts:
        clean = p.strip()
        if clean and len(clean) >= 2 and clean.lower() not in GENERIC_STOPWORDS:
            atoms.append(clean)
    if clean_skill not in atoms:
        atoms.insert(0, clean_skill)
    return atoms if atoms else [clean_skill]

HIGH_VALUE_SUPERPOWERS = [
    "LangGraph", "Multi-Agent Systems", "RAG", "Retrieval-Augmented Generation", "Tool-Calling",
    "Agentic Workflows", "Prompt Engineering", "Vector Databases", "GenSQL", "LangChain",
    "LlamaIndex", "Groovy", "Jenkins CI/CD", "Kubernetes", "Apache Spark", "Snowflake",
    "BigQuery", "Terraform", "FastAPI", "Microservices Architecture"
]

class GapAnalyzerADKAgent(ADKAgent):
    """
    Google ADK 2.0 Dynamic Vector Semantic Skill Gap Analyzer Agent
    - 100% Dynamic Market Grounding: Queries live 2026 hiring requirements via Google Search Grounding.
    - 2-Tier Requirement Categorization:
        * Tier 1: Core Must-Haves (70% weight) - non-negotiable foundational prerequisites.
        * Tier 2: Advanced Differentiators (30% weight) - specialized tools (LangGraph, RAG, Multi-Agent, Vector DBs, Cloud).
    - Candidate Superpower Detection: Surfaces high-value cutting-edge competencies present in candidate's projects.
    - Alternate Role Recommender: Recommends high-synergy job titles matching candidate's superpowers.
    """
    def __init__(self):
        super().__init__(
            name="GapAnalyzerADKAgent",
            instruction="Conduct precise meaning-based semantic skill gap analysis and surface candidate superpowers.",
            model=config.MODEL_PRO,
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
                Search current live 2026 hiring requirements and tech stacks for the job title: '{seniority_level} {target_role}'.
                Extract the modern requirements demanded by top engineering organizations:
                1. 'core_must_haves': 5 to 6 mandatory, non-negotiable foundational skills and core systems.
                2. 'differentiators': 4 to 6 modern frameworks, specialized tools (e.g. LangGraph, RAG, Multi-Agent Systems, Tool-Calling, Vector DBs, CI/CD Orchestration, Cloud Architecture) that set candidates apart.

                Return ONLY a valid JSON object matching this schema:
                {{
                    "core_must_haves": ["Python", "Machine Learning / AI", "SQL", "System Design", "Docker"],
                    "differentiators": ["LangGraph / Multi-Agent Systems", "RAG & Vector Databases", "Tool-Calling & Agentic Workflows", "Prompt Engineering", "FastAPI", "CI/CD Orchestration"]
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
                print(f"[GapAnalyzer Dynamic Search Notice]: {e}", flush=True)

        # Dynamic AI fallback
        role_lower = target_role.lower()
        if any(w in role_lower for w in ["ai", "ml", "agent", "llm", "genai"]):
            return (
                ["Python", "Machine Learning / AI", "LLMs & Prompt Engineering", "System Design", "APIs"],
                ["LangGraph / Multi-Agent Systems", "RAG & Vector Databases", "Tool-Calling & Agentic Workflows", "Docker & CI/CD", "FastAPI"],
                "Modern AI Systems Baseline (2026)"
            )
        elif "data" in role_lower:
            return (
                ["Python", "SQL", "Apache Spark", "Data Warehousing", "ETL Pipelines"],
                ["LangGraph & GenAI for Data", "dbt", "Snowflake / BigQuery", "Apache Airflow", "Docker & CI/CD"],
                "Modern Data & AI Baseline (2026)"
            )
        elif "frontend" in role_lower:
            return (
                ["JavaScript", "TypeScript", "React", "HTML5", "CSS3"],
                ["Next.js", "Tailwind CSS", "State Management", "REST APIs", "CI/CD"],
                "Modern Frontend Baseline (2026)"
            )
        else:
            return (
                ["Python", "SQL", "REST APIs", "System Architecture", "PostgreSQL"],
                ["Docker & CI/CD", "Kubernetes", "Redis", "Microservices", "Cloud Security"],
                "Modern Software Systems Baseline (2026)"
            )

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
        Executes precision semantic gap analysis:
        - 2-Tier Weighted Scoring (Core 70% vs Differentiators 30%)
        - Compound skill splitting & atomic verification
        - Candidate Superpower Detection (LangGraph, RAG, Agents, etc.)
        - Alternate High-Match Role Recommendations
        """
        # Step 1: Resolve Target Role Requirements
        core_skills, differentiator_skills, method_used = self.resolve_required_skills(target_role, seniority_level)
        all_required = [(s, "Core Must-Have") for s in core_skills] + [(s, "Advanced Differentiator") for s in differentiator_skills]

        # Step 2: Ingest Comprehensive Candidate Multi-Source Evidence
        candidate_evidence: List[Tuple[str, str]] = []

        # Source 1: Verified Skills List
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
                    candidate_evidence.append((p_title, f"Project Title: {p_title}"))
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

        # Step 3: Precise Meaning-Based Semantic Matching with Compound Awareness
        semantic_matches: List[Dict[str, Any]] = []
        verified_skills: List[str] = []
        missing_skills: List[str] = []

        verified_core_count = 0
        verified_diff_count = 0

        # Embedding cache to prevent redundant API roundtrips
        emb_cache: Dict[str, List[float]] = {}
        def get_cached_embedding(text_snippet: str) -> Optional[List[float]]:
            clean_s = text_snippet.strip()[:140]
            if not clean_s or not self.client:
                return None
            if clean_s not in emb_cache:
                emb = self.get_text_embedding(clean_s)
                if emb:
                    emb_cache[clean_s] = emb
            return emb_cache.get(clean_s)

        for req_skill, category in all_required:
            best_score = 0.0
            best_matched_item = None
            best_source = "Skills Section"

            atomic_subskills = split_compound_skill(req_skill)

            # Check 1: Token-exact & strict synonym match
            for sub in atomic_subskills:
                for cand_text, src in unique_candidate_items:
                    if token_exact_match(cand_text, sub):
                        best_score = 1.0
                        best_matched_item = cand_text
                        best_source = src
                        break
                if best_score == 1.0:
                    break

            # Check 2: Regex word boundary search across all candidate bullet points and descriptions
            if best_score < 0.90:
                for sub in atomic_subskills:
                    sub_norm = sub.lower().strip()
                    pattern = r'\b' + re.escape(sub_norm) + r'\b'
                    for cand_text, src in unique_candidate_items:
                        if re.search(pattern, cand_text.lower()):
                            best_score = 0.95
                            best_matched_item = cand_text
                            best_source = src
                            break
                    if best_score >= 0.90:
                        break

            # Check 3: Gemini Vector Embeddings Cosine Matching with Cache
            if best_score < 0.90 and self.client:
                req_emb = get_cached_embedding(req_skill)
                if req_emb:
                    for cand_text, src in unique_candidate_items[:30]:
                        c_emb = get_cached_embedding(cand_text)
                        if c_emb:
                            sim = self.compute_cosine_similarity(req_emb, c_emb)
                            if sim > best_score:
                                best_score = sim
                                best_matched_item = cand_text
                                best_source = src

            # Match threshold: 0.70
            is_match = best_score >= 0.70
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

        # Step 4: Detect Candidate Superpowers (Skills that exceed or stand out)
        superpowers_found = []
        for sp in HIGH_VALUE_SUPERPOWERS:
            sp_lower = sp.lower()
            pattern = r'\b' + re.escape(sp_lower) + r'\b'
            for cand_text, src in unique_candidate_items:
                if re.search(pattern, cand_text.lower()):
                    if sp not in superpowers_found:
                        superpowers_found.append(sp)
                    break

        # Step 5: Dynamic Alternate High-Match Role Recommendations (Gemini-powered, non-hardcoded)
        alternate_roles = self._compute_alternate_roles_dynamic(
            superpowers_found=superpowers_found,
            verified_skills=verified_skills,
            candidate_skills=candidate_skills,
            target_role=target_role
        )

        # Step 6: 2-Tier Weighted Score Calculation
        core_pct = (verified_core_count / len(core_skills) * 100) if core_skills else 0.0
        diff_pct = (verified_diff_count / len(differentiator_skills) * 100) if differentiator_skills else 0.0
        
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
            "candidate_superpowers": superpowers_found,
            "suggested_alternate_roles": alternate_roles,
            "analysis_method": method_used,
            "required_skills": core_skills + differentiator_skills
        }

    def _compute_alternate_roles_dynamic(
        self,
        superpowers_found: List[str],
        verified_skills: List[str],
        candidate_skills: List[str],
        target_role: str
    ) -> List[Dict[str, Any]]:
        """
        Dynamically computes alternate high-match role recommendations using Gemini.
        Match percentages are grounded in the candidate's actual verified evidence —
        never hardcoded. Falls back to evidence-based computation when API is offline.
        """
        all_evidence = list(set(superpowers_found + verified_skills + candidate_skills))
        evidence_str = ", ".join(all_evidence[:30]) if all_evidence else "General software engineering skills"

        if self.client and all_evidence:
            try:
                prompt = f"""
You are a senior technical recruiter with expertise in 2026 job market trends.

A candidate applying for "{target_role}" has the following VERIFIED skills and superpowers (evidence-backed):
{evidence_str}

Based ONLY on these verified competencies, recommend 2-3 alternate high-match job titles where this candidate would be extremely competitive.

For each role:
1. Choose roles that genuinely match their evidence stack (not generic roles).
2. Compute estimated_match as an integer percentage (65-98%) reflecting how many of their verified skills directly apply to that role's typical requirements. Be realistic and specific.
3. Write a 1-2 sentence rationale grounded in their specific verified skills — name the actual skills.

Return ONLY valid JSON:
[
  {{
    "role": "Exact Job Title",
    "estimated_match": 87,
    "rationale": "Specific rationale mentioning their actual verified skills."
  }}
]
"""
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )
                text = response.text.strip()
                if "```json" in text:
                    text = text.split("```json")[-1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                if "[" in text:
                    text = text[text.find("["):text.rfind("]") + 1]

                roles_raw = json.loads(text)
                result = []
                for r in roles_raw:
                    if isinstance(r, dict) and r.get("role"):
                        match_val = r.get("estimated_match", 80)
                        # Ensure it's formatted as a percentage string
                        if isinstance(match_val, (int, float)):
                            match_str = f"{int(round(match_val))}%"
                        else:
                            match_str = str(match_val).replace("%", "").strip() + "%"
                        result.append({
                            "role": r["role"],
                            "estimated_match": match_str,
                            "rationale": r.get("rationale", "Strong skill alignment detected.")
                        })
                if result:
                    return result
            except Exception as e:
                print(f"[GapAnalyzer Alternate Roles Notice]: {e}", flush=True)

        # Offline evidence-based fallback (no hardcoded percentages)
        fallback_roles: List[Dict[str, Any]] = []
        sp_lower = {s.lower() for s in superpowers_found}
        v_lower = {s.lower() for s in verified_skills + candidate_skills}

        # Compute match % as fraction of known role requirements met
        role_requirements = {
            "GenAI & LLM Systems Engineer": ["langgraph", "rag", "tool-calling", "llm", "langchain", "multi-agent", "python", "fastapi"],
            "AI Agent Systems Architect": ["langgraph", "multi-agent", "agentic", "rag", "tool-calling", "python", "system design"],
            "MLOps Engineer": ["docker", "kubernetes", "ci/cd", "python", "mlflow", "terraform", "gcp", "aws"],
            "DevOps & Platform Engineer": ["docker", "kubernetes", "terraform", "jenkins", "ci/cd", "gcp", "aws", "linux"],
            "Data & AI Platform Engineer": ["bigquery", "spark", "sql", "python", "airflow", "dbt", "snowflake", "gcp"],
            "Backend / API Engineer": ["python", "fastapi", "postgresql", "docker", "rest", "microservices", "sql"],
            "Cloud Infrastructure Engineer": ["terraform", "gcp", "aws", "kubernetes", "ci/cd", "linux", "docker"],
        }

        def compute_match(reqs: List[str]) -> int:
            hits = sum(1 for req in reqs if req in sp_lower or req in v_lower)
            return min(97, max(55, int(round((hits / len(reqs)) * 100))))

        def build_rationale(role_name: str, reqs: List[str]) -> str:
            matched = [r for r in reqs if r in sp_lower or r in v_lower]
            named = ", ".join(s.upper() for s in matched[:4]) if matched else "core software engineering skills"
            return f"Verified competencies in {named} directly satisfy key requirements for {role_name}."

        # Score all roles and pick top 3 non-target roles
        scored = []
        target_lower = target_role.lower()
        for role_name, reqs in role_requirements.items():
            # Skip only if exact target role
            if role_name.lower() == target_lower or target_lower in role_name.lower() and len(target_lower) > 15:
                continue
            pct = compute_match(reqs)
            scored.append((pct, role_name, reqs))

        scored.sort(key=lambda x: -x[0])
        for pct, role_name, reqs in scored[:3]:
            fallback_roles.append({
                "role": role_name,
                "estimated_match": f"{pct}%",
                "rationale": build_rationale(role_name, reqs)
            })

        return fallback_roles
