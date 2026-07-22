"""AAAI Outstanding Paper award scraper (bespoke parser).

AAAI's paper-awards page is plain WordPress content: each award
category is an <h2>, followed by one <p><strong>Title<br></strong>
Author1, Author2, ...</p> per winning paper. Non-paper categories
(Best Poster, Demonstration Awards, Doctoral Consortium, ...) are
skipped by only tracking <h2> headings that mention "paper". Update
AAAI_AWARDS_URL each year (it follows the aaai-<YY>-paper-awards
pattern) and re-check this structure if it changes.
"""
from __future__ import annotations

import re
import sys
from typing import List, Optional

from bs4 import BeautifulSoup

from .base import AwardPaper, fetch_html

CONFERENCE_NAME = "AAAI 2025"
AAAI_AWARDS_URL = "https://aaai.org/about-aaai/aaai-awards/aaai-25-paper-awards/"
SLUG = "aaai2025"


def scrape() -> List[AwardPaper]:
    html = fetch_html(AAAI_AWARDS_URL)
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", class_="entry-content") or soup

    results: List[AwardPaper] = []
    current_award: Optional[str] = None

    for tag in content.find_all(["h2", "p"]):
        if tag.name == "h2":
            text = tag.get_text(" ", strip=True)
            current_award = text if "paper" in text.lower() else None
            continue

        if tag.name == "p" and current_award:
            strong = tag.find("strong")
            if not strong:
                continue
            title = strong.get_text(" ", strip=True)
            if not title:
                continue

            full_text = tag.get_text(" ", strip=True)
            author_text = full_text[len(title):].strip(" :-")
            authors = [a.strip() for a in re.split(r"[;,]", author_text) if a.strip()]

            results.append(
                AwardPaper(
                    id=f"conf:{SLUG}:award:{len(results) + 1}",
                    title=title,
                    authors=authors,
                    conference=CONFERENCE_NAME,
                    award=current_award,
                    url=AAAI_AWARDS_URL,
                    category="cs.AI",
                )
            )

    if not results:
        print(f"  [{SLUG}] no award entries found at {AAAI_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
