# 🎯 AI Resume Screener & Recruiter Assistant (FastAPI Edition)

An AI-powered recruitment intelligence platform that parses, grades, and ranks resumes against job descriptions. Built with a **FastAPI** backend, interactive single-page dashboard with liquid-glass aesthetic, **spaCy** + **Sentence-Transformers (SBERT)** semantic matching, **SQLite** persistence, and optional **Google Gemini API** for executive summaries, interview questions, and a RAG recruiter chatbot.

---

## 🌟 Key Features

* **Interactive Liquid-Glass Web Suite** (`http://localhost:8000`): Single-page dark-mode dashboard with animated ambient orbs, drag-and-drop JD + resume upload, and real-time candidate cards.
* **Semantic Match Grading**: SBERT (`all-MiniLM-L6-v2`) computes contextual cosine similarity between JD and resumes — goes far beyond keyword counting.
* **Information & Skill Extraction**: spaCy `PhraseMatcher` against a 200+ skill taxonomy parses matching and missing skills. Extracts contact info (email, normalized phone), education level, and years of experience automatically.
* **Dynamic Recruiter Scoring**: Fine-tune weights on the fly — Semantic Match, Skill Coverage, Experience, and Education automatically normalize to 100%.
* **SQLite Persistence**: Every screening run saves candidates, JDs, and detailed score breakdowns to `resume_screener.db` with foreign keys and deduplication by email.
* **Built-in Analytics Suite**:
  * 📊 **Dashboard** (`#dashboard`): Total screenings, candidate counts, average/best scores, and tier distribution percentages.
  * 📜 **History** (`#history`): Browse all past screenings with one-click **Load** to restore rankings into the workspace.
  * ⚖️ **Compare** (`#compare`): Side-by-side metric comparison between any two candidates with winner trophies (🏆) and skill chips.
  * 🔥 **Skill Gap Heatmap**: Matrix view of candidate coverage against required JD skills.
  * ⬇️ **CSV Export** (`/api/export-csv`): Download structured screening reports.
* **Optional Gemini AI Enhancements**:
  * **Executive Summaries**: AI assessment of overall candidate fit.
  * **Strengths & Gaps**: Top 3 matching areas and top 2 risk gaps.
  * **Personalized Interview Guides**: 3 targeted technical/behavioral questions to probe gaps.
  * **RAG Chatbot Workspace**: Conversational querying over the active candidate pool.
* **Optional Password Protection**: Set `APP_PASSWORD` to gate the dashboard behind a login screen; unset = open dev mode.

---

## 🛠️ Technology Stack

* **Backend / API**: FastAPI, Uvicorn, Jinja2, python-multipart
* **NLP & Semantics**: spaCy (`en_core_web_sm`), Sentence-Transformers (`all-MiniLM-L6-v2`)
* **Generative AI**: Google Gemini API (raw REST calls, zero heavy SDK overhead)
* **Document Parsers**: PyMuPDF (`fitz`), `docx2txt`
* **Database**: SQLite (`resume_screener.db`) via standard library `sqlite3`
* **Frontend**: Pure HTML5 / CSS3 / Vanilla JS (no node_modules / build step required)

---

## 🚀 Quick Start

### 1. Setup Virtual Environment (PowerShell)

```powershell
cd "C:\Users\Karan M\Projects\AI_resumeScreener"
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
cd landing
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Run the Server

```powershell
# From landing/ directory:
python main.py

# OR with uvicorn directly:
uvicorn main:app --reload --port 8000
```

### 4. Open in Browser

👉 **http://localhost:8000**

---

## 🔑 Environment Variables (Optional)

Configure in your PowerShell session before starting the server:

```powershell
# Optional: Enable Gemini AI summaries, interview guides, and RAG chat
$env:GEMINI_API_KEY = "your_gemini_api_key_here"

# Optional: Password-protect the dashboard
$env:APP_PASSWORD = "your_secret_password"

