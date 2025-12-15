"""Main agent implementation for RV search."""

import json

import anthropic
from dotenv import load_dotenv

from .search_api import search_rv_listings, SearchAPIError

load_dotenv()

TOOLS = [
    {
        "name": "search_rv_listings",
        "description": "Search for RV listings from online marketplaces using Google Search. Returns a list of RV listings with details like price, year, make, model, and location.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query or keyword (e.g., 'Winnebago View', 'Storyteller Overland XO')",
                },
                "rv_type": {
                    "type": "string",
                    "description": "Type of RV (e.g., 'Class A', 'Class B', 'Class C', 'travel trailer', 'fifth wheel')",
                },
                "min_price": {
                    "type": "integer",
                    "description": "Minimum price filter",
                },
                "max_price": {
                    "type": "integer",
                    "description": "Maximum price filter",
                },
                "min_year": {
                    "type": "integer",
                    "description": "Minimum year filter",
                },
                "max_year": {
                    "type": "integer",
                    "description": "Maximum year filter",
                },
                "location": {
                    "type": "string",
                    "description": "Location to search near (e.g., 'California', 'Denver, CO')",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 10)",
                },
            },
            "required": [],
        },
    }
]

SYSTEM_PROMPT = """You are an RV search assistant that helps users find and analyze RV listings. You have access to a tool that can search for RV listings across the web.

When users ask about finding RVs:
1. Use the search_rv_listings tool to find relevant listings
2. Analyze the results and present them in a helpful format
3. Provide insights about pricing, value, and what to look for

You can filter by:
- Query terms (make, model, keywords)
- RV type (Class A, B, C, travel trailer, fifth wheel)
- Price range
- Year range
- Location

Always be helpful and provide actionable information about the RV market. Include listing URLs when available so users can view the full details."""


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process a tool call and return the result."""
    if tool_name == "search_rv_listings":
        try:
            listings = search_rv_listings(
                query=tool_input.get("query"),
                rv_type=tool_input.get("rv_type"),
                min_price=tool_input.get("min_price"),
                max_price=tool_input.get("max_price"),
                min_year=tool_input.get("min_year"),
                max_year=tool_input.get("max_year"),
                location=tool_input.get("location"),
                max_results=tool_input.get("max_results", 10),
            )

            if not listings:
                return json.dumps({
                    "results": [],
                    "message": "No listings found matching your criteria. Try broadening your search."
                })

            results = [listing.to_dict() for listing in listings]
            return json.dumps({"results": results, "count": len(results)})

        except SearchAPIError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            return json.dumps({"error": f"Unexpected error: {str(e)}"})

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def create_agent():
    """Create and return an Anthropic client for the agent."""
    return anthropic.Anthropic()


def run_agent(query: str) -> str:
    """
    Run the RV search agent with the given query.

    Args:
        query: The user's search query about RVs

    Returns:
        The agent's response
    """
    client = create_agent()
    messages = [{"role": "user", "content": query}]

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    while response.stop_reason == "tool_use":
        tool_use_block = next(
            block for block in response.content if block.type == "tool_use"
        )

        tool_result = process_tool_call(tool_use_block.name, tool_use_block.input)

        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": tool_result,
                }
            ],
        })

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

    text_blocks = [block.text for block in response.content if hasattr(block, "text")]
    return "\n".join(text_blocks)


if __name__ == "__main__":
    response = run_agent("Find me 2024 Storyteller Overland XO Classic RVs")
    print(response)
