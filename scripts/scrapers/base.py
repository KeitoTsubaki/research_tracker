"""Shared types/helpers for conference award-page scrapers.

Each scraper module (icra.py, cvpr.py, ...) exposes a module-level
`scrape() -> list[AwardPaper]` function. The orchestrator
(scripts/fetch_conference_awards.py) calls each scraper in isolation so
that one conference's page changing doesn't take down the others.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import requests

REQUEST_TIMEOUT_SECONDS = 20
USER_AGENT = "research-tracker-bot/1.0 (github.com research paper tracker; contact via repo issues)"


@dataclass
class AwardPaper:
    id: str
    title: str
    authors: List[str]
    conference: str
    award: str
    url: str
    abstract: str = ""
    category: str = "cs.RO"
    published_date: str = ""
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "authors": self.authors,
            "source": "conference_award",
            "category": self.category,
            "conference": self.conference,
            "award": self.award,
            "url": self.url,
            "abstract": self.abstract,
            "published_date": self.published_date,
            "tags": self.tags,
        }


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT_SECONDS)
    resp.raise_for_status()
    return resp.text


def classify_award(text: str, keyword_to_label: dict) -> Optional[str]:
    lowered = text.lower()
    # Sort by length descending so "best student paper" wins over "best paper".
    for needle in sorted(keyword_to_label, key=len, reverse=True):
        if needle in lowered:
            return keyword_to_label[needle]
    return None


def _resolve_url(href: str, base_url: str) -> str:
    if href.startswith("http"):
        return href
    if href.startswith("/"):
        return base_url.rstrip("/") + href
    return f"{base_url.rstrip('/')}/{href}"


def make_award_scraper(
    *,
    slug: str,
    conference: str,
    awards_url: str,
    base_url: str,
    award_keywords: dict,
    category: str = "cs.RO",
):
    """Build a scrape() function using the shared heuristic parser: scan
    headings/list items/paragraphs for award-keyword text, then grab the
    nearest link as the paper title/url.

    This heuristic is intentionally generic because every conference's
    awards page has different markup and no official structured feed
    exists. It works well enough for simple "Award Name: Paper Title"
    style pages; conferences with unusual markup may need a bespoke
    scraper instead (see icra.py for an example of overriding this).
    """
    from bs4 import BeautifulSoup  # local import keeps base.py import-light

    # Real paper titles are long, descriptive phrases. Nav/breadcrumb links
    # like "Awards" or "About AAAI" also contain award keywords somewhere on
    # the page and would otherwise be mistaken for a paper entry, so require
    # the extracted title to be reasonably long and distinct from the award
    # label itself.
    MIN_TITLE_LENGTH = 20

    def scrape() -> List[AwardPaper]:
        html = fetch_html(awards_url)
        soup = BeautifulSoup(html, "html.parser")
        results: List[AwardPaper] = []

        for node in soup.find_all(["h1", "h2", "h3", "h4", "li", "p"]):
            text = node.get_text(" ", strip=True)
            award = classify_award(text, award_keywords)
            if not award:
                continue

            link = node.find("a") or node.find_next("a")
            title = link.get_text(" ", strip=True) if link else text
            if not title or len(title) < MIN_TITLE_LENGTH or title.strip().lower() == award.lower():
                continue

            url = _resolve_url(link["href"], base_url) if link and link.has_attr("href") else awards_url

            results.append(
                AwardPaper(
                    id=f"conf:{slug}:award:{len(results) + 1}",
                    title=title,
                    authors=[],
                    conference=conference,
                    award=award,
                    url=url,
                    category=category,
                )
            )

        if not results:
            import sys

            print(f"  [{slug}] no award entries found at {awards_url} - page structure may have changed", file=sys.stderr)

        return results

    return scrape
