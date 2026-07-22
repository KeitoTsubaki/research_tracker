"""IEEE IV (Intelligent Vehicles Symposium) Best Paper award scraper.

As of this writing, no dedicated awards/results page could be found on
ieee-iv.org/2025/ (the site has call-for-* pages but nothing listing
winners). IEEE_IV_AWARDS_URL points at the year's conference landing
page for now; update it once a results page is published or found.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "IEEE IV 2025"
IEEE_IV_AWARDS_URL = "https://ieee-iv.org/2025/"
IEEE_IV_BASE_URL = "https://ieee-iv.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
}

scrape = make_award_scraper(
    slug="ieeeiv2025",
    conference=CONFERENCE_NAME,
    awards_url=IEEE_IV_AWARDS_URL,
    base_url=IEEE_IV_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.RO",
)
