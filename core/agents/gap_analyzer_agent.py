import os
import sys
import re
import math
from typing import List, Dict, Any, Optional
from google.genai import types
import config
from core.adk_agent import ADKAgent
from core.state import SkillGapResult, SemanticMatchItem
from core.agents.skill_normalizer_agent import normalize_skill_name, fuzzy_skill_match, EQUIVALENT_GROUPS
from core.mcp_tools.bigquery_mcp import BigQueryMCPTool

CORE_ROLE_TAXONOMY = {
    "data engineer": ["Python", "SQL", "Apache Spark", "PySpark", "BigQuery", "Apache Airflow", "Docker", "Data Warehousing", "ETL Pipelines", "Git"],
    "backend engineer": ["Python", "Node.js", "REST APIs", "SQL", "PostgreSQL", "Docker", "System Design", "Microservices", "Git", "Redis"],
    "ai/ml engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "LLMs", "LangChain", "Vector Databases", "Docker", "Git", "MLOps"],
    "frontend engineer": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Tailwind CSS", "REST APIs", "State Management", "Git"],
    "fullstack engineer": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "REST APIs", "SQL", "PostgreSQL", "Docker", "Git"],
    "devops / sre engineer": ["Linux", "Docker", "Kubernetes", "Terraform", "CI/CD", "AWS", "Python", "Bash", "Prometheus", "Git"],
    "cloud solutions architect": ["AWS", "Google Cloud Platform", "System Architecture", "Docker", "Kubernetes", "Terraform", "Networking", "Security", "Python"],
    "data scientist": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Data Visualization", "Statistics", "Git"],
    "mlops engineer": ["Python", "Docker", "Kubernetes", "MLflow", "Kubeflow", "CI/CD", "PyTorch", "Model Monitoring", "Git", "GCP"],
    "cybersecurity engineer": ["Linux", "Networking", "Penetration Testing", "SIEM", "Python", "Cryptography", "Identity & Access Management", "Cloud Security", "Git"],
    "mobile app developer": ["Swift", "Kotlin", "React Native", "Flutter", "REST APIs", "Mobile UI/UX", "Git", "State Management", "CI/CD"]
}

STOP_WORDS = {"engineer", "developer", "specialist", "analyst", "architect", "lead", "senior", "junior", "staff", "principal", "manager", "consultant", "intern"}

def extract_search_keywords(role_title: str) -> List[str]:
    raw = re.split(r'[/\-&\s]+', role_title.lower().strip())
    keywords = [w for w in raw if w and w not in STOP_WORDS]
    expansions = {
        "ai": ["artificial intelligence", "machine learning"],
        "ml": ["machine learning"],
        "nlp": ["natural language processing"],
        "sre": ["site reliability", "devops"],
        "devops": ["devops", "kubernetes"],
        "fullstack": ["full stack", "react", "node"],
        "data": ["data engineering", "sql", "spark"],
        "cloud": ["cloud", "aws", "gcp"],
        "mlops": ["mlops", "machine learning"]
    }
    expanded = list(keywords)
    for kw in keywords:
        if kw in expansions:
            expanded.extend(expansions[kw])
    seen = set()
    unique = []
    for k in expanded:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    return unique if unique else [role_title.lower().strip()]


