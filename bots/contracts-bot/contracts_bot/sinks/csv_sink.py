from __future__ import annotations

from typing import Any, Dict, List

from ..utils import write_csv_atomic


class CsvSink:
    def write(self, path: str, rows: List[Dict[str, Any]]) -> None:
        write_csv_atomic(path, rows)
