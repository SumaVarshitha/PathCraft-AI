import streamlit as st
import os
import json
import config
from core.orchestrator import CareerCopilotADKTeam
from core.agents.resume_generator_agent import generate_ats_pdf
from test_resumes import (
    STRONG_DATA_ENGINEER_RESUME,
    AIML_ENGINEER_RESUME,
    FULLSTACK_DEVELOPER_RESUME,
    WEAK_DESIGNER_RESUME
)


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
st.markdown("**Autonomous Multi-Agent Career Platform powered by Google ADK 2.0, Gemini 2.5 Flash, Dynamic Search Grounding & MCP Tools**")

# One‑time onboarding banner (shows only on first load)
if "onboard_shown" not in st.session_state:
    st.info(
        "👋 Welcome to PathCraft AI! Upload your resume, pick a target role, and let 10 autonomous agents do the rest. Expand the guide below if you need help getting started."
    )
    st.session_state["onboard_shown"] = True

# Quick‑use help expander (optional, collapsible)
with st.expander("❓ How to use PathCraft AI (quick guide)"):
    st.markdown(
        """
        **Step‑by‑Step Guide**

        1. **Select a benchmark resume or upload your own** – In the sidebar you can pick a ready‑made benchmark profile (e.g., Senior Data Engineer). If you prefer a custom resume, upload a PDF or paste the full text into the textarea. The system will extract your work history, projects, and achievements.

        2. **Provide your GitHub profile URL** – Enter the URL of a public GitHub account (or just the username). PathCraft AI will pull repository statistics, programming languages, and contribution metrics as additional evidence of your technical expertise.

        3. **Select your target role and seniority** – Choose the exact job title you aim for (e.g., *Data Engineer*, *AI/ML Engineer*) and the seniority level (Junior, Mid‑Level, Senior, etc.). This informs the agents which market requirements to benchmark against.

        4. **Launch the multi‑agent pipeline** – Click **Launch PathCraft AI Multi‑Agent Pipeline**. This triggers ten autonomous agents that will analyse your profile, identify skill gaps, optimise your resume, generate a personalised learning roadmap, and even run a mock interview.

        5. **Explore the four interactive hubs** – Once the pipeline completes, the following hubs appear:
           - 📊 **Skill Gap Diagnostic** – Detailed comparison of core versus differentiator skills.
           - ✍️ **Resume Optimiser** – ATS‑score improvements with side‑by‑side diff and PDF export.
           - 📅 **30‑60‑Day Roadmap** – Adaptive learning plan with resource recommendations.
           - 🎙️ **Mock Interview** – AI‑generated technical questions with instant feedback.
        """
    )



# Sidebar Configuration
st.sidebar.header("🔑 Google ADK 2.0 Engine Settings")
user_api_key = st.sidebar.text_input(
    "Google API Key (Optional)", 
    value="", 
    type="password",
    help="Enter your own Gemini API Key to test with your custom quota/key."
)

if user_api_key.strip():
    os.environ["GOOGLE_API_KEY"] = user_api_key.strip()
    st.sidebar.success("✅ Custom API Key Active")
elif os.getenv("GOOGLE_API_KEY"):
    st.sidebar.info("⚡ Using Default System API Key")
else:
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
    sample_text_map = {
        "1. Senior Data Engineer (Strong Match)": STRONG_DATA_ENGINEER_RESUME,
        "2. AI / ML Engineer (Strong Match)": AIML_ENGINEER_RESUME,
        "3. Fullstack Web Developer": FULLSTACK_DEVELOPER_RESUME,
        "4. UI/UX Designer (Weak Data Match)": WEAK_DESIGNER_RESUME
    }
    
    benchmark_active = sample_choice in sample_text_map
    if benchmark_active:
        st.success(f"📄 **Benchmark Profile Active**: `{sample_choice}`")
        default_resume_text = sample_text_map[sample_choice].strip()
    else:
        default_resume_text = ""

    upload_type = st.radio("Resume Upload Format", ["Paste / Edit Resume Text", "Upload PDF File"], horizontal=True)
    resume_text = ""
    resume_bytes = None
    
    if upload_type == "Paste / Edit Resume Text":
        resume_text = st.text_area(
            "Candidate Resume Text", 
            value=default_resume_text, 
            height=180, 
            placeholder="Paste complete resume text here or select a benchmark profile from the sidebar..."
        )
    else:
        uploaded_pdf = st.file_uploader("Upload Resume PDF (Complete Multi-Page Resume)", type=["pdf"])
        if uploaded_pdf:
            resume_bytes = uploaded_pdf.read()
        elif benchmark_active:
            # Fallback to benchmark text when benchmark is active in PDF mode
            resume_text = default_resume_text
            st.info(f"✅ Using loaded profile text for `{sample_choice}`.")

