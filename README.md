# 🎯 AI Resume Screener

> A production-ready, multi-page intelligent resume screening tool that ranks candidates against a job description using **Sentence-BERT semantic similarity**, **spaCy NLP skill extraction**, **Gemini AI analysis**, and a **RAG recruiter chatbot** — all wrapped in a secure, multi-page Streamlit dashboard.

---

## 📸 Dashboard Preview

> *(Add your screenshot here)*

---

## ⚡ What Makes This Different

Most resume screeners are glorified CTRL+F — they match keywords and call it AI.

This one doesn't:

- **SBERT embeddings** — understands "ML Engineer" and "Machine Learning Engineer" mean the same thing. TF-IDF doesn't.
- **Dynamic skill extraction** — Gemini AI reads the JD and extracts skills beyond the hardcoded taxonomy, so niche or emerging tools don't get missed
- **Date-aware experience parsing** — reads actual work history date ranges (e.g., "June 2021 – Present"), not just regex for "X years of experience"
- **Explainability first** — every score broken down into 4 dimensions with matched/missing skill chips
- **RAG recruiter chatbot** — ask natural language questions across the entire resume pool with full conversation memory
- **Password protected** — auth gate before anyone sees candidate data
- **Auto-normalized weights** — sliders never silently break your scoring

---

## 🗂️ Project Structure

```
ai-resume-screener/
├── app.py                        # Entry point — multi-page Streamlit app
│
├── pages/
│   ├── __init__.py
│   ├── home.py                   # Welcome screen + feature overview
│   ├── screen.py                 # Upload JD & resumes, configure weights, run screening
│   ├── results.py                # Rankings, analytics, skill gap heatmap, CSV download
│   └── chat.py                   # RAG recruiter chatbot with conversation memory
│
├── utils/
│   ├── __init__.py
│   ├── auth.py                   # Password protection gate
│   ├── nlp_utils.py              # SBERT, spaCy, scoring, text extraction
│   ├── gemini_utils.py           # Gemini API — skill extraction, summaries, chat
│   └── visualization.py          # Plotly charts, tier badges, CSV export
│
├── ai_resumeScreener.py          # CLI version — run without Streamlit
├── requirements.txt
└── README.md
```

---

## 🚀 Features

| Feature | Details |
|---|---|
| Semantic Matching | Sentence-BERT `all-MiniLM-L6-v2` — contextual similarity, not keyword overlap |
| Dynamic Skill Extraction | Gemini AI reads JD and extracts skills beyond hardcoded taxonomy |
| spaCy Skill Matching | `PhraseMatcher` across 70+ skills — languages, ML, cloud, BI, DevOps |
| Experience Parsing | Dual strategy — explicit mentions + date range parsing from work history |
| Education Detection | PhD → Master's → Bachelor's → Diploma hierarchy |
| Contact Extraction | Email and phone auto-parsed from each resume |
| Weighted Scoring | 4-dimension score: semantic, skills, experience, education |
| Auto-normalized Weights | Sidebar sliders auto-normalize — scoring never silently breaks |
| Tier Classification | Strong Match / Potential Fit / Weak Fit / Not Suitable |
| Gemini AI Summaries | Executive fit summary, strengths, gaps, interview questions per candidate |
| RAG Recruiter Chat | Ask questions across all resumes — full conversation memory |
| Skill Gap Heatmap | Visual matrix — who has which JD skills |
| Radar Charts | Per-candidate breakdown across all 4 scoring dimensions |
| Score Distribution | Histogram of candidate scores across the pool |
| CSV Export | Download full ranked results with all breakdown columns |
| Password Protection | Auth gate — secure before sharing with hiring teams |
| Multi-format Support | PDF, DOCX, TXT — JD and resumes |
| Auto spaCy Download | Downloads `en_core_web_sm` automatically if missing |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Semantic Similarity | `sentence-transformers` — SBERT `all-MiniLM-L6-v2` |
| NLP / Skill Extraction | `spaCy` PhraseMatcher |
| AI Summaries & Chat | Google Gemini API (`gemini-2.5-flash`) |
| PDF Parsing | `PyMuPDF` (fitz) |
| DOCX Parsing | `docx2txt` |
| Data Handling | `pandas` |
| Report Generation | `fpdf2` |
| Dashboard | `Streamlit` (multi-page) |
| Charts | `Plotly` |
| HTTP Client | `requests` |

---

## ⚙️ Setup & Installation

**1. Clone the repo**
```bash
git clone https://github.com/karanhub356/ai-resume-screener.git
cd ai-resume-screener
```

