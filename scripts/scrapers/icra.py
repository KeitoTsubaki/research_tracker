"""ICRA Best Paper / Best Student Paper award scraper.

ICRA publishes its awards page at a new URL every year and the HTML
structure is not standardized. Update ICRA_AWARDS_URL each year, and
adjust AWARD_KEYWORDS / the heuristic in base.make_award_scraper if a
given year's page doesn't match the "award name near a link" pattern.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "ICRA 2026"
ICRA_AWARDS_URL = "https://2026.ieee-icra.org/awards/"
ICRA_BASE_URL = "https://2026.ieee-icra.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
}

scrape = make_award_scraper(
    slug="icra2026",
    conference=CONFERENCE_NAME,
    awards_url=ICRA_AWARDS_URL,
    base_url=ICRA_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.RO",
)
