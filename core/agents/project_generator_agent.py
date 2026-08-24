import json
from typing import List, Dict, Any
import config
from core.adk_agent import ADKAgent

class ProjectGeneratorADKAgent(ADKAgent):
    """
    Google ADK 2.0 Project Generator Agent
    Powered by Gemini 2.5 Pro to design customized production GitHub mini-project blueprints.
    """
    def __init__(self):
        super().__init__(
            name="ProjectGeneratorADKAgent",
            instruction="""
            You are a Senior Principal Engineer and Hiring Manager Agent.
            Design 1 production-grade mini-project blueprint specifically tailored to showcase missing candidate skills on GitHub.
            Return a JSON array containing 1 object:
            [
              {
                "project_title": "Descriptive repository name (e.g. real-time-spark-etl-pipeline)",
                "target_skills": ["Skill1", "Skill2"],
                "overview": "Clear 2-sentence explanation of what the project builds and why it proves competence.",
                "folder_structure": ["src/main.py", "docker-compose.yml", "README.md"],
                "readme_spec": "# Project Name\\n\\n## Architecture\\n...\\n\\n## Tech Stack\\n- Skill1"
              }
            ]
            """,
            model=config.MODEL_PRO, # Deep reasoning with Gemini 2.5 Pro!
            temperature=0.2
        )

    def generate(self, missing_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
        if not missing_skills:
            return []
            
        skills_str = ", ".join(missing_skills[:4])
        prompt = f"Target Role: {target_role}\nMissing Skills: [{skills_str}]"
        
        try:
            raw_output = self.execute(prompt_input=prompt)
            if isinstance(raw_output, list):
                return raw_output
            text = str(raw_output).strip()
            if "```json" in text:
                text = text.split("```json")[-1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            projects = json.loads(text)
            return projects if isinstance(projects, list) else []
        except Exception as e:
            print(f"[ADK 2.0 Project Generator Error]: {e}")
            return [{
                "project_title": f"{target_role.lower().replace(' ', '-')}-proof-of-concept",
                "target_skills": missing_skills[:2],
                "overview": f"A comprehensive project integrating {', '.join(missing_skills[:2])}.",
                "folder_structure": ["src/", "tests/", "Dockerfile", "README.md"],
                "readme_spec": f"# {target_role} Project\n\nBuilds end-to-end functionality using {', '.join(missing_skills[:2])}."
            }]
