# ============================================================
# AI RESUME SCREENER — VS Code Version
# ============================================================

import io
import re
import os
import sys
import pandas as pd
import fitz
import docx2txt
import spacy
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer, util
from fpdf import FPDF

# Configure UTF-8 encoding for stdout/stderr to prevent UnicodeEncodeError in Windows terminal
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ── CONFIG: Set your paths here ─────────────────────────────
JD_PATH       = r"C:\Users\Karan M\Projects\AI_resumeScreener\jd.pdf"
RESUME_FOLDER = r"C:\Users\Karan M\Projects\AI_resumeScreener\Resumes"

# ── Load Models ──────────────────────────────────────────────
print("⏳ Loading models...")
nlp   = spacy.load("en_core_web_sm")
sbert = SentenceTransformer("all-MiniLM-L6-v2")
print("✅ Models loaded.")

# ── Skills Taxonomy ──────────────────────────────────────────
SKILLS_DB = [
    "Python", "Java", "C++", "C#", "R", "Scala", "Go", "Rust", "JavaScript", "TypeScript",
    "SQL", "NoSQL", "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "LLMs", "Generative AI", "Reinforcement Learning", "Statistical Modeling",
    "scikit-learn", "TensorFlow", "PyTorch", "Keras", "XGBoost", "LightGBM",
    "Hugging Face", "OpenCV", "NLTK", "spaCy",
    "Spark", "Hadoop", "Kafka", "Airflow", "dbt", "ETL", "Data Pipelines",
    "Pandas", "NumPy", "Matplotlib", "Seaborn",
    "Tableau", "Power BI", "Excel", "Looker", "Google Data Studio", "Metabase",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "CI/CD", "Git", "GitHub",
    "FastAPI", "Flask", "Django", "REST API",
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "BigQuery", "Snowflake",
    "Communication", "Problem Solving", "Team Leadership", "Agile", "Scrum",
    "Data Analysis", "Business Intelligence", "A/B Testing", "Statistics",
    "Forecasting", "Data Visualization", "Data Wrangling",
]

# ── Skill Extractor ──────────────────────────────────────────
matcher  = PhraseMatcher(nlp.vocab, attr="LOWER")
patterns = [nlp.make_doc(s.lower()) for s in SKILLS_DB]
matcher.add("SKILLS", patterns)

def extract_skills(text: str) -> list:
    doc     = nlp(text)
    matches = matcher(doc)
    return list(set(doc[start:end].text for _, start, end in matches))

# ── Text Extractor ───────────────────────────────────────────
def extract_text(file_obj, filename: str) -> str:
    filename = filename.lower()
    try:
        if filename.endswith(".pdf"):
            file_bytes = file_obj.read()
            if len(file_bytes) == 0:
                print(f"⚠️ Warning: PDF file {filename} is empty.")
                return ""
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)

            pdf_doc = fitz.open(stream=file_obj.read(), filetype="pdf")
            if pdf_doc.is_encrypted:
                print(f"⚠️ Warning: PDF file {filename} is encrypted/password-protected.")
                return ""

            text = ""
            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                text += page.get_text() + "\n"
            return text

        elif filename.endswith(".docx"):
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            return docx2txt.process(file_obj)

        elif filename.endswith(".txt"):
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
            content = file_obj.read()
            if isinstance(content, bytes):
                return content.decode("utf-8", errors="ignore")
            return str(content)

    except Exception as e:
        print(f"❌ Error extracting text from {filename}: {str(e)}")
        return ""
    return ""

