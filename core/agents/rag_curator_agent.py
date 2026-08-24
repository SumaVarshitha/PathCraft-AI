import json
from typing import List, Dict, Any
from google.genai import types
import config
from core.adk_agent import ADKAgent, ADKTool

class RAGCuratorADKAgent(ADKAgent):
    """
    Google ADK 2.0 RAG Resource Curator Agent
    Equipped with Google Search Tool for live grounding, dynamically fetching $0 free YouTube courses,
    official documentation, and free audit tutorials for missing candidate skills.
    """
    def __init__(self):
        # Bind Google Search Tool to ADK Agent
        search_tool = ADKTool(
            name="google_search",
            description="Live Google Search Tool for retrieving real-time learning links.",
            tool_object=types.Tool(google_search=types.GoogleSearch())
        )
        
        super().__init__(
            name="RAGCuratorADKAgent",
            instruction="""
            You are an expert Technical Education Curator Agent.
            Search Google for the missing technical skills and recommend 1 high-quality, 100% FREE ($0) learning resource per skill.
            Prioritize:
            1. Top-rated YouTube tutorials / playlists (e.g. freeCodeCamp, StatQuest)
            2. Official documentation guides (e.g., docs.docker.com, spark.apache.org)
            3. Free audit Coursera / edX courses.

            Return ONLY a valid JSON array of objects:
            [
              {
                "skill": "Skill Name",
                "title": "Clear descriptive title of course or guide",
                "platform": "YouTube / Official Docs / Coursera",
                "url": "Valid working HTTP/HTTPS URL",
                "cost": "Free",
                "duration": "Estimated time e.g. 2 Hours, Self-paced"
              }
            ]
            """,
            model=config.MODEL_FLASH,
            tools=[search_tool],
            temperature=0.2
        )

    def curate(self, missing_skills: List[str]) -> List[Dict[str, Any]]:
        if not missing_skills:
            return []
            
        skills_str = ", ".join(missing_skills[:5])
        prompt = f"Recommend free ($0) resources for these missing skills: [{skills_str}]."
        
        try:
            raw_output = self.execute(prompt_input=prompt)
            if isinstance(raw_output, list):
                return raw_output
            text = str(raw_output).strip()
            if "```json" in text:
                text = text.split("```json")[-1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            curated = json.loads(text)
            return curated if isinstance(curated, list) else []
        except Exception as e:
            print(f"[ADK 2.0 RAG Curator Error]: {e}")
            fallback = []
            for s in missing_skills[:4]:
                fallback.append({
                    "skill": s,
                    "title": f"Complete {s} Crash Course for Beginners",
                    "platform": "YouTube (freeCodeCamp)",
                    "url": f"https://www.youtube.com/results?search_query={s}+crash+course",
                    "cost": "Free",
                    "duration": "2 - 4 Hours"
                })
            return fallback
