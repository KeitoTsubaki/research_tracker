"""ICML Outstanding Paper / Best Paper award scraper.

Same situation as neurips.py: the exact awards-page URL for a given
year is only published close to the conference (icml.cc/Conferences/
2026/Awards 404s as of this writing), so ICML_AWARDS_URL points at the
site root for now. Update it once that year's awards page exists.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "ICML 2026"
ICML_AWARDS_URL = "https://icml.cc/"
ICML_BASE_URL = "https://icml.cc"

AWARD_KEYWORDS = {
    "outstanding paper award": "Outstanding Paper Award",
    "outstanding paper": "Outstanding Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
}

scrape = make_award_scraper(
    slug="icml2026",
    conference=CONFERENCE_NAME,
    awards_url=ICML_AWARDS_URL,
    base_url=ICML_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.LG",
)
