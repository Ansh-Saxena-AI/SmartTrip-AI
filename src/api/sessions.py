
"""In-memory store for credentials supplied through the settings panel."""

import secrets
import threading
import time

from src.config.session import Credentials

SESSION_COOKIE = "travelbrain_session"
SESSION_TTL_SECONDS = 12 * 3600
MAX_SESSIONS = 500

_lock = threading.Lock()
_sessions: dict[str, dict] = {}


def new_session_id() -> str:
    return secrets.token_urlsafe(24)


def _prune(now: float) -> None:
    expired = [
        sid for sid, entry in _sessions.items()
        if entry["expires_at"] <= now
    ]
    for sid in expired:
        del _sessions[sid]

    if len(_sessions) > MAX_SESSIONS:
        oldest = sorted(
            _sessions,
            key=lambda sid: _sessions[sid]["expires_at"],
        )
        for sid in oldest[: len(_sessions) - MAX_SESSIONS]:
            del _sessions[sid]


def get_credentials_for(session_id: str | None) -> Credentials | None:
    if not session_id:
        return None

    now = time.time()
    with _lock:
        _prune(now)
        entry = _sessions.get(session_id)
        if entry is None:
            return None

        entry["expires_at"] = now + SESSION_TTL_SECONDS
        return entry["credentials"]


def _merge(old: str | None, new: str | None) -> str | None:
    """Keep the existing value when the new value is blank or omitted."""
    return new.strip() if new and new.strip() else old


def store_credentials(
    session_id: str,
    gemini_api_key: str | None = None,
    database_url: str | None = None,
) -> Credentials:
    now = time.time()

    with _lock:
        _prune(now)
        existing = _sessions.get(session_id, {}).get(
            "credentials", Credentials()
        )

        credentials = Credentials(
            gemini_api_key=_merge(
                existing.gemini_api_key, gemini_api_key
            ),
            database_url=_merge(existing.database_url, database_url),
        )

        _sessions[session_id] = {
            "credentials": credentials,
            "expires_at": now + SESSION_TTL_SECONDS,
        }
        return credentials


def clear_credentials(session_id: str) -> None:
    with _lock:
        _sessions.pop(session_id, None)