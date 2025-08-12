import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "bots" / "contracts-bot"))

from contracts_bot.adapters.sam_api import SamApiAdapter  # type: ignore


def test_sam_normalization(monkeypatch):
    monkeypatch.setenv("SAM_API_KEY", "dummy")

    def fake_req(self, url, params, max_retries=3):
        return {
            "opportunitiesData": [
                {
                    "solicitationNumber": "W91-123",
                    "title": "Custodial Services",
                    "organizationName": "Army",
                    "uiLink": "https://sam.gov/opp/W91-123",
                    "responseDeadLine": "2025-02-01",
                    "publishDate": "2025-01-10T00:00:00Z",
                    "placeOfPerformance": "Missouri",
                    "classificationCode": "S201",
                }
            ]
        }

    monkeypatch.setattr(SamApiAdapter, "_request_with_retries", fake_req)

    s = SamApiAdapter()
    items = s.fetch(since_days=7, keywords=["custodial"])
    assert items and items[0].id == "W91-123"
    assert items[0].agency == "Army"
    assert items[0].source == "sam.gov"
