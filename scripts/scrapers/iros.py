"""IROS (IEEE/RSJ International Conference on Intelligent Robots and
Systems) Best Paper / Best Student Paper award scraper.

As of this writing, IROS 2025's site (www.iros25.org) only publishes a
"Call for Award Nominations" page, not a results/winners page -- IROS
doesn't appear to post a stable, predictable results URL the way ICRA
or RSS do. IROS_AWARDS_URL points at that nominations page for now, so
this scraper simply finds no award-keyword matches and logs a warning
(see base.make_award_scraper) rather than raising. If/when a results
page turns up, update IROS_AWARDS_URL to it.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "IROS 2025"
IROS_AWARDS_URL = "https://www.iros25.org/Award"
IROS_BASE_URL = "https://www.iros25.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
    "best conference paper": "Best Conference Paper Award",
}

scrape = make_award_scraper(
    slug="iros2025",
    conference=CONFERENCE_NAME,
    awards_url=IROS_AWARDS_URL,
    base_url=IROS_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.RO",
)
