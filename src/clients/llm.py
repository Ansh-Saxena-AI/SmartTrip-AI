
"""Central LLM client with Gemini-to-Groq quota fallback."""

from functools import lru_cache

from langchain_core.runnables import RunnableLambda
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from src.config.session import resolve_gemini_api_key, resolve_groq_api_key
from src.config.settings import GEMINI_MODEL

GROQ_MODEL = "openai/gpt-oss-120b"


@lru_cache(maxsize=8)
def _build_gemini(model: str, api_key: str):
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0,
    )


@lru_cache(maxsize=8)
def _build_groq(model: str, api_key: str):
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
        temperature=0,
    )


def _is_quota_error(error: Exception) -> bool:
    message = str(error).lower()
    markers = (
        "429",
        "resource_exhausted",
        "quota",
        "rate limit",
        "rate_limit_exceeded",
        "too many requests",
    )
    return any(marker in message for marker in markers)


def get_llm():
    """Use Gemini first, falling back to Groq on quota errors."""
    gemini_key = resolve_gemini_api_key()
    groq_key = resolve_groq_api_key()

    if not gemini_key and not groq_key:
        raise ValueError(
            "No LLM API key configured. Add GEMINI_API_KEY or GROQ_API_KEY to .env."
        )

    if not gemini_key:
        return _build_groq(GROQ_MODEL, groq_key)

    primary = _build_gemini(GEMINI_MODEL, gemini_key)

    if not groq_key:
        return primary

    fallback = _build_groq(GROQ_MODEL, groq_key)

    def invoke_with_fallback(input, config=None, **kwargs):
        try:
            return primary.invoke(input, config=config, **kwargs)
        except Exception as error:
            if not _is_quota_error(error):
                raise
            print("Gemini quota reached; switching to Groq.", flush=True)
            return fallback.invoke(input, config=config, **kwargs)

    return RunnableLambda(invoke_with_fallback)
