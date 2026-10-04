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

    df = pd.DataFrame(gap_matrix)
    df["Status"] = df["evidence_level"].map(level_map)
    df["Priority"] = df["is_high_priority"].apply(lambda v: "🚨 High" if v else "—")

    display_df = df[["skill", "Status", "frequency", "category", "justification", "Priority"]].copy()
    display_df.columns = ["Skill", "Status", "Market %", "Category", "Evidence", "Priority"]
    display_df["Market %"] = display_df["Market %"].apply(lambda v: f"{v}%")

    # Plain dataframe — no Styler (Styler causes React error #185 on Streamlit Cloud)
    st.dataframe(
        display_df,
        use_container_width=True,
        height=min(400, 45 * len(display_df) + 40),
        hide_index=True,
        column_config={
            "Skill":    st.column_config.TextColumn("Skill", width="medium"),
            "Status":   st.column_config.TextColumn("Status", width="small"),
            "Market %": st.column_config.TextColumn("Market %", width="small"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
            "Evidence": st.column_config.TextColumn("Evidence", width="large"),
            "Priority": st.column_config.TextColumn("Priority", width="small"),
        },
    )

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
                                border-radius:12px;padding:16px 18px;margin-bottom:10px;">
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
