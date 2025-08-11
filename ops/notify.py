import argparse
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime
import json


def load_meta(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_items(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def send_email(subject: str, body: str, attachment_path: str | None = None) -> None:
    email_from = os.getenv("EMAIL_FROM")
    email_to = os.getenv("EMAIL_TO")
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")

    if not all([email_from, email_to, host, user, password]):
        print("Missing SMTP configuration; skipping email.")
        return

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            data = f.read()
        msg.add_attachment(data, maintype="text", subtype="csv", filename=os.path.basename(attachment_path))

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

    meta = load_meta("data/contracts/latest.meta.json") or {}
    items = load_items("data/contracts/latest.json")
    csv_path = "data/contracts/latest.csv"

    new_count = int(meta.get("new_count", 0))
    date_str = datetime.utcnow().date().isoformat()
    subject = f"[BranchBot] {new_count} new opportunities found ({date_str})"

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
    send_email(subject, body, attachment_path=csv_path)


if __name__ == "__main__":
    main()