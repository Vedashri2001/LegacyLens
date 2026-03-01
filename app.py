"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  LegacyLens — Legacy Code Explainer & Modernizer                            ║
║                                                                              ║
║  Transforms mainframe code (RPGLE, COBOL, JCL, PL/I, Natural/ADABAS, CL)   ║
║  into clear documentation and modern Python — powered by AI.                ║
║                                                                              ║
║  Version : 1.1.0                                                             ║
║  Stack   : Streamlit · Google Gemini · Azure OpenAI                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Page Configuration — MUST be the first Streamlit command
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LegacyLens — Legacy Code Explainer & Modernizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Application Modules
# ─────────────────────────────────────────────────────────────────────────────
from frontend.css import inject_custom_css
from frontend.sidebar import init_session_state, render_sidebar
from frontend.main_content import render_main_content


def main() -> None:
    """Main entry point — wire everything together."""
    inject_custom_css()
    init_session_state()
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()
