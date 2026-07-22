"""RSS (Robotics: Science and Systems) Best Paper award scraper
(bespoke parser).

Note: "RSS" here is the conference (roboticsconference.org), unrelated
to the site's own RSS feed at public/rss.xml.

RSS's awards page lists each category as a <ul class="award-list"> of
<li> finalists; the actual winner is the one <li class="winner"> whose
<span class="winner-label"> reads "Winner: <Award Name>". Update
RSS_AWARDS_URL each year and re-check this structure if it changes.
"""
from __future__ import annotations

import re
import sys
from typing import List

from bs4 import BeautifulSoup

from .base import AwardPaper, fetch_html

CONFERENCE_NAME = "RSS 2025"
RSS_AWARDS_URL = "https://roboticsconference.org/2025/program/awards/"
SLUG = "rss2025"


def scrape() -> List[AwardPaper]:
    html = fetch_html(RSS_AWARDS_URL)
    soup = BeautifulSoup(html, "html.parser")
    results: List[AwardPaper] = []

    for li in soup.select("li.winner"):
        link = li.find("a", class_="paper-link") or li.find("a")
        if not link:
            continue
        title = link.get_text(" ", strip=True)
        if not title:
            continue

        em = li.find("em")
        authors = [a.strip() for a in em.get_text(" ", strip=True).split(",") if a.strip()] if em else []

        label = li.find(class_="winner-label")
        award = re.sub(r"^winner:\s*", "", label.get_text(" ", strip=True), flags=re.IGNORECASE) if label else "Best Paper Award"

        url = link.get("href", RSS_AWARDS_URL)

        results.append(
            AwardPaper(
                id=f"conf:{SLUG}:award:{len(results) + 1}",
                title=title,
                authors=authors,
                conference=CONFERENCE_NAME,
                award=award,
                url=url,
                category="cs.RO",
            )
        )

    if not results:
        print(f"  [{SLUG}] no award entries found at {RSS_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
