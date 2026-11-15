"""
Home page - Welcome screen and authentication gate.
"""
import streamlit as st
from utils.auth import check_password

def render():
    """Render the home page."""
    if not check_password():
        return

    st.markdown("""
    <div style="text-align:center; padding: 40px 20px;">
        <div style="font-size:48px; margin-bottom:20px;">🎯</div>
        <div style="font-size:32px; font-weight:700; color:#6366f1; margin-bottom:15px;">
            AI Resume Screener
        </div>
        <div style="font-size:16px; color:#888; margin-bottom:40px;">
            Intelligent resume screening powered by NLP and AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Features")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **📊 Smart Scoring**
        - Semantic similarity matching
        - Dynamic skill extraction with AI
        - Experience & education analysis
        - Customizable weight configuration

        **📈 Rich Analytics**
        - Candidate ranking dashboard
        - Radar charts for skill breakdown
        - Skill gap heatmaps
        - Export to CSV
        """)

    with col2:
        st.markdown("""
        **🤖 AI-Powered**
        - Gemini API integration
        - Dynamic skill taxonomy
        - AI candidate summaries
        - Strength/gap analysis

        **💬 RAG Chatbot**
        - Interactive recruiter assistant
        - Query candidate data
        - Conversation memory
        - Context-aware responses
        """)

    st.markdown("---")
    st.markdown("### 📝 How to Use")
    st.markdown("""
    1. **Navigate to Screen** → Upload your Job Description and candidate resumes
    2. **Configure Weights** → Adjust scoring criteria (semantic, skills, experience, education)
    3. **Run Screening** → Process all candidates and generate fit scores
    4. **View Results** → Explore rankings, analytics, and detailed candidate cards
    5. **Chat** → Ask questions about candidates using the AI chatbot
    """)

    st.info("👈 Use the sidebar to navigate between pages. Start with **Screen** to upload documents.")


render()
