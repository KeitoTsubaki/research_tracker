"""RSS (Robotics: Science and Systems) Best Paper award scraper.

Note: "RSS" here is the conference (roboticsconference.org), unrelated
to the site's own RSS feed at public/rss.xml. RSS_AWARDS_URL points at
the year's conference page for now (a guessed /awards/ subpath 404s as
of this writing); update it once the specific awards page exists.
"""
from __future__ import annotations

from .base import make_award_scraper

CONFERENCE_NAME = "RSS 2026"
RSS_AWARDS_URL = "https://roboticsconference.org/2026/"
RSS_BASE_URL = "https://roboticsconference.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
    "best systems paper award": "Best Systems Paper Award",
}

scrape = make_award_scraper(
    slug="rss2026",
    conference=CONFERENCE_NAME,
    awards_url=RSS_AWARDS_URL,
    base_url=RSS_BASE_URL,
    award_keywords=AWARD_KEYWORDS,
    category="cs.RO",
)
