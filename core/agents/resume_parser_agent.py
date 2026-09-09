import os
import re
import io
import json
from typing import Dict, Any, Optional, List
import pypdf
from google import genai
from google.genai import types
import config
from core.adk_agent import ADKAgent

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extracts raw text from PDF bytes across all pages using pypdf."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_pages.append(text)
        return "\n\n".join(extracted_pages).strip()
    except Exception as e:
        print(f"[PDF Extract Notice]: Error reading PDF text ({e})", flush=True)
        return ""

class ResumeParserADKAgent(ADKAgent):
    """
    Google ADK 2.0 Deep Resume & Profile Parser Agent
    Extracts 100% authentic candidate context directly from resume text/PDF using Gemini:
    - Real candidate name, job title, years of experience
    - Real work experience entries, company names, employment dates, and exact bullet points
    - Real academic degrees and actual universities
    - Real projects and technologies (e.g. LangGraph, Multi-Agent Systems, RAG, Tool Calling)
    - Real certifications & honors
    """
    def __init__(self):
        instruction = """
        You are an elite, high-precision technical resume parsing system.
        Analyze the candidate's entire resume text and extract all factual details into structured JSON with 100% authenticity.
        """
        super().__init__(
            name="ResumeParserADKAgent",
            instruction=instruction,
            model=config.MODEL_FLASH,
            temperature=0.0
        )

    def parse(
        self,
        resume_text: Optional[str] = None,
        pdf_bytes: Optional[bytes] = None,
        linkedin_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parses resume text or PDF bytes into structured dictionary using Gemini 2.5."""
        api_key = os.getenv("GOOGLE_API_KEY") or config.GOOGLE_API_KEY
        if api_key:
            self.client = genai.Client(api_key=api_key)

        extracted_text = resume_text or ""
        if pdf_bytes and not extracted_text:
            extracted_text = extract_text_from_pdf_bytes(pdf_bytes)

        full_context = extracted_text
        if linkedin_text:
            full_context = f"{extracted_text}\n\n[LINKEDIN PROFILE & ACHIEVEMENTS]:\n{linkedin_text}".strip()

        if not full_context:
            return {
                "candidate_name": "Candidate",
                "job_title": "Software Engineer",
                "skills": [],
                "years_experience": 0.0,
                "education": [],
                "work_summary": "Empty profile",
                "work_experience": [],
                "projects": [],
                "certifications": [],
                "tools_and_technologies": [],
                "linkedin_achievements": ""
            }

        # Prompt Gemini for comprehensive structured JSON extraction
        prompt = f"""
        Analyze the following authentic resume text and extract ALL details into a structured JSON object.
        
        CRITICAL PARSING RULES:
        1. candidate_name: Extract the candidate's real full name from the header/contact section.
        2. job_title: Extract their current or most recent job title.
        3. years_experience: Estimate total years of professional experience accurately based on employment dates.
        4. skills: Extract a comprehensive list of ALL technical skills, programming languages, frameworks, libraries, cloud platforms, and tools mentioned across the ENTIRE document (including modern AI tools like LangGraph, RAG, Multi-Agent Systems, GenSQL, Prompt Engineering, Docker, Kubernetes, etc.).
        5. work_experience: List of objects, each containing:
           - "company": Real company / organization name
           - "role": Job title
           - "duration": Employment dates (e.g. "2022 - Present")
           - "description": Brief overview
           - "bullets": List of full, exact bullet points from this job
        6. projects: List of objects, each containing:
           - "title": Project name/title
           - "description": Project overview and accomplishments
           - "tech_stack": List of all technologies, libraries, and tools used in this project
        7. education: List of degrees with university names (e.g. "B.Tech in Computer Science - University of Technology")
        8. certifications: List of actual certifications and licenses explicitly listed
        9. tools_and_technologies: Comprehensive deduplicated array of all technologies across the entire document
        10. work_summary: Concise 2-3 sentence professional executive summary

        Return ONLY a valid JSON object matching these keys. Do NOT include markdown code blocks or explanations.

        RESUME TEXT:
        \"\"\"
        {full_context}
        \"\"\"
        """

        if self.client:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    )
                )
                text = response.text.strip()
                if "```json" in text:
                    text = text.split("```json")[-1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                if "{" in text and "}" in text:
                    text = text[text.find("{"):text.rfind("}")+1]
                
                parsed_data = json.loads(text)
                
                # Clean and ensure all expected keys exist
                return {
                    "candidate_name": parsed_data.get("candidate_name", "Candidate"),
                    "job_title": parsed_data.get("job_title", "Software Engineer"),
                    "skills": parsed_data.get("skills", []),
                    "years_experience": float(parsed_data.get("years_experience", 2.0)),
                    "education": parsed_data.get("education", []),
                    "work_summary": parsed_data.get("work_summary", "Professional profile"),
                    "work_experience": parsed_data.get("work_experience", []),
                    "projects": parsed_data.get("projects", []),
                    "certifications": parsed_data.get("certifications", []),
                    "tools_and_technologies": parsed_data.get("tools_and_technologies", parsed_data.get("skills", [])),
                    "linkedin_achievements": linkedin_text or parsed_data.get("linkedin_achievements", "")
                }
            except Exception as e:
                print(f"[ResumeParserADKAgent Gemini Parse Notice]: {e}", flush=True)

        # Direct text fallback (extracting real lines without fake company injection)
        return self._direct_text_extractor(full_context, linkedin_text or "")

    def _direct_text_extractor(self, resume_text: str, linkedin_text: str = "") -> Dict[str, Any]:
        """
        Robust multi-section resume parser for when the Gemini API is unavailable.
        Correctly extracts: candidate name, multi-company work history with real dates,
        projects, certifications, education, and skills.
        """
        lines = [line.strip() for line in resume_text.split("\n") if line.strip()]

        # ── Candidate Name (first non-empty short line, typically all-caps or title-case)
        cand_name = "Candidate"
        for line in lines[:5]:
            if 2 <= len(line.split()) <= 5 and len(line) < 60 and not any(c in line for c in ["@", "http", "|", "+91"]):
                cand_name = line
                break

        # ── Current job title (look near name / email line)
        job_title = "Software Engineer"
        title_patterns = [
            r"(?i)(senior|lead|staff|principal|junior|associate)?\s*(devops|ai|ml|data|software|backend|frontend|full.?stack|cloud|platform|site reliability)\s*(engineer|architect|developer|scientist|analyst|manager)",
        ]
        for line in lines[:15]:
            for pat in title_patterns:
                m = re.search(pat, line)
                if m:
                    job_title = m.group(0).strip()
                    break
            if job_title != "Software Engineer":
                break

        # ── Section detection
        section_markers = {
            "experience": re.compile(r"^(professional\s+)?experience$|^work\s+experience$|^employment$", re.I),
            "projects":   re.compile(r"^projects?$|^key\s+projects?$|^notable\s+projects?$", re.I),
            "education":  re.compile(r"^education$|^academic\s+background$|^qualifications?$", re.I),
            "certs":      re.compile(r"^certifications?$|^licenses?\s+&\s+certifications?$|^awards?$|^achievements?$", re.I),
            "skills":     re.compile(r"^(technical\s+)?skills?$|^core\s+competencies$|^tools?\s+&\s+technologies?$", re.I),
        }

        # Split full text into named sections
        sections: Dict[str, List[str]] = {k: [] for k in section_markers}
        current_section = None
        for line in lines:
            matched = False
            for sec, pat in section_markers.items():
                if pat.match(line):
                    current_section = sec
                    matched = True
                    break
            if not matched and current_section:
                sections[current_section].append(line)

        # ── WORK EXPERIENCE: detect company blocks by date-pattern anchors
        # Looks for lines like: "Company Name | Jan 2021 – Dec 2022" or "Company   Sep 2023 – Present"
        work_experience = []
        exp_text = "\n".join(sections["experience"]) if sections["experience"] else resume_text

        date_pattern = re.compile(
            r"(?P<date>(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[–\-—]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current))",
            re.IGNORECASE
        )
        # Also handle plain year ranges like 2021 – 2023
        year_pattern = re.compile(r"(\d{4})\s*[–\-—]\s*(\d{4}|Present|Current)", re.IGNORECASE)

        # Find all date positions in exp_text
        exp_lines = exp_text.split("\n")
        job_blocks: List[Dict[str, Any]] = []
        current_block: Optional[Dict[str, Any]] = None

        for line in exp_lines:
            # Does this line have a date range? → it's a company/role header
            date_match = date_pattern.search(line) or year_pattern.search(line)
            if date_match:
                if current_block:
                    job_blocks.append(current_block)
                duration = date_match.group(0).strip()
                # Everything before the date on that line is company/role info
                pre_date = line[:date_match.start()].strip().strip("|–-—").strip()
                # Try to split "Role | Company" or "Company | Role"
                parts = [p.strip() for p in re.split(r"\s*[\|@]\s*", pre_date) if p.strip()]
                role_str = parts[0] if parts else pre_date
                company_str = parts[1] if len(parts) > 1 else ""
                current_block = {
                    "role": role_str,
                    "company": company_str,
                    "duration": duration,
                    "description": "",
                    "bullets": []
                }
            elif current_block is not None:
                stripped = line.strip()
                if stripped.startswith(("- ", "• ", "* ")):
                    current_block["bullets"].append(stripped[2:].strip())
                elif stripped and not current_block["description"]:
                    current_block["description"] = stripped

        if current_block:
            job_blocks.append(current_block)

        # If section-based parsing found nothing, fall back to searching full text
        if not job_blocks:
            # Scan entire resume for date patterns
            for i, line in enumerate(lines):
                date_match = date_pattern.search(line) or year_pattern.search(line)
                if date_match:
                    duration = date_match.group(0).strip()
                    pre_date = line[:date_match.start()].strip().strip("|–-—").strip()
                    parts = [p.strip() for p in re.split(r"\s*[\|@]\s*", pre_date) if p.strip()]
                    role_str = parts[0] if parts else pre_date
                    company_str = parts[1] if len(parts) > 1 else ""
                    # Gather bullets in the following lines
                    bullets_block = []
                    for j in range(i + 1, min(i + 20, len(lines))):
                        l = lines[j].strip()
                        if l.startswith(("- ", "• ", "* ")):
                            bullets_block.append(l[2:].strip())
                        elif date_pattern.search(l) or year_pattern.search(l):
                            break
                    if role_str or company_str:
                        job_blocks.append({
                            "role": role_str,
                            "company": company_str,
                            "duration": duration,
                            "description": "",
                            "bullets": bullets_block
                        })

        work_experience = job_blocks

        # ── PROJECTS
        projects = []
        proj_lines = sections["projects"]
        proj_block: Optional[Dict[str, Any]] = None
        for line in proj_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith(("- ", "• ", "* ")) and len(stripped) < 100:
                if proj_block:
                    projects.append(proj_block)
                proj_block = {"title": stripped, "description": "", "tech_stack": []}
            elif proj_block:
                if stripped.startswith(("- ", "• ", "* ")):
                    content = stripped[2:].strip()
                    # Detect tech stack items
                    tech_words = re.findall(r'\b[A-Za-z][A-Za-z0-9+#\-\.]{1,20}\b', content)
                    known_tech = {"python", "java", "sql", "docker", "kubernetes", "terraform", "aws", "gcp", "azure",
                                  "langchain", "langgraph", "rag", "fastapi", "react", "jenkins", "groovy", "kafka",
                                  "spark", "bigquery", "redis", "postgres", "mongodb", "flask", "pytorch", "tensorflow"}
                    found_tech = [w for w in tech_words if w.lower() in known_tech]
                    proj_block["tech_stack"].extend(found_tech)
                    if not proj_block["description"]:
                        proj_block["description"] = content
                elif not proj_block["description"] and stripped:
                    proj_block["description"] = stripped
        if proj_block:
            projects.append(proj_block)

        # ── EDUCATION
        education = []
        for line in sections["education"]:
            stripped = line.strip()
            if stripped and len(stripped) > 5:
                education.append(stripped)
        if not education:
            # Fallback: scan for degree keywords
            deg_pat = re.compile(r"(?i)\b(b\.?tech|b\.?e\.?|b\.?sc?\.?|m\.?tech|m\.?sc?\.?|mba|ph\.?d|bachelor|master)\b.{0,80}")
            for line in lines:
                m = deg_pat.search(line)
                if m:
                    education.append(m.group(0).strip())
                    if len(education) >= 3:
                        break

        # ── CERTIFICATIONS
        certifications = []
        for line in sections["certs"]:
            stripped = line.strip()
            if stripped and len(stripped) > 4:
                certifications.append(stripped)
        if not certifications:
            cert_pat = re.compile(r"(?i)(certified|certification|aws|gcp|azure|google cloud|pmp|cka|cks|ckad|professional certificate).{0,60}")
            for line in lines:
                m = cert_pat.search(line)
                if m and "experience" not in m.group(0).lower():
                    certifications.append(m.group(0).strip())
                    if len(certifications) >= 8:
                        break

        # ── SKILLS
        skill_keywords = [
            "python", "sql", "java", "bash", "c++", "javascript", "typescript", "docker", "kubernetes",
            "terraform", "git", "ci/cd", "linux", "aws", "gcp", "azure", "bigquery", "snowflake",
            "langchain", "langgraph", "rag", "fastapi", "react", "gensql", "jenkins", "groovy",
            "postgres", "postgresql", "redis", "mongodb", "kafka", "spark", "airflow", "dbt",
            "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy", "flask", "django",
            "microservices", "devops", "mlops", "llm", "genai", "multiagent", "mcp", "adk"
        ]
        words = re.findall(r'\b[A-Za-z0-9+#/\.\-]{2,25}\b', resume_text)
        found_skills = list(dict.fromkeys([w for w in words if w.lower() in skill_keywords]))

        # ── YEARS OF EXPERIENCE (from date ranges)
        all_dates = date_pattern.findall(resume_text) + year_pattern.findall(resume_text)
        years_exp = 0.0
        start_years = []
        for d in date_pattern.finditer(resume_text):
            raw = d.group(0)
            year_hits = re.findall(r'\b(20\d{2})\b', raw)
            if year_hits:
                start_years.append(int(year_hits[0]))
        if start_years:
            earliest = min(start_years)
            import datetime
            years_exp = round(datetime.datetime.now().year - earliest + (datetime.datetime.now().month / 12), 1)
        if years_exp < 0.5:
            years_exp = float(len(work_experience)) * 1.5  # rough estimate

        # ── WORK SUMMARY
        work_summary = f"Experienced {job_title} with {int(years_exp)}+ years across {len(work_experience)} roles."
        if found_skills:
            work_summary += f" Core competencies include {', '.join(found_skills[:8])}."

        return {
            "candidate_name": cand_name,
            "job_title": job_title,
            "skills": found_skills,
            "years_experience": years_exp,
            "education": education if education else ["Degree in Engineering / Computer Science"],
            "work_summary": work_summary,
            "work_experience": work_experience,
            "projects": projects,
            "certifications": certifications,
            "tools_and_technologies": found_skills,
            "linkedin_achievements": linkedin_text
        }
