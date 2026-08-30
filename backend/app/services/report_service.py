from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

from app.models.ocean_data import OceanData


def generate_report(data: list[OceanData]):

    buffer = BytesIO()

    document = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("OceanAI Report", styles["Heading1"])
    )

    elements.append(
        Paragraph("<br/><br/>", styles["Normal"])
    )

    for record in data:

        text = (
            f"""
            <b>Location:</b> {record.location}<br/>
            <b>Temperature:</b> {record.temperature} °C<br/>
            <b>pH:</b> {record.ph}<br/>
            <br/>
            """
        )

        elements.append(
            Paragraph(text, styles["BodyText"])
        )

    document.build(elements)

    buffer.seek(0)

    return buffer