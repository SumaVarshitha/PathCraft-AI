import os
from typing import List, Dict, Any
from google.genai import types
import config
from core.adk_agent import ADKAgent, ADKTool
from core.mcp_tools.resource_mcp import ResourceMCPTool

class RAGCuratorADKAgent(ADKAgent):
    """
    Google ADK 2.0 RAG Learning & Resource Curator Agent
    Integrates with ResourceMCPTool (Google Books API, arXiv API) and Google Search Grounding
    to assemble rich multi-format learning packs for missing candidate skills.
    """
    def __init__(self):
        self.resource_mcp = ResourceMCPTool()
        super().__init__(
            name="RAGCuratorADKAgent",
            instruction="Curate authoritative multi-format learning resources (Books, Research Papers, Official Docs, Video Tutorials) with direct URLs.",
            model=config.MODEL_FLASH,
            tools=[ADKTool(name="google_search", tool_instance=types.Tool(google_search=types.GoogleSearch()))],
            temperature=0.2
        )

    def curate(self, missing_skills: List[str]) -> Dict[str, Any]:
        """
        Assembles comprehensive learning resources for the top missing skills:
        - Books (Google Books API)
        - Research Papers (arXiv API)
        - Official Documentation
        - Free Video Tutorials & Crash Courses (Google Search Grounded)
        """
        target_skills = missing_skills[:4] if missing_skills else ["System Design", "Cloud Architecture"]
        
        books: List[Dict[str, Any]] = []
        papers: List[Dict[str, Any]] = []
        docs: List[Dict[str, Any]] = []
        video_courses: List[Dict[str, Any]] = []

        # 1. Query Resource MCP for Books, Papers, and Documentation
        for skill in target_skills:
            # Query Books
            b_list = self.resource_mcp.search_books(skill, limit=1)
            books.extend(b_list)

            # Query Papers
            p_list = self.resource_mcp.search_papers(skill, limit=1)
            papers.extend(p_list)

            # Query Official Docs
            d = self.resource_mcp.resolve_official_docs(skill)
            docs.append(d)

            # Fallback Video Course entry
            clean_q = skill.replace(" ", "+")
            video_courses.append({
                "skill": skill,
                "title": f"Mastering {skill} - End-to-End Course",
                "platform": "YouTube (freeCodeCamp / Tech Lead)",
                "url": f"https://www.youtube.com/results?search_query={clean_q}+full+course",
                "cost": "Free",
                "duration": "3 - 5 Hours"
            })

        # 2. Enhance with Google Search Grounding for Live Verified Courses
        if self.client and missing_skills:
            try:
                skills_str = ", ".join(target_skills)
                grounding_prompt = f"""
                Find top-rated, 100% free video courses or interactive tutorials for these skills: {skills_str}.
                Provide direct links to freeCodeCamp, Coursera audit mode, YouTube, or official learning paths.
                Return ONLY a JSON array of objects with keys: skill, title, platform, url, cost, duration.
                """
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=grounding_prompt,
                    config=types.GenerateContentConfig(
                        tools=[types.Tool(google_search=types.GoogleSearch())],
                        temperature=0.2
                    )
                )
                text = response.text.strip()
                import json
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()
                if "[" in text and "]" in text:
                    text = text[text.find("["):text.rfind("]")+1]
                parsed_courses = json.loads(text)
                if isinstance(parsed_courses, list) and len(parsed_courses) > 0:
                    video_courses = parsed_courses
            except Exception as e:
                print(f"[RAG Curator Notice]: Live Search Grounding notice ({e})", flush=True)

        return {
            "courses": video_courses,
            "books": books,
            "papers": papers,
            "docs": docs
        }
