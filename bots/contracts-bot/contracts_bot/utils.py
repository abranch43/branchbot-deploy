import json
import logging
import os
import shutil
import tempfile
from collections.abc import Iterable
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def load_settings() -> Dict[str, Any]:
    config_path = os.path.join("config", "settings.json")
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def ensure_dirs(paths: Iterable[str]) -> None:
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def get_logger(log_file: str) -> logging.Logger:
    logger = logging.getLogger("contracts_bot")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(ch)
        fh = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=5)
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(fh)
    return logger


def write_json_atomic(path: str, data: Any) -> None:
    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp:
        json.dump(data, tmp, indent=2, ensure_ascii=False)
        tmp_path = tmp.name
    shutil.move(tmp_path, path)


def write_csv_atomic(path: str, rows: List[Dict[str, Any]]) -> None:
    import csv

    fieldnames = [
        "solicitation_id",
        "title",
        "agency",
        "due_date",
        "url",
        "source",
        "posted_date",
    ]

    Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", newline="") as tmp:
        writer = csv.DictWriter(tmp, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})
        tmp_path = tmp.name
    shutil.move(tmp_path, path)


def read_json_file(path: str) -> Any | None:
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dedupe_by_solicitation_id(
    items: List[Dict[str, Any]], output_dir: str
) -> Tuple[List[Dict[str, Any]], Set[str]]:
    """Return (new_items, previously_seen_ids). Persist union to seen_ids.json."""
    seen_path = os.path.join(output_dir, "seen_ids.json")
    previously_seen: Set[str] = set(read_json_file(seen_path) or [])
    updated_seen: Set[str] = set(previously_seen)

    new_items: List[Dict[str, Any]] = []
    for item in items:
        sid = item.get("solicitation_id")
        if not sid:
            continue
        if sid not in updated_seen:
            new_items.append(item)
            updated_seen.add(sid)

    write_json_atomic(seen_path, sorted(list(updated_seen)))
    return new_items, previously_seen
