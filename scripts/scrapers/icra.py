"""ICRA Best Paper / Best Student Paper award scraper.

ICRA publishes its awards page at a new URL every year and the HTML
structure is not standardized, so this scraper is intentionally
defensive: it scans headings/list items for award-keyword text near a
link, and if it finds nothing it logs a warning and returns an empty
list rather than raising. Update ICRA_AWARDS_URL each year, and adjust
the parsing below if a given year's page doesn't match this pattern.
"""
from __future__ import annotations

import sys
from typing import List

from bs4 import BeautifulSoup

from .base import AwardPaper, classify_award, fetch_html

CONFERENCE_NAME = "ICRA 2026"
ICRA_AWARDS_URL = "https://2026.ieee-icra.org/awards/"
ICRA_BASE_URL = "https://2026.ieee-icra.org"

AWARD_KEYWORDS = {
    "best student paper award": "Best Student Paper Award",
    "best student paper": "Best Student Paper Award",
    "best paper award": "Best Paper Award",
    "best paper": "Best Paper Award",
}


def _resolve_url(href: str) -> str:
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return ICRA_BASE_URL + href
    return f"{ICRA_BASE_URL}/{href}"


def scrape() -> List[AwardPaper]:
    html = fetch_html(ICRA_AWARDS_URL)
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

        url = _resolve_url(link["href"]) if link and link.has_attr("href") else ICRA_AWARDS_URL

        results.append(
            AwardPaper(
                id=f"conf:icra2026:award:{len(results) + 1}",
                title=title,
                authors=[],
                conference=CONFERENCE_NAME,
                award=award,
                url=url,
                category="cs.RO",
            )
        )

    if not results:
        print(f"  [icra] no award entries found at {ICRA_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
