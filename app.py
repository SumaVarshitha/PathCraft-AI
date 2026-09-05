import streamlit as st
import os
import json
import config
from core.orchestrator import CareerCopilotADKTeam

# Page Setup
st.set_page_config(
    page_title="PathCraft AI - Google ADK 2.0 Engine",
    page_icon="🚀",
    layout="wide"
)

# Header Title
st.title("🚀 PathCraft AI - Enterprise Career & Skill Intelligence")
st.markdown("**Powered by Google ADK 2.0, Gemini 3.6 Models, Vector Semantic RAG & Model Context Protocol (MCP)**")

# Sidebar Configuration
st.sidebar.header("🔑 Google ADK 2.0 Configuration")
user_api_key = st.sidebar.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")

if user_api_key:
    os.environ["GOOGLE_API_KEY"] = user_api_key

if not os.getenv("GOOGLE_API_KEY"):
    st.sidebar.warning("⚠️ Enter a `GOOGLE_API_KEY` to enable Live Search Grounding & Gemini Embeddings.")

# Initialize Session State
if "adk_team" not in st.session_state:
    st.session_state["adk_team"] = CareerCopilotADKTeam()
if "adk_result" not in st.session_state:
    st.session_state["adk_result"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "current_question" not in st.session_state:
    st.session_state["current_question"] = None

# Input Form
st.subheader("1. Candidate Profile & Target Role")
col1, col2 = st.columns(2)
with col1:
    selected_role = st.selectbox(
        "Select Target Career Role",
        [
            "Data Engineer", 
            "Backend Engineer", 
            "AI/ML Engineer", 
            "Frontend Engineer",
            "Fullstack Engineer",
            "DevOps / SRE Engineer",
            "Cloud Solutions Architect",
            "Data Scientist",
            "MLOps Engineer",
            "Mobile App Developer",
            "Cybersecurity Engineer",
            "Database Administrator",
            "Custom Role (Type Below)"
        ],
        help="Select a role from the list or choose 'Custom Role' to enter any role."
    )
    if selected_role == "Custom Role (Type Below)":
        target_role = st.text_input(
            "Type Your Custom Target Role",
            placeholder="e.g. LLM Systems Engineer, Robotics Developer, Prompt Engineer"
        )
        if not target_role:
            st.warning("Please type a custom role name above.")
    else:
        target_role = selected_role
    
    st.caption(f"🎯 Target Role: **{target_role if target_role else 'Not Set'}**")
    github_url = st.text_input("GitHub Profile URL / Username (Optional)", placeholder="https://github.com/username")

with col2:
    upload_type = st.radio("Resume Upload Format", ["Paste Text", "Upload PDF File"])
    resume_text = ""
    resume_bytes = None
    
    if upload_type == "Paste Text":
        resume_text = st.text_area("Paste Resume Text (Include Skills, Experience, and Projects)", height=150, placeholder="Paste your complete resume text here...")
    else:
        uploaded_pdf = st.file_uploader("Upload Resume PDF", type=["pdf"])
        if uploaded_pdf:
            resume_bytes = uploaded_pdf.read()

# Run Pipeline Button
if st.button("🚀 Run Google ADK 2.0 Multi-Agent Team", type="primary", use_container_width=True):
    if not resume_text and not resume_bytes:
        st.error("Please paste resume text or upload a PDF resume to proceed.")
    else:
        with st.spinner("Executing Google ADK 2.0 Agent Team (ResumeParser ➔ SemanticGapAnalyzer ➔ MCP LearningCurator ➔ GitHubDiscovery)..."):
            initial_state = {
                "resume_bytes": resume_bytes,
                "resume_text": resume_text,
                "target_role": target_role if target_role else "Data Engineer",
                "github_url": github_url if github_url else None,
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
            res = st.session_state["adk_team"].run_tab1_pipeline(initial_state)
            st.session_state["adk_result"] = res
            st.success("✅ Multi-Agent Pipeline Execution Complete!")

# Render Results
if st.session_state["adk_result"]:
    res = st.session_state["adk_result"]
    st.divider()
    
    tab_diag, tab_learn, tab_interview, tab_jobs = st.tabs([
        "📊 1. Skill Gap Diagnostic",
        "📚 2. Free Learning & Real GitHub Projects",
        "🎯 3. AI Technical Mock Interviewer",
        "💼 4. Live Job Placement Hub"
    ])
    
    # -------------------------------------------------------------------
    # TAB 1: DIAGNOSTIC & SEMANTIC MATCHING
    # -------------------------------------------------------------------
    with tab_diag:
        st.subheader("Google ADK 2.0 Semantic Skill Match Diagnostic")
        st.info(f"⚙️ **Requirements Data Source**: `{res.get('analysis_method', 'Live 2026 Market Search Grounding')}`")
        
        match_score = res.get("match_score", 0.0)
        st.metric("Target Role Match Score", f"{match_score}%", delta=f"{match_score - 100:.1f}% Gap")
        
        col_v, col_m = st.columns(2)
        with col_v:
            st.success("##### ✅ Verified Candidate Skills (from Resume, Projects & GitHub)")
            verified = res.get("verified_skills", [])
            if verified:
                st.write(", ".join([f"`{s}`" for s in verified]))
            else:
                st.write("No matching skills identified for this role.")
                
        with col_m:
            st.error("##### ⚠️ Skill Gaps (To Master for Target Role)")
            gaps = res.get("skills_gap", [])
            if gaps:
                st.write(", ".join([f"`{s}`" for s in gaps]))
            else:
                st.write("🎉 Outstanding! No critical skill gaps detected for this role.")

        # Granular Semantic Match Breakdown Table
        sem_matches = res.get("semantic_matches", [])
        if sem_matches:
            st.markdown("##### 🔬 Meaning-Based Semantic Matching Breakdown")
            table_data = []
            for item in sem_matches:
                table_data.append({
                    "Required Target Skill": item.get("required_skill"),
                    "Matched Candidate Evidence": item.get("matched_candidate_skill") or "None Found",
                    "Evidence Location": item.get("evidence_source", "None"),
                    "Cosine Similarity": f"{item.get('similarity_score', 0.0):.2f}",
                    "Status": "✅ MATCH" if item.get("is_match") else "❌ GAP"
                })
            st.dataframe(table_data, use_container_width=True)

        # Raw Parsed Resume Context Expander
        with st.expander("🔍 View Complete Parsed Resume Data (Projects, Certifications, Tools)"):
            st.json(res.get("resume_data", {}))

    # -------------------------------------------------------------------
    # TAB 2: MULTI-FORMAT LEARNING & REAL GITHUB PROJECTS
    # -------------------------------------------------------------------
    with tab_learn:
        st.subheader("📚 Curated Learning Pack & Real Public GitHub Reference Projects")
        resources = res.get("learning_resources", {})

        # 1. Authoritative Technical Books
        books = resources.get("books", [])
        if books:
            st.markdown("#### 📖 Authoritative Technical Books (Google Books)")
            b_cols = st.columns(min(len(books), 2))
            for i, b in enumerate(books):
                with b_cols[i % len(b_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{b.get('title')}**")
                        st.caption(f"✍️ **Author(s)**: {b.get('author')}")
                        st.write(b.get("description"))
                        st.link_button("📖 View Book on Google Books", b.get("url", "https://books.google.com"))

        # 2. Research Papers & Preprints (arXiv)
        papers = resources.get("papers", [])
        if papers:
            st.markdown("#### 📄 Foundational Research Papers & Preprints (arXiv API)")
            p_cols = st.columns(min(len(papers), 2))
            for i, p in enumerate(papers):
                with p_cols[i % len(p_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{p.get('title')}**")
                        st.caption(f"🔬 **Authors**: {p.get('author')}")
                        st.write(p.get("description"))
                        st.link_button("📄 Read PDF on arXiv", p.get("url", "https://arxiv.org"))

        # 3. Official Documentation
        docs = resources.get("docs", [])
        if docs:
            st.markdown("#### 🌐 Official Documentation & Technical Guides")
            d_cols = st.columns(min(len(docs), 2))
            for i, d in enumerate(docs):
                with d_cols[i % len(d_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{d.get('title')}**")
                        st.write(d.get("description"))
                        st.link_button("🌐 Open Official Documentation", d.get("url", "https://google.com"))

        # 4. Verified Free Courses & Video Tutorials
        courses = resources.get("courses", [])
        if courses:
            st.markdown("#### 🎥 Free Video Tutorials & Interactive Courses")
            c_cols = st.columns(min(len(courses), 2))
            for i, c in enumerate(courses):
                with c_cols[i % len(c_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{c.get('title')}**")
                        st.caption(f"🎓 **Platform**: {c.get('platform')} | ⏳ {c.get('duration', '3 Hours')} | 💵 {c.get('cost', 'Free')}")
                        st.link_button("▶ Access Free Course", c.get("url", "https://youtube.com"))

        # 5. Real Public GitHub Reference Repositories
        st.divider()
        st.subheader("🐙 Real Public GitHub Reference Repositories")
        st.caption("Study production-grade, highly-starred open source implementations to build your portfolio projects.")
        
        gh_projects = res.get("github_projects", [])
        if gh_projects:
            for proj in gh_projects:
                with st.container(border=True):
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"### {proj.get('title')}")
                        st.markdown(f"⭐ **Stars**: `{proj.get('stars', 100):,}` | 🍴 **Forks**: `{proj.get('forks', 20):,}` | 💻 **Language**: `{proj.get('language', 'Python')}`")
                        st.write(proj.get("overview"))
                        if proj.get("topics"):
                            st.write("🏷️ " + " ".join([f"`{t}`" for t in proj.get("topics", [])]))
                    with col_btn:
                        st.link_button("🐙 View GitHub Repo", proj.get("html_url", "https://github.com"), type="primary")

    # -------------------------------------------------------------------
    # TAB 3: MOCK INTERVIEWER
    # -------------------------------------------------------------------
    with tab_interview:
        st.subheader("🎯 Contextual AI Technical Mock Interviewer")
        st.write("Practicing scenario-based questions generated from your identified skill gaps.")
        
        interview_agent = st.session_state["adk_team"].interview_simulator
        missing_skills = res.get("skills_gap", ["System Design", "Cloud Infrastructure"])
        target_role = res.get("target_role", "Data Engineer")
        
        if st.session_state["current_question"] is None:
            if st.button("🎲 Generate First Interview Question", key="btn_start_interview"):
                q = interview_agent.generate_question(
                    target_role=target_role,
                    missing_skills=missing_skills,
                    chat_history=st.session_state["chat_history"]
                )
                st.session_state["current_question"] = q
                st.rerun()

        if st.session_state["current_question"]:
            st.info(f"**Interviewer Question**:\n\n{st.session_state['current_question']}")
            
            with st.form("interview_answer_form"):
                candidate_answer = st.text_area("Your Response", height=130, placeholder="Explain your architectural reasoning, approach, and trade-offs...")
                submitted = st.form_submit_button("Submit Response & Get AI Feedback")
                
                if submitted and candidate_answer:
                    with st.spinner("AI evaluating technical precision, clarity, and trade-offs..."):
                        eval_res = interview_agent.evaluate_answer(
                            question=st.session_state["current_question"],
                            candidate_answer=candidate_answer,
                            target_role=target_role
                        )
                        st.session_state["chat_history"].append({
                            "question": st.session_state["current_question"],
                            "answer": candidate_answer,
                            "evaluation": eval_res
                        })
                        next_q = interview_agent.generate_question(
                            target_role=target_role,
                            missing_skills=missing_skills,
                            chat_history=st.session_state["chat_history"]
                        )
                        st.session_state["current_question"] = next_q
                        st.rerun()

        if st.session_state["chat_history"]:
            st.markdown("#### 📜 Interview Session History & Feedback")
            for i, turn in enumerate(reversed(st.session_state["chat_history"])):
                ev = turn["evaluation"]
                score = ev.get("score", 70)
                icon = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
                with st.expander(f"{icon} Turn {len(st.session_state['chat_history']) - i}: Score {score}/100 - {turn['question'][:65]}..."):
                    st.markdown(f"**Question**: {turn['question']}")
                    st.markdown(f"**Your Answer**: {turn['answer']}")
                    st.markdown(f"**AI Evaluation**: {ev.get('feedback')}")
                    st.info(f"💡 **Key Improvement Takeaway**: {ev.get('key_takeaway')}")

    # -------------------------------------------------------------------
    # TAB 4: LIVE JOB PLACEMENT HUB
    # -------------------------------------------------------------------
    with tab_jobs:
        st.subheader("💼 Live Job Placement Hub & Direct Application Links")
        st.caption("Active job listings matching your target role with direct application links.")
        
        live_jobs = res.get("live_jobs", [])
        if live_jobs:
            for job in live_jobs:
                with st.container(border=True):
                    col_j_info, col_j_btn = st.columns([4, 1])
                    with col_j_info:
                        st.markdown(f"### {job.get('title')}")
                        st.markdown(f"🏢 **{job.get('company')}** | 📍 `{job.get('location')}` | 🗓️ *{job.get('created')}*")
                        st.write(job.get("description"))
                        if job.get("salary_min") and job.get("salary_max"):
                            st.caption(f"💰 **Estimated Salary**: ${job.get('salary_min'):,} - ${job.get('salary_max'):,} USD")
                    with col_j_btn:
                        st.link_button("🚀 Apply Now", job.get("apply_url", "https://google.com"), type="primary")
