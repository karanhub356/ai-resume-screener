import sys
import os
import re
import json
import csv
import io
from typing import List, Optional

# Add parent directory to sys.path to access utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI, Request, UploadFile, File, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import quote
from pydantic import BaseModel
from spacy.matcher import PhraseMatcher

from contextlib import asynccontextmanager

from utils.nlp_utils import (
    load_models, build_matcher, extract_text, extract_skills,
    extract_experience_years, extract_education, extract_contact_info,
    get_similarity, calculate_fit_score, classify_tier, SKILLS_DB
)
from utils.gemini_utils import extract_skills_from_jd_with_ai, get_candidate_llm_analysis, call_gemini_api
from utils.database_helpers import (
    save_job_description, upsert_candidate, save_screening_result,
    get_historical_screenings, get_results_for_jd
)
from database.db import init_db
from api_endpoints import router as api_router

# Global models and session store
nlp_model = None
sbert_model = None
base_matcher = None
screening_store = {}

@asynccontextmanager
async def lifespan(app):
    global nlp_model, sbert_model, base_matcher
    print("Loading NLP and SBERT models for FastAPI landing server...")
    nlp_model, sbert_model = load_models()
    base_matcher = build_matcher(nlp_model)
    init_db()
    print("Models loaded successfully.")
    yield

app = FastAPI(title="ResumeAI - AI Resume Screener & Analytics", lifespan=lifespan)

# Templates
templates = Jinja2Templates(directory="templates")

# Include additional API routes
app.include_router(api_router)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/app")
@app.get("/screen")
async def redirect_to_dashboard():
    return RedirectResponse(url="/#workspace")

# ── OPTIONAL PASSWORD GATE (mirrors old Streamlit utils/auth.py) ──────────
# Set APP_PASSWORD env var to enable. Unset = open dev mode (no friction).
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")

@app.middleware("http")
async def auth_gate(request: Request, call_next):
    if not APP_PASSWORD:
        return await call_next(request)
    path = request.url.path
    if path in ("/login", "/logout", "/docs", "/openapi.json"):
        return await call_next(request)
    provided = (
        request.headers.get("X-App-Password")
        or request.query_params.get("auth")
        or request.cookies.get("app_session")
    )
    if provided == APP_PASSWORD:
        return await call_next(request)
    if path.startswith("/api/"):
        raise HTTPException(status_code=401, detail="Authentication required")
    return RedirectResponse(url=f"/login?next={quote(request.url.path, safe='')}")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if not APP_PASSWORD:
        return RedirectResponse(url="/")
    next_url = request.query_params.get("next", "/")
    return templates.TemplateResponse(request=request, name="login.html", context={"error": None, "next": next_url})

@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    if not APP_PASSWORD:
        return RedirectResponse(url="/")
    form = await request.form()
    password = form.get("password", "")
    next_url = form.get("next", "/") or "/"
    if password == APP_PASSWORD:
        response = RedirectResponse(url=next_url)
        response.set_cookie(key="app_session", value=APP_PASSWORD, httponly=True, samesite="lax")
        return response
    return templates.TemplateResponse(request=request, name="login.html", context={"error": "Incorrect password", "next": next_url})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="app_session")
    return response

