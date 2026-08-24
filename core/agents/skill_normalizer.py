from typing import List, Dict, Any, Optional

# Canonical Synonym Map
SYNONYM_MAP = {
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "py": "Python",
    "python3": "Python",
    "pyspark": "PySpark",
    "apache spark": "Apache Spark",
    "spark": "Apache Spark",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "k8s": "Kubernetes",
    "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform",
    "aws": "Amazon Web Services",
    "amazon web services": "Amazon Web Services",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
}

def normalize_skill(skill_name: str) -> str:
    """Standardize skill variants to canonical casing/naming."""
    cleaned = skill_name.strip().lower()
    return SYNONYM_MAP.get(cleaned, skill_name.strip())

def process_and_normalize_profile(
    resume_skills: List[str],
    github_skills: Optional[List[str]] = None,
    linkedin_skills: Optional[List[str]] = None
) -> List[str]:
    """
    Merges skills from all active candidate input sources and returns a deduplicated,
    normalized list of candidate skills.
    """
    all_raw_skills = list(resume_skills)
    if github_skills:
        all_raw_skills.extend(github_skills)
    if linkedin_skills:
        all_raw_skills.extend(linkedin_skills)
        
    normalized_set = set()
    for s in all_raw_skills:
        if s and isinstance(s, str):
            norm = normalize_skill(s)
            normalized_set.add(norm)
            
    return sorted(list(normalized_set))
