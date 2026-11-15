"""
Screen page - Upload Job Description and Resumes, configure weights, run screening.
"""
import streamlit as st
import os
import re
from spacy.matcher import PhraseMatcher
from utils.nlp_utils import (
    load_models, build_matcher, extract_text, extract_skills,
    extract_experience_years, extract_education, extract_contact_info,
    get_similarity, calculate_fit_score, classify_tier, SKILLS_DB
)
from utils.gemini_utils import extract_skills_from_jd_with_ai, get_candidate_llm_analysis

def render():
    """Render the screen page."""
    st.markdown("### 📂 Upload & Configure")

    # Sidebar: Upload
    with st.sidebar:
        st.markdown("### 📂 Upload Files")
        jd_file = st.file_uploader(
            "Job Description",
            type=["pdf", "docx", "txt"],
            help="Upload the JD you're hiring for"
        )
        resume_files = st.file_uploader(
            "Resumes",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            help="Upload one or more candidate resumes"
        )
        
        st.divider()
        
        with st.expander("🔑 Gemini API (Optional)"):
            env_key = os.environ.get("GEMINI_API_KEY", os.environ.get("GOOGLE_API_KEY", ""))
            gemini_api_key = st.text_input(
                "API Key",
                value=env_key,
                type="password",
                help="Enter your Gemini API Key to enable AI summaries, chat, and interview questions."
            )
            st.session_state["gemini_api_key"] = gemini_api_key
        
        st.markdown("### ⚙️ Score Weights")
        w_semantic = st.slider("Semantic Match", 0, 100, 50)
        w_skills   = st.slider("Skill Coverage", 0, 100, 30)
        w_exp      = st.slider("Experience",     0, 100, 12)
        w_edu      = st.slider("Education",      0, 100, 8)
        
        total_w = w_semantic + w_skills + w_exp + w_edu
        
        # Display weight status
        if total_w == 100:
            st.success(f"✓ Weights sum to {total_w}")
        else:
            st.info(f"Weights sum to {total_w} → Auto-normalized to 100%")
            
            # Auto-normalize weights
            if total_w > 0:
                w_semantic_norm = (w_semantic / total_w) * 100
                w_skills_norm   = (w_skills / total_w) * 100
                w_exp_norm      = (w_exp / total_w) * 100
                w_edu_norm      = (w_edu / total_w) * 100
            else:
                w_semantic_norm = w_skills_norm = w_exp_norm = w_edu_norm = 0
            
            st.caption(f"Normalized: {w_semantic_norm:.1f}% | {w_skills_norm:.1f}% | {w_exp_norm:.1f}% | {w_edu_norm:.1f}%")
        
        st.divider()
        run_btn = st.button("🚀 Run Screening", use_container_width=True, type="primary")
    
    # Main Area
    if not jd_file or not resume_files:
        st.markdown("""
        <div style="text-align:center; padding:80px 0; color:#444;">
            <div style="font-size:56px;">📄</div>
            <div style="font-size:20px; margin-top:12px;">Upload a JD and resumes in the sidebar to get started</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    if run_btn:
        if jd_file and resume_files:
            with st.spinner("Loading models..."):
                nlp, sbert = load_models()
                matcher    = build_matcher(nlp)
            
            # Extract JD
            with st.spinner("Reading JD..."):
                jd_text   = extract_text(jd_file, jd_file.name)
                jd_title_match = re.search(r'Job Title[:\s]+(.+)', jd_text, re.IGNORECASE)
                jd_title  = jd_title_match.group(1).strip() if jd_title_match else "Unknown Role"
                
                # Dynamic skill extraction with Gemini AI (if API key present)
                g_key = st.session_state.get("gemini_api_key", "")
                if g_key:
                    with st.spinner("🤖 Extracting required skills from JD using AI..."):
                        ai_extracted_skills = extract_skills_from_jd_with_ai(g_key, jd_text)
                        if ai_extracted_skills:
                            # Combine AI-extracted skills with base taxonomy for comprehensive matching
                            combined_skills = list(set(SKILLS_DB + ai_extracted_skills))
                            # Rebuild matcher with dynamic skills
                            matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
                            patterns = [nlp.make_doc(s.lower()) for s in combined_skills]
                            matcher.add("SKILLS", patterns)
                            st.success(f"✅ AI extracted {len(ai_extracted_skills)} skills from JD")
                
                # Extract skills from JD using the (possibly enhanced) matcher
                jd_skills = extract_skills(jd_text, nlp, matcher)
            
            # Auto-normalize weights
            if total_w > 0:
                w_semantic_norm = (w_semantic / total_w) * 100
                w_skills_norm   = (w_skills / total_w) * 100
                w_exp_norm      = (w_exp / total_w) * 100
                w_edu_norm      = (w_edu / total_w) * 100
            else:
                w_semantic_norm = w_skills_norm = w_exp_norm = w_edu_norm = 25.0
            
            weights = {
                'w_semantic': w_semantic_norm,
                'w_skills': w_skills_norm,
                'w_exp': w_exp_norm,
                'w_edu': w_edu_norm
            }
            
            # Process resumes
            results = []
            progress = st.progress(0, text="Screening resumes...")
            g_key = st.session_state.get("gemini_api_key", "")
            
            for i, rf in enumerate(resume_files):
                progress.progress((i + 1) / len(resume_files), text=f"Processing {rf.name}...")
                resume_text = extract_text(rf, rf.name)
                if not resume_text.strip():
                    continue
                
                sim              = get_similarity(resume_text, jd_text, sbert)
                matched_skills   = extract_skills(resume_text, nlp, matcher)
                exp_years        = extract_experience_years(resume_text)
                education        = extract_education(resume_text)
                contact          = extract_contact_info(resume_text)
                
                score, breakdown = calculate_fit_score(sim, matched_skills, jd_skills, exp_years, education, weights)
                tier = classify_tier(score)
                
                # If Gemini is active, run LLM analysis
                llm_analysis = None
                if g_key:
                    progress.progress((i + 1) / len(resume_files), text=f"AI analyzing {rf.name}...")
                    llm_analysis = get_candidate_llm_analysis(g_key, resume_text, jd_text)
                
                results.append({
                    "filename": rf.name,
                    "score": score,
                    "tier": tier,
                    "breakdown": breakdown,
                    "contact": contact,
                    "resume_text": resume_text,
                    "llm_analysis": llm_analysis
                })
            
            progress.empty()
            
            # Sort and rank
            results = sorted(results, key=lambda x: x["score"], reverse=True)
            for i, r in enumerate(results, 1):
                r["rank"] = i
            
            # Save to session state
            st.session_state["results"]   = results
            st.session_state["jd_skills"] = jd_skills
            st.session_state["jd_title"]  = jd_title
            st.session_state["jd_text"]   = jd_text
            
            st.success(f"✅ Screening complete! Processed {len(results)} candidates.")
            st.info("👉 Navigate to **Results** page to view detailed rankings and analytics.")
    
    # Show status if results exist
    if "results" in st.session_state:
        results = st.session_state["results"]
        jd_title = st.session_state.get("jd_title", "Unknown Role")
        
        st.markdown("---")
        st.markdown(f"### 📊 Last Screening Results")
        st.markdown(f"**Role:** {jd_title}")
        st.markdown(f"**Candidates Processed:** {len(results)}")
        st.markdown(f"**Top Score:** {results[0]['score']}%" if results else "—")
        st.info("👉 Go to **Results** page to explore detailed analytics.")


render()
