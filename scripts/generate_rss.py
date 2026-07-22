#!/usr/bin/env python3
"""Regenerate public/rss.xml from the most recently added papers.

Run this right after fetch_arxiv.py or fetch_conference_awards.py; it
reads data/latest_new.json (written by those scripts) and builds RSS
items for just that batch, so the feed only carries new papers instead
of the whole archive. If that state file is missing (e.g. a manual
run), it falls back to the FALLBACK_COUNT most recently fetched papers.

Usage:
    python scripts/generate_rss.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.store import DATA_PATH, LATEST_NEW_PATH, load_existing  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
RSS_PATH = REPO_ROOT / "public" / "rss.xml"
FALLBACK_COUNT = 20

SITE_TITLE = "研究論文トラッカー"
SITE_DESCRIPTION = "マルチエージェント強化学習・協調ロボット搬送・自動運転関連の新着論文"
SITE_LINK = "https://example.github.io/research_tracker/"


def get_new_paper_ids() -> list:
    if LATEST_NEW_PATH.exists():
        with LATEST_NEW_PATH.open("r", encoding="utf-8") as f:
            state = json.load(f)
        return state.get("ids", [])
    return []


def build_item(paper: dict) -> str:
    title = xml_escape(paper["title"])
    link = xml_escape(paper["url"])
    guid = xml_escape(paper["id"])
    pub_date = xml_escape(paper.get("published_date", ""))
    description = xml_escape(paper.get("abstract", "")[:500])
    return (
        "    <item>\n"
        f"      <title>{title}</title>\n"
        f"      <link>{link}</link>\n"
        f'      <guid isPermaLink="false">{guid}</guid>\n'
        f"      <pubDate>{pub_date}</pubDate>\n"
        f"      <description>{description}</description>\n"
        "    </item>"
    )


def main() -> None:
    papers = load_existing()
    by_id = {p["id"]: p for p in papers}

    new_ids = get_new_paper_ids()
    if new_ids:
        items_papers = [by_id[i] for i in new_ids if i in by_id]
    else:
        items_papers = sorted(papers, key=lambda p: p.get("fetched_at", ""), reverse=True)[:FALLBACK_COUNT]

    items_papers.sort(key=lambda p: p.get("published_date", ""), reverse=True)
    items_xml = "\n".join(build_item(p) for p in items_papers)

    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{xml_escape(SITE_TITLE)}</title>\n"
        f"    <link>{xml_escape(SITE_LINK)}</link>\n"
        f"    <description>{xml_escape(SITE_DESCRIPTION)}</description>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        f"{items_xml}\n"
        "  </channel>\n"
        "</rss>\n"
    )

    RSS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RSS_PATH.write_text(rss, encoding="utf-8")
    print(f"Wrote {len(items_papers)} item(s) to {RSS_PATH}")


if __name__ == "__main__":
    main()
