from __future__ import annotations

import csv
import os
from datetime import datetime
from typing import Any, List

from .base import Opportunity


class MoBuysAdapter:
    source_name = "MissouriBUYS"

    def fetch(self, **kwargs: Any) -> List[Opportunity]:
        results: List[Opportunity] = []
        import_path = os.path.join("data", "import", "mobuys.csv")
        if not os.path.exists(import_path) or os.path.getsize(import_path) == 0:
            return results
        try:
            with open(import_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = [h.strip().lower() for h in reader.fieldnames or []]
                # Case 1: full opportunities CSV with id/title...
                if set(["id", "title"]).issubset(headers):
                    for row in reader:
                        rid = str(row.get("id") or "").strip()
                        title = (row.get("title") or "").strip()
                        agency = (row.get("agency") or "Missouri").strip()
                        location = (row.get("location") or "").strip() or None
                        category = (row.get("category") or "").strip() or None
                        url = (row.get("url") or "").strip()
                        due_raw = (row.get("due_date") or "").strip()
                        created_raw = (row.get("created_at") or "").strip()
                        due_iso = None
                        created_iso = None
                        for val, out in ((due_raw, "due_iso"), (created_raw, "created_iso")):
                            if val:
                                try:
                                    try:
                                        dt = datetime.strptime(val, "%m/%d/%Y")
                                    except ValueError:
                                        dt = datetime.fromisoformat(val)
                                    if out == "due_iso":
                                        due_iso = dt.date().isoformat()
                                    else:
                                        created_iso = dt.isoformat()
                                except Exception:
                                    pass
                        if not rid or not title:
                            continue
                        results.append(
                            Opportunity(
                                id=rid,
                                title=title,
                                agency=agency,
                                location=location,
                                category=category,
                                source=self.source_name,
                                url=url,
                                due_date=due_iso,
                                created_at=created_iso,
                                raw=row,
                            )
                        )
                # Case 2: keywords CSV; accept and skip (no direct scraping here)
                elif set(["keyword", "city", "state"]).issubset(headers):
                    # We accept input for future scraping; no direct opportunities parsed.
                    # Read through to validate file structure.
                    for _row in reader:
                        pass
                    return []
        except Exception:
            return []
        return results