# Optional: Custom database file location (default: ./resume_screener.db)
$env:DATABASE_PATH = "C:\Users\Karan M\Projects\AI_resumeScreener\resume_screener.db"
```

*(You can also paste your Gemini API key directly into the workspace UI — it stays in session memory only.)*

---

## 🔌 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | Serves the interactive screening web app |
| `/login` | `GET` / `POST` | Login page (active only when `APP_PASSWORD` is set) |
| `/logout` | `GET` | Clears auth session cookie |
| `/api/screen` | `POST` | Upload JD + multiple resumes via multipart form; returns ranked JSON |
| `/api/chat` | `POST` | Query the candidate pool with RAG recruiter assistant |
| `/api/export-csv` | `GET` | Download CSV report (falls back to latest DB screening if server restarted) |
| `/api/history` | `GET` | List past screenings with aggregate stats |
| `/api/results/{jd_id}` | `GET` | Retrieve detailed candidate ranking for a specific JD |
| `/api/stats` | `GET` | Global dashboard metrics and tier distribution |

---

## 📁 Project Structure

```
AI_resumeScreener/
├── landing/                      # Main FastAPI Application
│   ├── main.py                   # Server, lifespan handler, routes, auth gate
│   ├── api_endpoints.py          # /api/history, /api/results/{id}, /api/stats
│   ├── requirements.txt          # Production dependencies
│   └── templates/
│       ├── index.html            # Single-page dashboard (liquid glass)
│       └── login.html            # Password gate screen
├── database/                     # SQLite persistence
│   ├── schema.sql                # 3 tables: job_descriptions, candidates, screening_results
│   ├── db.py                     # Connection manager & init_db()
│   └── __init__.py
├── utils/                        # NLP & AI pipeline
│   ├── nlp_utils.py              # Text extraction, spaCy matching, SBERT, scoring
│   ├── gemini_utils.py           # Gemini API wrappers (REST-based)
│   ├── database_helpers.py       # CRUD operations for screenings & candidates
│   └── __init__.py
├── Resumes/                      # Sample resumes for testing
│   ├── Karan_cv0605.pdf
│   └── Karan_cv503.pdf
├── jd.pdf                        # Sample Job Description
├── streamlit_backup/             # Complete archive of pre-migration Streamlit app
├── FASTAPI_GUIDE.md              # Deep-dive architecture & API reference
└── README.md                     # This file
```

---

## 🧪 Testing with Sample Files

1. Start the server (`python landing/main.py`) and visit `http://localhost:8000`.
2. In the **⚙️ Upload & Configure** panel:
   - Click **1. Job Description** and select `jd.pdf`.
   - Click **2. Candidate Resumes** and select both files from `Resumes/`.
   - (Optional) Paste your Gemini API key in the API key field.
3. Click **🚀 Run Screening**.
4. Explore:
   - **Rankings**: Live candidate cards, tier badges, contact info, matched & missing skill chips.
   - **Analytics**: Fit score bar chart.
   - **Skill Gap Heatmap**: Candidate vs required skill coverage matrix.
   - **Full Candidate Table**: Complete tabular view + CSV download.
   - **Recruiter Chat**: Ask "Who has the best experience with SQL and data pipelines?".
   - **Dashboard & History**: Scroll down to view stored aggregate metrics and reload past runs.
   - **Compare**: Side-by-side comparison with winner trophies.

---

## 🔄 Restoring the Streamlit App (Archive)

All pre-migration Streamlit files are preserved intact in `streamlit_backup/`:

```powershell
# To run the legacy Streamlit version:
cd streamlit_backup
pip install -r requirements.txt
streamlit run app.py
```

---

## 📄 License & Attribution

Developed by **Karan M** — SKCET B.Tech AI & Data Science (2026).
Portfolio: [karan-m-portfolio.vercel.app](https://karan-m-portfolio.vercel.app/)
GitHub: [@karanhub356](https://github.com/karanhub356)
