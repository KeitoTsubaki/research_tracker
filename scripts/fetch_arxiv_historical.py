#!/usr/bin/env python3
"""One-off backfill: search arXiv for older cooperative-transport /
multi-robot-transport papers that scripts/fetch_arxiv.py's "most recent
300 submissions" window would never reach.

Unlike fetch_arxiv.py (which pages through the newest submissions and
tags whatever matches), this script queries arXiv's full-text index
directly for the cooperative-transport keyword group and a wide date
range, so it can find a 2005 paper just as easily as a 2025 one. It
does NOT require a MARL match — classic control-theoretic cooperative
transport/box-pushing papers count too, since deep-RL-based MARL methods
didn't really exist before the 2010s but the cooperative-transport
research theme itself goes back further.

Usage:
    python scripts/fetch_arxiv_historical.py
    python scripts/fetch_arxiv_historical.py --start-year 1995

Run this manually whenever you want to (re)scan the historical
archive, e.g. after adding new keywords to KEYWORD_GROUPS in
scripts/lib/keywords.py. It's not on a cron schedule since the corpus
of already-published old papers doesn't change.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.arxiv import parse_entries  # noqa: E402
from lib.keywords import KEYWORD_GROUPS, match_tags  # noqa: E402
from lib.store import load_existing, merge_papers, save_latest_new, save_papers  # noqa: E402

ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "research-tracker-bot/1.0 (github.com research paper tracker; contact via repo issues)"

REQUEST_INTERVAL_SECONDS = 3.0
PAGE_SIZE = 100
MAX_PAGES = 20  # up to 2000 results; the actual corpus for this theme is in the low hundreds

DEFAULT_START_YEAR = 2000

# Broader than the daily fetch's CATEGORIES: cooperative transport is a
# classic control-theory topic too, so include systems/control categories
# in addition to the site's usual cs.RO/cs.AI/cs.LG/cs.MA.
CATEGORIES = ["cs.RO", "cs.AI", "cs.LG", "cs.MA", "cs.SY", "eess.SY"]

TARGET_GROUP = "cooperative-transport"


def build_search_query(start_year: int) -> str:
    cat_terms = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    keywords = KEYWORD_GROUPS[TARGET_GROUP]
    # Match keyword phrases in either the abstract or the title.
    kw_terms = " OR ".join(f'abs:"{kw}" OR ti:"{kw}"' for kw in keywords)
    start = f"{start_year}01010000"
    end = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    return f"(({cat_terms})) AND (({kw_terms})) AND submittedDate:[{start} TO {end}]"


def fetch_page(query: str, start: int, max_results: int) -> str:
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "ascending",
    }
    resp = requests.get(ARXIV_API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def fetch_all_entries(query: str) -> List[dict]:
    all_entries: List[dict] = []
    for page in range(MAX_PAGES):
        start = page * PAGE_SIZE
        print(f"  requesting page {page + 1} (start={start})...")
        try:
            xml_text = fetch_page(query, start, PAGE_SIZE)
        except requests.RequestException as exc:
            print(f"  request failed: {exc}", file=sys.stderr)
            break

        entries = list(parse_entries(xml_text))
        if not entries:
            break
        all_entries.extend(entries)

        if len(entries) < PAGE_SIZE:
            break  # last page

        if page < MAX_PAGES - 1:
            time.sleep(REQUEST_INTERVAL_SECONDS)

    return all_entries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--start-year",
        type=int,
        default=DEFAULT_START_YEAR,
        help=f"earliest submission year to search from (default: {DEFAULT_START_YEAR})",
    )
    args = parser.parse_args()

    query = build_search_query(args.start_year)
    print(f"Searching arXiv for '{TARGET_GROUP}' papers since {args.start_year} across: {', '.join(CATEGORIES)}")
    all_entries = fetch_all_entries(query)

    # arXiv's server-side abs:/ti: phrase search is a loose full-text match
    # (it can return papers whose abstract never actually contains the
    # phrase), so re-verify every candidate against our own strict
    # substring matcher before keeping it.
    tagged: List[dict] = []
    for paper in all_entries:
        tags = match_tags(paper["title"], paper["abstract"])
        if TARGET_GROUP not in tags:
            continue
        paper["tags"] = tags
        tagged.append(paper)

    print(f"Fetched {len(all_entries)} candidates, {len(tagged)} confirmed after strict keyword re-check.")

    existing = load_existing()
    merged, added = merge_papers(existing, tagged)
    save_papers(merged)
    save_latest_new(added, source="arxiv-historical")

    print(f"Added {len(added)} new paper(s). Total papers: {len(merged)}.")


if __name__ == "__main__":
    main()
