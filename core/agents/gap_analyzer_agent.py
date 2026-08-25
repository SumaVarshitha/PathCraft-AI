import os
import sys
import json
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

class GapAnalyzerADKAgent(ADKAgent):
    """
    Google ADK 2.0 Skill Gap Analyzer Agent
    Supports 3-Tier Execution with Immediate Unbuffered Logging:
    - Tier 1: BigQuery Live Data SQL Query
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
        """Executes a live SQL query against BigQuery Public Datasets."""
        if not self.gcp_project_id:
            return None

        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=self.gcp_project_id)
            
            sql_query = """
                SELECT skill_name
                FROM `bigquery-public-data.stackoverflow.posts_questions`
                WHERE LOWER(title) LIKE LOWER(@role)
                GROUP BY skill_name
                ORDER BY COUNT(*) DESC
                LIMIT 10
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("role", "STRING", f"%{target_role}%")
                ]
            )
            query_job = client.query(sql_query, job_config=job_config)
            results = query_job.result()
            skills = [row.skill_name for row in results if row.skill_name]
            return skills if skills else None
            
        except Exception as e:
            print(f"⚠️ [BigQuery Notice]: Unable to query BigQuery ({e}). Falling back to Tier 2 taxonomy.", flush=True)
            return None

    def analyze(self, candidate_skills: List[str], target_role: str) -> Dict[str, Any]:
        role_key = target_role.strip().lower()
        method_used = ""
        
        # 1. Tier 1: Try BigQuery Live Data SQL Query
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
                print(f"⚠️ [ADK 2.0 Gap Analyzer Error]: {e}", flush=True)
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