# ── Experience & Education ───────────────────────────────────
def extract_experience_years(text: str) -> int:
    """
    Extract years of experience from resume text.
    Strategy:
    1. Look for explicit statements like "X years of experience"
    2. Parse date ranges from work history (e.g., "June 2021 - Present", "2018-2021")
    3. Return the maximum of both approaches
    """
    from datetime import datetime

    # Strategy 1: Explicit years mentioned
    explicit_years = 0
    patterns = [
        r'(\d+)\+?\s+years?\s+of\s+experience',
        r'(\d+)\+?\s+years?\s+in\b',
        r'experience\s+of\s+(\d+)\+?\s+years?',
        r'(\d+)\+?\s+years?\s+working',
        r'over\s+(\d+)\s+years?',
    ]
    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            explicit_years = int(match.group(1))
            break

    # Strategy 2: Parse date ranges from work history
    date_range_patterns = [
        r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})\s*[-–—to]+\s*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})',
        r'(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{4})\s*[-–—to]+\s*Present',
        r'(\d{1,2})/(\d{4})\s*[-–—to]+\s*(\d{1,2})/(\d{4})',
        r'(\d{4})\s*[-–—to]+\s*(\d{4})',
        r'(\d{4})\s*[-–—to]+\s*Present',
    ]

    month_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
        'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'september': 9, 'oct': 10, 'october': 10,
        'nov': 11, 'november': 11, 'dec': 12, 'december': 12,
    }

    total_months = 0
    current_year = datetime.now().year
    current_month = datetime.now().month

    for pattern in date_range_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                groups = match.groups()
                if len(groups) == 4 and groups[0].isalpha():
                    start_month = month_map.get(groups[0].lower(), 1)
                    start_year = int(groups[1])
                    end_month = month_map.get(groups[2].lower(), 12)
                    end_year = int(groups[3])
                    duration = (end_year - start_year) * 12 + (end_month - start_month)
                    total_months += max(duration, 0)
                elif len(groups) == 2 and groups[0].isalpha():
                    start_month = month_map.get(groups[0].lower(), 1)
                    start_year = int(groups[1])
                    duration = (current_year - start_year) * 12 + (current_month - start_month)
                    total_months += max(duration, 0)
                elif len(groups) == 4 and groups[0].isdigit():
                    start_month = int(groups[0])
                    start_year = int(groups[1])
                    end_month = int(groups[2])
                    end_year = int(groups[3])
                    duration = (end_year - start_year) * 12 + (end_month - start_month)
                    total_months += max(duration, 0)
                elif len(groups) == 2 and groups[0].isdigit() and groups[1].isdigit():
                    start_year = int(groups[0])
                    end_year = int(groups[1])
                    duration = (end_year - start_year) * 12
                    total_months += max(duration, 0)
                elif len(groups) == 1 and groups[0].isdigit():
                    start_year = int(groups[0])
                    duration = (current_year - start_year) * 12
                    total_months += max(duration, 0)
            except (ValueError, IndexError):
                continue

    calculated_years = round(total_months / 12)
    return max(explicit_years, calculated_years)

def extract_education(text: str) -> str:
    hierarchy = [
        ("PhD",        ["phd", "ph.d", "doctorate", "doctor of philosophy"]),
        ("Master's",   ["master", "m.tech", "m.s.", "msc", "m.e.", "mba", "m.b.a"]),
        ("Bachelor's", ["bachelor", "b.tech", "b.e.", "b.s.", "bsc", "b.sc", "undergraduate"]),
        ("Diploma",    ["diploma", "associate"]),
    ]
    text_lower = text.lower()
    for level, keywords in hierarchy:
        if any(k in text_lower for k in keywords):
            return level
    return "Not detected"

def extract_contact_info(text: str) -> dict:
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    phone_match = re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text)
    return {
        "email": email_match.group(0) if email_match else "—",
        "phone": phone_match.group(0).strip() if phone_match else "—",
    }

# ── SBERT Similarity ─────────────────────────────────────────
def get_similarity(resume_text: str, jd_text: str) -> float:
    emb_r = sbert.encode(resume_text[:3000], convert_to_tensor=True)
    emb_j = sbert.encode(jd_text[:3000],    convert_to_tensor=True)
    return float(util.cos_sim(emb_r, emb_j))

