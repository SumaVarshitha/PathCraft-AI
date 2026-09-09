from typing import Dict, Any, List, Optional
from core.state import ADKState
from core.agents.resume_parser_agent import ResumeParserADKAgent, extract_text_from_pdf_bytes
from core.agents.github_inspector_agent import GitHubInspectorADKAgent
from core.agents.skill_normalizer_agent import SkillNormalizerADKAgent
from core.agents.gap_analyzer_agent import GapAnalyzerADKAgent
from core.agents.ats_analyzer_agent import ATSAnalyzerADKAgent
from core.agents.roadmap_agent import RoadmapADKAgent
from core.agents.resume_generator_agent import ResumeGeneratorADKAgent
from core.agents.rag_curator_agent import RAGCuratorADKAgent
from core.agents.project_generator_agent import ProjectGeneratorADKAgent
from core.agents.interview_simulator_agent import InterviewSimulatorADKAgent

class CareerCopilotADKTeam:
    """
    Google ADK 2.0 Multi-Agent Team Orchestrator
    Focused 4-Hub Career Intelligence System:
    1. ResumeParserADKAgent (Deep PDF/Text Ingestion + Work Bullets + Projects + Certifications + LinkedIn)
    2. GitHubInspectorADKAgent (Candidate GitHub profiling via GitHub MCP)
    3. SkillNormalizerADKAgent (Token-exact normalization & deduplication)
    4. GapAnalyzerADKAgent (Dynamic 2-Tier 70/30 Weighted Live Market Search Grounding + Superpower Detection)
    5. ATSAnalyzerADKAgent (100-pt ATS Resume Compatibility Audit)
    6. ResumeGeneratorADKAgent (Authentic In-Place Resume Optimizer on Original Text)
    7. RoadmapADKAgent (Personalized 30-60-90 Day Upskilling Roadmap by Weekly Budget)
    8. RAGCuratorADKAgent (Resource MCP: Books, Papers, Official Docs, Videos)
    9. ProjectGeneratorADKAgent (GitHub MCP real public repository discovery & blueprints)
    10. InterviewSimulatorADKAgent (Multi-turn conversational AI mock interviewer with live scoring)
    """
    def __init__(self):
        self.resume_parser = ResumeParserADKAgent()
        self.github_inspector = GitHubInspectorADKAgent()
        self.skill_normalizer = SkillNormalizerADKAgent()
        self.gap_analyzer = GapAnalyzerADKAgent()
        self.ats_analyzer = ATSAnalyzerADKAgent()
        self.resume_generator = ResumeGeneratorADKAgent()
        self.roadmap_agent = RoadmapADKAgent()
        self.rag_curator = RAGCuratorADKAgent()
        self.project_generator = ProjectGeneratorADKAgent()
        self.interview_simulator = InterviewSimulatorADKAgent()

    def parse_profile(self, state: ADKState) -> ADKState:
        """Stage 1: Multimodal Candidate Profile Ingestion (Resume, GitHub, LinkedIn)."""
        st = dict(state)
        resume_bytes = st.get("resume_bytes")
        resume_text = st.get("resume_text") or ""
        linkedin_text = st.get("linkedin_text") or ""

        if resume_bytes and not resume_text:
            resume_text = extract_text_from_pdf_bytes(resume_bytes)
            st["resume_text"] = resume_text

        resume_data = self.resume_parser.parse(
            resume_text=resume_text,
            pdf_bytes=resume_bytes,
            linkedin_text=linkedin_text
        )
        st["resume_data"] = resume_data
        resume_skills = resume_data.get("skills", [])

        github_data = None
        github_skills = []
        if st.get("github_url"):
            github_data = self.github_inspector.inspect(st["github_url"])
            # GitHubInspectorADKAgent returns 'detected_skills' and 'top_repos'
            # Normalize to consistent keys for gap analyzer (expects 'languages' + 'top_repositories')
            github_data_normalized = {
                "username": github_data.get("username", ""),
                "languages": github_data.get("detected_skills", []),
                "top_repositories": [
                    {
                        "name": r.get("name", ""),
                        "language": r.get("language", ""),
                        "stars": r.get("stars", 0),
                        "description": r.get("description", "")
                    }
                    for r in github_data.get("top_repos", [])
                ]
            }
            st["github_data"] = github_data_normalized
            github_skills = github_data_normalized.get("languages", [])


        # Normalize extracted skills
        unified_skills = self.skill_normalizer.normalize(
            resume_skills=resume_skills,
            github_skills=github_skills
        )
        st["unified_skills"] = unified_skills
        st["user_confirmed_skills"] = list(unified_skills)
        return st

    def run_full_pipeline(self, initial_state: ADKState) -> ADKState:
        """Executes the complete multi-agent pipeline end-to-end."""
        state = dict(initial_state)

        # 1. Parse Profile if not already parsed
        if not state.get("resume_data"):
            state = self.parse_profile(state)

        active_skills = state.get("user_confirmed_skills") or state.get("unified_skills", [])
        target_role = state.get("target_role", "Data Engineer")
        seniority_level = state.get("seniority_level", "Mid-Senior")

        # 2. Dynamic 2-Tier Semantic Skill Gap Analysis + Superpower Detection
        gap_result = self.gap_analyzer.analyze(
            candidate_skills=active_skills,
            target_role=target_role,
            seniority_level=seniority_level,
            resume_data=state.get("resume_data"),
            github_data=state.get("github_data"),
            linkedin_text=state.get("linkedin_text")
        )

        state["verified_skills"] = gap_result.get("verified_skills", [])
        state["skills_gap"] = gap_result.get("missing_skills", [])
        state["core_skills"] = gap_result.get("core_requirements", [])
        state["differentiator_skills"] = gap_result.get("differentiator_requirements", [])
        state["candidate_superpowers"] = gap_result.get("candidate_superpowers", [])
        state["suggested_alternate_roles"] = gap_result.get("suggested_alternate_roles", [])
        state["match_score"] = gap_result.get("match_percentage", 0.0)
        state["core_match_score"] = gap_result.get("core_match_percentage", 0.0)
        state["analysis_method"] = gap_result.get("analysis_method", "Live 2026 Market Search Grounding")
        state["semantic_matches"] = gap_result.get("semantic_matches", [])

        # Priority gaps
        active_gaps = state.get("user_prioritized_gaps") or state["skills_gap"]

        # 3. ATS Resume Compatibility Audit
        raw_resume_text = state.get("resume_text") or str(state.get("resume_data", ""))
        ats_audit = self.ats_analyzer.audit(
            resume_text=raw_resume_text,
            target_role=target_role,
            missing_skills=active_gaps
        )
        state["ats_audit"] = ats_audit

        # 4. In-Place Authentic Resume Optimization on Real Text
        cand_name = state.get("resume_data", {}).get("candidate_name", "Candidate")
        tailored_resume = self.resume_generator.optimize_in_place(
            raw_resume_text=raw_resume_text,
            target_role=target_role,
            missing_skills=active_gaps,
            candidate_name=cand_name
        )
        state["tailored_resume"] = tailored_resume

        # 5. Personalized 30-60-90 Day Upskilling Roadmap
        weekly_hours = state.get("study_pace_hours_per_week", 10)
        roadmap = self.roadmap_agent.generate_roadmap(
            target_role=target_role,
            missing_skills=active_gaps,
            candidate_summary=state.get("resume_data", {}).get("work_summary", ""),
            weekly_hours=weekly_hours
        )
        state["career_roadmap"] = roadmap

        # 6. Multi-Format Learning Pack & Live GitHub Reference Projects
        resource_pack = self.rag_curator.curate(missing_skills=active_gaps)
        state["learning_resources"] = resource_pack
        state["curated_courses"] = resource_pack.get("courses", [])

        discovered_projects = self.project_generator.generate(
            missing_skills=active_gaps,
            target_role=target_role
        )
        state["project_blueprints"] = discovered_projects
        state["github_projects"] = discovered_projects

        return state
