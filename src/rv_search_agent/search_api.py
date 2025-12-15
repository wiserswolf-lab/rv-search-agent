"""RV listing search with demo mode and Craigslist RSS support."""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from typing import Optional, List
from urllib.parse import urlencode

import httpx

from .models import RVListing


class SearchAPIError(Exception):
    """Exception for search API errors."""
    pass


# Sample data for demo mode
DEMO_LISTINGS = [
    # Storyteller Overland - Dealer listings
    RVListing(
        title="2024 Storyteller Overland Classic MODE XO AWD",
        price=189000,
        year=2024,
        make="Storyteller",
        model="Classic MODE XO",
        location="Los Angeles, CA",
        url="https://example.com/listing/1",
        rv_type="Class B",
        description="Like new! Lithionics battery system, Mercedes Sprinter AWD chassis, 8.4kWh lithium, solar ready.",
        source="Dealer",
    ),
    RVListing(
        title="2025 Storyteller Overland Beast MODE XO AWD",
        price=239000,
        year=2025,
        make="Storyteller",
        model="Beast MODE XO",
        location="Thousand Oaks, CA",
        url="https://example.com/listing/13",
        rv_type="Class B",
        description="New! 16.8kWh M-Power Lithionics system, Mercedes Sprinter 2500 AWD, high output alternator, 325W solar capable.",
        source="Dealer",
    ),
    RVListing(
        title="2025 Storyteller Overland Beast MODE OG AWD",
        price=225000,
        year=2025,
        make="Storyteller",
        model="Beast MODE OG",
        location="Denver, CO",
        url="https://example.com/listing/14",
        rv_type="Class B",
        description="Stone Gray, 16.8kWh Lithionics, Mercedes Sprinter AWD, GrooveLounge, Halo shower system. $15K rebate available!",
        source="Dealer",
    ),
    RVListing(
        title="2024 Storyteller Overland Stealth MODE 4x4",
        price=205000,
        year=2024,
        make="Storyteller",
        model="Stealth MODE",
        location="Seattle, WA",
        url="https://example.com/listing/15",
        rv_type="Class B",
        description="16.8kWh M-Power system, blacked-out exterior, Mercedes Sprinter 4x4, expedition-ready, 90W solar expandable to 325W.",
        source="Dealer",
    ),
    RVListing(
        title="2025 Storyteller Overland Dark MODE OG AWD",
        price=210000,
        year=2025,
        make="Storyteller",
        model="Dark MODE OG",
        location="Portland, OR",
        url="https://example.com/listing/16",
        rv_type="Class B",
        description="New 2025! 16.8kWh Lithionics system, Mercedes Sprinter turbo diesel AWD, dark interior theme, premium audio.",
        source="Dealer",
    ),
    RVListing(
        title="2024 Storyteller Overland Classic MODE OG AWD",
        price=179000,
        year=2024,
        make="Storyteller",
        model="Classic MODE OG",
        location="Austin, TX",
        url="https://example.com/listing/17",
        rv_type="Class B",
        description="8.4kWh Lithionics battery, Mercedes Sprinter AWD, GrooveLounge convertible seating, indoor/outdoor shower.",
        source="Dealer",
    ),
    RVListing(
        title="2024 Storyteller Overland Beast MODE XO - Used",
        price=199000,
        year=2024,
        make="Storyteller",
        model="Beast MODE XO",
        location="Phoenix, AZ",
        url="https://example.com/listing/18",
        rv_type="Class B",
        description="Excellent condition, 12K miles, 16.8kWh Lithionics, Mercedes Sprinter AWD, extended warranty available.",
        source="Dealer",
    ),
    RVListing(
        title="2023 Storyteller Overland Stealth MODE 4x4 - Used",
        price=175000,
        year=2023,
        make="Storyteller",
        model="Stealth MODE",
        location="San Diego, CA",
        url="https://example.com/listing/19",
        rv_type="Class B",
        description="One owner, 18K miles, full service history, 16.8kWh battery, blacked-out trim, upgraded solar.",
        source="Dealer",
    ),
    RVListing(
        title="2022 Storyteller Overland Stealth MODE 4x4 - Used",
        price=145000,
        year=2022,
        make="Storyteller",
        model="Stealth MODE",
        location="St. Petersburg, FL",
        url="https://example.com/listing/20",
        rv_type="Class B",
        description="Well maintained, 28K miles, new tires, lithium battery system, Mercedes Sprinter 4x4.",
        source="Dealer",
    ),
    RVListing(
        title="2025 Storyteller Overland Classic MODE XO AWD",
        price=195000,
        year=2025,
        make="Storyteller",
        model="Classic MODE XO",
        location="Atlanta, GA",
        url="https://example.com/listing/21",
        rv_type="Class B",
        description="Brand new 2025! 8.4kWh M-Power system, Mercedes Sprinter 2500 AWD, improved galley, softer mattress.",
        source="Dealer",
    ),
    # Storyteller Overland - Facebook Marketplace listings (private sellers)
    RVListing(
        title="2024 Storyteller Overland Beast MODE XO",
        price=185000,
        year=2024,
        make="Storyteller",
        model="Beast MODE XO",
        location="San Jose, CA",
        url="https://facebook.com/marketplace/item/example1",
        rv_type="Class B",
        mileage=8500,
        description="Selling my Beast MODE! 8.5K miles, garage kept, 16.8kWh Lithionics, all maintenance done at dealer. No accidents. Moving overseas.",
        source="Facebook Marketplace",
    ),
    RVListing(
        title="2024 Storyteller Overland Classic MODE OG",
        price=159000,
        year=2024,
        make="Storyteller",
        model="Classic MODE OG",
        location="Scottsdale, AZ",
        url="https://facebook.com/marketplace/item/example2",
        rv_type="Class B",
        mileage=15000,
        description="Downsizing - must sell! 15K miles, 8.4kWh battery, added 200W solar, WeBoost cell booster. Clean title, all records.",
        source="Facebook Marketplace",
    ),
    RVListing(
        title="2025 Storyteller Overland Stealth MODE 4x4",
        price=192000,
        year=2025,
        make="Storyteller",
        model="Stealth MODE",
        location="Boulder, CO",
        url="https://facebook.com/marketplace/item/example3",
        rv_type="Class B",
        mileage=3200,
        description="Barely used 2025 Stealth! Only 3.2K miles. 16.8kWh system, blacked out, Owl cam security. Bought new in Sept. Health issues forcing sale.",
        source="Facebook Marketplace",
    ),
    RVListing(
        title="2024 Storyteller Overland Dark MODE OG AWD",
        price=178000,
        year=2024,
        make="Storyteller",
        model="Dark MODE OG",
        location="Nashville, TN",
        url="https://facebook.com/marketplace/item/example4",
        rv_type="Class B",
        mileage=11000,
        description="Dark MODE with all the upgrades! 11K miles, Espar heater, MaxxFan, 325W solar, Starlink ready. Priced to sell quick!",
        source="Facebook Marketplace",
    ),
    RVListing(
        title="2023 Storyteller Overland Beast MODE XO 4x4",
        price=169000,
        year=2023,
        make="Storyteller",
        model="Beast MODE XO",
        location="Raleigh, NC",
        url="https://facebook.com/marketplace/item/example5",
        rv_type="Class B",
        mileage=22000,
        description="22K miles, full service history at Mercedes dealer. 16.8kWh battery, new tires, ARB awning added. Great condition!",
        source="Facebook Marketplace",
    ),
    RVListing(
        title="2024 Storyteller Overland Classic MODE XO",
        price=172000,
        year=2024,
        make="Storyteller",
        model="Classic MODE XO",
        location="Tampa, FL",
        url="https://facebook.com/marketplace/item/example6",
        rv_type="Class B",
        mileage=6800,
        description="Like new Classic MODE XO! 6.8K miles, 8.4kWh Lithionics, Halo shower, GrooveLounge. Extended warranty transfers!",
        source="Facebook Marketplace",
    ),
    RVListing(
        title="2025 Storyteller Beast MODE OG - LIKE NEW",
        price=208000,
        year=2025,
        make="Storyteller",
        model="Beast MODE OG",
        location="Sacramento, CA",
        url="https://facebook.com/marketplace/item/example7",
        rv_type="Class B",
        mileage=1200,
        description="1,200 miles! Bought for cross-country trip that got cancelled. Stone gray, 16.8kWh, still smells new. Save $20K off MSRP!",
        source="Facebook Marketplace",
    ),
    RVListing(
        title="2022 Storyteller Overland Classic MODE 4x4",
        price=135000,
        year=2022,
        make="Storyteller",
        model="Classic MODE",
        location="Albuquerque, NM",
        url="https://facebook.com/marketplace/item/example8",
        rv_type="Class B",
        mileage=35000,
        description="Well-loved Classic MODE! 35K miles, runs perfect, new brakes, lithium battery in great shape. Ready for adventure!",
        source="Facebook Marketplace",
    ),
    # Other RV listings
    RVListing(
        title="2023 Winnebago View 24D Class C",
        price=145000,
        year=2023,
        make="Winnebago",
        model="View 24D",
        location="San Diego, CA",
        url="https://example.com/listing/2",
        rv_type="Class C",
        description="Mercedes diesel chassis, only 12k miles, full warranty remaining.",
    ),
    RVListing(
        title="2022 Thor Four Winds 28A Class C Motorhome",
        price=89500,
        year=2022,
        make="Thor",
        model="Four Winds 28A",
        location="Phoenix, AZ",
        url="https://example.com/listing/3",
        rv_type="Class C",
        description="Ford E-450 chassis, sleeps 8, outdoor entertainment center.",
    ),
    RVListing(
        title="2024 Airstream Interstate 24GT Touring Coach",
        price=225000,
        year=2024,
        make="Airstream",
        model="Interstate 24GT",
        location="Denver, CO",
        url="https://example.com/listing/4",
        rv_type="Class B",
        description="Brand new, Mercedes Sprinter 3500, lithium batteries, leather interior.",
    ),
    RVListing(
        title="2021 Jayco Redhawk 31F Class C",
        price=79900,
        year=2021,
        make="Jayco",
        model="Redhawk 31F",
        location="Seattle, WA",
        url="https://example.com/listing/5",
        rv_type="Class C",
        description="Ford chassis, bunk beds, outdoor kitchen, 24k miles.",
    ),
    RVListing(
        title="2023 Coachmen Beyond 22C AWD Class B+",
        price=165000,
        year=2023,
        make="Coachmen",
        model="Beyond 22C",
        location="Portland, OR",
        url="https://example.com/listing/6",
        rv_type="Class B",
        description="Ford Transit AWD, EcoBoost, murphy bed, solar panels.",
    ),
    RVListing(
        title="2020 Fleetwood Flair 29M Class A Gas",
        price=95000,
        year=2020,
        make="Fleetwood",
        model="Flair 29M",
        location="Dallas, TX",
        url="https://example.com/listing/7",
        rv_type="Class A",
        description="Ford F-53 chassis, king bed, washer/dryer prep, 32k miles.",
    ),
    RVListing(
        title="2024 Grand Design Reflection 315RLTS Fifth Wheel",
        price=72000,
        year=2024,
        make="Grand Design",
        model="Reflection 315RLTS",
        location="Austin, TX",
        url="https://example.com/listing/8",
        rv_type="Fifth Wheel",
        description="Rear living, theater seating, king bed, solar prep.",
    ),
    RVListing(
        title="2022 Keystone Montana 3761FL Fifth Wheel",
        price=85000,
        year=2022,
        make="Keystone",
        model="Montana 3761FL",
        location="Chicago, IL",
        url="https://example.com/listing/9",
        rv_type="Fifth Wheel",
        description="Front living, 4 slides, residential fridge, fireplace.",
    ),
    RVListing(
        title="2023 Forest River Rockwood 2706WS Travel Trailer",
        price=42000,
        year=2023,
        make="Forest River",
        model="Rockwood 2706WS",
        location="Miami, FL",
        url="https://example.com/listing/10",
        rv_type="Travel Trailer",
        description="Murphy bed, outdoor kitchen, solar ready, aluminum frame.",
    ),
    RVListing(
        title="2019 Newmar Bay Star 3226 Class A Gas",
        price=115000,
        year=2019,
        make="Newmar",
        model="Bay Star 3226",
        location="Atlanta, GA",
        url="https://example.com/listing/11",
        rv_type="Class A",
        description="Ford chassis, full paint, 2 slides, king bed, 28k miles.",
    ),
    RVListing(
        title="2024 Pleasure-Way Plateau TS Class B",
        price=198000,
        year=2024,
        make="Pleasure-Way",
        model="Plateau TS",
        location="San Francisco, CA",
        url="https://example.com/listing/12",
        rv_type="Class B",
        description="Ford Transit, twin beds convert to king, 600W solar.",
    ),
]