**2. Create a virtual environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

> spaCy model also auto-downloads on first run if missing.

**4. Run the dashboard**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

**Default password:** `admin123`
Change it by setting the `APP_PASSWORD` environment variable or via Streamlit secrets.

---

## 🖥️ How to Use

### Dashboard (Streamlit)

| Step | Page | Action |
|---|---|---|
| 1 | Home | Read feature overview |
| 2 | Screen | Upload JD + resumes, set API key, adjust weights, run screening |
| 3 | Results | Explore rankings, radar charts, heatmap, download CSV |
| 4 | Chat | Ask questions across all resumes using Gemini AI |

### CLI Version
Set paths in `ai_resumeScreener.py`:
```python
JD_PATH       = r"path\to\jd.pdf"
RESUME_FOLDER = r"path\to\Resumes"
```
Run:
```bash
python ai_resumeScreener.py
```
Outputs `screening_report.csv` and `screening_report.pdf`

For Gemini AI in CLI mode, set environment variable:
```bash
# Windows
set GEMINI_API_KEY=your_key_here

# Mac/Linux
export GEMINI_API_KEY=your_key_here
```

---

## 📊 Scoring Engine

Each candidate scored across 4 weighted dimensions:

| Dimension | Default Weight | What It Measures |
|---|---|---|
| Semantic Match | 50% | SBERT cosine similarity between resume and JD |
| Skill Coverage | 30% | % of JD-required skills found in resume |
| Experience | 12% | Years extracted via explicit mention + date range parsing |
| Education | 8% | Highest education level detected |

Weights are adjustable in the sidebar. They auto-normalize — no need to manually sum to 100%.

**Tier Classification:**

| Score | Tier |
|---|---|
| ≥ 75% | 🟢 Strong Match |
| 55–74% | 🟡 Potential Fit |
| 35–54% | 🟠 Weak Fit |
| < 35% | 🔴 Not Suitable |

---

## 🤖 Gemini AI Features (Optional)

Enter your Gemini API key in the sidebar to unlock:

**Per Candidate:**
- Executive fit summary
- Top 3 strengths relative to the JD
- Top 2 gaps or weaknesses
- 3 targeted interview questions

**Dynamic JD Skill Extraction:**
- Gemini reads the JD and extracts skills beyond the 70+ base taxonomy
- Niche tools, emerging frameworks, role-specific requirements all captured
- Combined with base taxonomy for maximum coverage

**RAG Recruiter Chat:**
- Ask natural language questions across all uploaded resumes
- Full conversation memory — follow-up questions work
- Context-aware — cites specific candidates
- Examples:
  - *"Who has the most AWS experience?"*
  - *"Compare the top 2 candidates"*
  - *"Which candidates know both Python and SQL?"*
  - *"Who would be the best fit for a senior role?"*

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

---

## 🔐 Password Protection

Default password: `admin123`

**Change via environment variable:**
```bash
set APP_PASSWORD=yourpassword   # Windows
export APP_PASSWORD=yourpassword # Mac/Linux
```

**Change via Streamlit secrets** (for deployment):
```toml
# .streamlit/secrets.toml
APP_PASSWORD = "yourpassword"
```

---

## ⚠️ Known Limitations

- SBERT truncates text at 3000 characters — very long resumes get cut
- Date range experience parsing may overcount if resume lists overlapping roles
- Skill taxonomy is 70+ but manually curated — very niche tools may be missed without Gemini
- Gemini API requires internet and a valid key — falls back to base scoring without it
- Resume text stored in session state — memory usage grows with large candidate pools

---

## 🔮 Roadmap

- [ ] Role-based scoring presets (Tech / Management / Research / Entry Level)
- [ ] Multi-JD comparison — screen one resume against multiple roles simultaneously
- [ ] Resume section parser — detect Experience, Education, Skills sections explicitly
- [ ] Fine-tuned BERT on HR domain data for better semantic matching
- [ ] Deploy to Streamlit Cloud with secrets management
- [ ] Persistent screening history with database integration

---

## 📦 Requirements

```
streamlit>=1.35.0
spacy>=3.7.0
sentence-transformers>=2.2.0
PyMuPDF>=1.22.0
docx2txt>=0.8
fpdf2>=2.7.0
python-docx>=1.1.0
plotly>=5.15.0
pandas>=2.0.0
requests>=2.31.0
```

Install:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

---

## 👤 Author

**Karan M**
- GitHub: [@karanhub356](https://github.com/karanhub356)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-linkedin)
- Email: mkaran030506@gmail.com

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

> ⭐ Star the repo if it helped you.
