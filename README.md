# RV Search Agent

An AI agent for searching and analyzing RV listings. Works out of the box with demo data - no API keys required!

## Quick Start

```bash
cd ~/Desktop/rv-search-agent
python3 -m venv venv
source venv/bin/activate
pip install anthropic httpx python-dotenv
```

## Usage

### Search for RVs (Demo Mode - No API Key Required)

```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from rv_search_agent import search_rv_listings

# Search for Class C RVs under \$100k
listings = search_rv_listings(
    rv_type='Class C',
    max_price=100000
)

for listing in listings:
    print(f'{listing.title} - \${listing.price:,}')
    print(f'  {listing.location}')
    print()
"
```

### Search Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Make, model, or keywords | `"Storyteller"`, `"Winnebago"` |
| `rv_type` | Type of RV | `"Class A"`, `"Class B"`, `"Class C"`, `"Travel Trailer"`, `"Fifth Wheel"` |
| `min_price` | Minimum price | `50000` |
| `max_price` | Maximum price | `150000` |
| `min_year` | Minimum year | `2020` |
| `max_year` | Maximum year | `2024` |
| `location` | Location filter | `"California"`, `"Denver"` |
| `max_results` | Number of results | `10` |

### Use the AI Agent (Requires Anthropic API Key)

```bash
# Set your API key
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run the agent
python3 -c "
import sys
sys.path.insert(0, 'src')
from rv_search_agent import run_agent

response = run_agent('Find me Class C RVs under \$100,000')
print(response)
"
```

### Live Craigslist Search (From Home Network)

The demo mode uses sample data. To search live Craigslist listings, run from your home network:

```bash
DEMO_MODE=false python3 -c "
import sys
sys.path.insert(0, 'src')
from rv_search_agent import search_rv_listings

listings = search_rv_listings(
    query='motorhome',
    location='losangeles',
    max_results=10
)

for listing in listings:
    print(f'{listing.title}')
    print(f'  {listing.url}')
    print()
"
```

**Note:** Craigslist blocks requests from cloud servers. Live search works from home/residential IPs.

## Project Structure

```
rv-search-agent/
├── src/rv_search_agent/
│   ├── __init__.py
│   ├── agent.py        # Claude-powered agent
│   ├── models.py       # RVListing data model
│   └── search_api.py   # Search with demo data + Craigslist RSS
├── .env.example
├── pyproject.toml
└── README.md
```

## Demo Data

The demo mode includes 12 sample listings covering:
- Class A, B, C motorhomes
- Travel trailers and fifth wheels
- Popular brands: Winnebago, Thor, Jayco, Airstream, Storyteller Overland, etc.
- Price range: $42,000 - $225,000
- Years: 2019 - 2024
