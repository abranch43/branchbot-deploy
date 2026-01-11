from __future__ import annotations

from pathlib import Path
from apps.common.pdf import write_pdf_lines
from apps.contracts.mo_buys_parser import Receipt


def create_compliance_pdf(receipt: Receipt, out_path: Path) -> None:
    lines = [
        "MO BUYS Compliance Form",
        f"ID: {receipt.id}",
        f"Buyer: {receipt.buyer_name} <{receipt.buyer_email}>",
        f"Total items: {sum(i.qty for i in receipt.items)}",
        f"Currency: {receipt.currency}",
    ]
    write_pdf_lines(Path(out_path), lines, font_size=14)
