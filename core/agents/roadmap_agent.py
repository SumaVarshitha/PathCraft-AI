import os
from typing import Dict, Any, List, Optional
from google.genai import types
from pydantic import BaseModel, Field
import config
from core.adk_agent import ADKAgent

class MilestoneWeek(BaseModel):
    week_number: int = Field(description="Week number (1 to 12)")
    focus_topic: str = Field(description="Core technical theme or tool for this week")
    estimated_hours: int = Field(default=10, description="Estimated hours to complete weekly goals")
    action_items: List[str] = Field(description="Specific hands-on exercises, chapters, or code deliverables")
    learning_deliverable: str = Field(description="Tangible artifact, GitHub commit, or code created by end of week")

class RoadmapPhase(BaseModel):
    phase_title: str = Field(description="Phase title")
    duration_days: str = Field(description="Duration (e.g. Days 1-30)")
    key_objectives: List[str] = Field(description="Primary high-level learning and skill goals")
    weeks: List[MilestoneWeek] = Field(description="Weekly breakdown for this phase")

class CareerRoadmapResult(BaseModel):
    target_role: str = Field(description="Target career role")
    weekly_hours_budget: int = Field(default=10, description="Candidate allocated study hours per week")
    executive_summary: str = Field(description="Overview of the upskilling journey")
    phase_1_foundations: RoadmapPhase = Field(description="Phase 1: Core Fundamentals & Tooling")
    phase_2_architecture: RoadmapPhase = Field(description="Phase 2: Systems, Distributed Architecture & Deep Dive")
    phase_3_portfolio_launch: RoadmapPhase = Field(description="Phase 3: Independent Portfolio Build & Job Market Launch")

