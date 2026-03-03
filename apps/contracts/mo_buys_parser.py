from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReceiptItem:
    """Single line item parsed from a MO BUYS receipt payload."""

    sku: str
    qty: int
    price: float


@dataclass(slots=True)
class Receipt:
    """Normalized receipt shape used by compliance PDF generation."""

    id: str
    buyer_name: str
    buyer_email: str
    items: list[ReceiptItem]
    currency: str
