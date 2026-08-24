from typing import TypedDict, Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Google ADK 2.0 Pydantic Output Schemas
# ---------------------------------------------------------------------------
class ResumeSchema(BaseModel):
    candidate_name: str = Field(description="Full name of candidate, or Unknown if not found")
    job_title: str = Field(description="Primary job title or domain role of candidate")
    skills: List[str] = Field(default_factory=list, description="List of technical & domain skills extracted")
    years_experience: float = Field(default=0.0, description="Estimated total years of relevant work experience")
    education: List[str] = Field(default_factory=list, description="Degrees, certifications, or educational background")
    work_summary: str = Field(default="", description="Brief summary of candidate's career highlights")

class SkillGapResult(BaseModel):
    verified_skills: List[str] = Field(default_factory=list, description="Skills verified across inputs")
    missing_skills: List[str] = Field(default_factory=list, description="Skills required for target role but missing")
    match_percentage: float = Field(default=0.0, description="Match percentage score between candidate & target role")

class EvaluationResult(BaseModel):
    score: int = Field(description="Score between 0 and 100")
    feedback: str = Field(description="2-3 sentences of technical feedback on candidate's answer")
    key_takeaway: str = Field(description="1 key advice point for improvement")

# ---------------------------------------------------------------------------
# Google ADK 2.0 Shared Team State Schema
# ---------------------------------------------------------------------------
class ADKState(TypedDict):
    # Inputs
    resume_bytes: Optional[bytes]
    resume_text: Optional[str]
    target_role: str
    github_url: Optional[str]
    linkedin_url: Optional[str]
    
    # ADK 2.0 Agent Processed Outputs
    resume_data: Optional[Dict[str, Any]]
    github_data: Optional[Dict[str, Any]]
    linkedin_data: Optional[Dict[str, Any]]
    
    # Gap Analysis State
    unified_skills: List[str]
    skills_gap: List[str]
    match_score: float
    
    # Action Payload Outputs
    curated_courses: List[Dict[str, Any]]
    project_blueprints: List[Dict[str, Any]]
    live_jobs: List[Dict[str, Any]]
    
    # Interactive AI Interview State
    interview_history: List[Dict[str, Any]]
