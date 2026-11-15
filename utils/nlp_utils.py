"""
NLP and ML utilities for resume screening.
Contains text extraction, skill matching, experience parsing, and scoring logic.
"""
import re
from datetime import datetime
import fitz
import docx2txt
import spacy
import spacy.cli
from spacy.matcher import PhraseMatcher
from sentence_transformers import SentenceTransformer, util
try:
    import streamlit as st
    cache_resource = st.cache_resource
except ImportError:
    st = None
    cache_resource = lambda f: f

# Base Skills Taxonomy
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

@cache_resource
def load_models():
    """Load and cache spaCy and SBERT models."""
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
    sbert = SentenceTransformer("all-MiniLM-L6-v2")
    return nlp, sbert

def build_matcher(nlp, skills_list=None):
    """Build spaCy PhraseMatcher with given skills list."""
    if skills_list is None:
        skills_list = SKILLS_DB
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(s.lower()) for s in skills_list]
    matcher.add("SKILLS", patterns)
    return matcher

def extract_text(file_obj, filename: str) -> str:
    """Extract text from PDF, DOCX, or TXT files with error handling."""
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

def extract_skills(text, nlp, matcher):
    """Extract skills from text using spaCy PhraseMatcher."""
    doc = nlp(text)
    matches = matcher(doc)
    return list(set(doc[start:end].text for _, start, end in matches))

def extract_experience_years(text: str) -> int:
    """
    Extract years of experience using two strategies:
    1. Explicit mentions like "5 years of experience"
    2. Date range parsing from work history
    """
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
    """Extract highest education level from text."""
    hierarchy = [
        ("PhD", ["phd", "ph.d", "doctorate", "doctor of philosophy"]),
        ("Master's", ["master", "m.tech", "m.s.", "msc", "m.e.", "mba", "m.b.a"]),
        ("Bachelor's", ["bachelor", "b.tech", "b.e.", "b.s.", "bsc", "b.sc", "undergraduate"]),
        ("Diploma", ["diploma", "associate"]),
    ]
    text_lower = text.lower()
    for level, keywords in hierarchy:
        if any(k in text_lower for k in keywords):
            return level
    return "Not detected"

def extract_contact_info(text: str) -> dict:
    """Extract email and phone from text."""
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', text)
    # Phone: match but strip newlines and normalize to single line
    phone_match = re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text)
    phone = "—"
    if phone_match:
        # Remove newlines, collapse whitespace
        phone = re.sub(r'\s+', ' ', phone_match.group(0).strip())
    return {
        "email": email_match.group(0) if email_match else "—",
        "phone": phone,
    }

def get_similarity(resume_text, jd_text, sbert):
    """Calculate cosine similarity between resume and JD using SBERT."""
    emb_r = sbert.encode(resume_text[:3000], convert_to_tensor=True)
    emb_j = sbert.encode(jd_text[:3000], convert_to_tensor=True)
    return float(util.cos_sim(emb_r, emb_j))

def calculate_fit_score(similarity, matched_skills, jd_skills, exp_years, education, weights):
    """
    Calculate weighted fit score with automatic normalization.
    weights: dict with keys w_semantic, w_skills, w_exp, w_edu
    """
    # Normalize weights
    total_w = weights['w_semantic'] + weights['w_skills'] + weights['w_exp'] + weights['w_edu']
    if total_w > 0:
        w_semantic_norm = (weights['w_semantic'] / total_w) * 100
        w_skills_norm = (weights['w_skills'] / total_w) * 100
        w_exp_norm = (weights['w_exp'] / total_w) * 100
        w_edu_norm = (weights['w_edu'] / total_w) * 100
    else:
        w_semantic_norm = w_skills_norm = w_exp_norm = w_edu_norm = 0

    jd_skill_count = max(len(jd_skills), 1)
    jd_matched = [s for s in matched_skills if s.lower() in [j.lower() for j in jd_skills]]
    skill_score = min(len(jd_matched) / jd_skill_count, 1.0)
    exp_score = min(exp_years / 10, 1.0)
    edu_map = {"PhD": 1.0, "Master's": 0.85, "Bachelor's": 0.7, "Diploma": 0.5, "Not detected": 0.3}
    edu_score = edu_map.get(education, 0.3)

    final = (similarity * (w_semantic_norm/100) + skill_score * (w_skills_norm/100) +
             exp_score * (w_exp_norm/100) + edu_score * (w_edu_norm/100)) * 100
    score = round(final, 2)

    breakdown = {
        "semantic_match": round(similarity * 100, 1),
        "skill_score": round(skill_score * 100, 1),
        "exp_score": round(exp_score * 100, 1),
        "edu_score": round(edu_score * 100, 1),
        "jd_skills_matched": jd_matched,
        "all_skills_found": matched_skills,
        "skills_missing": [s for s in jd_skills if s.lower() not in [m.lower() for m in matched_skills]],
        "experience_years": exp_years,
        "education": education,
    }
    return score, breakdown

def classify_tier(score: float) -> str:
    """Classify score into tier categories."""
    if score >= 75: return "Strong Match"
    if score >= 55: return "Potential Fit"
    if score >= 35: return "Weak Fit"
    return "Not Suitable"
