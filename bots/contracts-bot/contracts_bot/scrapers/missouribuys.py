from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List
import requests
from bs4 import BeautifulSoup


class MissouriBuysScraper:
    source_name = "missouribuys"

    def fetch(self, cutoff: datetime) -> List[Dict[str, Any]]:
        url = "https://missouribuys.mo.gov/bidboard/Default.aspx"
        results: List[Dict[str, Any]] = []
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.find_all("tr")
            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
                link = row.find("a")
                href = link["href"] if link and link.has_attr("href") else None
                if not cols or not href:
                    continue
                sol_id = cols[0]
                title = cols[1] if len(cols) > 1 else ""
                agency = cols[2] if len(cols) > 2 else "Missouri"
                due = cols[3] if len(cols) > 3 else None
                results.append({
                    "solicitation_id": sol_id,
                    "title": title,
                    "agency": agency,
                    "due_date": due,
                    "url": f"https://missouribuys.mo.gov{href}" if href.startswith("/") else href,
                    "source": self.source_name,
                    "posted_date": None,
                })
        except Exception:
            return []
        return results