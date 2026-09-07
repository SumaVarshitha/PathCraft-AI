import os
from typing import Dict, Any, List, Optional
from google.genai import types
from pydantic import BaseModel, Field
import config
from core.adk_agent import ADKAgent

class MilestoneWeek(BaseModel):
    week_number: int = Field(description="Week number (1 to 12)")
    focus_topic: str = Field(description="Core technical theme or tool for this week")
    action_items: List[str] = Field(description="Specific hands-on exercises, chapters, or code deliverables")
    learning_deliverable: str = Field(description="Tangible artifact or code created by end of week")

class RoadmapPhase(BaseModel):
    phase_title: str = Field(description="Phase title (e.g. Phase 1: Core Fundamentals & Tooling (Days 1-30))")
    duration_days: str = Field(description="Duration (e.g. Days 1-30)")
    key_objectives: List[str] = Field(description="Primary high-level learning and skill goals")
    weeks: List[MilestoneWeek] = Field(description="Weekly breakdown for this phase")

class CareerRoadmapResult(BaseModel):
    target_role: str = Field(description="Target career role")
    executive_summary: str = Field(description="2-sentence overview of the upskilling journey")
    phase_1_foundations: RoadmapPhase = Field(description="Days 1-30: Core Fundamentals & Tooling")
    phase_2_architecture: RoadmapPhase = Field(description="Days 31-60: Systems, Distributed Architecture & Deep Dive")
    phase_3_portfolio_launch: RoadmapPhase = Field(description="Days 61-90: Independent Portfolio Build & Job Market Launch")

