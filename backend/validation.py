"""
Input validation and safety limits for LegacyLens.
"""
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# Safety Constants
# ─────────────────────────────────────────────────────────────────────────────
# Rough token estimate: 1 token ≈ 4 characters for English/code.
INPUT_WARN_CHARS = 12000   # ~3,000 tokens — show a warning
INPUT_MAX_CHARS = 40000    # ~10,000 tokens — hard block
MAX_RETRIES = 2            # Retry count on rate-limit errors
RETRY_DELAY_SECS = 5       # Wait between retries


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for code."""
    return len(text) // 4


def validate_input(code: str, language: str) -> tuple[bool, str | None]:
    """
    Validate the user's input code before sending to the LLM.

    Returns:
        (is_valid, error_message). If is_valid is True, error_message is None.
    """
    if not code or not code.strip():
        return False, f"⚠️ Please paste some {language} code or load the sample code before running analysis."

    char_count = len(code)
    if char_count > INPUT_MAX_CHARS:
        est_tokens = estimate_tokens(code)
        return False, (
            f"🚫 **Input too large** ({char_count:,} characters, ~{est_tokens:,} tokens).\n\n"
            f"The maximum is {INPUT_MAX_CHARS:,} characters (~{INPUT_MAX_CHARS // 4:,} tokens). "
            f"Please split your code into smaller sections and analyze each part separately."
        )

    return True, None


def check_input_warnings(code: str) -> None:
    """Show non-blocking warnings for large (but allowed) inputs."""
    char_count = len(code)
    if char_count > INPUT_WARN_CHARS:
        est_tokens = estimate_tokens(code)
        st.warning(
            f"⚠️ **Large input** ({char_count:,} chars, ~{est_tokens:,} tokens). "
            f"The output may be truncated if the code is too complex. "
            f"Consider splitting into smaller sections for best results.",
            icon="⚠️",
        )
