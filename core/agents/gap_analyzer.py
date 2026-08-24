import os
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from core.state import SkillGapResult
from core.agents.skill_normalizer import normalize_skill

# Baseline Core Role Requirements Matrix
CORE_ROLE_TAXONOMY = {
    "data engineer": [
        "Python", "SQL", "Apache Spark", "PySpark", "BigQuery", 
        "Apache Airflow", "Docker", "Data Warehousing", "ETL Pipelines", "Git"
    ],
    "backend engineer": [
        "Python", "Node.js", "REST APIs", "SQL", "PostgreSQL", 
        "Docker", "System Design", "Microservices", "Git", "Redis"
    ],
    "ai/ml engineer": [
        "Python", "PyTorch", "TensorFlow", "Scikit-Learn", "LLMs", 
        "LangChain", "Vector Databases", "Docker", "Git", "MLOps"
    ],
    "frontend engineer": [
        "JavaScript", "TypeScript", "React", "HTML5", "CSS3", 
        "Tailwind CSS", "REST APIs", "State Management", "Git"
    ]
}

def analyze_skill_gap(candidate_skills: List[str], target_role: str) -> Dict[str, Any]:
    """
    Compares candidate's unified skills against target role requirements.
    Calculates missing skills and match percentage.
    """
    role_key = target_role.strip().lower()
    
    # Check baseline taxonomy first
    required_skills = None
    for k in CORE_ROLE_TAXONOMY:
        if k in role_key or role_key in k:
            required_skills = CORE_ROLE_TAXONOMY[k]
            break
            
    # Normalize candidate skills set
    cand_set = set(normalize_skill(s) for s in candidate_skills)
    
    # If role not found in baseline taxonomy, call Gemini to generate target role skills
    if not required_skills:
        api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
        if api_key:
            client = genai.Client(api_key=api_key)
            prompt = f"List the 8 to 10 most critical hard technical skills required for a '{target_role}' role."
            try:
                response = client.models.generate_content(
                    model=config.MODEL_FLASH,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=SkillGapResult,
                        temperature=0.1
                    )
                )
                res_dict = json.loads(response.text)
                return res_dict
            except Exception as e:
                print(f"Gemini fallback gap analysis error: {e}")

        # Basic fallback list if LLM unavailable
        required_skills = ["Python", "SQL", "Git", "System Architecture", "Docker"]
        
    req_normalized = [normalize_skill(s) for s in required_skills]
    verified = [s for s in req_normalized if s in cand_set]
    missing = [s for s in req_normalized if s not in cand_set]
    
    match_pct = round((len(verified) / len(req_normalized)) * 100, 1) if req_normalized else 0.0
    
    return {
        "verified_skills": verified,
        "missing_skills": missing,
        "match_percentage": match_pct
    }
