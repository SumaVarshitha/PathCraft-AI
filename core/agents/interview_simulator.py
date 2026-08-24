import os
from typing import List, Dict, Any
from google import genai
from google.genai import types

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

def generate_interview_question(target_role: str, missing_skills: List[str], chat_history: List[Dict[str, str]]) -> str:
    """
    Generates the next technical interview question targeting missing skills.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
    if not api_key:
        return "Can you explain how you would approach learning and applying your top missing technical skills in a production environment?"
        
    client = genai.Client(api_key=api_key)
    skills_str = ", ".join(missing_skills[:3]) if missing_skills else "software engineering fundamentals"
    
    prompt = f"""
    You are an expert Technical Interviewer for a '{target_role}' position.
    The candidate is working on strengthening the following skills: [{skills_str}].

    Chat History so far:
    {chat_history}

    Ask the candidate ONE concise, realistic, technical interview question testing their knowledge or conceptual understanding of one of these skills: [{skills_str}].
    Do not add conversational fluff. Ask a direct, scenario-based or conceptual technical interview question.
    """
    
    try:
        response = client.models.generate_content(
            model=config.MODEL_FLASH,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3)
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating interview question: {e}")
        return f"How does {missing_skills[0] if missing_skills else 'your primary stack'} handle scalability and error handling under heavy load?"

def evaluate_interview_response(question: str, candidate_answer: str, target_role: str) -> Dict[str, Any]:
    """
    Evaluates the candidate's answer to an interview question and provides feedback & score.
    """
    api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
    if not api_key:
        return {
            "score": 70,
            "feedback": "Answer recorded. (API key needed for live AI scoring).",
            "key_takeaway": "Good general understanding."
        }
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Target Role: {target_role}
    Question Asked: "{question}"
    Candidate Answer: "{candidate_answer}"

    Evaluate the technical accuracy, depth, and clarity of the candidate's answer.
    Return a JSON object with:
    {{
      "score": 0 to 100 integer,
      "feedback": "2-3 sentences explaining strengths and what was missing in their answer",
      "key_takeaway": "1 clear sentence of improvement advice"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=config.MODEL_FLASH,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        import json
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error evaluating interview response: {e}")
        return {
            "score": 75,
            "feedback": "Valid effort! Ensure you mention specific technical mechanisms and production considerations.",
            "key_takeaway": "Focus on quantitative metrics and specific tool mechanisms in your answers."
        }
