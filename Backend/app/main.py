from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import pdfplumber
import io
import re
import os
import json
import traceback
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="ResumeIQ AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE"))

SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "kotlin", "swift", "r", "scala", "php", "ruby", "dart",
    "react", "angular", "vue", "html", "css", "tailwind", "bootstrap",
    "next.js", "nuxt", "svelte", "redux", "jquery",
    "fastapi", "django", "flask", "node.js", "express", "spring boot",
    "rest api", "graphql", "grpc", "microservices",
    "machine learning", "deep learning", "nlp", "bert", "gpt", "llm",
    "langchain", "huggingface", "tensorflow", "pytorch", "keras",
    "scikit-learn", "xgboost", "lightgbm", "computer vision", "opencv",
    "rag", "vector database", "faiss", "embeddings", "generative ai",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "power bi",
    "tableau", "excel", "sql", "mysql", "postgresql", "mongodb",
    "data analysis", "data visualization", "statistics",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "github",
    "ci/cd", "terraform", "linux", "bash",
    "agile", "scrum", "jira", "figma", "canva",
]

EXPECTED_SECTIONS = [
    "education", "experience", "projects", "skills",
    "certifications", "achievements", "summary", "publications"
]

# ── Helpers ──────────────────────────────────────────────────────
def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def extract_skills(text):
    return list(set(s for s in SKILL_KEYWORDS if s.lower() in text.lower()))

def compute_similarity(t1, t2):
    v = TfidfVectorizer(stop_words="english")
    m = v.fit_transform([t1, t2])
    return round(cosine_similarity(m[0:1], m[1:2])[0][0] * 100, 2)

def analyze_sections(resume_text):
    tl = resume_text.lower()
    found = [s.title() for s in EXPECTED_SECTIONS if s in tl]
    missing = [s.title() for s in EXPECTED_SECTIONS if s not in tl]
    score = round(len(found) / len(EXPECTED_SECTIONS) * 100)
    suggestions = []
    if "Summary" in missing: suggestions.append("Add a professional summary at the top.")
    if "Certifications" in missing: suggestions.append("Add certifications to strengthen your profile.")
    if "Achievements" in missing: suggestions.append("Add achievements with metrics.")
    return {
        "Found Sections": found,
        "Missing Sections": missing,
        "Section Score": score,
        "Section Suggestions": suggestions
    }

def get_ai_feedback(resume_text, job_description):
    try:
        prompt = f"""You are an ATS resume expert. Give EXACTLY 5 specific actionable bullet points to improve this resume for this job.
Resume: {resume_text[:1500]}
Job: {job_description[:1000]}
Return ONLY a Python list: ["point1","point2","point3","point4","point5"]"""
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=600
        )
        items = re.findall(r'"([^"]+)"', r.choices[0].message.content)
        return items[:5] if items else [
            "Tailor skills to JD.", "Quantify achievements.",
            "Add strong summary.", "Use action verbs.",
            "Highlight relevant experience."
        ]
    except:
        return [
            "Tailor skills to JD.", "Quantify achievements.",
            "Add strong summary.", "Use action verbs.",
            "Highlight relevant experience."
        ]

# ✅ Cleans ANY text so FPDF (latin-1 only) never crashes
def clean_for_pdf(text):
    if text is None:
        return ""
    text = str(text)
    replacements = {
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u2022": "-",
        "\u00a0": " ", "\u2192": "->", "\u2713": "v", "\u2714": "v",
        "\u2717": "x", "\u2718": "x",
    }
    for uni, ascii_char in replacements.items():
        text = text.replace(uni, ascii_char)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    text = re.sub(r"\s+", " ", text).strip()
    return text

