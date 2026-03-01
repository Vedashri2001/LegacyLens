"""
AI Service — LLM API callers and orchestrator for LegacyLens.
"""
import time
import streamlit as st

from backend.prompts import build_system_prompt, build_user_prompt
from backend.validation import MAX_RETRIES, RETRY_DELAY_SECS

# ─────────────────────────────────────────────────────────────────────────────
# Lazy imports for LLM SDKs (keeps startup fast)
# ─────────────────────────────────────────────────────────────────────────────
try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from openai import AzureOpenAI
except ImportError:
    AzureOpenAI = None


# ─────────────────────────────────────────────────────────────────────────────
# Gemini API Caller
# ─────────────────────────────────────────────────────────────────────────────
def call_gemini_api(
    user_prompt: str,
    system_prompt: str,
    api_key: str,
    model_name: str = "gemini-flash-latest",
) -> str:
    """
    Call Google Gemini API using the official SDK.

    Raises:
        RuntimeError: If the SDK is not installed or the API call fails.
    """
    if genai is None:
        raise RuntimeError(
            "The `google-generativeai` package is not installed. "
            "Run `pip install google-generativeai` to fix this."
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_prompt,
    )

    last_error = None
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            response = model.generate_content(
                user_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=8192,
                ),
            )

            # Check for blocked/empty responses
            if not response.text:
                raise RuntimeError(
                    "🚫 **Empty response.** The model returned no output. "
                    "This may happen if the input code was flagged by safety filters. "
                    "Try removing any sensitive data from the code."
                )
            return response.text

        except Exception as e:
            error_msg = str(e).lower()
            last_error = e

            # Auth errors — no retry
            if "api key" in error_msg or "invalid" in error_msg or "authenticate" in error_msg:
                raise RuntimeError(
                    "🔑 **Invalid API Key.** Please check your Gemini API key in the sidebar and try again."
                ) from e

            # Rate limit — retry with backoff
            if "quota" in error_msg or "rate" in error_msg or "429" in error_msg or "resource" in error_msg:
                if attempt <= MAX_RETRIES:
                    wait_time = RETRY_DELAY_SECS * attempt
                    st.toast(f"⏳ Rate limited. Retrying in {wait_time}s... (attempt {attempt}/{MAX_RETRIES})", icon="⏳")
                    time.sleep(wait_time)
                    continue
                else:
                    raise RuntimeError(
                        "⏳ **Rate limit reached** after retries.\n\n"
                        "**What to do:**\n"
                        "- Wait 60 seconds and try again\n"
                        "- Switch to **Gemini Flash (Latest)** in the sidebar for higher limits\n"
                        "- Use **Generate Documentation** instead of **Full Analysis** to reduce output size"
                    ) from e

            # Timeout — retry once
            if "timeout" in error_msg or "deadline" in error_msg:
                if attempt <= MAX_RETRIES:
                    st.toast(f"🕐 Timeout. Retrying... (attempt {attempt}/{MAX_RETRIES})", icon="🕐")
                    time.sleep(2)
                    continue
                else:
                    raise RuntimeError(
                        "🕐 **Request timed out** after retries. The code may be too large. "
                        "Try splitting it into smaller sections."
                    ) from e

            # Safety/content filter
            if "safety" in error_msg or "blocked" in error_msg or "harm" in error_msg:
                raise RuntimeError(
                    "🛡️ **Content blocked by safety filters.** "
                    "The model flagged the input or output. Try removing any "
                    "sensitive data (passwords, PII) from your code snippet."
                ) from e

            # Unknown error — no retry
            raise RuntimeError(f"❌ **Gemini API Error:** {e}") from e

    # Should not reach here, but just in case
    raise RuntimeError(f"❌ **Failed after {MAX_RETRIES} retries:** {last_error}")


# ─────────────────────────────────────────────────────────────────────────────
# Azure OpenAI API Caller
# ─────────────────────────────────────────────────────────────────────────────
def call_azure_openai_api(
    user_prompt: str,
    system_prompt: str,
    api_key: str,
    endpoint: str,
    deployment_name: str,
    api_version: str = "2024-02-01",
) -> str:
    """
    Call Azure OpenAI API using the official OpenAI SDK with Azure config.

    Raises:
        RuntimeError: If the SDK is not installed or the API call fails.
    """
    if AzureOpenAI is None:
        raise RuntimeError(
            "The `openai` package is not installed. "
            "Run `pip install openai` to fix this."
        )

    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=8192,
        )
        return response.choices[0].message.content

    except Exception as e:
        error_msg = str(e).lower()
        if "authentication" in error_msg or "401" in error_msg:
            raise RuntimeError(
                "🔑 **Authentication failed.** Please verify your Azure OpenAI credentials."
            ) from e
        elif "429" in error_msg or "rate" in error_msg:
            raise RuntimeError(
                "⏳ **Rate limit exceeded.** Please wait a moment and retry."
            ) from e
        elif "timeout" in error_msg:
            raise RuntimeError(
                "🕐 **Request timed out.** Please try again."
            ) from e
        elif "404" in error_msg or "not found" in error_msg:
            raise RuntimeError(
                "🔍 **Deployment not found.** Check your Azure endpoint URL and deployment name."
            ) from e
        else:
            raise RuntimeError(f"❌ **Azure OpenAI Error:** {e}") from e


# ─────────────────────────────────────────────────────────────────────────────
# Orchestrator — Route to the right LLM
# ─────────────────────────────────────────────────────────────────────────────
def call_llm(legacy_code: str, mode: str = "full") -> str:
    """
    High-level function: build prompts, select provider, call the LLM.

    Args:
        legacy_code: Raw legacy source code.
        mode: "full", "docs_only", or "python_only".

    Returns:
        Raw LLM response text.
    """
    language = st.session_state.get("selected_language", "RPGLE / AS400")
    system_prompt = build_system_prompt(language=language)
    user_prompt = build_user_prompt(legacy_code, language=language, mode=mode)
    provider = st.session_state.get("selected_model", "Gemini Flash (Latest)")

    if provider.startswith("Gemini"):
        api_key = st.session_state.get("gemini_api_key", "")
        if not api_key:
            raise RuntimeError("🔑 Please enter your **Gemini API Key** in the sidebar.")
        # Map display name to actual Gemini model ID
        model_map = {
            "Gemini Flash (Latest)": "gemini-flash-latest",
            "Gemini 1.5 Pro": "gemini-1.5-pro",
            "Gemini 1.5 Flash": "gemini-1.5-flash",
        }
        model_name = model_map.get(provider, "gemini-flash-latest")
        return call_gemini_api(user_prompt, system_prompt, api_key, model_name=model_name)

    elif provider.startswith("Azure"):
        api_key = st.session_state.get("azure_api_key", "")
        endpoint = st.session_state.get("azure_endpoint", "")
        deployment = st.session_state.get("azure_deployment", "")
        api_version = st.session_state.get("azure_api_version", "2024-02-01")
        if not all([api_key, endpoint, deployment]):
            raise RuntimeError(
                "🔑 Please enter your **Azure OpenAI credentials** (API key, endpoint, and deployment name) in the sidebar."
            )
        return call_azure_openai_api(
            user_prompt, system_prompt, api_key, endpoint, deployment, api_version
        )
    else:
        raise RuntimeError(f"Unknown model provider: {provider}")
