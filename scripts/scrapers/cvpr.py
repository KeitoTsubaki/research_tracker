"""CVPR Best Paper / Best Student Paper award scraper.

Same caveats as scrapers/icra.py: CVPR's award-announcement page moves
and restructures every year, so update CVPR_AWARDS_URL for the current
year and re-check the parsing if it stops finding anything.
"""
from __future__ import annotations

import sys
from typing import List

from bs4 import BeautifulSoup

from .base import AwardPaper, classify_award, fetch_html

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


def _resolve_url(href: str) -> str:
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return CVPR_BASE_URL + href
    return f"{CVPR_BASE_URL}/{href}"


def scrape() -> List[AwardPaper]:
    html = fetch_html(CVPR_AWARDS_URL)
    soup = BeautifulSoup(html, "html.parser")
    results: List[AwardPaper] = []

    for node in soup.find_all(["h1", "h2", "h3", "h4", "li", "p"]):
        text = node.get_text(" ", strip=True)
        award = classify_award(text, AWARD_KEYWORDS)
        if not award:
            continue

        link = node.find("a") or node.find_next("a")
        title = link.get_text(" ", strip=True) if link else text
        if not title:
            continue

        url = _resolve_url(link["href"]) if link and link.has_attr("href") else CVPR_AWARDS_URL

        results.append(
            AwardPaper(
                id=f"conf:cvpr2026:award:{len(results) + 1}",
                title=title,
                authors=[],
                conference=CONFERENCE_NAME,
                award=award,
                url=url,
                category="cs.AI",
            )
        )

    if not results:
        print(f"  [cvpr] no award entries found at {CVPR_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
