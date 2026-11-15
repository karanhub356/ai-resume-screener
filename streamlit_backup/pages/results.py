"""
Results page - Display candidate rankings, analytics, skill gaps, and data table.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.visualization import radar_chart, score_bar_chart, skill_heatmap, build_csv, tier_badge, score_color

def render():
    """Render the results page."""
    if "results" not in st.session_state:
        st.warning("⚠️ No screening results found. Please run screening first on the **Screen** page.")
        return

    results   = st.session_state["results"]
    jd_skills = st.session_state.get("jd_skills", [])
    jd_title  = st.session_state.get("jd_title", "Unknown Role")

    # Summary Metrics
    st.markdown(f"<div style='font-size:20px; color:#aaa; margin-bottom:16px;'>Results for: <b style='color:#7986cb;'>{jd_title}</b></div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Screened",   len(results))
    col2.metric("Strong Matches",   sum(1 for r in results if r["tier"] == "Strong Match"))
    col3.metric("Potential Fits",   sum(1 for r in results if r["tier"] == "Potential Fit"))
    col4.metric("Top Score",        f"{results[0]['score']}%" if results else "—")
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Rankings", "📊 Analytics", "🔥 Skill Gap", "📋 Table & Download"])
    
    # Tab 1: Rankings
    with tab1:
        st.markdown("<div class='section-title'>Candidate Rankings</div>", unsafe_allow_html=True)
        
        # Filter
        tier_filter = st.multiselect(
            "Filter by tier",
            ["Strong Match", "Potential Fit", "Weak Fit", "Not Suitable"],
            default=["Strong Match", "Potential Fit", "Weak Fit", "Not Suitable"]
        )
        filtered = [r for r in results if r["tier"] in tier_filter]
        
        for r in filtered:
            b = r["breakdown"]
            with st.container():
                st.markdown(f"""
                <div class="candidate-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div>
                            <span class="candidate-rank">#{r['rank']}</span>
                            <span class="candidate-name" style="margin-left:12px;">{r['filename']}</span>
                        </div>
                        <div style="text-align:right;">
                            <span class="score-big" style="color:{score_color(r['score'])};">{r['score']}%</span>
                            &nbsp;&nbsp;{tier_badge(r['tier'])}
                        </div>
                    </div>
                    <div style="color:#888; font-size:13px; margin-bottom:12px;">
                        📧 {r['contact']['email']} &nbsp;|&nbsp; 📞 {r['contact']['phone']}
                        &nbsp;|&nbsp; 🎓 {b['education']} &nbsp;|&nbsp; 💼 {b['experience_years']} yrs exp
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns([1, 1])
                with c1:
                    sub1, sub2, sub3, sub4 = st.columns(4)
                    sub1.metric("Semantic",   f"{b['semantic_match']}%")
                    sub2.metric("Skills",     f"{b['skill_score']}%")
                    sub3.metric("Experience", f"{b['exp_score']}%")
                    sub4.metric("Education",  f"{b['edu_score']}%")
                    
                    st.markdown("**✅ Matched Skills**")
                    if b["jd_skills_matched"]:
                        chips = " ".join([f'<span class="chip-match">{s}</span>' for s in b["jd_skills_matched"]])
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:#666;'>None matched</span>", unsafe_allow_html=True)
                    
                    st.markdown("**❌ Missing Skills**")
                    if b["skills_missing"]:
                        chips = " ".join([f'<span class="chip-missing">{s}</span>' for s in b["skills_missing"][:12]])
                        st.markdown(chips, unsafe_allow_html=True)
                    else:
                        st.markdown("<span style='color:#00e676;'>No gaps!</span>", unsafe_allow_html=True)
                
                with c2:
                    st.plotly_chart(radar_chart(b, r["filename"]), use_container_width=True, key=f"radar_{r['rank']}")
                
                # AI Analysis if available
                if r.get("llm_analysis"):
                    la = r["llm_analysis"]
                    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
                    st.markdown("**🤖 Gemini AI Candidate Summary**")
                    st.info(la.get("executive_summary", "No summary generated."))
                    
                    sc1, sc2 = st.columns(2)
                    with sc1:
                        st.markdown("**🌟 Key Strengths**")
                        for strg in la.get("strengths", []):
                            if strg and strg != "N/A":
                                st.markdown(f"- {strg}")
                    with sc2:
                        st.markdown("**⚠️ Gaps & Risks**")
                        for gap in la.get("gaps", []):
                            if gap and gap != "N/A":
                                st.markdown(f"- {gap}")
                    
                    st.markdown("**❓ Suggested Interview Questions**")
                    for q in la.get("interview_questions", []):
                        if q and q != "N/A":
                            st.markdown(f"- *{q}*")
                
                with st.expander("📄 View Extracted Resume Text"):
                    st.text(r.get("resume_text", "No text available."))
                
                st.divider()
    
    # Tab 2: Analytics
    with tab2:
        st.markdown("<div class='section-title'>Score Overview</div>", unsafe_allow_html=True)
        st.plotly_chart(score_bar_chart(results), use_container_width=True)
        
        st.markdown("<div class='section-title'>Score Distribution</div>", unsafe_allow_html=True)
        scores = [r["score"] for r in results]
        fig_hist = px.histogram(
            x=scores, nbins=10,
            labels={"x": "Fit Score (%)", "y": "Count"},
            color_discrete_sequence=["#5c6bc0"],
        )
        fig_hist.update_layout(
            paper_bgcolor="#1a1d27", plot_bgcolor="#13151f",
            font=dict(color="#ccc"),
            xaxis=dict(gridcolor="#2d3250"),
            yaxis=dict(gridcolor="#2d3250"),
            margin=dict(t=10),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Tab 3: Skill Gap Heatmap
    with tab3:
        st.markdown("<div class='section-title'>Skill Gap Heatmap</div>", unsafe_allow_html=True)
        st.markdown("<div style='color:#888; font-size:13px; margin-bottom:16px;'>Green = skill present &nbsp;|&nbsp; Red = skill missing</div>", unsafe_allow_html=True)
        fig_heat = skill_heatmap(results, jd_skills)
        if fig_heat:
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Not enough data to build heatmap.")
    
    # Tab 4: Table & Download
    with tab4:
        st.markdown("<div class='section-title'>Full Results Table</div>", unsafe_allow_html=True)
        table_data = []
        for r in results:
            table_data.append({
                "Rank":       r["rank"],
                "Resume":     r["filename"],
                "Score (%)":  r["score"],
                "Tier":       r["tier"],
                "Semantic":   f"{r['breakdown']['semantic_match']}%",
                "Skills":     f"{r['breakdown']['skill_score']}%",
                "Exp (yrs)":  r["breakdown"]["experience_years"],
                "Education":  r["breakdown"]["education"],
                "Email":      r["contact"]["email"],
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)
        
        # Download
        csv_data = build_csv(results)
        st.download_button(
            label     = "⬇️ Download CSV Report",
            data      = csv_data,
            file_name = "screening_report.csv",
            mime      = "text/csv",
            use_container_width=True,
        )


render()
