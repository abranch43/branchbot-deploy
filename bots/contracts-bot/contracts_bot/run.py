import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Tuple, Set
from pathlib import Path
import yaml

from .utils import (
    load_settings,
    ensure_dirs,
    get_logger,
    write_json_atomic,
    write_csv_atomic,
    read_json_file,
)
from .adapters.base import Opportunity
from .adapters.sam_api import SamApiAdapter
from .adapters.mobuys_rss import MoBuysAdapter


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="contracts_bot", description="BranchBot Contracts Bot")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run all configured sources")
    run.add_argument("--since", type=int, default=7, help="Only include items posted in the last N days (adapters may ignore)")

    return parser.parse_args(argv)


def load_contract_filters() -> Dict[str, List[str]]:
    cfg_path = os.path.join("config", "contracts.yaml")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            return data.get("filters", {})
    return {"keywords": [], "regions": []}


def normalize_list(val: Any) -> List[str]:
    if not val:
        return []
    if isinstance(val, list):
        return [str(x).lower() for x in val]
    return [str(val).lower()]


def apply_filters(opps: List[Opportunity], filters: Dict[str, List[str]]) -> List[Opportunity]:
    kw = set(normalize_list(filters.get("keywords")))
    rg = set(normalize_list(filters.get("regions")))
    if not kw and not rg:
        return opps
    filtered: List[Opportunity] = []
    for o in opps:
        hay = f"{o.title} {o.agency} {o.location or ''} {o.category or ''}".lower()
        ok_kw = (not kw) or any(k in hay for k in kw)
        ok_rg = (not rg) or any(r in hay for r in rg)
        if ok_kw and ok_rg:
            filtered.append(o)
    return filtered


def write_markdown_report(path: str, opps: List[Opportunity]) -> None:
    by_source: Dict[str, List[Opportunity]] = {}
    for o in opps:
        by_source.setdefault(o.source, []).append(o)
    for v in by_source.values():
        v.sort(key=lambda x: (x.due_date or "9999-12-31"))
    lines: List[str] = ["# Opportunities", ""]
    for source, items in sorted(by_source.items()):
        lines.append(f"## {source}")
        lines.append("")
        for o in items:
            lines.append(f"- [{o.title}]({o.url}) — {o.agency} — due: {o.due_date or 'N/A'} (id: {o.id})")
        lines.append("")
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def create_github_issues(new_opps: List[Opportunity]) -> None:
    token = os.getenv("GH_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    if not token or not repo or not new_opps:
        return
    import requests
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    api = f"https://api.github.com/repos/{repo}/issues"
    for o in new_opps[:25]:
        title = f"{o.agency} – {o.title} (due {o.due_date or 'N/A'})"
        body = f"Source: {o.source}\nURL: {o.url}\nAgency: {o.agency}\nLocation: {o.location or ''}\nCategory: {o.category or ''}\nID: {o.id}"
        payload = {"title": title, "body": body, "labels": ["opportunity"]}
        try:
            requests.post(api, headers=headers, json=payload, timeout=15)
        except Exception:
            continue


def run_all(since_days: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    output_dir = os.path.join("data")
    logs_dir = os.path.join("logs")
    ensure_dirs([output_dir, logs_dir, ".cache", "reports", os.path.join("data", "import")])
    logger = get_logger(os.path.join(logs_dir, "contracts_bot.log"))

    filters = load_contract_filters()

    adapters = [SamApiAdapter(), MoBuysAdapter()]
    opps: List[Opportunity] = []
    for ad in adapters:
        try:
            data = ad.fetch(since_days=since_days)
            logger.info("Adapter %s returned %s items", ad.source_name, len(data))
            opps.extend(data)
        except Exception:
            logger.exception("Adapter failed: %s", getattr(ad, 'source_name', 'unknown'))

    # apply filters
    opps = apply_filters(opps, filters)

    # dedupe by id with cache
    cache_path = os.path.join(".cache", "opps.json")
    seen_ids: Set[str] = set(read_json_file(cache_path) or [])
    new_ids: Set[str] = set(o.id for o in opps if o.id not in seen_ids)
    all_ids = sorted(list(seen_ids | set(o.id for o in opps)))
    write_json_atomic(cache_path, all_ids)

    # write outputs
    opps_json_path = os.path.join("data", "opportunities.json")
    write_json_atomic(opps_json_path, [o.__dict__ for o in opps])

    report_path = os.path.join("reports", "opportunities.md")
    write_markdown_report(report_path, opps)

    meta = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "total": len(opps),
        "new_count": len(new_ids),
        "new_ids": sorted(list(new_ids)),
        "since_days": since_days,
    }

    # issues for new
    if new_ids:
        create_github_issues([o for o in opps if o.id in new_ids])

    return [o.__dict__ for o in opps], meta


def run_main() -> None:
    args = parse_args(sys.argv[1:])
    if args.command == "run":
        items, meta = run_all(since_days=args.since)
        print(json.dumps({"total": len(items), **meta}, indent=2))
        return
    raise SystemExit(1)