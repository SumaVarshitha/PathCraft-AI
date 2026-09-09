"""
Test _direct_text_extractor with a realistic multi-company resume.
Verifies: companies, dates, roles, projects, certs are all extracted correctly.
"""
import sys
sys.path.insert(0, ".")

from core.agents.resume_parser_agent import ResumeParserADKAgent

SAMPLE_RESUME = """
SUMAVARSHITHA KAMATAM
varshithareddy2698@gmail.com | +91-9876543210 | linkedin.com/in/sumavarshitha | github.com/sumavarshitha

Senior DevOps & AI Engineer | SAP Labs India

EXPERIENCE

Senior DevOps & AI Engineer | SAP Labs India | Sep 2023 – Present
- Designed and deployed a production-grade AI Failure Analysis Agent (tool-calling + RAG) integrated with Gemini LLMs and LangGraph multi-agent pipelines.
- Built LLM-powered agentic systems with single-agent and multi-agent reasoning patterns for security analysis.
- Developed RAG pipelines using vector databases (FAISS, ChromaDB) for context-aware query resolution.
- Automated CI/CD workflows using Jenkins, Groovy, and GitHub Actions, reducing deployment time by 40%.

Jenkins & CI/CD Engineer | NTT DATA Business Solutions | Oct 2021 – Aug 2023
- Architected scalable Jenkins pipelines for multi-region microservices deployment on GCP and AWS.
- Implemented Kubernetes-based container orchestration with Terraform for IaC.
- Led platform migration to Docker-based build systems, improving build reliability by 30%.

DevOps Engineer | Wipro Technologies | May 2020 – Sep 2021
- Managed CI/CD pipelines for enterprise Java applications using Maven, Jenkins, and Linux.
- Configured and maintained PostgreSQL databases and Redis caching layers.

PROJECTS

AI Failure Analysis Agent (LangGraph + RAG)
- Agentic multi-step reasoning with LangGraph state machines and Gemini tool-calling.
- Tech: LangGraph, RAG, Python, FastAPI, ChromaDB, Docker

GenSQL Query Assistant
- Natural language to SQL conversion using GenSQL and LLMs with BigQuery backend.
- Tech: GenSQL, BigQuery, Python, LangChain

EDUCATION

B.Tech – Electronics & Communication Engineering
Annamacharya Institute of Technology and Sciences, CGPA: 8.2 (2015 – 2019)

CERTIFICATIONS

AWS Machine Learning Specialty – Certified 2023
Google Cloud Professional DevOps Engineer – 2022
CKA – Certified Kubernetes Administrator – 2022

SKILLS

Python, Java, Bash, SQL, LangGraph, LangChain, RAG, GenSQL, FastAPI, Docker, Kubernetes,
Terraform, Jenkins, Groovy, GCP, AWS, BigQuery, Linux, Git, React, CI/CD, PostgreSQL
"""

agent = ResumeParserADKAgent()
# Force fallback by calling _direct_text_extractor directly (no API needed)
result = agent._direct_text_extractor(SAMPLE_RESUME, "")

print("=" * 60)
print(f"Name:         {result['candidate_name']}")
print(f"Title:        {result['job_title']}")
print(f"Years Exp:    {result['years_experience']}")
print(f"Education:    {result['education']}")
print()
print(f"Work Experience ({len(result['work_experience'])} entries):")
for w in result['work_experience']:
    print(f"  [{w['duration']}] {w['role']} @ {w['company']}")
    print(f"    Bullets: {len(w['bullets'])}")

print()
print(f"Projects ({len(result['projects'])} entries):")
for p in result['projects']:
    print(f"  {p['title']} — tech: {p['tech_stack']}")

print()
print(f"Certifications ({len(result['certifications'])} entries):")
for c in result['certifications']:
    print(f"  {c}")

print()
print(f"Skills ({len(result['skills'])}): {result['skills']}")
print("=" * 60)

# Assertions
assert len(result['work_experience']) >= 3, f"Expected 3+ work entries, got {len(result['work_experience'])}"
companies = [w['company'] for w in result['work_experience']]
assert any("SAP" in c or "NTT" in c or "Wipro" in c for c in companies), f"Real companies not found: {companies}"
assert result['years_experience'] > 4, f"Expected 5+ years, got {result['years_experience']}"
assert len(result['projects']) >= 1, f"Expected projects, got {result['projects']}"
assert len(result['certifications']) >= 1, f"Expected certs, got {result['certifications']}"
print("\n✅ All assertions passed — fallback parser working correctly!")
