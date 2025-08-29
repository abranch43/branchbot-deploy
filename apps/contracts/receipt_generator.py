from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from apps.common.pdf import write_minimal_pdf
from .mo_buys_parser import Receipt, ReceiptItem


def write_receipt_json(receipt: Receipt, out_path: Path) -> None:
    total = sum(it.qty * it.price for it in receipt.items)
    payload = {
        "id": receipt.id,
        "issued_at": datetime.now(timezone.utc).isoformat(),
        "buyer": {"name": receipt.buyer_name, "email": receipt.buyer_email},
        "items": [
            {"sku": it.sku, "qty": it.qty, "price": it.price} for it in receipt.items
        ],
        "total": total,
        "currency": receipt.currency,
        "note": "Generated from MO BUYS form",
    }
    Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_compliance_pdf(receipt: Receipt, out_path: Path) -> None:
    title = f"Compliance Form: {receipt.id}"
    write_minimal_pdf(Path(out_path), title)

