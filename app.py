import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="SkillGap AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global Design System ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
[data-testid="stAppViewContainer"] { background: #070b14; }
.block-container { padding: 2.5rem 2.5rem 3rem 2.5rem !important; max-width: 1200px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0c1220 !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
section[data-testid="stSidebarContent"] { padding: 1.8rem 1.2rem !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.4) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.55) !important;
}
.stButton > button[kind="primary"]:active { transform: translateY(0px) !important; }
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.05) !important;
    color: #cbd5e1 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255,255,255,0.09) !important;
    border-color: rgba(255,255,255,0.2) !important;
    color: #f1f5f9 !important;
}
.stButton > button:disabled {
    opacity: 0.35 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    font-family: 'Inter', sans-serif !important;
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
    color: #f1f5f9 !important;
    font-size: 0.9rem !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: rgba(99,102,241,0.6) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    outline: none !important;
}
.stSelectbox > div > div { border-radius: 10px !important; }

/* ── Selectbox dropdown ── */
[data-baseweb="select"] > div {
    background: #0f1829 !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 10px !important;
}
[data-baseweb="popover"] { background: #0f1829 !important; border-radius: 10px !important; }
[role="listbox"] { background: #0f1829 !important; }
[role="option"]:hover { background: rgba(99,102,241,0.12) !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(99,102,241,0.04) !important;
    border: 1.5px dashed rgba(99,102,241,0.35) !important;
    border-radius: 12px !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(99,102,241,0.65) !important;
    background: rgba(99,102,241,0.07) !important;
}

/* ── Tabs ── */
div.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: rgba(255,255,255,0.025);
    padding: 5px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.05);
}
div.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 9px 20px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.01em !important;
}
div.stTabs [aria-selected="true"] {
    background: rgba(99,102,241,0.18) !important;
    color: #a5b4fc !important;
    font-weight: 600 !important;
}
div.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: #94a3b8 !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"]:hover {
    border-color: rgba(255,255,255,0.1) !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 20px 22px;
    transition: all 0.2s ease;
}
[data-testid="stMetric"]:hover {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.1);
    transform: translateY(-1px);
}
[data-testid="stMetricValue"] { color: #f1f5f9 !important; font-size: 2rem !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: #64748b !important; font-size: 0.78rem !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.06em; }

/* ── Alerts ── */
.stSuccess, .stWarning, .stError, .stInfo { border-radius: 10px !important; font-size: 0.875rem !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.06); }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.05) !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.18); }

/* ── Radio ── */
.stRadio label { font-size: 0.875rem !important; color: #94a3b8 !important; }
.stRadio [data-testid="stMarkdownContainer"] p { font-size: 0.875rem !important; }

/* ── Spinner ── */
.stSpinner > div { color: #a5b4fc !important; font-size: 0.875rem !important; }

/* ── Chat ── */
[data-testid="stChatInput"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.09) !important;
    border-radius: 12px !important;
}
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.02) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    margin-bottom: 10px !important;
}

