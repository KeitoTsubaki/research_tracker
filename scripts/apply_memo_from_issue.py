#!/usr/bin/env python3
"""Parse a "memo-update" GitHub Issue body and write the memo into
data/papers.json for the referenced paper id.

Triggered by .github/workflows/apply-memo.yml on `issues: opened`,
which passes the issue body via the ISSUE_BODY env var. The issue body
comes from .github/ISSUE_TEMPLATE/memo-update.yml, which GitHub
renders as a sequence of "### <field label>\n\n<value>" blocks.

Usage (from the workflow):
    ISSUE_BODY="$ISSUE_BODY" python scripts/apply_memo_from_issue.py
"""
from __future__ import annotations

import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.store import load_existing, save_papers  # noqa: E402

PAPER_ID_LABEL = "論文ID"
MEMO_LABEL = "メモ"
EMPTY_MARKERS = {"", "_no response_"}


def extract_field(body: str, label: str) -> str:
    match = re.search(rf"### {re.escape(label)}\s*\n+(.*?)(?=\n### |\Z)", body, re.DOTALL)
    return match.group(1).strip() if match else ""


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "")

    paper_id = extract_field(body, PAPER_ID_LABEL)
    if not paper_id:
        print("no paper id found in issue body", file=sys.stderr)
        sys.exit(1)

    memo = extract_field(body, MEMO_LABEL)
    if memo.lower() in EMPTY_MARKERS:
        memo = ""

    papers = load_existing()
    target = next((p for p in papers if p["id"] == paper_id), None)
    if target is None:
        print(f"paper id {paper_id!r} not found in data/papers.json", file=sys.stderr)
        sys.exit(1)

    target["memo"] = memo
    target["memo_updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    save_papers(papers)
    print(f"updated memo for {paper_id}")


if __name__ == "__main__":
    main()
