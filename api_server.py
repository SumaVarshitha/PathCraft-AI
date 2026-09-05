"""
PathCraft AI - FastAPI REST API Server (Google ADK 2.0 Engine & MCP Tools)
Exposes REST endpoints for testing individual agents & running full pipeline execution.
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
    version="3.0.0"
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

class GitHubInspectRequest(BaseModel):
    github_url_or_username: str = Field(description="GitHub profile URL or username")

class GapAnalysisRequest(BaseModel):
    candidate_skills: List[str] = Field(description="List of candidate verified skills")
    target_role: str = Field(description="Target career job role e.g. Data Engineer")
    resume_data: Optional[Dict[str, Any]] = Field(default=None, description="Complete parsed resume dictionary including projects")

class CurateCoursesRequest(BaseModel):
    missing_skills: List[str] = Field(description="List of missing skills to curate multi-format resources for")

class DiscoverProjectsRequest(BaseModel):
    missing_skills: List[str] = Field(description="List of missing skills")
    target_role: str = Field(description="Target career role")

class InterviewQuestionRequest(BaseModel):
    target_role: str = Field(description="Target career role")
    missing_skills: List[str] = Field(description="Candidate missing skills")
    chat_history: List[Dict[str, Any]] = Field(default_factory=list)

class InterviewEvaluateRequest(BaseModel):
    question: str = Field(description="Question asked by interviewer")
    candidate_answer: str = Field(description="Answer provided by candidate")
    target_role: str = Field(description="Target career role")

class LiveJobsRequest(BaseModel):
    target_role: str = Field(description="Target career job role")
    location: str = Field(default="us", description="Target location code e.g. us, uk")

class FullPipelineRequest(BaseModel):
    resume_text: Optional[str] = None
    github_url: Optional[str] = None
    target_role: str = Field(default="Data Engineer", description="Target job role")

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "online",
        "service": "PathCraft AI - Google ADK 2.0 & MCP Tools Engine",
        "version": "3.0.0",
        "docs_url": "http://localhost:8000/docs",
        "models": [config.MODEL_FLASH, config.MODEL_PRO]
    }

@app.post("/api/v1/parse-resume-text", summary="Agent 1: Parse Text Resume (Full Context)")
def parse_resume_text(req: ParseResumeTextRequest):
    """Executes ResumeParserADKAgent to extract structured metrics and projects."""
    try:
        res = adk_team.resume_parser.parse(resume_text=req.resume_text)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/parse-resume-file", summary="Agent 1: Parse PDF File Resume (Full Context)")
async def parse_resume_file(file: UploadFile = File(...)):
    """Executes ResumeParserADKAgent on uploaded PDF resume file."""
    try:
        pdf_bytes = await file.read()
        res = adk_team.resume_parser.parse(pdf_bytes=pdf_bytes)
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

@app.post("/api/v1/analyze-gap", summary="Agent 4: Semantic Skill Gap Analyzer")
def analyze_gap(req: GapAnalysisRequest):
    """Executes GapAnalyzerADKAgent using Gemini Vector Embeddings and cosine similarity."""
    try:
        res = adk_team.gap_analyzer.analyze(
            candidate_skills=req.candidate_skills,
            target_role=req.target_role,
            resume_data=req.resume_data
        )
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/curate-resources", summary="Agent 5: Multi-Format Learning Curator (Books, Papers, Docs, Videos)")
def curate_resources(req: CurateCoursesRequest):
    """Executes RAGCuratorADKAgent with ResourceMCPTool & Google Search Grounding."""
    try:
        res = adk_team.rag_curator.curate(missing_skills=req.missing_skills)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/discover-projects", summary="Agent 6: Real Public GitHub Project Discovery")
def discover_projects(req: DiscoverProjectsRequest):
    """Executes ProjectGeneratorADKAgent querying GitHub MCP for live public reference repos."""
    try:
        res = adk_team.project_generator.generate(missing_skills=req.missing_skills, target_role=req.target_role)
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/interview/question", summary="Agent 7: Generate Mock Interview Question")
def generate_interview_question_endpoint(req: InterviewQuestionRequest):
    """Executes InterviewSimulatorADKAgent question generator."""
    try:
        question = adk_team.interview_simulator.generate_question(
            target_role=req.target_role,
            missing_skills=req.missing_skills,
            chat_history=req.chat_history
        )
        return {"status": "success", "question": question}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/interview/evaluate", summary="Agent 7: Evaluate Mock Interview Answer")
def evaluate_interview_answer_endpoint(req: InterviewEvaluateRequest):
    """Executes InterviewSimulatorADKAgent answer scoring & constructive feedback."""
    try:
        eval_res = adk_team.interview_simulator.evaluate_answer(
            question=req.question,
            candidate_answer=req.candidate_answer,
            target_role=req.target_role
        )
        return {"status": "success", "evaluation": eval_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/fetch-live-jobs", summary="Agent 8: Fetch Live Job Openings with Apply Links")
def fetch_live_jobs(req: LiveJobsRequest):
    """Executes LiveJobMarketADKAgent via JobMarketMCPTool."""
    try:
        jobs = adk_team.job_market_agent.fetch_live_job_postings(target_role=req.target_role, location=req.location)
        return {"status": "success", "data": jobs}
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
            "github_url": req.github_url,
            "linkedin_url": None,
            "resume_data": None,
            "github_data": None,
            "linkedin_data": None,
            "unified_skills": [],
            "skills_gap": [],
            "match_score": 0.0,
            "analysis_method": "",
            "semantic_matches": [],
            "curated_courses": [],
            "learning_resources": {},
            "project_blueprints": [],
            "github_projects": [],
            "live_jobs": [],
            "interview_history": []
        }
        final_state = adk_team.run_tab1_pipeline(initial_state)
        return {"status": "success", "result": final_state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
