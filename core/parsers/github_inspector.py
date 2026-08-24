import requests
import json
from typing import Dict, Any, List, Optional

def inspect_github_user(github_url_or_username: str, github_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Inspects a candidate's public GitHub profile and top repositories using the GitHub REST API.
    Extracts primary languages, repository topics, and overall public repo statistics.
    """
    # Clean username from URL if necessary
    username = github_url_or_username.strip().rstrip('/')
    if 'github.com/' in username:
        username = username.split('github.com/')[-1]
        
    if not username:
        return {"username": "", "detected_skills": [], "top_repos": [], "total_public_repos": 0}
        
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        
    # Fetch user repos
    api_url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"GitHub API Error ({response.status_code}): {response.text}")
            return {"username": username, "detected_skills": [], "top_repos": [], "total_public_repos": 0}
            
        repos = response.json()
        detected_languages = set()
        repo_highlights = []
        
        for repo in repos:
            if repo.get("fork"):
                continue  # Skip forked repositories
                
            lang = repo.get("language")
            if lang:
                detected_languages.add(lang)
                
            repo_highlights.append({
                "name": repo.get("name"),
                "language": lang,
                "stars": repo.get("stargazers_count", 0),
                "description": repo.get("description", ""),
                "topics": repo.get("topics", [])
            })
            
        return {
            "username": username,
            "detected_skills": list(detected_languages),
            "top_repos": repo_highlights[:5],
            "total_public_repos": len(repos)
        }
        
    except Exception as e:
        print(f"Exception inspecting GitHub user: {e}")
        return {"username": username, "detected_skills": [], "top_repos": [], "total_public_repos": 0}
