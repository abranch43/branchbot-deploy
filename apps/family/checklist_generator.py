from __future__ import annotations

from pathlib import Path


DEFAULT_STEPS = [
    ("Backup iPhone", "TODO", "iCloud or local iTunes"),
    ("Check storage", "TODO", "Free up at least 5GB"),
    ("Verify Apple ID", "TODO", "Have password ready"),
]


def write_checklist_csv(path: Path, steps=DEFAULT_STEPS) -> None:
    rows = ["step,status,notes"] + [",".join(map(str, row)) for row in steps]
    Path(path).write_text("\n".join(rows) + "\n", encoding="utf-8")

