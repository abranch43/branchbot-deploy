from __future__ import annotations

from pathlib import Path

from apps.common.pdf import write_pdf_lines


def write_screen_repair_intake_pdf(
    out_path: Path,
    *,
    name: str,
    device: str,
    issue: str,
) -> None:
    """Create a minimal screen-repair intake PDF used by tests and intake flows."""

    lines = [
        "Screen Repair Intake",
        f"Name: {name}",
        f"Device: {device}",
        f"Issue: {issue}",
    ]
    write_pdf_lines(Path(out_path), lines, font_size=14)
