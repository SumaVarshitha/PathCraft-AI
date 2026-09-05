import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

os.makedirs("sample_resumes", exist_ok=True)

def create_pdf(filename, title, name, email, location, summary, skills, experience, projects, education):
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=0
    )
    
    sub_style = ParagraphStyle(
        'SubStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4B5563')
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=8,
        spaceAfter=4
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#1F2937')
    )
    
    bold_body = ParagraphStyle(
        'BoldBody',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    story = []
    
    # Header
    story.append(Paragraph(f"<b>{name}</b>", header_style))
    story.append(Paragraph(f"<b>{title}</b> | {email} | {location}", sub_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=2, spaceAfter=6))
    
    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", section_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 4))
    
    # Skills
    story.append(Paragraph("TECHNICAL SKILLS & COMPETENCIES", section_style))
    for category, skill_list in skills.items():
        story.append(Paragraph(f"<b>{category}:</b> {skill_list}", body_style))
    story.append(Spacer(1, 4))
    
    # Experience
    story.append(Paragraph("WORK EXPERIENCE", section_style))
    for exp in experience:
        story.append(Paragraph(f"<b>{exp['role']}</b> — <i>{exp['company']}</i> ({exp['period']})", bold_body))
        for bullet in exp['bullets']:
            story.append(Paragraph(f"• {bullet}", body_style))
        story.append(Spacer(1, 3))
        
    # Projects
    story.append(Paragraph("FEATURED PROJECTS", section_style))
    for proj in projects:
        story.append(Paragraph(f"<b>{proj['name']}</b> | <i>Tech: {proj['tech']}</i>", bold_body))
        story.append(Paragraph(f"• {proj['desc']}", body_style))
        story.append(Spacer(1, 3))
        
    # Education
    story.append(Paragraph("EDUCATION & CERTIFICATIONS", section_style))
    for edu in education:
        story.append(Paragraph(f"• {edu}", body_style))
        
    doc.build(story)
    print(f"Created: {filename}")

# 1. Senior Data Engineer Resume
create_pdf(
    "sample_resumes/1_Senior_Data_Engineer.pdf",
    "Senior Data Engineer",
    "Alex Chen",
    "alex.chen@example.com",
    "San Francisco, CA",
    "Senior Data Engineer with 5+ years of experience architecting petabyte-scale distributed data pipelines, lakehouse architectures, and real-time streaming infrastructure. Proficient in Python, SQL, Apache Spark, PySpark, Google Cloud BigQuery, and Airflow workflow orchestration.",
    {
        "Languages & Big Data": "Python, SQL, Apache Spark, PySpark, Scala, Apache Kafka, Apache Flink",
        "Cloud & Warehousing": "Google Cloud Platform (GCP), BigQuery, Snowflake, Amazon Redshift, AWS S3",
        "Orchestration & DevOps": "Apache Airflow, Docker, Kubernetes, Terraform, Git, CI/CD, dbt",
        "Data Modeling": "Star Schema, Dimensional Modeling, Lakehouse Architecture, Real-Time ETL"
    },
    [
        {
            "role": "Senior Data Platform Engineer",
            "company": "CloudData Corp",
            "period": "2022 - Present",
            "bullets": [
                "Architected and deployed streaming ETL pipelines using PySpark and Kafka, ingesting 250M+ events daily into Google Cloud BigQuery with 99.99% uptime.",
                "Orchestrated 50+ critical production DAGs using Apache Airflow, reducing data processing latency by 45%.",
                "Built dimensional data warehouse marts using dbt, SQL, and BigQuery, serving executive business intelligence dashboards."
            ]
        },
        {
            "role": "Data Engineer",
            "company": "Nexus Systems",
            "period": "2020 - 2022",
            "bullets": [
                "Built automated data ingestion pipelines using Python, SQL, and PostgreSQL for financial analytics.",
                "Containerized batch processing microservices using Docker and deployed on Kubernetes clusters."
            ]
        }
    ],
    [
        {
            "name": "Real-Time Lakehouse Streaming Ingestion Engine",
            "tech": "Python, PySpark, Apache Spark, BigQuery, Docker, Git",
            "desc": "Built an automated real-time stream processing engine capturing clickstream telemetry into BigQuery with sub-minute query latency."
        },
        {
            "name": "Enterprise Data Pipeline & Airflow Orchestrator",
            "tech": "Python, Apache Airflow, SQL, PostgreSQL, Docker, GCP",
            "desc": "Designed reusable Airflow DAG architectures and ETL data validation frameworks reducing pipeline failure rates by 60%."
        }
    ],
    [
        "B.S. in Computer Science — University of California, Berkeley",
        "Google Cloud Certified Professional Data Engineer (GCP PDE)"
    ]
)

# 2. AI / ML Engineer Resume
create_pdf(
    "sample_resumes/2_AIML_Engineer.pdf",
    "AI / Machine Learning Engineer",
    "Dr. Sarah Lin",
    "sarah.lin@example.com",
    "Seattle, WA",
    "Machine Learning and AI Systems Engineer with 4+ years of experience designing deep learning models, RAG agentic pipelines, and MLOps deployment architectures. Specialized in PyTorch, TensorFlow, LLMs, LangChain, Vector Databases, and production model serving.",
    {
        "ML & Deep Learning": "Python, PyTorch, TensorFlow, Scikit-Learn, Keras, HuggingFace, Transformers",
        "Generative AI & LLMs": "LLMs, LangChain, LlamaIndex, RAG Pipelines, Vector Databases (Pinecone, ChromaDB), Prompt Engineering",
        "MLOps & Cloud": "Docker, Kubernetes, MLflow, Triton Inference Server, AWS, GCP, Git, CI/CD",
        "Data & Architecture": "SQL, Pandas, NumPy, FastAPI, Distributed Training, Model Quantization"
    },
    [
        {
            "role": "Senior Machine Learning Engineer",
            "company": "Synthetix AI Lab",
            "period": "2022 - Present",
            "bullets": [
                "Fine-tuned open-source LLMs using PyTorch, HuggingFace, and LoRA/QLoRA for enterprise question-answering systems.",
                "Architected high-throughput RAG pipelines using LangChain, Vector Databases, and FastAPI, serving 10,000+ daily user requests.",
                "Implemented automated model evaluation, tracking, and deployment using MLflow and Docker containers on Kubernetes."
            ]
        }
    ],
    [
        {
            "name": "Multi-Agent RAG Knowledge Copilot",
            "tech": "Python, PyTorch, LangChain, Vector Databases, FastAPI, Docker",
            "desc": "Engineered an autonomous multi-agent document analysis system utilizing semantic embeddings and hybrid search retrieval."
        },
        {
            "name": "Distributed Computer Vision & Inference Pipeline",
            "tech": "Python, TensorFlow, PyTorch, Triton, Docker, Git",
            "desc": "Deployed optimized deep learning vision models with ONNX Runtime, achieving 4x throughput improvement on GPU nodes."
        }
    ],
    [
        "Ph.D. in Artificial Intelligence & Computer Science — University of Washington",
        "AWS Certified Machine Learning - Specialty"
    ]
)

# 3. Fullstack Web Developer Resume
create_pdf(
    "sample_resumes/3_Fullstack_Developer.pdf",
    "Fullstack Web Developer",
    "David Kumar",
    "david.kumar@example.com",
    "Austin, TX",
    "Fullstack Software Engineer with 3+ years of experience building modern web applications, scalable REST APIs, and interactive cloud frontends. Strong foundation in JavaScript, TypeScript, React, Node.js, Python, PostgreSQL, and Docker containerization.",
    {
        "Frontend": "JavaScript, TypeScript, React, Next.js, HTML5, CSS3, Tailwind CSS, Redux, State Management",
        "Backend & APIs": "Node.js, Express.js, Python, FastAPI, REST APIs, GraphQL, Microservices",
        "Databases & Cloud": "PostgreSQL, SQL, MongoDB, Redis, Docker, Git, AWS, CI/CD, Jest"
    },
    [
        {
            "role": "Fullstack Software Engineer",
            "company": "Veloce Technologies",
            "period": "2023 - Present",
            "bullets": [
                "Developed responsive frontend web apps using React, TypeScript, and Tailwind CSS with 99.8% test coverage.",
                "Engineered scalable REST APIs and microservices in Node.js and Python (FastAPI), connecting to PostgreSQL databases.",
                "Containerized services with Docker and set up automated GitHub Actions CI/CD deployment pipelines."
            ]
        }
    ],
    [
        {
            "name": "Collaborative SaaS Project Workspace",
            "tech": "TypeScript, React, Node.js, PostgreSQL, Docker, Git",
            "desc": "Created real-time kanban and document collaboration platform supporting 5,000+ active users."
        }
    ],
    [
        "B.S. in Software Engineering — University of Texas at Austin"
    ]
)

# 4. Weak UI/UX Designer Resume (Mismatched for Data Engineer / AI Role)
create_pdf(
    "sample_resumes/4_UIUX_Designer_Weak_Match.pdf",
    "UI / UX Visual Designer",
    "Jordan Miller",
    "jordan.miller@example.com",
    "New York, NY",
    "Creative Visual and UI/UX Designer with 2 years of experience crafting interactive wireframes, brand identity systems, and user interfaces. Passionate about typography, design systems, and responsive website aesthetics.",
    {
        "Design Tools": "Figma, Adobe XD, Adobe Photoshop, Adobe Illustrator, InVision, Sketch",
        "Web Visuals": "HTML5, CSS3, Responsive Design, Typography, Color Palettes, Brand Guidelines",
        "Design Methods": "User Research, Wireframing, Rapid Prototyping, Usability Testing, Persona Mapping"
    },
    [
        {
            "role": "Junior Product Designer",
            "company": "CreativeStudio Agency",
            "period": "2023 - Present",
            "bullets": [
                "Designed interactive high-fidelity mobile prototypes and component libraries in Figma.",
                "Conducted qualitative user interviews and usability testing sessions for e-commerce client redesigns.",
                "Created responsive HTML/CSS landing page mockups for digital marketing campaigns."
            ]
        }
    ],
    [
        {
            "name": "Food Delivery Mobile App UI Redesign",
            "tech": "Figma, Adobe Photoshop, User Research",
            "desc": "Crafted 40+ UI screens and interactive clickable prototypes in Figma."
        }
    ],
    [
        "B.A. in Graphic Design & Visual Arts — Pratt Institute"
    ]
)
