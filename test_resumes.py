"""
PathCraft AI - Test Resumes Benchmark Dataset
Contains 4 calibrated resumes to verify semantic matching accuracy:
1. STRONG_DATA_ENGINEER_RESUME: Expected Match ~85-95% for Data Engineer
2. AIML_ENGINEER_RESUME: Expected Match ~85-95% for AI/ML Engineer
3. FULLSTACK_DEVELOPER_RESUME: Expected Match ~85-95% for Fullstack Developer
4. WEAK_DESIGNER_RESUME: Expected Match < 35% for Data Engineer
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

AIML_ENGINEER_RESUME = """
Maya Lin
Senior AI / ML Systems Engineer | maya.lin@example.com | Seattle, WA | github.com/mayalin-ai

SUMMARY
Senior AI/ML Engineer with 4+ years of experience building autonomous multi-agent workflows, production RAG systems, and fine-tuning LLMs for enterprise applications. Expert in Python, PyTorch, LangGraph, Vector Databases, and FastAPI microservices.

TECHNICAL SKILLS
- Languages & Frameworks: Python, PyTorch, LangGraph, LangChain, LlamaIndex, FastAPI, Scikit-Learn
- AI & LLM Engineering: Multi-Agent Systems, RAG, Prompt Engineering, Tool-Calling, Fine-Tuning, LoRA
- Vector Databases: Pinecone, Qdrant, ChromaDB, pgvector
- Cloud & Infrastructure: Google Cloud Platform (GCP), Vertex AI, Docker, Kubernetes, CI/CD, Git

PROFESSIONAL EXPERIENCE
Senior AI Systems Engineer | NextGen AI Labs | 2022 - Present
- Architected an enterprise multi-agent research copilot using LangGraph and Gemini models, serving 50k+ daily queries with sub-second response latency.
- Implemented hybrid dense/sparse RAG pipelines using Qdrant and vector embeddings, improving context retrieval precision by 35%.
- Fine-tuned open-source LLMs using PyTorch and LoRA on proprietary enterprise datasets.

PROJECTS
1. Autonomous Multi-Agent Code Auditor
   - Built an agentic workflow using LangGraph, Tool-Calling, and FastAPI for automated code security scanning.
   - Tech Stack: Python, LangGraph, Gemini API, Docker, FastAPI, Qdrant.

2. High-Throughput Semantic Vector Search Engine
   - Engineered scalable RAG search service processing 10M+ technical documentation pages.
   - Tech Stack: Python, PyTorch, Pinecone, Docker, GCP.

CERTIFICATIONS & EDUCATION
- Google Cloud Certified Professional Machine Learning Engineer
- M.S. in Computer Science (Artificial Intelligence), University of Washington
"""

FULLSTACK_DEVELOPER_RESUME = """
David Kim
Fullstack Web Systems Engineer | david.kim@example.com | Austin, TX | github.com/davidkim-dev

SUMMARY
Fullstack Software Engineer with 4+ years of experience developing responsive single-page applications, distributed microservices, and REST/GraphQL APIs. Proficient in React, TypeScript, Node.js, Next.js, and PostgreSQL.

TECHNICAL SKILLS
- Frontend: JavaScript, TypeScript, React, Next.js, Tailwind CSS, HTML5, CSS3, Redux Toolkit
- Backend: Node.js, Express.js, NestJS, Python, FastAPI, REST APIs, GraphQL
- Databases: PostgreSQL, MongoDB, Redis, Prisma ORM
- DevOps & Tools: Docker, Git, GitHub Actions, AWS, Vercel, Jest

PROFESSIONAL EXPERIENCE
Senior Fullstack Developer | WebScale Technologies | 2022 - Present
- Developed high-performance React and Next.js frontend applications visited by 500k+ monthly active users.
- Built scalable Node.js and TypeScript microservices backed by PostgreSQL and Redis caching.
- Integrated automated CI/CD pipelines with GitHub Actions and Docker, cutting deployment time by 50%.

PROJECTS
1. Real-Time Collaborative Project Management Platform
   - Created fullstack Next.js app with real-time WebSocket sync and PostgreSQL backend.
   - Tech Stack: React, TypeScript, Next.js, Tailwind CSS, Node.js, PostgreSQL, Docker.

EDUCATION
- B.S. in Software Engineering, University of Texas at Austin
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
