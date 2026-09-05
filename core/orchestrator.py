from typing import Dict, Any
from core.state import ADKState
from core.agents.resume_parser_agent import ResumeParserADKAgent, extract_text_from_pdf_bytes
from core.agents.github_inspector_agent import GitHubInspectorADKAgent
from core.agents.skill_normalizer_agent import SkillNormalizerADKAgent
from core.agents.gap_analyzer_agent import GapAnalyzerADKAgent
from core.agents.rag_curator_agent import RAGCuratorADKAgent
from core.agents.project_generator_agent import ProjectGeneratorADKAgent
from core.agents.interview_simulator_agent import InterviewSimulatorADKAgent
from core.agents.live_job_market_agent import LiveJobMarketADKAgent
from core.agents.ats_analyzer_agent import ATSAnalyzerADKAgent

class CareerCopilotADKTeam:
    """
    Google ADK 2.0 Multi-Agent Team Orchestrator
    Coordinates 9 specialized autonomous agents using Model Context Protocol (MCP) tools:
    1. ResumeParserADKAgent (Multimodal PDF/Text + Projects & Certifications extraction)
    2. GitHubInspectorADKAgent (Candidate GitHub repo & language profiling)
    3. SkillNormalizerADKAgent (Synonym deduplication & canonicalization)
    4. GapAnalyzerADKAgent (3-Tier Consensus + Gemini Vector Embedding Semantic Matcher)
    5. ATSAnalyzerADKAgent (ATS Compatibility Scoring & Power Bullet Point Optimizer)
    6. RAGCuratorADKAgent (Resource MCP + Search Grounding multi-format learning packs)
    7. ProjectGeneratorADKAgent (GitHub MCP real public repository discovery)
    8. InterviewSimulatorADKAgent (Contextual technical scenario Q&A)
    9. LiveJobMarketADKAgent (Live job placement & direct application links)
    """
    def __init__(self):
        self.resume_parser = ResumeParserADKAgent()
        self.github_inspector = GitHubInspectorADKAgent()
        self.skill_normalizer = SkillNormalizerADKAgent()
        self.gap_analyzer = GapAnalyzerADKAgent()
        self.ats_analyzer = ATSAnalyzerADKAgent()
        self.rag_curator = RAGCuratorADKAgent()
        self.project_generator = ProjectGeneratorADKAgent()
        self.interview_simulator = InterviewSimulatorADKAgent()
        self.job_market_agent = LiveJobMarketADKAgent()

    def run_tab1_pipeline(self, initial_state: ADKState) -> ADKState:
        """Executes the complete multi-agent pipeline with full resume context, semantic matching, and ATS audit."""
        state = dict(initial_state)

        # Stage 1: Multimodal Candidate Profile Ingestion
        resume_bytes = state.get("resume_bytes")
        resume_text = state.get("resume_text") or ""
        if resume_bytes and not resume_text:
            resume_text = extract_text_from_pdf_bytes(resume_bytes)
            state["resume_text"] = resume_text

        resume_data = self.resume_parser.parse(
            resume_text=resume_text,
            pdf_bytes=resume_bytes
        )
        state["resume_data"] = resume_data
        resume_skills = resume_data.get("skills", [])

        github_data = None
        github_skills = []
        if state.get("github_url"):
            github_data = self.github_inspector.inspect(state["github_url"])
            state["github_data"] = github_data
            github_skills = github_data.get("skills", [])

        # Stage 2: Profile Normalization & Semantic Skill Gap Analysis
        unified_skills = self.skill_normalizer.normalize(
            resume_skills=resume_skills,
            github_skills=github_skills
        )
        state["unified_skills"] = unified_skills

        target_role = state.get("target_role", "Data Engineer")
        gap_result = self.gap_analyzer.analyze(
            candidate_skills=unified_skills,
            target_role=target_role,
            resume_data=resume_data
        )
        
        state["verified_skills"] = gap_result.get("verified_skills", [])
        state["skills_gap"] = gap_result.get("missing_skills", [])
        state["match_score"] = gap_result.get("match_percentage", 0.0)
        state["analysis_method"] = gap_result.get("analysis_method", "Live 2026 Market Search Grounding")
        state["semantic_matches"] = gap_result.get("semantic_matches", [])

        # Stage 3: ATS Resume Compatibility Audit & Bullet Point Optimizer
        ats_audit = self.ats_analyzer.audit(
            resume_text=resume_text or str(resume_data),
            target_role=target_role,
            missing_skills=state["skills_gap"]
        )
        state["ats_audit"] = ats_audit

        # Stage 4: Multi-Format Learning Pack & Public GitHub Project Discovery
        missing_skills = state["skills_gap"]

        resource_pack = self.rag_curator.curate(missing_skills=missing_skills)
        state["learning_resources"] = resource_pack
        state["curated_courses"] = resource_pack.get("courses", [])

        discovered_projects = self.project_generator.generate(
            missing_skills=missing_skills,
            target_role=target_role
        )
        state["project_blueprints"] = discovered_projects
        state["github_projects"] = discovered_projects

        # Stage 5: Live Job Market & Direct Application Links
        live_jobs = self.job_market_agent.fetch_live_job_postings(
            target_role=target_role,
            location="us"
        )
        state["live_jobs"] = live_jobs

        return state
