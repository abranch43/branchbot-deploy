from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from apps.family.intake_generator import write_screen_repair_intake_pdf  # noqa: E402


def test_intake_pdf_contains_fields(tmp_path: Path):
    pdf_path = tmp_path / "intake.pdf"
    write_screen_repair_intake_pdf(
        pdf_path, name="Jennise", device="iPhone 12", issue="Cracked screen"
    )
    data = pdf_path.read_bytes()
    assert b"Screen Repair Intake" in data
    assert b"Jennise" in data
    assert b"iPhone 12" in data
    assert b"Cracked screen" in data