# Craigslist regions
CRAIGSLIST_REGIONS = {
    "sfbay": "San Francisco Bay Area",
    "losangeles": "Los Angeles",
    "sandiego": "San Diego",
    "seattle": "Seattle",
    "portland": "Portland",
    "denver": "Denver",
    "phoenix": "Phoenix",
    "dallas": "Dallas",
    "houston": "Houston",
    "austin": "Austin",
    "chicago": "Chicago",
    "miami": "Miami",
    "atlanta": "Atlanta",
    "boston": "Boston",
    "newyork": "New York",
    "lasvegas": "Las Vegas",
}


def search_rv_listings(
    query: Optional[str] = None,
    rv_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    location: Optional[str] = None,
    max_results: int = 20,
    demo_mode: Optional[bool] = None,
) -> List[RVListing]:
    """
    Search for RV listings.

    Uses demo data by default, or Craigslist RSS feeds when DEMO_MODE=false.

    Args:
        query: Search query (e.g., "Winnebago", "Storyteller Overland")
        rv_type: Type of RV (e.g., "Class A", "Class B", "Class C")
        min_price: Minimum price filter
        max_price: Maximum price filter
        min_year: Minimum year filter
        max_year: Maximum year filter
        location: Region/location to search
        max_results: Maximum number of results (default 20)
        demo_mode: Force demo mode on/off (default: auto-detect)

    Returns:
        List of RVListing objects
    """
    # Determine if we should use demo mode
    if demo_mode is None:
        demo_mode = os.getenv("DEMO_MODE", "true").lower() != "false"

    if demo_mode:
        return _search_demo(
            query=query,
            rv_type=rv_type,
            min_price=min_price,
            max_price=max_price,
            min_year=min_year,
            max_year=max_year,
            location=location,
            max_results=max_results,
        )
    else:
        return _search_craigslist(
            query=query,
            rv_type=rv_type,
            min_price=min_price,
            max_price=max_price,
            min_year=min_year,
            max_year=max_year,
            location=location,
            max_results=max_results,
        )


