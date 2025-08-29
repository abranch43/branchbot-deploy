import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from apps.contracts.mo_buys_parser import parse_form_json  # noqa: E402
from apps.contracts.receipt_generator import (  # noqa: E402
    write_receipt_json,
    write_compliance_pdf,
)


def test_parse_form_json_sample():
    repo = Path(__file__).resolve().parents[3]
    sample = repo / "apps" / "contracts" / "samples" / "form_sample.json"
    receipt = parse_form_json(sample)
    assert receipt.id == "MO-BUYS-SAMPLE-002"
    assert receipt.buyer_email.endswith("@acme.example")
    assert receipt.items and receipt.items[0].sku == "FORM-001"


def test_receipt_and_pdf_generation(tmp_path: Path):
    # Build a minimal receipt and write outputs
    receipt = parse_form_json(
        Path(__file__).resolve().parents[3]
        / "apps"
        / "contracts"
        / "samples"
        / "form_sample.json"
    )
    out_dir = tmp_path / "contracts"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "receipt.json"
    pdf_path = out_dir / "form.pdf"
    write_receipt_json(receipt, json_path)
    write_compliance_pdf(receipt, pdf_path)

    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["id"] == receipt.id
    assert pdf_path.is_file() and pdf_path.stat().st_size > 20
