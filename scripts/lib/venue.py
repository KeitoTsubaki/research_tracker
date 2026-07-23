"""Heuristic classification of whether an arXiv paper has been accepted
to / published at a venue, versus still being a plain preprint.

arXiv authors commonly self-report acceptance in the free-text
"comment" field (e.g. "Accepted to CVPR 2025", "To appear in IROS
2025 (oral)") and set "journal-ref" once a paper is formally
published. This is a best-effort heuristic over that author-provided
metadata, not an authoritative acceptance check: authors don't always
keep the comment field up to date, and phrasing varies. Treat
"published" here as "the author says so", not a verified fact.
"""
from __future__ import annotations

import re

PUBLISHED = "published"
PREPRINT = "preprint"

_ACCEPTANCE_PATTERNS = [
    r"\baccepted\b",
    r"\bto appear\b",
    r"\bcamera[- ]ready\b",
    r"\bin proceedings of\b",
    r"\bpublished (in|at|as)\b",
    r"\bproc\.\s",
]


def classify_venue_status(comment: str, journal_ref: str = "") -> str:
    if journal_ref and journal_ref.strip():
        return PUBLISHED

    text = (comment or "").lower()
    for pattern in _ACCEPTANCE_PATTERNS:
        if re.search(pattern, text):
            return PUBLISHED

    return PREPRINT
