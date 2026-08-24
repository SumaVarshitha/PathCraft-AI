import os
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

def generate_portfolio_projects(missing_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
    """
    Generates tailored mini-project blueprints (directory structure, README, tech stack)
    designed to showcase missing skills on candidate's GitHub portfolio.
    """
    if not missing_skills:
        return []
        
    api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
    if not api_key:
        print("Warning: GOOGLE_API_KEY missing for Project Generator.")
        return []
        
    client = genai.Client(api_key=api_key)
    skills_str = ", ".join(missing_skills[:4])
    
    prompt = f"""
    You are a Senior Principal Engineer and Hiring Manager.
    Target Role: {target_role}
    Missing Candidate Skills: [{skills_str}]

    Create 1 production-grade mini-project blueprint specifically designed to showcase these missing skills on the candidate's GitHub portfolio to hiring managers.

    Return a JSON array containing 1 project blueprint object with the exact structure:
    [
      {{
        "project_title": "Descriptive, professional repository name (e.g. real-time-spark-etl-pipeline)",
        "target_skills": ["Skill1", "Skill2"],
        "overview": "Clear 2-sentence explanation of what the project builds and why it proves senior competence.",
        "folder_structure": [
          "src/main.py",
          "src/config.py",
          "docker-compose.yml",
          "Dockerfile",
          "README.md",
          "requirements.txt"
        ],
        "readme_spec": "# Project Name\\n\\n## Architecture Overview\\n...\\n\\n## Tech Stack\\n- Skill1\\n- Skill2\\n\\n## Key Features\\n1. Feature 1\\n2. Feature 2"
      }}
    ]
    """
    
    try:
        response = client.models.generate_content(
            model=config.MODEL_PRO,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            )
        )
        text = response.text.strip()
        projects = json.loads(text)
        return projects if isinstance(projects, list) else []
        
    except Exception as e:
        print(f"Error generating portfolio projects with Gemini Pro: {e}")
        # Fallback project blueprint
        return [{
            "project_title": f"{target_role.lower().replace(' ', '-')}-proof-of-concept",
            "target_skills": missing_skills[:2],
            "overview": f"A comprehensive project integrating {', '.join(missing_skills[:2])} for enterprise workloads.",
            "folder_structure": ["src/", "tests/", "Dockerfile", "README.md"],
            "readme_spec": f"# {target_role} Showcase Project\n\nBuilds end-to-end functionality using {', '.join(missing_skills[:2])}."
        }]
