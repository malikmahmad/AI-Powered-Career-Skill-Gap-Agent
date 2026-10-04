import streamlit as st
import json
import os
import uuid

from src.services.gemini_service import extract_candidate_skills, extract_market_skills
from src.services.gap_engine import calculate_market_frequencies, analyze_gaps
from src.ui.charts import render_candidate_radar_chart, render_readiness_gauge, render_gap_matrix
from src.services.roadmap_service import generate_roadmap, get_chat_response
from src.services.export_service import gap_matrix_to_csv
from src.db.supabase_client import save_analysis


# ── Helpers ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def load_presets():
    preset_path = os.path.join(os.path.dirname(__file__), "..", "data", "presets.json")
    try:
        with open(preset_path, "r", encoding="utf-8") as f:
            return json.load(f).get("presets", [])
    except Exception as e:
        st.error(f"Failed to load presets: {e}")
        return []


def process_analysis():
    resume_text = st.session_state.get("resume_text", "")
    jds         = st.session_state.get("jds", [])

    bar = st.progress(0, text="Starting analysis…")
    bar.progress(10, text="Extracting skills from your resume…")
    cand_skills = extract_candidate_skills(resume_text)

    bar.progress(42, text="Analysing job market requirements…")
    jd_analyses = extract_market_skills(jds)

    bar.progress(72, text="Computing skill gap matrix…")
    freq   = calculate_market_frequencies(jd_analyses)
    result = analyze_gaps(cand_skills, freq)

    bar.progress(92, text="Saving results…")
    st.session_state["gap_matrix"]         = result["gap_matrix"]
    st.session_state["readiness_score"]    = result["readiness_score"]
    st.session_state["market_frequencies"] = freq
    st.session_state["analysis_complete"]  = True

    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    try:
        save_analysis(
            st.session_state["user_id"],
            st.session_state.get("user_email", "anonymous"),
            {"resume": resume_text[:500] + "…",
             "target_role": st.session_state.get("selected_preset", "custom")},
            result["gap_matrix"],
        )
    except Exception:
        pass

    st.session_state.pop("roadmap", None)
    st.session_state["messages"] = []
    bar.progress(100, text="Done!")
    bar.empty()


# ── Dashboard ─────────────────────────────────────────────────────────────────

