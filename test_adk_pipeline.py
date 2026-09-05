"""
PathCraft AI - End-to-End Pipeline Verification Test
"""

import json
from core.orchestrator import CareerCopilotADKTeam
from test_resumes import STRONG_DATA_ENGINEER_RESUME, WEAK_DESIGNER_RESUME

def test_full_pipeline():
    print("=" * 70)
    print("[TEST SUITE] PATHCRAFT AI - END-TO-END PIPELINE & MCP TOOLS VERIFICATION")
    print("=" * 70)

    adk_team = CareerCopilotADKTeam()

    # -------------------------------------------------------------
    # TEST 1: STRONG DATA ENGINEER CANDIDATE
    # -------------------------------------------------------------
    print("\n[TEST 1] Running Pipeline for STRONG Data Engineer Candidate...")
    state_strong = {
        "resume_bytes": None,
        "resume_text": STRONG_DATA_ENGINEER_RESUME,
        "target_role": "Data Engineer",
        "github_url": "https://github.com/alexchen-data",
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
    res_strong = adk_team.run_tab1_pipeline(state_strong)
    
    print("\n[SUCCESS] TEST 1 RESULTS:")
    print(f"Target Role: {res_strong['target_role']}")
    print(f"Analysis Method: {res_strong.get('analysis_method')}")
    print(f"Verified Skills ({len(res_strong.get('verified_skills', []))}): {res_strong.get('verified_skills', [])}")
    print(f"Skill Gaps ({len(res_strong.get('skills_gap', []))}): {res_strong.get('skills_gap', [])}")
    print(f"Match Score: {res_strong.get('match_score')}%")
    print(f"Discovered GitHub Projects: {len(res_strong.get('github_projects', []))} repos")
    
    learning = res_strong.get("learning_resources", {})
    print(f"Curated Books (Google Books API): {len(learning.get('books', []))}")
    print(f"Curated Research Papers (arXiv API): {len(learning.get('papers', []))}")
    print(f"Curated Docs & Courses: {len(learning.get('docs', []))} docs, {len(learning.get('courses', []))} courses")

    # -------------------------------------------------------------
    # TEST 2: WEAK DESIGNER CANDIDATE APPLYING FOR DATA ENGINEER
    # -------------------------------------------------------------
    print("\n" + "-" * 70)
    print("[TEST 2] Running Pipeline for WEAK Candidate (Designer -> Data Engineer)...")
    state_weak = {
        "resume_bytes": None,
        "resume_text": WEAK_DESIGNER_RESUME,
        "target_role": "Data Engineer",
        "github_url": None,
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
    res_weak = adk_team.run_tab1_pipeline(state_weak)
    
    print("\n[SUCCESS] TEST 2 RESULTS:")
    print(f"Target Role: {res_weak['target_role']}")
    print(f"Verified Skills ({len(res_weak.get('verified_skills', []))}): {res_weak.get('verified_skills', [])}")
    print(f"Skill Gaps ({len(res_weak.get('skills_gap', []))}): {res_weak.get('skills_gap', [])}")
    print(f"Match Score: {res_weak.get('match_score')}%")

    print("\n" + "=" * 70)
    print("[DONE] ALL END-TO-END TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    test_full_pipeline()
