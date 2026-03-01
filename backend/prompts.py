"""
Prompt engineering — system and user prompt builders for LegacyLens.
"""
import textwrap


def build_system_prompt(language: str = "RPGLE / AS400") -> str:
    """
    Construct a concise system prompt for the LLM.
    Kept short to minimize token usage on free-tier API keys.
    """
    return textwrap.dedent(f"""\
    You are LegacyLens AI, an expert in legacy mainframe code (RPGLE, COBOL, JCL, PL/I, Natural/ADABAS, CL).
    You are analyzing {language} code.

    Return your response in exactly THREE sections with these markdown headings:

    ## EXECUTIVE SUMMARY
    3-5 sentence plain-English explanation for non-technical stakeholders.

    ## TECHNICAL DOCUMENTATION
    Include: files/tables used, key variables (name, type, purpose), step-by-step logic flow, I/O operations, edge cases.

    ## PYTHON CODE
    Modern Python 3.12+ equivalent with type hints, comments referencing original {language} code, error handling, and a main block.
    """)


def build_user_prompt(legacy_code: str, language: str = "RPGLE / AS400", mode: str = "full") -> str:
    """
    Build the user-facing prompt that wraps the pasted legacy code.

    Args:
        legacy_code: The raw legacy source code from the user.
        language: The legacy language being analyzed.
        mode: "full" for all three sections, "docs_only" for just
              Executive Summary + Technical Documentation,
              "python_only" for just the Python translation.
    """
    mode_instruction = {
        "full": "Provide ALL THREE sections: Executive Summary, Technical Documentation, and Python Code.",
        "docs_only": "Provide ONLY the Executive Summary and Technical Documentation sections. Do NOT include Python Code.",
        "python_only": "Provide ONLY the Python Code section. Do NOT include Executive Summary or Technical Documentation.",
    }
    return textwrap.dedent(f"""\
    Analyze the following {language} code.
    {mode_instruction.get(mode, mode_instruction["full"])}

    ```
    {legacy_code}
    ```
    """)
