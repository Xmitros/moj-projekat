"""
PDF Generator - Fiskalni račun i profit izvještaj
Koristi ReportLab biblioteku
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO
from datetime import datetime


# Boje brenda
GOLD = colors.HexColor("#C9A84C")
DARK = colors.HexColor("#1A1A2E")
LIGHT_GRAY = colors.HexColor("#F5F5F5")
WHITE = colors.white


def _header_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        "BrosHeader",
        parent=styles["Title"],
        fontSize=24,
        textColor=GOLD,
        alignment=TA_CENTER,
        spaceAfter=2,
        fontName="Helvetica-Bold",
    )


def _subtitle_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        "BrosSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.gray,
        alignment=TA_CENTER,
        spaceAfter=12,
    )


def _normal_style():
    styles = getSampleStyleSheet()
    return ParagraphStyle(
        "BrosNormal",
        parent=styles["Normal"],
        fontSize=10,
        textColor=DARK,
    )


def generate_receipt(appt) -> bytes:
    """
    Generiše fiskalni račun za jedan termin.
    appt: sqlite3.Row sa poljima iz appointments + worker_name, user_name
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=3 * cm,
        leftMargin=3 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    normal = _normal_style()

    # --- ZAGLAVLJE ---
    story.append(Paragraph("✂ BROS", _header_style()))
    story.append(Paragraph("Frizerski Salon", _subtitle_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=16))

    # Broj računa i datum
    receipt_no = f"R-{appt['id']:05d}"
    issued_on = datetime.now().strftime("%d.%m.%Y %H:%M")

    info_data = [
        ["Broj računa:", receipt_no],
        ["Datum izdavanja:", issued_on],
        ["Klijent:", appt["user_name"]],
        ["Frizer:", appt["worker_name"]],
    ]

    info_table = Table(info_data, colWidths=[6 * cm, 9 * cm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.gray),
        ("TEXTCOLOR", (1, 0), (1, -1), DARK),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # --- STAVKE ---
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY, spaceAfter=8))

    items_header = ["Usluga", "Datum", "Termin", "Cijena"]
    items_data = [
        items_header,
        [
            appt["service"] or "Šišanje",
            appt["appointment_date"],
            appt["appointment_time"],
            f"{appt['price']:.2f} KM",
        ],
    ]

    items_table = Table(items_data, colWidths=[6 * cm, 4 * cm, 3 * cm, 3 * cm])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GRAY),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GRAY, WHITE]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 8))

    # --- UKUPNO ---
    total_data = [
        ["", "", "UKUPNO:", f"{appt['price']:.2f} KM"],
    ]
    total_table = Table(total_data, colWidths=[6 * cm, 4 * cm, 3 * cm, 3 * cm])
    total_table.setStyle(TableStyle([
        ("FONTNAME", (2, 0), (3, 0), "Helvetica-Bold"),
        ("FONTSIZE", (2, 0), (3, 0), 12),
        ("TEXTCOLOR", (2, 0), (2, 0), colors.gray),
        ("TEXTCOLOR", (3, 0), (3, 0), GOLD),
        ("ALIGN", (3, 0), (3, 0), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(total_table)

    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=12))

    # --- STATUS ---
    status_color = colors.green if appt["status"] == "zakazano" else colors.gray
    status_text = appt["status"].upper()
    status_style = ParagraphStyle(
        "status",
        fontSize=12,
        textColor=status_color,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )
    story.append(Paragraph(f"Status: {status_text}", status_style))
    story.append(Spacer(1, 16))

    # --- FOOTER ---
    footer_style = ParagraphStyle(
        "footer",
        fontSize=9,
        textColor=colors.gray,
        alignment=TA_CENTER,
    )
    story.append(Paragraph("Hvala na posjeti! · BROS Frizerski Salon", footer_style))
    story.append(Paragraph("Ponovo vas vidimo uskoro! ✂", footer_style))

    doc.build(story)
    return buf.getvalue()


def generate_profit_report(appointments, by_worker, total, month: str) -> bytes:
    """
    Generiše PDF profit izvještaj za admin.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []

    # Naslov
    story.append(Paragraph("✂ BROS — Profit Izvještaj", _header_style()))

    try:
        dt = datetime.strptime(month, "%Y-%m")
        month_label = dt.strftime("%B %Y")
    except Exception:
        month_label = month

    story.append(Paragraph(f"Period: {month_label}", _subtitle_style()))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=16))

    # --- SAŽETAK PO RADNIKU ---
    story.append(Paragraph("Pregled po radnicima", ParagraphStyle(
        "section", fontSize=13, fontName="Helvetica-Bold",
        textColor=DARK, spaceAfter=8
    )))

    summary_data = [["Radnik", "Br. termina", "Prihod (KM)"]]
    for r in by_worker:
        summary_data.append([
            r["name"],
            str(r["count"]),
            f"{r['total']:.2f}",
        ])
    summary_data.append(["UKUPNO", str(sum(r["count"] for r in by_worker)), f"{total:.2f}"])

    summary_table = Table(summary_data, colWidths=[8 * cm, 5 * cm, 4 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [LIGHT_GRAY, WHITE]),
        ("BACKGROUND", (0, -1), (-1, -1), GOLD),
        ("TEXTCOLOR", (0, -1), (-1, -1), WHITE),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))

    # --- DETALJNA LISTA ---
    if appointments:
        story.append(Paragraph("Detaljna lista termina", ParagraphStyle(
            "section", fontSize=13, fontName="Helvetica-Bold",
            textColor=DARK, spaceAfter=8
        )))

        detail_data = [["Datum", "Termin", "Klijent", "Frizer", "Usluga", "Cijena"]]
        for a in appointments:
            detail_data.append([
                a["appointment_date"],
                a["appointment_time"],
                a["user_name"],
                a["worker_name"],
                a["service"] or "Šišanje",
                f"{a['price']:.2f}",
            ])

        col_widths = [3 * cm, 2.5 * cm, 4 * cm, 3 * cm, 3.5 * cm, 2.5 * cm]
        detail_table = Table(detail_data, colWidths=col_widths)
        detail_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_GRAY, WHITE]),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(detail_table)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=2, color=GOLD, spaceAfter=8))

    generated = datetime.now().strftime("%d.%m.%Y %H:%M")
    story.append(Paragraph(
        f"Izvještaj generisan: {generated} · BROS Frizerski Salon",
        ParagraphStyle("footer", fontSize=8, textColor=colors.gray, alignment=TA_CENTER)
    ))

    doc.build(story)
    return buf.getvalue()
