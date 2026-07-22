"""ICRA Best Paper award scraper (bespoke parser).

ICRA 2025's awards page uses a distinctive structure that the generic
base.make_award_scraper() heuristic can't handle: each award category
is an <h3> heading, followed by an <h4>Award Winner:</h4> marker and
then a <p><strong>Title</strong><em>Authors: ...</em></p> block (with
an "Other Finalists" block afterwards that must be skipped, since
those aren't the winner). Update ICRA_AWARDS_URL to the current year's
page and re-check this structure each year.
"""
from __future__ import annotations

import re
import sys
from typing import List, Optional

from bs4 import BeautifulSoup

from .base import AwardPaper, fetch_html

CONFERENCE_NAME = "ICRA 2025"
ICRA_AWARDS_URL = "https://2025.ieee-icra.org/program/awards-and-finalists/"
SLUG = "icra2025"


def _clean_title(text: str) -> str:
    return text.strip().lstrip("*").strip()


def scrape() -> List[AwardPaper]:
    html = fetch_html(ICRA_AWARDS_URL)
    soup = BeautifulSoup(html, "html.parser")
    results: List[AwardPaper] = []

    current_award: Optional[str] = None
    awaiting_winner = False

    for node in soup.find_all(["h3", "h4", "p"]):
        if node.name == "h3":
            text = node.get_text(" ", strip=True)
            current_award = text if "award" in text.lower() else None
            awaiting_winner = False
            continue

        if node.name == "h4":
            if current_award and "winner" in node.get_text(" ", strip=True).lower():
                awaiting_winner = True
            continue

        if node.name == "p" and awaiting_winner and current_award:
            strong = node.find("strong")
            if not strong:
                continue
            title = _clean_title(strong.get_text(" ", strip=True))
            awaiting_winner = False  # only the first <p> after "Award Winner:" is the winner
            if not title or "finalist" in title.lower():
                continue

            em = node.find("em")
            authors: List[str] = []
            if em:
                author_text = re.sub(r"^authors?:\s*", "", em.get_text(" ", strip=True), flags=re.IGNORECASE)
                authors = [a.strip() for a in author_text.split(",") if a.strip()]

            results.append(
                AwardPaper(
                    id=f"conf:{SLUG}:award:{len(results) + 1}",
                    title=title,
                    authors=authors,
                    conference=CONFERENCE_NAME,
                    award=current_award,
                    url=ICRA_AWARDS_URL,
                    category="cs.RO",
                )
            )

    if not results:
        print(f"  [{SLUG}] no award entries found at {ICRA_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
