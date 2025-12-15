"""Data models for RV listings."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RVListing:
    """Represents an RV listing from a marketplace."""

    title: str
    price: Optional[int] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    mileage: Optional[int] = None
    length_ft: Optional[int] = None
    rv_type: Optional[str] = None  # Class A, Class B, Class C, Travel Trailer, etc.
    fuel_type: Optional[str] = None
    slides: Optional[int] = None
    sleeping_capacity: Optional[int] = None
    description: Optional[str] = None
    image_urls: list[str] = field(default_factory=list)
    source: Optional[str] = None  # Dealer, Facebook Marketplace, Craigslist, etc.

    def to_dict(self) -> dict:
        """Convert listing to dictionary."""
        return {
            "title": self.title,
            "price": self.price,
            "year": self.year,
            "make": self.make,
            "model": self.model,
            "location": self.location,
            "url": self.url,
            "mileage": self.mileage,
            "length_ft": self.length_ft,
            "rv_type": self.rv_type,
            "fuel_type": self.fuel_type,
            "slides": self.slides,
            "sleeping_capacity": self.sleeping_capacity,
            "description": self.description,
            "image_urls": self.image_urls,
            "source": self.source,
        }

    def summary(self) -> str:
        """Return a brief summary of the listing."""
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.make:
            parts.append(self.make)
        if self.model:
            parts.append(self.model)

        title = " ".join(parts) if parts else self.title

        price_str = f"${self.price:,}" if self.price else "Price N/A"
        location_str = self.location or "Location N/A"

        return f"{title} - {price_str} - {location_str}"
