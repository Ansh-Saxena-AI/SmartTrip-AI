
from unittest.mock import MagicMock, patch

import pytest

from src.clients.llm import get_llm


def test_gemini_quota_error_uses_groq():
    gemini = MagicMock()
    groq = MagicMock()

    gemini.invoke.side_effect = Exception("429 quota exceeded")
    groq.invoke.return_value = "Groq response"

    with (
        patch("src.clients.llm.resolve_gemini_api_key", return_value="gemini-test-key"),
        patch("src.clients.llm.resolve_groq_api_key", return_value="groq-test-key"),
        patch("src.clients.llm._build_gemini", return_value=gemini),
        patch("src.clients.llm._build_groq", return_value=groq),
    ):
        result = get_llm().invoke("Test prompt")

    assert result == "Groq response"
    gemini.invoke.assert_called_once()
    groq.invoke.assert_called_once()


def test_groq_error_is_propagated_when_fallback_fails():
    gemini = MagicMock()
    groq = MagicMock()

    gemini.invoke.side_effect = Exception("429 quota exceeded")
    groq.invoke.side_effect = Exception("Groq rate limit exceeded")

    with (
        patch("src.clients.llm.resolve_gemini_api_key", return_value="gemini-test-key"),
        patch("src.clients.llm.resolve_groq_api_key", return_value="groq-test-key"),
        patch("src.clients.llm._build_gemini", return_value=gemini),
        patch("src.clients.llm._build_groq", return_value=groq),
    ):
        with pytest.raises(Exception, match="Groq rate limit exceeded"):
            get_llm().invoke("Test prompt")
