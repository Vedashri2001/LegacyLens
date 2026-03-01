"""
Response parser — splits raw LLM output into structured sections.
"""
import re


def parse_llm_response(raw_response: str) -> dict[str, str]:
    """
    Parse the LLM's raw markdown response into three sections by looking
    for the ## headings we instructed it to use.

    Returns a dict with keys: 'executive_summary', 'technical_docs', 'python_code'.
    If a section is missing, its value will be a friendly fallback message.
    """
    sections: dict[str, str] = {
        "executive_summary": "",
        "technical_docs": "",
        "python_code": "",
    }

    # Patterns to match section headings (case-insensitive, flexible spacing)
    patterns = {
        "executive_summary": re.compile(r"^##\s*EXECUTIVE\s+SUMMARY", re.IGNORECASE | re.MULTILINE),
        "technical_docs": re.compile(r"^##\s*TECHNICAL\s+DOCUMENTATION", re.IGNORECASE | re.MULTILINE),
        "python_code": re.compile(r"^##\s*(?:PYTHON\s+CODE|MODERNIZED\s+PYTHON|PYTHON\s+MODERNIZATION)", re.IGNORECASE | re.MULTILINE),
    }

    # Find positions of each section heading
    positions: list[tuple[int, str]] = []
    for key, pattern in patterns.items():
        match = pattern.search(raw_response)
        if match:
            positions.append((match.start(), key))

    # Sort by position so we can slice between headings
    positions.sort(key=lambda x: x[0])

    # Extract content between section boundaries
    for i, (start, key) in enumerate(positions):
        # Find the end of the heading line
        heading_end = raw_response.index("\n", start) + 1 if "\n" in raw_response[start:] else len(raw_response)
        # End is either the start of the next section or end of text
        end = positions[i + 1][0] if i + 1 < len(positions) else len(raw_response)
        sections[key] = raw_response[heading_end:end].strip()

    # Friendly fallbacks
    if not sections["executive_summary"]:
        sections["executive_summary"] = "_No executive summary was generated. The LLM may not have followed the expected format._"
    if not sections["technical_docs"]:
        sections["technical_docs"] = "_No technical documentation was generated._"
    if not sections["python_code"]:
        sections["python_code"] = "_No Python code was generated._"

    # Detect truncated output — if the Python section looks incomplete
    python_out = sections["python_code"]
    if python_out and not python_out.startswith("_No"):
        # Only flag truncation if there's an unclosed code block (odd number of ```)
        open_fences = python_out.count("```")
        if open_fences % 2 != 0:
            sections["python_code_truncated"] = True

    return sections
