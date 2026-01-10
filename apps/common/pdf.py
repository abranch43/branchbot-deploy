from __future__ import annotations

from pathlib import Path
from typing import Iterable

def write_pdf_lines(out_path: Path, lines: Iterable[str], font_size: int = 14) -> None:
    """
    Minimal PDF writer used by layout modules.
    Requires: reportlab
    """
    from reportlab.lib.pagesizes import LETTER
    from reportlab.pdfgen.canvas import Canvas

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    canvas = Canvas(str(out_path), pagesize=LETTER)
    width, height = LETTER

    y = height - 72  # top margin
    line_height = max(font_size + 4, 14)

    canvas.setFont("Helvetica", font_size)
    for line in lines:
        if y <= 72:  # bottom margin -> new page
            canvas.showPage()
            canvas.setFont("Helvetica", font_size)
            y = height - 72
        canvas.drawString(72, y, str(line))
        y -= line_height

    canvas.save()