# ── Scoring Engine ───────────────────────────────────────────
def calculate_fit_score(similarity, matched_skills, jd_skills, exp_years, education):
    jd_skill_count = max(len(jd_skills), 1)
    jd_matched     = [s for s in matched_skills if s.lower() in [j.lower() for j in jd_skills]]
    skill_score    = min(len(jd_matched) / jd_skill_count, 1.0)
    exp_score      = min(exp_years / 10, 1.0)
    edu_map        = {"PhD": 1.0, "Master's": 0.85, "Bachelor's": 0.7, "Diploma": 0.5, "Not detected": 0.3}
    edu_score      = edu_map.get(education, 0.3)

    final = (similarity * 0.50 + skill_score * 0.30 + exp_score * 0.12 + edu_score * 0.08) * 100

    breakdown = {
        "semantic_match":    round(similarity   * 100, 1),
        "skill_score":       round(skill_score  * 100, 1),
        "exp_score":         round(exp_score    * 100, 1),
        "edu_score":         round(edu_score    * 100, 1),
        "jd_skills_matched": jd_matched,
        "all_skills_found":  matched_skills,
        "skills_missing":    [s for s in jd_skills if s.lower() not in [m.lower() for m in matched_skills]],
        "experience_years":  exp_years,
        "education":         education,
    }
    return round(final, 2), breakdown

def classify_tier(score: float) -> str:
    if score >= 75: return "Strong Match"
    if score >= 55: return "Potential Fit"
    if score >= 35: return "Weak Fit"
    return "Not Suitable"

# ── Report Generators ────────────────────────────────────────
def generate_csv_report(results, filename="screening_report.csv"):
    rows = []
    for r in results:
        rows.append({
            "Rank":               r["rank"],
            "Resume":             r["filename"],
            "Fit Score (%)":      r["score"],
            "Tier":               r["tier"],
            "Semantic Match (%)": r["breakdown"]["semantic_match"],
            "Skill Score (%)":    r["breakdown"]["skill_score"],
            "Experience (yrs)":   r["breakdown"]["experience_years"],
            "Education":          r["breakdown"]["education"],
            "JD Skills Matched":  ", ".join(r["breakdown"]["jd_skills_matched"]),
            "Skills Missing":     ", ".join(r["breakdown"]["skills_missing"]),
            "Email":              r["contact"]["email"],
            "Phone":              r["contact"]["phone"],
        })
    df = pd.DataFrame(rows)
    df.to_csv(filename, index=False)
    print(f"✅ CSV saved: {filename}")
    return df

def generate_pdf_report(results, jd_title="Job Description", filename="screening_report.pdf"):
    report = FPDF()
    report.set_auto_page_break(auto=True, margin=15)
    report.add_page()
    safe = lambda s: s.encode("latin-1", "replace").decode("latin-1")

    report.set_font("Arial", "B", 18)
    report.cell(0, 12, "AI Resume Screening Report", ln=True, align="C")
    report.set_font("Arial", "I", 11)
    report.cell(0, 8, f"Position: {jd_title}", ln=True, align="C")
    report.set_font("Arial", "", 10)
    report.cell(0, 6, f"Total Candidates Evaluated: {len(results)}", ln=True, align="C")
    report.ln(6)

    for r in results:
        b = r["breakdown"]
        report.set_font("Arial", "B", 13)
        report.set_fill_color(230, 240, 255)
        report.cell(0, 9, safe(f"#{r['rank']}  {r['filename']}  -  {r['score']}%  {r['tier']}"), ln=True, fill=True)
        report.set_font("Arial", "", 10)
        report.cell(0, 6, safe(f"  Semantic: {b['semantic_match']}%  |  Skills: {b['skill_score']}%  |  Exp: {b['experience_years']} yrs  |  Edu: {b['education']}"), ln=True)
        report.cell(0, 6, safe(f"  Email: {r['contact']['email']}   Phone: {r['contact']['phone']}"), ln=True)
        report.set_font("Arial", "I", 9)
        report.cell(0, 5, safe(f"  Matched : {', '.join(b['jd_skills_matched']) or 'None'}"), ln=True)
        report.cell(0, 5, safe(f"  Missing : {', '.join(b['skills_missing']) or 'None'}"), ln=True)
        report.ln(4)

    report.output(filename)
    print(f"✅ PDF saved: {filename}")

