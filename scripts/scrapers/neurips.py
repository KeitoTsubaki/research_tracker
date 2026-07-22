"""NeurIPS Outstanding/Best Paper award scraper (bespoke parser).

NeurIPS's awards_detail page renders a table: each row's first <td> is
the award label (e.g. "Best Paper", "Outstanding Paper", "Test of Time
Award"), and the second <td> holds one or more
`<div class="displaycards">` blocks, each with a title <a> and an
author line containing "⋅"-separated names. Update
NEURIPS_AWARDS_URL each year and re-check this structure if it moves.
"""
from __future__ import annotations

import sys
from typing import List

from bs4 import BeautifulSoup

from .base import AwardPaper, fetch_html

CONFERENCE_NAME = "NeurIPS 2025"
NEURIPS_AWARDS_URL = "https://neurips.cc/virtual/2025/awards_detail"
NEURIPS_BASE_URL = "https://neurips.cc"
SLUG = "neurips2025"

# "Test of Time Award" recognizes a paper from ~10 years ago, not a
# 2025 paper, so it's deliberately excluded here.
SKIP_LABELS = {"test of time award", "test of time"}


AUTHOR_SEPARATORS = ("·", "⋅")  # middle dot, dot operator - platform uses one or the other


def _extract_authors(card) -> List[str]:
    author_div = card.find(class_="author-str")
    if author_div is not None:
        text = author_div.get_text(" ", strip=True)
        for sep in AUTHOR_SEPARATORS:
            if sep in text:
                return [a.strip() for a in text.split(sep) if a.strip()]
        return [text] if text else []

    for div in card.find_all("div"):
        text = div.get_text(" ", strip=True)
        for sep in AUTHOR_SEPARATORS:
            if sep in text:
                return [a.strip() for a in text.split(sep) if a.strip()]
    return []


def scrape() -> List[AwardPaper]:
    html = fetch_html(NEURIPS_AWARDS_URL)
    soup = BeautifulSoup(html, "html.parser")
    results: List[AwardPaper] = []
    seen = set()

    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        label = cells[0].get_text(" ", strip=True)
        if not label or "paper" not in label.lower() or label.lower() in SKIP_LABELS:
            continue

        for card in cells[1].select("div.displaycards"):
            link = card.find("a", href=True)
            if not link:
                continue
            title = link.get_text(" ", strip=True)
            if not title or (label, title) in seen:
                continue
            seen.add((label, title))

            authors = _extract_authors(card)
            href = link["href"]
            url = NEURIPS_BASE_URL + href if href.startswith("/") else href

            results.append(
                AwardPaper(
                    id=f"conf:{SLUG}:award:{len(results) + 1}",
                    title=title,
                    authors=authors,
                    conference=CONFERENCE_NAME,
                    award=label,
                    url=url,
                    category="cs.LG",
                )
            )

    if not results:
        print(f"  [{SLUG}] no award entries found at {NEURIPS_AWARDS_URL} - page structure may have changed", file=sys.stderr)

    return results
