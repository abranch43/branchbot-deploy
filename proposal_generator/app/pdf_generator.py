"""PDF generation using ReportLab."""

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors

from app.models import ProposalData


def generate_pdf(data: ProposalData, output_path: Path) -> None:
    """Render *data* as a formatted PDF and write it to *output_path*.

    Args:
        data: Validated proposal data.
        output_path: Destination file path (the parent directory will be created
            if it does not already exist).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=LETTER,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ProposalTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=18,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=14,
        spaceAfter=6,
        textColor=colors.HexColor("#2C3E50"),
    )
    body_style = ParagraphStyle(
        "ProposalBody",
        parent=styles["BodyText"],
        leading=16,
    )

    elements = []

    # Title
    elements.append(Paragraph("Project Proposal", title_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Metadata table
    price_formatted = f"${data.price:,.2f}"
    date_formatted = data.date.strftime("%B %d, %Y")

    table_data = [
        ["Client Name", data.client_name],
        ["Project Name", data.project_name],
        ["Date", date_formatted],
        ["Proposed Price", price_formatted],
    ]

    col_widths = [2 * inch, 4.5 * inch]
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ECF0F1")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#2C3E50")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(table)

    # Scope of Work section
    elements.append(Paragraph("Scope of Work", heading_style))
    for line in data.scope_of_work.splitlines():
        stripped = line.strip()
        if stripped:
            elements.append(Paragraph(stripped, body_style))
        else:
            elements.append(Spacer(1, 0.1 * inch))

    # Closing note
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(
        Paragraph(
            "We look forward to working with you on this project. "
            "Please review the details above and reach out with any questions.",
            body_style,
        )
    )

    doc.build(elements)
