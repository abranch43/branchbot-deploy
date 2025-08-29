from __future__ import annotations

import argparse
from pathlib import Path
import sys as _sys
from pathlib import Path as _P

if __package__ in (None, ""):
    # Ensure repo root is importable when executed as a script
    _sys.path.insert(0, str(_P(__file__).resolve().parents[2]))

from apps.family.checklist_generator import write_checklist_csv  # noqa: E402
from apps.family.intake_generator import write_screen_repair_intake_pdf  # noqa: E402




def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Family Tech sample artifacts.")
    parser.add_argument("--out", default="out/family", help="Output directory (default: out/family)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    checklist_csv = out_dir / "iphone_upgrade_checklist.csv"
    intake_pdf = out_dir / "screen_repair_intake.pdf"

    write_checklist_csv(checklist_csv)
    write_screen_repair_intake_pdf(intake_pdf)

    print(f"Wrote: {checklist_csv.resolve()}")
    print(f"Wrote: {intake_pdf.resolve()}")


if __name__ == "__main__":
    main()
