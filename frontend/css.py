"""
Custom CSS injection for LegacyLens — gives the app a premium SaaS look.
"""
import streamlit as st


def inject_custom_css() -> None:
    """Inject custom CSS to give the app a polished, premium SaaS look."""
    st.markdown(
        """
        <style>
        /* ── Import Google Font ────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* ── Root Variables ────────────────────────────────────────── */
        :root {
            --ll-primary: #6C63FF;
            --ll-primary-light: #8B83FF;
            --ll-primary-dark: #4F46E5;
            --ll-accent: #00D4AA;
            --ll-accent-light: #34E0BF;
            --ll-bg-dark: #0F1117;
            --ll-bg-card: #1A1D2E;
            --ll-bg-card-hover: #22263A;
            --ll-text-primary: #E8E8ED;
            --ll-text-secondary: #9CA3AF;
            --ll-border: #2D3148;
            --ll-success: #10B981;
            --ll-warning: #F59E0B;
            --ll-error: #EF4444;
            --ll-gradient: linear-gradient(135deg, #6C63FF 0%, #00D4AA 100%);
        }

        /* ── Global Font ───────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* ── Hero Header ───────────────────────────────────────────── */
        .hero-header {
            background: linear-gradient(135deg, #1a1d2e 0%, #0f1117 50%, #1a1d2e 100%);
            border: 1px solid var(--ll-border);
            border-radius: 16px;
            padding: 2.5rem 2rem;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }
        .hero-header::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--ll-gradient);
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: var(--ll-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
        }
        .hero-subtitle {
            font-size: 1.05rem;
            color: var(--ll-text-secondary);
            font-weight: 400;
            line-height: 1.6;
        }

        /* ── Card Containers ───────────────────────────────────────── */
        .ll-card {
            background: var(--ll-bg-card);
            border: 1px solid var(--ll-border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .ll-card:hover {
            border-color: var(--ll-primary);
            box-shadow: 0 0 20px rgba(108, 99, 255, 0.1);
        }
        .ll-card-title {
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--ll-primary-light);
            margin-bottom: 0.75rem;
        }

        /* ── Sidebar Styling ───────────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #12141F 0%, #0F1117 100%);
            border-right: 1px solid var(--ll-border);
        }
        .sidebar-brand {
            text-align: center;
            padding: 1rem 0 1.5rem;
            border-bottom: 1px solid var(--ll-border);
            margin-bottom: 1.5rem;
        }
        .sidebar-brand-icon {
            font-size: 2.4rem;
            margin-bottom: 0.25rem;
        }
        .sidebar-brand-name {
            font-size: 1.3rem;
            font-weight: 700;
            background: var(--ll-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .sidebar-section-label {
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--ll-text-secondary);
            margin: 1.25rem 0 0.5rem 0;
        }

        /* ── Buttons ───────────────────────────────────────────────── */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
            border: none;
            letter-spacing: 0.01em;
        }
        div[data-testid="stHorizontalBlock"] .stButton > button {
            width: 100%;
            padding: 0.7rem 1.5rem;
        }

        /* ── Tabs ──────────────────────────────────────────────────── */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 2px solid var(--ll-border);
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            font-family: 'Inter', sans-serif;
            letter-spacing: 0.01em;
        }
        .stTabs [aria-selected="true"] {
            border-bottom: 2px solid var(--ll-primary) !important;
        }

        /* ── Text Area ─────────────────────────────────────────────── */
        .stTextArea textarea {
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
            font-size: 0.85rem !important;
            line-height: 1.6 !important;
            border-radius: 10px !important;
            border: 1px solid var(--ll-border) !important;
        }
        .stTextArea textarea:focus {
            border-color: var(--ll-primary) !important;
            box-shadow: 0 0 0 2px rgba(108, 99, 255, 0.25) !important;
        }

        /* ── Expanders ─────────────────────────────────────────────── */
        .streamlit-expanderHeader {
            font-weight: 600;
            font-family: 'Inter', sans-serif;
        }

        /* ── Download Button ───────────────────────────────────────── */
        .stDownloadButton > button {
            background: var(--ll-gradient) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        .stDownloadButton > button:hover {
            opacity: 0.9;
            box-shadow: 0 4px 15px rgba(108, 99, 255, 0.4);
        }

        /* ── Status Badges ─────────────────────────────────────────── */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.03em;
        }
        .status-ready {
            background: rgba(16, 185, 129, 0.15);
            color: #10B981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .status-waiting {
            background: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* ── Footer ────────────────────────────────────────────────── */
        .ll-footer {
            text-align: center;
            padding: 2rem 0 1rem;
            color: var(--ll-text-secondary);
            font-size: 0.8rem;
            border-top: 1px solid var(--ll-border);
            margin-top: 3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
