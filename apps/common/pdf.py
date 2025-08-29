from __future__ import annotations

from io import BytesIO
from pathlib import Path


def write_minimal_pdf(path: Path, text: str) -> None:
    """Write a small, valid one-page PDF with simple text.

    Avoids external dependencies for fast, offline generation.
    """
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
    content_stream = f"BT /F1 18 Tf 72 720 Td ({text}) Tj ET"
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

    Path(path).write_bytes(buf.getvalue())

