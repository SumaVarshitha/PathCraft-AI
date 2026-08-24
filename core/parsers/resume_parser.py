import os
import json
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from core.state import ResumeSchema

def parse_resume(resume_text: str = "", pdf_bytes: Optional[bytes] = None) -> Dict[str, Any]:
    """
    Parses a candidate resume (either raw text or PDF bytes) using Gemini 2.5 Flash
    and returns a structured dictionary adhering to ResumeSchema.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set.")
    
    client = genai.Client(api_key=api_key)
    
    prompt = """
    You are an expert HR Tech & Engineering Recruiter Resume Parser.
    Extract the candidate's canonical name, job title, technical skills, total years of experience,
    education history, and a brief work summary from the provided resume.
    Standardize skill names (e.g. 'React.js' -> 'React', 'Python 3' -> 'Python').
    """
    
    contents = []
    if pdf_bytes:
        contents.append(
            types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf"
            )
        )
        contents.append(prompt)
    elif resume_text:
        contents.append(f"{prompt}\n\nRESUME CONTENT:\n{resume_text}")
    else:
        # Fallback if empty
        return ResumeSchema(
            candidate_name="Unknown",
            job_title="General Candidate",
            skills=[],
            years_experience=0.0,
            education=[],
            work_summary="No resume provided."
        ).model_dump()

    try:
        response = client.models.generate_content(
            model=config.MODEL_FLASH,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeSchema,
                temperature=0.1
            )
        )
        parsed_dict = json.loads(response.text)
        return parsed_dict
    except Exception as e:
        print(f"Error parsing resume with Gemini: {e}")
        # Return graceful fallback schema
        return ResumeSchema(
            candidate_name="Unknown",
            job_title="General Candidate",
            skills=[],
            years_experience=0.0,
            education=[],
            work_summary=f"Parsing error: {str(e)}"
        ).model_dump()
