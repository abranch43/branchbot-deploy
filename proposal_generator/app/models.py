"""Data models for the proposal generator."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation


@dataclass
class ProposalData:
    """Structured representation of a project proposal."""

    client_name: str
    project_name: str
    scope_of_work: str
    price: Decimal
    date: datetime

    @staticmethod
    def from_dict(payload: dict) -> "ProposalData":
        """Validate *payload* and return a :class:`ProposalData` instance.

        Raises:
            ValueError: If any required field is missing, empty, or invalid.
        """
        required_fields = [
            "client_name",
            "project_name",
            "scope_of_work",
            "price",
            "date",
        ]
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing required field: '{field}'")

        string_fields = ["client_name", "project_name", "scope_of_work"]
        for field in string_fields:
            value = payload[field]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Field '{field}' must be a non-empty string")

        # Validate price
        try:
            price = Decimal(str(payload["price"]))
        except (InvalidOperation, TypeError):
            raise ValueError(
                f"Field 'price' must be a valid numeric value, got: {payload['price']!r}"
            )
        if price < 0:
            raise ValueError("Field 'price' must not be negative")

        # Validate date
        date_value = payload["date"]
        if not isinstance(date_value, str):
            raise ValueError("Field 'date' must be a string in YYYY-MM-DD format")
        try:
            date = datetime.strptime(date_value, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Field 'date' must be in YYYY-MM-DD format, got: {date_value!r}"
            )

        return ProposalData(
            client_name=payload["client_name"].strip(),
            project_name=payload["project_name"].strip(),
            scope_of_work=payload["scope_of_work"].strip(),
            price=price,
            date=date,
        )
