import streamlit as st
import os
import json
import config
from core.orchestrator import CareerCopilotADKTeam
from core.agents.resume_generator_agent import generate_ats_pdf
from test_resumes import STRONG_DATA_ENGINEER_RESUME, WEAK_DESIGNER_RESUME

# Page Setup
st.set_page_config(
    page_title="PathCraft AI - Enterprise Career & Skill Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "adk_team" not in st.session_state:
    st.session_state["adk_team"] = CareerCopilotADKTeam()
if "adk_result" not in st.session_state:
    st.session_state["adk_result"] = None
if "interview_turns" not in st.session_state:
    st.session_state["interview_turns"] = []
if "interview_active" not in st.session_state:
    st.session_state["interview_active"] = False
if "current_question_data" not in st.session_state:
    st.session_state["current_question_data"] = None
if "interview_finished" not in st.session_state:
    st.session_state["interview_finished"] = False

# App Header
st.title("🚀 PathCraft AI - Enterprise Career & Skill Intelligence")
st.markdown("**Autonomous Multi-Agent Career Platform powered by Google ADK 2.0, Gemini 2.5, Dynamic Search Grounding & MCP Tools**")

# Sidebar Configuration
st.sidebar.header("🔑 Google ADK 2.0 Engine Settings")
user_api_key = st.sidebar.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")

if user_api_key:
    os.environ["GOOGLE_API_KEY"] = user_api_key

if not os.getenv("GOOGLE_API_KEY"):
    st.sidebar.warning("⚠️ Enter a `GOOGLE_API_KEY` to enable Live Search Grounding & Gemini Embeddings.")

# Benchmark Profiles Selector in Sidebar
st.sidebar.divider()
st.sidebar.subheader("📄 1-Click Benchmark Resumes")
sample_choice = st.sidebar.selectbox(
    "Load Benchmark Profile:",
    [
        "-- Custom Candidate Profile --", 
        "1. Senior Data Engineer (Strong Match)", 
        "2. AI / ML Engineer (Strong Match)", 
        "3. Fullstack Web Developer", 
        "4. UI/UX Designer (Weak Data Match)"
    ]
)

# Main Input Form
st.subheader("1. Candidate Profile & Target Trajectory")
col_role, col_input = st.columns([1, 1])

with col_role:
    default_role_idx = 0
    if "AI / ML" in sample_choice:
        default_role_idx = 1
    elif "Fullstack" in sample_choice:
        default_role_idx = 5
    elif "Data Engineer" in sample_choice:
        default_role_idx = 2

    selected_role = st.selectbox(
        "Target Career Job Role",
        [
            "GenAI / LLM Systems Engineer",
            "AI Agent & Multi-Agent Systems Architect",
            "Data Engineer", 
            "Data & AI Platform Engineer",
            "AI/ML Engineer", 
            "Backend & Cloud Systems Engineer",
            "Fullstack Engineer",
            "DevOps / SRE Engineer",
            "Cloud Solutions Architect",
            "Data Scientist",
            "MLOps Engineer",
            "Custom Role (Type Below)"
        ],
        index=default_role_idx
    )
    if selected_role == "Custom Role (Type Below)":
        target_role = st.text_input("Type Your Custom Target Role", placeholder="e.g. Autonomous AI Agent Developer, Robotics Systems Engineer")
    else:
        target_role = selected_role

    col_sen, col_hrs = st.columns(2)
    with col_sen:
        seniority_level = st.selectbox("Target Seniority Level", ["Junior / Entry-Level", "Mid-Level", "Senior Engineer", "Staff / Principal Lead"], index=2)
    with col_hrs:
        weekly_hours = st.select_slider("Weekly Study Budget", options=[5, 10, 15, 20, 25, 30], value=10, format_func=lambda x: f"{x} hrs/wk")

    github_url = st.text_input("GitHub Profile URL / Username (Optional)", placeholder="https://github.com/username")
    linkedin_text = st.text_area("LinkedIn Profile / Achievements / Honors (Optional)", height=80, placeholder="Paste LinkedIn summary, awards, certifications, or key project accomplishments...")

with col_input:
    upload_type = st.radio("Resume Upload Format", ["Upload PDF File", "Paste Text"], horizontal=True)
    resume_text = ""
    resume_bytes = None
    
    if sample_choice == "1. Senior Data Engineer (Strong Match)":
        resume_text = STRONG_DATA_ENGINEER_RESUME
    elif sample_choice == "2. AI / ML Engineer (Strong Match)":
        if os.path.exists("sample_resumes/2_AIML_Engineer.pdf"):
            with open("sample_resumes/2_AIML_Engineer.pdf", "rb") as f:
                resume_bytes = f.read()
    elif sample_choice == "3. Fullstack Web Developer":
        if os.path.exists("sample_resumes/3_Fullstack_Developer.pdf"):
            with open("sample_resumes/3_Fullstack_Developer.pdf", "rb") as f:
                resume_bytes = f.read()
    elif sample_choice == "4. UI/UX Designer (Weak Data Match)":
        resume_text = WEAK_DESIGNER_RESUME

    if upload_type == "Paste Text":
        resume_text = st.text_area("Paste Resume Text (Complete Experience, Projects & Skills)", value=resume_text, height=160, placeholder="Paste full resume text...")
    else:
        uploaded_pdf = st.file_uploader("Upload Resume PDF (Complete Multi-Page Resume)", type=["pdf"])
        if uploaded_pdf:
            resume_bytes = uploaded_pdf.read()
        elif resume_bytes:
            st.info(f"📄 Sample PDF Loaded: `{sample_choice}`")

# Action Execution Buttons
st.write("")
col_btn1, col_btn2 = st.columns([1, 1])

with col_btn1:
    run_pipeline = st.button("🚀 Run Complete Career Copilot Pipeline", type="primary", use_container_width=True)

with col_btn2:
    step_parse_btn = st.button("🔍 Step 1: Parse Profile & Verify Skills (HITL)", use_container_width=True)

# Step 1 Profile Ingestion
if step_parse_btn or run_pipeline:
    if not resume_text and not resume_bytes:
        st.error("Please upload a PDF resume or paste resume text to proceed.")
    else:
        with st.spinner("Extracting candidate context and evaluating against live 2026 market standards..."):
            initial_state = {
                "resume_bytes": resume_bytes,
                "resume_text": resume_text,
                "target_role": target_role if target_role else "GenAI / LLM Systems Engineer",
                "seniority_level": seniority_level,
                "github_url": github_url if github_url else None,
                "linkedin_url": None,
                "linkedin_text": linkedin_text if linkedin_text else None,
                "user_confirmed_skills": [],
                "user_prioritized_gaps": [],
                "study_pace_hours_per_week": weekly_hours,
                "resume_data": None,
                "github_data": None,
                "linkedin_data": None,
                "unified_skills": [],
                "skills_gap": [],
                "core_skills": [],
                "differentiator_skills": [],
                "candidate_superpowers": [],
                "suggested_alternate_roles": [],
                "match_score": 0.0,
                "core_match_score": 0.0,
                "analysis_method": "",
                "semantic_matches": [],
                "ats_audit": None,
                "career_roadmap": None,
                "tailored_resume": None,
                "curated_courses": [],
                "learning_resources": {},
                "project_blueprints": [],
                "github_projects": [],
                "live_jobs": [],
                "interview_history": [],
                "interview_turns": []
            }
            if run_pipeline:
                st.session_state["adk_result"] = st.session_state["adk_team"].run_full_pipeline(initial_state)
                st.success("✅ Multi-Agent Pipeline Completed!")
            else:
                st.session_state["adk_result"] = st.session_state["adk_team"].parse_profile(initial_state)
                st.success("✅ Profile Ingestion Complete! Review and confirm your skills below.")

st.divider()

# -------------------------------------------------------------------
# FOCUSED 4-HUB INTERACTIVE WORKSPACE
# -------------------------------------------------------------------
tab_diag, tab_resume, tab_roadmap, tab_interview = st.tabs([
    "📊 1. Skill Gap Diagnostic & Superpowers",
    "✍️ 2. In-Place Resume Optimizer",
    "📅 3. Dynamic Roadmap & Learning Pack",
    "🎙️ 4. AI Mock Interview Hub"
])

res = st.session_state["adk_result"]

# -------------------------------------------------------------------
# HUB 1: DIAGNOSTIC, SUPERPOWERS & HITL SKILL VERIFICATION
# -------------------------------------------------------------------
with tab_diag:
    st.subheader("📊 Dynamic Semantic Skill Gap Diagnostic & Candidate Superpowers")
    if res:
        # Superpowers Banner
        superpowers = res.get("candidate_superpowers", [])
        if superpowers:
            with st.container(border=True):
                st.markdown("### 🌟 Candidate Superpowers & Standout Capabilities")
                st.caption("Advanced competencies detected in your projects and work experience that exceed standard baseline requirements:")
                st.write(" ".join([f"✨ **`{sp}`**" for sp in superpowers]))
                
                alt_roles = res.get("suggested_alternate_roles", [])
                if alt_roles:
                    st.divider()
                    st.markdown("##### 💡 High-Synergy Alternate Roles For Your Background:")
                    for ar in alt_roles:
                        st.info(f"🎯 **{ar.get('role')}** (Est. Match: `{ar.get('estimated_match')}`): {ar.get('rationale')}")

        # HITL Candidate Skill Editor
        with st.expander("👤 Human-in-the-Loop: Candidate Verified Skills Editor", expanded=not res.get("match_score")):
            st.markdown("Review the skills extracted from your resume, projects, and GitHub. You can add or remove skills to refine the analysis.")
            current_skills = res.get("user_confirmed_skills") or res.get("unified_skills", [])
            
            col_add, col_sel = st.columns([1, 2])
            with col_add:
                new_skill = st.text_input("Add Unlisted Skill", placeholder="e.g. LangGraph, RAG, FastAPI, dbt")
                if st.button("➕ Add Skill"):
                    if new_skill and new_skill.strip() not in current_skills:
                        current_skills.append(new_skill.strip())
                        res["user_confirmed_skills"] = current_skills
                        st.rerun()

            with col_sel:
                confirmed = st.multiselect("Verified Skills List", options=current_skills, default=current_skills)
                if confirmed != current_skills:
                    res["user_confirmed_skills"] = confirmed

            if st.button("🔄 Recalculate 2-Tier Skill Gap Diagnostic", type="primary"):
                with st.spinner("Re-analyzing with updated skills against live 2026 market standards..."):
                    res = st.session_state["adk_team"].run_full_pipeline(res)
                    st.session_state["adk_result"] = res
                    st.rerun()

        if res.get("match_score") is not None and res.get("match_score") > 0:
            st.info(f"⚙️ **Market Data Source**: `{res.get('analysis_method', 'Live 2026 Market Search Grounding')}`")
            
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("Overall Weighted Match", f"{res.get('match_score', 0.0)}%", help="Weighted: 70% Core Must-Haves + 30% Differentiators")
            with m_col2:
                st.metric("Core Must-Haves Match", f"{res.get('core_match_score', 0.0)}%", help="Foundational non-negotiable requirements")
            with m_col3:
                total_reqs = len(res.get("semantic_matches", []))
                verified_cnt = len(res.get("verified_skills", []))
                st.metric("Requirements Satisfied", f"{verified_cnt}/{total_reqs}")

            st.divider()
            col_v, col_m = st.columns(2)
            with col_v:
                st.success("##### ✅ Verified Candidate Skills")
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
                        "Required Skill": item.get("required_skill"),
                        "Tier": item.get("skill_category", "Core Must-Have"),
                        "Matched Candidate Evidence": item.get("matched_candidate_skill") or "None Found",
                        "Evidence Source": item.get("evidence_source", "None"),
                        "Cosine Similarity": f"{item.get('similarity_score', 0.0):.2f}",
                        "Status": "✅ MATCH" if item.get("is_match") else "❌ GAP"
                    })
                st.dataframe(table_data, use_container_width=True)

            with st.expander("🔍 View Complete Extracted Context (Work History Bullets, Projects, Certifications)"):
                st.json(res.get("resume_data", {}))
    else:
        st.info("👆 Upload or select a sample resume above and click **'🚀 Run Complete Career Copilot Pipeline'** or **'🔍 Step 1'** to begin!")

