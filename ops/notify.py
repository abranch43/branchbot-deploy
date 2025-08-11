import argparse
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import json


def load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def send_email(subject: str, body: str, attachments: list[str] | None = None) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    email_from = os.getenv("FROM_EMAIL") or os.getenv("EMAIL_FROM")
    email_to = os.getenv("TO_EMAIL") or os.getenv("EMAIL_TO")

    if not all([email_from, email_to, host, user, password]):
        print("Missing SMTP configuration; skipping email.")
        return

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.set_content(body)

    for apath in attachments or []:
        if os.path.exists(apath):
            with open(apath, "rb") as f:
                data = f.read()
            subtype = "markdown" if apath.endswith(".md") else "csv"
            msg.add_attachment(data, maintype="text", subtype=subtype, filename=os.path.basename(apath))

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description="BranchBot notifier")
    parser.add_argument("--error", help="Path to error log to email", default=None)
    args = parser.parse_args()

    if args.error:
        subject = f"[BranchBot] Failure detected ({datetime.utcnow().date().isoformat()})"
        body = f"A failure occurred. See logs at: {args.error}"
        send_email(subject, body)
        return

    # New opportunities path
    meta = load_json("data/contracts/latest.meta.json") or load_json("data/opportunities.meta.json") or {}
    opps = load_json("data/opportunities.json") or []

    if opps:
        new_count = meta.get("new_count", 0)
        subject = f"[BranchBot] {new_count} new opportunities found ({datetime.utcnow().date().isoformat()})"
        top_lines = []
        for it in opps[:10]:
            line = f"- {it.get('title','Untitled')} | {it.get('agency','')} | due: {it.get('due_date','N/A')} | {it.get('url','')}"
            top_lines.append(line)
        body = "\n".join([f"Found {len(opps)} total. New this run: {new_count}.", "", "Top items:", *top_lines])
        send_email(subject, body, attachments=["reports/opportunities.md"])
        return

    # Fallback to legacy
    items = load_json("data/contracts/latest.json") or []
    new_count = int((load_json("data/contracts/latest.meta.json") or {}).get("new_count", 0))
    subject = f"[BranchBot] {new_count} new opportunities found ({datetime.utcnow().date().isoformat()})"
    top_items = []
    for it in items[:10]:
        line = f"- {it.get('title','Untitled')} | {it.get('agency','')} | due: {it.get('due_date','N/A')} | {it.get('url','')}"
        top_items.append(line)
    body = "\n".join([
        f"Found {len(items)} total. New this run: {new_count}.",
        "",
        "Top items:",
        *top_items,
    ])
    send_email(subject, body)


if __name__ == "__main__":
    main()