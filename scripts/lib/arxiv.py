"""Shared arXiv Atom-feed parsing, used by fetch_arxiv.py and
fetch_arxiv_historical.py so entry-parsing logic (including venue
status detection) lives in exactly one place.
"""
from __future__ import annotations

import re
from typing import Iterator

import feedparser

from .venue import classify_venue_status


def _primary_category(entry) -> str:
    cat = entry.get("arxiv_primary_category")
    if isinstance(cat, dict) and cat.get("term"):
        return cat["term"]
    tags = entry.get("tags") or []
    if tags:
        return tags[0].get("term", "")
    return ""


def parse_entries(xml_text: str) -> Iterator[dict]:
    feed = feedparser.parse(xml_text)
    for entry in feed.entries:
        arxiv_id = entry.id.rsplit("/", 1)[-1]
        arxiv_id = re.sub(r"v\d+$", "", arxiv_id)
        title = " ".join(entry.title.split())
        abstract = " ".join(entry.summary.split())
        published = entry.published[:10] if getattr(entry, "published", "") else ""
        authors = [a.get("name", "") for a in getattr(entry, "authors", [])]
        comment = " ".join(entry.get("arxiv_comment", "").split())
        journal_ref = " ".join(entry.get("arxiv_journal_ref", "").split())

        yield {
            "id": f"arxiv:{arxiv_id}",
            "title": title,
            "authors": authors,
            "source": "arxiv",
            "category": _primary_category(entry),
            "conference": None,
            "award": None,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "abstract": abstract,
            "published_date": published,
            "tags": [],
            "venue_status": classify_venue_status(comment, journal_ref),
            "venue_note": comment or None,
        }
