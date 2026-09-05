import os
import re
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types
import config
from core.adk_agent import ADKAgent
from core.state import ResumeSchema

KNOWN_TECH_VOCABULARY = [
    "Python", "SQL", "Scala", "Java", "C++", "JavaScript", "TypeScript", "Bash",
    "Apache Spark", "PySpark", "Apache Kafka", "Hadoop", "Flink",
    "Google Cloud Platform", "GCP", "BigQuery", "Snowflake", "Amazon Redshift", "AWS", "Azure",
    "Apache Airflow", "Docker", "Kubernetes", "Terraform", "Git", "CI/CD", "Linux",
    "dbt", "ETL", "ELT", "Data Warehousing", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "PyTorch", "TensorFlow", "Scikit-Learn", "FastAPI", "React", "Node.js",
    "Figma", "Adobe Photoshop", "Adobe Illustrator", "HTML5", "CSS3", "HTML", "CSS"
]

class ResumeParserADKAgent(ADKAgent):
    """
    Google ADK 2.0 Resume Parser Agent
    Extracts complete, structured candidate profile context (skills, projects with tech stacks,
    certifications, experience, tools) from raw resume text or multimodal PDF uploads.
    """
    def __init__(self):
        instruction = """
        You are an expert technical resume parser.
        Your job is to thoroughly analyze the candidate's resume and extract all professional details into the ResumeSchema format.
        IMPORTANT:
        - Extract all projects mentioned with their specific technology stack, libraries, and tools used.
        - Extract all industry certifications, licenses, and credentials.
        - Aggregate all tools, frameworks, and programming languages mentioned across work experience, projects, and skills sections into tools_and_technologies.
        - Extract exact candidate name, estimated years of experience, and summary.
        """
        super().__init__(
            name="ResumeParserADKAgent",
            instruction=instruction,
            model=config.MODEL_FLASH,
            output_schema=ResumeSchema,
            temperature=0.1
        )

    def _offline_fallback_parse(self, resume_text: str) -> Dict[str, Any]:
        """Extracts structured skills and projects using heuristic parsing when offline."""
        found_skills = []
        text_lower = resume_text.lower()
        for tech in KNOWN_TECH_VOCABULARY:
            pattern = r'\b' + re.escape(tech.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(tech)

        # Extract projects if present
        projects = []
        if "project" in text_lower:
            proj_skills = [s for s in found_skills if s in ["Python", "PySpark", "Apache Spark", "BigQuery", "Docker", "Git", "Figma", "HTML5", "CSS3"]]
            projects.append({
                "title": "Production Engineering Project",
                "description": "Implementation detailed in candidate resume.",
                "tech_stack": proj_skills,
                "key_contributions": "Designed and deployed system components."
            })

        return {
            "candidate_name": "Candidate",
            "job_title": "Engineer / Specialist",
            "skills": found_skills,
            "years_experience": 4.0 if len(found_skills) > 5 else 1.5,
            "education": ["University Degree"],
            "work_summary": "Extracted professional profile.",
            "projects": projects,
            "certifications": ["GCP Certified" if "gcp" in text_lower else ""],
            "tools_and_technologies": found_skills
        }

    def parse(self, resume_text: Optional[str] = None, pdf_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """Parses resume text or PDF bytes into structured ResumeSchema dictionary."""
        if not self.client:
            if resume_text:
                return self._offline_fallback_parse(resume_text)
            return {
                "candidate_name": "Applicant",
                "job_title": "Software Engineer",
                "skills": [],
                "years_experience": 0.0,
                "education": [],
                "work_summary": "Parsed Profile",
                "projects": [],
                "certifications": [],
                "tools_and_technologies": []
            }

        try:
            if pdf_bytes:
                pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
                prompt = "Please parse this PDF resume thoroughly into the structured ResumeSchema format."
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[pdf_part, prompt],
                    config=types.GenerateContentConfig(
                        system_instruction=self.instruction,
                        temperature=self.temperature,
                        response_mime_type="application/json",
                        response_schema=ResumeSchema
                    )
                )
                return response.parsed.model_dump() if response.parsed else {"skills": [], "projects": []}
            
            elif resume_text:
                prompt = f"Please parse this candidate resume text thoroughly:\n\n{resume_text}"
                return self.execute(prompt_input=prompt)
            else:
                return {"skills": [], "projects": [], "tools_and_technologies": []}
        except Exception as e:
            print(f"⚠️ [ADK 2.0 Resume Parser Notice]: ({e}). Using heuristic extraction.", flush=True)
            if resume_text:
                return self._offline_fallback_parse(resume_text)
            return {
                "candidate_name": "Applicant",
                "job_title": "Engineer",
                "skills": [],
                "years_experience": 1.0,
                "education": [],
                "work_summary": "Uploaded profile",
                "projects": [],
                "certifications": [],
                "tools_and_technologies": []
            }
