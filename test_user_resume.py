import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agents.resume_parser_agent import ResumeParserADKAgent
from core.agents.gap_analyzer_agent import GapAnalyzerADKAgent

sample_text = """
SUMAVARSHITHA KAMATAM
AI / LLM Systems Engineer | sumavarshitha@example.com

PROFESSIONAL EXPERIENCE:
Senior AI Systems Engineer — NextGen Enterprise AI (2022 - Present)
- Designed and deployed a production-grade AI Failure Analysis Agent (tool-calling + RAG) integrated with cloud telemetry.
- Built LLM-powered agentic systems with single-agent and multi-agent reasoning patterns for security and workflow automation.
- Applied systematic prompt engineering to ensure reliable, auditable, and deterministic automation outputs.
- Developed GenAI UI system that converts natural language prompts into dynamic dashboards (charts, metrics, graphs).
- Built an agentic data-insights platform using LangGraph + GenSQL, enabling API-based database connectivity.
- Architected fully automated CI/CD orchestration system (Docker + Jenkins + Groovy) executing 400+ daily builds.

FEATURED PROJECTS:
- LangGraph Autonomous Workflow Orchestrator: Multi-agent framework with state graphs, dynamic memory, and tool integration.
- GenSQL Natural Language Query Engine: Schema-grounded SQL generation system with vector indexing.

EDUCATION:
B.Tech in Computer Science and Engineering — JNTU (2018 - 2022)

CERTIFICATIONS:
Google Cloud Professional Data & AI Engineer
"""

def test_user_resume_parsing():
    parser = ResumeParserADKAgent()
    parsed = parser.parse(resume_text=sample_text)
    print("\n--- PARSED RESUME DATA ---")
    print(f"Name: {parsed.get('candidate_name')}")
    print(f"Job Title: {parsed.get('job_title')}")
    print(f"Years Exp: {parsed.get('years_experience')}")
    print(f"Education: {parsed.get('education')}")
    print(f"Projects Count: {len(parsed.get('projects', []))}")
    for p in parsed.get("projects", []):
        print(f"  * Project: {p.get('title')} (Tech: {p.get('tech_stack')})")
    print(f"Work Experience Count: {len(parsed.get('work_experience', []))}")
    for w in parsed.get("work_experience", []):
        print(f"  * Role: {w.get('role')} at {w.get('company')} ({w.get('duration')})")
        print(f"    Bullets ({len(w.get('bullets', []))}):")
        for b in w.get("bullets", [])[:3]:
            print(f"      - {b[:80]}...")
    print(f"Certifications: {parsed.get('certifications')}")
    print(f"Skills ({len(parsed.get('skills', []))}): {parsed.get('skills')[:10]}")

    # Test Gap Analyzer on this profile
    analyzer = GapAnalyzerADKAgent()
    gap = analyzer.analyze(
        candidate_skills=parsed.get("skills", []),
        target_role="AI/ML Engineer",
        seniority_level="Senior",
        resume_data=parsed
    )
    print("\n--- GAP ANALYSIS RESULTS ---")
    print(f"Match Score: {gap.get('match_percentage')}% (Core: {gap.get('core_match_percentage')}%)")
    print(f"Verified Skills ({len(gap.get('verified_skills', []))}): {gap.get('verified_skills')}")
    print(f"Missing Skills: {gap.get('missing_skills')}")
    print("\nEvidence Breakdown:")
    for m in gap.get("semantic_matches", []):
        status = "MATCH" if m.get("is_match") else "GAP"
        print(f"  [{status}] {m.get('required_skill')} <-> '{m.get('matched_candidate_skill')}' (Source: {m.get('evidence_source')})")

if __name__ == "__main__":
    test_user_resume_parsing()
