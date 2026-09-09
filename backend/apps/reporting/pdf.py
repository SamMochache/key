from datetime import datetime

from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Shared KEY report palette. Keep this separate from the application UI so PDFs remain
# consistent even when the frontend theme changes.
INK = colors.HexColor("#0f172a")
MUTED = colors.HexColor("#475569")
BORDER = colors.HexColor("#cbd5e1")
SOFT = colors.HexColor("#f8fafc")
HEADER = colors.HexColor("#e2e8f0")
LABEL = colors.HexColor("#f1f5f9")


def report_styles():
    styles = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("KeyReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=INK, alignment=TA_LEFT, spaceAfter=1.5 * mm),
        "subtitle": ParagraphStyle("KeyReportSubtitle", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.5, leading=12, textColor=MUTED, spaceAfter=4 * mm),
        "heading": ParagraphStyle("KeyReportHeading", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=INK, spaceBefore=4 * mm, spaceAfter=2 * mm),
        "body": ParagraphStyle("KeyReportBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=11, textColor=INK),
        "small": ParagraphStyle("KeyReportSmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.5, leading=9.5, textColor=MUTED),
        "table": ParagraphStyle("KeyReportTable", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.8, leading=9.5, textColor=INK),
        "table_header": ParagraphStyle("KeyReportTableHeader", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.8, leading=9.5, textColor=INK),
    }


def info_table(rows, col_widths):
    table = Table(rows, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTNAME", (4, 0), (4, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, 0), (0, -1), LABEL),
        ("BACKGROUND", (2, 0), (2, -1), LABEL),
        ("BACKGROUND", (4, 0), (4, -1), LABEL),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("FONTSIZE", (0, 0), (-1, -1), 8.3),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def summary_table(row, col_widths):
    table = Table([row], colWidths=col_widths, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def data_table(rows, col_widths, repeat_rows=1, font_size=7.8, center_from=None):
    table = Table(rows, colWidths=col_widths, repeatRows=repeat_rows, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]
    if center_from is not None:
        commands.append(("ALIGN", (center_from, 1), (-1, -1), "CENTER"))
    table.setStyle(TableStyle(commands))
    return table


def report_header(story, school_name, title, subtitle=None):
    styles = report_styles()
    header = Table([[Paragraph("KEY", styles["title"]), Paragraph(school_name or "Institution", styles["body"])]], colWidths=[30 * mm, 230 * mm])
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.1, INK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(header)
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(title, styles["title"]))
    if subtitle:
        story.append(Paragraph(subtitle, styles["subtitle"]))


def footer(canvas, doc):
    canvas.saveState()
    width = doc.pagesize[0]
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(doc.leftMargin, 9 * mm, width - doc.rightMargin, 9 * mm)
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MUTED)
    timestamp = timezone.localtime(datetime.now(timezone.UTC)).strftime("%d %b %Y %H:%M")
    canvas.drawString(doc.leftMargin, 5.5 * mm, f"KEY • Generated {timestamp}")
    canvas.drawRightString(width - doc.rightMargin, 5.5 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_document(buffer, *, landscape_mode=False, title="KEY Report"):
    from reportlab.lib.pagesizes import landscape

    return SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4) if landscape_mode else A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=title,
        author="KEY",
    )
