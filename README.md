# SmartTrip AI - A Budget-Aware Multi-Agent AI Travel Planner

**Domain:** Artificial Intelligence, Generative AI, Multi-Agent Systems

SmartTrip AI is a college mini-project that uses a multi-agent AI workflow to help users plan trips, explore travel options, organize day-by-day itineraries, and understand estimated travel costs.

The project builds on the open-source TravelBrain project and adds budget-analysis functionality, deterministic cost calculations, clearer budget status reporting, and a demo mode that can be explored without making AI API calls.

## Features

* **Multi-agent planning:** Separate agents handle travel research and itinerary generation.
* **Travel information:** Supports flight-related information, accommodation research, and weather information through configured services.
* **Day-by-day itinerary:** Organizes suggested activities into a travel plan.
* **Budget analysis:** Calculates estimated expenses, compares the total with the user's budget, and identifies missing cost categories.
* **Three budget outcomes:**

  * Within budget
  * Slightly over budget
  * Significantly over budget
* **Demo trip:** Explore a sample trip without calling the AI planning workflow.
* **Automated tests:** Tests important budget calculations and validation cases.

## Technology Stack

* Python
* LangChain and LangGraph
* FastAPI
* PostgreSQL
* HTML, CSS, and JavaScript
* pytest
* uv for Python dependency management

## Requirements

* Python 3.11 or later
* [uv](https://docs.astral.sh/uv/)
* PostgreSQL configured for the application
* API credentials for the external services used by the AI workflow

## Installation

Clone the repository:

```bash
git clone https://github.com/KalyanM45/TravelBrain-Multi-Agent-AI-Travel-Planner.git
cd TravelBrain-Multi-Agent-AI-Travel-Planner
```

Install the project dependencies:

```bash
uv sync
```

Create a `.env` file in the project root and configure the variables expected by the application. Consult the application's configuration code for the exact required names and values.

Never publish API keys, database passwords, or other secrets.

## Run the Application

Start the server:

```bash
uv run python app.py
```

Open http://127.0.0.1:8000 in your browser.

Use the demo-trip option to explore the sample interface without triggering the AI trip-planning workflow. Demo figures are illustrative and are not verified travel prices.

## Run the Tests

Install the development dependencies:

```bash
uv sync --dev
```

Run the budget utility tests:

```bash
uv run pytest tests/test_budget_utils.py -v
```

The tests cover budget status calculations, exact-budget handling, budget extraction, invalid negative amounts, expense extraction, and missing-budget reporting.

## Budget Calculation Rules

The budget utility classifies a calculated trip total as follows:

| Status                    | Rule                                                            |
| ------------------------- | --------------------------------------------------------------- |
| Within budget             | Estimated total is less than or equal to the target budget      |
| Slightly over budget      | Estimated total is above the target and no more than 110% of it |
| Significantly over budget | Estimated total exceeds 110% of the target                      |

These classifications are calculated by Python code. Their usefulness depends on the accuracy and completeness of the cost estimates supplied to the calculation.

## Important Limitations

* AI-generated travel recommendations may contain errors.
* Prices and availability should be independently verified before booking.
* An estimated cost is not a booking confirmation.
* Live AI planning depends on valid API credentials, provider availability, and usage quotas.
* A successful local unit test does not prove that every external integration works end to end.

## Future Improvements

* More reliable structured extraction of travel costs
* Better handling of incomplete budget categories
* Expanded automated tests for the agent workflow
* Improved validation of itinerary duration
* More robust error handling for external API failures

## License

Licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE).

