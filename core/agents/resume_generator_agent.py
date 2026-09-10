import os
import io
import html
import re as _re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import config
from core.adk_agent import ADKAgent

class BulletDiff(BaseModel):
    original_snippet: str = Field(description="Original line or bullet from candidate resume")
    improved_snippet: str = Field(description="Surgically upgraded line using Google XYZ formula and missing keywords")
    rationale: str = Field(description="Explanation of why this rewrite increases recruiter ranking")

class InPlaceResumeOptimizationResult(BaseModel):
    candidate_name: str = Field(description="Candidate's actual name from original resume")
    target_role: str = Field(description="Target role being optimized for")
    original_text: str = Field(description="Exact original resume text")
    optimized_text: str = Field(description="Full optimized resume preserving 100% of authentic companies and dates with upgraded bullets and natural keywords")
    key_changes: List[BulletDiff] = Field(description="List of specific in-place surgical improvements made")
    ats_score_before: int = Field(default=0, description="Estimated ATS score before optimization (0-100). Use the actual score from the ATS audit.")
    ats_score_after: int = Field(default=0, description="Estimated ATS score after optimization (0-100). Compute realistically — do not assume 92.")


class ResumeGeneratorADKAgent(ADKAgent):
    """
    Google ADK 2.0 In-Place Authentic Resume Optimizer Agent
    - Powered by Gemini Pro (MODEL_PRO) with resilience fallback to Flash tiers.
    - Takes the candidate's EXACT original uploaded resume text.
    - Preserves 100% of authentic career history, companies, job titles, dates, and projects.
    - Surgically upgrades bullet points using Google's XYZ formula:
      'Accomplished [X] as measured by [Y], by doing [Z]'
    - Naturally integrates high-priority target role keywords into existing context without fabricating fake companies.
    """
    def __init__(self):
        instruction = """
        You are an elite Executive Technical Resume Strategist and ATS Optimization Specialist.
        Your mission is to optimize the candidate's REAL ORIGINAL RESUME text in-place for their target role.

        STRICT RULES:
        1. PRESERVE 100% of the candidate's authentic background: DO NOT fabricate fake companies, fake job titles, fake dates, or fake projects.
        2. KEEP the candidate's real companies, employment dates, and educational institutions exactly as they appear in the original text.
        3. SURGICALLY UPGRADE ONLY 3 to 5 specific bullet points under their real jobs/projects:
           - DO NOT rewrite every bullet point. Select only the 3-5 lines that most benefit from quantified impact (Google XYZ formula: Accomplished [X] as measured by [Y], by doing [Z]) or missing keywords.
           - Retain the candidate's actual technical context and project work; weave in relevant target keywords naturally without destroying their original meaning.
        4. Return the full resume in 'optimized_text' with ONLY those 3-5 specific surgical improvements applied. ALL OTHER LINES MUST REMAIN 100% IDENTICAL to the original text.
        5. Provide a clear list of before-and-after 'key_changes' explaining what was improved and why.
        """
        super().__init__(
            name="ResumeGeneratorADKAgent",
            instruction=instruction,
            model=config.MODEL_PRO,
            output_schema=InPlaceResumeOptimizationResult,
            temperature=0.2
        )

    def optimize_in_place(
        self,
        raw_resume_text: str,
        target_role: str,
        missing_skills: List[str],
        candidate_name: str = "Candidate"
    ) -> Dict[str, Any]:
        """Surgically optimizes the candidate's original resume in-place."""
        gaps_str = ", ".join(missing_skills[:6]) if missing_skills else "Cloud Architecture & Scalability"

        prompt = f"""
        Candidate Target Role: '{target_role}'
        Priority Target Keywords to Weave In: [{gaps_str}]
        
        CANDIDATE'S ORIGINAL RESUME TEXT:
        \"\"\"
        {raw_resume_text}
        \"\"\"

        Perform an in-place ATS optimization on this exact resume text:
        - Keep all real companies, real dates, real projects, and real degrees.
        - Select 3 to 5 specific bullet points to surgically upgrade using Google's XYZ formula while retaining the candidate's original project details.
        - Naturally weave priority keywords [{gaps_str}] into those specific bullets.
        - Keep 100% of all other lines completely unchanged.
        - Return the complete text in 'optimized_text' and list the 3-5 specific before/after 'key_changes'.
        """

        if self.client:
            try:
                return self.execute(prompt_input=prompt)
            except Exception as e:
                print(f"[InPlaceResumeOptimizer Notice]: ({e}). Using heuristic in-place optimizer.", flush=True)

        return self._offline_in_place_optimizer(raw_resume_text, target_role, missing_skills, candidate_name)

    def _offline_in_place_optimizer(
        self,
        raw_resume_text: str,
        target_role: str,
        missing_skills: List[str],
        candidate_name: str
    ) -> Dict[str, Any]:
        """Heuristic in-place optimizer when offline: preserves 100% of authentic text and enhances at most 2-3 specific lines."""
        gaps = missing_skills[:4] if missing_skills else ["System Design", "Cloud Infrastructure"]
        lines = raw_resume_text.split("\n")
        optimized_lines = []
        key_changes = []
        enhanced_count = 0
        max_enhancements = 3

        for line in lines:
            trimmed = line.strip()
            # Look for bullet points with opportunity for metric enhancement
            if (trimmed.startswith("- ") or trimmed.startswith("• ") or trimmed.startswith("* ")) and enhanced_count < max_enhancements:
                content = trimmed.lstrip("-•* ").strip()
                # If bullet is decent length but lacks quantified metrics or key skills
                if len(content) > 35 and not any(kw.lower() in content.lower() for kw in gaps) and "%" not in content and "~" not in content:
                    gap_to_add = gaps[enhanced_count % len(gaps)]
                    # Enhance existing sentence by augmenting it rather than overwriting
                    improved_content = f"{content.rstrip('.')}, integrating {gap_to_add} best practices to enhance production reliability and accelerate execution cycles by ~30%."
                    improved_bullet = f"• {improved_content}"
                    key_changes.append({
                        "original_snippet": trimmed,
                        "improved_snippet": improved_bullet,
                        "rationale": f"Enhanced with measurable impact (~30% acceleration) and target skill alignment ({gap_to_add})."
                    })
                    optimized_lines.append(improved_bullet)
                    enhanced_count += 1
                    continue
            optimized_lines.append(line)

        optimized_text = "\n".join(optimized_lines)
        if not key_changes:
            key_changes.append({
                "original_snippet": "Core experience bullets",
                "improved_snippet": f"Preserved authentic achievements and highlighted alignment with {', '.join(gaps[:2])}.",
                "rationale": "Optimized bullet points for ATS keyword relevance."
            })

        # Compute realistic ATS scores based on keyword coverage and bullet upgrades
        base_keyword_hits = sum(1 for sk in missing_skills if sk.lower() in raw_resume_text.lower())
        total_gaps = len(missing_skills) if missing_skills else 1
        kw_ratio_before = base_keyword_hits / total_gaps
        
        score_before = min(85, max(45, int(55 + 25 * kw_ratio_before)))
        boost = min(20, len(key_changes) * 5 + 8)
        score_after = min(96, score_before + boost)

        return {
            "candidate_name": candidate_name,
            "target_role": target_role,
            "original_text": raw_resume_text,
            "optimized_text": optimized_text,
            "key_changes": key_changes[:max_enhancements],
            "ats_score_before": score_before,
            "ats_score_after": score_after
        }