def call_gemini_api(api_key: str, prompt: str, json_mode: bool = False) -> str:
    import requests
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    if json_mode:
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
            except (KeyError, IndexError):
                return ""
        else:
            return ""
    except Exception:
        return ""

def extract_skills_from_jd_with_ai(api_key: str, jd_text: str) -> list:
    """
    Uses Gemini API to dynamically extract required skills from Job Description.
    Returns a list of skill strings. Falls back to empty list on failure.
    """
    import json
    prompt = f"""
You are an expert technical recruiter and skill taxonomist. Extract ALL required technical skills, tools, frameworks, programming languages, and soft skills from the following Job Description.

Return ONLY a JSON array of skill strings (e.g., ["Python", "React", "Docker", "Communication"]).
Do not include explanations, just the array.

Job Description:
{jd_text[:4000]}
"""
    result_text = call_gemini_api(api_key, prompt, json_mode=True)
    if not result_text.strip():
        return []
    try:
        cleaned_text = result_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        parsed = json.loads(cleaned_text.strip())
        # Ensure it's a list
        if isinstance(parsed, list):
            return [str(s).strip() for s in parsed if s]
        return []
    except Exception:
        return []

def get_candidate_llm_analysis(api_key: str, resume_text: str, jd_text: str) -> dict:
    import json
    prompt = f"""
You are an expert technical recruiter. Analyze the following candidate resume text against the job description.
Identify the candidate's executive summary of fit, top 3 strengths relative to the job, top 2 missing gaps or weaknesses, and 3 targeted technical or behavioral interview questions to probe their experience.

Return a JSON object matching this schema exactly:
{{
  "executive_summary": "2-3 sentences summarizing their fit",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps": ["gap 1", "gap 2"],
  "interview_questions": ["question 1", "question 2", "question 3"]
}}

Job Description:
{jd_text[:3000]}

Candidate Resume:
{resume_text[:4000]}
"""
    result_text = call_gemini_api(api_key, prompt, json_mode=True)
    default_res = {
        "executive_summary": "Could not generate AI summary.",
        "strengths": ["N/A", "N/A", "N/A"],
        "gaps": ["N/A", "N/A"],
        "interview_questions": ["N/A", "N/A", "N/A"]
    }
    if not result_text.strip():
        return default_res
    try:
        cleaned_text = result_text.strip()
        if cleaned_text.startswith("```json"):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text[:-3]
        parsed = json.loads(cleaned_text.strip())
        for k in default_res:
            if k not in parsed:
                parsed[k] = default_res[k]
        return parsed
    except Exception:
        return default_res

