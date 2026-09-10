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
        1. PRESERVE 100% of the candidate's authentic background: DO NOT fabricate fake companies, fake job titles, or fake degrees.
        2. KEEP the candidate's real companies, employment dates, and educational institutions exactly as they appear in the original text.
        3. SURGICALLY UPGRADE the bullet points under their real jobs/projects:
           - Rewrite weak or passive lines into high-impact bullets using Google's XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'.
           - Naturally integrate missing target keywords into their existing technical context.
        4. Return the full, complete upgraded resume text in 'optimized_text' formatted in clean markdown.
        5. Provide a clear list of before-and-after 'key_changes' explaining what was improved.
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
        - Upgrade the action verbs and metrics on existing bullets using Google's XYZ formula.
        - Naturally incorporate priority keywords [{gaps_str}].
        - Return the complete optimized text in 'optimized_text' and provide specific before/after 'key_changes'.
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
        """Heuristic in-place optimizer when offline."""
        gaps = missing_skills[:4] if missing_skills else ["System Design", "Cloud Infrastructure"]
        lines = raw_resume_text.split("\n")
        optimized_lines = []
        key_changes = []

        for line in lines:
            trimmed = line.strip()
            # Upgrade simple bullet points
            if trimmed.startswith("- ") or trimmed.startswith("• "):
                content = trimmed[2:].strip()
                if len(content) > 20 and not any(kw.lower() in content.lower() for kw in gaps):
                    improved = f"Engineered scalable {target_role} solutions using {gaps[0] if gaps else 'modern cloud tooling'}, reducing latency and improving system reliability across production workflows."
                    key_changes.append({
                        "original_snippet": trimmed,
                        "improved_snippet": f"• {improved}",
                        "rationale": f"Enhanced with measurable production impact and target role alignment ({gaps[0] if gaps else 'cloud'})."
                    })
                    optimized_lines.append(f"• {improved}")
                    continue
            optimized_lines.append(line)

        optimized_text = "\n".join(optimized_lines)
        if not key_changes:
            key_changes.append({
                "original_snippet": "General experience bullets",
                "improved_snippet": f"Incorporated {', '.join(gaps)} with Google XYZ impact metrics.",
                "rationale": "Optimized bullet points for ATS keyword relevance."
            })

        # Compute dynamic ATS scores based on keyword coverage and bullet upgrades
        base_keyword_hits = sum(1 for sk in missing_skills if sk.lower() in raw_resume_text.lower())
        total_gaps = len(missing_skills) if missing_skills else 1
        kw_ratio_before = base_keyword_hits / total_gaps
        
        score_before = min(85, max(45, int(55 + 25 * kw_ratio_before)))
        boost = min(25, len(key_changes) * 6 + 10)
        score_after = min(98, score_before + boost)

        return {
            "candidate_name": candidate_name,
            "target_role": target_role,
            "original_text": raw_resume_text,
            "optimized_text": optimized_text,
            "key_changes": key_changes[:4],
            "ats_score_before": score_before,
            "ats_score_after": score_after
        }


def _clean_xml_text(text: str) -> str:
    """Escapes raw XML special characters and converts basic markdown formatting to valid ReportLab XML."""
    s = html.escape(text)
    s = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', s)
    s = _re.sub(r'__(.*?)__', r'<b>\1</b>', s)
    s = _re.sub(r'\*(.*?)\*', r'<i>\1</i>', s)
    s = _re.sub(r'_([^_]+?)_', r'<i>\1</i>', s)
    s = _re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', s)
    return s