def _search_demo(
    query: Optional[str] = None,
    rv_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    location: Optional[str] = None,
    max_results: int = 20,
) -> List[RVListing]:
    """Search demo listings with filters."""
    results = []

    for listing in DEMO_LISTINGS:
        # Apply filters
        if query and query.lower() not in listing.title.lower():
            if listing.make and query.lower() not in listing.make.lower():
                if listing.model and query.lower() not in listing.model.lower():
                    continue

        if rv_type and listing.rv_type:
            if rv_type.lower() not in listing.rv_type.lower():
                continue

        if min_price and listing.price and listing.price < min_price:
            continue

        if max_price and listing.price and listing.price > max_price:
            continue

        if min_year and listing.year and listing.year < min_year:
            continue

        if max_year and listing.year and listing.year > max_year:
            continue

        if location and listing.location:
            if location.lower() not in listing.location.lower():
                continue

        results.append(listing)

        if len(results) >= max_results:
            break

    return results


def _search_craigslist(
    query: Optional[str] = None,
    rv_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
    location: Optional[str] = None,
    max_results: int = 20,
) -> List[RVListing]:
    """Search Craigslist RSS feeds (works from home IPs, may be blocked from cloud)."""
    region = _get_region(location)

    # Build search query
    search_terms = []
    if query:
        search_terms.append(query)
    if rv_type:
        search_terms.append(rv_type)
    if min_year:
        search_terms.append(str(min_year))

    search_query = " ".join(search_terms) if search_terms else ""

    # Build RSS feed URL
    base_url = f"https://{region}.craigslist.org/search/rva"
    params = {"format": "rss"}

    if search_query:
        params["query"] = search_query
    if min_price:
        params["min_price"] = min_price
    if max_price:
        params["max_price"] = max_price

    url = f"{base_url}?{urlencode(params)}"

    try:
        with httpx.Client(
            timeout=30,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            }
        ) as client:
            response = client.get(url)
            response.raise_for_status()
            return _parse_rss_feed(response.text, max_results, min_year, max_year)
    except httpx.HTTPError as e:
        raise SearchAPIError(
            f"Craigslist blocked the request (common from cloud servers). "
            f"Try running from your home network with DEMO_MODE=false, or use demo mode. "
            f"Error: {e}"
        )
    except ET.ParseError as e:
        raise SearchAPIError(f"Failed to parse RSS feed: {e}")


