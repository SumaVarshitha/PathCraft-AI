"""
PathCraft AI - FastAPI REST API Server (Google ADK 2.0 Engine & MCP Tools)
Exposes high-performance async REST endpoints for testing individual agents,
running step-by-step HITL operations, or full pipeline execution.
Interactive Swagger API Docs available at: http://localhost:8000/docs
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

import config
from core.orchestrator import CareerCopilotADKTeam
from core.state import ADKState, ResumeSchema, SkillGapResult, EvaluationResult

# Initialize FastAPI App
app = FastAPI(
    title="PathCraft AI - Google ADK 2.0 API Engine",
    description="Enterprise Multi-Agent Career & Skill Engineering API powered by Google ADK 2.0, Vector Semantic RAG & MCP Tools",
    version="3.5.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Agent Team
adk_team = CareerCopilotADKTeam()

# ---------------------------------------------------------------------------
# Request Payload Models
# ---------------------------------------------------------------------------
class ParseResumeTextRequest(BaseModel):
    resume_text: str = Field(description="Raw text content of candidate resume")
    linkedin_text: Optional[str] = Field(default=None, description="Optional LinkedIn profile or achievements text")

class GitHubInspectRequest(BaseModel):
    github_url_or_username: str = Field(description="GitHub profile URL or username")

class GapAnalysisRequest(BaseModel):
    candidate_skills: List[str] = Field(description="List of candidate verified skills")
    target_role: str = Field(default="Data Engineer", description="Target career job role")
    seniority_level: str = Field(default="Mid-Senior", description="Seniority level (e.g. Junior, Mid, Senior, Staff)")
    resume_data: Optional[Dict[str, Any]] = Field(default=None, description="Complete parsed resume dictionary including work bullets & projects")
    github_data: Optional[Dict[str, Any]] = Field(default=None, description="GitHub profile inspection data")
    linkedin_text: Optional[str] = Field(default=None, description="Imported LinkedIn text")

class CurateCoursesRequest(BaseModel):
    missing_skills: List[str] = Field(description="List of missing skills to curate multi-format resources for")

class DiscoverProjectsRequest(BaseModel):
    missing_skills: List[str] = Field(description="List of missing skills")
    target_role: str = Field(description="Target career role")

class NextInterviewQuestionRequest(BaseModel):
    target_role: str = Field(description="Target career role")
    missing_skills: List[str] = Field(default_factory=list, description="Candidate missing skills")
    verified_skills: List[str] = Field(default_factory=list, description="Candidate verified skills")
    turn_index: int = Field(default=0, description="Question turn number (0-indexed)")
    total_questions: int = Field(default=5, description="Total questions in session")
    chat_history: List[Dict[str, Any]] = Field(default_factory=list)
    difficulty: str = Field(default="Senior", description="Interview difficulty")

class EvaluateInterviewAnswerRequest(BaseModel):
    question: str = Field(description="Question asked by interviewer")
    candidate_answer: str = Field(description="Answer provided by candidate")
    target_role: str = Field(description="Target career role")
    skill_focus: str = Field(description="Specific skill being tested")
    difficulty: str = Field(default="Senior")

class FinalReportCardRequest(BaseModel):
    target_role: str = Field(description="Target career role")
    turns: List[Dict[str, Any]] = Field(description="List of completed interview turns with questions and evaluations")

class LiveJobsRequest(BaseModel):
    target_role: str = Field(description="Target career job role")
    location: str = Field(default="Remote / United States", description="Target location or Remote")
    limit: int = Field(default=10, description="Number of job openings to fetch (5 to 30)")
    candidate_skills: List[str] = Field(default_factory=list, description="Candidate verified skills for match scoring")

class FullPipelineRequest(BaseModel):
    resume_text: Optional[str] = None
    linkedin_text: Optional[str] = None
    github_url: Optional[str] = None
    target_role: str = Field(default="Data Engineer", description="Target job role")
    seniority_level: str = Field(default="Senior", description="Target seniority")
    study_pace_hours_per_week: int = Field(default=10, description="Weekly study budget")

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "PathCraft AI - Google ADK 2.0 & MCP Tools Engine",
        "version": "3.5.0",
        "docs_url": "http://localhost:8000/docs",
        "models": [config.MODEL_FLASH, config.MODEL_PRO]
    }

@app.post("/api/v1/parse-resume-text", summary="Agent 1: Parse Text Resume (Deep Multi-Page Context)")
def parse_resume_text(req: ParseResumeTextRequest):
    """Executes ResumeParserADKAgent to extract structured metrics, work bullets, and projects."""
    try:
        res = adk_team.resume_parser.parse(resume_text=req.resume_text, linkedin_text=req.linkedin_text)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/parse-resume-file", summary="Agent 1: Parse PDF File Resume (Deep Multi-Page Context)")
async def parse_resume_file(file: UploadFile = File(...), linkedin_text: Optional[str] = Form(None)):
    """Executes ResumeParserADKAgent on uploaded PDF resume file."""
    try:
        pdf_bytes = await file.read()
        res = adk_team.resume_parser.parse(pdf_bytes=pdf_bytes, linkedin_text=linkedin_text)
        return {"status": "success", "filename": file.filename, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/inspect-github", summary="Agent 2: Inspect GitHub Profile via MCP")
def inspect_github(req: GitHubInspectRequest):
    """Executes GitHubInspectorADKAgent to profile user repos and languages."""
    try:
        res = adk_team.github_inspector.inspect(req.github_url_or_username)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/analyze-gap", summary="Agent 4: 2-Tier Weighted Semantic Skill Gap Analyzer")
def analyze_gap(req: GapAnalysisRequest):
    """Executes GapAnalyzerADKAgent using dynamic market grounding and Gemini Vector Embeddings."""
    try:
        res = adk_team.gap_analyzer.analyze(
            candidate_skills=req.candidate_skills,
            target_role=req.target_role,
            seniority_level=req.seniority_level,
            resume_data=req.resume_data,
            github_data=req.github_data,
            linkedin_text=req.linkedin_text
        )
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/interview/next-question", summary="Agent 7: Generate Next Conversational Interview Question")
def get_next_interview_question(req: NextInterviewQuestionRequest):
    """Executes InterviewSimulatorADKAgent question generator."""
    try:
        q_data = adk_team.interview_simulator.generate_next_question(
            target_role=req.target_role,
            missing_skills=req.missing_skills,
            verified_skills=req.verified_skills,
            turn_index=req.turn_index,
            total_questions=req.total_questions,
            chat_history=req.chat_history,
            difficulty=req.difficulty
        )
        return {"status": "success", "data": q_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/interview/evaluate-turn", summary="Agent 7: Evaluate Mock Interview Turn with Model Answer")
def evaluate_interview_turn(req: EvaluateInterviewAnswerRequest):
    """Executes InterviewSimulatorADKAgent answer scoring, feedback & model snippet."""
    try:
        eval_res = adk_team.interview_simulator.evaluate_answer(
            question=req.question,
            candidate_answer=req.candidate_answer,
            target_role=req.target_role,
            skill_focus=req.skill_focus,
            difficulty=req.difficulty
        )
        return {"status": "success", "evaluation": eval_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/interview/report-card", summary="Agent 7: Generate Final Mock Interview Scorecard")
def get_interview_report_card(req: FinalReportCardRequest):
    """Calculates overall average score and hire readiness rating."""
    try:
        report = adk_team.interview_simulator.generate_final_report_card(
            target_role=req.target_role,
            turns=req.turns
        )
        return {"status": "success", "report_card": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fetch-live-jobs", summary="Agent 8: Fetch Live Job Openings (10-30+) with Match Scoring")
def fetch_live_jobs(req: LiveJobsRequest):
    """Executes LiveJobMarketADKAgent via Google Search Grounding and Job MCP."""
    try:
        jobs = adk_team.job_market_agent.fetch_live_job_postings(
            target_role=req.target_role,
            location=req.location,
            limit=req.limit,
            candidate_skills=req.candidate_skills
        )
        return {"status": "success", "count": len(jobs), "data": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/run-pipeline", summary="Full Multi-Agent Pipeline Execution")
def run_pipeline(req: FullPipelineRequest):
    """Executes the complete Google ADK 2.0 Agent Team pipeline end-to-end."""
    try:
        initial_state = {
            "resume_bytes": None,
            "resume_text": req.resume_text or "",
            "target_role": req.target_role,
            "seniority_level": req.seniority_level,
            "github_url": req.github_url,
            "linkedin_url": None,
            "linkedin_text": req.linkedin_text,
            "user_confirmed_skills": [],
            "user_prioritized_gaps": [],
            "study_pace_hours_per_week": req.study_pace_hours_per_week,
            "resume_data": None,
            "github_data": None,
            "linkedin_data": None,
            "unified_skills": [],
            "skills_gap": [],
            "core_skills": [],
            "differentiator_skills": [],
            "match_score": 0.0,
            "core_match_score": 0.0,
            "analysis_method": "",
            "semantic_matches": [],
            "ats_audit": None,
            "career_roadmap": None,
            "tailored_resume": None,
            "curated_courses": [],
            "learning_resources": {},
            "project_blueprints": [],
            "github_projects": [],
            "live_jobs": [],
            "interview_history": [],
            "interview_turns": []
        }
        final_state = adk_team.run_full_pipeline(initial_state)
        return {"status": "success", "result": final_state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
