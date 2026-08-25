import os
import sys
import json
import re
from typing import List, Dict, Any, Optional
from google.genai import types
import config
from core.adk_agent import ADKAgent
from core.state import SkillGapResult
from core.agents.skill_normalizer_agent import normalize_skill_name

CORE_ROLE_TAXONOMY = {
    "data engineer": ["Python", "SQL", "Apache Spark", "PySpark", "BigQuery", "Apache Airflow", "Docker", "Data Warehousing", "ETL Pipelines", "Git"],
    "backend engineer": ["Python", "Node.js", "REST APIs", "SQL", "PostgreSQL", "Docker", "System Design", "Microservices", "Git", "Redis"],
    "ai/ml engineer": ["Python", "PyTorch", "TensorFlow", "Scikit-Learn", "LLMs", "LangChain", "Vector Databases", "Docker", "Git", "MLOps"],
    "frontend engineer": ["JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Tailwind CSS", "REST APIs", "State Management", "Git"],
    "fullstack engineer": ["JavaScript", "TypeScript", "React", "Node.js", "Python", "REST APIs", "SQL", "PostgreSQL", "Docker", "Git"],
    "devops / sre engineer": ["Linux", "Docker", "Kubernetes", "Terraform", "CI/CD", "AWS", "Python", "Bash", "Prometheus", "Git"],
    "cloud solutions architect": ["AWS", "Google Cloud Platform", "System Architecture", "Docker", "Kubernetes", "Terraform", "Networking", "Security", "Python"],
    "data scientist": ["Python", "R", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Data Visualization", "Statistics", "Git"],
    "mlops engineer": ["Python", "Docker", "Kubernetes", "MLflow", "Kubeflow", "CI/CD", "PyTorch", "Model Monitoring", "Git", "GCP"]
}

# Generic filler words to strip from any role title before BigQuery search
STOP_WORDS = {"engineer", "developer", "specialist", "analyst", "architect", "lead", "senior", "junior", "staff", "principal", "manager", "consultant", "intern", "associate", "head", "vp", "director"}

def extract_search_keywords(role_title: str) -> List[str]:
    """
    Dynamically extracts meaningful search keywords from ANY role title.
    Examples:
      'AI/ML Engineer'         -> ['ai', 'ml', 'machine learning']
      'Data Engineer'          -> ['data']
      'DevOps / SRE Engineer'  -> ['devops', 'sre']
      'Blockchain Developer'   -> ['blockchain']
      'Prompt Engineer'        -> ['prompt']
      'Cloud Solutions Architect' -> ['cloud', 'solutions']
    """
    # 1. Lowercase and split on /, -, spaces, &
    raw = re.split(r'[/\-&\s]+', role_title.lower().strip())
    
    # 2. Remove generic filler words
    keywords = [w for w in raw if w and w not in STOP_WORDS]
    
    # 3. Add common synonyms/expansions for well-known abbreviations
    expansions = {
        "ai": ["artificial intelligence", "machine learning", "deep learning"],
        "ml": ["machine learning"],
        "nlp": ["natural language processing"],
        "cv": ["computer vision"],
        "sre": ["site reliability", "devops"],
        "devops": ["devops", "ci cd", "infrastructure"],
        "fullstack": ["full stack", "frontend", "backend"],
        "frontend": ["front end", "javascript", "react"],
        "backend": ["back end", "api", "server"],
        "data": ["data", "database", "analytics"],
        "cloud": ["cloud", "aws", "gcp", "azure"],
        "mlops": ["mlops", "machine learning", "deployment"],
        "ios": ["ios", "swift", "mobile"],
        "android": ["android", "kotlin", "mobile"],
        "qa": ["testing", "quality assurance", "automation testing"],
        "security": ["cybersecurity", "security", "penetration testing"],
        "blockchain": ["blockchain", "web3", "smart contract"],
        "prompt": ["prompt engineering", "llm", "generative ai"],
        "genai": ["generative ai", "llm", "large language model"],
    }
    
    expanded = list(keywords)  # start with original keywords
    for kw in keywords:
        if kw in expansions:
            expanded.extend(expansions[kw])
    
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for k in expanded:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    
    return unique if unique else [role_title.lower().strip()]


class GapAnalyzerADKAgent(ADKAgent):
    """
    Google ADK 2.0 Skill Gap Analyzer Agent
    Supports 3-Tier Execution with Immediate Unbuffered Logging:
    - Tier 1: BigQuery Live Data SQL Query (dynamic keyword extraction, works for ANY role)
    - Tier 2: Static Industry Taxonomy Matrix
    - Tier 3: Gemini 3.6 Flash Dynamic Skill Generation
    """
    def __init__(self, gcp_project_id: Optional[str] = None):
        self.gcp_project_id = gcp_project_id or os.getenv("GCP_PROJECT_ID", "")
        
        super().__init__(
            name="GapAnalyzerADKAgent",
            instruction="Compare candidate verified skills against target job role requirements and output verified vs missing skills and match score.",
            model=config.MODEL_FLASH,
            output_schema=SkillGapResult,
            temperature=0.1
        )

    def query_bigquery_live_data(self, target_role: str) -> Optional[List[str]]:
        """
        Executes a live SQL query against BigQuery Public Datasets.
        Dynamically extracts search keywords from ANY role title —
        no hardcoding needed. Works for dropdown roles AND custom typed roles.
        """
        if not self.gcp_project_id:
            return None

        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=self.gcp_project_id)
            
            # Dynamically extract search keywords from any role title
            keywords = extract_search_keywords(target_role)
            
            print(f"[LOG - BigQuery] Role: '{target_role}' -> Search Keywords: {keywords}", flush=True)
            
            # Build dynamic OR conditions: one LIKE per keyword
            where_clauses = " OR ".join([f"LOWER(title) LIKE @kw{i}" for i in range(len(keywords))])
            
            sql_query = f"""
                SELECT tag, COUNT(*) as cnt
                FROM `bigquery-public-data.stackoverflow.posts_questions`,
                UNNEST(SPLIT(tags, '|')) as tag
                WHERE {where_clauses}
                GROUP BY tag
                ORDER BY cnt DESC
                LIMIT 15
            """
            
            # Build parameterized query parameters dynamically
            query_params = [
                bigquery.ScalarQueryParameter(f"kw{i}", "STRING", f"%{kw}%")
                for i, kw in enumerate(keywords)
            ]
            
            job_config = bigquery.QueryJobConfig(query_parameters=query_params)
            query_job = client.query(sql_query, job_config=job_config)
            results = query_job.result()
            skills = [row.tag.replace('-', ' ').title() for row in results if row.tag]
            
            print(f"[LOG - BigQuery] Raw tags returned: {skills}", flush=True)
            sys.stdout.flush()
            
            return skills if skills else None
            
        except Exception as e:
            print(f"[BigQuery Notice]: Unable to query BigQuery ({e}). Falling back to Tier 2 taxonomy.", flush=True)
            return None

    def analyze(self, candidate_skills: List[str], target_role: str) -> Dict[str, Any]:
        role_key = target_role.strip().lower()
        method_used = ""
        
        # 1. Tier 1: Try BigQuery Live Data SQL Query (works for ANY role dynamically)
        required_skills = self.query_bigquery_live_data(target_role)
        if required_skills:
            method_used = "TIER 1 (GCP BigQuery Live Data SQL)"
        
        # 2. Tier 2: Try Static Taxonomy Matrix lookup
        if not required_skills:
            for k in CORE_ROLE_TAXONOMY:
                if k in role_key or role_key in k:
                    required_skills = CORE_ROLE_TAXONOMY[k]
                    method_used = "TIER 2 (Industry Taxonomy Matrix)"
                    break
                    
        cand_set = set(normalize_skill_name(s) for s in candidate_skills)
        
        # 3. Tier 3: Fallback to Gemini 3.6 Flash Dynamic Skill Generation
        if not required_skills:
            method_used = "TIER 3 (Gemini 3.6 Flash Dynamic Generation)"
            prompt = f"""
            Identify the 8 to 10 most essential hard technical skills required for a candidate applying for the target role: '{target_role}'.
            Compare these requirements against the candidate's verified skills: {list(cand_set)}.
            Return verified skills, missing skills, and calculate match_percentage.
            """
            try:
                result = self.execute(prompt_input=prompt)
                print(f"[LOG - SKILL GAP ENGINE]: Fetched skills for '{target_role}' using METHOD: {method_used}", flush=True)
                sys.stdout.flush()
                return result
            except Exception as e:
                print(f"[ADK 2.0 Gap Analyzer Error]: {e}", flush=True)
                required_skills = ["Python", "SQL", "Git", "System Architecture", "Docker"]

        # EXPLICIT IMMEDIATE LOGGING PRINT
        print(f"\n====================== SKILL GAP ENGINE LOG ======================", flush=True)
        print(f"[LOG - SKILL GAP ENGINE]: Fetched skills for '{target_role}' using METHOD: {method_used}", flush=True)
        print(f"   -> Required Skills: {required_skills}", flush=True)
        print(f"==================================================================\n", flush=True)
        sys.stdout.flush()

        req_norm = [normalize_skill_name(s) for s in required_skills]
        verified = [s for s in req_norm if s in cand_set]
        missing = [s for s in req_norm if s not in cand_set]
        match_pct = round((len(verified) / len(req_norm)) * 100, 1) if req_norm else 0.0
        
        return {
            "verified_skills": verified,
            "missing_skills": missing,
            "match_percentage": match_pct,
            "analysis_method": method_used,
            "required_skills": required_skills
        }
