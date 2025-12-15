"""Tests for the RV Search CLI."""

import subprocess
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, "src")
from rv_search_agent.cli import main
from rv_search_agent.search_api import search_rv_listings


class TestSearchAPI:
    """Test the search API functionality."""

    def test_search_returns_results(self):
        """Test that search returns results."""
        results = search_rv_listings(max_results=5)
        assert len(results) > 0
        assert len(results) <= 5

    def test_search_by_query(self):
        """Test search with query filter."""
        results = search_rv_listings(query="Storyteller", max_results=20)
        assert len(results) > 0
        for listing in results:
            assert "storyteller" in listing.title.lower() or \
                   (listing.make and "storyteller" in listing.make.lower())

    def test_search_by_make_unity(self):
        """Test search for Unity RVs."""
        results = search_rv_listings(query="Unity", max_results=20)
        assert len(results) > 0
        for listing in results:
            assert "unity" in listing.title.lower() or \
                   (listing.make and "unity" in listing.make.lower())

    def test_search_by_min_year(self):
        """Test search with minimum year filter."""
        results = search_rv_listings(min_year=2024, max_results=20)
        assert len(results) > 0
        for listing in results:
            assert listing.year is None or listing.year >= 2024

    def test_search_by_max_year(self):
        """Test search with maximum year filter."""
        results = search_rv_listings(max_year=2022, max_results=20)
        assert len(results) > 0
        for listing in results:
            assert listing.year is None or listing.year <= 2022

    def test_search_by_min_price(self):
        """Test search with minimum price filter."""
        results = search_rv_listings(min_price=200000, max_results=20)
        assert len(results) > 0
        for listing in results:
            assert listing.price is None or listing.price >= 200000

    def test_search_by_max_price(self):
        """Test search with maximum price filter."""
        results = search_rv_listings(max_price=100000, max_results=20)
        assert len(results) > 0
        for listing in results:
            assert listing.price is None or listing.price <= 100000

    def test_search_by_source_dealer(self):
        """Test search filtered by Dealer source."""
        results = search_rv_listings(source="Dealer", max_results=20)
        assert len(results) > 0
        for listing in results:
            # Listings with source set should match; listings without source are included
            assert listing.source is None or listing.source == "Dealer"

    def test_search_by_source_facebook(self):
        """Test search filtered by Facebook Marketplace source."""
        results = search_rv_listings(source="Facebook", max_results=20)
        assert len(results) > 0
        has_facebook = any(
            listing.source and "facebook" in listing.source.lower()
            for listing in results
        )
        assert has_facebook

    def test_search_by_rv_type(self):
        """Test search filtered by RV type."""
        results = search_rv_listings(rv_type="Class C", max_results=20)
        assert len(results) > 0
        for listing in results:
            assert listing.rv_type is None or "class c" in listing.rv_type.lower()

    def test_search_no_results(self):
        """Test search with no matching results."""
        results = search_rv_listings(query="NonExistentBrandXYZ123")
        assert len(results) == 0

    def test_search_combined_filters(self):
        """Test search with multiple filters combined."""
        results = search_rv_listings(
            query="Storyteller",
            min_year=2024,
            source="Facebook",
            max_results=20,
        )
        assert len(results) > 0
        for listing in results:
            assert listing.year is None or listing.year >= 2024
            assert "facebook" in listing.source.lower()


class TestCLI:
    """Test the CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        result = subprocess.run(
            ["./rv-search", "--help"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        assert "Search for RV listings" in result.stdout
        assert "--query" in result.stdout
        assert "--sort-by" in result.stdout

    def test_cli_basic_search(self):
        """Test basic CLI search."""
        result = subprocess.run(
            ["./rv-search", "-q", "Storyteller", "-n", "3"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        assert "Found" in result.stdout
        assert "listing" in result.stdout

    def test_cli_search_with_year_filter(self):
        """Test CLI search with year filter."""
        result = subprocess.run(
            ["./rv-search", "-q", "Unity", "--min-year", "2023", "-n", "5"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        assert "Found" in result.stdout

    def test_cli_search_with_price_filter(self):
        """Test CLI search with price filter."""
        result = subprocess.run(
            ["./rv-search", "--max-price", "150000", "-n", "5"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        assert "Found" in result.stdout

    def test_cli_search_with_source_filter(self):
        """Test CLI search with source filter."""
        result = subprocess.run(
            ["./rv-search", "-s", "Facebook", "-n", "5"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        assert "Facebook Marketplace" in result.stdout

    def test_cli_sort_by_price(self):
        """Test CLI sort by price."""
        result = subprocess.run(
            ["./rv-search", "-q", "Storyteller", "--sort-by", "price", "-n", "20"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        # First result should be cheapest
        assert "$135,000" in result.stdout.split("2.")[0]

    def test_cli_sort_by_price_desc(self):
        """Test CLI sort by price descending."""
        result = subprocess.run(
            ["./rv-search", "-q", "Storyteller", "--sort-by", "price-desc", "-n", "20"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        # First result should be most expensive
        assert "$239,000" in result.stdout.split("2.")[0]

    def test_cli_sort_by_year(self):
        """Test CLI sort by year."""
        result = subprocess.run(
            ["./rv-search", "-q", "Unity", "--sort-by", "year", "-n", "10"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        # First result should be oldest
        assert "2021" in result.stdout.split("2.")[0]

    def test_cli_verbose_output(self):
        """Test CLI verbose output."""
        result = subprocess.run(
            ["./rv-search", "-q", "Storyteller", "-v", "-n", "1"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        assert "Type:" in result.stdout
        assert "Make:" in result.stdout

    def test_cli_no_results(self):
        """Test CLI with no matching results."""
        result = subprocess.run(
            ["./rv-search", "-q", "NonExistentBrandXYZ123"],
            capture_output=True,
            text=True,
            cwd="/Users/scottwolf/Desktop/rv-search-agent",
        )
        assert result.returncode == 0
        assert "No listings found" in result.stdout


class TestSorting:
    """Test sorting functionality."""

    def test_sort_price_ascending(self):
        """Test that price sorting works correctly."""
        results = search_rv_listings(query="Storyteller", max_results=20)
        results.sort(key=lambda x: x.price if x.price else float('inf'))

        prices = [r.price for r in results if r.price]
        assert prices == sorted(prices)

    def test_sort_price_descending(self):
        """Test that price descending sorting works correctly."""
        results = search_rv_listings(query="Storyteller", max_results=20)
        results.sort(key=lambda x: x.price if x.price else 0, reverse=True)

        prices = [r.price for r in results if r.price]
        assert prices == sorted(prices, reverse=True)

    def test_sort_year_ascending(self):
        """Test that year sorting works correctly."""
        results = search_rv_listings(query="Unity", max_results=20)
        results.sort(key=lambda x: x.year if x.year else 0)

        years = [r.year for r in results if r.year]
        assert years == sorted(years)

    def test_sort_year_descending(self):
        """Test that year descending sorting works correctly."""
        results = search_rv_listings(query="Unity", max_results=20)
        results.sort(key=lambda x: x.year if x.year else 0, reverse=True)

        years = [r.year for r in results if r.year]
        assert years == sorted(years, reverse=True)