class GapAnalyzerADKAgent(ADKAgent):
    """
    Google ADK 2.0 Semantic Skill Gap Analyzer Agent
    - Resolves required skills via Live 2026 Market Search Grounding, BigQuery MCP, or Taxonomy.
    - Ingests full candidate context (Skills, Projects, Certifications, GitHub).
    - Performs true Semantic Embedding Cosine Matching (gemini-embedding-001) for meaning-based scoring.
    """
    def __init__(self, gcp_project_id: Optional[str] = None):
        self.bigquery_mcp = BigQueryMCPTool(gcp_project_id=gcp_project_id)
        super().__init__(
            name="GapAnalyzerADKAgent",
            instruction="Conduct meaning-based semantic skill gap analysis comparing candidate context against target role requirements.",
            model=config.MODEL_FLASH,
            output_schema=SkillGapResult,
            temperature=0.1
        )

    def resolve_required_skills(self, target_role: str) -> tuple[List[str], str]:
        """Resolves target role required skills using 3-tier consensus."""
        role_key = target_role.strip().lower()

        # 1. Tier 1: Live Market Search Grounding with Gemini 3.6 / 2.5 Flash
        if self.client:
            try:
                grounding_prompt = f"""
                Search current 2026 hiring requirements for the job title: '{target_role}'.
                List the 8 to 10 most critical hard technical skills, tools, and frameworks mandatory for this role.
                Return ONLY a valid JSON list of strings, for example: ["Python", "Apache Spark", "BigQuery", "Docker"]
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
                import json
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                
                # Extract json list if surrounded by text
                if "[" in text and "]" in text:
                    text = text[text.find("["):text.rfind("]")+1]
                skills = json.loads(text)
                if isinstance(skills, list) and len(skills) >= 4:
                    return [s.title() if len(s) > 3 else s for s in skills[:10]], "TIER 1 (Live 2026 Market Search Grounding)"
            except Exception as e:
                print(f"[GapAnalyzer Notice]: Live Search Grounding notice ({e}). Falling back to BigQuery/Taxonomy.", flush=True)

        # 2. Tier 2: BigQuery MCP Tool
        keywords = extract_search_keywords(target_role)
        bq_skills = self.bigquery_mcp.query_role_skills(keywords, limit=10)
        if bq_skills and len(bq_skills) >= 4:
            return bq_skills, "TIER 2 (GCP BigQuery Live Dataset SQL)"

        # 3. Tier 3: Curated Industry Taxonomy Matrix
        for k in CORE_ROLE_TAXONOMY:
            if k in role_key or role_key in k:
                return CORE_ROLE_TAXONOMY[k], "TIER 3 (Curated Industry Taxonomy Matrix)"

        return ["Python", "SQL", "Docker", "Git", "REST APIs", "System Design"], "TIER 3 (Default Engineering Baseline)"

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
        if not self.client:
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
        resume_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executes semantic gap analysis comparing candidate's entire context (skills + projects + certs)
        against target role requirements using Gemini Vector Embeddings.
        """
        # Step 1: Resolve Target Role Requirements
        required_skills, method_used = self.resolve_required_skills(target_role)

        # Step 2: Aggregate Candidate Comprehensive Context
        candidate_items = [] # tuples of (text, source)
        for s in candidate_skills:
            candidate_items.append((s, "Skills Section"))

        if resume_data:
            # Ingest Projects tech stacks and titles
            projects = resume_data.get("projects", [])
            for proj in projects:
                if isinstance(proj, dict):
                    title = proj.get("title", "")
                    for tech in proj.get("tech_stack", []):
                        candidate_items.append((tech, f"Project: {title}"))
                    desc = proj.get("description", "")
                    if desc:
                        candidate_items.append((desc[:80], f"Project: {title}"))
            
            # Ingest Certifications
            for cert in resume_data.get("certifications", []):
                candidate_items.append((cert, "Certifications"))
                
            # Ingest Tools and Technologies
            for tool in resume_data.get("tools_and_technologies", []):
                candidate_items.append((tool, "Tools & Technologies"))

        # Deduplicate candidate items
        unique_cand_items = []
        seen = set()
        for text, src in candidate_items:
            if text and text.strip().lower() not in seen:
                seen.add(text.strip().lower())
                unique_cand_items.append((text.strip(), src))

        # Step 3: Meaning-Based Semantic Matching
        semantic_matches: List[Dict[str, Any]] = []
        verified_skills: List[str] = []
        missing_skills: List[str] = []
        match_scores: List[float] = []

        print(f"\n====================== SEMANTIC SKILL GAP ANALYSIS LOG ======================", flush=True)
        print(f"[LOG - SKILL GAP ENGINE]: Role: '{target_role}' | Source: {method_used}", flush=True)
        print(f"   -> Target Role Requirements ({len(required_skills)}): {required_skills}", flush=True)

        for req in required_skills:
            req_norm = normalize_skill_name(req)
            best_score = 0.0
            best_match_skill = None
            best_source = "Skills Section"

            # 1. Quick rule check (Exact or Synonyms or Groups)
            for c_text, c_src in unique_cand_items:
                if fuzzy_skill_match(c_text, req):
                    best_score = 0.95
                    best_match_skill = c_text
                    best_source = c_src
                    break

            # 2. Embedding Cosine Similarity (if not already exact match)
            if best_score < 0.90 and self.client:
                req_emb = self.get_text_embedding(req)
                if req_emb:
                    for c_text, c_src in unique_cand_items:
                        c_emb = self.get_text_embedding(c_text)
                        if c_emb:
                            sim = self.compute_cosine_similarity(req_emb, c_emb)
                            if sim > best_score:
                                best_score = sim
                                best_match_skill = c_text
                                best_source = c_src

            # Threshold for matching: 0.72
            is_match = best_score >= 0.72
            if is_match:
                verified_skills.append(req)
                match_scores.append(min(1.0, best_score))
                print(f"   + [MATCH] '{req}' <-> '{best_match_skill}' ({best_source}) | Score: {best_score:.2f}", flush=True)
            else:
                missing_skills.append(req)
                match_scores.append(best_score if best_score > 0.3 else 0.0)
                print(f"   - [GAP]   '{req}' (Best candidate match: '{best_match_skill or 'None'}' | Score: {best_score:.2f})", flush=True)

            semantic_matches.append({
                "required_skill": req,
                "matched_candidate_skill": best_match_skill if is_match else None,
                "similarity_score": round(best_score, 2),
                "is_match": is_match,
                "evidence_source": best_source if is_match else "None"
            })

        overall_score = round((len(verified_skills) / len(required_skills) * 100), 1) if required_skills else 0.0
        print(f"\n[LOG - SKILL GAP ENGINE]: Verified: {len(verified_skills)}/{len(required_skills)} | Overall Match: {overall_score}%", flush=True)
        print(f"==============================================================================\n", flush=True)
        sys.stdout.flush()

        return {
            "verified_skills": verified_skills,
            "missing_skills": missing_skills,
            "match_percentage": overall_score,
            "semantic_matches": semantic_matches,
            "analysis_method": method_used,
            "required_skills": required_skills
        }
