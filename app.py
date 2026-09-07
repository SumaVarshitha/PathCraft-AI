import streamlit as st
import os
import json
import config
from core.orchestrator import CareerCopilotADKTeam
from core.agents.resume_generator_agent import generate_ats_pdf
from test_resumes import STRONG_DATA_ENGINEER_RESUME, WEAK_DESIGNER_RESUME

# Page Setup
st.set_page_config(
    page_title="PathCraft AI - Career & Skill Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Header Title
st.title("🚀 PathCraft AI - Enterprise Career & Skill Intelligence")
st.markdown("**Powered by Google ADK 2.0, Vector Semantic RAG & Model Context Protocol (MCP) Tools**")

# Sidebar Configuration
st.sidebar.header("🔑 Google ADK 2.0 Configuration")
user_api_key = st.sidebar.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")

if user_api_key:
    os.environ["GOOGLE_API_KEY"] = user_api_key

if not os.getenv("GOOGLE_API_KEY"):
    st.sidebar.warning("⚠️ Enter a `GOOGLE_API_KEY` to enable Live Search Grounding & Gemini Embeddings.")

# Sample Resumes Selector in Sidebar
st.sidebar.divider()
st.sidebar.subheader("📄 1-Click Sample Resumes (Test Instantly)")
sample_choice = st.sidebar.selectbox(
    "Load Benchmark Resume Profile:",
    ["-- Select Sample Resume --", "1. Senior Data Engineer (Strong Match)", "2. AI / ML Engineer (Strong Match)", "3. Fullstack Web Developer", "4. UI/UX Designer (Weak Data Match)"]
)

# Initialize Session State
if "adk_team" not in st.session_state:
    st.session_state["adk_team"] = CareerCopilotADKTeam()
if "adk_result" not in st.session_state:
    st.session_state["adk_result"] = None

# Input Form
st.subheader("1. Candidate Profile & Target Role")
col1, col2 = st.columns(2)
with col1:
    default_role_idx = 0
    if "AI / ML" in sample_choice:
        default_role_idx = 2
    elif "Fullstack" in sample_choice:
        default_role_idx = 4
    elif "Data Engineer" in sample_choice:
        default_role_idx = 0

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
        index=default_role_idx,
        help="Select a role from the list or choose 'Custom Role' to enter any role."
    )
    if selected_role == "Custom Role (Type Below)":
        target_role = st.text_input(
            "Type Your Custom Target Role",
            placeholder="e.g. LLM Systems Engineer, Robotics Developer, Prompt Engineer"
        )
    else:
        target_role = selected_role
    
    st.caption(f"🎯 Selected Target Role: **{target_role if target_role else 'Data Engineer'}**")
    github_url = st.text_input("GitHub Profile URL / Username (Optional)", placeholder="https://github.com/username")

with col2:
    upload_type = st.radio("Resume Upload Format", ["Upload PDF File", "Paste Text"], horizontal=True)
    resume_text = ""
    resume_bytes = None
    
    # Pre-fill if sample selected
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
        resume_text = st.text_area("Paste Resume Text (Include Skills, Experience, and Projects)", value=resume_text, height=140, placeholder="Paste complete resume text here...")
    else:
        uploaded_pdf = st.file_uploader("Upload Resume PDF", type=["pdf"])
        if uploaded_pdf:
            resume_bytes = uploaded_pdf.read()
        elif resume_bytes:
            st.info(f"📄 Sample PDF Loaded: `{sample_choice}`")

