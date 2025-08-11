from __future__ import annotations

import csv
import os
from typing import Any, List
from .base import Opportunity


class MoBuysAdapter:
    source_name = "missouribuys"

    def fetch(self, **kwargs: Any) -> List[Opportunity]:
        results: List[Opportunity] = []
        # Placeholder for RSS/CSV endpoints (if available). For now, manual import fallback.
        import_path = os.path.join("data", "import", "mobuys.csv")
        if os.path.exists(import_path):
            try:
                with open(import_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if not row.get("id") or not row.get("title"):
                            continue
                        results.append(Opportunity(
                            id=str(row.get("id")),
                            title=row.get("title", ""),
                            agency=row.get("agency", "Missouri"),
                            location=row.get("location") or None,
                            category=row.get("category") or None,
                            source=self.source_name,
                            url=row.get("url", ""),
                            due_date=row.get("due_date") or None,
                            created_at=row.get("created_at") or None,
                            raw=row,
                        ))
            except Exception:
                return []
        return results