class RoadmapADKAgent(ADKAgent):
    """
    Google ADK 2.0 Dynamic Career Roadmap Architect Agent
    Synthesizes structured 30-60-90 day personalized upskilling plans tailored to candidate skill gaps
    and their exact weekly time budget (e.g. 5 hrs/week vs 20 hrs/week).
    """
    def __init__(self):
        instruction = """
        You are an elite Principal Staff Engineer and Career Mentor.
        Construct a practical, actionable 30-60-90 Day Upskilling Roadmap tailored to:
        - The candidate's target role and specific missing skill gaps.
        - The candidate's weekly study budget (e.g., 5 hrs/week for working professionals, 20 hrs/week for full-time learners).
        - Phase 1 (Days 1-30): Master core missing tools with hands-on exercises.
        - Phase 2 (Days 31-60): Deep dive into system design and distributed architectures.
        - Phase 3 (Days 61-90): Build an end-to-end portfolio capstone project and prepare for job applications.
        """
        super().__init__(
            name="RoadmapADKAgent",
            instruction=instruction,
            model=config.MODEL_FLASH,
            output_schema=CareerRoadmapResult,
            temperature=0.2
        )

    def generate_roadmap(
        self,
        target_role: str,
        missing_skills: List[str],
        candidate_summary: str = "",
        weekly_hours: int = 10
    ) -> Dict[str, Any]:
        """Synthesizes the customized roadmap."""
        gaps_str = ", ".join(missing_skills[:6]) if missing_skills else "Cloud Architecture & Scalability"
        
        prompt = f"""
        Target Role: {target_role}
        Priority Missing Skills to Master: [{gaps_str}]
        Candidate Background: {candidate_summary[:200] if candidate_summary else 'Technical Professional'}
        Weekly Time Commitment: {weekly_hours} Hours/Week

        Generate a structured 30-60-90 day action roadmap formatted in CareerRoadmapResult JSON.
        Make weekly actions realistic for {weekly_hours} hours/week of dedicated study and coding.
        """

        if self.client:
            try:
                return self.execute(prompt_input=prompt)
            except Exception as e:
                print(f"[RoadmapADKAgent Notice]: ({e}). Using adaptive fallback roadmap.", flush=True)

        return self._offline_fallback_roadmap(target_role, missing_skills, weekly_hours)

    def _offline_fallback_roadmap(self, target_role: str, missing_skills: List[str], weekly_hours: int = 10) -> Dict[str, Any]:
        """Provides heuristic 30-60-90 roadmap when offline."""
        gaps = missing_skills if missing_skills else ["System Design", "Cloud Infrastructure", "Distributed Data"]
        skill_1 = gaps[0] if len(gaps) > 0 else "Core Language & Tools"
        skill_2 = gaps[1] if len(gaps) > 1 else "Cloud Architecture"
        skill_3 = gaps[2] if len(gaps) > 2 else "Scalable Systems"

        return {
            "target_role": target_role,
            "weekly_hours_budget": weekly_hours,
            "executive_summary": f"A targeted trajectory bridging your background to {target_role} at {weekly_hours} hours/week through structured foundations, systems design, and a complete open-source capstone.",
            "phase_1_foundations": {
                "phase_title": "Phase 1: Core Fundamentals & Tooling",
                "duration_days": "Days 1-30",
                "key_objectives": [
                    f"Establish environment and develop fluency in {skill_1}",
                    "Complete daily hands-on implementation labs and unit tests",
                    "Build automated CI testing for your exercises"
                ],
                "weeks": [
                    {
                        "week_number": 1,
                        "focus_topic": f"{skill_1} Core Syntax & CLI Workflows",
                        "estimated_hours": weekly_hours,
                        "action_items": [f"Install toolchains, study core paradigms, and build a local {skill_1} prototype", "Implement error logging and unit assertions"],
                        "learning_deliverable": f"Working GitHub repo containing basic {skill_1} scripts"
                    },
                    {
                        "week_number": 2,
                        "focus_topic": f"{skill_1} Data Structures & Internal APIs",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Study official documentation and implement automated test fixtures", "Profile runtime performance"],
                        "learning_deliverable": "Benchmark test report with memory metrics"
                    },
                    {
                        "week_number": 3,
                        "focus_topic": f"{skill_2} Setup & Integration",
                        "estimated_hours": weekly_hours,
                        "action_items": [f"Connect {skill_1} to {skill_2} in Docker container environment", "Write ingestion script"],
                        "learning_deliverable": "Docker Compose setup with connected services"
                    },
                    {
                        "week_number": 4,
                        "focus_topic": "Phase 1 Consolidation Lab",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Combine all components into a clean demo pipeline", "Conduct code review"],
                        "learning_deliverable": "Functional end-to-end prototype on GitHub"
                    }
                ]
            },
            "phase_2_architecture": {
                "phase_title": "Phase 2: Systems, Distributed Architecture & Deep Dive",
                "duration_days": "Days 31-60",
                "key_objectives": [
                    f"Master distributed workflows with {skill_2} and {skill_3}",
                    "Implement observability, schema validation, and retry mechanisms",
                    "Study system design trade-offs and research preprints"
                ],
                "weeks": [
                    {
                        "week_number": 5,
                        "focus_topic": f"{skill_2} Distributed Operations",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Configure multi-node or partitioned processing", "Simulate network partitioning"],
                        "learning_deliverable": "Resilience test suite with logs"
                    },
                    {
                        "week_number": 6,
                        "focus_topic": f"{skill_3} Cloud Integration",
                        "estimated_hours": weekly_hours,
                        "action_items": [f"Deploy {skill_3} instances and optimize query cost", "Setup monitoring dashboards"],
                        "learning_deliverable": "Cloud infrastructure configuration scripts"
                    },
                    {
                        "week_number": 7,
                        "focus_topic": "Scalability & Performance Tuning",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Optimize query execution plans and caching", "Implement Prometheus metrics"],
                        "learning_deliverable": "Performance tuning technical write-up"
                    },
                    {
                        "week_number": 8,
                        "focus_topic": "System Design Synthesis",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Create architecture diagrams in Mermaid", "Document fault tolerance decisions"],
                        "learning_deliverable": "Complete Architecture RFC document"
                    }
                ]
            },
            "phase_3_portfolio_launch": {
                "phase_title": "Phase 3: Independent Portfolio Build & Job Market Launch",
                "duration_days": "Days 61-90",
                "key_objectives": [
                    f"Develop a production-grade showcase project using {skill_1}, {skill_2}, and {skill_3}",
                    "Write an authoritative README, architecture guide, and live demo",
                    "Tailor resume, conduct mock interviews, and launch job applications"
                ],
                "weeks": [
                    {
                        "week_number": 9,
                        "focus_topic": "Capstone Architecture & Data Modeling",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Initialize repository and setup automated GitHub Actions CI/CD", "Define schemas and endpoints"],
                        "learning_deliverable": "Clean repository skeleton with CI passes"
                    },
                    {
                        "week_number": 10,
                        "focus_topic": "Core Implementation & Testing",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Build core processing pipelines and API layer", "Achieve >80% test coverage"],
                        "learning_deliverable": "Complete application codebase"
                    },
                    {
                        "week_number": 11,
                        "focus_topic": "Production Packaging & Documentation",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Create 1-click Docker run command and architectural diagrams", "Record 2-minute video walkthrough"],
                        "learning_deliverable": "Recruiter-ready showcase portfolio on GitHub"
                    },
                    {
                        "week_number": 12,
                        "focus_topic": "Interview Simulations & Targeted Applications",
                        "estimated_hours": weekly_hours,
                        "action_items": ["Conduct 5 multi-turn mock interview rounds", "Submit 10 targeted job applications with tailored resume"],
                        "learning_deliverable": "Active interview pipelines with prospective employers"
                    }
                ]
            }
        }