def generate_pdf_report(result, candidate_name="Candidate"):
    candidate_name = clean_for_pdf(candidate_name) or "Candidate"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_fill_color(37, 99, 235)
    pdf.rect(0, 0, 210, 36, 'F')
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(8)
    pdf.cell(0, 10, "ResumeIQ AI - ATS Analysis Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Prepared for: {candidate_name}", ln=True, align="C")
    pdf.ln(12)

    def section_header(title):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 9, clean_for_pdf(title), ln=True)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    def safe_multicell(text, w=0, h=8):
        text = clean_for_pdf(text)
        if not text:
            text = " "
        pdf.set_x(10)
        pdf.multi_cell(w, h, text)

    section_header("Score Summary")
    for label, val in [
        ("ATS Score",      f"{result['ATS Score']}%"),
        ("Skill Match",    f"{result['Skill Match']}%"),
        ("Resume Length",  result["Resume Length"]),
        ("Missing Skills", str(len(result.get("Missing Skills", [])))),
        ("Status",         clean_for_pdf(result["Message"])),
    ]:
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(70, 8, f"  {label}:", ln=False)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 8, clean_for_pdf(val), ln=True)
    pdf.ln(4)

    section_header("Matched Skills")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(22, 163, 74)
    m = result.get("Matched Skills", [])
    safe_multicell("  " + ", ".join(m) if m else "  None found.")
    pdf.ln(3)

    section_header("Missing Skills")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(220, 38, 38)
    ms = result.get("Missing Skills", [])
    safe_multicell("  " + ", ".join(ms) if ms else "  None - great match!")
    pdf.ln(3)

    section_header("Suggestions")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    for s in result.get("Suggestions", []):
        safe_multicell(f"  - {s}")
    pdf.ln(3)

    section_header("AI Resume Feedback (LLaMA 3.3 70B)")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    for f in result.get("AI Feedback", []):
        safe_multicell(f"  - {f}")
    pdf.ln(3)

    ra = result.get("Resume Analysis", {})
    section_header(f"Section Analysis - Score: {ra.get('Section Score', 0)}%")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(22, 163, 74)
    pdf.cell(0, 8, "Found Sections:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    safe_multicell("  " + ", ".join(ra.get("Found Sections", [])))
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 8, "Missing Sections:", ln=True)
    pdf.set_font("Helvetica", "", 11)
    missing_sec = ", ".join(ra.get("Missing Sections", []))
    safe_multicell("  " + missing_sec if missing_sec else "  None!")

    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Generated by ResumeIQ AI | Built by Shyama Mishra | Galgotias 2027", align="C")

    return bytes(pdf.output())


# ✅ NEW FEATURE 1 — Cover letter PDF generator
def generate_cover_letter_pdf(cover_letter_text, candidate_name="Candidate"):
    candidate_name = clean_for_pdf(candidate_name) or "Candidate"
    cover_letter_text = clean_for_pdf(cover_letter_text)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    pdf.set_fill_color(124, 58, 237)
    pdf.rect(0, 0, 210, 30, 'F')
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.set_y(8)
    pdf.cell(0, 10, "Cover Letter", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, candidate_name, ln=True, align="C")
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.set_x(15)
    pdf.multi_cell(180, 8, cover_letter_text or "No content generated.")

    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "Generated by ResumeIQ AI | Shyama Mishra", align="C")

    return bytes(pdf.output())


# ════════════════════════════════════════════════════════════
# ENDPOINT 1 — Calculate ATS Score
# ════════════════════════════════════════════════════════════
@app.post("/calculate-ats/")
async def calculate_ats(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)

    if not resume_text.strip():
        return {"error": "Could not extract text from PDF."}

    ats_score    = compute_similarity(resume_text, job_description)
    resume_skills = extract_skills(resume_text)
    jd_skills    = extract_skills(job_description)
    matched      = [s for s in jd_skills if s in resume_skills]
    missing      = [s for s in jd_skills if s not in resume_skills]
    skill_match  = round((len(matched) / len(jd_skills) * 100) if jd_skills else 0, 2)
    word_count   = len(resume_text.split())

    if word_count < 300:
        resume_length = f"Too Short ({word_count} words)"
    elif word_count > 1000:
        resume_length = f"Too Long ({word_count} words)"
    else:
        resume_length = f"Ideal ({word_count} words)"

    suggestions = []
    if ats_score < 50:  suggestions.append("Low ATS match. Add more JD keywords to your resume.")
    if skill_match < 60: suggestions.append("Add more skills from the job description.")
    if missing:         suggestions.append(f"Add these missing skills: {', '.join(missing[:5])}")
    if word_count < 300: suggestions.append("Resume too short. Expand experience and projects.")
    if not suggestions: suggestions.append("Great match! Tailor your professional summary further.")

    message = (
        "🎉 Excellent Match!" if ats_score >= 75
        else "⚠️ Good Match. Some improvements needed." if ats_score >= 50
        else "❌ Low Match. Significant improvements needed."
    )

    return {
        "ATS Score":       ats_score,
        "Skill Match":     skill_match,
        "Resume Length":   resume_length,
        "Matched Skills":  [s.title() for s in matched],
        "Missing Skills":  [s.title() for s in missing],
        "Suggestions":     suggestions,
        "AI Feedback":     get_ai_feedback(resume_text, job_description),
        "Resume Analysis": analyze_sections(resume_text),
        "Message":         message,
    }


