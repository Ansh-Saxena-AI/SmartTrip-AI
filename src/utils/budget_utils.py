
"""Deterministic helpers for travel budget calculations."""

import re


def extract_budget(user_query: str) -> float | None:
    """Extract an explicitly stated budget from the user's request."""
    patterns = [
        r"\b(?:budget(?:\s+of)?|under|within|maximum(?:\s+budget)?)\s*"
        r"(?:₹|rs\.?)?\s*([\d,]+(?:\.\d+)?)\s*(k\b)?",
        r"(?:₹|rs\.?)\s*([\d,]+(?:\.\d+)?)\s*(k\b)?",
    ]

    for pattern in patterns:
        match = re.search(pattern, user_query, re.IGNORECASE)
        if match:
            amount = float(match.group(1).replace(",", ""))
            if match.group(2) and match.group(2).lower() == "k":
                amount *= 1000
            return amount

    return None


def calculate_budget(budget: float, costs: dict[str, float]) -> dict:
    """Calculate totals and budget status from supplied cost estimates."""
    if budget < 0:
        raise ValueError("Budget cannot be negative.")

    if any(
        not isinstance(cost, (int, float))
        or isinstance(cost, bool)
        or cost < 0
        for cost in costs.values()
    ):
        raise ValueError("All costs must be non-negative numbers.")

    total = sum(costs.values())
    difference = total - budget

    if total <= budget:
        status = "WITHIN BUDGET"
    elif total <= budget * 1.10:
        status = "SLIGHTLY OVER BUDGET"
    else:
        status = "SIGNIFICANTLY OVER BUDGET"

    return {
        "target_budget": round(budget, 2),
        "estimated_total": round(total, 2),
        "difference": round(difference, 2),
        "remaining_budget": round(budget - total, 2),
        "status": status,
    }


def format_budget_analysis(
    budget: float | None,
    costs: dict[str, float],
    ai_analysis: str = "",
) -> str:
    """Format budget results using Python-calculated totals."""
    if budget is None:
        return (
            "Budget analysis: INCOMPLETE — "
            "no explicit budget was provided.\n\n"
            + ai_analysis
        )

    if not costs:
        return (
            f"Target Budget: ₹{budget:,.2f}\n"
            "Estimated Total: Unknown\n"
            "Difference: Unknown\n"
            "Remaining Budget: Unknown\n"
            "Status: INCOMPLETE — no structured expense estimates available.\n"
            "Do not treat the trip as affordable until essential costs "
            "have been estimated or verified.\n\n"
            + ai_analysis
        )

    result = calculate_budget(budget, costs)
    required_categories = {
        "Round-trip transportation",
        "Accommodation",
        "Food",
        "Local transportation",
        "Activities and entry fees",
        "Taxes and miscellaneous",
        "Contingency",
    }

    missing_categories = required_categories - costs.keys()
    complete = not missing_categories

    lines = [
        "BUDGET ANALYSIS",
        f"Target Budget: ₹{result['target_budget']:,.2f}",
        f"Estimated Total: ₹{result['estimated_total']:,.2f}",
        f"Difference (estimated total - target): "
        f"₹{result['difference']:,.2f}",
        f"Remaining Budget: ₹{result['remaining_budget']:,.2f}",
        f"Status: {result['status'] if complete else 'INCOMPLETE — required costs missing'}",
        f"Missing categories: {', '.join(sorted(missing_categories)) if missing_categories else 'None'}",
        "Estimate Completeness: INCOMPLETE — extracted amounts "
        "must be checked against reliable sources.",
        "All extracted amounts are unverified estimates unless "
        "independently verified.",
        "",
        "COST BREAKDOWN",
    ]

    lines.extend(
        f"- {name}: ₹{amount:,.2f}"
        for name, amount in costs.items()
    )

    lines.extend([
        "",
        "AI ANALYSIS, ASSUMPTIONS AND COST-SAVING SUGGESTIONS",
        ai_analysis or "No additional analysis was provided.",
    ])

    return "\n".join(lines)

def extract_costs_from_text(text: str) -> dict[str, float]:
    """Extract labelled expense estimates from budget analysis."""
    categories = {
        "Round-trip transportation": r"round[- ]trip transportation",
        "Accommodation": r"accommodation",
        "Food": r"food",
        "Local transportation": r"local transportation",
        "Activities and entry fees": r"activities and entry fees",
        "Taxes and miscellaneous": r"taxes and miscellaneous",
        "Contingency": r"contingency",
    }

    costs = {}

    for name, label_pattern in categories.items():
        pattern = (
            rf"^\s*(?:[-*]\s*)?{label_pattern}\s*:\s*"
            rf"(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d+)?)"
        )
        match = re.search(
            pattern,
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if match:
            costs[name] = float(match.group(1).replace(",", ""))

    return costs

