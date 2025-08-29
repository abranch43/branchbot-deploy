from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def generate_checklist_csv(path: Path) -> None:
    rows = [
        "step,status,notes",
        "Backup iPhone,TODO,iCloud or local iTunes",
        "Check storage,TODO,Free up at least 5GB",
        "Verify Apple ID,TODO,Have password ready",
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def generate_screen_repair_pdf(path: Path) -> None:
    # Minimal placeholder bytes; replace with real PDF generation as needed.
    content = (
        b"%PDF-1.4\n% screen repair intake placeholder\n"  # not a valid full PDF
    )
    path.write_bytes(content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Family Tech sample artifacts.")
    parser.add_argument("--out", default="out/family", help="Output directory (default: out/family)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    checklist_csv = out_dir / "iphone_upgrade_checklist.csv"
    intake_pdf = out_dir / "screen_repair_intake.pdf"

    generate_checklist_csv(checklist_csv)
    generate_screen_repair_pdf(intake_pdf)

    print(f"Wrote: {checklist_csv.resolve()}")
    print(f"Wrote: {intake_pdf.resolve()}")


if __name__ == "__main__":
    main()

