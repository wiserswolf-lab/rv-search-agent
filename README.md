# RV Search Agent

An AI agent for searching and analyzing RV listings. Works out of the box with demo data - no API keys required!

## Quick Start

```bash
cd ~/Desktop/rv-search-agent
python3 -m venv venv
source venv/bin/activate
pip install anthropic httpx python-dotenv
```

## Command Line Interface

The easiest way to search for RVs:

```bash
# Search for Storyteller Overland
./rv-search -q "Storyteller"

# Search Facebook Marketplace only, 2024+
./rv-search -q "Storyteller" --min-year 2024 -s "Facebook"

# Search Class C under $100k
./rv-search -t "Class C" --max-price 100000

# Open Facebook Marketplace search in browser
./rv-search -q "Storyteller Overland" --open-fb

# Open RV Trader search in browser
./rv-search -q "Storyteller Overland" --open-rvtrader

# Verbose output with full details
./rv-search -q "Storyteller" -v

# Show help
./rv-search --help
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-q, --query` | Search query (make, model, keywords) |
| `-t, --type` | RV type (Class A, B, C, Travel Trailer, Fifth Wheel) |
| `--min-price` | Minimum price |
| `--max-price` | Maximum price |
| `--min-year` | Minimum year |
| `--max-year` | Maximum year |
| `-l, --location` | Location filter |
| `-s, --source` | Source filter (Dealer, Facebook Marketplace) |
| `-n, --max-results` | Number of results (default: 10) |
| `-v, --verbose` | Show detailed listing information |
| `--open-fb` | Open Facebook Marketplace search in browser |
| `--open-rvtrader` | Open RV Trader search in browser |

## Python API

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
| `source` | Listing source | `"Dealer"`, `"Facebook Marketplace"` |
| `max_results` | Number of results | `10` |

### Filter by Source

```python
# Facebook Marketplace only (private sellers, often lower prices)
listings = search_rv_listings(
    query='Storyteller',
    source='Facebook Marketplace'
)

# Dealer listings only
listings = search_rv_listings(
    query='Storyteller',
    source='Dealer'
)
```

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
├── rv-search              # CLI wrapper script
├── src/rv_search_agent/
│   ├── __init__.py
│   ├── agent.py           # Claude-powered agent
│   ├── cli.py             # Command-line interface
│   ├── models.py          # RVListing data model
│   └── search_api.py      # Search with demo data + Craigslist RSS
├── .env.example
├── pyproject.toml
└── README.md
```

## Demo Data

The demo mode includes 28 sample listings covering:

**Sources:**
- 10 Dealer listings
- 8 Facebook Marketplace listings (with mileage)

**Storyteller Overland Models:**
- Classic MODE (OG & XO)
- Beast MODE (OG & XO)
- Stealth MODE
- Dark MODE

**Other Brands:**
- Winnebago, Thor, Jayco, Airstream, Coachmen, Fleetwood, etc.

**Types:** Class A, B, C motorhomes, Travel Trailers, Fifth Wheels

**Price Range:** $42,000 - $239,000

**Years:** 2019 - 2025
