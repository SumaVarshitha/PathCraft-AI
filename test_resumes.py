"""
PathCraft AI - Test Resumes Benchmark Dataset
Contains 2 calibrated resumes to verify semantic matching accuracy:
1. STRONG_DATA_ENGINEER_RESUME: Expected Match ~85-95% for Data Engineer
2. WEAK_DESIGNER_RESUME: Expected Match < 35% for Data Engineer
"""

STRONG_DATA_ENGINEER_RESUME = """
Alex Chen
Senior Data Engineer | alex.chen@example.com | San Francisco, CA | github.com/alexchen-data

SUMMARY
Senior Data Engineer with 5+ years of experience architecting petabyte-scale distributed data pipelines, lakehouse architectures, and real-time streaming infrastructure. Proficient in Python, SQL, Apache Spark, PySpark, Google Cloud BigQuery, and Airflow workflow orchestration.

TECHNICAL SKILLS
- Programming Languages: Python, SQL, Scala, Bash
- Distributed Computing & Big Data: Apache Spark, PySpark, Apache Kafka, Hadoop
- Cloud & Data Warehousing: Google Cloud Platform (GCP), BigQuery, Snowflake, Amazon Redshift
- Orchestration & DevOps: Apache Airflow, Docker, Kubernetes, Terraform, Git, CI/CD
- Data Modeling: Dimensional Modeling, Star Schema, dbt, ETL / ELT Pipeline Architecture

PROFESSIONAL EXPERIENCE
Senior Data Platform Engineer | CloudData Corp | 2022 - Present
- Designed and deployed streaming ETL pipelines using PySpark and Kafka, ingesting 200M+ events daily into Google Cloud BigQuery with 99.9% uptime.
- Orchestrated 45+ critical production DAGs using Apache Airflow, reducing data latency by 40%.
- Containerized data services using Docker and managed cloud deployments via Terraform.

PROJECTS
1. Real-Time Lakehouse Streaming Ingestion Engine
   - Built an end-to-end real-time ingestion pipeline using PySpark, Delta Lake, and BigQuery.
   - Automated data quality assertions using dbt and Docker containers.
   - Tech Stack: Python, PySpark, Apache Spark, BigQuery, Docker, Git.

2. Enterprise Orchestration & ETL Pipeline Framework
   - Created reusable Airflow DAG templates for extracting API data into PostgreSQL and BigQuery warehouses.
   - Tech Stack: Python, Apache Airflow, SQL, PostgreSQL, Docker, GCP.

CERTIFICATIONS & EDUCATION
- Google Cloud Certified Professional Data Engineer (GCP PDE)
- B.S. in Computer Science, University of California, Berkeley
"""

WEAK_DESIGNER_RESUME = """
Jordan Miller
UI/UX Graphic Designer | jordan.miller@example.com | New York, NY

SUMMARY
Creative Visual and UI/UX Designer with 3 years of experience crafting wireframes, brand design systems, and responsive website landing pages. Passionate about typography, user research, and interactive prototyping.

SKILLS
- Design Tools: Figma, Adobe XD, Adobe Photoshop, Adobe Illustrator, InVision
- Web Design: HTML5, CSS3, Responsive Design, Typography, Color Theory
- Methodologies: User Research, Wireframing, Rapid Prototyping, Usability Testing

EXPERIENCE
Junior Product Designer | CreativeStudio Agency | 2023 - Present
- Designed high-fidelity prototypes and UI component libraries in Figma for e-commerce clients.
- Conducted user interviews and usability testing sessions to improve app navigation.
- Created responsive HTML/CSS landing pages for promotional marketing campaigns.

PROJECTS
1. Mobile Food Delivery App UI Redesign
   - Developed interactive mobile prototypes in Figma and Adobe Illustrator.
   - Tech Stack: Figma, Adobe Photoshop, User Testing.

EDUCATION
- B.A. in Graphic Design & Visual Arts, Pratt Institute
"""
