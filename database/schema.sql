CREATE TABLE IF NOT EXISTS job_descriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT,
    location TEXT,
    jd_text TEXT NOT NULL,
    file_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    phone TEXT,
    resume_text TEXT,
    file_name TEXT,
    education TEXT,
    experience_years INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS screening_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jd_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    score REAL NOT NULL,
    tier TEXT NOT NULL,
    semantic_match REAL,
    skill_score REAL,
    exp_score REAL,
    edu_score REAL,
    matched_skills TEXT,
    missing_skills TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    llm_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (jd_id) REFERENCES job_descriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_results_jd ON screening_results(jd_id);