from typing import List, Optional
import config
from core.adk_agent import ADKAgent

SYNONYM_MAP = {
    "py": "Python", "python3": "Python", "python 3": "Python",
    "js": "JavaScript", "javascript": "JavaScript", "ecmascript": "JavaScript",
    "ts": "TypeScript", "typescript": "TypeScript",
    "reactjs": "React", "react.js": "React", "react": "React",
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js", "express": "Node.js",
    "sql": "SQL", "mysql": "SQL", "mssql": "SQL", "plsql": "SQL",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL", "pg": "PostgreSQL",
    "mongo": "MongoDB", "mongodb": "MongoDB",
    "spark": "Apache Spark", "apache spark": "Apache Spark", "pyspark": "PySpark",
    "k8s": "Kubernetes", "kubernetes": "Kubernetes",
    "docker": "Docker", "dockerfile": "Docker", "containerization": "Docker",
    "gcp": "Google Cloud Platform", "google cloud": "Google Cloud Platform",
    "aws": "AWS", "amazon web services": "AWS",
    "azure": "Azure", "microsoft azure": "Azure",
    "ml": "Machine Learning", "machine learning": "Machine Learning",
    "ai": "Artificial Intelligence", "artificial intelligence": "Artificial Intelligence",
    "deep learning": "Deep Learning", "dl": "Deep Learning",
    "llm": "LLMs", "llms": "LLMs", "large language models": "LLMs",
    "genai": "Generative AI", "generative ai": "Generative AI",
    "nlp": "NLP", "natural language processing": "NLP",
    "tensorflow": "TensorFlow", "tf": "TensorFlow",
    "pytorch": "PyTorch", "torch": "PyTorch",
    "scikit-learn": "Scikit-Learn", "sklearn": "Scikit-Learn",
    "pandas": "Pandas", "numpy": "NumPy",
    "langchain": "LangChain",
    "ci/cd": "CI/CD", "cicd": "CI/CD",
    "terraform": "Terraform",
    "airflow": "Apache Airflow", "apache airflow": "Apache Airflow",
    "kafka": "Apache Kafka", "apache kafka": "Apache Kafka",
    "bigquery": "BigQuery", "big query": "BigQuery",
    "etl": "ETL Pipelines", "etl pipelines": "ETL Pipelines",
    "data warehouse": "Data Warehousing", "data warehousing": "Data Warehousing",
    "git": "Git", "github": "Git",
    "linux": "Linux", "bash": "Bash",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
    "rest": "REST APIs", "rest api": "REST APIs", "rest apis": "REST APIs"
}

EQUIVALENT_GROUPS = [
    {"Machine Learning", "Deep Learning", "Artificial Intelligence", "AI/ML"},
    {"AWS", "Google Cloud Platform", "Azure", "Cloud"},
    {"REST APIs", "FastAPI", "Flask", "APIs"},
    {"Docker", "Containerization", "Kubernetes"},
    {"CI/CD", "GitHub Actions", "Jenkins"},
    {"Git", "GitHub", "Version Control"},
    {"SQL", "PostgreSQL", "MySQL", "BigQuery"},
    {"LLMs", "Generative AI", "LangChain", "Prompt Engineering"},
    {"PyTorch", "TensorFlow", "Keras"},
    {"Apache Spark", "PySpark", "ETL Pipelines"}
]

def normalize_skill_name(skill: str) -> str:
    cleaned = skill.strip().lower()
    return SYNONYM_MAP.get(cleaned, skill.strip().title())

def fuzzy_skill_match(candidate_skill: str, required_skill: str) -> bool:
    c = normalize_skill_name(candidate_skill).lower()
    r = normalize_skill_name(required_skill).lower()
    if c == r or c in r or r in c:
        return True
    for group in EQUIVALENT_GROUPS:
        group_lower = {g.lower() for g in group}
        if c in group_lower and r in group_lower:
            return True
    return False

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