class RoadmapADKAgent(ADKAgent):
    """
    Google ADK 2.0 Career Roadmap Architect Agent
    Synthesizes structured 30-60-90 day personalized upskilling plans tailored to candidate skill gaps.
    """
    def __init__(self):
        instruction = """
        You are an elite Principal Staff Engineer and Career Mentor.
        Construct a rigorous, practical, and highly actionable 30-60-90 Day Upskilling Roadmap
        designed to systematically close the candidate's technical skill gaps and prepare them for the target role:
        - Phase 1 (Days 1-30): Master core missing languages, libraries, and foundational tools.
        - Phase 2 (Days 31-60): Deep dive into system design, distributed architectures, and research papers.
        - Phase 3 (Days 61-90): Study public GitHub reference repositories, build an independent portfolio project, and launch job search.
        """
        super().__init__(
            name="RoadmapADKAgent",
            instruction=instruction,
            model=config.MODEL_FLASH,
            output_schema=CareerRoadmapResult,
            temperature=0.2
        )

    def _offline_fallback_roadmap(self, target_role: str, missing_skills: List[str]) -> Dict[str, Any]:
        """Provides heuristic 30-60-90 roadmap when offline."""
        gaps = missing_skills if missing_skills else ["System Design", "Cloud Infrastructure", "Distributed Data"]
        skill_1 = gaps[0] if len(gaps) > 0 else "Core Language & Tools"
        skill_2 = gaps[1] if len(gaps) > 1 else "Cloud Architecture"
        skill_3 = gaps[2] if len(gaps) > 2 else "Scalable Systems"

        return {
            "target_role": target_role,
            "executive_summary": f"A targeted 90-day trajectory bridging your profile to {target_role} through structured foundations, architectural deep dives, and real open-source reference implementations.",
            "phase_1_foundations": {
                "phase_title": "Phase 1: Core Fundamentals & Tooling",
                "duration_days": "Days 1-30",
                "key_objectives": [
                    f"Master syntax, core paradigms, and CLI tooling for {skill_1}.",
                    "Study authoritative textbook chapters and official documentation.",
                    "Build small localized script prototypes and automated tests."
                ],
                "weeks": [
                    {
                        "week_number": 1,
                        "focus_topic": f"Foundations of {skill_1}",
                        "action_items": [f"Install SDKs and complete {skill_1} official quickstart tutorial.", "Read chapters 1-3 of recommended technical guide."],
                        "learning_deliverable": "Working local dev environment and baseline sandbox scripts."
                    },
                    {
                        "week_number": 2,
                        "focus_topic": f"Core Mechanics & Data Structures in {skill_1}",
                        "action_items": ["Implement key algorithmic patterns and data validation schemas.", "Write unit tests covering edge cases."],
                        "learning_deliverable": "Tested modular library utility published to personal GitHub."
                    },
                    {
                        "week_number": 3,
                        "focus_topic": f"Tooling & Pipeline Integration with {skill_2}",
                        "action_items": [f"Connect {skill_1} workflows with {skill_2} services.", "Containerize applications using Docker."],
                        "learning_deliverable": "Dockerized container processing local sample datasets."
                    },
                    {
                        "week_number": 4,
                        "focus_topic": "Phase 1 Synthesis & Review",
                        "action_items": ["Review all phase 1 code and benchmark performance bottlenecks.", "Refactor for clean code standards."],
                        "learning_deliverable": "Phase 1 foundational milestone project tagged on GitHub."
                    }
                ]
            },
            "phase_2_architecture": {
                "phase_title": "Phase 2: Systems, Distributed Architecture & Deep Dive",
                "duration_days": "Days 31-60",
                "key_objectives": [
                    f"Analyze distributed consensus, partition strategies, and latency trade-offs for {skill_3}.",
                    "Read seminal arXiv research papers on large-scale system designs.",
                    "Implement fault tolerance, retry backoffs, and observability metrics."
                ],
                "weeks": [
                    {
                        "week_number": 5,
                        "focus_topic": f"Distributed System Patterns with {skill_3}",
                        "action_items": ["Study master-worker architectures and partition sharding.", "Read research papers on stream processing."],
                        "learning_deliverable": "Architecture blueprint diagram illustrating data flow."
                    },
                    {
                        "week_number": 6,
                        "focus_topic": "High-Throughput Ingestion & Storage Optimization",
                        "action_items": ["Configure caching tiers and asynchronous batch processing.", "Tune database indices and schema models."],
                        "learning_deliverable": "Benchmarked prototype achieving 10,000+ operations/sec."
                    },
                    {
                        "week_number": 7,
                        "focus_topic": "Observability, Logging & CI/CD",
                        "action_items": ["Instrument Prometheus metrics, structured JSON logs, and health checks.", "Build GitHub Actions automated CI/CD pipeline."],
                        "learning_deliverable": "Automated build and test workflow passing on GitHub."
                    },
                    {
                        "week_number": 8,
                        "focus_topic": "Phase 2 Architectural Audit",
                        "action_items": ["Conduct architecture review and eliminate Single Points of Failure.", "Document trade-offs in system README."],
                        "learning_deliverable": "Architectural design document and resilience test suite."
                    }
                ]
            },
            "phase_3_portfolio_launch": {
                "phase_title": "Phase 3: Independent Portfolio Build & Job Market Launch",
                "duration_days": "Days 61-90",
                "key_objectives": [
                    "Study top-starred public GitHub reference repositories.",
                    f"Architect and build an original, end-to-end showcase project demonstrating {target_role} competencies.",
                    "Update resume with Google XYZ formula power bullets and begin selective applications."
                ],
                "weeks": [
                    {
                        "week_number": 9,
                        "focus_topic": "Reference Codebase Study & Project Scaffolding",
                        "action_items": ["Clone and inspect public GitHub reference repositories.", "Scaffold repository structure, Dockerfile, and README."],
                        "learning_deliverable": "Initial project repository with system design specification."
                    },
                    {
                        "week_number": 10,
                        "focus_topic": "Core Implementation & Integration",
                        "action_items": [f"Implement end-to-end pipelines combining {skill_1}, {skill_2}, and {skill_3}.", "Write comprehensive test suite."],
                        "learning_deliverable": "Fully functional production codebase with live demo."
                    },
                    {
                        "week_number": 11,
                        "focus_topic": "Documentation, Live Cloud Deployment & Polish",
                        "action_items": ["Deploy project to Google Cloud Run or cloud sandbox.", "Record 2-minute video walkthrough demonstration."],
                        "learning_deliverable": "Live hosted portfolio project with demo video link in README."
                    },
                    {
                        "week_number": 12,
                        "focus_topic": "Resume Tailoring & Market Launch",
                        "action_items": ["Incorporate new project bullet points into ATS-optimized resume.", "Begin warm networking and recruiter outreach."],
                        "learning_deliverable": "Exported ATS-optimized PDF resume and active job applications."
                    }
                ]
            }
        }

    def generate_roadmap(self, target_role: str, missing_skills: List[str], candidate_summary: str = "") -> Dict[str, Any]:
        """Generates structured 30-60-90 day career roadmap."""
        if not self.client:
            return self._offline_fallback_roadmap(target_role, missing_skills)

        try:
            prompt = f"""
            Target Career Role: '{target_role}'
            Identified Technical Skill Gaps: {missing_skills}
            Candidate Background Summary: {candidate_summary}
            
            Synthesize a rigorous, highly actionable 30-60-90 Day Upskilling Roadmap across Phase 1, Phase 2, and Phase 3 in structured CareerRoadmapResult format.
            """
            return self.execute(prompt_input=prompt)
        except Exception as e:
            print(f"[Roadmap Agent Notice]: ({e}). Using fallback roadmap.", flush=True)
            return self._offline_fallback_roadmap(target_role, missing_skills)
