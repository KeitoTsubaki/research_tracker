#!/usr/bin/env python3
"""One-off migration: fill in venue_status / venue_note for papers that
were saved before those fields existed.

- conference_award papers: no API call needed, they're award winners by
  definition, so venue_status is just set to "published" directly.
- arxiv papers: re-queried from the arXiv API in batches (via id_list)
  to read each paper's "comment"/"journal-ref" metadata, since that
  wasn't captured by the original fetch and isn't present in
  data/papers.json to backfill from locally.

Safe to re-run: only touches entries where venue_status is missing.

Usage:
    python scripts/backfill_venue_status.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import List

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.arxiv import parse_entries  # noqa: E402
from lib.store import load_existing, save_papers  # noqa: E402

ARXIV_API_URL = "https://export.arxiv.org/api/query"
USER_AGENT = "research-tracker-bot/1.0 (github.com research paper tracker; contact via repo issues)"
REQUEST_INTERVAL_SECONDS = 3.0
BATCH_SIZE = 50


def fetch_batch(arxiv_ids: List[str]) -> str:
    params = {
        "id_list": ",".join(arxiv_ids),
        "max_results": len(arxiv_ids),
    }
    resp = requests.get(ARXIV_API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def main() -> None:
    papers = load_existing()

    for paper in papers:
        if paper.get("source") == "conference_award" and "venue_status" not in paper:
            paper["venue_status"] = "published"
            paper["venue_note"] = None

    needs_backfill = [
        p for p in papers if p.get("source") == "arxiv" and "venue_status" not in p
    ]
    print(f"{len(needs_backfill)} arXiv paper(s) need venue_status backfilled.")

    by_id = {p["id"]: p for p in papers}
    raw_ids = [p["id"][len("arxiv:"):] for p in needs_backfill]

    updated_count = 0
    for i in range(0, len(raw_ids), BATCH_SIZE):
        batch = raw_ids[i : i + BATCH_SIZE]
        print(f"  querying batch {i // BATCH_SIZE + 1} ({len(batch)} ids)...")
        try:
            xml_text = fetch_batch(batch)
        except requests.RequestException as exc:
            print(f"  batch request failed: {exc}", file=sys.stderr)
            continue

        fetched_by_id = {entry["id"]: entry for entry in parse_entries(xml_text)}
        for arxiv_id in batch:
            full_id = f"arxiv:{arxiv_id}"
            target = by_id.get(full_id)
            fetched = fetched_by_id.get(full_id)
            if target is None:
                continue
            if fetched is not None:
                target["venue_status"] = fetched["venue_status"]
                target["venue_note"] = fetched["venue_note"]
                updated_count += 1
            else:
                # Paper no longer resolvable via id_list (e.g. withdrawn);
                # default to preprint rather than leaving the field missing.
                target["venue_status"] = "preprint"
                target["venue_note"] = None

        if i + BATCH_SIZE < len(raw_ids):
            time.sleep(REQUEST_INTERVAL_SECONDS)

    save_papers(papers)
    print(f"Backfilled {updated_count} arXiv paper(s). Total papers: {len(papers)}.")


if __name__ == "__main__":
    main()
