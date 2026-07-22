"""IEEE ITSC (Intelligent Transportation Systems Conference) Best Paper
award scraper.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "IEEE ITSC 2026"
ITSC_AWARDS_URL = "https://ieee-itsc.org/2026/awards/"
ITSC_BASE_URL = "https://ieee-itsc.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
}

scrape = make_award_scraper(
    slug="itsc2026",
    conference=CONFERENCE_NAME,
    awards_url=ITSC_AWARDS_URL,
    base_url=ITSC_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.RO",
)
