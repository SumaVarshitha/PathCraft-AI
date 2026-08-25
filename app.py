import streamlit as st
import os
import json
import config
from core.orchestrator import CareerCopilotADKTeam

# Page Setup
st.set_page_config(
    page_title="AI Career Copilot - Google ADK 2.0 Engine",
    page_icon="🤖",
    layout="wide"
)

# Header Title
st.title("🤖 AI Career Copilot & Adaptive Learning Engine")
st.markdown("**Powered by Google ADK 2.0 (Agent Development Kit) & Gemini 2.5**")

# Sidebar Configuration
st.sidebar.header("🔑 Google ADK 2.0 Configuration")
user_api_key = st.sidebar.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")

if user_api_key:
    os.environ["GOOGLE_API_KEY"] = user_api_key

if not os.getenv("GOOGLE_API_KEY"):
    st.warning("⚠️ Please enter a `GOOGLE_API_KEY` in the sidebar or in your `.env` file to initialize Google ADK 2.0 Agents.")

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
st.subheader("1. Candidate Input Profile")
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
        ]
    )
    if selected_role == "Custom Role (Type Below)":
        target_role = st.text_input("Type Custom Target Role Name", placeholder="e.g. LLM Systems Engineer, Robotics Developer")
    else:
        target_role = selected_role
    github_url = st.text_input("GitHub Profile URL / Username (Optional)", placeholder="https://github.com/username")

with col2:
    upload_type = st.radio("Resume Upload Format", ["Paste Text", "Upload PDF File"])
    resume_text = ""
    resume_bytes = None
    
    if upload_type == "Paste Text":
        resume_text = st.text_area("Paste Resume Text", height=140, placeholder="Paste your work summary, skills, and experience here...")
    else:
        uploaded_pdf = st.file_uploader("Upload Resume PDF", type=["pdf"])
        if uploaded_pdf:
            resume_bytes = uploaded_pdf.read()

