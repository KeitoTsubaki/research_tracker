"""IROS (IEEE/RSJ International Conference on Intelligent Robots and
Systems) Best Paper / Best Student Paper award scraper.

IROS_AWARDS_URL currently points at the conference site root because
the dedicated awards page usually isn't published until shortly before
or after the conference itself. Update it to the specific awards page
once it exists; until then this scraper will simply find no matches
and log a warning (see base.make_award_scraper), which is expected.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "IROS 2026"
IROS_AWARDS_URL = "https://2026.ieee-iros.org/"
IROS_BASE_URL = "https://2026.ieee-iros.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
    "best conference paper": "Best Conference Paper Award",
}

scrape = make_award_scraper(
    slug="iros2026",
    conference=CONFERENCE_NAME,
    awards_url=IROS_AWARDS_URL,
    base_url=IROS_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.RO",
)
