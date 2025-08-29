import sys
import subprocess
import tempfile
from pathlib import Path


def test_funnels_scaffold_writes_snapshot_with_title():
    repo_root = Path(__file__).resolve().parents[3]
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "out" / "funnels" / "funnels_snapshot.md"
        subprocess.run(
            [sys.executable, "jobs/funnels/run.py", "--out", str(out_path)],
            cwd=str(repo_root),
            check=True,
        )

        assert out_path.is_file(), f"missing: {out_path}"
        content = out_path.read_text(encoding="utf-8")
        assert "# Funnels Pulse" in content