# ════════════════════════════════════════════════════════════
# ENDPOINT 2 — Download PDF
# ════════════════════════════════════════════════════════════
@app.post("/download-pdf/")
async def download_pdf(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_name: str = Form(default="Candidate"),
):
    file_bytes    = await resume.read()
    resume_text   = extract_text_from_pdf(file_bytes)
    ats_score     = compute_similarity(resume_text, job_description)
    resume_skills = extract_skills(resume_text)
    jd_skills     = extract_skills(job_description)
    matched       = [s for s in jd_skills if s in resume_skills]
    missing       = [s for s in jd_skills if s not in resume_skills]
    skill_match   = round((len(matched) / len(jd_skills) * 100) if jd_skills else 0, 2)
    word_count    = len(resume_text.split())
    resume_length = (
        f"Ideal ({word_count} words)" if 300 <= word_count <= 1000
        else f"{word_count} words"
    )
    message = (
        "Excellent Match!" if ats_score >= 75
        else "Good Match." if ats_score >= 50
        else "Low Match."
    )

    result = {
        "ATS Score":       ats_score,
        "Skill Match":     skill_match,
        "Resume Length":   resume_length,
        "Matched Skills":  [s.title() for s in matched],
        "Missing Skills":  [s.title() for s in missing],
        "Suggestions":     [f"Add: {', '.join(missing[:5])}"] if missing else ["Great match!"],
        "AI Feedback":     get_ai_feedback(resume_text, job_description),
        "Resume Analysis": analyze_sections(resume_text),
        "Message":         message,
    }

    try:
        pdf_bytes = generate_pdf_report(result, candidate_name)
    except Exception as e:
        print("PDF GENERATION ERROR:", str(e))
        traceback.print_exc()
        # ✅ Better fallback — includes ALL data, plain text only
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, clean_for_pdf("ResumeIQ AI Report"), ln=True)
        pdf.set_font("Helvetica", "", 12)
        pdf.ln(4)
        pdf.cell(0, 8, clean_for_pdf(f"ATS Score: {result['ATS Score']}%"), ln=True)
        pdf.cell(0, 8, clean_for_pdf(f"Skill Match: {result['Skill Match']}%"), ln=True)
        pdf.cell(0, 8, clean_for_pdf(f"Resume Length: {result['Resume Length']}"), ln=True)
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Matched Skills:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, clean_for_pdf(", ".join(result.get("Matched Skills", []))) or "None")
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Missing Skills:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, clean_for_pdf(", ".join(result.get("Missing Skills", []))) or "None")
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "AI Feedback:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for fb in result.get("AI Feedback", []):
            pdf.multi_cell(0, 7, clean_for_pdf(f"- {fb}"))
        pdf_bytes = bytes(pdf.output())

    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', candidate_name) or "Report"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition":         f"attachment; filename=ResumeIQ_{safe_name}.pdf",
            "Content-Length":              str(len(pdf_bytes)),
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Content-Disposition, Content-Length",
        }
    )


