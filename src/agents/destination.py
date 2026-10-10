"""Pulls the destination out of a free-form travel query."""

from src.agents.prompts import DESTINATION_EXTRACTION_PROMPT
from src.clients.cache import cached
from src.clients.llm import get_llm
from src.config.settings import CACHE_TTL_DESTINATION


@cached(prefix="destination", ttl=CACHE_TTL_DESTINATION)
def extract_destination(query: str) -> str:
    """
    Cached: the same query always maps to the same destination.
    """

    prompt = DESTINATION_EXTRACTION_PROMPT.format(query=query)
    response = get_llm().invoke(prompt)
    content = response.content

    if isinstance(content, str):
        destination = content.strip()

    elif isinstance(content, list):
        destination = "".join(
            item if isinstance(item, str)
            else item.get("text", "")
            if isinstance(item, dict)
            and isinstance(item.get("text"), str)
            else ""
            for item in content
        ).strip()

    else:
        destination = ""

    if not destination:
        raise ValueError("Gemini returned no usable destination text.")

    return destination
