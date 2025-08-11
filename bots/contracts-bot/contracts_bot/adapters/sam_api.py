from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
import requests
from .base import Opportunity


class SamApiAdapter:
    source_name = "sam.gov"

    def __init__(self) -> None:
        self.api_key = os.getenv("SAM_API_KEY")

    def fetch(self, **kwargs: Any) -> List[Opportunity]:
        if not self.api_key:
            return []
        keywords_env = os.getenv("SAM_KEYWORDS")
        keywords = [k.strip() for k in (keywords_env or "janitorial,facility support,IT support").split(",") if k.strip()]
        base_url = "https://api.sam.gov/prod/opportunities/v2/search"
        headers = {"Accept": "application/json"}
        results: List[Opportunity] = []
        for keyword in keywords:
            params = {
                "api_key": self.api_key,
                "q": keyword,
                "noticeType": "All",
                "limit": 50,
                "offset": 0,
                "sort": "-modifiedDate",
            }
            try:
                resp = requests.get(base_url, headers=headers, params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json()
                for n in data.get("opportunitiesData", [])[:50]:
                    sol_id = n.get("solicitationNumber") or n.get("noticeId") or n.get("id")
                    if not sol_id:
                        continue
                    title = n.get("title") or n.get("description") or "Untitled"
                    agency = n.get("organizationName") or n.get("department") or "Unknown"
                    url = n.get("uiLink") or n.get("webLink") or "https://sam.gov/"
                    due = n.get("responseDeadLine")
                    created = n.get("publishDate") or n.get("modifiedDate")
                    opp = Opportunity(
                        id=str(sol_id),
                        title=title,
                        agency=agency,
                        location=None,
                        category=None,
                        source=self.source_name,
                        url=url,
                        due_date=due,
                        created_at=created,
                        raw=n,
                    )
                    results.append(opp)
            except Exception:
                continue
        return results