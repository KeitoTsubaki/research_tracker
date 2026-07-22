#!/usr/bin/env python3
"""Run every registered conference scraper and merge results into
data/papers.json. Each scraper runs in isolation: if one conference's
page fails to load or parse, that failure is logged and the rest keep
going (see scripts/scrapers/__init__.py for the scraper registry).

Usage:
    python scripts/fetch_conference_awards.py
"""
from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.store import load_existing, merge_papers, save_latest_new, save_papers  # noqa: E402
from scrapers import SCRAPERS  # noqa: E402


def main() -> None:
    all_papers: List[dict] = []

    for name, module in SCRAPERS.items():
        print(f"Scraping {name}...")
        try:
            papers = module.scrape()
        except Exception:
            print(f"  scraper '{name}' failed, skipping it and continuing with the rest:", file=sys.stderr)
            traceback.print_exc()
            continue

        print(f"  found {len(papers)} award paper(s)")
        all_papers.extend(p.to_dict() for p in papers)

    existing = load_existing()
    merged, added = merge_papers(existing, all_papers)
    save_papers(merged)
    save_latest_new(added, source="conference_award")

    print(f"Added {len(added)} new award paper(s). Total papers: {len(merged)}.")


if __name__ == "__main__":
    main()