# -------------------------------------------------------------------
# HUB 2: AUTHENTIC IN-PLACE RESUME OPTIMIZER (SIDE-BY-SIDE DIFF)
# -------------------------------------------------------------------
with tab_resume:
    st.subheader("✍️ Authentic In-Place Resume Optimizer (Side-by-Side Comparison)")
    st.caption("Takes your real uploaded resume, preserves 100% of your authentic companies, dates, and projects, and surgically upgrades your bullet points using Google's XYZ formula and target keywords.")

    if res and res.get("tailored_resume"):
        tailored = res.get("tailored_resume", {})
        
        # ATS Metric Cards
        ats = res.get("ats_audit", {})
        ats_score_before = tailored.get("ats_score_before", ats.get("ats_score", 68))
        ats_score_after = tailored.get("ats_score_after", 92)

        c_sc1, c_sc2, c_sc3 = st.columns(3)
        with c_sc1:
            st.metric("Original ATS Score", f"{ats_score_before}/100", help="Score before keyword and metric optimization")
        with c_sc2:
            st.metric("Optimized ATS Score", f"{ats_score_after}/100", delta=f"+{ats_score_after - ats_score_before} pts")
        with c_sc3:
            st.metric("Target Role Alignment", f"{target_role}")

        # Surgical Changes List
        key_changes = tailored.get("key_changes", [])
        if key_changes:
            st.divider()
            st.markdown("##### ✨ Surgical In-Place Enhancements (Google XYZ Formula)")
            for chg in key_changes:
                with st.container(border=True):
                    st.markdown(f"❌ **Original**: *\"{chg.get('original_snippet')}\"*")
                    st.markdown(f"✅ **Upgraded**: **\"{chg.get('improved_snippet')}\"**")
                    st.info(f"💡 **Why this ranks higher**: {chg.get('rationale')}")

        # Side-by-Side Comparison
        st.divider()
        st.markdown("##### 🔍 Side-by-Side Resume Comparison")
        col_orig, col_opt = st.columns(2)

        with col_orig:
            st.markdown("#### 📄 Original Uploaded Resume")
            st.text_area("Original Text (Read-Only)", value=res.get("resume_text", ""), height=350, disabled=True)

        with col_opt:
            st.markdown("#### ✨ ATS-Optimized Resume (Editable)")
            current_opt_text = tailored.get("optimized_text", "")
            edited_opt_text = st.text_area("Optimized Text (Edit in real-time below)", value=current_opt_text, height=350)
            if edited_opt_text != current_opt_text:
                tailored["optimized_text"] = edited_opt_text

        # Download Buttons
        col_dl_pdf, col_dl_md = st.columns(2)
        with col_dl_pdf:
            pdf_bytes_out = generate_ats_pdf(tailored)
            st.download_button(
                label="📄 Download Upgraded Resume (PDF)",
                data=pdf_bytes_out,
                file_name=f"{tailored.get('candidate_name', 'Candidate')}_{target_role.replace(' ', '_')}_Optimized.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )
        with col_dl_md:
            st.download_button(
                label="📝 Download Upgraded Resume (Markdown)",
                data=tailored.get("optimized_text", ""),
                file_name=f"{tailored.get('candidate_name', 'Candidate')}_{target_role.replace(' ', '_')}_Optimized.md",
                mime="text/markdown",
                use_container_width=True
            )
    else:
        st.info("👆 Run the multi-agent analysis to optimize your authentic resume in-place!")

# -------------------------------------------------------------------
# HUB 3: 30-60-90 DAY DYNAMIC ROADMAP & LEARNING PACK
# -------------------------------------------------------------------
with tab_roadmap:
    st.subheader("📅 Personalized 30-60-90 Day Upskilling Roadmap & Curated Resources")
    if res and res.get("career_roadmap"):
        rm = res.get("career_roadmap", {})
        budget = rm.get("weekly_hours_budget", weekly_hours)
        st.caption(f"🎯 **Trajectory ({budget} Hours/Week Commitment)**: {rm.get('executive_summary', 'Structured career roadmap.')}")
        
        # Phase 1
        p1 = rm.get("phase_1_foundations", {})
        with st.expander(f"🟢 {p1.get('phase_title', 'Phase 1: Core Fundamentals')} ({p1.get('duration_days', 'Days 1-30')})", expanded=True):
            st.markdown("**Key Phase Objectives:**")
            for obj in p1.get("key_objectives", []):
                st.write(f"• {obj}")
            st.divider()
            for w in p1.get("weeks", []):
                st.markdown(f"**Week {w.get('week_number')}: {w.get('focus_topic')}** ({w.get('estimated_hours', budget)} hrs)")
                for act in w.get("action_items", []):
                    st.checkbox(f"{act}", key=f"p1_w{w.get('week_number')}_{act[:20]}")
                st.caption(f"📦 *Deliverable: {w.get('learning_deliverable')}*")
                st.write("")

        # Phase 2
        p2 = rm.get("phase_2_architecture", {})
        with st.expander(f"🟡 {p2.get('phase_title', 'Phase 2: Systems & Architecture')} ({p2.get('duration_days', 'Days 31-60')})", expanded=False):
            st.markdown("**Key Phase Objectives:**")
            for obj in p2.get("key_objectives", []):
                st.write(f"• {obj}")
            st.divider()
            for w in p2.get("weeks", []):
                st.markdown(f"**Week {w.get('week_number')}: {w.get('focus_topic')}** ({w.get('estimated_hours', budget)} hrs)")
                for act in w.get("action_items", []):
                    st.checkbox(f"{act}", key=f"p2_w{w.get('week_number')}_{act[:20]}")
                st.caption(f"📦 *Deliverable: {w.get('learning_deliverable')}*")
                st.write("")

        # Phase 3
        p3 = rm.get("phase_3_portfolio_launch", {})
        with st.expander(f"🔵 {p3.get('phase_title', 'Phase 3: Independent Portfolio & Launch')} ({p3.get('duration_days', 'Days 61-90')})", expanded=False):
            st.markdown("**Key Phase Objectives:**")
            for obj in p3.get("key_objectives", []):
                st.write(f"• {obj}")
            st.divider()
            for w in p3.get("weeks", []):
                st.markdown(f"**Week {w.get('week_number')}: {w.get('focus_topic')}** ({w.get('estimated_hours', budget)} hrs)")
                for act in w.get("action_items", []):
                    st.checkbox(f"{act}", key=f"p3_w{w.get('week_number')}_{act[:20]}")
                st.caption(f"📦 *Deliverable: {w.get('learning_deliverable')}*")
                st.write("")

        # Curated Learning Pack & GitHub Repos
        st.divider()
        st.subheader("📚 Curated Learning Pack & GitHub Reference Repositories")
        resources = res.get("learning_resources", {})

        # Technical Books
        books = resources.get("books", [])
        if books:
            st.markdown("#### 📖 Authoritative Technical Books (Google Books API)")
            b_cols = st.columns(min(len(books), 2))
            for i, b in enumerate(books):
                with b_cols[i % len(b_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{b.get('title')}**")
                        st.caption(f"✍️ **Author(s)**: {b.get('author')}")
                        st.write(b.get("description"))
                        st.link_button("📖 View on Google Books", b.get("url", "https://books.google.com"))

        # Research Papers
        papers = resources.get("papers", [])
        if papers:
            st.markdown("#### 📄 Foundational Research Papers (arXiv API)")
            p_cols = st.columns(min(len(papers), 2))
            for i, p in enumerate(papers):
                with p_cols[i % len(p_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{p.get('title')}**")
                        st.caption(f"🔬 **Authors**: {p.get('author')}")
                        st.write(p.get("description"))
                        st.link_button("📄 Read on arXiv", p.get("url", "https://arxiv.org"))

        # GitHub Reference Projects
        gh_projects = res.get("github_projects", [])
        if gh_projects:
            st.markdown("#### 🐙 Real Public GitHub Reference Repositories")
            for proj in gh_projects:
                with st.container(border=True):
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"### {proj.get('title')}")
                        st.markdown(f"⭐ **Stars**: `{proj.get('stars', 100):,}` | 🍴 **Forks**: `{proj.get('forks', 20):,}` | 💻 **Language**: `{proj.get('language', 'Python')}`")
                        st.write(proj.get("overview"))
                    with col_btn:
                        st.link_button("🐙 View GitHub Repo", proj.get("html_url", "https://github.com"), type="primary")
    else:
        st.info("👆 Run the multi-agent analysis to generate your customized action roadmap and learning packs!")

# -------------------------------------------------------------------
# HUB 4: INTERACTIVE MULTI-TURN AI MOCK INTERVIEWER
# -------------------------------------------------------------------
with tab_interview:
    st.subheader("🎙️ Interactive Multi-Turn AI Technical Interview Simulator")
    st.caption("Practice realistic scenario-based technical questions. The AI tests your missing skill gaps and core competencies, evaluates answers in real-time, and provides a final scorecard.")

    missing_skills = res.get("skills_gap", []) if res else []
    verified_skills = res.get("verified_skills", []) if res else []
    active_role = target_role if target_role else "GenAI / LLM Systems Engineer"

    # Interview Configuration
    col_ic1, col_ic2, col_ic3 = st.columns(3)
    with col_ic1:
        interview_len = st.selectbox("Interview Length", [3, 5, 10], index=0, format_func=lambda x: f"{x} Questions")
    with col_ic2:
        interview_diff = st.selectbox("Interview Difficulty", ["Junior / Entry", "Mid-Level", "Senior Engineer", "Staff / Principal"], index=2)
    with col_ic3:
        st.write("")
        if not st.session_state["interview_active"]:
            if st.button("🚀 Start Mock Technical Interview", type="primary", use_container_width=True):
                st.session_state["interview_active"] = True
                st.session_state["interview_turns"] = []
                st.session_state["interview_finished"] = False
                with st.spinner("Generating Question 1..."):
                    q_data = st.session_state["adk_team"].interview_simulator.generate_next_question(
                        target_role=active_role,
                        missing_skills=missing_skills,
                        verified_skills=verified_skills,
                        turn_index=0,
                        total_questions=interview_len,
                        difficulty=interview_diff
                    )
                    st.session_state["current_question_data"] = q_data
                st.rerun()
        else:
            if st.button("🔄 Reset / Restart Interview", use_container_width=True):
                st.session_state["interview_active"] = False
                st.session_state["interview_turns"] = []
                st.session_state["current_question_data"] = None
                st.session_state["interview_finished"] = False
                st.rerun()

    st.divider()

    # Active Interview Session
    if st.session_state["interview_active"]:
        turns = st.session_state["interview_turns"]
        turn_idx = len(turns)
        
        # Display completed turns
        for i, t in enumerate(turns):
            with st.container(border=True):
                st.markdown(f"#### ❓ Question {i + 1} ({t.get('skill_focus', 'Skill')})")
                st.markdown(f"**{t.get('question')}**")
                st.markdown(f"💬 **Your Answer**: *{t.get('candidate_answer')}*")
                
                eval_res = t.get("evaluation", {})
                score = eval_res.get("score", 75)
                score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                st.markdown(f"{score_color} **Score**: `{score}/100`")
                st.info(f"💡 **Evaluation Feedback**: {eval_res.get('feedback')}")
                st.caption(f"🎯 **Key Takeaway**: {eval_res.get('key_takeaway')}")
                if eval_res.get("model_answer_snippet"):
                    with st.expander("🏆 View Production Model Solution"):
                        st.markdown(eval_res.get("model_answer_snippet"))

        # Check if interview complete
        if turn_idx >= interview_len:
            st.session_state["interview_finished"] = True
            st.balloons()
            st.success("🎉 Mock Interview Complete! Here is your Performance Scorecard:")
            
            report = st.session_state["adk_team"].interview_simulator.generate_final_report_card(
                target_role=active_role,
                turns=turns
            )
            
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.metric("Overall Score", f"{report.get('overall_score', 0)}/100")
            with sc2:
                st.metric("Hiring Readiness", report.get("readiness", "Evaluated"))
            with sc3:
                st.metric("Questions Answered", f"{len(turns)}/{interview_len}")

            st.markdown(f"**Executive Summary**: {report.get('summary')}")
        else:
            # Current active question
            q_data = st.session_state["current_question_data"]
            if q_data:
                st.markdown(f"### ❓ Question {turn_idx + 1} of {interview_len}")
                st.caption(f"🎯 Focus: **{q_data.get('skill_focus')}** | *{q_data.get('question_type')}*")
                with st.container(border=True):
                    st.markdown(f"### \"{q_data.get('question')}\"")

                cand_ans = st.text_area("Your Technical Answer (Include architecture trade-offs, code, or metrics)", height=150, placeholder="Explain your design, specific tools, code snippets, or failure handling...")
                
                if st.button("📤 Submit Answer for AI Evaluation", type="primary"):
                    if not cand_ans or len(cand_ans.strip()) < 5:
                        st.warning("Please provide a detailed technical answer to receive accurate evaluation.")
                    else:
                        with st.spinner("AI Evaluating answer against production rubric..."):
                            eval_res = st.session_state["adk_team"].interview_simulator.evaluate_answer(
                                question=q_data.get("question"),
                                candidate_answer=cand_ans,
                                target_role=active_role,
                                skill_focus=q_data.get("skill_focus"),
                                difficulty=interview_diff
                            )
                            # Append turn
                            turns.append({
                                "turn_index": turn_idx,
                                "skill_focus": q_data.get("skill_focus"),
                                "question": q_data.get("question"),
                                "candidate_answer": cand_ans,
                                "evaluation": eval_res
                            })
                            st.session_state["interview_turns"] = turns

                            # Pre-fetch next question if not finished
                            if len(turns) < interview_len:
                                next_q = st.session_state["adk_team"].interview_simulator.generate_next_question(
                                    target_role=active_role,
                                    missing_skills=missing_skills,
                                    verified_skills=verified_skills,
                                    turn_index=len(turns),
                                    total_questions=interview_len,
                                    difficulty=interview_diff
                                )
                                st.session_state["current_question_data"] = next_q
                            st.rerun()
    else:
        st.info("👆 Click **'🚀 Start Mock Technical Interview'** above to test your technical skills in a live scenario-based simulation!")
