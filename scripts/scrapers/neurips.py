"""NeurIPS Outstanding Paper / Best Paper award scraper.

NeurIPS usually announces awards via a blog-style page under
neurips.cc/Conferences/<year>/... rather than a stable "/Awards" path,
and the exact URL for a given year is only published close to the
conference (as of this writing, /Conferences/2026/Awards 404s). Update
NEURIPS_AWARDS_URL once that year's page exists; until then this
points at the site root so the request succeeds but simply finds no
award-keyword matches.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "NeurIPS 2026"
NEURIPS_AWARDS_URL = "https://neurips.cc/"
NEURIPS_BASE_URL = "https://neurips.cc"

AWARD_KEYWORDS = {
    "outstanding main track paper": "Outstanding Paper Award",
    "outstanding paper award": "Outstanding Paper Award",
    "outstanding paper": "Outstanding Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
}

scrape = make_award_scraper(
    slug="neurips2026",
    conference=CONFERENCE_NAME,
    awards_url=NEURIPS_AWARDS_URL,
    base_url=NEURIPS_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.LG",
)
