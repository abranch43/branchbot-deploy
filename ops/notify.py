import argparse
import csv
import json
import os
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path


def load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _parse_recipients(to_value: str | None) -> list[str]:
    if not to_value:
        return []
    return [e.strip() for e in to_value.split(",") if e.strip()]


def send_email(subject: str, body: str, attachments: list[str] | None = None) -> None:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    email_from = os.getenv("FROM_EMAIL") or os.getenv("EMAIL_FROM") or os.getenv("ALERT_FROM")
    email_to = os.getenv("TO_EMAIL") or os.getenv("EMAIL_TO") or os.getenv("ALERT_TO")

    recipients = _parse_recipients(email_to)

    if not all([email_from, host, user, password]) or not recipients:
        print("Missing SMTP configuration; skipping email.")
        return

    msg = EmailMessage()
    msg["From"] = email_from
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    for apath in attachments or []:
        if os.path.exists(apath):
            with open(apath, "rb") as f:
                data = f.read()
            subtype = "markdown" if apath.endswith(".md") else "csv"
            msg.add_attachment(
                data, maintype="text", subtype=subtype, filename=os.path.basename(apath)
            )

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
    except Exception as e:
        print(f"Email send failed: {e}")


def write_csv_from_payload(payload: dict | list) -> str:
    outdir = Path("data/output")
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    csv_path = outdir / f"opps_{ts}.csv"
    fields = ["id", "title", "agency", "source", "link", "place", "published", "response_due"]
    items = payload.get("items") if isinstance(payload, dict) else payload
    if items is None:
        items = []
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for it in items:
            w.writerow(
                {
                    "id": it.get("id") or it.get("solicitation_id"),
                    "title": it.get("title"),
                    "agency": it.get("agency"),
                    "source": it.get("source"),
                    "link": it.get("url") or it.get("link"),
                    "place": it.get("place_of_performance")
                    or it.get("place")
                    or it.get("location"),
                    "published": it.get("published_date")
                    or it.get("published")
                    or it.get("posted_date"),
                    "response_due": it.get("response_deadline")
                    or it.get("response_due")
                    or it.get("due_date"),
                }
            )
    return str(csv_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="BranchBot notifier")
    parser.add_argument("--error", help="Path to error log to email", default=None)
    args = parser.parse_args()

    stdin_data = sys.stdin.read().strip()
    if stdin_data:
        try:
            payload = json.loads(stdin_data)
        except Exception:
            print("Invalid JSON on stdin")
            return
        csv_path = write_csv_from_payload(payload)
        host = os.getenv("SMTP_HOST")
        user = os.getenv("SMTP_USER")
        pw = os.getenv("SMTP_PASS")
        if host and user and pw:
            total = payload.get("total", 0) if isinstance(payload, dict) else len(payload)
            newc = payload.get("new_count", 0) if isinstance(payload, dict) else 0
            subject = (
                f"BranchBot Opps {datetime.utcnow().strftime('%Y%m%d')} (Total {total}, New {newc})"
            )
            body = f"Total: {total}\nNew: {newc}\nCSV: {csv_path}\n"
            send_email(subject, body)
        print(csv_path)
        return

    if args.error:
        subject = f"[BranchBot] Failure detected ({datetime.utcnow().date().isoformat()})"
        body = f"A failure occurred. See logs at: {args.error}"
        send_email(subject, body)
        print("")
        return

    meta = (
        load_json("data/contracts/latest.meta.json")
        or load_json("data/opportunities.meta.json")
        or {}
    )
    opps = load_json("data/opportunities.json") or []

    if opps:
        new_count = meta.get("new_count", 0)
        subject = f"[BranchBot] {new_count} new opportunities found ({datetime.utcnow().date().isoformat()})"
        top_lines = []
        for it in opps[:10]:
            line = f"- {it.get('title','Untitled')} | {it.get('agency','')} | due: {it.get('due_date','N/A')} | {it.get('url','')}"
            top_lines.append(line)
        body = "\n".join(
            [f"Found {len(opps)} total. New this run: {new_count}.", "", "Top items:", *top_lines]
        )
        send_email(subject, body, attachments=["reports/opportunities.md"])
        csv_path = write_csv_from_payload(opps)
        print(csv_path)
        return

    items = load_json("data/contracts/latest.json") or []
    new_count = int((load_json("data/contracts/latest.meta.json") or {}).get("new_count", 0))
    subject = (
        f"[BranchBot] {new_count} new opportunities found ({datetime.utcnow().date().isoformat()})"
    )
    top_items = []
    for it in items[:10]:
        line = f"- {it.get('title','Untitled')} | {it.get('agency','')} | due: {it.get('due_date','N/A')} | {it.get('url','')}"
        top_items.append(line)
    body = "\n".join(
        [
            f"Found {len(items)} total. New this run: {new_count}.",
            "",
            "Top items:",
            *top_items,
        ]
    )
    send_email(subject, body)
    csv_path = write_csv_from_payload(items)
    print(csv_path)


if __name__ == "__main__":
    main()
