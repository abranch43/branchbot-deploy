from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

from .base import Opportunity


class SamApiAdapter:
    source_name = "sam.gov"

    def __init__(self) -> None:
        self.api_key = os.getenv("SAM_API_KEY")

    def _request_with_retries(
        self, url: str, params: Dict[str, Any], max_retries: int = 3
    ) -> Dict[str, Any] | None:
        backoff = 1.0
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, params=params, timeout=20)
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                resp.raise_for_status()
                return resp.json()
            except Exception:
                time.sleep(backoff)
                backoff *= 2
        return None

    def fetch(self, **kwargs: Any) -> List[Opportunity]:
        if not self.api_key:
            return []

        since_days = int(kwargs.get("since_days", 7))
        keywords = kwargs.get("keywords") or []
        if not keywords:
            kw_env = os.getenv("SAM_KEYWORDS")
            keywords = [
                k.strip()
                for k in (kw_env or "janitorial,facility support,IT support").split(",")
                if k.strip()
            ]

        base_url = "https://api.sam.gov/opportunities/v1/search"
        posted_from = (datetime.utcnow() - timedelta(days=since_days)).strftime("%Y-%m-%d")

        results: List[Opportunity] = []
        for keyword in keywords:
            params = {
                "api_key": self.api_key,
                "q": keyword,
                "postedFrom": posted_from,
                "limit": 100,
                "sort": "-modifiedDate",
            }
            data = self._request_with_retries(base_url, params)
            if not data:
                continue
            notices = data.get("opportunitiesData") or data.get("results") or []
            for n in notices:
                sol_id = n.get("solicitationNumber") or n.get("noticeId") or n.get("id")
                if not sol_id:
                    continue
                title = n.get("title") or n.get("description") or "Untitled"
                agency = (
                    n.get("organizationName") or n.get("department") or n.get("agency") or "Unknown"
                )
                url = n.get("uiLink") or n.get("webLink") or n.get("url") or "https://sam.gov/"
                due = n.get("responseDeadLine") or n.get("dueDate")
                created = n.get("publishDate") or n.get("modifiedDate") or n.get("postedDate")
                location = n.get("placeOfPerformance") or None
                category = n.get("classificationCode") or n.get("naics") or None
                results.append(
                    Opportunity(
                        id=str(sol_id),
                        title=title,
                        agency=agency,
                        location=location,
                        category=category,
                        source=self.source_name,
                        url=url,
                        due_date=due,
                        created_at=created,
                        raw=n,
                    )
                )
        return results
