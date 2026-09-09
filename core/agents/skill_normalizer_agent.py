import re
from typing import List, Optional, Set
import config
from core.adk_agent import ADKAgent

SYNONYM_MAP = {
    "py": "Python", "python3": "Python", "python 3": "Python",
    "js": "JavaScript", "javascript": "JavaScript", "ecmascript": "JavaScript",
    "ts": "TypeScript", "typescript": "TypeScript",
    "reactjs": "React", "react.js": "React", "react": "React",
    "node": "Node.js", "nodejs": "Node.js", "node.js": "Node.js", "express": "Node.js", "express.js": "Node.js",
    "sql": "SQL", "mysql": "MySQL", "mssql": "Microsoft SQL Server", "plsql": "PL/SQL",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL", "pg": "PostgreSQL",
    "mongo": "MongoDB", "mongodb": "MongoDB",
    "spark": "Apache Spark", "apache spark": "Apache Spark", "pyspark": "PySpark",
    "k8s": "Kubernetes", "kubernetes": "Kubernetes",
    "docker": "Docker", "dockerfile": "Docker", "containerization": "Containerization",
    "gcp": "Google Cloud Platform", "google cloud": "Google Cloud Platform", "google cloud platform": "Google Cloud Platform",
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
    "langchain": "LangChain", "llamaindex": "LlamaIndex",
    "ci/cd": "CI/CD", "cicd": "CI/CD", "ci cd": "CI/CD",
    "terraform": "Terraform",
    "airflow": "Apache Airflow", "apache airflow": "Apache Airflow",
    "kafka": "Apache Kafka", "apache kafka": "Apache Kafka",
    "bigquery": "BigQuery", "big query": "BigQuery",
    "snowflake": "Snowflake",
    "dbt": "dbt",
    "etl": "ETL Pipelines", "etl pipelines": "ETL Pipelines", "data pipelines": "ETL Pipelines",
    "data warehouse": "Data Warehousing", "data warehousing": "Data Warehousing",
    "git": "Git", "github": "Git", "gitlab": "Git",
    "linux": "Linux", "bash": "Bash", "shell scripting": "Bash",
    "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
    "rest": "REST APIs", "rest api": "REST APIs", "rest apis": "REST APIs", "restful apis": "REST APIs",
    "graphql": "GraphQL",
    "system design": "System Design", "system architecture": "System Architecture",
    "microservices": "Microservices"
}

# Strict 1-to-1 equivalent aliases (interchangeable terms)
STRICT_EQUIVALENTS = [
    {"Python", "Python3", "Python 3"},
    {"JavaScript", "JS", "ECMAScript"},
    {"TypeScript", "TS"},
    {"PyTorch", "Torch"},
    {"PostgreSQL", "Postgres"},
    {"Apache Spark", "Spark"},
    {"Apache Kafka", "Kafka"},
    {"Apache Airflow", "Airflow"},
    {"Google Cloud Platform", "GCP", "Google Cloud"},
    {"Amazon Web Services", "AWS"},
    {"Microsoft Azure", "Azure"},
    {"ETL Pipelines", "ETL", "Data Pipelines"},
    {"REST APIs", "RESTful APIs", "REST API"},
    {"CI/CD", "Continuous Integration"}
]

def normalize_skill_name(skill: str) -> str:
    """Normalizes a raw skill string into canonical representation."""
    cleaned = skill.strip().lower()
    return SYNONYM_MAP.get(cleaned, skill.strip())

def token_exact_match(candidate_text: str, required_skill: str) -> bool:
    """
    Checks if required_skill is present as an exact whole-word token in candidate_text.
    Prevents 'Java' from matching 'JavaScript', or 'C' from matching 'CI/CD'.
    """
    c_norm = normalize_skill_name(candidate_text).strip().lower()
    r_norm = normalize_skill_name(required_skill).strip().lower()

    if c_norm == r_norm:
        return True

    # Check strict alias groups
    for group in STRICT_EQUIVALENTS:
        group_lower = {g.lower() for g in group}
        if c_norm in group_lower and r_norm in group_lower:
            return True

    # Check whole word token regex
    pattern = r'\b' + re.escape(r_norm) + r'\b'
    if re.search(pattern, c_norm):
        return True

    return False

def fuzzy_skill_match(candidate_skill: str, required_skill: str) -> bool:
    """Precise token-aware matching preventing false-positive substring matches."""
    return token_exact_match(candidate_skill, required_skill)

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
            
        normalized_set: Set[str] = set()
        for s in all_skills:
            if s and isinstance(s, str) and len(s.strip()) > 0:
                normalized_set.add(normalize_skill_name(s))
                
        return sorted(list(normalized_set))
