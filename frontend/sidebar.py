"""
Sidebar UI — branding, model/language selection, API keys, and help section.
"""
import streamlit as st

from backend.samples import SUPPORTED_LANGUAGES


def init_session_state() -> None:
    """Initialize all session state variables with sensible defaults."""
    defaults = {
        # API Keys
        "gemini_api_key": "",
        "azure_api_key": "",
        "azure_endpoint": "",
        "azure_deployment": "",
        "azure_api_version": "2024-02-01",
        # Model & language selection
        "selected_model": "Gemini Flash (Latest)",
        "selected_language": "RPGLE / AS400",
        # User input
        "rpgle_input": "",
        # Generated output sections
        "executive_summary": "",
        "technical_docs": "",
        "python_code": "",
        # Status flags
        "analysis_complete": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar() -> None:
    """Render the sidebar with branding, configuration, and help section."""
    with st.sidebar:
        # ── Brand ─────────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-icon">🔍</div>
                <div class="sidebar-brand-name">LegacyLens</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Model Selection ───────────────────────────────────────
        st.markdown('<div class="sidebar-section-label">🤖 Model Provider</div>', unsafe_allow_html=True)
        selected_model = st.selectbox(
            "Choose your LLM",
            options=["Gemini Flash (Latest)", "Gemini 1.5 Pro", "Gemini 1.5 Flash", "Azure GPT-4", "Azure GPT-4o"],
            index=0,
            label_visibility="collapsed",
            key="selected_model",
        )

        st.divider()

        # ── Language Selection ────────────────────────────────────
        st.markdown('<div class="sidebar-section-label">🖥️ Legacy Language</div>', unsafe_allow_html=True)
        st.selectbox(
            "Choose legacy language",
            options=SUPPORTED_LANGUAGES,
            index=0,
            label_visibility="collapsed",
            key="selected_language",
        )

        st.divider()

        # ── API Key Inputs — conditional based on provider ────────
        if selected_model.startswith("Gemini"):
            st.markdown('<div class="sidebar-section-label">🔐 Gemini API Key</div>', unsafe_allow_html=True)
            st.text_input(
                "Gemini API Key",
                type="password",
                placeholder="AIza...",
                label_visibility="collapsed",
                key="gemini_api_key",
                help="Get your API key from https://aistudio.google.com/app/apikey",
            )

            # Connection status indicator
            if st.session_state.get("gemini_api_key"):
                st.markdown(
                    '<span class="status-badge status-ready">● Key Entered</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-badge status-waiting">○ Awaiting Key</span>',
                    unsafe_allow_html=True,
                )

        elif selected_model.startswith("Azure"):
            st.markdown('<div class="sidebar-section-label">🔐 Azure OpenAI Credentials</div>', unsafe_allow_html=True)
            st.text_input(
                "Azure API Key",
                type="password",
                placeholder="Enter your Azure API key",
                label_visibility="collapsed",
                key="azure_api_key",
            )
            st.text_input(
                "Endpoint URL",
                placeholder="https://your-resource.openai.azure.com/",
                label_visibility="collapsed",
                key="azure_endpoint",
                help="Your Azure OpenAI resource endpoint URL",
            )
            st.text_input(
                "Deployment Name",
                placeholder="gpt-4",
                label_visibility="collapsed",
                key="azure_deployment",
                help="The name of your Azure model deployment",
            )
            with st.expander("Advanced Settings"):
                st.text_input(
                    "API Version",
                    placeholder="2024-02-01",
                    label_visibility="collapsed",
                    key="azure_api_version",
                )

            # Connection status indicator
            if all([
                st.session_state.get("azure_api_key"),
                st.session_state.get("azure_endpoint"),
                st.session_state.get("azure_deployment"),
            ]):
                st.markdown(
                    '<span class="status-badge status-ready">● Credentials Set</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="status-badge status-waiting">○ Incomplete</span>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # ── How It Works Section ──────────────────────────────────
        st.markdown('<div class="sidebar-section-label">📖 How It Works</div>', unsafe_allow_html=True)
        st.markdown(
            """
            **LegacyLens** acts as a bridge between legacy
            mainframe systems and modern cloud architecture.

            **Supported Languages:**
            RPGLE, COBOL, JCL, PL/I, Natural/ADABAS, CL

            1. **Select** your legacy language
            2. **Paste** your mainframe code
            3. **Choose** your preferred AI model
            4. **Click** to generate documentation or Python code

            The AI analyzes your legacy code and produces:
            - 📝 **Executive Summary** — plain-English overview for stakeholders
            - 📋 **Technical Docs** — detailed variable & logic breakdown
            - 🐍 **Python Code** — modern, production-ready equivalent

            > *Your API keys are never stored on any server.
            > They exist only in your browser session.*
            """,
        )

        st.divider()

        # ── Footer ────────────────────────────────────────────────
        st.caption("LegacyLens v1.1.0 • Built with Streamlit")
