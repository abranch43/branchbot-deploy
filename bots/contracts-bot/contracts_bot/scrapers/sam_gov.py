from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List
import requests


class SamGovScraper:
    source_name = "sam.gov"

    def __init__(self) -> None:
        self.api_key = os.getenv("SAM_API_KEY")

    def fetch(self, cutoff: datetime) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []

        keywords_env = os.getenv("SAM_KEYWORDS")
        if keywords_env:
            keywords = [k.strip() for k in keywords_env.split(",") if k.strip()]
        else:
            keywords = ["janitorial", "facility support", "IT support"]

        results: List[Dict[str, Any]] = []
        base_url = "https://api.sam.gov/prod/opportunities/v2/search"
        headers = {"Accept": "application/json"}

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
                notices = data.get("opportunitiesData", [])
                for n in notices:
                    posted = n.get("publishDate") or n.get("modifiedDate")
                    due = n.get("responseDeadLine")
                    try:
                        posted_dt = datetime.fromisoformat(posted.replace("Z", "+00:00")) if posted else None
                    except Exception:
                        posted_dt = None
                    if posted_dt and posted_dt < cutoff:
                        continue
                    sol_id = n.get("solicitationNumber") or n.get("noticeId") or n.get("id")
                    url = n.get("uiLink") or n.get("webLink") or "https://sam.gov/"
                    agency = n.get("organizationName") or n.get("department") or "Unknown"
                    item = {
                        "solicitation_id": str(sol_id) if sol_id else None,
                        "title": n.get("title") or n.get("description") or "Untitled",
                        "agency": agency,
                        "due_date": due,
                        "url": url,
                        "source": self.source_name,
                        "posted_date": posted,
                        "raw": n,
                    }
                    if item["solicitation_id"]:
                        results.append(item)
            except Exception:
                continue
        return results