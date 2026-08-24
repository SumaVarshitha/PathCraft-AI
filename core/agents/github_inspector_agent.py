import requests
from typing import Dict, Any, Optional
import config
from core.adk_agent import ADKAgent

class GitHubInspectorADKAgent(ADKAgent):
    """
    Google ADK 2.0 GitHub Inspector Agent
    Scrapes user's GitHub public repositories to verify coding languages and project topics.
    """
    def __init__(self):
        super().__init__(
            name="GitHubInspectorADKAgent",
            instruction="Inspect candidate public GitHub repositories and extract verified technical stack signals.",
            model=config.MODEL_FLASH
        )

    def inspect(self, github_url_or_username: str, github_token: Optional[str] = None) -> Dict[str, Any]:
        """Executes GitHub Inspection."""
        username = github_url_or_username.strip().rstrip('/')
        if 'github.com/' in username:
            username = username.split('github.com/')[-1]
            
        if not username:
            return {"username": "", "detected_skills": [], "top_repos": []}
            
        headers = {"Accept": "application/vnd.github.v3+json"}
        token = github_token or config.GITHUB_TOKEN
        if token:
            headers["Authorization"] = f"token {token}"
            
        api_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10"
        
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"username": username, "detected_skills": [], "top_repos": []}
                
            repos = response.json()
            detected_languages = set()
            repo_highlights = []
            
            for repo in repos:
                if repo.get("fork"):
                    continue
                lang = repo.get("language")
                if lang:
                    detected_languages.add(lang)
                repo_highlights.append({
                    "name": repo.get("name"),
                    "language": lang,
                    "stars": repo.get("stargazers_count", 0),
                    "description": repo.get("description", "")
                })
                
            return {
                "username": username,
                "detected_skills": list(detected_languages),
                "top_repos": repo_highlights[:5]
            }
        except Exception as e:
            print(f"[ADK 2.0 GitHub Inspector Error]: {e}")
            return {"username": username, "detected_skills": [], "top_repos": []}
