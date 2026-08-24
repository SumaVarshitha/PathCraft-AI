import os
import json
from typing import List, Dict, Any
from google import genai
from google.genai import types

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

def curate_learning_resources(missing_skills: List[str]) -> List[Dict[str, Any]]:
    """
    Dynamically fetches top free ($0) learning resources (YouTube tutorials, official docs, free courses)
    for missing skills using Gemini 2.5 with search grounding.
    """
    if not missing_skills:
        return []
        
    api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
    if not api_key:
        print("Warning: GOOGLE_API_KEY missing for RAG Curator.")
        return []
        
    client = genai.Client(api_key=api_key)
    skills_str = ", ".join(missing_skills[:5])  # Focus on top 5 missing skills
    
    prompt = f"""
    You are an expert technical education curator.
    For each of the following missing technical skills: [{skills_str}], recommend 1 high-quality, 100% FREE ($0) learning resource.
    Prioritize:
    1. Top-rated YouTube tutorials / playlists (e.g. freeCodeCamp, StatQuest, TechWorld with Nana)
    2. Official documentation guides (e.g., docs.docker.com, spark.apache.org)
    3. Free audit Coursera / edX courses.

    Return a JSON array of objects with the exact schema:
    [
      {{
        "skill": "Skill Name",
        "title": "Clear descriptive title of course or guide",
        "platform": "YouTube / Official Docs / Coursera",
        "url": "Valid working HTTP/HTTPS URL",
        "cost": "Free",
        "duration": "Estimated completion time e.g. 2 Hours, Self-paced"
      }}
    ]
    """
    
    try:
        response = client.models.generate_content(
            model=config.MODEL_FLASH,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                tools=[types.Tool(google_search=types.GoogleSearch())] # Live Search Grounding!
            )
        )
        
        # Parse output text as JSON array
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[-1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        curated_list = json.loads(text)
        return curated_list if isinstance(curated_list, list) else []
        
    except Exception as e:
        print(f"Error curating live resources: {e}")
        # Fallback structured placeholder if search fails or hits quota
        fallback_list = []
        for s in missing_skills[:4]:
            fallback_list.append({
                "skill": s,
                "title": f"Complete {s} Crash Course for Beginners",
                "platform": "YouTube (freeCodeCamp)",
                "url": f"https://www.youtube.com/results?search_query={s}+crash+course",
                "cost": "Free",
                "duration": "2 - 4 Hours"
            })
        return fallback_list