/* ── Progress bar ── */
[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
    border-radius: 4px !important;
}
</style>
""", unsafe_allow_html=True)

from src.ui.dashboard import render_dashboard


def render_sidebar():
    with st.sidebar:
        # Brand
        st.markdown("""
            <div style="margin-bottom:2rem;">
                <div style="font-size:1.35rem;font-weight:800;color:#f1f5f9;
                            letter-spacing:-0.5px;margin-bottom:2px;">
                    ⚡ SkillGap AI
                </div>
                <div style="font-size:0.75rem;color:#334155;font-weight:500;
                            letter-spacing:0.05em;text-transform:uppercase;">
                    Career Intelligence
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # How it works
        st.markdown("""
            <div style="margin-bottom:1.5rem;">
                <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
                            text-transform:uppercase;color:#334155;margin-bottom:12px;">
                    How it works
                </div>
        """, unsafe_allow_html=True)

        steps = [
            ("01", "#6366f1", "Choose a role", "Pick from 6 industry presets or paste your own JD"),
            ("02", "#10b981", "Upload resume", "PDF or plain text — we handle both"),
            ("03", "#f59e0b", "Get analysis",  "AI maps your skills against market demand"),
            ("04", "#8b5cf6", "Follow roadmap","Close gaps with targeted micro-projects"),
        ]
        for num, color, title, desc in steps:
            st.markdown(f"""
                <div style="display:flex;gap:10px;margin-bottom:14px;align-items:flex-start;">
                    <div style="min-width:22px;height:22px;background:{color}22;
                                border:1px solid {color}55;border-radius:6px;
                                display:flex;align-items:center;justify-content:center;
                                font-size:0.65rem;font-weight:700;color:{color};
                                margin-top:1px;">{num}</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#cbd5e1;
                                    margin-bottom:1px;">{title}</div>
                        <div style="font-size:0.75rem;color:#475569;line-height:1.4;">{desc}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

        # Analysis summary (post-analysis)
        if st.session_state.get("analysis_complete"):
            score      = st.session_state.get("readiness_score", 0)
            gap_matrix = st.session_state.get("gap_matrix", [])
            high_p     = sum(1 for g in gap_matrix if g.get("is_high_priority"))
            missing    = sum(1 for g in gap_matrix if g["evidence_level"] == 0)
            color      = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"

            st.markdown(f"""
                <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);
                            border-radius:12px;padding:16px;margin-bottom:14px;">
                    <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
                                text-transform:uppercase;color:#334155;margin-bottom:10px;">
                        Last Analysis
                    </div>
                    <div style="font-size:2rem;font-weight:800;color:{color};
                                margin-bottom:4px;">{score}%</div>
                    <div style="font-size:0.75rem;color:#475569;margin-bottom:10px;">
                        Readiness Score
                    </div>
                    <div style="display:flex;gap:8px;">
                        <div style="flex:1;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.15);
                                    border-radius:8px;padding:8px;text-align:center;">
                            <div style="font-size:1.1rem;font-weight:700;color:#f87171;">{high_p}</div>
                            <div style="font-size:0.65rem;color:#64748b;margin-top:1px;">High Priority</div>
                        </div>
                        <div style="flex:1;background:rgba(100,116,139,0.08);border:1px solid rgba(100,116,139,0.15);
                                    border-radius:8px;padding:8px;text-align:center;">
                            <div style="font-size:1.1rem;font-weight:700;color:#94a3b8;">{missing}</div>
                            <div style="font-size:0.65rem;color:#64748b;margin-top:1px;">Missing</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if st.button("🔄  New Analysis", use_container_width=True, type="secondary"):
                for k in ["analysis_complete","gap_matrix","readiness_score",
                          "market_frequencies","roadmap","messages",
                          "resume_text","resume_text_staged","jds","selected_preset"]:
                    st.session_state.pop(k, None)
                st.rerun()
        else:
            st.markdown("""
                <div style="background:rgba(99,102,241,0.05);border:1px solid rgba(99,102,241,0.12);
                            border-radius:12px;padding:14px;font-size:0.78rem;color:#64748b;
                            line-height:1.5;text-align:center;">
                    Complete Setup &amp; Run to see your analysis summary here.
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Stack
        st.markdown("""
            <div style="font-size:0.68rem;font-weight:700;letter-spacing:0.1em;
                        text-transform:uppercase;color:#334155;margin-bottom:10px;">
                Powered by
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;">
                <div style="font-size:0.78rem;color:#475569;">🤖 Google Gemini 3.5 Flash Lite</div>
                <div style="font-size:0.78rem;color:#475569;">🗄️ Supabase</div>
                <div style="font-size:0.78rem;color:#475569;">📊 Plotly</div>
            </div>
        """, unsafe_allow_html=True)


def main():
    if not os.getenv("GEMINI_API_KEY"):
        st.warning("**GEMINI_API_KEY** not found — add it to your `.env` file.", icon="⚠️")

    render_sidebar()
    render_dashboard()


if __name__ == "__main__":
    main()
