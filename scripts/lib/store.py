"""Shared helpers for loading, merging, and saving data/papers.json.

Both scripts/fetch_arxiv.py and scripts/fetch_conference_awards.py use
these so the "same id is never duplicated, existing memo is always
preserved" rule lives in exactly one place.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = REPO_ROOT / "data" / "papers.json"
LATEST_NEW_PATH = REPO_ROOT / "data" / "latest_new.json"


def load_existing(path: Path = DATA_PATH) -> List[dict]:
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return []


def merge_papers(existing: List[dict], new_papers: Iterable[dict]) -> Tuple[List[dict], List[dict]]:
    """Merge new_papers into existing, keyed by id.

    Papers that already exist are left completely untouched (so their
    memo / memo_updated_at survive). Only genuinely new ids are added.
    Returns (merged_list, newly_added_papers).
    """
    by_id = {p["id"]: p for p in existing}
    added: List[dict] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for paper in new_papers:
        pid = paper["id"]
        if pid in by_id:
            continue
        paper = dict(paper)
        paper.setdefault("fetched_at", now)
        paper.setdefault("memo", "")
        paper.setdefault("memo_updated_at", None)
        by_id[pid] = paper
        added.append(paper)

    merged = list(by_id.values())
    merged.sort(key=lambda p: p.get("published_date", ""), reverse=True)
    return merged, added


def save_papers(papers: List[dict], path: Path = DATA_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(papers, f, ensure_ascii=False, indent=2)
        f.write("\n")


def save_latest_new(added: List[dict], source: str, path: Path = LATEST_NEW_PATH) -> None:
    """Record which ids were just added so generate_rss.py can build a
    diff-only feed instead of re-publishing every paper in the repo."""
    state = {
        "source": source,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ids": [p["id"] for p in added],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")
