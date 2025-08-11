import os
import sys
from pathlib import Path

from contracts_bot.scrapers.sam_gov import SamGovScraper  # type: ignore
from contracts_bot.scrapers.missouribuys import MissouriBuysScraper  # type: ignore


def test_sam_gov_skip_without_api_key(monkeypatch):
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    s = SamGovScraper()
    items = s.fetch(__import__('datetime').datetime.utcnow())
    assert isinstance(items, list)


def test_missouribuys_returns_list(monkeypatch):
    import requests
    from types import SimpleNamespace

    def fake_get(url, timeout=20):
        html = """
        <table>
          <tr><th>ID</th><th>Title</th><th>Agency</th><th>Due</th></tr>
          <tr>
            <td>IFB-123</td>
            <td>Janitorial Services</td>
            <td>MO</td>
            <td>2025-02-01</td>
            <td><a href='/bid/IFB-123'>View</a></td>
          </tr>
        </table>
        """
        return SimpleNamespace(text=html, status_code=200, raise_for_status=lambda: None)

    monkeypatch.setattr(requests, "get", fake_get)
    items = MissouriBuysScraper().fetch(__import__('datetime').datetime.utcnow())
    assert isinstance(items, list)
    assert items and items[0]["solicitation_id"] == "IFB-123"