def _get_active_screening():
    """Return (results, jd_title) from memory; fall back to latest DB screening after restart."""
    global screening_store
    results = screening_store.get("results", [])
    if results:
        return results, screening_store.get("jd_title", "General Role")
    try:
        from database.db import get_db_connection
        conn = get_db_connection()
        row = conn.execute("SELECT id, title FROM job_descriptions ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()
        if row:
            results = get_results_for_jd(row["id"])
            screening_store["results"] = results
            screening_store["jd_title"] = row["title"]
            screening_store.setdefault("jd_text", "")
            return results, row["title"]
    except Exception as e:
        print(f"⚠️ DB fallback failed: {e}")
    return [], "General Role"

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

def _allowed_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

@app.post("/api/screen")
async def run_screening(
    jd_file: UploadFile = File(...),
    resumes: List[UploadFile] = File(...),
    w_semantic: float = Form(50.0),
    w_skills: float = Form(30.0),
    w_exp: float = Form(12.0),
    w_edu: float = Form(8.0),
    gemini_api_key: str = Form("")
):
    global nlp_model, sbert_model, base_matcher, screening_store

    if not nlp_model or not sbert_model:
        nlp_model, sbert_model = load_models()
        base_matcher = build_matcher(nlp_model)

    if not _allowed_file(jd_file.filename):
        raise HTTPException(status_code=400, detail="JD file must be .pdf, .docx, or .txt")

    # 1. Read JD Text
    jd_content = await jd_file.read()
    jd_file_obj = io.BytesIO(jd_content)
    jd_text = extract_text(jd_file_obj, jd_file.filename)

    if not jd_text.strip():
        raise HTTPException(status_code=400, detail=f"Failed to extract text from Job Description file: {jd_file.filename}")

    # Extract JD Title
    jd_title_match = re.search(r'Job Title[:\s]+(.+)', jd_text, re.IGNORECASE)
    jd_title = jd_title_match.group(1).strip() if jd_title_match else jd_file.filename.rsplit('.', 1)[0]

    matcher = base_matcher
    ai_skills_extracted = []

    # Optional AI skill extraction from JD
    if gemini_api_key.strip():
        try:
            ai_skills_extracted = extract_skills_from_jd_with_ai(gemini_api_key.strip(), jd_text)
            if ai_skills_extracted:
                combined_skills = list(set(SKILLS_DB + ai_skills_extracted))
                matcher = PhraseMatcher(nlp_model.vocab, attr="LOWER")
                patterns = [nlp_model.make_doc(s.lower()) for s in combined_skills]
                matcher.add("SKILLS", patterns)
        except Exception as e:
            print(f"⚠️ AI Skill extraction error: {e}")

    jd_skills = extract_skills(jd_text, nlp_model, matcher)

    # Normalize weights
    total_w = w_semantic + w_skills + w_exp + w_edu
    if total_w > 0:
        weights = {
            'w_semantic': (w_semantic / total_w) * 100,
            'w_skills': (w_skills / total_w) * 100,
            'w_exp': (w_exp / total_w) * 100,
            'w_edu': (w_edu / total_w) * 100
        }
    else:
        weights = {'w_semantic': 25.0, 'w_skills': 25.0, 'w_exp': 25.0, 'w_edu': 25.0}

    # 2. Process Candidates
    results = []

    for resume_file in resumes:
        if not _allowed_file(resume_file.filename):
            continue  # skip invalid file types
        r_content = await resume_file.read()
        r_file_obj = io.BytesIO(r_content)
        resume_text = extract_text(r_file_obj, resume_file.filename)

        if not resume_text.strip():
            continue

        sim = get_similarity(resume_text, jd_text, sbert_model)
        matched_skills = extract_skills(resume_text, nlp_model, matcher)
        exp_years = extract_experience_years(resume_text)
        education = extract_education(resume_text)
        contact = extract_contact_info(resume_text)

        score, breakdown = calculate_fit_score(sim, matched_skills, jd_skills, exp_years, education, weights)
        tier = classify_tier(score)

        llm_analysis = None
        if gemini_api_key.strip():
            try:
                llm_analysis = get_candidate_llm_analysis(gemini_api_key.strip(), resume_text, jd_text)
            except Exception as e:
                print(f"⚠️ Gemini candidate analysis error for {resume_file.filename}: {e}")

        results.append({
            "filename": resume_file.filename,
            "score": score,
            "tier": tier,
            "breakdown": breakdown,
            "contact": contact,
            "resume_text": resume_text[:1500],
            "llm_analysis": llm_analysis
        })

    # Sort candidates by score descending
    results = sorted(results, key=lambda x: x["score"], reverse=True)
    for idx, item in enumerate(results, 1):
        item["rank"] = idx

    # Save in global session store
    screening_store["results"] = results
    screening_store["jd_title"] = jd_title
    screening_store["jd_skills"] = jd_skills
    screening_store["jd_text"] = jd_text

    # Persist to SQLite (Dashboard / History / Compare read from here)
    jd_id = None
    try:
        jd_id = save_job_description(jd_title, None, None, jd_text, jd_file.filename)
        for r in results:
            email = r["contact"]["email"] if r["contact"]["email"] != "—" else None
            phone = r["contact"]["phone"] if r["contact"]["phone"] != "—" else None
            cid = upsert_candidate(email, phone, r.get("resume_text", ""), r["filename"], r["breakdown"]["education"], r["breakdown"]["experience_years"])
            save_screening_result(jd_id, cid, r["score"], r["tier"], r["breakdown"], r["contact"], r.get("llm_analysis"))
    except Exception as e:
        print(f"⚠️ Database save failed: {e}")

    return {
        "success": True,
        "count": len(results),
        "jd_id": jd_id,
        "jd_title": jd_title,
        "jd_skills": jd_skills,
        "results": results
    }

class ChatQuery(BaseModel):
    question: str
    gemini_api_key: str

@app.post("/api/chat")
async def chat_with_recruiter(payload: ChatQuery):
    if not payload.gemini_api_key.strip():
        raise HTTPException(status_code=400, detail="Gemini API Key is required for RAG Recruiter Chat.")

    results, jd_title = _get_active_screening()
    jd_text = screening_store.get("jd_text", "")

    if not results:
        raise HTTPException(status_code=400, detail="No screening results found. Please run screening first.")

    # Construct context from candidate pool
    context_lines = [f"Job Title: {jd_title}", "Candidate Pool Summary:"]
    for r in results[:10]:
        b = r["breakdown"]
        context_lines.append(
            f"- Rank #{r['rank']}: {r['filename']} | Score: {r['score']}% | Tier: {r['tier']} | "
            f"Exp: {b['experience_years']} yrs | Edu: {b['education']} | "
            f"Matched Skills: {', '.join(b['jd_skills_matched'])} | "
            f"Missing Skills: {', '.join(b['skills_missing'])}"
        )

    pool_context = "\n".join(context_lines)

    system_instruction = f"""
You are ResumeAI, an expert AI recruiter assistant. You have full context over the candidate pool for the role of "{jd_title}".
Answer the recruiter's question accurately, highlighting top candidate matches, specific skills, strengths, and experience.

Candidate Pool Context:
{pool_context}
"""

    answer = call_gemini_api(payload.gemini_api_key.strip(), system_instruction=system_instruction, prompt=payload.question)
    if not answer.strip():
        answer = "I couldn't generate a response with the provided Gemini API key. Please check the key and try again."

    return {"answer": answer}

@app.get("/api/export-csv")
async def export_csv():
    results, _ = _get_active_screening()
    if not results:
        raise HTTPException(status_code=400, detail="No screening results to export.")

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Filename", "Fit Score (%)", "Tier", "Semantic Match (%)",
        "Skill Score (%)", "Experience Score (%)", "Education Score (%)",
        "Exp (Years)", "Education Level", "Email", "Phone", "Matched Skills", "Missing Skills"
    ])

    for r in results:
        b = r["breakdown"]
        c = r["contact"]
        writer.writerow([
            r["rank"],
            r["filename"],
            r["score"],
            r["tier"],
            b["semantic_match"],
            b["skill_score"],
            b["exp_score"],
            b["edu_score"],
            b["experience_years"],
            b["education"],
            c["email"],
            c["phone"],
            "; ".join(b["jd_skills_matched"]),
            "; ".join(b["skills_missing"])
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=screening_report.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
