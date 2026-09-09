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
    ["-- Custom Candidate Profile --", "1. Senior Data Engineer (Strong Match)", "2. AI / ML Engineer (Strong Match)", "3. Fullstack Web Developer", "4. UI/UX Designer (Weak Data Match)"]
)

# Main Input Form
st.subheader("1. Candidate Profile & Target Trajectory")
col_role, col_input = st.columns([1, 1])

with col_role:
    default_role_idx = 0
    if "AI / ML" in sample_choice:
        default_role_idx = 2
    elif "Fullstack" in sample_choice:
        default_role_idx = 4
    elif "Data Engineer" in sample_choice:
        default_role_idx = 0

    selected_role = st.selectbox(
        "Target Career Job Role",
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
        index=default_role_idx
    )
    if selected_role == "Custom Role (Type Below)":
        target_role = st.text_input("Type Your Custom Target Role", placeholder="e.g. LLM Systems Engineer, Robotics Developer")
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
    run_pipeline = st.button("🚀 Run Complete Multi-Agent Career Copilot", type="primary", use_container_width=True)

with col_btn2:
    step_parse_btn = st.button("🔍 Step 1: Parse Profile & Verify Skills (HITL)", use_container_width=True)

# Step 1 Profile Ingestion
if step_parse_btn or run_pipeline:
    if not resume_text and not resume_bytes:
        st.error("Please upload a PDF resume or paste resume text to proceed.")
    else:
        with st.spinner("Extracting complete candidate context (Skills, Experience, Projects, Certifications, GitHub & LinkedIn)..."):
            initial_state = {
                "resume_bytes": resume_bytes,
                "resume_text": resume_text,
                "target_role": target_role if target_role else "Data Engineer",
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
# 6-HUB INTERACTIVE WORKSPACE
# -------------------------------------------------------------------
tab_diag, tab_ats, tab_roadmap, tab_learn, tab_interview, tab_jobs = st.tabs([
    "📊 1. Skill Gap Diagnostic (HITL)",
    "🎯 2. ATS Audit & Live Resume Editor",
    "📅 3. Dynamic Action Roadmap",
    "📚 4. Learning Pack & GitHub Repos",
    "🎙️ 5. AI Mock Interview Hub",
    "💼 6. Live Job Opportunities"
])

res = st.session_state["adk_result"]

# -------------------------------------------------------------------
# HUB 1: DIAGNOSTIC & HUMAN-IN-THE-LOOP SKILL VERIFICATION
# -------------------------------------------------------------------
with tab_diag:
    st.subheader("📊 Dynamic Semantic Skill Gap Diagnostic & Profile Verification")
    if res:
        # HITL Candidate Skill Editor
        with st.expander("👤 Human-in-the-Loop: Candidate Verified Skills Editor", expanded=not res.get("match_score")):
            st.markdown("Review the skills extracted from your resume, projects, and GitHub. You can add or remove skills to refine the analysis.")
            current_skills = res.get("user_confirmed_skills") or res.get("unified_skills", [])
            
            col_add, col_sel = st.columns([1, 2])
            with col_add:
                new_skill = st.text_input("Add Unlisted Skill", placeholder="e.g. Terraform, FastAPI, dbt")
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
        st.info("👆 Upload or select a sample resume above and click **'🚀 Run Complete Multi-Agent Career Copilot'** or **'🔍 Step 1'** to begin!")

# -------------------------------------------------------------------
# HUB 2: ATS RESUME AUDIT & LIVE IN-BROWSER RESUME EDITOR
# -------------------------------------------------------------------
with tab_ats:
    st.subheader("🎯 ATS Compatibility Audit & Live In-Browser Tailored Resume Editor")
    if res and res.get("ats_audit"):
        ats = res.get("ats_audit", {})
        
        # Metric Cards
        col_ats1, col_ats2, col_ats3, col_ats4, col_ats5 = st.columns(5)
        with col_ats1:
            st.metric("Overall ATS Score", f"{ats.get('ats_score', 80)}/100")
        with col_ats2:
            st.metric("Formatting", f"{ats.get('formatting_score', 20)}/25")
        with col_ats3:
            st.metric("Keyword Density", f"{ats.get('keyword_score', 25)}/35")
        with col_ats4:
            st.metric("Measurable Impact", f"{ats.get('impact_score', 20)}/25")
        with col_ats5:
            st.metric("Completeness", f"{ats.get('completeness_score', 15)}/15")
            
        st.divider()
        col_str, col_fix = st.columns(2)
        with col_str:
            st.success("##### 🏆 ATS Strengths")
            for s in ats.get("strengths", []):
                st.write(f"• {s}")
        with col_fix:
            st.warning("##### ⚠️ Critical ATS Fixes")
            for f in ats.get("critical_fixes", []):
                st.write(f"• {f}")

        # Missing Keywords
        missing_kw = ats.get("missing_ats_keywords", [])
        if missing_kw:
            st.markdown("##### 🔑 High-Priority Missing ATS Keywords")
            st.write(" ".join([f"`{k}`" for k in missing_kw]))

        # AI Bullet Point Rewriter
        st.divider()
        st.subheader("✨ AI Power Bullet Point Optimizer (Google XYZ Formula)")
        rewrites = ats.get("power_bullet_rewrites", [])
        for r in rewrites:
            with st.container(border=True):
                st.markdown(f"❌ **Before (Weak)**: *\"{r.get('original')}\"*")
                st.markdown(f"✅ **After (Power Bullet)**: **\"{r.get('improved')}\"**")
                st.info(f"💡 **Recruiter Rationale**: {r.get('rationale')}")

        # Live In-Browser Resume Editor & Exporter
        tailored = res.get("tailored_resume")
        if tailored:
            st.divider()
            st.subheader("📝 Live In-Browser Tailored Resume Editor & Exporter")
            st.caption("Edit your tailored resume directly below. Any edits you make will be preserved in your PDF and Markdown downloads.")

            current_md = tailored.get("markdown_content", "")
            edited_md = st.text_area("Edit Tailored Resume (Markdown)", value=current_md, height=280)
            if edited_md != current_md:
                tailored["markdown_content"] = edited_md

            col_dl_pdf, col_dl_md = st.columns(2)
            with col_dl_pdf:
                pdf_bytes_out = generate_ats_pdf(tailored)
                st.download_button(
                    label="📄 Download Tailored Resume (PDF)",
                    data=pdf_bytes_out,
                    file_name=f"{tailored.get('candidate_name', 'Candidate')}_{target_role.replace(' ', '_')}_Resume.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            with col_dl_md:
                st.download_button(
                    label="📝 Download Tailored Resume (Markdown)",
                    data=edited_md,
                    file_name=f"{tailored.get('candidate_name', 'Candidate')}_{target_role.replace(' ', '_')}_Resume.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    else:
        st.info("👆 Run the multi-agent analysis to generate your ATS Compatibility Score and Tailored Resume!")

# -------------------------------------------------------------------
# HUB 3: 30-60-90 DAY DYNAMIC ACTION ROADMAP
# -------------------------------------------------------------------
with tab_roadmap:
    st.subheader("📅 Personalized 30-60-90 Day Upskilling Roadmap")
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
    else:
        st.info("👆 Run the multi-agent analysis to generate your customized action roadmap!")

# -------------------------------------------------------------------
# HUB 4: MULTI-FORMAT LEARNING & GITHUB REFERENCE PROJECTS
# -------------------------------------------------------------------
with tab_learn:
    st.subheader("📚 Curated Learning Pack & Public GitHub Reference Projects")
    if res:
        resources = res.get("learning_resources", {})

        # 1. Technical Books
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

        # 2. Research Papers (arXiv)
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
                        st.link_button("🌐 Open Documentation", d.get("url", "https://google.com"))

        # 4. Free Courses & Tutorials
        courses = resources.get("courses", [])
        if courses:
            st.markdown("#### 🎥 Free Video Tutorials & Interactive Courses")
            c_cols = st.columns(min(len(courses), 2))
            for i, c in enumerate(courses):
                with c_cols[i % len(c_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{c.get('title')}**")
                        st.caption(f"🎓 **Platform**: {c.get('platform')} | ⏳ {c.get('duration', '3 Hours')} | 💵 {c.get('cost', 'Free')}")
                        st.link_button("▶ Access Course", c.get("url", "https://youtube.com"))

        # 5. GitHub Reference Projects
        st.divider()
        st.subheader("🐙 Real Public GitHub Reference Repositories")
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
    else:
        st.info("👆 Run the multi-agent analysis to generate your curated Books, Research Papers, Docs, and GitHub projects!")

# -------------------------------------------------------------------
# HUB 5: INTERACTIVE MULTI-TURN AI MOCK INTERVIEWER
# -------------------------------------------------------------------
with tab_interview:
    st.subheader("🎙️ Interactive Multi-Turn AI Technical Interview Simulator")
    st.caption("Practice realistic scenario-based technical questions. The AI tests your missing skill gaps and core competencies, evaluates answers in real-time, and provides a final scorecard.")

    missing_skills = res.get("skills_gap", []) if res else []
    verified_skills = res.get("verified_skills", []) if res else []
    active_role = target_role if target_role else "Data Engineer"

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

# -------------------------------------------------------------------
# HUB 6: LIVE JOB OPPORTUNITIES & DIRECT APPLICATION PORTAL
# -------------------------------------------------------------------
with tab_jobs:
    st.subheader("💼 Live Job Market & 1-Click Application Portal")
    st.caption("Active job openings matching your target role with candidate skill match scores and direct application links.")

    col_j1, col_j2, col_j3 = st.columns([1, 1, 1])
    with col_j1:
        job_limit = st.selectbox("Job Results Limit", [5, 10, 15, 20, 25], index=1, format_func=lambda x: f"{x} Live Openings")
    with col_j2:
        job_loc = st.text_input("Target Location / Country", value="Remote / United States")
    with col_j3:
        st.write("")
        fetch_jobs_btn = st.button("🔄 Search Live Job Openings", type="primary", use_container_width=True)

    if fetch_jobs_btn:
        with st.spinner(f"Querying live active job openings for '{target_role}' in '{job_loc}'..."):
            jobs = st.session_state["adk_team"].job_market_agent.fetch_live_job_postings(
                target_role=target_role,
                location=job_loc,
                limit=job_limit,
                candidate_skills=res.get("verified_skills", []) if res else []
            )
            if res:
                res["live_jobs"] = jobs
            st.session_state["adk_result"] = res

    active_jobs = res.get("live_jobs", []) if res else []
    if active_jobs:
        st.markdown(f"#### 🎯 Found **{len(active_jobs)}** Live Opportunities for **{target_role}**")
        for j in active_jobs:
            with st.container(border=True):
                col_j_info, col_j_apply = st.columns([4, 1])
                with col_j_info:
                    st.markdown(f"### {j.get('title')} — `{j.get('company')}`")
                    st.markdown(f"📍 **Location**: `{j.get('location')}` | 💰 **Salary**: `{j.get('salary_range')}` | 🎯 **Candidate Match**: `{j.get('match_percentage', 75)}%`")
                    st.write(j.get("description_snippet"))
                    if j.get("key_skills"):
                        st.write("🔑 **Key Tech Stack**: " + " ".join([f"`{s}`" for s in j.get("key_skills", [])]))
                with col_j_apply:
                    st.link_button("🚀 Apply Now", j.get("apply_url", "https://google.com"), type="primary", use_container_width=True)
    else:
        st.info("👆 Click **'🔄 Search Live Job Openings'** to fetch 10–25+ live active postings for your target role!")
