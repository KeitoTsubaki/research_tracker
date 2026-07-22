"""CVPR Best Paper / Best Student Paper award scraper.

Same caveats as icra.py: CVPR's award-announcement page moves and
restructures every year, so update CVPR_AWARDS_URL for the current
year and re-check the parsing if it stops finding anything.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "CVPR 2026"
CVPR_AWARDS_URL = "https://cvpr.thecvf.com/Conferences/2026/AwardsBanquet"
CVPR_BASE_URL = "https://cvpr.thecvf.com"

AWARD_KEYWORDS = {
    "best student paper honorable mention": "Best Student Paper Honorable Mention",
    "best paper honorable mention": "Best Paper Honorable Mention",
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
}

scrape = make_award_scraper(
    slug="cvpr2026",
    conference=CONFERENCE_NAME,
    awards_url=CVPR_AWARDS_URL,
    base_url=CVPR_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.AI",
)