# ════════════════════════════════════════════════════════════
# ENDPOINT 3 — Cover Letter Generator (text)
# ════════════════════════════════════════════════════════════
@app.post("/generate-cover-letter/")
async def generate_cover_letter(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    candidate_name: str = Form(default="Candidate"),
):
    file_bytes  = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)
    try:
        prompt = f"""Write a professional cover letter for {candidate_name}.
Resume: {resume_text[:1200]}
Job Description: {job_description[:800]}
Write exactly 3 paragraphs. Professional, confident, warm tone. ~250 words.
No date or address headers — just the letter body."""
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=700
        )
        return {"cover_letter": r.choices[0].message.content.strip()}
    except Exception as e:
        return {
            "cover_letter": "Error generating cover letter. Check Groq API key.",
            "error": str(e)
        }


# ════════════════════════════════════════════════════════════
# ✅ NEW FEATURE 1 — Download Cover Letter as PDF
# ════════════════════════════════════════════════════════════
@app.post("/download-cover-letter-pdf/")
async def download_cover_letter_pdf(
    cover_letter: str = Form(...),
    candidate_name: str = Form(default="Candidate"),
):
    try:
        pdf_bytes = generate_cover_letter_pdf(cover_letter, candidate_name)
    except Exception as e:
        print("COVER LETTER PDF ERROR:", str(e))
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 8, clean_for_pdf(cover_letter))
        pdf_bytes = bytes(pdf.output())

    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', candidate_name) or "CoverLetter"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=CoverLetter_{safe_name}.pdf",
            "Content-Length": str(len(pdf_bytes)),
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Expose-Headers": "Content-Disposition, Content-Length",
        }
    )


# ════════════════════════════════════════════════════════════
# ✅ NEW FEATURE 2 — Interview Question Generator
# ════════════════════════════════════════════════════════════
@app.post("/interview-questions/")
async def interview_questions(job_description: str = Form(...)):
    try:
        prompt = f"""Generate exactly 10 interview questions for this job description.
Job Description: {job_description[:1000]}

Format: 6 technical questions + 4 behavioral/HR questions.
Return ONLY a JSON array of objects like this, nothing else:
[{{"type":"Technical","question":"..."}}, {{"type":"Behavioral","question":"..."}}]
"""
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=900
        )
        raw = r.choices[0].message.content.strip()
        raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        try:
            questions = json.loads(raw)
        except Exception:
            # fallback parsing if model didn't return clean JSON
            found = re.findall(r'"question"\s*:\s*"([^"]+)"', raw)
            questions = [{"type": "Technical" if i < 6 else "Behavioral", "question": q} for i, q in enumerate(found)]
        return {"questions": questions[:10]}
    except Exception as e:
        return {"questions": [], "error": str(e)}


# ════════════════════════════════════════════════════════════
# ✅ NEW FEATURE 3 — Resume Bullet Point Rewriter
# ════════════════════════════════════════════════════════════
@app.post("/rewrite-bullets/")
async def rewrite_bullets(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    file_bytes = await resume.read()
    resume_text = extract_text_from_pdf(file_bytes)
    try:
        prompt = f"""You are an expert resume writer. Based on this resume and job description,
give EXACTLY 3 bullet point rewrite suggestions to better match the job.

Resume: {resume_text[:1500]}
Job Description: {job_description[:800]}

For each suggestion, return JSON objects with "before" (a weak resume line) and
"after" (an improved, quantified, JD-aligned version).
Return ONLY a JSON array, nothing else:
[{{"before":"...", "after":"..."}}, {{"before":"...", "after":"..."}}, {{"before":"...", "after":"..."}}]
"""
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=800
        )
        raw = r.choices[0].message.content.strip()
        raw = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
        try:
            rewrites = json.loads(raw)
        except Exception:
            befores = re.findall(r'"before"\s*:\s*"([^"]+)"', raw)
            afters = re.findall(r'"after"\s*:\s*"([^"]+)"', raw)
            rewrites = [{"before": b, "after": a} for b, a in zip(befores, afters)]
        return {"rewrites": rewrites[:3]}
    except Exception as e:
        return {"rewrites": [], "error": str(e)}


# ── Run: uvicorn app.main:app --reload ──