# Run Pipeline Button
if st.button("🚀 Run Google ADK 2.0 Multi-Agent Team", type="primary", use_container_width=True):
    if not resume_text and not resume_bytes:
        st.error("Please upload a PDF resume or paste resume text to proceed.")
    else:
        with st.spinner("Executing Google ADK 2.0 Agent Team (ResumeParser ➔ SemanticGapAnalyzer ➔ ATSAuditor ➔ RoadmapArchitect ➔ LearningCurator ➔ GitHubDiscovery)..."):
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
                "ats_audit": None,
                "career_roadmap": None,
                "tailored_resume": None,
                "curated_courses": [],
                "learning_resources": {},
                "project_blueprints": [],
                "github_projects": [],
                "live_jobs": [],
                "interview_history": []
            }
            res = st.session_state["adk_team"].run_tab1_pipeline(initial_state)
            st.session_state["adk_result"] = res
            st.success("✅ Multi-Agent Analysis & Roadmap Synthesis Complete!")

st.divider()

# Clean 4-Hub Interface
tab_diag, tab_ats, tab_roadmap, tab_learn = st.tabs([
    "📊 1. Skill Gap Diagnostic",
    "🎯 2. ATS Audit & Resume Exporter",
    "📅 3. 30-60-90 Day Action Roadmap",
    "📚 4. Learning Pack & GitHub Repos"
])

res = st.session_state["adk_result"]

# -------------------------------------------------------------------
# TAB 1: DIAGNOSTIC & SEMANTIC MATCHING
# -------------------------------------------------------------------
with tab_diag:
    st.subheader("Google ADK 2.0 Semantic Skill Match Diagnostic")
    if res:
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

        with st.expander("🔍 View Complete Parsed Resume Context (Name, Projects, Certifications, Tools)"):
            st.json(res.get("resume_data", {}))
    else:
        st.info("👆 Upload or select a sample resume above and click **'🚀 Run Google ADK 2.0 Multi-Agent Team'** to see your live Skill Match Diagnostic!")

