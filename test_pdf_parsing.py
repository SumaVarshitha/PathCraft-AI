import os
from core.agents.resume_parser_agent import ResumeParserADKAgent, extract_text_from_pdf_bytes

def test_pdf_parsing():
    print("=" * 60)
    print("Testing PDF Parsing directly on sample PDF files...")
    print("=" * 60)
    
    parser = ResumeParserADKAgent()
    
    for pdf_path in [
        "sample_resumes/1_Senior_Data_Engineer.pdf",
        "sample_resumes/2_AIML_Engineer.pdf",
        "sample_resumes/3_Fullstack_Developer.pdf",
        "sample_resumes/4_UIUX_Designer_Weak_Match.pdf"
    ]:
        print(f"\n--- Testing: {pdf_path} ---")
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        text = extract_text_from_pdf_bytes(pdf_bytes)
        print(f"Extracted Text Length: {len(text)} characters")
        print(f"Text Preview: {text[:120]}...\n")
        
        parsed = parser.parse(pdf_bytes=pdf_bytes)
        print(f"Candidate Name: {parsed.get('candidate_name')}")
        print(f"Job Title: {parsed.get('job_title')}")
        print(f"Extracted Skills ({len(parsed.get('skills', []))}): {parsed.get('skills')[:8]}")
        print(f"Extracted Projects ({len(parsed.get('projects', []))}): {parsed.get('projects')}")
        print(f"Tools & Tech: {parsed.get('tools_and_technologies')[:8]}")

if __name__ == "__main__":
    test_pdf_parsing()
