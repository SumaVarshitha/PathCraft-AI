from typing import Dict, Any
from langgraph.graph import StateGraph, END
from core.state import Tab1State
from core.parsers.resume_parser import parse_resume
from core.parsers.github_inspector import inspect_github_user
from core.agents.skill_normalizer import process_and_normalize_profile
from core.agents.gap_analyzer import analyze_skill_gap
from core.agents.rag_curator import curate_learning_resources
from core.agents.project_generator import generate_portfolio_projects

# ---------------------------------------------------------------------------
# Node Functions for LangGraph
# ---------------------------------------------------------------------------

def parse_inputs_node(state: Tab1State) -> Dict[str, Any]:
    """Node 1: Parses Resume PDF/Text and optional GitHub profile."""
    resume_bytes = state.get("resume_bytes")
    resume_text = state.get("resume_text", "")
    github_url = state.get("github_url")
    
    # Parse Resume
    parsed_resume = parse_resume(resume_text=resume_text, pdf_bytes=resume_bytes)
    
    # Parse GitHub if provided
    github_data = None
    if github_url:
        github_data = inspect_github_user(github_url)
        
    return {
        "resume_data": parsed_resume,
        "github_data": github_data
    }

def normalize_profile_node(state: Tab1State) -> Dict[str, Any]:
    """Node 2: Merges & normalizes skills across parsed inputs."""
    resume_data = state.get("resume_data", {})
    resume_skills = resume_data.get("skills", [])
    
    github_data = state.get("github_data")
    github_skills = github_data.get("detected_skills", []) if github_data else []
    
    unified = process_and_normalize_profile(
        resume_skills=resume_skills,
        github_skills=github_skills
    )
    
    return {"unified_skills": unified}

def gap_analysis_node(state: Tab1State) -> Dict[str, Any]:
    """Node 3: Compares unified candidate profile against target role requirements."""
    unified_skills = state.get("unified_skills", [])
    target_role = state.get("target_role", "Data Engineer")
    
    gap_result = analyze_skill_gap(candidate_skills=unified_skills, target_role=target_role)
    
    return {
        "skills_gap": gap_result.get("missing_skills", []),
        "match_score": gap_result.get("match_percentage", 0.0)
    }

def action_engine_node(state: Tab1State) -> Dict[str, Any]:
    """Node 4: Curates live free resources and generates portfolio project blueprints."""
    missing_skills = state.get("skills_gap", [])
    target_role = state.get("target_role", "Data Engineer")
    
    # Curate Courses
    courses = curate_learning_resources(missing_skills)
    
    # Generate Project Blueprints
    projects = generate_portfolio_projects(missing_skills, target_role)
    
    return {
        "curated_courses": courses,
        "project_blueprints": projects
    }

# ---------------------------------------------------------------------------
# Construct LangGraph Pipeline
# ---------------------------------------------------------------------------

def build_tab1_graph():
    builder = StateGraph(Tab1State)
    
    # Add Nodes
    builder.add_node("parse_inputs", parse_inputs_node)
    builder.add_node("normalize_profile", normalize_profile_node)
    builder.add_node("gap_analysis", gap_analysis_node)
    builder.add_node("action_engine", action_engine_node)
    
    # Define Edges
    builder.set_entry_point("parse_inputs")
    builder.add_edge("parse_inputs", "normalize_profile")
    builder.add_edge("normalize_profile", "gap_analysis")
    builder.add_edge("gap_analysis", "action_engine")
    builder.add_edge("action_engine", END)
    
    return builder.compile()
