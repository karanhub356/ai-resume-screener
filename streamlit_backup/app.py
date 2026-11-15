# ============================================================
# AI RESUME SCREENER — Streamlit Multi-page App
# Run: streamlit run app.py
# ============================================================
import streamlit as st
from utils.auth import check_password

# Page Config must be the first Streamlit command
st.set_page_config(
    page_title="AI Resume Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Password Protection Gate
if not check_password():
    st.stop()

# Custom CSS styling (applied globally)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Core Typography & Base */
    .stApp, .candidate-name, .candidate-rank, .score-big, .section-title, p, li, h1, h2, h3, h4, h5, h6, input, select, textarea {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.011em;
    }
    .stApp button, .stApp label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    /* Do not override icon fonts */
    .stApp [class*="material-symbols"], .stApp [class*="material-icons"], .stApp [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }

    /* Main background */
    .stApp {
        background: linear-gradient(to bottom, #0a0b0f 0%, #13141a 100%);
        color: #e8e9ec;
    }
    /* Metric cards */
    div[data-testid="metric-container"] {
        background: #16171d;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: border-color 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: rgba(99,102,241,0.3);
    }
    /* Tier badges */
    .badge-strong  { background: rgba(0, 230, 118, 0.12); color:#00e676; border: 1px solid rgba(0, 230, 118, 0.25); padding:4px 14px; border-radius:20px; font-size:13px; font-weight:600; }
    .badge-potential{ background: rgba(255, 214, 0, 0.12); color:#ffd600; border: 1px solid rgba(255, 214, 0, 0.25); padding:4px 14px; border-radius:20px; font-size:13px; font-weight:600; }
    .badge-weak    { background: rgba(255, 145, 0, 0.12); color:#ff9100; border: 1px solid rgba(255, 145, 0, 0.25); padding:4px 14px; border-radius:20px; font-size:13px; font-weight:600; }
    .badge-no      { background: rgba(255, 23, 68, 0.12); color:#ff1744; border: 1px solid rgba(255, 23, 68, 0.25); padding:4px 14px; border-radius:20px; font-size:13px; font-weight:600; }

    /* Candidate card */
    .candidate-card {
        background: #16171d;
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }
    .candidate-card:hover {
        border-color: rgba(99,102,241,0.3);
        box-shadow: 0 4px 16px rgba(99,102,241,0.1);
    }
    .candidate-rank {
        font-size: 28px;
        font-weight: 700;
        color: #6366f1;
        letter-spacing: -0.02em;
    }
    .candidate-name {
        font-size: 17px;
        font-weight: 600;
        color: #e8e9ec;
        letter-spacing: -0.01em;
    }
    .score-big {
        font-size: 36px;
        font-weight: 700;
        color: #6366f1;
        letter-spacing: -0.02em;
    }
    /* Skill chips */
    .chip-match   { display:inline-block; background: rgba(0, 230, 118, 0.08); color:#00e676; border: 1px solid rgba(0, 230, 118, 0.2); padding:4px 12px; border-radius:14px; font-size:12px; margin:3px; }
    .chip-missing { display:inline-block; background: rgba(255, 82, 82, 0.08); color:#ff5252; border: 1px solid rgba(255, 82, 82, 0.2); padding:4px 12px; border-radius:14px; font-size:12px; margin:3px; }

    /* Section headers */
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: #e8e9ec;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding-bottom: 12px;
        margin-bottom: 24px;
        letter-spacing: -0.01em;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0d0e12;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    /* Primary button override */
    div[data-testid="stSidebar"] button[kind="primary"] {
        background: #6366f1 !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        transition: background 0.2s ease !important;
    }
    div[data-testid="stSidebar"] button[kind="primary"]:hover {
        background: #5558e3 !important;
    }
    /* Style slider handles */
    div[role="slider"] {
        background-color: #6366f1 !important;
        border: 2px solid #ffffff !important;
    }
    /* Streamlit tabs override */
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 500 !important;
        color: #888 !important;
        border-bottom: 2px solid transparent !important;
        padding: 12px 20px !important;
        transition: color 0.2s ease, border-color 0.2s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        color: #a5b4fc !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #6366f1 !important;
        border-bottom: 2px solid #6366f1 !important;
        font-weight: 700 !important;
    }
    /* Progress bar color override */
    .stProgress > div > div { background-color: #6366f1; }

    /* Custom chatbot style overrides */
    div[data-testid="stChatMessage"] {
        border-radius: 16px;
        margin-bottom: 16px;
        padding: 14px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        border: 1px solid #1c1f2e;
    }
    div[data-testid="stChatMessage"][data-testid="stChatMessage-user"] {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(79, 70, 229, 0.15) 100%) !important;
        border-color: rgba(99, 102, 241, 0.3) !important;
    }
    div[data-testid="stChatMessage"][data-testid="stChatMessage-assistant"] {
        background: linear-gradient(135deg, #1b1e2a 0%, #12141c 100%) !important;
        border-color: #2d334a !important;
    }
    div[data-testid="stChatMessage"] div[data-testid="stChatMessageContent"] {
        color: #e3e4e9;
    }
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Define multi-page structure
home_page    = st.Page("pages/home.py",    title="Home",           icon="🏠", default=True)
screen_page  = st.Page("pages/screen.py",  title="Screen Resumes", icon="📂")
results_page = st.Page("pages/results.py", title="View Rankings",  icon="📊")
chat_page    = st.Page("pages/chat.py",    title="AI Recruiter Chat", icon="💬")

# Create Navigation
pg = st.navigation({
    "Main Menu": [home_page],
    "Recruitment Workflow": [screen_page, results_page, chat_page]
})

# Run Page Navigation
pg.run()
