"""Keyword groups shared by scripts/fetch_arxiv.py (daily new-submission
fetch) and scripts/fetch_arxiv_historical.py (one-off backfill search).

Keeping this in one place means both scripts tag papers identically, and
the UI's KEYWORD_GROUPS in src/lib/papers.ts must use the same slugs.

Group semantics:
  - marl: reinforcement-learning-specific multi-agent techniques.
  - cooperative-transport: multi-robot cooperative transport/manipulation
    research generally, whether or not it uses MARL/RL at all (classic
    control-theoretic cooperative box-pushing papers count too).
  - autonomous-driving: self-driving / motion planning / perception.
"""
from __future__ import annotations

from typing import Dict, List

KEYWORD_GROUPS: Dict[str, List[str]] = {
    "marl": [
        "multi-agent reinforcement learning",
        "marl",
        "mappo",
        "dec-pomdp",
        "ctde",
        "decentralized control",
        "multi-agent",
        "multi-robot reinforcement learning",
    ],
    "cooperative-transport": [
        "cooperative transport",
        "collaborative transport",
        "cooperative transportation",
        "collaborative transportation",
        "cooperative object transport",
        "collaborative object transport",
        "cooperative payload transport",
        "multi-robot transport",
        "multi-robot transportation",
        "multi-robot object transportation",
        "cooperative manipulation",
        "multi-robot manipulation",
        "distributed manipulation",
        "cooperative carrying",
        "cooperative box pushing",
        "cooperative box-pushing",
        "cooperative pushing",
        "collective transport",
        "object transportation",
        "cooperative object manipulation",
        "multi-robot object manipulation",
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


def match_tags(title: str, abstract: str) -> List[str]:
    text = f"{title} {abstract}".lower()
    return [group for group, keywords in KEYWORD_GROUPS.items() if any(kw in text for kw in keywords)]
