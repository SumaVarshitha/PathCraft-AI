from typing import Dict, Any
from core.state import ADKState
from core.adk_agent import ADKRunner

# Import Google ADK 2.0 Agents
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
    Coordinates execution across specialized ADK 2.0 Agents powered by Gemini 3.6.
    """
    def __init__(self):
        # Initialize Google ADK 2.0 Agent Team
        self.resume_parser = ResumeParserADKAgent()
        self.github_inspector = GitHubInspectorADKAgent()
        self.skill_normalizer = SkillNormalizerADKAgent()
        self.gap_analyzer = GapAnalyzerADKAgent()
        self.rag_curator = RAGCuratorADKAgent()
        self.project_generator = ProjectGeneratorADKAgent()
        self.interview_simulator = InterviewSimulatorADKAgent()
        self.job_market_agent = LiveJobMarketADKAgent()

        # Wrap in ADK Runner
        self.runner = ADKRunner(agents=[
            self.resume_parser,
            self.github_inspector,
            self.skill_normalizer,
            self.gap_analyzer,
            self.rag_curator,
            self.project_generator,
            self.interview_simulator,
            self.job_market_agent
        ])

    def run_tab1_pipeline(self, initial_state: ADKState) -> ADKState:
        """Executes the Google ADK 2.0 Agent Team Workflow for Tab 1."""
        state = dict(initial_state)

        # Step 1: Input Parsing Stage
        resume_bytes = state.get("resume_bytes")
        resume_text = state.get("resume_text", "")
        github_url = state.get("github_url")

        resume_data = self.resume_parser.parse(resume_text=resume_text, pdf_bytes=resume_bytes)
        state["resume_data"] = resume_data

        github_data = None
        if github_url:
            github_data = self.github_inspector.inspect(github_url)
        state["github_data"] = github_data

        # Step 2: Profiling & Gap Analysis Stage
        resume_skills = resume_data.get("skills", [])
        github_skills = github_data.get("detected_skills", []) if github_data else []

        unified_skills = self.skill_normalizer.normalize(
            resume_skills=resume_skills,
            github_skills=github_skills
        )
        state["unified_skills"] = unified_skills

        target_role = state.get("target_role", "Data Engineer")
        gap_result = self.gap_analyzer.analyze(candidate_skills=unified_skills, target_role=target_role)
        
        state["skills_gap"] = gap_result.get("missing_skills", [])
        state["match_score"] = gap_result.get("match_percentage", 0.0)

        # Step 3: Action Engine Stage (RAG Courses + Projects + Live Job Links)
        missing_skills = state["skills_gap"]

        curated_courses = self.rag_curator.curate(missing_skills=missing_skills)
        state["curated_courses"] = curated_courses

        project_blueprints = self.project_generator.generate(
            missing_skills=missing_skills,
            target_role=target_role
        )
        state["project_blueprints"] = project_blueprints

        # Step 4: Fetch Live Active Job Listings with Direct Apply Links
        live_jobs = self.job_market_agent.fetch_live_job_postings(target_role=target_role)
        state["live_jobs"] = live_jobs

        return state