# Action Execution Button
st.write("")
run_pipeline = st.button("🚀 Launch PathCraft AI Multi-Agent Pipeline", type="primary", use_container_width=True)

# Profile Ingestion & Full Pipeline Execution
if run_pipeline:
    if not resume_text and not resume_bytes:
        st.error("Please upload a PDF resume, paste resume text, or select a benchmark profile from the sidebar to proceed.")
    else:
        with st.status("🚀 Running PathCraft AI Multi-Agent Pipeline...", expanded=True) as status:
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
            
            st.write("🤖 **PathCraft AI Orchestrator**: Running full 10-agent intelligence pipeline...")
            st.session_state["adk_result"] = st.session_state["adk_team"].run_full_pipeline(initial_state)
            status.update(label="✅ Complete Multi-Agent Pipeline Executed Successfully!", state="complete", expanded=False)

st.divider()

# -------------------------------------------------------------------
# FOCUSED 4-HUB INTERACTIVE WORKSPACE
# -------------------------------------------------------------------
tab_diag, tab_resume, tab_roadmap, tab_interview = st.tabs([
    "📊 1. Skill Gap Diagnostic",
    "✍️ 2. Resume Optimizer",
    "📅 3. Roadmap & Learning",
    "🎙️ 4. Mock Interview"
])

res = st.session_state["adk_result"]

