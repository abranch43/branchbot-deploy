from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Protocol


@dataclass
class Opportunity:
    id: str
    title: str
    agency: str
    location: str | None
    category: str | None
    source: str
    url: str
    due_date: str | None
    created_at: str | None
    raw: Dict[str, Any] | None


class Adapter(Protocol):
    source_name: str

    def fetch(self, **kwargs: Any) -> List[Opportunity]:
        ...