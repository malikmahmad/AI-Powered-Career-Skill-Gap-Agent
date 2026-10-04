import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ── Radar Chart ───────────────────────────────────────────────────────────────

def render_candidate_radar_chart(gap_matrix):
    if not gap_matrix:
        st.info("No data available for the chart.")
        return

    top = sorted(gap_matrix, key=lambda x: x["frequency"], reverse=True)[:10]

    skills      = [item["skill"] for item in top]
    market_vals = [item["frequency"] for item in top]
    cand_vals   = [item["evidence_level"] * 50 for item in top]

    df = pd.DataFrame({
        "r":      market_vals + cand_vals,
        "theta":  skills + skills,
        "Entity": ["Market Demand"] * len(skills) + ["Your Profile"] * len(skills),
    })

    fig = px.line_polar(
        df, r="r", theta="theta", color="Entity",
        line_close=True,
        color_discrete_map={
            "Market Demand": "#6366f1",
            "Your Profile":  "#10b981",
        },
    )

    fig.update_traces(
        fill="toself", opacity=0.15, line=dict(width=2),
        selector=dict(name="Market Demand")
    )
    fig.update_traces(
        fill="toself", opacity=0.20, line=dict(width=2.5),
        selector=dict(name="Your Profile")
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                showticklabels=False,
                gridcolor="rgba(255,255,255,0.05)",
                linecolor="rgba(255,255,255,0.05)",
            ),
            angularaxis=dict(
                gridcolor="rgba(255,255,255,0.05)",
                linecolor="rgba(255,255,255,0.05)",
                tickfont=dict(color="#64748b", size=11, family="Inter"),
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="h", yanchor="bottom", y=-0.20,
            xanchor="center", x=0.5,
            font=dict(color="#94a3b8", size=12, family="Inter"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        height=400,
    )

    st.plotly_chart(fig, use_container_width=True)


# ── Readiness Gauge ───────────────────────────────────────────────────────────

def render_readiness_gauge(readiness_score: int):
    color = (
        "#10b981" if readiness_score >= 70
        else "#f59e0b" if readiness_score >= 40
        else "#ef4444"
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness_score,
        number={
            "suffix": "%",
            "font": {"size": 46, "color": color, "family": "Inter"},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "rgba(255,255,255,0.1)",
                "tickwidth": 1,
                "tickfont": {"color": "#334155", "size": 9, "family": "Inter"},
                "nticks": 6,
            },
            "bar": {"color": color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  40],  "color": "rgba(239,68,68,0.06)"},
                {"range": [40, 70],  "color": "rgba(245,158,11,0.06)"},
                {"range": [70, 100], "color": "rgba(16,185,129,0.06)"},
            ],
            "threshold": {
                "line": {"color": "rgba(255,255,255,0.15)", "width": 2},
                "thickness": 0.8, "value": 100,
            },
        },
        title={
            "text": "Readiness Score",
            "font": {"size": 13, "color": "#475569", "family": "Inter"},
        },
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=210,
        margin=dict(l=16, r=16, t=28, b=8),
    )

    st.plotly_chart(fig, use_container_width=True)


# ── Gap Matrix Table ──────────────────────────────────────────────────────────