def _get_region(location: Optional[str]) -> str:
    """Convert location string to Craigslist region code."""
    if not location:
        return "sfbay"

    location_lower = location.lower().strip()

    if location_lower in CRAIGSLIST_REGIONS:
        return location_lower

    for code, name in CRAIGSLIST_REGIONS.items():
        if location_lower in name.lower() or name.lower() in location_lower:
            return code

    for code in CRAIGSLIST_REGIONS:
        if location_lower in code or code in location_lower:
            return code

    return "sfbay"


def _parse_rss_feed(
    xml_content: str,
    max_results: int,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None,
) -> List[RVListing]:
    """Parse Craigslist RSS feed XML into RVListing objects."""
    listings = []
    root = ET.fromstring(xml_content)
    items = root.findall(".//item")

    for item in items[:max_results * 2]:
        listing = _parse_rss_item(item)
        if listing:
            if min_year and listing.year and listing.year < min_year:
                continue
            if max_year and listing.year and listing.year > max_year:
                continue
            listings.append(listing)
            if len(listings) >= max_results:
                break

    return listings


def _parse_rss_item(item: ET.Element) -> Optional[RVListing]:
    """Parse a single RSS item into an RVListing."""
    title_elem = item.find("title")
    if title_elem is None or not title_elem.text:
        return None

    title = title_elem.text.strip()
    link_elem = item.find("link")
    url = link_elem.text.strip() if link_elem is not None and link_elem.text else None
    desc_elem = item.find("description")
    description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else None

    # Extract price
    price = None
    price_match = re.search(r"\$[\d,]+", title)
    if price_match:
        try:
            price = int(price_match.group().replace("$", "").replace(",", ""))
        except ValueError:
            pass

    # Extract year
    year = None
    year_match = re.search(r"\b(19|20)\d{2}\b", title)
    if year_match:
        potential_year = int(year_match.group())
        if 1980 <= potential_year <= 2026:
            year = potential_year

    # Extract location
    location = None
    loc_match = re.search(r"\(([^)]+)\)\s*$", title)
    if loc_match:
        location = loc_match.group(1)

    # Extract make
    make = None
    makes = [
        "Winnebago", "Thor", "Jayco", "Coachmen", "Forest River",
        "Keystone", "Fleetwood", "Newmar", "Tiffin", "Entegra",
        "Airstream", "Grand Design", "Heartland", "Dutchmen",
        "Storyteller", "Mercedes", "Pleasure-Way", "Roadtrek",
    ]
    for m in makes:
        if m.lower() in title.lower():
            make = m
            break

    # Extract RV type
    rv_type = None
    if re.search(r"class\s*a", title, re.IGNORECASE):
        rv_type = "Class A"
    elif re.search(r"class\s*b", title, re.IGNORECASE):
        rv_type = "Class B"
    elif re.search(r"class\s*c", title, re.IGNORECASE):
        rv_type = "Class C"
    elif re.search(r"travel\s*trailer", title, re.IGNORECASE):
        rv_type = "Travel Trailer"
    elif re.search(r"fifth\s*wheel|5th\s*wheel", title, re.IGNORECASE):
        rv_type = "Fifth Wheel"

    # Clean title
    clean_title = re.sub(r"\s*-?\s*\$[\d,]+", "", title)
    clean_title = re.sub(r"\s*\([^)]+\)\s*$", "", clean_title).strip()

    return RVListing(
        title=clean_title or title,
        price=price,
        year=year,
        make=make,
        location=location,
        url=url,
        description=description,
        rv_type=rv_type,
    )


def get_available_regions() -> dict:
    """Return dictionary of available Craigslist regions."""
    return CRAIGSLIST_REGIONS.copy()
