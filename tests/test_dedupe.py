import os
import sys
from pathlib import Path

# add bot package to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'bots' / 'contracts-bot'))

from contracts_bot.utils import dedupe_by_solicitation_id  # type: ignore  # noqa: E402


def test_dedupe_by_solicitation_id(tmp_path):
    output_dir = tmp_path / "contracts"
    output_dir.mkdir(parents=True, exist_ok=True)

    items = [
        {"solicitation_id": "A", "title": "One"},
        {"solicitation_id": "B", "title": "Two"},
        {"solicitation_id": "A", "title": "Dup"},
    ]

    new_items, seen_before = dedupe_by_solicitation_id(items, str(output_dir))
    assert len(new_items) == 2
    assert len(seen_before) == 0

    items2 = [
        {"solicitation_id": "B", "title": "Two again"},
        {"solicitation_id": "C", "title": "Three"},
    ]
    new_items2, seen_before2 = dedupe_by_solicitation_id(items2, str(output_dir))
    assert len(new_items2) == 1
    assert "C" not in seen_before2