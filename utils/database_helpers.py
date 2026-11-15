"""Database operations for screening results and candidates."""
import json
from database.db import get_db_connection

def save_job_description(title, company, location, jd_text, file_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO job_descriptions (title, company, location, jd_text, file_name) VALUES (?, ?, ?, ?, ?)", (title, company, location, jd_text, file_name))
    jd_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return jd_id

def upsert_candidate(email, phone, resume_text, file_name, education, experience_years):
    conn = get_db_connection()
    cursor = conn.cursor()
    if email:
        cursor.execute("SELECT id FROM candidates WHERE email = ?", (email,))
        existing = cursor.fetchone()
        if existing:
            cursor.execute("UPDATE candidates SET phone=?, resume_text=?, file_name=?, education=?, experience_years=? WHERE id=?", (phone, resume_text, file_name, education, experience_years, existing[0]))
            candidate_id = existing[0]
        else:
            cursor.execute("INSERT INTO candidates (email, phone, resume_text, file_name, education, experience_years) VALUES (?, ?, ?, ?, ?, ?)", (email, phone, resume_text, file_name, education, experience_years))
            candidate_id = cursor.lastrowid
    else:
        cursor.execute("INSERT INTO candidates (email, phone, resume_text, file_name, education, experience_years) VALUES (?, ?, ?, ?, ?, ?)", (email, phone, resume_text, file_name, education, experience_years))
        candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return candidate_id

def save_screening_result(jd_id, candidate_id, score, tier, breakdown, contact, llm_summary=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO screening_results (jd_id, candidate_id, score, tier, semantic_match, skill_score, exp_score, edu_score, matched_skills, missing_skills, contact_email, contact_phone, llm_summary) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (jd_id, candidate_id, score, tier, breakdown.get('semantic_match'), breakdown.get('skill_score'), breakdown.get('exp_score'), breakdown.get('edu_score'), json.dumps(breakdown.get('jd_skills_matched', [])), json.dumps(breakdown.get('skills_missing', [])), contact.get('email'), contact.get('phone'), json.dumps(llm_summary) if llm_summary else None))
    conn.commit()
    conn.close()

def get_historical_screenings(limit=20):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT jd.id, jd.title, jd.created_at, COUNT(sr.id) as candidate_count, AVG(sr.score) as avg_score FROM job_descriptions jd LEFT JOIN screening_results sr ON jd.id = sr.jd_id GROUP BY jd.id ORDER BY jd.created_at DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_results_for_jd(jd_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sr.*, c.file_name, c.resume_text, c.experience_years, c.education FROM screening_results sr JOIN candidates c ON sr.candidate_id = c.id WHERE sr.jd_id = ? ORDER BY sr.score DESC", (jd_id,))
    rows = cursor.fetchall()
    conn.close()
    results = []
    for i, row in enumerate(rows, 1):
        results.append({"rank": i, "filename": row["file_name"], "score": row["score"], "tier": row["tier"], "breakdown": {"semantic_match": row["semantic_match"] or 0, "skill_score": row["skill_score"] or 0, "exp_score": row["exp_score"] or 0, "edu_score": row["edu_score"] or 0, "experience_years": row["experience_years"] or 0, "education": row["education"] or "Not detected", "jd_skills_matched": json.loads(row["matched_skills"] or "[]"), "skills_missing": json.loads(row["missing_skills"] or "[]"), "all_skills_found": []}, "contact": {"email": row["contact_email"] or "—", "phone": row["contact_phone"] or "—"}, "resume_text": row["resume_text"][:1500] if row["resume_text"] else "", "llm_analysis": json.loads(row["llm_summary"]) if row["llm_summary"] else None})
    return results