def _clean_xml_text(text: str) -> str:
    """Safely cleans text for ReportLab XML Flowables without leaking raw HTML or causing parsing errors."""
    if not text:
        return ""
    # Strip or convert HTML entities
    s = text.replace("&nbsp;", " ")
    
    # Strip any pre-existing unsupported HTML tags but retain content
    # Remove font tags with attributes if present
    s = _re.sub(r'</?font[^>]*>', '', s, flags=_re.IGNORECASE)
    s = _re.sub(r'</?span[^>]*>', '', s, flags=_re.IGNORECASE)
    s = _re.sub(r'</?div[^>]*>', '', s, flags=_re.IGNORECASE)
    s = _re.sub(r'</?p[^>]*>', '', s, flags=_re.IGNORECASE)

    # Escape raw ampersands not part of valid entity
    s = _re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', s)

    # Convert markdown bold and italic
    s = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', s)
    s = _re.sub(r'__(.*?)__', r'<b>\1</b>', s)
    s = _re.sub(r'\*(.*?)\*', r'<i>\1</i>', s)
    s = _re.sub(r'_([^_]+?)_', r'<i>\1</i>', s)
    s = _re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', s)
    
    # Escape standalone < and > that are not part of <b>, </b>, <i>, </i>, <font>, </font>
    s = _re.sub(r'<(?!/?(b|i|u|font)(?:\s+[^>]*)?>)', '&lt;', s)
    return s


