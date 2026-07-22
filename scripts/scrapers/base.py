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
