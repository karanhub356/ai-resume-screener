"""
Visualization and reporting utilities.
Contains Plotly charts, UI helpers, and CSV export functions.
"""
import pandas as pd
import plotly.graph_objects as go

def tier_badge(tier: str) -> str:
    """Return HTML badge for tier classification."""
    classes = {
        "Strong Match":  "badge-strong",
        "Potential Fit": "badge-potential",
        "Weak Fit":      "badge-weak",
        "Not Suitable":  "badge-no",
    }
    return f'<span class="{classes.get(tier, "badge-no")}">{tier}</span>'

def score_color(score: float) -> str:
    """Return color code based on score threshold."""
    if score >= 75: return "#00e676"
    if score >= 55: return "#ffd600"
    if score >= 35: return "#ff9100"
    return "#ff1744"

def radar_chart(breakdown: dict, name: str):
    """Create Plotly radar chart for candidate skill breakdown."""
    categories = ["Semantic", "Skills", "Experience", "Education"]
    values     = [
        breakdown["semantic_match"],
        breakdown["skill_score"],
        breakdown["exp_score"],
        breakdown["edu_score"],
    ]
    fig = go.Figure(go.Scatterpolar(
        r      = values + [values[0]],
        theta  = categories + [categories[0]],
        fill   = "toself",
        fillcolor = "rgba(92, 107, 192, 0.2)",
        line   = dict(color="#7986cb", width=2),
        name   = name,
    ))
    fig.update_layout(
        polar=dict(
            bgcolor     = "#1a1d27",
            radialaxis  = dict(visible=True, range=[0, 100], color="#555", gridcolor="#2d3250"),
            angularaxis = dict(color="#aaa", gridcolor="#2d3250"),
        ),
        paper_bgcolor = "#1a1d27",
        plot_bgcolor  = "#1a1d27",
        font          = dict(color="#ccc"),
        margin        = dict(t=20, b=20, l=20, r=20),
        showlegend    = False,
        height        = 280,
    )
    return fig

def score_bar_chart(results):
    """Create horizontal bar chart showing candidate scores ranked."""
    names  = [r["filename"].replace(".pdf","").replace(".docx","") for r in results]
    scores = [r["score"] for r in results]
    colors = [score_color(s) for s in scores]
    fig = go.Figure(go.Bar(
        x           = scores,
        y           = names,
        orientation = "h",
        marker_color= colors,
        text        = [f"{s}%" for s in scores],
        textposition= "outside",
        textfont    = dict(color="#ccc", size=13),
    ))
    fig.update_layout(
        paper_bgcolor = "#1a1d27",
        plot_bgcolor  = "#13151f",
        font          = dict(color="#ccc"),
        xaxis         = dict(range=[0, 110], color="#555", gridcolor="#2d3250", title="Fit Score (%)"),
        yaxis         = dict(color="#ccc", autorange="reversed"),
        margin        = dict(t=10, b=10, l=10, r=60),
        height        = max(200, len(results) * 55),
    )
    return fig

def skill_heatmap(results, jd_skills):
    """Create skill gap heatmap showing which skills each candidate has."""
    if not jd_skills or not results:
        return None
    candidates = [r["filename"].replace(".pdf","").replace(".docx","") for r in results]
    matrix     = []
    for r in results:
        matched_lower = [m.lower() for m in r["breakdown"]["all_skills_found"]]
        row = [1 if s.lower() in matched_lower else 0 for s in jd_skills]
        matrix.append(row)
    fig = go.Figure(go.Heatmap(
        z           = matrix,
        x           = jd_skills,
        y           = candidates,
        colorscale  = [[0, "#2d0a0a"], [1, "#0d3b2e"]],
        showscale   = False,
        text        = [["✓" if v else "✗" for v in row] for row in matrix],
        texttemplate= "%{text}",
        textfont    = dict(size=14),
    ))
    fig.update_layout(
        paper_bgcolor = "#1a1d27",
        plot_bgcolor  = "#1a1d27",
        font          = dict(color="#ccc", size=11),
        xaxis         = dict(tickangle=-40, color="#aaa", side="bottom"),
        yaxis         = dict(color="#ccc"),
        margin        = dict(t=10, b=120, l=10, r=10),
        height        = max(250, len(results) * 60 + 140),
    )
    return fig

def build_csv(results):
    """Export screening results to CSV bytes for download."""
    rows = []
    for r in results:
        rows.append({
            "Rank":               r["rank"],
            "Resume":             r["filename"],
            "Fit Score (%)":      r["score"],
            "Tier":               r["tier"],
            "Semantic Match (%)": r["breakdown"]["semantic_match"],
            "Skill Score (%)":    r["breakdown"]["skill_score"],
            "Experience (yrs)":   r["breakdown"]["experience_years"],
            "Education":          r["breakdown"]["education"],
            "JD Skills Matched":  ", ".join(r["breakdown"]["jd_skills_matched"]),
            "Skills Missing":     ", ".join(r["breakdown"]["skills_missing"]),
            "Email":              r["contact"]["email"],
            "Phone":              r["contact"]["phone"],
        })
    return pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