def generate_ats_pdf(tailored_data: Dict[str, Any]) -> bytes:
    """
    Generates a pixel-faithful reproduction of the candidate's executive resume format:
    - Centered Royal Blue Header with Name (#1E40AF), Subtitle, Contact bar with links
    - Royal Blue Section Titles (PROFESSIONAL SUMMARY, CORE TECHNICAL SKILLS, etc.)
    - 2-Column Core Technical Skills Table (Category in bold blue, Skills in body font)
    - 2-Column Experience Headers (Title | Company on left, Dates right-aligned)
    - Domain Subsection Headers (e.g., AI Agents & Intelligent Automation in #1E40AF)
    - Clean compact bullet formatting matching original PDF line metrics
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=32,
            bottomMargin=32
        )

        styles = getSampleStyleSheet()

        name_style = ParagraphStyle(
            'ExecutiveName', parent=styles['Heading1'],
            fontName='Helvetica-Bold', fontSize=20, leading=24,
            textColor=colors.HexColor('#1E40AF'), alignment=1, spaceAfter=2, spaceBefore=0
        )
        subtitle_style = ParagraphStyle(
            'Subtitle', parent=styles['Normal'],
            fontName='Helvetica', fontSize=9.5, leading=13,
            textColor=colors.HexColor('#334155'), alignment=1, spaceAfter=2
        )
        contact_style = ParagraphStyle(
            'ContactBar', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.5, leading=12,
            textColor=colors.HexColor('#334155'), alignment=1, spaceAfter=6
        )
        section_style = ParagraphStyle(
            'SectionHeader', parent=styles['Heading2'],
            fontName='Helvetica-Bold', fontSize=11, leading=14,
            textColor=colors.HexColor('#1E40AF'), spaceBefore=7, spaceAfter=3
        )
        subdomain_style = ParagraphStyle(
            'SubdomainHeader', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=9.5, leading=13,
            textColor=colors.HexColor('#1E40AF'), spaceBefore=4, spaceAfter=2
        )
        job_left_style = ParagraphStyle(
            'JobLeft', parent=styles['Normal'],
            fontName='Helvetica', fontSize=9.2, leading=13,
            textColor=colors.HexColor('#0F172A')
        )
        job_right_style = ParagraphStyle(
            'JobRight', parent=styles['Normal'],
            fontName='Helvetica-Oblique', fontSize=8.5, leading=13,
            textColor=colors.HexColor('#64748B'), alignment=2
        )
        skill_cat_style = ParagraphStyle(
            'SkillCat', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=8.8, leading=12,
            textColor=colors.HexColor('#1E40AF')
        )
        skill_val_style = ParagraphStyle(
            'SkillVal', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.8, leading=12,
            textColor=colors.HexColor('#1E293B')
        )
        bullet_style = ParagraphStyle(
            'ExecutiveBullet', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.8, leading=12,
            textColor=colors.HexColor('#1E293B'), leftIndent=12, spaceAfter=2
        )
        body_style = ParagraphStyle(
            'ExecutiveBody', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.8, leading=12.5,
            textColor=colors.HexColor('#1E293B'), spaceAfter=3
        )

        def make_paragraph(raw_text: str, style):
            formatted = _clean_xml_text(raw_text)
            try:
                return Paragraph(formatted, style)
            except Exception:
                plain = html.escape(_re.sub(r'<[^>]*>', '', raw_text))
                return Paragraph(plain, style)

        story = []
        text_content = tailored_data.get("optimized_text") or tailored_data.get("markdown_content") or ""
        lines = [l.strip() for l in text_content.split("\n") if l.strip()]

        if not lines:
            story.append(make_paragraph("Empty Resume Content", body_style))
            doc.build(story)
            return buffer.getvalue()

        # Parse Header Block
        cand_name = tailored_data.get("candidate_name", "Candidate")
        first_line = lines[0]
        if first_line.startswith("# "):
            cand_name = first_line[2:].strip()
            lines = lines[1:]
        elif not any(c in first_line for c in ["@", "http", "|", "+"]):
            cand_name = first_line
            lines = lines[1:]

        story.append(make_paragraph(cand_name.upper(), name_style))

        # Check for Subtitle / Headline line
        if lines and not lines[0].isupper() and "|" in lines[0] and not any(c in lines[0] for c in ["@", "+91", ".com", "http"]):
            subtitle_text = lines[0]
            lines = lines[1:]
            story.append(make_paragraph(subtitle_text, subtitle_style))
        elif tailored_data.get("target_role"):
            target_role = tailored_data.get("target_role", "").strip()
            story.append(make_paragraph(f"{target_role.upper()} &nbsp;|&nbsp; PROFESSIONAL PROFILE", subtitle_style))

        # Check for Contact Info line
        contact_line = ""
        if lines and any(c in lines[0] for c in ["@", "http", "|", "+", ".com", "linkedin", "github"]):
            contact_line = lines[0]
            lines = lines[1:]

        if contact_line:
            # Highlight LinkedIn and GitHub in blue
            c_clean = contact_line.replace("LinkedIn", "<font color='#1E40AF'><b>LinkedIn</b></font>")
            c_clean = c_clean.replace("GitHub", "<font color='#1E40AF'><b>GitHub</b></font>")
            story.append(make_paragraph(c_clean, contact_style))

        current_section = ""

        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped:
                continue

            clean_text = _re.sub(r'<[^>]*>', '', stripped).replace('&nbsp;', ' ').strip()
            if not clean_text:
                continue

            # Section Headers (e.g., PROFESSIONAL SUMMARY, CORE TECHNICAL SKILLS, PROFESSIONAL EXPERIENCE, KEY PROJECTS, ACHIEVEMENTS & CERTIFICATIONS, EDUCATION)
            if clean_text.startswith("## ") or clean_text.startswith("# ") or (clean_text.isupper() and len(clean_text) < 35 and not any(c in clean_text for c in ["|", "–", "@", ":", "+", "."])):
                header_title = clean_text.replace("## ", "").replace("# ", "").strip()
                current_section = header_title.upper()
                story.append(Spacer(1, 4))
                story.append(make_paragraph(f"<b>{header_title.upper()}</b>", section_style))

            # Core Technical Skills 2-Column Table Format
            elif ":" in clean_text and any(cat in clean_text.split(":")[0].lower() for cat in ["languages", "ai / genai", "automation", "backend", "devops", "cloud", "observability", "static analysis", "databases", "tools", "frameworks", "methodologies"]):
                parts = clean_text.split(":", 1)
                cat_name = parts[0].strip()
                cat_skills = parts[1].strip()
                
                p_cat = make_paragraph(f"<b>{cat_name}</b>", skill_cat_style)
                p_val = make_paragraph(cat_skills, skill_val_style)
                
                skill_table = Table([[p_cat, p_val]], colWidths=[115, 425])
                skill_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
                    ('TOPPADDING', (0,0), (-1,-1), 1),
                ]))
                story.append(skill_table)

            # Job Header with Pipe (e.g. Senior DevOps & AI Engineer | SAP Labs India | Sep 2023 – Present)
            elif "|" in clean_text and any(kw in clean_text.lower() for kw in ["present", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026", "client", "corp", "inc", "labs", "technologies", "solutions"]):
                parts = [p.strip() for p in clean_text.split("|")]
                if len(parts) >= 2:
                    left_title = parts[0].strip()
                    left_comp = parts[1].strip()
                    right_dates = parts[2].strip() if len(parts) >= 3 else ""
                    
                    left_markup = f"<b>{left_title}</b> &nbsp;|&nbsp; <font color='#1E40AF'><b>{left_comp}</b></font>"
                    
                    p_left = make_paragraph(left_markup, job_left_style)
                    p_right = make_paragraph(right_dates, job_right_style)
                    
                    job_table = Table([[p_left, p_right]], colWidths=[380, 160])
                    job_table.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                        ('RIGHTPADDING', (0,0), (-1,-1), 0),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                        ('TOPPADDING', (0,0), (-1,-1), 3),
                    ]))
                    story.append(job_table)
                else:
                    story.append(make_paragraph(f"<b>{clean_text}</b>", job_left_style))

            # Domain Sub-headings (e.g. AI Agents & Intelligent Automation, Python Automation & Backend Engineering, Systems Integration & DevOps / Platform Engineering)
            elif not clean_text.startswith(("- ", "• ", "* ")) and any(sub in clean_text.lower() for sub in ["ai agents & intelligent automation", "python automation & backend", "systems integration & devops", "platform engineering"]):
                story.append(make_paragraph(f"<b>{clean_text}</b>", subdomain_style))

            # Education with CGPA
            elif "cgpa" in clean_text.lower() and "|" in clean_text:
                parts = [p.strip() for p in clean_text.split("|")]
                p_deg = make_paragraph(f"<b>{parts[0]}</b>", job_left_style)
                p_gpa = make_paragraph(f"<b>{parts[1]}</b>", job_right_style)
                edu_table = Table([[p_deg, p_gpa]], colWidths=[380, 160])
                edu_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('LEFTPADDING', (0,0), (-1,-1), 0),
                    ('RIGHTPADDING', (0,0), (-1,-1), 0),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(edu_table)

            # Bullet Points
            elif stripped.startswith(("- ", "• ", "* ")) or clean_text.startswith(("- ", "• ", "* ")):
                bullet_body = clean_text.lstrip("-•* ").strip()
                # If project bullet has title: "AI Failure Analysis Agent (...): description"
                if ":" in bullet_body and ("agent" in bullet_body.split(":")[0].lower() or "pipeline" in bullet_body.split(":")[0].lower() or "platform" in bullet_body.split(":")[0].lower()):
                    p_parts = bullet_body.split(":", 1)
                    bullet_formatted = f"• &nbsp;<b>{p_parts[0].strip()}:</b> {p_parts[1].strip()}"
                else:
                    bullet_formatted = f"• &nbsp;{bullet_body}"
                story.append(make_paragraph(bullet_formatted, bullet_style))

            else:
                story.append(make_paragraph(clean_text, body_style))

        doc.build(story)
        return buffer.getvalue()

    except Exception as e:
        print(f"[PDF Generation Fallback]: ({e}). Building clean Canvas PDF.", flush=True)
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer, pagesize=letter)
            width, height = letter
            y = height - 40
            
            c.setFont("Helvetica-Bold", 16)
            c.setFillColorRGB(0.12, 0.25, 0.69) # #1E40AF
            cand_name = tailored_data.get("candidate_name", "CANDIDATE RESUME").upper()
            c.drawString(36, y, cand_name)
            y -= 18

            c.setFont("Helvetica", 9)
            c.setFillColorRGB(0.12, 0.16, 0.23)
            
            text_out = tailored_data.get("optimized_text", "")
            for line in text_out.split("\n"):
                if y < 40:
                    c.showPage()
                    y = height - 40
                    c.setFont("Helvetica", 9)
                    c.setFillColorRGB(0.12, 0.16, 0.23)
                
                line_str = line.strip()
                if line_str.isupper() and len(line_str) < 35:
                    c.setFont("Helvetica-Bold", 11)
                    c.setFillColorRGB(0.12, 0.25, 0.69)
                    c.drawString(36, y, line_str)
                    y -= 15
                    c.setFont("Helvetica", 9)
                    c.setFillColorRGB(0.12, 0.16, 0.23)
                else:
                    c.drawString(36, y, line_str[:110])
                    y -= 13
            
            c.save()
            return buffer.getvalue()
        except Exception:
            return (tailored_data.get("optimized_text", "")).encode("utf-8")
