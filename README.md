# 🎯 AI Resume Screener

> An intelligent, multi-modal resume screening tool that ranks candidates against a job description using **Sentence-BERT semantic similarity**, **spaCy NLP skill extraction**, **weighted scoring**, and optional **Gemini AI analysis** — all wrapped in an interactive Streamlit dashboard.

---

## 📸 Dashboard Preview

> *(Add your screenshot here)*

---

## ⚡ What Makes This Different

Most resume screeners are glorified CTRL+F — they match keywords and call it AI.

This one doesn't:

- **SBERT embeddings** — understands that "ML Engineer" and "Machine Learning Engineer" mean the same thing. TF-IDF doesn't.
- **Explainability** — every score broken down into 4 dimensions. You know *why* a candidate ranked where they did.
- **Gemini AI layer** — optional LLM analysis generates candidate summaries, gap analysis, and interview questions per resume
- **Recruiter Chat** — ask natural language questions across the entire resume pool ("Who has the most AWS experience?")
- **Adjustable weights** — tune semantic vs skill vs experience vs education importance per role type

---

## 🚀 Features

| Feature | Details |
|---|---|
| Semantic Matching | Sentence-BERT `all-MiniLM-L6-v2` — contextual similarity, not keyword overlap |
| Skill Extraction | spaCy `PhraseMatcher` — 70+ skills across languages, ML, cloud, BI, DevOps |
| Scoring Engine | 4-dimension weighted score: semantic, skills, experience, education |
| Adjustable Weights | Sidebar sliders — tune scoring live per role type |
| Tier Classification | Strong Match / Potential Fit / Weak Fit / Not Suitable |
| Gemini AI Summaries | Executive fit summary, top strengths, gaps, interview questions per candidate |
| AI Recruiter Chat | Ask questions across all uploaded resumes using Gemini |
| Skill Gap Heatmap | Visual matrix — which candidates have which JD skills |
| Radar Charts | Per-candidate breakdown across all 4 scoring dimensions |
| Score Distribution | Histogram of candidate scores across the pool |
| CSV Export | Download full ranked results with all breakdown columns |
| PDF Report | Auto-generated ranked report saved locally |
| Multi-format Support | PDF, DOCX, TXT — JD and resumes |
| Contact Extraction | Email and phone auto-parsed from each resume |
| Education Detection | PhD → Master's → Bachelor's → Diploma hierarchy |
| Experience Parsing | Regex-based years-of-experience extraction |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Semantic Similarity | `sentence-transformers` (SBERT) |
| NLP / Skill Extraction | `spaCy` PhraseMatcher |
| AI Summaries & Chat | Google Gemini API (`gemini-2.5-flash`) |
| PDF Parsing | `PyMuPDF` (fitz) |
| DOCX Parsing | `docx2txt` |
| Data Handling | `pandas` |
| Report Generation | `fpdf2` |
| Dashboard | `Streamlit` |
| Charts | `Plotly` |

---

## 📁 Project Structure

```
ai-resume-screener/
├── app.py                  # Streamlit dashboard (main UI)
├── ai_resumeScreener.py    # Core pipeline (CLI version)
├── requirements.txt        # All dependencies
├── jd.pdf                  # Sample job description
├── Resumes/                # Drop candidate resumes here (CLI mode)
└── README.md
```

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

**4. Run the dashboard**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## 🖥️ How to Use

### Dashboard (Streamlit)
1. Run `streamlit run app.py`
2. Upload your **JD file** (PDF/DOCX/TXT) in the sidebar
3. Upload one or more **candidate resumes**
4. *(Optional)* Enter your **Gemini API key** to unlock AI summaries and recruiter chat
5. Adjust **scoring weights** if needed
6. Click **Run Screening**
7. Explore ranked results, charts, heatmap, and download CSV

### CLI Version
1. Set `JD_PATH` and `RESUME_FOLDER` in `ai_resumeScreener.py`
2. Run:
```bash
python ai_resumeScreener.py
```
Reports saved as `screening_report.csv` and `screening_report.pdf`

---

## 📊 Scoring Engine

Each candidate scored across 4 weighted dimensions:

| Dimension | Default Weight | What It Measures |
|---|---|---|
| Semantic Match | 50% | SBERT cosine similarity between resume and JD |
| Skill Coverage | 30% | % of JD-required skills found in resume |
| Experience | 12% | Years of experience extracted via regex |
| Education | 8% | Highest education level detected |

Weights are fully adjustable via sidebar sliders. Total must equal 100%.

**Tier Classification:**

| Score | Tier |
|---|---|
| ≥ 75% | 🟢 Strong Match |
| 55–74% | 🟡 Potential Fit |
| 35–54% | 🟠 Weak Fit |
| < 35% | 🔴 Not Suitable |

---

## 🤖 Gemini AI Features (Optional)

Add your Gemini API key in the sidebar to unlock:

- **Executive Summary** — 2-3 sentence fit analysis per candidate
- **Strengths** — top 3 strengths relative to the JD
- **Gaps** — top 2 weaknesses or missing experience areas
- **Interview Questions** — 3 targeted questions auto-generated per candidate
- **AI Recruiter Chat** — ask anything across all resumes:
  - *"Who has the most AWS experience?"*
  - *"Compare the top 2 candidates"*
  - *"Which candidates know both Python and SQL?"*

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

---

## ⚠️ Known Limitations

- SBERT truncates text at 3000 characters — very long resumes get cut
- Experience extraction is regex-based — non-standard formats (e.g. "4 yrs") may be missed
- Skill taxonomy is manually curated — niche or emerging tools may not be detected
- Gemini API requires internet and a valid key — offline use falls back to base scoring

---

## 🔮 Roadmap

- [ ] Role-based scoring presets (Tech / Management / Research / Entry Level)
- [ ] Multi-JD comparison — screen one resume against multiple roles
- [ ] Fine-tuned BERT on HR domain data
- [ ] Resume section parser (detect Experience, Education, Skills sections explicitly)
- [ ] Deploy to Streamlit Cloud

---

## 👤 Author

**Karan M**
- GitHub: [@karanhub356](https://github.com/karanhub356)
- Email: mkaran030506@gmail.com

---

