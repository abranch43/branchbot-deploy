import os
import sys
from pathlib import Path

# add bot package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bots" / "contracts-bot"))

from contracts_bot.adapters.mobuys_rss import MoBuysAdapter  # type: ignore


def test_mobuys_csv_parsing(tmp_path):
    data_dir = tmp_path / "data" / "import"
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_path = data_dir / "mobuys.csv"
    csv_path.write_text(
        "id,title,agency,location,category,url,due_date,created_at\nIFB-1,Trash Pickup,MO,Springfield,waste,https://ex/1,01/15/2025,2025-01-01",
        encoding="utf-8",
    )

    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        items = MoBuysAdapter().fetch()
    finally:
        os.chdir(cwd)

    assert items and items[0].id == "IFB-1"
    assert items[0].due_date == "2025-01-15"
    assert items[0].source == "MissouriBUYS"
