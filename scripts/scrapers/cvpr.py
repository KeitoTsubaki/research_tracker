"""CVPR Best Paper / Best Student Paper award scraper (bespoke parser).

CVPR's BestPapersDemos page lists awards as a flat sequence of <p>
tags: an award-label paragraph ("Best Paper:", "Best Student Paper:",
"Best Paper Honorable Mention: ID: 1234", ...), followed by a
"Paper Name: <title>" paragraph, followed by an "Authors: ..."
paragraph. The generic base.make_award_scraper() heuristic can't
handle this multi-paragraph layout, hence the bespoke parser. Update
CVPR_AWARDS_URL each year and re-check this structure if it changes.
"""
from __future__ import annotations

import re
import sys
from typing import List, Optional

from bs4 import BeautifulSoup

from .base import AwardPaper, fetch_html

CONFERENCE_NAME = "CVPR 2025"
CVPR_AWARDS_URL = "https://cvpr.thecvf.com/Conferences/2025/BestPapersDemos"
SLUG = "cvpr2025"

AWARD_LABEL_RE = re.compile(r"^(Best (?:Student )?Paper(?: Honorable Mention)?)\s*:", re.IGNORECASE)


def scrape() -> List[AwardPaper]:
    html = fetch_html(CVPR_AWARDS_URL)
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]

    results: List[AwardPaper] = []
    current_award: Optional[str] = None

    i = 0
    while i < len(paragraphs):
        text = paragraphs[i]

        match = AWARD_LABEL_RE.match(text)
        if match:
            current_award = match.group(1).strip() + " Award" if "Honorable Mention" not in match.group(1) else match.group(1).strip()
            i += 1
            continue

        if current_award and text.lower().startswith("paper name:"):
            title = text.split(":", 1)[1].strip()
            authors: List[str] = []
            if i + 1 < len(paragraphs) and paragraphs[i + 1].lower().startswith("authors"):
                author_text = re.sub(r"^authors:?\s*", "", paragraphs[i + 1], flags=re.IGNORECASE)
                authors = [a.strip() for a in author_text.split(",") if a.strip()]
                i += 1

            if title:
                results.append(
                    AwardPaper(
                        id=f"conf:{SLUG}:award:{len(results) + 1}",
                        title=title,
                        authors=authors,
                        conference=CONFERENCE_NAME,
                        award=current_award,
                        url=CVPR_AWARDS_URL,
                        category="cs.AI",
                    )
                )
            current_award = None

        i += 1

    if not results:
        print(f"  [{SLUG}] no award entries found at {CVPR_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
