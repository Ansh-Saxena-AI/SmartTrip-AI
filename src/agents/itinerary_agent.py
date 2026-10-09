
"""Combines flight, hotel and weather results into a day-by-day itinerary."""

import re

from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.prompts import ITINERARY_AGENT_PROMPT, ITINERARY_SYSTEM_PROMPT
from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.utils.async_utils import bump_llm_calls


def get_requested_days(user_query: str) -> int | None:
    """Extract an explicitly requested trip duration."""
    patterns = [
        r"\b(\d+)\s*[- ]?\s*days?\b",
        r"\b(\d+)\s*[- ]?\s*nights?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, user_query, re.IGNORECASE)
        if match:
            return int(match.group(1))

    return None


def get_itinerary_days(itinerary: str) -> list[int]:
    """Find day numbers in itinerary headings."""
    matches = re.findall(
        r"^\s{0,3}#{0,3}\s*Day\s+(\d+)\b",
        itinerary,
        re.IGNORECASE | re.MULTILINE,
    )
    return [int(day) for day in matches]


def itinerary_agent(state: TravelState):
    prompt = ITINERARY_AGENT_PROMPT.format(
        user_query=state["user_query"],
        flight_results=state["flight_results"],
        hotel_results=state["hotel_results"],
        weather_results=state["weather_results"],
    )

    response = get_llm().invoke([
        SystemMessage(content=ITINERARY_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    itinerary = response.content
    requested_days = get_requested_days(state["user_query"])
    generated_days = get_itinerary_days(itinerary)

    if requested_days and generated_days != list(range(1, requested_days + 1)):
        itinerary += (
            "\n\n**Planning validation warning:** The generated day headings "
            f"({generated_days}) do not match the requested {requested_days}-day "
            "duration. Please verify the itinerary before relying on it."
        )

    return {
        "itinerary": itinerary,
        "messages": [response],
        "llm_calls": bump_llm_calls(state),
    }