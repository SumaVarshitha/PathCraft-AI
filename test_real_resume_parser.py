import os
import json
from google import genai
from google.genai import types

api_key = os.getenv("GOOGLE_API_KEY")
print(f"GOOGLE_API_KEY present: {bool(api_key)}")

if api_key:
    client = genai.Client(api_key=api_key)
    sample_text = """
    SUMAVARSHITHA KAMATAM
    Email: sumavarshitha@example.com | LinkedIn: linkedin.com/in/sumavarshitha

    PROFESSIONAL EXPERIENCE:
    AI / Data Systems Engineer — Tech Innovations Inc. (2022 - Present)
    - Designed and deployed a production-grade AI Failure Analysis Agent (tool-calling + RAG) integrated with cloud telemetry.
    - Built LLM-powered agentic systems with single-agent and multi-agent reasoning patterns for security and workflow automation.
    - Applied systematic prompt engineering to ensure reliable, auditable, and deterministic automation outputs.
    - Developed GenAI UI system that converts natural language prompts into dynamic dashboards.
    - Built an agentic data-insights platform using LangGraph + GenSQL, enabling API-based database connectivity.
    - Architected fully automated CI/CD orchestration system (Docker + Jenkins + Groovy) executing 400+ daily builds.

    EDUCATION:
    B.Tech in Computer Science and Engineering — University of Technology (2018 - 2022)

    PROJECTS:
    - LangGraph Multi-Agent Workflow Engine: Built autonomous multi-agent orchestration for enterprise analytics.
    - GenSQL Query Synthesizer: Developed NL-to-SQL agent with schema grounding.
    """

    prompt = f"""
    You are an expert technical resume parser. Analyze this resume text and extract the candidate's authentic profile into a complete JSON object.
    
    CRITICAL REQUIREMENTS:
    1. Extract all technical skills and tools (including LangGraph, RAG, Tool-Calling, Multi-Agent Systems, GenSQL, Prompt Engineering, Docker, Jenkins, Groovy, Python, SQL).
    2. Extract all real work experience with exact company names, roles, duration, and all bullet points.
    3. Extract all projects with their titles, descriptions, and tech stacks.
    4. Extract real education degrees and institutions.
    5. Calculate accurate total years of experience.

    Resume Text:
    {sample_text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.0
            )
        )
        print("\n--- GEMINI RESPONSE ---")
        print(response.text)
    except Exception as e:
        print(f"\n--- ERROR ---: {e}")
