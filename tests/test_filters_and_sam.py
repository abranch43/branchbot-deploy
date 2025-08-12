import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "bots" / "contracts-bot"))

from contracts_bot.adapters.base import Opportunity  # type: ignore
from contracts_bot.adapters.sam_api import SamApiAdapter  # type: ignore
from contracts_bot.run import apply_filters  # type: ignore


def test_filters_keywords_and_regions(tmp_path):
    opps = [
        Opportunity(
            id="1",
            title="Janitorial Service",
            agency="MO",
            location="Springfield",
            category=None,
            source="x",
            url="u",
            due_date=None,
            created_at=None,
            raw={},
        ),
        Opportunity(
            id="2",
            title="IT Support",
            agency="Dept",
            location="Kansas City",
            category=None,
            source="x",
            url="u",
            due_date=None,
            created_at=None,
            raw={},
        ),
    ]
    filters = {"keywords": ["janitorial"], "regions": ["Springfield"]}
    out = apply_filters(opps, filters)
    assert len(out) == 1 and out[0].id == "1"


def test_sam_skip_without_key(monkeypatch):
    monkeypatch.delenv("SAM_API_KEY", raising=False)
    s = SamApiAdapter()
    items = s.fetch(since_days=7, keywords=["janitorial"])
    assert items == []
