from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field

class WorkExperienceItem(BaseModel):
    role: str = Field(description="Job title held")
    company: str = Field(description="Company or Organization name")
    duration: Optional[str] = Field(default="", description="Tenure or dates of employment")
    description: Optional[str] = Field(default="", description="High-level overview of responsibilities")
    bullets: List[str] = Field(default_factory=list, description="Specific project deliverables, metrics, and achievements")

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
    work_experience: List[WorkExperienceItem] = Field(default_factory=list, description="Detailed chronological work experience with bullet points")
    projects: List[ProjectItem] = Field(default_factory=list, description="Academic, personal, or professional projects detailed in resume")
    certifications: List[str] = Field(default_factory=list, description="Industry certifications or licenses (e.g. AWS, GCP, CKA)")
    tools_and_technologies: List[str] = Field(default_factory=list, description="All tools, libraries, databases, and frameworks mentioned across the entire resume")
    linkedin_achievements: Optional[str] = Field(default="", description="Imported LinkedIn honors, recommendations, awards, or public achievements")

class SemanticMatchItem(BaseModel):
    required_skill: str = Field(description="The target job role required skill")
    skill_category: str = Field(default="Core Must-Have", description="Tier category: 'Core Must-Have' or 'Advanced Differentiator'")
    matched_candidate_skill: Optional[str] = Field(default=None, description="The candidate skill or project tech that semantically matched")
    similarity_score: float = Field(description="Semantic cosine similarity score between 0.0 and 1.0")
    is_match: bool = Field(description="True if similarity meets or exceeds matching threshold")
    evidence_source: str = Field(default="Skills Section", description="Source where skill/context was found: Skills Section, Work Experience, Projects, Certifications, GitHub, or LinkedIn")

class SkillGapResult(BaseModel):
    verified_skills: List[str] = Field(description="List of skills successfully matched in candidate profile")
    missing_skills: List[str] = Field(description="List of required skills missing from candidate profile")
    core_requirements: List[str] = Field(default_factory=list, description="High-priority core must-have skills for the role")
    differentiator_requirements: List[str] = Field(default_factory=list, description="Advanced differentiator skills for the role")
    match_percentage: float = Field(description="Overall weighted candidate profile match score from 0.0 to 100.0")
    core_match_percentage: float = Field(default=0.0, description="Match score on core must-have skills")
    semantic_matches: List[SemanticMatchItem] = Field(default_factory=list, description="Granular semantic matching breakdown for each required skill")
    candidate_superpowers: List[str] = Field(default_factory=list, description="Cutting-edge candidate strengths that exceed baseline role requirements (e.g. LangGraph, RAG, Multi-Agent Systems)")
    suggested_alternate_roles: List[Dict[str, Any]] = Field(default_factory=list, description="High-match alternate job titles where candidate has exceptional synergy")
    analysis_method: str = Field(default="Live 2026 Market Search Grounding & Gemini Embeddings", description="Method used to fetch and evaluate requirements")

class EvaluationResult(BaseModel):
    score: int = Field(description="Score between 0 and 100")
    feedback: str = Field(description="Constructive evaluation feedback explaining strengths and gaps")
    key_takeaway: str = Field(description="1 actionable improvement recommendation for future interviews")
    model_answer_snippet: Optional[str] = Field(default="", description="Brief reference model answer or production architectural tip")

class InterviewTurn(BaseModel):
    turn_index: int = Field(description="Question number index")
    skill_focus: str = Field(description="Primary skill or competency being tested")
    question: str = Field(description="Question asked by interviewer")
    candidate_answer: Optional[str] = Field(default="", description="Candidate submitted response")
    evaluation: Optional[EvaluationResult] = Field(default=None, description="Detailed score and feedback")

class ADKState(TypedDict):
    resume_bytes: Optional[bytes]
    resume_text: str
    target_role: str
    seniority_level: str
    github_url: Optional[str]
    linkedin_url: Optional[str]
    linkedin_text: Optional[str]
    user_confirmed_skills: List[str]
    user_prioritized_gaps: List[str]
    study_pace_hours_per_week: int
    resume_data: Optional[Dict[str, Any]]
    github_data: Optional[Dict[str, Any]]
    linkedin_data: Optional[Dict[str, Any]]
    unified_skills: List[str]
    skills_gap: List[str]
    core_skills: List[str]
    differentiator_skills: List[str]
    candidate_superpowers: List[str]
    suggested_alternate_roles: List[Dict[str, Any]]
    match_score: float
    core_match_score: float
    analysis_method: str
    semantic_matches: List[Dict[str, Any]]
    curated_courses: List[Dict[str, Any]]
    learning_resources: Dict[str, Any]
    project_blueprints: List[Dict[str, Any]]
    github_projects: List[Dict[str, Any]]
    live_jobs: List[Dict[str, Any]]
    interview_history: List[Dict[str, Any]]
    interview_turns: List[Dict[str, Any]]
    ats_audit: Optional[Dict[str, Any]]
    career_roadmap: Optional[Dict[str, Any]]
    tailored_resume: Optional[Dict[str, Any]]