def render_dashboard():

    # ── Hero ─────────────────────────────────────────────────────────────────
    st.markdown("""
        <div style="margin-bottom:2.5rem;">
            <div style="display:inline-flex;align-items:center;gap:8px;
                        background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.2);
                        border-radius:20px;padding:4px 14px;margin-bottom:16px;">
                <div style="width:6px;height:6px;background:#6366f1;border-radius:50%;
                            box-shadow:0 0 6px #6366f1;"></div>
                <span style="font-size:0.72rem;font-weight:600;color:#a5b4fc;
                             letter-spacing:0.08em;text-transform:uppercase;">
                    AI-Powered · Real Market Data
                </span>
            </div>
            <h1 style="font-size:2.4rem;font-weight:800;color:#f8fafc;
                       letter-spacing:-1px;margin:0 0 10px 0;line-height:1.15;">
                Career Skill Gap Analyzer
            </h1>
            <p style="color:#64748b;font-size:1rem;margin:0;max-width:560px;line-height:1.6;">
                Pick a target role, upload your resume, and get an AI-powered gap analysis
                with a personalised roadmap — in under a minute.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # ── Score banner (post-analysis) ──────────────────────────────────────────
    if st.session_state.get("analysis_complete"):
        score = st.session_state.get("readiness_score", 0)
        clr   = "#10b981" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
        bg    = "rgba(16,185,129,0.07)" if score >= 70 else "rgba(245,158,11,0.07)" if score >= 40 else "rgba(239,68,68,0.07)"
        lbl   = "Strong match" if score >= 70 else "Moderate match" if score >= 40 else "Significant gaps"
        role  = next((p["name"] for p in load_presets()
                      if p["id"] == st.session_state.get("selected_preset")), "Custom JD")
        st.markdown(f"""
            <div style="background:{bg};border:1px solid rgba(255,255,255,0.07);
                        border-left:3px solid {clr};border-radius:12px;
                        padding:16px 24px;margin-bottom:2rem;
                        display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div style="display:flex;align-items:center;gap:16px;">
                    <span style="font-weight:800;color:{clr};font-size:2rem;line-height:1;">{score}%</span>
                    <div>
                        <div style="font-size:0.9rem;font-weight:600;color:#f1f5f9;">{lbl}</div>
                        <div style="font-size:0.78rem;color:#64748b;margin-top:1px;">Target: {role}</div>
                    </div>
                </div>
                <div style="font-size:0.8rem;color:#475569;">
                    See full breakdown in the tabs below ↓
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚙️  Setup & Run",
        "📊  Results",
        "🔍  Skill Gaps",
        "🗺️  Roadmap & Chat",
    ])

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 1 — Setup & Run
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns([1, 1], gap="large")

        # ── LEFT: Target Role ─────────────────────────────────────────────────
        with left:
            _step_header("1", "#6366f1", "#a5b4fc",
                         "Target Role",
                         "Choose from 6 industry presets or paste your own job description.")

            presets    = load_presets()
            preset_map = {p["name"]: p for p in presets}
            options    = ["— select a role —"] + [p["name"] for p in presets] + ["✏️  Paste my own JD"]

            saved_name  = next((p["name"] for p in presets
                                if p["id"] == st.session_state.get("selected_preset")), None)
            default_idx = options.index(saved_name) if saved_name and saved_name in options else 0

            chosen = st.selectbox("Role", options, index=default_idx,
                                  label_visibility="collapsed")

            if chosen == "— select a role —":
                st.markdown("""
                    <div style="background:rgba(255,255,255,0.02);border:1px dashed rgba(255,255,255,0.07);
                                border-radius:10px;padding:20px;text-align:center;margin-top:8px;">
                        <div style="font-size:1.4rem;margin-bottom:6px;">👆</div>
                        <div style="font-size:0.82rem;color:#475569;">
                            Select a role from the dropdown above
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            elif chosen == "✏️  Paste my own JD":
                st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
                custom_jd = st.text_area(
                    "Job description",
                    height=220,
                    placeholder="Paste the full job description here — the AI will extract required skills automatically.",
                    label_visibility="collapsed",
                )
                if custom_jd and custom_jd.strip():
                    st.session_state["jds"]             = [custom_jd.strip()]
                    st.session_state["selected_preset"] = "custom"
                    st.success("✓ Custom JD ready")

            else:
                preset = preset_map[chosen]
                if st.session_state.get("selected_preset") != preset["id"]:
                    st.session_state["selected_preset"] = preset["id"]
                    st.session_state["jds"]             = preset["job_descriptions"]

                n = len(preset["job_descriptions"])
                st.markdown(f"""
                    <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.18);
                                border-radius:12px;padding:16px 20px;margin-top:10px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;
                                    margin-bottom:6px;">
                            <span style="font-size:0.88rem;font-weight:700;color:#a5b4fc;">
                                ✓ {chosen}
                            </span>
                            <span style="background:rgba(99,102,241,0.15);color:#818cf8;
                                         font-size:0.7rem;font-weight:600;padding:2px 8px;
                                         border-radius:20px;">{n} JDs</span>
                        </div>
                        <div style="font-size:0.78rem;color:#475569;">
                            Market baseline loaded — ready to analyse.
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander("Preview job descriptions"):
                    for i, jd in enumerate(preset["job_descriptions"], 1):
                        st.markdown(f"**JD {i}**")
                        st.markdown(jd)
                        if i < n:
                            st.divider()

        # ── RIGHT: Resume ─────────────────────────────────────────────────────
        with right:
            _step_header("2", "#10b981", "#34d399",
                         "Your Resume",
                         "Upload a PDF or paste your resume text.")

            resume_mode = st.radio(
                "Input",
                ["📄  Upload PDF", "📋  Paste text"],
                horizontal=True,
                label_visibility="collapsed",
            )

            if resume_mode == "📄  Upload PDF":
                uploaded = st.file_uploader(
                    "Resume PDF", type=["pdf"], label_visibility="collapsed"
                )
                if uploaded:
                    import pypdf
                    try:
                        reader = pypdf.PdfReader(uploaded)
                        extracted = "\n".join(
                            p.extract_text() or "" for p in reader.pages
                        ).strip()
                        # Persist immediately to session state — survives reruns
                        st.session_state["resume_text_staged"] = extracted
                        st.markdown(f"""
                            <div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.2);
                                        border-radius:10px;padding:12px 16px;margin-top:10px;
                                        display:flex;align-items:center;gap:10px;">
                                <span style="font-size:1.1rem;">✅</span>
                                <div>
                                    <div style="font-size:0.85rem;font-weight:600;color:#6ee7b7;">
                                        PDF extracted successfully
                                    </div>
                                    <div style="font-size:0.75rem;color:#64748b;margin-top:1px;">
                                        {len(reader.pages)} page{"s" if len(reader.pages)!=1 else ""} · {len(extracted):,} characters
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        with st.expander("Preview extracted text"):
                            st.text(extracted[:2000] + ("…" if len(extracted) > 2000 else ""))
                    except Exception as e:
                        st.error(f"Could not read PDF: {e}")
                elif st.session_state.get("resume_text_staged"):
                    # File was uploaded in a previous run — show persisted state
                    chars = len(st.session_state["resume_text_staged"])
                    st.markdown(f"""
                        <div style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.15);
                                    border-radius:10px;padding:10px 16px;margin-top:10px;
                                    font-size:0.8rem;color:#64748b;">
                            ✓ Resume loaded · {chars:,} characters · re-upload to change
                        </div>
                    """, unsafe_allow_html=True)
            else:
                # Clear any previously staged PDF text when switching to paste mode
                if st.session_state.get("resume_text_staged"):
                    st.session_state.pop("resume_text_staged", None)
                paste_text = st.text_area(
                    "Resume text",
                    height=280,
                    placeholder="Paste the full content of your resume here…",
                    label_visibility="collapsed",
                )
                if paste_text.strip():
                    st.session_state["resume_text_staged"] = paste_text.strip()
                    wc = len(paste_text.split())
                    st.markdown(f"""
                        <div style="font-size:0.75rem;color:#475569;margin-top:4px;text-align:right;">
                            ~{wc:,} words
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.session_state.pop("resume_text_staged", None)

        # ── Run Section ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.divider()

        jds_ready    = bool(st.session_state.get("jds"))
        resume_ready = bool(st.session_state.get("resume_text_staged", "").strip())

        # Status pills
        st.markdown("""
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;">
        """, unsafe_allow_html=True)

        c1, c2, spacer = st.columns([1, 1, 2])
        with c1:
            if jds_ready:
                presets_list = load_presets()
                role_name = next((p["name"] for p in presets_list
                                  if p["id"] == st.session_state.get("selected_preset")), "Custom JD")
                st.success(f"✓ {role_name}")
            else:
                st.warning("① Choose a target role")
        with c2:
            if resume_ready:
                st.success("✓ Resume ready")
            else:
                st.warning("② Add your resume")

        st.markdown("<br>", unsafe_allow_html=True)
        _, btn_col, _ = st.columns([1, 1.6, 1])
        with btn_col:
            run_disabled = not (jds_ready and resume_ready)
            if st.button("🚀  Run Analysis", type="primary",
                         use_container_width=True, disabled=run_disabled):
                st.session_state["resume_text"] = st.session_state["resume_text_staged"]
                process_analysis()
                st.success("✅ Analysis complete! Switch to the **Results** tab.")
            if run_disabled:
                st.markdown("""
                    <p style="text-align:center;color:#334155;font-size:0.78rem;margin-top:8px;">
                        Complete both steps above to run the analysis.
                    </p>
                """, unsafe_allow_html=True)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 2 — Results
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab2:
        if not st.session_state.get("analysis_complete"):
            _empty_state("📊", "No results yet",
                         "Complete the Setup & Run tab to see your readiness score and market radar.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            score      = st.session_state.get("readiness_score", 0)
            gap_matrix = st.session_state.get("gap_matrix", [])

            col_gauge, col_stats = st.columns([1, 2], gap="large")

            with col_gauge:
                render_readiness_gauge(score)
                color, label, tip = _score_label(score)
                st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.025);
                                border:1px solid rgba(255,255,255,0.07);
                                border-top:2px solid {color};border-radius:12px;
                                padding:16px 18px;margin-top:16px;">
                        <div style="font-weight:700;color:{color};font-size:0.95rem;margin-bottom:5px;">
                            {label}
                        </div>
                        <div style="color:#64748b;font-size:0.82rem;line-height:1.55;">{tip}</div>
                    </div>
                """, unsafe_allow_html=True)

            with col_stats:
                total   = len(gap_matrix)
                demo    = sum(1 for g in gap_matrix if g["evidence_level"] == 2)
                theory  = sum(1 for g in gap_matrix if g["evidence_level"] == 1)
                missing = sum(1 for g in gap_matrix if g["evidence_level"] == 0)
                high_p  = sum(1 for g in gap_matrix if g.get("is_high_priority"))

                m1, m2, m3, m4 = st.columns(4)
                with m1: st.metric("Total Skills",  total)
                with m2: st.metric("Demonstrated",  demo)
                with m3: st.metric("Theoretical",   theory)
                with m4: st.metric("Missing",        missing)

                st.markdown("<br>", unsafe_allow_html=True)

                if high_p:
                    st.markdown(f"""
                        <div style="background:rgba(239,68,68,0.06);
                                    border:1px solid rgba(239,68,68,0.18);
                                    border-radius:10px;padding:14px 18px;">
                            <div style="font-size:0.85rem;font-weight:600;color:#f87171;margin-bottom:4px;">
                                ⚠️ {high_p} high-priority gap{"s" if high_p != 1 else ""}
                            </div>
                            <div style="font-size:0.78rem;color:#64748b;line-height:1.5;">
                                Skills with ≥50% market demand that aren't yet demonstrated in your profile.
                                See the Skill Gaps tab for details.
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="background:rgba(16,185,129,0.06);
                                    border:1px solid rgba(16,185,129,0.18);
                                    border-radius:10px;padding:14px 18px;">
                            <div style="font-size:0.85rem;font-weight:600;color:#34d399;margin-bottom:4px;">
                                ✓ No high-priority gaps
                            </div>
                            <div style="font-size:0.78rem;color:#64748b;">
                                You've demonstrated all high-demand skills for this role.
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            _section_label("Candidate Proficiency vs. Market Demand")
            st.markdown("""
                <p style="color:#475569;font-size:0.8rem;margin:-6px 0 16px 0;">
                    Top 10 most-demanded skills. Indigo = market standard · Green = your proficiency
                    (100% demonstrated · 50% theoretical · 0% missing).
                </p>
            """, unsafe_allow_html=True)
            render_candidate_radar_chart(gap_matrix)

            # ── Export ───────────────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            csv_data = gap_matrix_to_csv(gap_matrix)
            role_name_safe = st.session_state.get("selected_preset", "analysis").replace(" ", "_")
            st.download_button(
                label="⬇️  Download Full Report (CSV)",
                data=csv_data,
                file_name=f"skillgap_{role_name_safe}.csv",
                mime="text/csv",
                use_container_width=False,
            )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 3 — Skill Gaps
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab3:
        if not st.session_state.get("analysis_complete"):
            _empty_state("🔍", "No gap data yet",
                         "Complete the Setup & Run tab to see a skill-by-skill breakdown.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            _section_label("Skill-by-Skill Breakdown")
            st.markdown("""
                <p style="color:#475569;font-size:0.8rem;margin:-6px 0 18px 0;">
                    Every skill the market demands, your current status, and how frequently
                    it appears in job postings — sorted by demand.
                </p>
            """, unsafe_allow_html=True)
            render_gap_matrix(st.session_state.get("gap_matrix", []))

            # ── Export ───────────────────────────────────────────────────────
            st.markdown("<br>", unsafe_allow_html=True)
            csv_data = gap_matrix_to_csv(st.session_state.get("gap_matrix", []))
            role_name_safe = st.session_state.get("selected_preset", "analysis").replace(" ", "_")
            st.download_button(
                label="⬇️  Export Gap Matrix (CSV)",
                data=csv_data,
                file_name=f"skillgap_{role_name_safe}.csv",
                mime="text/csv",
                use_container_width=False,
            )

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # TAB 4 — Roadmap & Chat
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab4:
        if not st.session_state.get("analysis_complete"):
            _empty_state("🗺️", "Roadmap not generated yet",
                         "Complete the Setup & Run tab first. Your personalised roadmap and AI career coach will appear here.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            road_col, chat_col = st.columns([1, 1], gap="large")

            with road_col:
                _section_label("Learning Roadmap")
                st.markdown("""
                    <p style="color:#475569;font-size:0.8rem;margin:-6px 0 16px 0;">
                        A project-first plan targeting your highest-priority gaps.
                        Each step is a concrete micro-project you can add to your portfolio.
                    </p>
                """, unsafe_allow_html=True)

                if "roadmap" not in st.session_state:
                    with st.spinner("Generating your personalised roadmap…"):
                        st.session_state["roadmap"] = generate_roadmap(
                            st.session_state["gap_matrix"]
                        )

                st.markdown("""
                    <div style="background:rgba(255,255,255,0.02);
                                border:1px solid rgba(255,255,255,0.07);
                                border-radius:14px;padding:6px 22px 18px 22px;
                                margin-bottom:14px;">
                """, unsafe_allow_html=True)
                st.markdown(st.session_state["roadmap"])
                st.markdown("</div>", unsafe_allow_html=True)

                if st.button("🔄  Regenerate Roadmap", type="secondary"):
                    st.session_state.pop("roadmap", None)
                    st.rerun()

            with chat_col:
                _section_label("AI Career Coach")
                st.markdown("""
                    <p style="color:#475569;font-size:0.8rem;margin:-6px 0 16px 0;">
                        Ask anything about your gaps, the roadmap, or next steps.
                        The coach has full context from your analysis.
                    </p>
                """, unsafe_allow_html=True)

                if "messages" not in st.session_state:
                    st.session_state["messages"] = []

                chat_box = st.container(height=440)
                with chat_box:
                    if not st.session_state["messages"]:
                        st.markdown("""
                            <div style="height:100%;display:flex;flex-direction:column;
                                        align-items:center;justify-content:center;
                                        padding:40px 20px;text-align:center;">
                                <div style="width:44px;height:44px;background:rgba(99,102,241,0.1);
                                            border:1px solid rgba(99,102,241,0.2);border-radius:12px;
                                            display:flex;align-items:center;justify-content:center;
                                            font-size:1.3rem;margin-bottom:14px;">💬</div>
                                <div style="font-size:0.88rem;font-weight:600;color:#64748b;
                                            margin-bottom:6px;">Ask your career coach</div>
                                <div style="font-size:0.78rem;color:#334155;line-height:1.5;">
                                    "Why is Docker high priority?"<br>
                                    "What project should I build first?"<br>
                                    "How long will it take to close these gaps?"
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    for msg in st.session_state["messages"]:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["content"])

                if prompt := st.chat_input("Ask your career coach…"):
                    st.session_state["messages"].append({"role": "user", "content": prompt})
                    with st.spinner("Thinking…"):
                        response = get_chat_response(
                            st.session_state["messages"],
                            st.session_state.get("gap_matrix", []),
                        )
                    st.session_state["messages"].append({"role": "assistant", "content": response})
                    st.rerun()


# ── UI Utilities ──────────────────────────────────────────────────────────────

def _step_header(num: str, accent: str, text_col: str, title: str, subtitle: str):
    st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:18px;">
            <div style="min-width:26px;height:26px;background:{accent}18;
                        border:1px solid {accent}44;border-radius:8px;
                        display:flex;align-items:center;justify-content:center;
                        font-size:0.72rem;font-weight:700;color:{text_col};
                        margin-top:2px;flex-shrink:0;">{num}</div>
            <div>
                <div style="font-size:0.95rem;font-weight:700;color:#f1f5f9;margin-bottom:3px;">
                    {title}
                </div>
                <div style="font-size:0.8rem;color:#64748b;line-height:1.4;">{subtitle}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def _section_label(text: str):
    st.markdown(f"""
        <h3 style="font-size:1.05rem;font-weight:700;color:#f1f5f9;
                   margin:0 0 8px 0;letter-spacing:-0.2px;">{text}</h3>
    """, unsafe_allow_html=True)


def _empty_state(icon: str, title: str, desc: str):
    st.markdown("<br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"""
            <div style="text-align:center;padding:56px 28px;
                        background:rgba(255,255,255,0.018);
                        border:1px dashed rgba(255,255,255,0.07);
                        border-radius:16px;">
                <div style="font-size:2.4rem;margin-bottom:14px;opacity:0.7;">{icon}</div>
                <div style="font-size:1rem;font-weight:600;color:#64748b;margin-bottom:8px;">
                    {title}
                </div>
                <div style="font-size:0.82rem;color:#334155;line-height:1.6;max-width:320px;margin:0 auto;">
                    {desc}
                </div>
            </div>
        """, unsafe_allow_html=True)


def _score_label(score: int):
    if score >= 75:
        return "#10b981", "Strong match", \
            "You've demonstrated most high-demand skills. Focus on the remaining gaps to maximise your competitiveness."
    elif score >= 50:
        return "#f59e0b", "Moderate match", \
            "Solid foundation, but several in-demand skills still need project-based proof. Check the roadmap."
    elif score >= 25:
        return "#f97316", "Needs work", \
            "Notable gaps between your profile and market demands. The roadmap prioritises the highest-impact areas first."
    else:
        return "#ef4444", "Significant gaps", \
            "Substantial skill development needed for this role. Start with the roadmap — it guides you step by step."
