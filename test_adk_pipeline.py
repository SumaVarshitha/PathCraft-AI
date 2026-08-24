import os
import json
from core.orchestrator import CareerCopilotADKTeam

SAMPLE_RESUME = """
Jane Doe
Senior Data Engineer | San Francisco, CA | jane.doe@example.com

SUMMARY:
Data Engineer with 5+ years of experience building scalable data pipelines on Google Cloud Platform.
Expert in Python, SQL, Apache Spark, PySpark, and BigQuery. Familiar with Docker and Airflow.

EXPERIENCE:
Data Engineer at CloudData Inc (2021 - Present)
- Built real-time streaming pipelines using PySpark and Kafka, processing 5TB daily.
- Optimized BigQuery data warehouse queries, reducing monthly GCP costs by 25%.
- Containerized ETL applications using Docker and orchestrated workflows with Apache Airflow.

SKILLS:
Python, PySpark, SQL, BigQuery, Apache Airflow, Docker, Git, GCP, PostgreSQL
"""

if __name__ == "__main__":
    print("Testing Google ADK 2.0 Multi-Agent Team Pipeline...")
    print("=" * 60)
    
    adk_team = CareerCopilotADKTeam()
    
    initial_state = {
        "resume_bytes": None,
        "resume_text": SAMPLE_RESUME,
        "target_role": "Data Engineer",
        "github_url": None,
        "linkedin_url": None,
        "resume_data": None,
        "github_data": None,
        "linkedin_data": None,
        "unified_skills": [],
        "skills_gap": [],
        "match_score": 0.0,
        "curated_courses": [],
        "project_blueprints": [],
        "interview_history": []
    }
    
    try:
        final_state = adk_team.run_tab1_pipeline(initial_state)
        print("\n[SUCCESS] Google ADK 2.0 Team Output:")
        print(f"Verified Skills: {final_state.get('unified_skills')}")
        print(f"Skills Gap: {final_state.get('skills_gap')}")
        print(f"Match Score: {final_state.get('match_score')}%")
        print("\nCurated Courses (Sample):")
        print(json.dumps(final_state.get('curated_courses', []), indent=2))
    except Exception as e:
        print(f"[TEST EXCEPTION]: {e}")