# -------------------------------------------------------------------
# TAB 2: ATS RESUME AUDIT & 1-CLICK TAILORED RESUME EXPORTER
# -------------------------------------------------------------------
with tab_ats:
    st.subheader("🎯 ATS Resume Compatibility Audit & 1-Click Tailored Resume Exporter")
    if res and res.get("ats_audit"):
        ats = res.get("ats_audit", {})
        
        # ATS Metric Cards
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
        st.subheader("✨ AI Power Bullet Point Optimizer (Before vs. After)")
        st.caption("Rewritten using Google's XYZ Formula: 'Accomplished [X] as measured by [Y], by doing [Z]'")
        
        rewrites = ats.get("power_bullet_rewrites", [])
        for r in rewrites:
            with st.container(border=True):
                st.markdown(f"❌ **Before (Weak)**: *\"{r.get('original')}\"*")
                st.markdown(f"✅ **After (ATS Power Bullet)**: **\"{r.get('improved')}\"**")
                st.info(f"💡 **Why this ranks higher**: {r.get('rationale')}")

        # 1-Click Tailored Resume Exporter Section
        tailored = res.get("tailored_resume")
        if tailored:
            st.divider()
            st.subheader("📥 1-Click Tailored ATS-Optimized Resume Exporter")
            st.caption("Download your recruiter-ready, ATS-compliant tailored resume in PDF or Markdown format.")
            
            pdf_bytes_out = generate_ats_pdf(tailored)
            md_content = tailored.get("markdown_content", "# Resume")
            
            col_dl_pdf, col_dl_md = st.columns(2)
            with col_dl_pdf:
                st.download_button(
                    label="📄 Download Tailored Resume (PDF)",
                    data=pdf_bytes_out,
                    file_name=f"{tailored.get('candidate_name', 'Tailored')}_{target_role.replace(' ', '_')}_Resume.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            with col_dl_md:
                st.download_button(
                    label="📝 Download Tailored Resume (Markdown)",
                    data=md_content,
                    file_name=f"{tailored.get('candidate_name', 'Tailored')}_{target_role.replace(' ', '_')}_Resume.md",
                    mime="text/markdown",
                    use_container_width=True
                )

            with st.expander("👁️ Preview Tailored Resume Content"):
                st.markdown(md_content)
    else:
        st.info("👆 Run the multi-agent analysis to generate your ATS Compatibility Score and 1-Click Tailored Resume!")

# -------------------------------------------------------------------
# TAB 3: 30-60-90 DAY CAREER ACTION ROADMAP
# -------------------------------------------------------------------
with tab_roadmap:
    st.subheader("📅 Personalized 30-60-90 Day Upskilling Action Roadmap")
    if res and res.get("career_roadmap"):
        rm = res.get("career_roadmap", {})
        st.caption(f"🎯 **Target Trajectory**: {rm.get('executive_summary', 'Structured career roadmap.')}")
        
        # Phase 1
        p1 = rm.get("phase_1_foundations", {})
        with st.expander(f"🟢 {p1.get('phase_title', 'Phase 1: Core Fundamentals')} ({p1.get('duration_days', 'Days 1-30')})", expanded=True):
            st.markdown("**Key Phase Objectives:**")
            for obj in p1.get("key_objectives", []):
                st.write(f"• {obj}")
            st.divider()
            st.markdown("**Weekly Milestone Actions:**")
            for w in p1.get("weeks", []):
                st.markdown(f"**Week {w.get('week_number')}: {w.get('focus_topic')}**")
                for act in w.get("action_items", []):
                    st.checkbox(f"{act}", key=f"p1_w{w.get('week_number')}_{act[:20]}")
                st.caption(f"📦 *Weekly Deliverable: {w.get('learning_deliverable')}*")
                st.write("")

        # Phase 2
        p2 = rm.get("phase_2_architecture", {})
        with st.expander(f"🟡 {p2.get('phase_title', 'Phase 2: Systems & Architecture')} ({p2.get('duration_days', 'Days 31-60')})", expanded=False):
            st.markdown("**Key Phase Objectives:**")
            for obj in p2.get("key_objectives", []):
                st.write(f"• {obj}")
            st.divider()
            st.markdown("**Weekly Milestone Actions:**")
            for w in p2.get("weeks", []):
                st.markdown(f"**Week {w.get('week_number')}: {w.get('focus_topic')}**")
                for act in w.get("action_items", []):
                    st.checkbox(f"{act}", key=f"p2_w{w.get('week_number')}_{act[:20]}")
                st.caption(f"📦 *Weekly Deliverable: {w.get('learning_deliverable')}*")
                st.write("")

        # Phase 3
        p3 = rm.get("phase_3_portfolio_launch", {})
        with st.expander(f"🔵 {p3.get('phase_title', 'Phase 3: Independent Portfolio & Launch')} ({p3.get('duration_days', 'Days 61-90')})", expanded=False):
            st.markdown("**Key Phase Objectives:**")
            for obj in p3.get("key_objectives", []):
                st.write(f"• {obj}")
            st.divider()
            st.markdown("**Weekly Milestone Actions:**")
            for w in p3.get("weeks", []):
                st.markdown(f"**Week {w.get('week_number')}: {w.get('focus_topic')}**")
                for act in w.get("action_items", []):
                    st.checkbox(f"{act}", key=f"p3_w{w.get('week_number')}_{act[:20]}")
                st.caption(f"📦 *Weekly Deliverable: {w.get('learning_deliverable')}*")
                st.write("")
    else:
        st.info("👆 Run the multi-agent analysis to synthesize your personalized 30-60-90 day career action roadmap!")

# -------------------------------------------------------------------
# TAB 4: MULTI-FORMAT LEARNING & REAL GITHUB PROJECTS
# -------------------------------------------------------------------
with tab_learn:
    st.subheader("📚 Curated Learning Pack & Real Public GitHub Reference Projects")
    if res:
        resources = res.get("learning_resources", {})

        # 1. Authoritative Technical Books
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
    else:
        st.info("👆 Run the multi-agent analysis to generate your curated Books, Research Papers, Docs, and Real GitHub projects!")
