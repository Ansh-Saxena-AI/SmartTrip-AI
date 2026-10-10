"""Shared state passed between every node of the travel graph."""

import operator
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage


class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    weather_results: str
    budget_analysis: str
    budget_costs: dict[str, float]
    budget_target: float | None
    llm_calls: Annotated[int, operator.add]


def initial_state(user_query: str) -> TravelState:
    """Build the empty state the graph starts from."""

    from langchain_core.messages import HumanMessage

    return {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "flight_results": "",
        "hotel_results": "",
        "weather_results": "",
        "itinerary": "",
        "budget_analysis": "",
        "budget_costs": {},
        "budget_target": None,
        "llm_calls": 0,
    }
