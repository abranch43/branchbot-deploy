from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path


def generate_checklist_csv(path: Path) -> None:
    rows = [
        "step,status,notes",
        "Backup iPhone,TODO,iCloud or local iTunes",
        "Check storage,TODO,Free up at least 5GB",
        "Verify Apple ID,TODO,Have password ready",
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_minimal_pdf(path: Path, title: str = "Screen Repair Intake") -> None:
    buf = BytesIO()
    w = lambda s: buf.write(s if isinstance(s, bytes) else s.encode("latin-1"))
    w("%PDF-1.4\n")

    offsets = []
    # 1: Catalog
    offsets.append(buf.tell())
    w("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    # 2: Pages
    offsets.append(buf.tell())
    w("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    # 3: Page
    offsets.append(buf.tell())
    w(
        "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
    )
    # 4: Contents stream
    content_stream = f"BT /F1 18 Tf 72 720 Td ({title}) Tj ET"
    cb = content_stream.encode("latin-1")
    offsets.append(buf.tell())
    w(f"4 0 obj\n<< /Length {len(cb)} >>\nstream\n")
    w(cb)
    w("\nendstream\nendobj\n")
    # 5: Font
    offsets.append(buf.tell())
    w("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")

    xref_pos = buf.tell()
    w("xref\n0 6\n")
    w("%010d %05d f \n" % (0, 65535))
    for off in offsets:
        w("%010d 00000 n \n" % off)
    w("trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n%d\n%%EOF\n" % xref_pos)

    path.write_bytes(buf.getvalue())


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Family Tech sample artifacts.")
    parser.add_argument("--out", default="out/family", help="Output directory (default: out/family)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    checklist_csv = out_dir / "iphone_upgrade_checklist.csv"
    intake_pdf = out_dir / "screen_repair_intake.pdf"

    generate_checklist_csv(checklist_csv)
    write_minimal_pdf(intake_pdf)

    print(f"Wrote: {checklist_csv.resolve()}")
    print(f"Wrote: {intake_pdf.resolve()}")


if __name__ == "__main__":
    main()
