from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field

class ProjectItem(BaseModel):
    title: str = Field(description="Title or name of the project")
    description: str = Field(description="Overview of the project and what was built")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies, libraries, and tools used in the project")
    key_contributions: Optional[str] = Field(default="", description="Key accomplishments or features developed")

class ResumeSchema(BaseModel):
    candidate_name: str = Field(description="Full name of candidate")
    job_title: str = Field(description="Current or most recent target job title")
    skills: List[str] = Field(description="List of core technical and soft skills extracted from skills section")
    years_experience: float = Field(description="Total estimated years of relevant professional experience")
    education: List[str] = Field(description="List of degrees, universities, or academic qualifications")
    work_summary: str = Field(description="Brief 2-3 sentence executive professional summary")
    projects: List[ProjectItem] = Field(default_factory=list, description="Academic, personal, or professional projects detailed in resume")
    certifications: List[str] = Field(default_factory=list, description="Industry certifications or licenses (e.g. AWS, GCP, CKA)")
    tools_and_technologies: List[str] = Field(default_factory=list, description="All tools, libraries, databases, and frameworks mentioned across the resume")

class SemanticMatchItem(BaseModel):
    required_skill: str = Field(description="The target job role required skill")
    matched_candidate_skill: Optional[str] = Field(default=None, description="The candidate skill or project tech that semantically matched")
    similarity_score: float = Field(description="Semantic cosine similarity score between 0.0 and 1.0")
    is_match: bool = Field(description="True if similarity meets or exceeds matching threshold")
    evidence_source: str = Field(default="Skills Section", description="Source where skill/context was found: Skills Section, Projects, or Work Experience")

class SkillGapResult(BaseModel):
    verified_skills: List[str] = Field(description="List of skills successfully matched in candidate profile")
    missing_skills: List[str] = Field(description="List of required skills missing from candidate profile")
    match_percentage: float = Field(description="Overall candidate profile match score from 0.0 to 100.0")
    semantic_matches: List[SemanticMatchItem] = Field(default_factory=list, description="Granular semantic matching breakdown for each required skill")
    analysis_method: str = Field(default="Hybrid Consensus & Gemini Embeddings", description="Method used to fetch and evaluate requirements")

class EvaluationResult(BaseModel):
    score: int = Field(description="Score between 0 and 100")
    feedback: str = Field(description="Constructive evaluation feedback explaining strengths and gaps")
    key_takeaway: str = Field(description="1 actionable improvement recommendation for future interviews")

class ADKState(TypedDict):
    resume_bytes: Optional[bytes]
    resume_text: str
    target_role: str
    github_url: Optional[str]
    linkedin_url: Optional[str]
    resume_data: Optional[Dict[str, Any]]
    github_data: Optional[Dict[str, Any]]
    linkedin_data: Optional[Dict[str, Any]]
    unified_skills: List[str]
    skills_gap: List[str]
    match_score: float
    analysis_method: str
    semantic_matches: List[Dict[str, Any]]
    curated_courses: List[Dict[str, Any]]
    learning_resources: Dict[str, Any]
    project_blueprints: List[Dict[str, Any]]
    github_projects: List[Dict[str, Any]]
    live_jobs: List[Dict[str, Any]]
    interview_history: List[Dict[str, Any]]
    ats_audit: Optional[Dict[str, Any]]
