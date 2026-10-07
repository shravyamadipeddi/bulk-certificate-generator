from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path("generated_certificates")
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_certificate(
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    event_date: str
) -> str:

    file_path = OUTPUT_DIR / (
        f"certificate_{certificate_id}_{recipient_name.replace(' ', '_')}.pdf"
    )

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=landscape(A4)
    )

    # Title
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 120,
        "CERTIFICATE OF PARTICIPATION"
    )

    # Main text
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 190,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 240,
        recipient_name
    )

    # Event
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 290,
        f"for participating in {event_name}"
    )

    # Date
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 340,
        f"Date: {event_date}"
    )

    # Signature
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        page_width / 2,
        100,
        "Authorized Signature"
    )

    pdf.line(
        page_width / 2 - 80,
        115,
        page_width / 2 + 80,
        115
    )

    pdf.save()

    return str(file_path)