from __future__ import annotations

from pathlib import Path
from apps.common.pdf import write_minimal_pdf


def write_screen_repair_intake_pdf(path: Path) -> None:
    write_minimal_pdf(Path(path), "Screen Repair Intake (Sample)")