# ── MAIN PIPELINE ────────────────────────────────────────────
if __name__ == "__main__":

    # --- Load JD ---
    if not os.path.exists(JD_PATH):
        raise FileNotFoundError(f"JD not found: {JD_PATH}")

    with open(JD_PATH, "rb") as f:
        jd_text = extract_text(f, JD_PATH)

    jd_title_match = re.search(r'Job Title[:\s]+(.+)', jd_text, re.IGNORECASE)
    jd_title      = jd_title_match.group(1).strip() if jd_title_match else "Unknown Role"

    # Check for Gemini API key early for dynamic skill extraction
    g_key = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))

    if g_key:
        print("🔑 Gemini API key detected. AI-enhanced screening enabled.")
        # Dynamic skill extraction with Gemini AI
        print("🤖 Extracting required skills from JD using AI...")
        ai_extracted_skills = extract_skills_from_jd_with_ai(g_key, jd_text)
        if ai_extracted_skills:
            # Combine AI-extracted skills with base taxonomy
            combined_skills = list(set(SKILLS_DB + ai_extracted_skills))
            # Rebuild matcher with dynamic skills
            matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
            patterns = [nlp.make_doc(s.lower()) for s in combined_skills]
            matcher.add("SKILLS", patterns)
            print(f"✅ AI extracted {len(ai_extracted_skills)} skills from JD")
    else:
        print("ℹ️ No Gemini API key detected. Running in local fallback mode.")

    jd_skills = extract_skills(jd_text)

    print(f"\n✅ JD loaded: '{jd_title}'")
    print(f"📌 Skills in JD ({len(jd_skills)}): {', '.join(jd_skills) or 'None detected'}")

    # --- Load Resumes ---
    if not os.path.exists(RESUME_FOLDER):
        raise FileNotFoundError(f"Resumes folder not found: {RESUME_FOLDER}")

    resume_files = [f for f in os.listdir(RESUME_FOLDER)
                    if f.lower().endswith((".pdf", ".docx", ".txt"))]

    if not resume_files:
        raise ValueError("No resume files found in Resumes folder.")

    print(f"\n🔍 Screening {len(resume_files)} resume(s)...\n")
    results = []

    for fname in resume_files:
        print(f"  Processing: {fname}")
        fpath = os.path.join(RESUME_FOLDER, fname)
        with open(fpath, "rb") as f:
            resume_text = extract_text(f, fname)

        if not resume_text.strip():
            print(f"  ⚠️  Could not extract text from {fname}. Skipping.")
            continue

        sim              = get_similarity(resume_text, jd_text)
        matched_skills   = extract_skills(resume_text)
        exp_years        = extract_experience_years(resume_text)
        education        = extract_education(resume_text)
        contact          = extract_contact_info(resume_text)
        score, breakdown = calculate_fit_score(sim, matched_skills, jd_skills, exp_years, education)
        tier             = classify_tier(score)

        # If Gemini key is present, get LLM analysis
        llm_analysis = None
        if g_key:
            llm_analysis = get_candidate_llm_analysis(g_key, resume_text, jd_text)

        results.append({
            "filename":  fname,
            "score":     score,
            "tier":      tier,
            "breakdown": breakdown,
            "contact":   contact,
            "llm_analysis": llm_analysis,
        })

    if not results:
        print("No results. Check your resume files.")
        exit()

    # --- Rank ---
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    for i, r in enumerate(results, 1):
        r["rank"] = i

    # --- Display ---
    print("\n" + "=" * 60)
    print(f"{'RANK':<5} {'CANDIDATE':<30} {'SCORE':>7}  TIER")
    print("=" * 60)
    for r in results:
        print(f"  #{r['rank']:<3} {r['filename']:<30} {r['score']:>6}%  {r['tier']}")
    print("=" * 60)

    print("\n📊 DETAILED BREAKDOWN\n")
    for r in results:
        b = r["breakdown"]
        print(f"▶ {r['filename']}  ({r['score']}% — {r['tier']})")
        print(f"   Semantic Match : {b['semantic_match']}%")
        print(f"   Skill Score    : {b['skill_score']}%  ({len(b['jd_skills_matched'])}/{len(jd_skills)} JD skills)")
        print(f"   Experience     : {b['experience_years']} years")
        print(f"   Education      : {b['education']}")
        print(f"   Matched        : {', '.join(b['jd_skills_matched']) or 'None'}")
        print(f"   Missing        : {', '.join(b['skills_missing']) or 'None'}")
        print(f"   Contact        : {r['contact']['email']}  |  {r['contact']['phone']}")
        
        # Print LLM details if available
        if r.get("llm_analysis"):
            la = r["llm_analysis"]
            print("   🤖 Gemini AI Candidate Summary:")
            print(f"      Summary : {la.get('executive_summary')}")
            print(f"      Strengths: {', '.join(la.get('strengths', []))}")
            print(f"      Gaps     : {', '.join(la.get('gaps', []))}")
            print("      Suggested Interview Questions:")
            for q in la.get('interview_questions', []):
                print(f"        - {q}")
        print()

    # --- Save Reports ---
    generate_csv_report(results, "screening_report.csv")
    generate_pdf_report(results, jd_title, "screening_report.pdf")

    print("\n✅ Reports saved to your project folder.")