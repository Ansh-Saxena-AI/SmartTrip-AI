
"""Validate Gemini API keys and PostgreSQL connections."""

import psycopg
import requests

from src.config.settings import normalize_database_url

GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def check_gemini_api_key(api_key: str) -> tuple[bool, str]:
    try:
        response = requests.get(
            GEMINI_MODELS_URL,
            headers={"x-goog-api-key": api_key},
            params={"pageSize": 1},
            timeout=10,
        )
    except requests.RequestException:
        return False, "Could not reach Google Gemini. Check your internet connection."

    if response.status_code in (400, 401, 403):
        return False, "Gemini rejected this key. Check your API key and access."

    if not response.ok:
        return False, f"Gemini returned HTTP {response.status_code}."

    return True, "Gemini API key accepted."


def check_database_url(database_url: str) -> tuple[bool, str]:
    try:
        connection = psycopg.connect(
            normalize_database_url(database_url),
            connect_timeout=10,
        )
    except Exception as error:
        return False, f"Could not connect: {error}"

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as error:
        return False, f"Connected, but the test query failed: {error}"
    finally:
        connection.close()

    return True, "Connected successfully."