import sys
import subprocess
import tempfile
from pathlib import Path


def test_family_scaffold_creates_csv_and_pdf():
    repo_root = Path(__file__).resolve().parents[3]
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "out" / "family"
        subprocess.run(
            [sys.executable, "apps/family/main.py", "--out", str(out_dir)],
            cwd=str(repo_root),
            check=True,
        )

        csv = out_dir / "iphone_upgrade_checklist.csv"
        pdf = out_dir / "screen_repair_intake.pdf"
        assert csv.is_file(), f"missing: {csv}"
        assert pdf.is_file(), f"missing: {pdf}"

