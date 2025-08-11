from __future__ import annotations

import os
from typing import Any, Dict, List
import requests


class NotionSink:
    def __init__(self) -> None:
        self.token = os.getenv("NOTION_TOKEN")
        self.database_id = os.getenv("NOTION_DB_ID")

    def write(self, rows: List[Dict[str, Any]]) -> None:
        if not self.token or not self.database_id:
            return
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }
        url = "https://api.notion.com/v1/pages"
        for r in rows[:50]:
            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Title": {"title": [{"text": {"content": r.get("title", "Untitled")}}]},
                    "Solicitation ID": {"rich_text": [{"text": {"content": r.get("solicitation_id", "")}}]},
                    "Agency": {"rich_text": [{"text": {"content": r.get("agency", "")}}]},
                    "Due Date": {"date": {"start": r.get("due_date")}} if r.get("due_date") else None,
                    "URL": {"url": r.get("url")},
                    "Source": {"rich_text": [{"text": {"content": r.get("source", "")}}]},
                },
            }
            payload["properties"] = {k: v for k, v in payload["properties"].items() if v is not None}
            try:
                requests.post(url, headers=headers, json=payload, timeout=20)
            except Exception:
                continue