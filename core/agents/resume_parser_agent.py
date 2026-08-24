import os
from typing import Dict, Any, Optional
from google.genai import types
import config
from core.adk_agent import ADKAgent
from core.state import ResumeSchema

class ResumeParserADKAgent(ADKAgent):
    """
    Google ADK 2.0 Resume Parser Agent
    Extracts canonical candidate metrics from PDF resumes or raw text using Gemini 2.5 Flash.
    """
    def __init__(self):
        super().__init__(
            name="ResumeParserADKAgent",
            instruction="""
            You are an expert HR Tech & Engineering Recruiter Resume Parser Agent.
            Extract the candidate's name, job title, technical skills, total years of experience,
            education, and work summary from the resume.
            Standardize skill names (e.g. 'React.js' -> 'React', 'Python 3' -> 'Python').
            """,
            model=config.MODEL_FLASH,
            output_schema=ResumeSchema,
            temperature=0.1
        )

    def parse(self, resume_text: str = "", pdf_bytes: Optional[bytes] = None) -> Dict[str, Any]:
        """Executes ADK 2.0 Resume Parsing."""
        contents = []
        if pdf_bytes:
            contents.append(
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf"
                )
            )
            contents.append("Parse this PDF resume.")
        elif resume_text:
            contents.append(f"Parse this text resume:\n{resume_text}")
        else:
            return ResumeSchema(
                candidate_name="Unknown",
                job_title="General Candidate",
                skills=[],
                years_experience=0.0,
                education=[],
                work_summary="No resume content provided."
            ).model_dump()

        try:
            result = self.execute(prompt_input=contents)
            return result
        except Exception as e:
            print(f"[ADK 2.0 Resume Parser Error]: {e}")
            return ResumeSchema(
                candidate_name="Unknown",
                job_title="General Candidate",
                skills=[],
                years_experience=0.0,
                education=[],
                work_summary=f"Parsing error: {str(e)}"
            ).model_dump()
