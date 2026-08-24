import os
from core.parsers.resume_parser import parse_resume

# Sample Resume Text for testing
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

EDUCATION:
B.S. in Computer Science, University of California, Berkeley (2020)

SKILLS:
Python, PySpark, SQL, BigQuery, Apache Airflow, Docker, Git, GCP, PostgreSQL
"""

if __name__ == "__main__":
    print("Testing Resume Parser Agent with Gemini 2.5 Flash...")
    print("=" * 60)
    
    # Run resume parser
    result = parse_resume(resume_text=SAMPLE_RESUME)
    
    print("\n[SUCCESS] Extracted Resume Schema:")
    import json
    print(json.dumps(result, indent=2))
