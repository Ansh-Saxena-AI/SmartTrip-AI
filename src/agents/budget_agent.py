"""Analyzes trip cost, budget status, and cost-cutting options."""

from langchain_core.messages import HumanMessage, SystemMessage

from src.utils.budget_utils import (
    extract_budget,
    extract_costs_from_text,
    format_budget_analysis,
)

from src.clients.llm import get_llm
from src.graph.state import TravelState
from src.utils.async_utils import bump_llm_calls


BUDGET_SYSTEM_PROMPT = """
You are a careful travel budget analyst.

Analyze the complete trip budget in Indian Rupees (INR).

Account for:

* Round-trip transportation for the entire group
* Accommodation for the correct number of nights
* Food for every traveller and day
* Local transportation
* Activities and entry fees
* Taxes and miscellaneous expenses
* A reasonable contingency amount

BUDGET RULES:

* Treat the user's stated budget as the maximum spending target.
* Clearly distinguish live-verified prices, sourced estimates, and unverified estimates.
* Never invent exact fares, hotel rates, ticket prices, or booking availability.
* If reliable prices are unavailable, use clearly labelled estimates or state that the cost is unknown.
* Do not describe estimates as actual or confirmed expenses.
* State the assumptions used, including traveller count, trip duration, and accommodation nights.
* Avoid double-counting expenses already included in package or ticket prices.
* Show each expense as a numeric INR amount where a reasonable estimate is possible.
* Make the total equal the sum of all listed expense categories.
* Calculate the difference as estimated total minus target budget.
* Calculate remaining budget as target budget minus estimated total.
* If important costs are unknown, explicitly mark the estimate as incomplete.
* Never claim affordability is confirmed when essential costs are missing.

Classify the budget as:

* WITHIN BUDGET: estimated total is at or below the target.
* SLIGHTLY OVER BUDGET: estimated total is more than the target but no more than 110% of it.
* SIGNIFICANTLY OVER BUDGET: estimated total is above 110% of the target.

If the estimate exceeds the target, suggest 2-4 practical ways to reduce costs.
Give potential savings as estimates, and do not subtract the same saving twice.

Use this structure:

BUDGET ANALYSIS
Target Budget: ₹...
Estimated Total: ₹...
Difference (estimated total - target): ₹...
Remaining Budget (target - estimated total): ₹...
Status: ...
Estimate Completeness: COMPLETE or INCOMPLETE
Assumptions: ...

COST BREAKDOWN

* Round-trip transportation: ₹...
* Accommodation: ₹...
* Food: ₹...
* Local transportation: ₹...
* Activities and entry fees: ₹...
* Taxes and miscellaneous: ₹...
* Contingency: ₹...
* TOTAL: ₹...

SMART COST-CUTTING SUGGESTIONS

1. Suggestion — potential saving: ₹...
2. Suggestion — potential saving: ₹...

Potential Savings: ₹...
Possible Revised Total: ₹...
Revised Status: ...

IMPORTANT:
These are planning estimates, not a booking confirmation.
Do not fabricate live data or present unsupported prices as verified.
If a cost cannot be reasonably estimated, state that it is unknown.
"""




def budget_agent(state: TravelState):
    prompt = f"""
User's request:
{state["user_query"]}

Flight information:
{state["flight_results"]}

Hotel information:
{state["hotel_results"]}

Weather information:
{state["weather_results"]}

Itinerary:
{state["itinerary"]}

Prepare a practical budget estimate for the entire group.

Return the cost breakdown in INR. Clearly label estimated, sourced,
and live-verified prices. Do not invent exact prices.

Include these categories:
- Round-trip transportation
- Accommodation
- Food
- Local transportation
- Activities and entry fees
- Taxes and miscellaneous
- Contingency

State any missing costs and assumptions. Do not claim the trip is
affordable if essential expenses are unknown.

Provide cost-saving suggestions, but avoid claiming that savings
are guaranteed.
"""
    budget_target = extract_budget(state["user_query"])

    response = get_llm().invoke([
        SystemMessage(content=BUDGET_SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ])

    
    budget_text = response.content

    budget_costs = extract_costs_from_text(budget_text)

    calculated_analysis = format_budget_analysis(
        budget_target,
        budget_costs,
)

    return {
        "budget_analysis": calculated_analysis,
        "budget_target": budget_target,
        "budget_costs": budget_costs,
        "messages": [response],
        "llm_calls": bump_llm_calls(state),
    }