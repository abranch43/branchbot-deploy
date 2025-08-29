import sys
import subprocess
import tempfile
from pathlib import Path


def test_contracts_scaffold_creates_artifacts():
    repo_root = Path(__file__).resolve().parents[3]
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "out" / "contracts"
        subprocess.run(
            [sys.executable, "apps/contracts/main.py", "--out", str(out_dir)],
            cwd=str(repo_root),
            check=True,
        )

        receipt = out_dir / "receipts" / "receipt.sample.json"
        pdf = out_dir / "pdfs" / "form.sample.pdf"
        assert receipt.is_file(), f"missing: {receipt}"
        assert pdf.is_file(), f"missing: {pdf}"

