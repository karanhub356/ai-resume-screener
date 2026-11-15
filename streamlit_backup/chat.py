"""
Chat page - RAG Recruiter Chatbot with conversation memory.
"""
import streamlit as st
from utils.gemini_utils import call_gemini_api

def render():
    """Render the chat page."""
    if "results" not in st.session_state:
        st.warning("⚠️ No screening results found. Please run screening first on the **Screen** page.")
        return

    results   = st.session_state["results"]
    jd_skills = st.session_state.get("jd_skills", [])
    jd_title  = st.session_state.get("jd_title", "Unknown Role")

    st.markdown("<div class='section-title'>💬 AI Recruiter Chat</div>", unsafe_allow_html=True)

    g_key = st.session_state.get("gemini_api_key", "")
    if not g_key:
        st.info("💡 To enable the AI Recruiter Chat, enter your Gemini API Key in the sidebar on the **Screen** page.")
        return

    st.markdown("<div style='color:#888; font-size:13px; margin-bottom:16px;'>Ask questions about your uploaded resumes (e.g., 'Compare the top 2 candidates' or 'Which candidate has experience with Python?')</div>", unsafe_allow_html=True)
    
    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    
    # Build context from resumes (only once, cached in session)
    if "chat_context" not in st.session_state:
        context_parts = []
        for candidate in results:
            la = candidate.get("llm_analysis") or {}
            summary_text = la.get("executive_summary", "No AI summary available.")
            context_parts.append(
                f"Candidate: {candidate['filename']}\n"
                f"Rank: {candidate['rank']}\n"
                f"Fit Score: {candidate['score']}%\n"
                f"Tier: {candidate['tier']}\n"
                f"Email: {candidate['contact']['email']}\n"
                f"Phone: {candidate['contact']['phone']}\n"
                f"Matched Skills: {', '.join(candidate['breakdown']['jd_skills_matched'])}\n"
                f"Missing Skills: {', '.join(candidate['breakdown']['skills_missing'])}\n"
                f"AI Fit Summary: {summary_text}\n"
                f"Resume Content (Excerpt):\n{candidate.get('resume_text', '')[:1500]}\n"
                f"===================================="
            )
        context_str = "\n".join(context_parts)
        
        system_instruction = f"""
You are an AI recruiter assistant helping a hiring manager analyze a batch of resumes against a job description.
Use the candidate details and resumes provided below to answer the user's questions accurately, citing specific candidates when relevant. Keep your answers professional, concise, and structured.

Job Description Title: {jd_title}
Job Description Skills Needed: {', '.join(jd_skills)}

Candidate Data and Resume Excerpts:
{context_str}
"""
        st.session_state["chat_context"] = system_instruction
    
    system_instruction = st.session_state["chat_context"]
    
    # Display chat messages
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if chat_prompt := st.chat_input("Ask a question about the candidates..."):
        with st.chat_message("user"):
            st.write(chat_prompt)
        st.session_state["chat_history"].append({"role": "user", "content": chat_prompt})
        
        with st.spinner("AI is analyzing the resume pool..."):
            # Call Gemini API with conversation history for multi-turn memory
            response_text = call_gemini_api(
                api_key=g_key,
                system_instruction=system_instruction,
                prompt=chat_prompt,
                conversation_history=st.session_state["chat_history"][:-1],  # Exclude the just-added user message
                json_mode=False
            )
            if not response_text:
                response_text = "Sorry, I encountered an error communicating with the AI service. Please verify your API Key and network connection."
        
        with st.chat_message("assistant"):
            st.write(response_text)
        st.session_state["chat_history"].append({"role": "assistant", "content": response_text})
        
        # Rerun to update chat display
        st.rerun()


render()