def render_gap_matrix(gap_matrix):
    if not gap_matrix:
        st.info("No gap data available. Run the analysis first.")
        return

    level_map = {2: "✅ Demonstrated", 1: "⚠️ Theoretical", 0: "❌ Missing"}
    status_colors = {
        2: ("rgba(16,185,129,0.12)", "#34d399"),
        1: ("rgba(245,158,11,0.12)", "#fbbf24"),
        0: ("rgba(239,68,68,0.12)",  "#f87171"),
    }

    # ── Build HTML table ────────────────────────────────────────────────────
    header = """
        <tr>
            <th style="text-align:left;padding:10px 14px;font-size:0.78rem;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.04em;
                       border-bottom:1px solid rgba(255,255,255,0.08);">Skill</th>
            <th style="text-align:left;padding:10px 14px;font-size:0.78rem;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.04em;
                       border-bottom:1px solid rgba(255,255,255,0.08);">Status</th>
            <th style="text-align:right;padding:10px 14px;font-size:0.78rem;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.04em;
                       border-bottom:1px solid rgba(255,255,255,0.08);">Market %</th>
            <th style="text-align:left;padding:10px 14px;font-size:0.78rem;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.04em;
                       border-bottom:1px solid rgba(255,255,255,0.08);">Category</th>
            <th style="text-align:left;padding:10px 14px;font-size:0.78rem;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.04em;
                       border-bottom:1px solid rgba(255,255,255,0.08);">Evidence</th>
            <th style="text-align:center;padding:10px 14px;font-size:0.78rem;font-weight:600;
                       color:#64748b;text-transform:uppercase;letter-spacing:0.04em;
                       border-bottom:1px solid rgba(255,255,255,0.08);">Priority</th>
        </tr>
    """

    rows_html = ""
    for row in gap_matrix:
        ev      = row.get("evidence_level", 0)
        status  = level_map.get(ev, "Unknown")
        bg, clr = status_colors.get(ev, ("transparent", "#94a3b8"))
        freq    = row.get("frequency", 0)
        is_hp   = row.get("is_high_priority", False)
        priority_badge = (
            '<span style="background:rgba(239,68,68,0.15);color:#f87171;'
            'padding:2px 8px;border-radius:20px;font-size:0.72rem;font-weight:600;">🚨 High</span>'
            if is_hp else
            '<span style="color:#334155;font-size:0.82rem;">—</span>'
        )

        rows_html += f"""
            <tr style="border-bottom:1px solid rgba(255,255,255,0.04);
                       transition:background 0.15s ease;"
                onmouseover="this.style.background='rgba(255,255,255,0.025)';"
                onmouseout="this.style.background='transparent';">
                <td style="padding:10px 14px;font-size:0.85rem;font-weight:600;color:#f1f5f9;">
                    {row.get('skill', '')}</td>
                <td style="padding:10px 14px;">
                    <span style="background:{bg};color:{clr};padding:3px 10px;
                                 border-radius:6px;font-size:0.78rem;font-weight:500;">
                        {status}
                    </span>
                </td>
                <td style="padding:10px 14px;text-align:right;font-size:0.85rem;
                           font-weight:600;color:{clr};">{freq}%</td>
                <td style="padding:10px 14px;font-size:0.82rem;color:#94a3b8;">
                    {row.get('category', '')}</td>
                <td style="padding:10px 14px;font-size:0.8rem;color:#64748b;max-width:280px;
                           overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">
                    {row.get('justification', '')}</td>
                <td style="padding:10px 14px;text-align:center;">{priority_badge}</td>
            </tr>
        """

    table_html = f"""
        <div style="overflow-x:auto;border-radius:12px;
                    border:1px solid rgba(255,255,255,0.06);">
            <table style="width:100%;border-collapse:collapse;
                         background:rgba(255,255,255,0.015);">
                <thead>{header}</thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)

    # ── High-priority cards ───────────────────────────────────────────────────
    high_p = [g for g in gap_matrix if g.get("is_high_priority")]
    if high_p:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <h3 style="font-size:1rem;font-weight:700;color:#f1f5f9;margin-bottom:6px;">
                🚨 High-Priority Gaps
            </h3>
            <p style="color:#475569;font-size:0.8rem;margin-bottom:16px;">
                Skills with ≥50% market demand that aren't yet demonstrated in your profile.
                These should be your first priority.
            </p>
        """, unsafe_allow_html=True)

        cols = st.columns(min(len(high_p), 3))
        for i, row in enumerate(high_p):
            status_str = level_map.get(row.get("evidence_level", 0), "Unknown")
            clr = "#f59e0b" if row.get("evidence_level") == 1 else "#ef4444"
            with cols[i % 3]:
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.025);
                                border:1px solid rgba(255,255,255,0.07);
                                border-top:2px solid {clr};
                                border-radius:12px;padding:16px 18px;margin-bottom:10px;
                                transition:all 0.2s ease;">
                        <div style="font-weight:700;color:#f1f5f9;font-size:0.9rem;
                                    margin-bottom:6px;">{row['skill']}</div>
                        <div style="display:flex;align-items:center;justify-content:space-between;
                                    margin-bottom:8px;">
                            <span style="font-size:0.75rem;color:#64748b;">Market demand</span>
                            <span style="font-size:0.82rem;font-weight:700;color:{clr};">
                                {row.get('frequency', 0)}%
                            </span>
                        </div>
                        <div style="background:rgba(255,255,255,0.04);border-radius:6px;
                                    padding:5px 10px;font-size:0.75rem;color:#64748b;">
                            {status_str}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