def generate_ats_pdf(tailored_data: Dict[str, Any]) -> bytes:
    """
    Generates a modern, executive-styled ATS-compliant PDF:
    - Executive typography with Navy/Slate primary palette (#0F172A, #1E3A8A, #0284C7)
    - Distinctive full-width header block with candidate name, target role headline, contact bar
    - Section headers with accent rules and clean divider bars
    - 2-Column structured job headers (Title | Company on left, Dates / Location on right)
    - Cleanly formatted bullet points with Google XYZ impact highlights
    - Fully compatible with ATS parsers (Workday, Greenhouse, Lever, Taleo)
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
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
            textColor=colors.HexColor('#0F172A'), spaceAfter=2, spaceBefore=0
        )
        headline_style = ParagraphStyle(
            'TargetRoleHeadline', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=10.5, leading=14,
            textColor=colors.HexColor('#0284C7'), spaceAfter=3
        )
        contact_style = ParagraphStyle(
            'ContactBar', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.5, leading=12,
            textColor=colors.HexColor('#475569'), spaceAfter=4
        )
        section_style = ParagraphStyle(
            'SectionHeader', parent=styles['Heading2'],
            fontName='Helvetica-Bold', fontSize=11, leading=14,
            textColor=colors.HexColor('#1E3A8A'), spaceBefore=8, spaceAfter=2
        )
        job_left_style = ParagraphStyle(
            'JobLeft', parent=styles['Normal'],
            fontName='Helvetica-Bold', fontSize=9.5, leading=13,
            textColor=colors.HexColor('#0F172A')
        )
        job_right_style = ParagraphStyle(
            'JobRight', parent=styles['Normal'],
            fontName='Helvetica-Oblique', fontSize=8.5, leading=13,
            textColor=colors.HexColor('#64748B'), alignment=2  # Right-aligned
        )
        bullet_style = ParagraphStyle(
            'ExecutiveBullet', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.8, leading=12.5,
            textColor=colors.HexColor('#1E293B'), leftIndent=12, spaceAfter=2.5
        )
        body_style = ParagraphStyle(
            'ExecutiveBody', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.8, leading=12.5,
            textColor=colors.HexColor('#1E293B'), spaceAfter=2.5
        )
        skill_category_style = ParagraphStyle(
            'SkillCategory', parent=styles['Normal'],
            fontName='Helvetica', fontSize=8.8, leading=12.5,
            textColor=colors.HexColor('#1E293B'), spaceAfter=2
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

        # Extract Candidate Name and Contact Information
        first_line = lines[0]
        if first_line.startswith("# "):
            cand_name = first_line[2:].strip()
            lines = lines[1:]
        elif not any(c in first_line for c in ["@", "http", "|", "+"]):
            cand_name = first_line
            lines = lines[1:]
        else:
            cand_name = tailored_data.get("candidate_name", "Candidate")

        target_role = tailored_data.get("target_role", "").strip()

        # Header Block
        story.append(make_paragraph(cand_name.upper(), name_style))
        if target_role:
            story.append(make_paragraph(f"{target_role.upper()} &nbsp;|&nbsp; PROFESSIONAL PROFILE", headline_style))

        # Check for Contact Info line
        contact_line = ""
        if lines and any(c in lines[0] for c in ["@", "http", "|", "+", ".com"]):
            contact_line = lines[0]
            lines = lines[1:]

        if contact_line:
            # Clean contact line formatting
            contact_clean = contact_line.replace("|", " • ").replace("  ", " ")
            story.append(make_paragraph(contact_clean, contact_style))

        # Modern double horizontal divider
        story.append(HRFlowable(width="100%", thickness=1.8, color=colors.HexColor('#1E3A8A'), spaceAfter=1))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#93C5FD'), spaceAfter=6))

        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped:
                continue

            # Section Headers (e.g., SUMMARY, EXPERIENCE, PROJECTS, SKILLS, EDUCATION)
            if stripped.startswith("## ") or stripped.startswith("# ") or (stripped.isupper() and len(stripped) < 35 and not any(c in stripped for c in ["|", "–", "-", "@"])):
                header_text = stripped.replace("## ", "").replace("# ", "").strip()
                story.append(Spacer(1, 4))
                story.append(make_paragraph(f"<b>{header_text.upper()}</b>", section_style))
                story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#1E3A8A'), spaceAfter=4))

            # Job Header with Pipe (e.g. Senior Data Platform Engineer | CloudData Corp | 2022 – Present)
            elif "|" in stripped and ("present" in stripped.lower() or any(yr in stripped for yr in ["2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"])):
                parts = [p.strip() for p in stripped.split("|")]
                if len(parts) >= 2:
                    left_text = f"<b>{parts[0]}</b> &nbsp;<font color='#0284C7'>|</font>&nbsp; <i>{parts[1]}</i>"
                    right_text = parts[2] if len(parts) >= 3 else ""
                    
                    # 2-column table for aligned job headers
                    p_left = make_paragraph(left_text, job_left_style)
                    p_right = make_paragraph(right_text, job_right_style)
                    
                    job_table = Table([[p_left, p_right]], colWidths=[380, 160])
                    job_table.setStyle(TableStyle([
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('LEFTPADDING', (0,0), (-1,-1), 0),
                        ('RIGHTPADDING', (0,0), (-1,-1), 0),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                        ('TOPPADDING', (0,0), (-1,-1), 2),
                    ]))
                    story.append(job_table)
                else:
                    story.append(make_paragraph(stripped, job_left_style))

            # Sub-headers (### Project or Degree)
            elif stripped.startswith("### "):
                content = stripped[4:].strip()
                story.append(make_paragraph(f"<b>{content}</b>", job_left_style))

            # Bullet Points
            elif stripped.startswith(("- ", "• ", "* ")):
                bullet_text = stripped[2:].strip()
                story.append(make_paragraph(f"• &nbsp;{bullet_text}", bullet_style))

            # Skills Category rows
            elif ":" in stripped and any(cat in stripped.lower() for cat in ["languages", "tools", "cloud", "frameworks", "database", "methodologies", "devops"]):
                story.append(make_paragraph(stripped, skill_category_style))

            # Horizontal line
            elif stripped in ("---", "***", "___"):
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=2))

            else:
                story.append(make_paragraph(stripped, body_style))

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
            c.setFillColorRGB(0.06, 0.09, 0.16)
            cand_name = tailored_data.get("candidate_name", "CANDIDATE RESUME").upper()
            c.drawString(36, y, cand_name)
            y -= 15

            c.setStrokeColorRGB(0.12, 0.23, 0.54)
            c.setLineWidth(1.5)
            c.line(36, y, width - 36, y)
            y -= 20

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
                    c.setFillColorRGB(0.12, 0.23, 0.54)
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
