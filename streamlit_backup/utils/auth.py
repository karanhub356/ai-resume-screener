import os
import streamlit as st

def check_password():
    """Returns True if the user has correct password, False otherwise."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        correct_password = os.environ.get("APP_PASSWORD", "admin123")
        try:
            if hasattr(st, 'secrets') and "APP_PASSWORD" in st.secrets:
                correct_password = st.secrets["APP_PASSWORD"]
        except:
            pass

        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px;">
            <div style="font-size:48px; margin-bottom:20px;">🔐</div>
            <div style="font-size:28px; font-weight:700; color:#6366f1; margin-bottom:10px;">AI Resume Screener</div>
            <div style="font-size:14px; color:#888; margin-bottom:30px;">Enter password to access</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed", placeholder="Enter password...")

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            with col2:
                st.error("❌ Incorrect password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px;">
            <div style="font-size:48px; margin-bottom:20px;">🔐</div>
            <div style="font-size:28px; font-weight:700; color:#6366f1; margin-bottom:10px;">AI Resume Screener</div>
            <div style="font-size:14px; color:#888; margin-bottom:30px;">Enter password to access</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Password", type="password", on_change=password_entered, key="password", label_visibility="collapsed", placeholder="Enter password...")
            st.error("❌ Incorrect password")
        return False
    else:
        return True
