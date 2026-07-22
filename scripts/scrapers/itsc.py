"""IEEE ITSC (Intelligent Transportation Systems Conference) Best Paper
award scraper (bespoke parser).

ITSC's awards page lists winners as <h3>Nth Prize – Award Name</h3>
followed by a <p> reading "<strong>Presenting Author</strong><br>For
paper co-authored with A, B, C<br>Titled: "Title"". Update
ITSC_AWARDS_URL each year and re-check this structure if it changes.
"""
from __future__ import annotations

import re
import sys
from typing import List

from bs4 import BeautifulSoup

from .base import AwardPaper, fetch_html

CONFERENCE_NAME = "IEEE ITSC 2025"
ITSC_AWARDS_URL = "https://ieee-itsc.org/2025/awards/"
SLUG = "itsc2025"

TITLE_RE = re.compile(r"Titled:\s*[“\"](.+?)[”\"]\s*$")
COAUTHOR_RE = re.compile(r"co-authored with (.+?)(?:Titled:|$)", re.IGNORECASE)


def scrape() -> List[AwardPaper]:
    html = fetch_html(ITSC_AWARDS_URL)
    soup = BeautifulSoup(html, "html.parser")
    results: List[AwardPaper] = []

    for h3 in soup.find_all("h3"):
        label = h3.get_text(" ", strip=True)
        if "prize" not in label.lower() or "paper award" not in label.lower():
            continue

        p = h3.find_next_sibling("p")
        if not p:
            continue

        strong = p.find("strong")
        presenting_author = strong.get_text(" ", strip=True) if strong else ""
        full_text = p.get_text(" ", strip=True)

        title_match = TITLE_RE.search(full_text)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        if not title:
            continue

        authors: List[str] = [presenting_author] if presenting_author else []
        coauthor_match = COAUTHOR_RE.search(full_text)
        if coauthor_match:
            authors.extend(a.strip() for a in coauthor_match.group(1).split(",") if a.strip())

        results.append(
            AwardPaper(
                id=f"conf:{SLUG}:award:{len(results) + 1}",
                title=title,
                authors=authors,
                conference=CONFERENCE_NAME,
                award=label,
                url=ITSC_AWARDS_URL,
                category="cs.RO",
            )
        )

    if not results:
        print(f"  [{SLUG}] no award entries found at {ITSC_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