# Run ADK 2.0 Pipeline Button
if st.button("🚀 Run Google ADK 2.0 Multi-Agent Team", type="primary", use_container_width=True):
    if not resume_text and not resume_bytes:
        st.error("Please paste resume text or upload a PDF resume to proceed.")
    else:
        with st.spinner("Executing Google ADK 2.0 Agents (ResumeParser ➔ Normalizer ➔ GapAnalyzer ➔ RAGCurator ➔ ProjectGenerator)..."):
            initial_state = {
                "resume_bytes": resume_bytes,
                "resume_text": resume_text,
                "target_role": target_role,
                "github_url": github_url if github_url else None,
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
            
            # Execute ADK 2.0 Team Orchestrator
            adk_team = st.session_state["adk_team"]
            final_state = adk_team.run_tab1_pipeline(initial_state)
            st.session_state["adk_result"] = final_state
            st.session_state["chat_history"] = []
            st.session_state["current_question"] = None
            st.success("✅ Google ADK 2.0 Multi-Agent Execution Complete!")

# Render Results
if st.session_state["adk_result"]:
    res = st.session_state["adk_result"]
    st.divider()
    
    tab_diag, tab_learn, tab_interview, tab_jobs = st.tabs([
        "📊 1. Skill Gap Diagnostic", 
        "📚 2. Free Learning & Projects Hub", 
        "🎯 3. AI Technical Mock Interviewer",
        "💼 4. Live Job Placement Hub"
    ])
    
    # -------------------------------------------------------------------
    # TAB 1: DIAGNOSTIC
    # -------------------------------------------------------------------
    with tab_diag:
        st.subheader("Google ADK 2.0 Skill Match Diagnostic")
        st.info(f"⚙️ **Analysis Data Source Used**: `{res.get('analysis_method', 'TIER 2 (Industry Taxonomy Matrix)')}`")
        match_score = res.get("match_score", 0.0)
        st.metric("Target Role Match Score", f"{match_score}%", delta=f"{match_score - 100:.1f}% Gap")
        
        col_v, col_m = st.columns(2)
        with col_v:
            st.success("##### ✅ Verified Candidate Skills")
            verified = res.get("unified_skills", [])
            if verified:
                st.write(", ".join([f"`{s}`" for s in verified]))
            else:
                st.info("No verified skills extracted.")
                
        with col_m:
            st.error("##### ⚠️ Skill Gaps (To Learn)")
            gaps = res.get("skills_gap", [])
            if gaps:
                st.write(", ".join([f"`{s}`" for s in gaps]))
            else:
                st.success("Great job! No major skill gaps detected.")
                
        with st.expander("🔍 View Raw Parsed Resume Output (ADK 2.0 Schema)"):
            st.json(res.get("resume_data", {}))

    # -------------------------------------------------------------------
    # TAB 2: LEARNING & PROJECTS
    # -------------------------------------------------------------------
    with tab_learn:
        st.subheader("📖 Curated Free Learning Resources (Google Search Tool Grounded)")
        courses = res.get("curated_courses", [])
        if courses:
            for c in courses:
                with st.container(border=True):
                    c_col1, c_col2 = st.columns([3, 1])
                    with c_col1:
                        st.markdown(f"### `{c.get('skill')}`: {c.get('title')}")
                        st.write(f"**Platform**: {c.get('platform')} | **Duration**: {c.get('duration')} | **Cost**: {c.get('cost')}")
                    with c_col2:
                        st.link_button("▶ Access Resource", c.get('url', '#'), use_container_width=True)
        else:
            st.info("No course recommendations required.")
            
        st.divider()
        st.subheader("🛠️ GitHub Portfolio Mini-Project Blueprints (Gemini 2.5 Pro)")
        projects = res.get("project_blueprints", [])
        if projects:
            for p in projects:
                with st.container(border=True):
                    st.markdown(f"### 📦 `{p.get('project_title')}`")
                    st.write(f"**Target Skills**: {', '.join(p.get('target_skills', []))}")
                    st.write(f"**Overview**: {p.get('overview')}")
                    
                    with st.expander("📂 View Recommended Folder Structure"):
                        st.code("\n".join(p.get("folder_structure", [])), language="bash")
                        
                    with st.expander("📝 View README.md Specification Template"):
                        st.markdown(p.get("readme_spec", ""))
        else:
            st.info("No project blueprints generated.")

    # -------------------------------------------------------------------
    # TAB 3: MOCK INTERVIEW SIMULATOR
    # -------------------------------------------------------------------
    with tab_interview:
        st.subheader("🎯 ADK 2.0 Technical Mock Interview Simulator")
        st.caption("Practice answering technical interview questions generated by your ADK Agent.")
        
        gaps = res.get("skills_gap", [])
        interview_agent = st.session_state["adk_team"].interview_simulator
        
        if not st.session_state["current_question"]:
            with st.spinner("ADK Agent generating question..."):
                st.session_state["current_question"] = interview_agent.generate_question(
                    target_role=res.get("target_role", "Data Engineer"),
                    missing_skills=gaps,
                    chat_history=st.session_state["chat_history"]
                )
                
        q = st.session_state["current_question"]
        st.info(f"**Interviewer Question**: {q}")
        
        with st.form("interview_form_adk", clear_on_submit=True):
            user_answer = st.text_area("Your Technical Answer:", height=120, placeholder="Explain your approach, technical keywords, and solution logic...")
            submitted = st.form_submit_button("Submit Answer for ADK Scoring", type="primary")
            
            if submitted and user_answer:
                with st.spinner("ADK Agent evaluating response..."):
                    eval_result = interview_agent.evaluate_answer(
                        question=q,
                        candidate_answer=user_answer,
                        target_role=res.get("target_role", "Data Engineer")
                    )
                    
                    st.session_state["chat_history"].append({
                        "question": q,
                        "answer": user_answer,
                        "score": eval_result.get("score", 70),
                        "feedback": eval_result.get("feedback", ""),
                        "takeaway": eval_result.get("key_takeaway", "")
                    })
                    
                    st.session_state["current_question"] = interview_agent.generate_question(
                        target_role=res.get("target_role", "Data Engineer"),
                        missing_skills=gaps,
                        chat_history=st.session_state["chat_history"]
                    )
                    st.rerun()

        if st.session_state["chat_history"]:
            st.subheader("📜 Interview Evaluation History")
            for idx, turn in enumerate(reversed(st.session_state["chat_history"])):
                score = turn.get("score", 70)
                score_color = "🟢" if score >= 80 else ("🟡" if score >= 60 else "🔴")
                
                with st.expander(f"Q{len(st.session_state['chat_history']) - idx}: {turn.get('question')} — Score: {score_color} {score}/100", expanded=(idx==0)):
                    st.markdown(f"**Your Answer**: {turn.get('answer')}")
                    st.markdown(f"**Feedback**: {turn.get('feedback')}")
                    st.info(f"💡 **Key Improvement Tip**: {turn.get('takeaway')}")

    # -------------------------------------------------------------------
    # TAB 4: LIVE JOB PLACEMENT HUB
    # -------------------------------------------------------------------
    with tab_jobs:
        st.subheader("💼 Active Live Job Openings & Direct Application Links")
        st.caption(f"Real active market job postings matching target role: **{res.get('target_role', 'Data Engineer')}**")
        
        jobs = res.get("live_jobs", [])
        if jobs:
            for j in jobs:
                with st.container(border=True):
                    j_col1, j_col2 = st.columns([3, 1])
                    with j_col1:
                        st.markdown(f"### 🏢 {j.get('title')}")
                        st.markdown(f"**Company**: {j.get('company')}")
                        st.write(f"{j.get('description')[:250]}...")
                    with j_col2:
                        st.link_button("🚀 Apply Now", j.get('redirect_url', 'https://google.com/about/careers'), type="primary", use_container_width=True)
        else:
            st.info("No active live job listings found for this query.")
