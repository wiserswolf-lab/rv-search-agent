#!/usr/bin/env python3
"""Command-line interface for RV Search Agent."""

import argparse
import sys
import webbrowser
from urllib.parse import quote

from .search_api import search_rv_listings


def open_fb_marketplace(query: str = None, min_price: int = None, max_price: int = None):
    """Open Facebook Marketplace search in browser."""
    base_url = "https://www.facebook.com/marketplace/vehicles"

    # Build search query
    search_term = query or "RV motorhome"
    url = f"{base_url}?query={quote(search_term)}"

    # Add price filters if specified
    if min_price:
        url += f"&minPrice={min_price}"
    if max_price:
        url += f"&maxPrice={max_price}"

    print(f"Opening Facebook Marketplace: {search_term}")
    webbrowser.open(url)


def main():
    parser = argparse.ArgumentParser(
        description="Search for RV listings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "Storyteller"
  %(prog)s --query "Winnebago" --type "Class C" --max-price 100000
  %(prog)s --query "Storyteller" --source "Facebook Marketplace"
  %(prog)s --min-year 2024 --max-year 2025
        """,
    )

    parser.add_argument(
        "-q", "--query",
        help="Search query (make, model, keywords)",
    )
    parser.add_argument(
        "-t", "--type",
        dest="rv_type",
        help="RV type (Class A, Class B, Class C, Travel Trailer, Fifth Wheel)",
    )
    parser.add_argument(
        "--min-price",
        type=int,
        help="Minimum price",
    )
    parser.add_argument(
        "--max-price",
        type=int,
        help="Maximum price",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        help="Minimum year",
    )
    parser.add_argument(
        "--max-year",
        type=int,
        help="Maximum year",
    )
    parser.add_argument(
        "-l", "--location",
        help="Location filter",
    )
    parser.add_argument(
        "-s", "--source",
        help="Source filter (Dealer, Facebook Marketplace)",
    )
    parser.add_argument(
        "-n", "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed listing information",
    )
    parser.add_argument(
        "--open-fb",
        action="store_true",
        help="Open Facebook Marketplace search in browser",
    )

    args = parser.parse_args()

    # Open Facebook Marketplace if requested
    if args.open_fb:
        open_fb_marketplace(args.query, args.min_price, args.max_price)
        sys.exit(0)

    # Run search
    listings = search_rv_listings(
        query=args.query,
        rv_type=args.rv_type,
        min_price=args.min_price,
        max_price=args.max_price,
        min_year=args.min_year,
        max_year=args.max_year,
        location=args.location,
        source=args.source,
        max_results=args.max_results,
    )

    if not listings:
        print("No listings found matching your criteria.")
        sys.exit(0)

    print(f"Found {len(listings)} listing(s):\n")

    for i, listing in enumerate(listings, 1):
        # Title line
        price_str = f"${listing.price:,}" if listing.price else "Price N/A"
        print(f"{i}. {listing.title}")
        print(f"   Price: {price_str}")

        if listing.year:
            print(f"   Year: {listing.year}")

        if listing.location:
            print(f"   Location: {listing.location}")

        if listing.source:
            print(f"   Source: {listing.source}")

        if listing.mileage:
            print(f"   Mileage: {listing.mileage:,} miles")

        if args.verbose:
            if listing.rv_type:
                print(f"   Type: {listing.rv_type}")
            if listing.make:
                print(f"   Make: {listing.make}")
            if listing.model:
                print(f"   Model: {listing.model}")
            if listing.description:
                print(f"   Details: {listing.description}")
            if listing.url:
                print(f"   URL: {listing.url}")

        print()


if __name__ == "__main__":
    main()
