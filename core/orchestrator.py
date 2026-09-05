from typing import Dict, Any
from core.state import ADKState
from core.agents.resume_parser_agent import ResumeParserADKAgent
from core.agents.github_inspector_agent import GitHubInspectorADKAgent
from core.agents.skill_normalizer_agent import SkillNormalizerADKAgent
from core.agents.gap_analyzer_agent import GapAnalyzerADKAgent
from core.agents.rag_curator_agent import RAGCuratorADKAgent
from core.agents.project_generator_agent import ProjectGeneratorADKAgent
from core.agents.interview_simulator_agent import InterviewSimulatorADKAgent
from core.agents.live_job_market_agent import LiveJobMarketADKAgent

class CareerCopilotADKTeam:
    """
    Google ADK 2.0 Multi-Agent Team Orchestrator
    Coordinates 8 specialized autonomous agents using Model Context Protocol (MCP) tools:
    1. ResumeParserADKAgent (Multimodal PDF/Text + Projects & Certifications extraction)
    2. GitHubInspectorADKAgent (Candidate GitHub repo & language profiling)
    3. SkillNormalizerADKAgent (Synonym deduplication & canonicalization)
    4. GapAnalyzerADKAgent (3-Tier Consensus + Gemini Vector Embedding Semantic Matcher)
    5. RAGCuratorADKAgent (Resource MCP + Search Grounding multi-format learning packs)
    6. ProjectGeneratorADKAgent (GitHub MCP real public repository discovery)
    7. InterviewSimulatorADKAgent (Contextual technical scenario Q&A)
    8. LiveJobMarketADKAgent (Live job placement & direct application links)
    """
    def __init__(self):
        self.resume_parser = ResumeParserADKAgent()
        self.github_inspector = GitHubInspectorADKAgent()
        self.skill_normalizer = SkillNormalizerADKAgent()
        self.gap_analyzer = GapAnalyzerADKAgent()
        self.rag_curator = RAGCuratorADKAgent()
        self.project_generator = ProjectGeneratorADKAgent()
        self.interview_simulator = InterviewSimulatorADKAgent()
        self.job_market_agent = LiveJobMarketADKAgent()

    def run_tab1_pipeline(self, initial_state: ADKState) -> ADKState:
        """Executes the complete multi-agent pipeline with full resume context and semantic matching."""
        state = dict(initial_state)

        # Stage 1: Multimodal Candidate Profile Ingestion
        resume_data = self.resume_parser.parse(
            resume_text=state.get("resume_text"),
            pdf_bytes=state.get("resume_bytes")
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

        # Stage 3: Multi-Format Learning Pack & Public GitHub Project Discovery
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

        # Stage 4: Live Job Market & Direct Application Links
        live_jobs = self.job_market_agent.fetch_live_job_postings(
            target_role=target_role,
            location="us"
        )
        state["live_jobs"] = live_jobs

        return state
