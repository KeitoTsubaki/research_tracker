#!/usr/bin/env python3
"""Fetch new arXiv papers, tag them by research-theme keyword group, and
merge the results into data/papers.json.

Usage:
    python scripts/fetch_arxiv.py

Only papers whose title/abstract match at least one keyword group
(marl / autonomous-driving) are kept, since the point of this tracker is
to follow those specific research themes rather than mirror all of
cs.RO/cs.AI/cs.LG/cs.MA.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import feedparser
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.store import load_existing, merge_papers, save_latest_new, save_papers  # noqa: E402

ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "research-tracker-bot/1.0 (github.com research paper tracker; contact via repo issues)"

# arXiv asks for no more than one request every 3 seconds.
REQUEST_INTERVAL_SECONDS = 3.0
PAGE_SIZE = 100
MAX_PAGES = 3  # up to 300 most recent submissions across the target categories

CATEGORIES = ["cs.RO", "cs.AI", "cs.LG", "cs.MA"]

# Keyword groups -> tag slug. A paper can receive both tags.
KEYWORD_GROUPS: Dict[str, List[str]] = {
    "marl": [
        "multi-agent reinforcement learning",
        "marl",
        "cooperative transport",
        "mappo",
        "dec-pomdp",
        "ctde",
        "decentralized control",
        "multi-robot",
    ],
    "autonomous-driving": [
        "autonomous driving",
        "self-driving",
        "end-to-end driving",
        "motion planning",
        "trajectory prediction",
        "motion forecasting",
        "sensor fusion",
        "bev perception",
        "occupancy prediction",
        "v2x",
        "software-defined vehicle",
        "sdv",
    ],
}


def build_search_query() -> str:
    return "(" + " OR ".join(f"cat:{c}" for c in CATEGORIES) + ")"


def fetch_page(start: int, max_results: int) -> str:
    params = {
        "search_query": build_search_query(),
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    resp = requests.get(ARXIV_API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


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
        }


def match_tags(paper: dict) -> List[str]:
    text = f"{paper['title']} {paper['abstract']}".lower()
    return [group for group, keywords in KEYWORD_GROUPS.items() if any(kw in text for kw in keywords)]


def fetch_all_entries() -> List[dict]:
    all_entries: List[dict] = []
    for page in range(MAX_PAGES):
        start = page * PAGE_SIZE
        print(f"  requesting page {page + 1} (start={start})...")
        try:
            xml_text = fetch_page(start, PAGE_SIZE)
        except requests.RequestException as exc:
            print(f"  request failed: {exc}", file=sys.stderr)
            break

        entries = list(parse_entries(xml_text))
        if not entries:
            break
        all_entries.extend(entries)

        if page < MAX_PAGES - 1:
            time.sleep(REQUEST_INTERVAL_SECONDS)

    return all_entries


def main() -> None:
    print(f"Fetching arXiv papers for categories: {', '.join(CATEGORIES)}")
    all_entries = fetch_all_entries()

    tagged: List[dict] = []
    for paper in all_entries:
        tags = match_tags(paper)
        if not tags:
            continue
        paper["tags"] = tags
        tagged.append(paper)

    print(f"Fetched {len(all_entries)} entries, {len(tagged)} matched a tracked keyword group.")

    existing = load_existing()
    merged, added = merge_papers(existing, tagged)
    save_papers(merged)
    save_latest_new(added, source="arxiv")

    print(f"Added {len(added)} new paper(s). Total papers: {len(merged)}.")


if __name__ == "__main__":
    main()
