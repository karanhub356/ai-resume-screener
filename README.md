# 🎯 AI Resume Screener

An intelligent resume screening tool that ranks candidates against a job description using **semantic similarity**, **NLP-based skill extraction**, and a **weighted scoring engine** — with an interactive Streamlit dashboard.

> Built with Sentence-BERT, spaCy, and Streamlit. No keyword-matching gimmicks — actual semantic understanding.

---

## 📸 Dashboard Preview

> <img width="1916" height="1021" alt="Screenshot 2026-06-11 091801" src="https://github.com/user-attachments/assets/c5dedc31-8dcc-49e3-b4b6-463218319dcc" />


---

## 🚀 Features

- **Semantic Matching** — Uses Sentence-BERT (`all-MiniLM-L6-v2`) to measure contextual similarity between resume and JD, not just keyword overlap
- **NLP Skill Extraction** — spaCy `PhraseMatcher` scans resumes against a taxonomy of 70+ technical and soft skills
- **Weighted Scoring Engine** — Scores candidates across 4 dimensions: semantic match, skill coverage, experience, and education
- **Adjustable Weights** — Recruiter can tune scoring weights (semantic/skills/exp/edu) in real time via sidebar sliders
- **Explainability** — Every score broken down: matched skills, missing skills, semantic %, education level
- **Interactive Dashboard** — Streamlit UI with radar charts, skill gap heatmap, score bar chart, and ranked candidate cards
- **Export Reports** — Download results as CSV; PDF report auto-generated on each run
- **Multi-format Support** — Accepts PDF, DOCX, and TXT for both JD and resumes

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Semantic Similarity | `sentence-transformers` (SBERT) |
| Skill Extraction | `spaCy` PhraseMatcher |
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
├── app.py                  # Streamlit dashboard
├── ai_resumeScreener.py    # Core pipeline (CLI version)
├── requirements.txt        # Dependencies
├── jd.pdf                  # Sample job description
├── Resumes/                # Drop candidate resumes here
│   └── candidate.pdf
└── README.md
```

---

## ⚙️ Setup & Installation

**1. Clone the repo**
```bash
git clone https://github.com/yourusername/ai-resume-screener.git
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

**Dashboard (Streamlit)**
1. Run `streamlit run app.py`
2. Upload your JD file (PDF/DOCX/TXT) in the sidebar
3. Upload one or more candidate resumes
4. Adjust scoring weights if needed (default: Semantic 50%, Skills 30%, Exp 12%, Edu 8%)
5. Click **Run Screening**
6. View ranked results, charts, skill gap heatmap, and download CSV report

**CLI Version**
1. Set `JD_PATH` and `RESUME_FOLDER` in `ai_resumeScreener.py`
2. Run:
```bash
python ai_resumeScreener.py
```
Reports saved as `screening_report.csv` and `screening_report.pdf`

---

## 📊 Scoring Breakdown

Each candidate is scored across 4 weighted dimensions:

| Dimension | Default Weight | What It Measures |
|---|---|---|
| Semantic Match | 50% | Contextual similarity between resume and JD using SBERT embeddings |
| Skill Coverage | 30% | % of JD-required skills found in resume |
| Experience | 12% | Years of experience extracted from resume text |
| Education | 8% | Highest education level detected |

**Tier Classification:**

| Score | Tier |
|---|---|
| ≥ 75% | 🟢 Strong Match |
| 55–74% | 🟡 Potential Fit |
| 35–54% | 🟠 Weak Fit |
| < 35% | 🔴 Not Suitable |

---

## 📦 Requirements

```
PyMuPDF
fpdf2
docx2txt
spacy
scikit-learn
sentence-transformers
pandas
openpyxl
streamlit
plotly
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🔮 Roadmap

- [ ] Multi-JD comparison (screen against multiple roles simultaneously)
- [ ] Resume parsing with section detection (Experience, Education, Skills sections)
- [ ] LLM-based feedback — tell candidates exactly what to improve
- [ ] Database integration — store and compare screening history
- [ ] Deploy to Streamlit Cloud for public access

---

## 👤 Author

**Karan M**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-linkedin)
- Email: mkaran030506@gmail.com

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

> ⭐ If this project helped you, give it a star on GitHub!
