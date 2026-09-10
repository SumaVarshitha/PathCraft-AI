import os
import requests
from typing import Dict, Any, Optional, List
import config
from core.adk_agent import ADKAgent

def _infer_repo_purpose(name: str, language: str, description: Optional[str] = None, topics: Optional[List[str]] = None) -> str:
    """Infers an informative technical purpose for a repository if description is missing."""
    if description and len(description.strip()) > 10:
        return description.strip()
    
    n_lower = name.lower().replace("-", " ").replace("_", " ")
    lang_str = f" using {language}" if language else ""
    
    if "pathcraft" in n_lower or "career" in n_lower or "copilot" in n_lower:
        return f"Enterprise autonomous multi-agent career intelligence platform with live market grounding and resume optimization{lang_str}."
    elif "multiagent" in n_lower or "adk" in n_lower or "agent" in n_lower:
        return f"Autonomous multi-agent system architecture and agentic workflow orchestration{lang_str}."
    elif "minikube" in n_lower or "k8s" in n_lower or "kubernetes" in n_lower:
        return f"Local Kubernetes cluster orchestration and containerized microservice web deployment{lang_str}."
    elif "action" in n_lower or "cicd" in n_lower or "pipeline" in n_lower:
        return f"Automated CI/CD workflows, build automation, and continuous delivery pipelines."
    elif "docker" in n_lower:
        return f"Containerization and automated Docker deployment configurations."
    elif "rag" in n_lower or "vector" in n_lower:
        return f"Retrieval-Augmented Generation (RAG) architecture and semantic vector search implementation."
    elif "llm" in n_lower or "genai" in n_lower:
        return f"Generative AI application with prompt engineering and LLM integrations{lang_str}."
    elif "api" in n_lower or "backend" in n_lower:
        return f"Backend REST API microservices architecture and database integration{lang_str}."
    elif "web" in n_lower or "app" in n_lower:
        return f"Fullstack responsive web application with frontend and backend services{lang_str}."
    elif "test" in n_lower:
        return f"Automated testing suite and benchmark validation workflows{lang_str}."
    else:
        clean_title = name.replace("-", " ").replace("_", " ").title()
        return f"Open-source software project implementing {clean_title} architecture and codebase{lang_str}."


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
            response = requests.get(api_url, headers=headers, timeout=5)
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
                    
                repo_name = repo.get("name", "")
                repo_highlights.append({
                    "name": repo_name,
                    "language": lang or "Code",
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "html_url": repo.get("html_url", f"https://github.com/{username}/{repo_name}"),
                    "topics": repo.get("topics", []),
                    "description": _infer_repo_purpose(
                        name=repo_name,
                        language=lang or "",
                        description=repo.get("description"),
                        topics=repo.get("topics", [])
                    )
                })
                
            return {
                "username": username,
                "detected_skills": list(detected_languages),
                "top_repos": repo_highlights[:6]
            }
        except Exception as e:
            print(f"[ADK 2.0 GitHub Inspector Error]: {e}", flush=True)
            return {"username": username, "detected_skills": [], "top_repos": []}
