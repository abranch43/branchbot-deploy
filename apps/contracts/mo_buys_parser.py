from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class ReceiptItem:
    sku: str
    qty: int
    price: float


@dataclass
class Receipt:
    id: str
    buyer_name: str
    buyer_email: str
    items: List[ReceiptItem]
    currency: str = "USD"


def parse_form_json(path: Path) -> Receipt:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    items = [ReceiptItem(**it) for it in data.get("items", [])]
    return Receipt(
        id=data["id"],
        buyer_name=data["buyer"]["name"],
        buyer_email=data["buyer"]["email"],
        items=items,
        currency=data.get("currency", "USD"),
    )

