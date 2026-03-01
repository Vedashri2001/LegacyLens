"""
Main content UI — hero header, code input, action buttons, output tabs, and footer.
"""
import streamlit as st
from datetime import datetime

from backend.samples import SAMPLE_CODES, SAMPLE_RPGLE_CODE
from backend.validation import validate_input, check_input_warnings, estimate_tokens
from backend.ai_service import call_llm
from backend.parser import parse_llm_response
from backend.report import generate_report_markdown


def render_main_content() -> None:
    """Render the main workspace: header, input area, action buttons, output tabs."""

    # ── Hero Header ───────────────────────────────────────────────
    st.markdown(
        """
        <div class="hero-header">
            <div class="hero-title">🔍 LegacyLens</div>
            <div class="hero-subtitle">
                Transform cryptic legacy mainframe code (RPGLE, COBOL, JCL, PL/I & more)
                into clear documentation and modern Python — powered by AI.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Input Section ─────────────────────────────────────────────
    selected_lang = st.session_state.get("selected_language", "RPGLE / AS400")
    st.markdown(
        f'<div class="ll-card-title">📥 {selected_lang} Source Code</div>',
        unsafe_allow_html=True,
    )

    # "Load Sample Code" button
    col_sample, col_clear = st.columns([1, 1])
    with col_sample:
        if st.button(f"📄 Load {selected_lang} Sample", use_container_width=True, help=f"Load a demo {selected_lang} snippet to try the tool"):
            st.session_state["rpgle_input"] = SAMPLE_CODES.get(selected_lang, SAMPLE_RPGLE_CODE)
            st.rerun()
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True, help="Clear the code input area"):
            st.session_state["rpgle_input"] = ""
            st.session_state["analysis_complete"] = False
            st.session_state["executive_summary"] = ""
            st.session_state["technical_docs"] = ""
            st.session_state["python_code"] = ""
            st.rerun()

    # Code input text area
    rpgle_code = st.text_area(
        "Paste your legacy code here",
        height=300,
        placeholder=f"Paste your {selected_lang} code here...\n\nOr click 'Load Sample' above to try a demo.",
        label_visibility="collapsed",
        key="rpgle_input",
    )

    # Show character count
    if rpgle_code:
        line_count = rpgle_code.count("\n") + 1
        st.caption(f"📊 {len(rpgle_code)} characters • {line_count} lines")

    st.markdown("---")

    # ── Action Buttons ────────────────────────────────────────────
    st.markdown(
        '<div class="ll-card-title">⚡ Actions</div>',
        unsafe_allow_html=True,
    )

    col_doc, col_python, col_full = st.columns(3)

    with col_doc:
        btn_docs = st.button(
            "📝 Generate Documentation",
            use_container_width=True,
            help="Generate Executive Summary and Technical Documentation only",
        )
    with col_python:
        btn_python = st.button(
            "🐍 Translate to Python",
            use_container_width=True,
            help="Generate modernized Python code only",
        )
    with col_full:
        btn_full = st.button(
            "🚀 Full Analysis",
            use_container_width=True,
            type="primary",
            help="Generate all outputs: Summary, Docs, and Python code",
        )

    # ── Handle Button Clicks ──────────────────────────────────────
    action_mode = None
    if btn_full:
        action_mode = "full"
    elif btn_docs:
        action_mode = "docs_only"
    elif btn_python:
        action_mode = "python_only"

    if action_mode:
        # ── Input Validation ──────────────────────────────────────
        is_valid, error_msg = validate_input(rpgle_code, selected_lang)
        if not is_valid:
            st.error(error_msg)
        else:
            # Show warnings for large inputs (but still proceed)
            check_input_warnings(rpgle_code)

            # Show estimated tokens
            est_input_tokens = estimate_tokens(rpgle_code) + 200  # +200 for system prompt
            st.caption(f"🪙 Estimated input: ~{est_input_tokens:,} tokens")

            with st.spinner("🔄 Analyzing your legacy code... This may take 15-30 seconds."):
                try:
                    raw_response = call_llm(rpgle_code, mode=action_mode)
                    sections = parse_llm_response(raw_response)

                    # Store results — clear stale data from other tabs
                    if action_mode == "full":
                        st.session_state["executive_summary"] = sections["executive_summary"]
                        st.session_state["technical_docs"] = sections["technical_docs"]
                        st.session_state["python_code"] = sections["python_code"]
                    elif action_mode == "docs_only":
                        st.session_state["executive_summary"] = sections["executive_summary"]
                        st.session_state["technical_docs"] = sections["technical_docs"]
                        st.session_state["python_code"] = ""  # Clear stale python
                    elif action_mode == "python_only":
                        st.session_state["executive_summary"] = ""  # Clear stale summary
                        st.session_state["technical_docs"] = ""     # Clear stale docs
                        st.session_state["python_code"] = sections["python_code"]

                    st.session_state["last_action_mode"] = action_mode
                    st.session_state["analysis_complete"] = True

                    # Check for truncated output
                    if sections.get("python_code_truncated"):
                        st.warning(
                            "⚠️ **Output may be truncated.** The Python code section "
                            "appears incomplete. Try using **Translate to Python** "
                            "separately, or split your input into smaller sections.",
                            icon="⚠️",
                        )
                        st.toast("⚠️ Analysis complete (output may be truncated)", icon="⚠️")
                    else:
                        st.toast("✅ Analysis complete!", icon="🎉")

                except RuntimeError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")

    # ── Output Tabs ───────────────────────────────────────────────
    if st.session_state.get("analysis_complete"):
        st.markdown("---")
        st.markdown(
            '<div class="ll-card-title">📊 Analysis Results</div>',
            unsafe_allow_html=True,
        )

        last_mode = st.session_state.get("last_action_mode", "full")
        has_summary = bool(st.session_state.get("executive_summary", ""))
        has_docs = bool(st.session_state.get("technical_docs", ""))
        has_python = bool(st.session_state.get("python_code", ""))

        tab_summary, tab_tech, tab_python = st.tabs([
            "📝 Executive Summary",
            "📋 Technical Documentation",
            "🐍 Python Modernization",
        ])

        with tab_summary:
            summary = st.session_state.get("executive_summary", "")
            if summary and not summary.startswith("_No"):
                st.markdown(
                    """<div class="ll-card">"""
                    """<div class="ll-card-title">Executive Summary</div>"""
                    """</div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(summary)
            else:
                if last_mode == "python_only":
                    st.markdown(
                        '<div style="text-align:center; padding:40px 20px; color:#666; '
                        'background:rgba(100,100,100,0.05); border-radius:10px; margin:10px 0;">'
                        '<div style="font-size:2rem; margin-bottom:10px;">📝</div>'
                        '<strong>Not generated in this run</strong><br>'
                        '<span style="font-size:0.85rem;">You selected <em>Translate to Python</em> only. '
                        'Use <strong>Generate Documentation</strong> or <strong>Full Analysis</strong> '
                        'to populate this tab.</span></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("📝 Click **Generate Documentation** or **Full Analysis** to generate the executive summary.")

        with tab_tech:
            tech_docs = st.session_state.get("technical_docs", "")
            if tech_docs and not tech_docs.startswith("_No"):
                st.markdown(
                    """<div class="ll-card">"""
                    """<div class="ll-card-title">Technical Documentation</div>"""
                    """</div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(tech_docs)
            else:
                if last_mode == "python_only":
                    st.markdown(
                        '<div style="text-align:center; padding:40px 20px; color:#666; '
                        'background:rgba(100,100,100,0.05); border-radius:10px; margin:10px 0;">'
                        '<div style="font-size:2rem; margin-bottom:10px;">📋</div>'
                        '<strong>Not generated in this run</strong><br>'
                        '<span style="font-size:0.85rem;">You selected <em>Translate to Python</em> only. '
                        'Use <strong>Generate Documentation</strong> or <strong>Full Analysis</strong> '
                        'to populate this tab.</span></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("📋 Click **Generate Documentation** or **Full Analysis** to generate technical docs.")

        with tab_python:
            python_code = st.session_state.get("python_code", "")
            if python_code and not python_code.startswith("_No"):
                st.markdown(
                    """<div class="ll-card">"""
                    """<div class="ll-card-title">Modernized Python Code</div>"""
                    """</div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(python_code)
            else:
                if last_mode == "docs_only":
                    st.markdown(
                        '<div style="text-align:center; padding:40px 20px; color:#666; '
                        'background:rgba(100,100,100,0.05); border-radius:10px; margin:10px 0;">'
                        '<div style="font-size:2rem; margin-bottom:10px;">🐍</div>'
                        '<strong>Not generated in this run</strong><br>'
                        '<span style="font-size:0.85rem;">You selected <em>Generate Documentation</em> only. '
                        'Use <strong>Translate to Python</strong> or <strong>Full Analysis</strong> '
                        'to populate this tab.</span></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.info("🐍 Click **Translate to Python** or **Full Analysis** to generate Python code.")

        # ── Download Report Button ────────────────────────────────
        st.markdown("---")
        report_sections = {
            "executive_summary": st.session_state.get("executive_summary", ""),
            "technical_docs": st.session_state.get("technical_docs", ""),
            "python_code": st.session_state.get("python_code", ""),
        }

        # Only show download if there's actual content
        has_content = any(
            v and not v.startswith("_No") for v in report_sections.values()
        )
        if has_content:
            report_md = generate_report_markdown(rpgle_code, report_sections)
            col_dl, col_spacer = st.columns([1, 2])
            with col_dl:
                st.download_button(
                    label="📥 Download Full Report (.md)",
                    data=report_md,
                    file_name=f"legacylens_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

    # ── Footer ────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="ll-footer">
            Built with ❤️ using Streamlit • LegacyLens v1.1.0<br>
            <span style="font-size: 0.7rem;">
                Your API keys never leave your browser session.
                No data is stored on our servers.
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )
