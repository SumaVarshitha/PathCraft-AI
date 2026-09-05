import os
from typing import List, Dict, Any
import config
from core.adk_agent import ADKAgent
from core.mcp_tools.github_mcp import GitHubMCPTool

class ProjectGeneratorADKAgent(ADKAgent):
    """
    Google ADK 2.0 GitHub Project Discovery Agent
    Discovers real, production-grade public GitHub repositories and open-source starter projects
    that implement the candidate's missing skills so they can study real codebases and build their own.
    """
    def __init__(self):
        self.github_mcp = GitHubMCPTool()
        super().__init__(
            name="ProjectGeneratorADKAgent",
            instruction="Discover real, high-quality public GitHub reference projects matching target skills.",
            model=config.MODEL_PRO,
            temperature=0.2
        )

    def generate(self, missing_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
        """
        Queries GitHub API via GitHubMCPTool to discover real public reference repositories
        covering the candidate's identified skill gaps.
        """
        target_skills = missing_skills[:4] if missing_skills else ["Data Engineering", "Microservices"]
        discovered_projects: List[Dict[str, Any]] = []

        for skill in target_skills:
            repos = self.github_mcp.search_public_repositories(skill=skill, min_stars=50, limit=2)
            for r in repos:
                discovered_projects.append({
                    "title": f"Production {skill} Project ({r.get('name')})",
                    "target_skills": [skill, r.get("language", "Python")],
                    "overview": r.get("description", "Open-source reference implementation."),
                    "html_url": r.get("html_url", "https://github.com"),
                    "stars": r.get("stars", 100),
                    "forks": r.get("forks", 20),
                    "language": r.get("language", "Python"),
                    "topics": r.get("topics", []),
                    "folder_structure": [
                        "src/",
                        "├── core/",
                        "├── pipelines/",
                        "├── tests/",
                        "Dockerfile",
                        "README.md",
                        "requirements.txt"
                    ],
                    "readme_template": f"# {r.get('name')}\n\n{r.get('description')}\n\n## Direct GitHub URL\n{r.get('html_url')}\n\n## Key Tech Stack\n- {skill}\n- {r.get('language')}\n"
                })

        return discovered_projects
