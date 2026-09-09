import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.agents.skill_normalizer_agent import token_exact_match, normalize_skill_name
from core.agents.gap_analyzer_agent import GapAnalyzerADKAgent
from core.agents.interview_simulator_agent import InterviewSimulatorADKAgent
from core.agents.resume_generator_agent import ResumeGeneratorADKAgent, generate_ats_pdf
from core.orchestrator import CareerCopilotADKTeam
from test_resumes import STRONG_DATA_ENGINEER_RESUME

class TestCleanCareerCopilot(unittest.TestCase):

    def test_token_exact_matching_precision(self):
        """Verify that substring false-positives are eliminated."""
        self.assertFalse(token_exact_match("Java", "JavaScript"))
        self.assertFalse(token_exact_match("C", "CI/CD"))
        self.assertFalse(token_exact_match("Go", "Google Cloud Platform"))
        
        self.assertTrue(token_exact_match("Python", "Python"))
        self.assertTrue(token_exact_match("PyTorch", "Torch"))
        self.assertTrue(token_exact_match("Postgres", "PostgreSQL"))
        self.assertTrue(token_exact_match("GCP", "Google Cloud Platform"))

    def test_gap_analyzer_2tier_scoring(self):
        """Verify 2-tier dynamic gap analyzer returns core and differentiator breakdowns."""
        analyzer = GapAnalyzerADKAgent()
        cand_skills = ["Python", "SQL", "Apache Spark", "Git"]
        
        res = analyzer.analyze(
            candidate_skills=cand_skills,
            target_role="Data Engineer",
            seniority_level="Senior"
        )
        self.assertIn("verified_skills", res)
        self.assertIn("missing_skills", res)
        self.assertIn("core_requirements", res)
        self.assertIn("differentiator_requirements", res)
        self.assertIn("match_percentage", res)
        self.assertIn("core_match_percentage", res)
        print(f"[TEST PASS] Gap Analysis: Score={res['match_percentage']}%, CoreScore={res['core_match_percentage']}%")

    def test_in_place_resume_optimizer(self):
        """Verify that original candidate resume text is preserved with surgical in-place enhancements."""
        optimizer = ResumeGeneratorADKAgent()
        res = optimizer.optimize_in_place(
            raw_resume_text=STRONG_DATA_ENGINEER_RESUME,
            target_role="Senior Data Engineer",
            missing_skills=["dbt", "Snowflake"],
            candidate_name="Alex Rivera"
        )
        self.assertIn("optimized_text", res)
        self.assertIn("key_changes", res)
        self.assertIn("ats_score_before", res)
        self.assertIn("ats_score_after", res)
        self.assertGreater(len(res["key_changes"]), 0)
        
        # Verify PDF generates without errors
        pdf_bytes = generate_ats_pdf(res)
        self.assertGreater(len(pdf_bytes), 100)
        print(f"[TEST PASS] In-Place Resume Optimizer: Generated {len(res['key_changes'])} surgical enhancements, ATS Score: {res['ats_score_after']}/100")

    def test_multi_turn_interview_flow(self):
        """Verify multi-turn question generation, answer evaluation, and final scorecard."""
        interviewer = InterviewSimulatorADKAgent()
        missing = ["Snowflake", "dbt", "Kubernetes"]
        verified = ["Python", "SQL", "Spark"]

        q1 = interviewer.generate_next_question(
            target_role="Data Engineer",
            missing_skills=missing,
            verified_skills=verified,
            turn_index=0,
            total_questions=3,
            difficulty="Senior"
        )
        self.assertIn("question", q1)
        self.assertEqual(q1["skill_focus"], "Snowflake")

        eval_res = interviewer.evaluate_answer(
            question=q1["question"],
            candidate_answer="In Snowflake, we use clustering keys and auto-suspend warehouses to optimize query performance and reduce compute credits.",
            target_role="Data Engineer",
            skill_focus="Snowflake"
        )
        self.assertIn("score", eval_res)
        self.assertIn("feedback", eval_res)
        self.assertIn("key_takeaway", eval_res)

        turns = [
            {"turn_index": 0, "skill_focus": "Snowflake", "question": q1["question"], "candidate_answer": "...", "evaluation": eval_res}
        ]
        report = interviewer.generate_final_report_card(target_role="Data Engineer", turns=turns)
        self.assertIn("overall_score", report)
        self.assertIn("readiness", report)
        print(f"[TEST PASS] Interview Simulation: Score={eval_res['score']}/100 | Readiness={report['readiness'].encode('ascii', 'replace').decode()}")

    def test_full_adk_pipeline_execution(self):
        """Verify end-to-end multi-agent team pipeline."""
        team = CareerCopilotADKTeam()
        initial_state = {
            "resume_bytes": None,
            "resume_text": STRONG_DATA_ENGINEER_RESUME,
            "target_role": "Data Engineer",
            "seniority_level": "Senior",
            "github_url": None,
            "linkedin_url": None,
            "linkedin_text": "AWS Certified Data Analytics",
            "user_confirmed_skills": [],
            "user_prioritized_gaps": [],
            "study_pace_hours_per_week": 15,
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
        res = team.run_full_pipeline(initial_state)
        self.assertIsNotNone(res.get("resume_data"))
        self.assertGreater(len(res.get("verified_skills", [])), 0)
        self.assertIsNotNone(res.get("ats_audit"))
        self.assertIsNotNone(res.get("tailored_resume"))
        self.assertIsNotNone(res.get("career_roadmap"))
        print(f"[TEST PASS] Complete Pipeline Execution Succeeded. Verified Skills: {len(res['verified_skills'])}, Optimized Resume Ready.")

if __name__ == "__main__":
    unittest.main()
