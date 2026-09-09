# 🚀 PathCraft AI - Enterprise Career & Skill Intelligence Copilot

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Google%20ADK-2.0-orange.svg)](https://cloud.google.com/vertex-ai)
[![Models](https://img.shields.io/badge/Gemini-2.5%20Flash%20%2F%20Pro-purple.svg)](https://deepmind.google/technologies/gemini/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **PathCraft AI** is an enterprise-grade autonomous multi-agent career intelligence platform powered by **Google ADK 2.0 (Agent Development Kit)**, **Gemini 2.5**, **Dynamic Vector Semantic RAG**, and **Model Context Protocol (MCP)** tools. Featuring a Human-in-the-Loop (HITL) architecture, it dynamically diagnoses 2-tier weighted skill gaps against live 2026 hiring markets, audits ATS resumes with live in-browser editing, customizes 30-60-90 day upskilling roadmaps by weekly study budget, conducts interactive multi-turn AI mock interviews, curates learning packs, and connects candidates directly to live active job openings with match percentages.

---

## 📑 Table of Contents

- [Key Upgrades & Architecture](#-key-upgrades--architecture)
- [Interactive 6-Hub Workspace](#-interactive-6-hub-workspace)
- [The 10 Autonomous Agents](#-the-10-autonomous-agents)
- [Project Directory Structure](#-project-directory-structure)
- [Installation & Setup](#-installation--setup)
- [Running the Applications](#-running-the-applications)
- [REST API Reference & Endpoints](#-rest-api-reference--endpoints)
- [Testing & Validation](#-testing--validation)

---

## 🌟 Key Upgrades & Architecture

### 1. 👤 Human-in-the-Loop (HITL) Workflow
- **Candidate Skill Verification**: Step 1 parsing presents an interactive chip editor to review, add, remove, and confirm extracted skills before running analysis.
- **Skill Gap Prioritization**: Choose specific priority gaps to focus on rather than forcing an all-or-nothing trajectory.
- **In-Browser Resume Editor**: Live markdown editor in Hub 2 allows in-place modifications to bullet points and summary text with real-time PDF/Markdown export.

### 2. 🔬 Dynamic Non-Hardcoded 2-Tier Skill Gap Analyzer
- **100% Dynamic Market Grounding**: Queries live 2026 hiring requirements across tech companies via Google Search Grounding for any selected or custom target role and seniority.
- **2-Tier 70/30 Weighted Scoring**:
  $$\text{Match Score} = 0.70 \times \left(\frac{\text{Verified Core}}{\text{Total Core}}\right) + 0.30 \times \left(\frac{\text{Verified Differentiators}}{\text{Total Differentiators}}\right)$$
- **Deep Evidence Ingestion**: Indexes Skills section, Work Experience bullet points, Project tech stacks, Certifications, GitHub languages, and LinkedIn achievements.
- **Strict Token-Aware Matching**: Eliminates false substring matches (e.g. `Java` $\leftrightarrow$ `JavaScript`, `C` $\leftrightarrow$ `CI/CD`).

### 3. 🎙️ Multi-Turn Conversational AI Mock Interview Hub
- **Realistic Scenario-Based Q&A**: Progressively asks 3, 5, or 10 technical questions testing missing skill gaps (70%) and core architecture (30%).
- **Turn-by-Turn Evaluation**: Instant 0–100 rubric score, constructive strengths/gaps feedback, and production model answers.
- **Final Performance Scorecard**: Cumulative average, Hiring Readiness rating (*Strong Hire / Mid-Senior / Needs Practice*), and downloadable transcript.

### 4. 💼 Live Job Opportunities & 1-Click Application Portal
- **Configurable Results (5 to 30+ Jobs)**: Real-time active job openings via Google Search Grounding with locations, estimated salary ranges, and direct apply links.
- **Dynamic Candidate Match Score (%)**: Computed against candidate verified skills.

---

## 🖥️ Interactive 6-Hub Workspace

1. **📊 1. Skill Gap Diagnostic (HITL)**: Dynamic 2-tier breakdown, verified skills chip editor, and granular semantic matching table with cosine similarity scores.
2. **🎯 2. ATS Audit & Live Resume Editor**: 100-point ATS scorecard, Google XYZ power bullet rewriter, in-browser live editor, and 1-click PDF/Markdown downloads.
3. **📅 3. Dynamic Action Roadmap**: 30-60-90 day milestone roadmap tailored to candidate's weekly study budget (5–30 hrs/wk) with interactive progress tracking.
4. **📚 4. Learning Pack & GitHub Repos**: Curated technical books (Google Books), arXiv research preprints, official docs, video courses, and real GitHub reference repositories.
5. **🎙️ 5. AI Mock Interview Hub**: Multi-turn conversational interview with real-time scoring, feedback, model solutions, and final scorecard.
6. **💼 6. Live Job Opportunities**: Active hiring vacancies with match percentages, salary estimates, and direct apply links.

---

## 🤖 The 10 Autonomous Agents

| # | Agent Name | Primary Responsibility |
|---|------------|------------------------|
| **1** | `ResumeParserADKAgent` | Ingests multi-page PDFs, work experience bullets, projects, certs, and LinkedIn. |
| **2** | `GitHubInspectorADKAgent` | Inspects GitHub repositories and languages via GitHub MCP. |
| **3** | `SkillNormalizerADKAgent` | Token-exact canonicalization and strict alias resolution. |
| **4** | `GapAnalyzerADKAgent` | Dynamic 2-tier 70/30 weighted gap analysis with Gemini Vector Embeddings. |
| **5** | `ATSAnalyzerADKAgent` | 100-point ATS audit and Google XYZ formula power bullet optimizer. |
| **6** | `ResumeGeneratorADKAgent` | Synthesizes recruiter-ready tailored resumes in PDF & Markdown. |
| **7** | `RoadmapADKAgent` | 30-60-90 day upskilling roadmap customized to candidate's weekly time budget. |
| **8** | `RAGCuratorADKAgent` | Multi-format learning packs (Google Books API, arXiv API, Docs, Videos). |
| **9** | `ProjectGeneratorADKAgent` | Real public GitHub reference repositories and architecture blueprints. |
| **10** | `LiveJobMarketADKAgent` | Live job vacancies with match scoring and direct apply links. |
| **11** | `InterviewSimulatorADKAgent` | Multi-turn conversational mock interviewer with rubric scoring and report card. |

---

## 📁 Project Directory Structure

```plaintext
ai_career_copilot/
├── api_server.py                 # FastAPI REST API server with interactive Swagger docs
├── app.py                        # Streamlit 6-Hub interactive web dashboard
├── config.py                     # Global model and environment configuration
├── requirements.txt              # Production dependencies
├── Dockerfile                    # Container configuration
│
├── core/                         # Core ADK 2.0 Engine & Agents
│   ├── adk_agent.py              # Base Google ADK 2.0 Agent & Tool abstractions
│   ├── state.py                  # Pydantic data schemas & ADKState TypedDict
│   ├── orchestrator.py           # CareerCopilotADKTeam Multi-Agent Pipeline
│   │
│   ├── agents/                   # Autonomous ADK 2.0 Agents
│   │   ├── resume_parser_agent.py      # Agent 1: Deep Profile & Context Parser
│   │   ├── github_inspector_agent.py   # Agent 2: GitHub MCP Profiler
│   │   ├── skill_normalizer_agent.py   # Agent 3: Token-Exact Skill Normalizer
│   │   ├── gap_analyzer_agent.py       # Agent 4: Dynamic 2-Tier Semantic Gap Analyzer
│   │   ├── ats_analyzer_agent.py       # Agent 5: ATS Audit & XYZ Bullet Rewriter
│   │   ├── resume_generator_agent.py   # Agent 6: Tailored ATS Resume Generator
│   │   ├── roadmap_agent.py            # Agent 7: Dynamic Budget Roadmap Architect
│   │   ├── rag_curator_agent.py        # Agent 8: Multi-Format Resource Curator
│   │   ├── project_generator_agent.py  # Agent 9: GitHub Reference Repo Discovery
│   │   ├── live_job_market_agent.py    # Agent 10: Live Job Placement Agent
│   │   └── interview_simulator_agent.py# Agent 11: Multi-Turn AI Mock Interviewer
│   │
│   └── mcp_tools/                # Standardized MCP Tool Interfaces
│       ├── resource_mcp.py       # Google Books & arXiv API connector
│       ├── github_mcp.py         # GitHub API search & inspection connector
│       ├── job_market_mcp.py     # Live job openings connector
│       └── bigquery_mcp.py       # BigQuery labor dataset connector
│
├── sample_resumes/               # Benchmark PDF resumes
└── test_upgraded_pipeline.py     # Automated test suite
```

---

## ⚙️ Installation & Setup

```bash
# 1. Clone & create virtual environment
git clone https://github.com/your-org/pathcraft-ai.git
cd pathcraft-ai
python -m venv venv
.\venv\Scripts\activate  # Windows (or source venv/bin/activate on Linux/macOS)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Add GOOGLE_API_KEY to your .env file or Streamlit sidebar
```

---

## 🚀 Running the Applications

### 1. Streamlit 6-Hub Web Dashboard
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

### 2. FastAPI REST Server
```bash
python api_server.py
```
Interactive Swagger API documentation available at **`http://localhost:8000/docs`**.

---

## 🧪 Testing & Validation

Run the automated test suite verifying token matching, 2-tier gap analysis, live jobs, multi-turn interview, and full pipeline execution:

```bash
python test_upgraded_pipeline.py
```
