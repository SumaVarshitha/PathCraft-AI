from typing import List, Optional
import config
from core.adk_agent import ADKAgent

SYNONYM_MAP = {
    "reactjs": "React", "react.js": "React", "react": "React",
    "py": "Python", "python3": "Python", "pyspark": "PySpark",
    "apache spark": "Apache Spark", "spark": "Apache Spark",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "k8s": "Kubernetes", "gcp": "Google Cloud Platform",
    "google cloud": "Google Cloud Platform", "aws": "Amazon Web Services",
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js"
}

def normalize_skill_name(skill: str) -> str:
    cleaned = skill.strip().lower()
    return SYNONYM_MAP.get(cleaned, skill.strip())

class SkillNormalizerADKAgent(ADKAgent):
    """
    Google ADK 2.0 Skill Normalizer Agent
    Merges and normalizes candidate skill metrics from all active input sources.
    """
    def __init__(self):
        super().__init__(
            name="SkillNormalizerADKAgent",
            instruction="Normalize and deduplicate candidate skills into canonical tech stack terms.",
            model=config.MODEL_FLASH
        )

    def normalize(self, resume_skills: List[str], github_skills: Optional[List[str]] = None) -> List[str]:
        all_skills = list(resume_skills)
        if github_skills:
            all_skills.extend(github_skills)
            
        normalized_set = set()
        for s in all_skills:
            if s and isinstance(s, str):
                normalized_set.add(normalize_skill_name(s))
                
        return sorted(list(normalized_set))
