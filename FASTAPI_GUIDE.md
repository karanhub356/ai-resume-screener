# AI Resume Screener — FastAPI Edition

## ✅ Project Cleanup Complete (Nov 14, 2026)

**Streamlit files removed** — All backed up in `streamlit_backup/`  
**FastAPI now primary** — Clean structure, DB-backed, ready to run

## 🏗️ Final Structure

```
AI_resumeScreener/
├── landing/                      # Main FastAPI App
│   ├── main.py                   # Server + /api/screen, /chat, /export-csv
│   ├── api_endpoints.py          # NEW: /api/history, /results/{id}, /stats
│   ├── requirements.txt          # Complete dependencies
│   ├── templates/index.html      # Interactive dashboard
│   └── static/css/style.css
├── database/                     # SQLite (3 tables)
│   ├── schema.sql
│   └── db.py
├── utils/                        # NLP + Gemini + DB helpers
│   ├── nlp_utils.py
│   ├── gemini_utils.py
│   └── database_helpers.py
├── Resumes/ (test data)
├── jd.pdf (test JD)
├── streamlit_backup/ (archived)
└── FASTAPI_GUIDE.md (this file)
```

## 🚀 Quick Start

```bash
cd C:\Users\Karan M\Projects\AI_resumeScreener\landing
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python main.py
```

Open: **http://localhost:8000**

## 🔌 API Endpoints

### ✅ Existing (Now DB-backed)
- `POST /api/screen` — Upload JD + resumes, returns ranked results + **jd_id** (saved to DB)
- `POST /api/chat` — RAG recruiter assistant
- `GET /api/export-csv` — Download CSV report

### ✅ NEW Analytics Endpoints
- `GET /api/history` — List past screenings with stats
- `GET /api/results/{jd_id}` — Retrieve results by screening ID
- `GET /api/stats` — Dashboard metrics (totals, avg/best scores, tier distribution)

## 📊 Database Persistence

**All screenings now save to SQLite** (`resume_screener.db`)
- Job descriptions → `job_descriptions` table
- Candidates → `candidates` table (dedupe by email)
- Results → `screening_results` table (with FK links)

## 🎨 Frontend

`templates/index.html` already wired:
- Liquid glass design (orbs, glassmorphism)
- File drag-and-drop
- Live screening with tier badges
- Skill gap visualization
- RAG chat integration
- CSV export

**What's missing:** Dashboard/History/Compare pages (exist only in Streamlit backup)

## 📦 Dependencies Installed

All needed packages in `landing/requirements.txt`:
- FastAPI, Uvicorn, Jinja2
- spaCy, Sentence-Transformers
- PyMuPDF, docx2txt, pandas
- python-multipart (file uploads)

## 🧪 Test with Sample Data

1. Start server: `python main.py`
2. Open http://localhost:8000
3. Upload `../jd.pdf` + resumes from `../Resumes/`
4. View results with scores, tier badges, skill chips

## 🔄 Restore Streamlit (if needed)

```bash
cp -r streamlit_backup/* .
pip install streamlit plotly openpyxl
streamlit run app.py
```

## 📝 Next Steps (Optional)

1. **Build Dashboard page** — Fetch `/api/stats`, render charts
2. **Build History page** — List `/api/history`, click to load results
3. **Build Compare page** — Radar charts for candidate comparison
4. **Add authentication** — JWT tokens, user sessions
5. **Deploy** — Vercel, Render, or Docker

---

**Status:** ✅ FastAPI complete, DB working, API documented, ready to extend  
**Last Updated:** 2026-11-14 15:05 UTC
