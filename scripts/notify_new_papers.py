#!/usr/bin/env python3
"""Notify about newly added papers via Slack and/or email.

Reads data/latest_new.json (written by fetch_arxiv.py /
fetch_conference_awards.py) to find which papers were just added, then
sends a summary through whichever channel is configured:

  - Slack: set the SLACK_WEBHOOK_URL secret (an Incoming Webhook URL
    from https://api.slack.com/messaging/webhooks - free, no paid tier
    required).
  - Email: set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, and
    NOTIFY_EMAIL_TO secrets (e.g. Gmail SMTP with an App Password).

Both are optional and independent; configure one, both, or neither. If
neither is configured, this script logs that and exits 0 (a missing
notification channel should never fail the data-fetch workflow).

Usage (from a workflow, after fetch_arxiv.py / fetch_conference_awards.py):
    python scripts/notify_new_papers.py
"""
from __future__ import annotations

import json
import os
import smtplib
import sys
import urllib.error
import urllib.request
from email.mime.text import MIMEText
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.store import LATEST_NEW_PATH, load_existing  # noqa: E402

SITE_URL = os.environ.get("NOTIFY_SITE_URL", "").rstrip("/")


def load_new_papers() -> List[dict]:
    if not LATEST_NEW_PATH.exists():
        return []
    with LATEST_NEW_PATH.open("r", encoding="utf-8") as f:
        state = json.load(f)
    ids = set(state.get("ids", []))
    if not ids:
        return []

    papers = load_existing()
    by_id = {p["id"]: p for p in papers}
    return [by_id[i] for i in ids if i in by_id]


def format_paper_line(paper: dict) -> str:
    tags = ", ".join(paper.get("tags", [])) or "-"
    if paper.get("award"):
        prefix = f"🏆 [{paper['conference']}] {paper['award']}"
    else:
        prefix = f"[{paper.get('category', '')}]"
    return f"{prefix} {paper['title']}\n  タグ: {tags}\n  {paper['url']}"


def build_message(new_papers: List[dict]) -> str:
    awards = [p for p in new_papers if p.get("source") == "conference_award"]
    others = [p for p in new_papers if p.get("source") != "conference_award"]

    lines = [f"研究論文トラッカー: 新着 {len(new_papers)} 件"]
    if SITE_URL:
        lines.append(SITE_URL)
    lines.append("")

    if awards:
        lines.append(f"■ 受賞論文 ({len(awards)}件)")
        lines.extend(format_paper_line(p) for p in awards)
        lines.append("")

    if others:
        lines.append(f"■ 新着論文 ({len(others)}件)")
        lines.extend(format_paper_line(p) for p in others)

    return "\n".join(lines).strip()


def send_slack(message: str) -> bool:
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return False

    payload = json.dumps({"text": message}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
        print("Slack notification sent.")
        return True
    except urllib.error.URLError as exc:
        print(f"Slack notification failed: {exc}", file=sys.stderr)
        return False


def send_email(message: str, paper_count: int) -> bool:
    host = os.environ.get("SMTP_HOST", "").strip()
    port = os.environ.get("SMTP_PORT", "").strip()
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    to_addr = os.environ.get("NOTIFY_EMAIL_TO", "").strip()

    if not (host and port and user and password and to_addr):
        return False

    msg = MIMEText(message, _charset="utf-8")
    msg["Subject"] = f"研究論文トラッカー: 新着{paper_count}件"
    msg["From"] = user
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(host, int(port), timeout=15) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(user, [to_addr], msg.as_string())
        print("Email notification sent.")
        return True
    except (smtplib.SMTPException, OSError) as exc:
        print(f"Email notification failed: {exc}", file=sys.stderr)
        return False


def main() -> None:
    new_papers = load_new_papers()
    if not new_papers:
        print("No new papers to notify about.")
        return

    message = build_message(new_papers)

    sent_slack = send_slack(message)
    sent_email = send_email(message, len(new_papers))

    if not sent_slack and not sent_email:
        print(
            "No notification channel configured (set SLACK_WEBHOOK_URL and/or "
            "SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/NOTIFY_EMAIL_TO secrets "
            "to enable). Skipping."
        )


if __name__ == "__main__":
    main()