# -------------------------------------------------------------------
# HUB 1: SKILL GAP DIAGNOSTIC & CANDIDATE DIFFERENTIATORS
# -------------------------------------------------------------------
with tab_diag:
    st.subheader("📊 Dynamic Semantic Skill Gap Diagnostic")
    if res:
        # Key Differentiators Card
        differentiators = res.get("candidate_superpowers", [])
        if differentiators:
            with st.container(border=True):
                st.markdown("#### 🌟 Key Differentiators & Advanced Competencies")
                st.caption("High-value skills detected across your work history, projects, and certifications that set you apart from baseline candidates:")
                tags_html = "  ".join([f"`{sp}`" for sp in differentiators])
                st.write(tags_html)

        # High-Synergy Alternate Role Suggestions (Always shown if available)
        alt_roles = res.get("suggested_alternate_roles", [])
        if alt_roles:
            with st.container(border=True):
                st.markdown("#### 💡 High-Synergy Alternate Roles For Your Background")
                st.caption("Based on your verified skills and project evidence, you are also highly competitive for these alternative career paths:")
                for ar in alt_roles:
                    st.info(f"🎯 **{ar.get('role')}** &nbsp;·&nbsp; **Est. Match: `{ar.get('estimated_match')}`**\n\n{ar.get('rationale')}")

        # GitHub Profile Card
        gh_data = res.get("github_data")
        if gh_data and (gh_data.get("languages") or gh_data.get("top_repositories")):
            with st.expander(f"🐙 GitHub Profile: `{gh_data.get('username', '')}` — Verified Technical Evidence", expanded=True):
                gh_langs = gh_data.get("languages", [])
                if gh_langs:
                    st.markdown("**Verified Programming Languages:**")
                    st.write("  ".join([f"`{l}`" for l in gh_langs]))
                
                gh_repos = gh_data.get("top_repositories", [])
                if gh_repos:
                    st.markdown("**Top Public Repositories & Inferred Technical Scope:**")
                    for repo in gh_repos:
                        repo_name = repo.get("name", "Repository")
                        url = repo.get("html_url") or f"https://github.com/{gh_data.get('username')}/{repo_name}"
                        lang = repo.get("language")
                        lang_badge = f" · `{lang}`" if lang else ""
                        stars = f" · ⭐ {repo.get('stars', 0)}" if repo.get("stars", 0) > 0 else ""
                        forks = f" · 🍴 {repo.get('forks', 0)}" if repo.get("forks", 0) > 0 else ""
                        desc = repo.get("description") or "Open-source software project implementing core architectural modules."
                        topics = repo.get("topics", [])
                        topic_str = f" `{'` `'.join(topics)}`" if topics else ""
                        
                        st.markdown(
                            f"• **[{repo_name}]({url})**{lang_badge}{stars}{forks}{topic_str}\n\n"
                            f"  &nbsp;&nbsp;&nbsp;_{desc}_"
                        )

        if res.get("match_score") is not None and res.get("match_score") > 0:
            st.info(f"**Market Data Source**: `{res.get('analysis_method', 'Live 2026 Market Search Grounding')}`")

            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("Overall Weighted Match", f"{res.get('match_score', 0.0)}%", help="Weighted: 70% Core Must-Haves + 30% Differentiators")
            with m_col2:
                st.metric("Core Skills Match", f"{res.get('core_match_score', 0.0)}%", help="Foundational non-negotiable requirements")
            with m_col3:
                total_reqs = len(res.get("semantic_matches", []))
                verified_cnt = len(res.get("verified_skills", []))
                st.metric("Requirements Satisfied", f"{verified_cnt}/{total_reqs}")

            st.divider()
            col_v, col_m = st.columns(2)
            with col_v:
                st.success("##### Verified Skills")
                verified = res.get("verified_skills", [])
                if verified:
                    st.write(", ".join([f"`{s}`" for s in verified]))
                else:
                    st.write("No matching skills identified for this role.")

            with col_m:
                st.error("##### Skill Gaps — Priority Areas to Develop")
                gaps = res.get("skills_gap", [])
                if gaps:
                    st.write(", ".join([f"`{s}`" for s in gaps]))
                else:
                    st.write("No critical skill gaps detected for this role.")

            # Semantic Match Breakdown Table
            sem_matches = res.get("semantic_matches", [])
            if sem_matches:
                st.markdown("##### Semantic Matching Breakdown — Evidence-Backed Analysis")
                st.caption("Skills are matched against your work bullets, project descriptions, certifications, tools, and GitHub repos — not just your skills list.")
                table_data = []
                for item in sem_matches:
                    table_data.append({
                        "Required Skill": item.get("required_skill"),
                        "Tier": item.get("skill_category", "Core Must-Have"),
                        "Matched Evidence": item.get("matched_candidate_skill") or "—",
                        "Source": item.get("evidence_source", "—"),
                        "Score": f"{item.get('similarity_score', 0.0):.2f}",
                        "Status": "MATCH" if item.get("is_match") else "GAP"
                    })
                st.dataframe(table_data, use_container_width=True)


        st.divider()
        # ── Skill Correction Panel (Human-in-the-Loop Checkpoint)
        with st.expander("🛡️ Human-in-the-Loop (HITL) Checkpoint — Review & Fine-Tune Extracted Skills", expanded=False):
            st.caption("🤝 **Human-in-the-Loop (HITL) Oversight**: The AI automatically extracts skills across your resume and GitHub. Use this checkpoint to add missing competencies or remove inaccurate extractions, then re-run the pipeline with your verified human input.")
            current_skills = res.get("user_confirmed_skills") or res.get("unified_skills", [])

            col_add, col_sel = st.columns([1, 2])
            with col_add:
                new_skill = st.text_input("Add a Missing Skill", placeholder="e.g. LangGraph, RAG, dbt")
                if st.button("➕ Add Skill"):
                    if new_skill and new_skill.strip() not in current_skills:
                        current_skills.append(new_skill.strip())
                        res["user_confirmed_skills"] = current_skills
                        st.rerun()

            with col_sel:
                confirmed = st.multiselect("Verified Skills List (uncheck to remove)", options=current_skills, default=current_skills)
                if confirmed != current_skills:
                    res["user_confirmed_skills"] = confirmed

            if st.button("🔄 Re-run Pipeline with Confirmed Human Input", type="primary"):
                with st.spinner("Re-analyzing with human-confirmed skill inputs against live 2026 market standards..."):
                    res = st.session_state["adk_team"].run_full_pipeline(res)
                    st.session_state["adk_result"] = res
                    st.rerun()
    else:
        st.info("Upload or select a sample resume above and click **'Run Complete Career Copilot Pipeline'** to begin.")


