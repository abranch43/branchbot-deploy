import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple

from .utils import (
    load_settings,
    ensure_dirs,
    get_logger,
    write_json_atomic,
    write_csv_atomic,
    read_json_file,
    dedupe_by_solicitation_id,
)
from .scrapers.sam_gov import SamGovScraper
from .scrapers.missouribuys import MissouriBuysScraper
from .sinks.csv_sink import CsvSink
from .sinks.notion_sink import NotionSink
from .sinks.google_sheets_sink import GoogleSheetsSink


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="contracts_bot", description="BranchBot Contracts Bot")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run all configured sources")
    run.add_argument("--since", type=int, default=7, help="Only include items posted in the last N days")

    return parser.parse_args(argv)


def run_all(since_days: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    settings = load_settings()
    output_dir = settings.get("output_dir", "data/contracts")
    logs_dir = settings.get("logs_dir", "logs")
    ensure_dirs([output_dir, logs_dir])
    logger = get_logger(os.path.join(logs_dir, "contracts_bot.log"))

    start_time = datetime.now(timezone.utc)
    logger.info("Starting contracts bot run")

    cutoff = start_time - timedelta(days=since_days)

    all_items: List[Dict[str, Any]] = []

    scrapers = [
        SamGovScraper(),
        MissouriBuysScraper(),
    ]

    for scraper in scrapers:
        try:
            items = scraper.fetch(cutoff=cutoff)
            logger.info("Scraper completed: %s count=%s", scraper.source_name, len(items))
            all_items.extend(items)
        except Exception as ex:  # noqa: BLE001
            logger.exception("Scraper failed: %s", getattr(scraper, "source_name", "unknown"))

    # Dedupe by solicitation_id
    deduped_items, previously_seen = dedupe_by_solicitation_id(all_items, output_dir)

    # Sort
    def parsed_date(date_str: str | None) -> datetime:
        if not date_str:
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:  # noqa: BLE001
            return datetime.min.replace(tzinfo=timezone.utc)

    deduped_items.sort(key=lambda x: (
        parsed_date(x.get("posted_date")),
        (datetime.max.replace(tzinfo=timezone.utc) if not x.get("due_date") else parsed_date(x.get("due_date"))),
    ), reverse=True)

    date_str = start_time.strftime("%Y-%m-%d")
    daily_json_path = os.path.join(output_dir, f"{date_str}.json")
    latest_json_path = os.path.join(output_dir, "latest.json")
    latest_csv_path = os.path.join(output_dir, "latest.csv")
    meta_path = os.path.join(output_dir, "latest.meta.json")

    write_json_atomic(daily_json_path, deduped_items)
    write_json_atomic(latest_json_path, deduped_items)

    CsvSink().write(latest_csv_path, deduped_items)

    new_ids = sorted(list({i["solicitation_id"] for i in deduped_items} - previously_seen))
    meta = {
        "created_at": start_time.isoformat(),
        "total": len(deduped_items),
        "new_count": len(new_ids),
        "new_ids": new_ids,
        "since_days": since_days,
    }
    write_json_atomic(meta_path, meta)

    sinks_cfg = settings.get("sinks", {})
    if sinks_cfg.get("notion"):
        try:
            NotionSink().write(deduped_items)
        except Exception:
            logger.exception("Notion sink failed")
    if sinks_cfg.get("google_sheets"):
        try:
            GoogleSheetsSink().write(latest_csv_path)
        except Exception:
            logger.exception("Google Sheets sink failed")

    logger.info("Contracts bot run complete: total=%s new=%s", len(deduped_items), len(new_ids))
    return deduped_items, meta


def run_main() -> None:
    args = parse_args(sys.argv[1:])
    if args.command == "run":
        items, meta = run_all(since_days=args.since)
        print(json.dumps({"total": len(items), **meta}, indent=2))
        return
    raise SystemExit(1)