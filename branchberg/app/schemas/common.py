"""Shared schema helpers."""


def normalize_currency(value: str) -> str:
    normalized = (value or "").strip().upper()
    return normalized or "USD"


def non_empty_trimmed(value: str) -> str:
    trimmed = (value or "").strip()
    if not trimmed:
        raise ValueError("must not be empty")
    return trimmed
