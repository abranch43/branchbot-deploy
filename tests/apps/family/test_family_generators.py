from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from apps.family.checklist_generator import write_checklist_csv  # noqa: E402
from apps.family.intake_generator import write_screen_repair_intake_pdf  # noqa: E402


def test_family_generators(tmp_path: Path):
    out_dir = tmp_path / "family"
    out_dir.mkdir(parents=True, exist_ok=True)

    csv_path = out_dir / "iphone_upgrade_checklist.csv"
    pdf_path = out_dir / "screen_repair_intake.pdf"

    write_checklist_csv(csv_path)
    write_screen_repair_intake_pdf(pdf_path)

    assert csv_path.is_file() and csv_path.read_text(encoding="utf-8").splitlines()[0] == "step,status,notes"
    assert pdf_path.is_file() and pdf_path.stat().st_size > 20