# -------------------------------------------------------------------
# HUB 2: AUTHENTIC IN-PLACE RESUME OPTIMIZER (SIDE-BY-SIDE DIFF)
# -------------------------------------------------------------------
with tab_resume:
    st.subheader("✍️ Authentic In-Place Resume Optimizer")
    st.caption("Your real resume is preserved exactly — companies, dates, and projects are untouched. Only bullet phrasing and keyword density are upgraded.")

    if res and res.get("tailored_resume"):
        tailored = res.get("tailored_resume", {})

        # ── ATS Score Metrics
        ats = res.get("ats_audit", {})
        ats_score_before = tailored.get("ats_score_before", ats.get("ats_score", 68))
        ats_score_after = tailored.get("ats_score_after", 92)

        c_sc1, c_sc2, c_sc3 = st.columns(3)
        with c_sc1:
            st.metric("Original ATS Score", f"{ats_score_before}/100")
        with c_sc2:
            st.metric("Optimized ATS Score", f"{ats_score_after}/100", delta=f"+{ats_score_after - ats_score_before} pts")
        with c_sc3:
            st.metric("Target Role", f"{target_role}")

        # ── Granular ATS Score Breakdown & Audit Details
        with st.expander("🔍 View Detailed ATS Audit Breakdown & Criteria", expanded=False):
            sc_col1, sc_col2, sc_col3, sc_col4 = st.columns(4)
            with sc_col1:
                st.metric("Formatting & Structure", f"{ats.get('formatting_score', 0)}/25", help="Section headers, chronological layout, parser readability")
            with sc_col2:
                st.metric("Keyword Match", f"{ats.get('keyword_score', 0)}/35", help="Target role skill density and placement")
            with sc_col3:
                st.metric("Impact & Metrics", f"{ats.get('impact_score', 0)}/25", help="Action verbs, quantified scale, Google XYZ impact")
            with sc_col4:
                st.metric("Section Completeness", f"{ats.get('completeness_score', 0)}/15", help="Presence of summary, experience, projects, education, skills")

            st.divider()
            col_str, col_fix = st.columns(2)
            with col_str:
                st.markdown("**Resume Strengths Identified:**")
                for s in ats.get("strengths", []):
                    st.markdown(f"• {s}")
            with col_fix:
                st.markdown("**Critical Fixes Recommended:**")
                fixes_list = ats.get("critical_fixes", [])
                if fixes_list:
                    for f in fixes_list:
                        st.markdown(f"• {f}")
                else:
                    st.markdown("• Profile satisfies core ATS requirements with high keyword alignment.")

        # ── Proposed Surgical Enhancements with HITL Checkbox Approvals
        key_changes = tailored.get("key_changes", [])
        applied_changes = []
        if key_changes:
            st.divider()
            st.markdown("##### 🔍 Proposed Surgical Enhancements (Review & Select Which Changes to Apply)")
            st.caption("Review each targeted enhancement. Check the boxes for the improvements you want applied to your authentic resume:")
            
            for i, chg in enumerate(key_changes):
                with st.container(border=True):
                    c_col1, c_col2 = st.columns([0.85, 0.15])
                    with c_col1:
                        st.markdown(f"**Original:** *\"{chg.get('original_snippet')}\"*")
                        st.markdown(f"**Proposed Enhancement:** **\"{chg.get('improved_snippet')}\"**")
                        st.caption(f"💡 *Rationale:* {chg.get('rationale')}")
                    with c_col2:
                        accept = st.checkbox("Apply", value=True, key=f"apply_enhancement_{i}")
                        if accept:
                            applied_changes.append(chg)

        # ── Version selector: use optimized or revert to original
        st.divider()
        use_original = st.toggle(
            "Use 100% Original Resume (revert all optimizations)",
            value=False,
            help="Switch to your original uploaded resume without any modifications."
        )

        original_text = tailored.get("original_text") or res.get("resume_text", "")
        
        # Dynamically build optimized text based only on accepted changes
        custom_optimized_text = original_text
        for chg in applied_changes:
            orig_snip = chg.get("original_snippet", "").strip()
            imp_snip = chg.get("improved_snippet", "").strip()
            if orig_snip and imp_snip and orig_snip in custom_optimized_text:
                custom_optimized_text = custom_optimized_text.replace(orig_snip, imp_snip)
            elif orig_snip and imp_snip:
                # Also try without leading bullet symbols
                orig_clean = orig_snip.lstrip("-•* ").strip()
                imp_clean = imp_snip.lstrip("-•* ").strip()
                if orig_clean in custom_optimized_text:
                    custom_optimized_text = custom_optimized_text.replace(orig_clean, imp_clean)

        optimized_text = custom_optimized_text if applied_changes else tailored.get("optimized_text", original_text)
        active_text = original_text if use_original else optimized_text

        # ── Side-by-Side Comparison with diff highlighting
        st.markdown("##### Side-by-Side Comparison")
        st.caption("Lines highlighted in the optimized version indicate changes from the original.")

        col_orig, col_opt = st.columns(2)

        orig_lines = original_text.splitlines()
        opt_lines = optimized_text.splitlines()

        # Build highlighted HTML for optimized side
        import difflib
        import html
        diff_matcher = difflib.SequenceMatcher(None, orig_lines, opt_lines)

        highlighted_orig = []
        highlighted_opt = []

        for tag, i1, i2, j1, j2 in diff_matcher.get_opcodes():
            for line in orig_lines[i1:i2]:
                safe_line = html.escape(line) if line else "&nbsp;"
                if tag == "replace":
                    highlighted_orig.append(f'<div style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-left:3px solid #ef4444;margin:1px 0;white-space:pre-wrap;word-break:break-word;">{safe_line}</div>')
                elif tag == "delete":
                    highlighted_orig.append(f'<div style="background:#fee2e2;color:#991b1b;text-decoration:line-through;padding:2px 8px;border-left:3px solid #ef4444;margin:1px 0;white-space:pre-wrap;word-break:break-word;">{safe_line}</div>')
                else:
                    highlighted_orig.append(f'<div style="color:#0f172a;padding:2px 8px;margin:1px 0;white-space:pre-wrap;word-break:break-word;">{safe_line}</div>')
            for line in opt_lines[j1:j2]:
                safe_line = html.escape(line) if line else "&nbsp;"
                if tag in ("replace", "insert"):
                    highlighted_opt.append(f'<div style="background:#dcfce7;color:#166534;font-weight:500;padding:2px 8px;border-left:3px solid #22c55e;margin:1px 0;white-space:pre-wrap;word-break:break-word;">{safe_line}</div>')
                else:
                    highlighted_opt.append(f'<div style="color:#0f172a;padding:2px 8px;margin:1px 0;white-space:pre-wrap;word-break:break-word;">{safe_line}</div>')

        diff_css = "font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace;font-size:12.5px;line-height:1.55;overflow-y:auto;max-height:450px;border:1px solid #cbd5e1;border-radius:8px;padding:10px;background:#ffffff;color:#0f172a !important;"

        with col_orig:
            st.markdown("**Original Resume**")
            orig_html = "".join(highlighted_orig)
            st.markdown(f'<div style="{diff_css}">{orig_html}</div>', unsafe_allow_html=True)

        with col_opt:
            st.markdown("**Optimized Resume** *(🟢 green = enhanced lines)*")
            if use_original:
                plain_html = "".join([f'<div style="color:#0f172a;padding:2px 8px;margin:1px 0;white-space:pre-wrap;word-break:break-word;">{html.escape(l) if l else "&nbsp;"}</div>' for l in orig_lines])
                st.markdown(f'<div style="{diff_css}">{plain_html}</div>', unsafe_allow_html=True)
            else:
                opt_html = "".join(highlighted_opt)
                st.markdown(f'<div style="{diff_css}">{opt_html}</div>', unsafe_allow_html=True)

        # ── Editable area for final tweaks
        st.divider()
        st.markdown("##### Edit & Finalize Your Resume")
        st.caption("Make any final edits below before downloading. Changes are saved automatically in this session.")

        edited_text = st.text_area(
            "Editable Resume Text",
            value=active_text,
            height=420,
            label_visibility="collapsed"
        )

        # Persist edits back into state
        if use_original:
            tailored["original_text"] = edited_text
        else:
            tailored["optimized_text"] = edited_text
        res["tailored_resume"] = tailored
        st.session_state["adk_result"] = res

        # ── Single PDF Download
        st.divider()
        final_for_pdf = {**tailored, "optimized_text": edited_text}
        pdf_bytes_out = generate_ats_pdf(final_for_pdf)
        cand_name = tailored.get("candidate_name", "Candidate").replace(" ", "_")
        role_slug = target_role.replace(" ", "_").replace("/", "-")
        version_tag = "Original" if use_original else "Optimized"

        st.download_button(
            label=f"Download Resume as PDF ({version_tag})",
            data=pdf_bytes_out,
            file_name=f"{cand_name}_{role_slug}_{version_tag}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=False
        )

    else:
        st.info("Run the pipeline to generate an optimized resume.")


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

        # Free Video Courses & YouTube Crash Courses
        courses = resources.get("courses", []) or res.get("curated_courses", [])
        if courses:
            st.markdown("#### 📺 Free Video Courses & YouTube Masterclasses")
            c_cols = st.columns(min(len(courses), 2))
            for i, c in enumerate(courses):
                with c_cols[i % len(c_cols)]:
                    with st.container(border=True):
                        st.markdown(f"**{c.get('title')}**")
                        st.caption(f"🎯 **Skill**: `{c.get('skill')}` &nbsp;·&nbsp; 🏢 **Platform**: {c.get('platform', 'YouTube')} &nbsp;·&nbsp; ⏱️ **Duration**: {c.get('duration', '3-5 Hours')}")
                        course_url = c.get("url") or f"https://www.youtube.com/results?search_query={c.get('skill', '').replace(' ', '+')}+full+course"
                        st.link_button("▶️ Watch Free Course on YouTube", course_url, type="secondary")

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
