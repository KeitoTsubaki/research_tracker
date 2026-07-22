"""AAAI Best Paper / Best Student Paper award scraper.

AAAI_AWARDS_URL points at the year's conference landing page
(aaai.org/conference/aaai/aaai-26/awards/ 404s as of this writing);
update it once the specific awards subpage is published.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "AAAI 2026"
AAAI_AWARDS_URL = "https://aaai.org/conference/aaai/aaai-26/"
AAAI_BASE_URL = "https://aaai.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
    "outstanding paper award": "Outstanding Paper Award",
}

scrape = make_award_scraper(
    slug="aaai2026",
    conference=CONFERENCE_NAME,
    awards_url=AAAI_AWARDS_URL,
    base_url=AAAI_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.AI",
)
