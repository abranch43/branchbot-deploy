from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from jobs.funnels.run import build_snapshot_from_data  # noqa: E402


def test_build_snapshot_from_data_contains_counts():
    md = build_snapshot_from_data(
        gumroad_messages=3, gumroad_sales=2, fiverr_briefs=4, upwork_jobs=5
    )
    assert "# Funnels Pulse" in md
    assert "Gumroad: 3 new messages, 2 sales" in md
    assert "Fiverr: 4 new briefs" in md
    assert "Upwork: 5 relevant jobs" in md
