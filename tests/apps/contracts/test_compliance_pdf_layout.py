from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from apps.contracts.mo_buys_parser import Receipt, ReceiptItem  # noqa: E402
from apps.contracts.layouts.compliance_pdf import create_compliance_pdf  # noqa: E402


def test_compliance_pdf_contains_key_text(tmp_path: Path):
    receipt = Receipt(
        id="MO-123",
        buyer_name="Sample Buyer",
        buyer_email="buyer@example.com",
        items=[ReceiptItem(sku="FORM-001", qty=1, price=0.0)],
        currency="USD",
    )
    pdf_path = tmp_path / "form.pdf"
    create_compliance_pdf(receipt, pdf_path)
    data = pdf_path.read_bytes()
    # Text is embedded as plain bytes in content stream
    assert b"MO BUYS Compliance Form" in data
    assert b"Sample Buyer" in data

