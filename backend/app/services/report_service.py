# ==========================================
# PDF REPORT GENERATOR — MediScan AI
# ==========================================

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.platypus import Flowable
from reportlab.lib.styles import ParagraphStyle
import os
from datetime import datetime

# ── PALETTE ───────────────────────────────────────────────────
TEAL        = colors.HexColor("#00b8a9")
TEAL_LIGHT  = colors.HexColor("#e6f9f7")
TEAL_MID    = colors.HexColor("#b2ede8")
NAVY        = colors.HexColor("#0a1628")
NAVY_MID    = colors.HexColor("#1a3a5c")
SLATE       = colors.HexColor("#4a6580")
LIGHT_GREY  = colors.HexColor("#f4f7f9")
MID_GREY    = colors.HexColor("#dde5ec")
DARK_TEXT   = colors.HexColor("#1a2633")
BODY_TEXT   = colors.HexColor("#2d3f50")
MUTED_TEXT  = colors.HexColor("#7a94aa")
RED_WARN    = colors.HexColor("#c0392b")
RED_LIGHT   = colors.HexColor("#fdf0ee")
WHITE       = colors.white

PAGE_W, PAGE_H = letter
MARGIN = 0.7 * inch
CONTENT_W = PAGE_W - 2 * MARGIN


# ── CUSTOM FLOWABLE: Colored Rule ─────────────────────────────
class ColorRule(Flowable):
    def __init__(self, color, height=2, width=None):
        Flowable.__init__(self)
        self.color = color
        self.rule_height = height
        self.rule_width = width
    def draw(self):
        w = self.rule_width or CONTENT_W
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, w, self.rule_height, fill=1, stroke=0)
    def wrap(self, *args):
        return (CONTENT_W, self.rule_height)


# ── STYLES ────────────────────────────────────────────────────
def _styles():
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "title": S("title",
            fontName="Helvetica-Bold", fontSize=24, leading=30,
            textColor=WHITE, alignment=TA_LEFT),

        "subtitle": S("subtitle",
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=colors.HexColor("#a0cfc9"), alignment=TA_LEFT),

        "meta_label": S("meta_label",
            fontName="Helvetica-Bold", fontSize=7.5, leading=11,
            textColor=MUTED_TEXT, spaceAfter=1),

        "meta_value": S("meta_value",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=DARK_TEXT),

        "section_title": S("section_title",
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=TEAL, spaceBefore=0, spaceAfter=0),

        "finding_key": S("finding_key",
            fontName="Helvetica-Bold", fontSize=9.5, leading=14,
            textColor=DARK_TEXT),

        "finding_val": S("finding_val",
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=BODY_TEXT),

        "body": S("body",
            fontName="Helvetica", fontSize=10, leading=16,
            textColor=BODY_TEXT, alignment=TA_JUSTIFY,
            spaceAfter=8),

        "caption": S("caption",
            fontName="Helvetica-Oblique", fontSize=8, leading=12,
            textColor=MUTED_TEXT, alignment=TA_CENTER),

        "disclaimer_head": S("disclaimer_head",
            fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=RED_WARN),

        "disclaimer_body": S("disclaimer_body",
            fontName="Helvetica", fontSize=8.5, leading=13,
            textColor=colors.HexColor("#7a2020")),

        "footer": S("footer",
            fontName="Helvetica", fontSize=7.5, leading=11,
            textColor=MUTED_TEXT, alignment=TA_CENTER),
    }


# ── HEADER BANNER ─────────────────────────────────────────────
def _header(styles, date_str, report_id):
    # Left: branding
    left_cell = [
        Paragraph("MediScan AI", styles["title"]),
        Spacer(1, 3),
        Paragraph("Breast Ultrasound Diagnostic Report", styles["subtitle"]),
    ]

    # Right: report meta
    meta = (
        f'<font name="Helvetica-Bold" size="7" color="#7ab8b0">REPORT ID</font><br/>'
        f'<font name="Helvetica" size="9" color="#ffffff">{report_id}</font><br/><br/>'
        f'<font name="Helvetica-Bold" size="7" color="#7ab8b0">DATE GENERATED</font><br/>'
        f'<font name="Helvetica" size="9" color="#ffffff">{date_str}</font><br/><br/>'
        f'<font name="Helvetica-Bold" size="7" color="#7ab8b0">DOCUMENT TYPE</font><br/>'
        f'<font name="Helvetica" size="9" color="#00b8a9">AI Diagnostic Report</font>'
    )
    right_cell = Paragraph(meta, ParagraphStyle("hdr_r",
        fontName="Helvetica", fontSize=9, leading=13,
        textColor=WHITE, alignment=TA_RIGHT))

    tbl = Table([[left_cell, right_cell]],
                colWidths=[CONTENT_W * 0.58, CONTENT_W * 0.42])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 22),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
        ("LEFTPADDING",   (0, 0), (0, -1),  22),
        ("RIGHTPADDING",  (1, 0), (1, -1),  22),
    ]))
    return tbl


# ── TEAL ACCENT BAR below header ──────────────────────────────
def _accent_bar():
    tbl = Table([[""]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), TEAL),
        ("ROWPADDING",    (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tbl


# ── META INFO BAR ─────────────────────────────────────────────
def _meta_bar(styles):
    cells = [
        [Paragraph("PATIENT", styles["meta_label"]),
         Paragraph("—", styles["meta_value"])],
        [Paragraph("REFERRING PHYSICIAN", styles["meta_label"]),
         Paragraph("—", styles["meta_value"])],
        [Paragraph("MODALITY", styles["meta_label"]),
         Paragraph("Breast Ultrasound", styles["meta_value"])],
        [Paragraph("AI MODEL", styles["meta_label"]),
         Paragraph("MediScan CNN v2", styles["meta_value"])],
    ]
    col_w = CONTENT_W / len(cells)
    tbl = Table([cells], colWidths=[col_w] * len(cells))
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GREY),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("LINEAFTER",     (0, 0), (-2, -1), 0.5, MID_GREY),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
    ]))
    return tbl


# ── SECTION HEADER ────────────────────────────────────────────
def _section_header(title, styles):
    tbl = Table([[Paragraph(title, styles["section_title"])]],
                colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), TEAL_LIGHT),
        ("LINEBEFORE",    (0, 0), (0, -1),  3.5, TEAL),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0.5, TEAL_MID),
    ]))
    return tbl


# ── FINDINGS TABLE ────────────────────────────────────────────
def _findings_table(findings_lines, styles):
    rows = []
    for i, line in enumerate(findings_lines):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
        else:
            key, val = "", line

        row_bg = WHITE if i % 2 == 0 else LIGHT_GREY
        rows.append((
            Paragraph(key, styles["finding_key"]),
            Paragraph(val, styles["finding_val"]),
            row_bg
        ))

    if not rows:
        return Paragraph("No findings recorded.", styles["body"])

    table_data = [[r[0], r[1]] for r in rows]
    col_w = [CONTENT_W * 0.32, CONTENT_W * 0.68]
    tbl = Table(table_data, colWidths=col_w)

    style_cmds = [
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",   (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 9),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("LINEBELOW",    (0, 0), (-1, -2), 0.5, MID_GREY),
        ("BOX",          (0, 0), (-1, -1), 0.5, MID_GREY),
    ]
    for i, (_, _, bg) in enumerate(rows):
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

    tbl.setStyle(TableStyle(style_cmds))
    return tbl


# ── DISCLAIMER BOX ────────────────────────────────────────────
def _disclaimer(styles):
    content = [
        Paragraph("⚠  IMPORTANT DISCLAIMER", styles["disclaimer_head"]),
        Spacer(1, 4),
        Paragraph(
            "This report is generated by an artificial intelligence system and does not "
            "constitute a medical diagnosis. It is intended solely for informational and "
            "research purposes. Always consult a certified radiologist or licensed physician "
            "before making any clinical or treatment decisions.",
            styles["disclaimer_body"]
        ),
    ]
    tbl = Table([[content]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), RED_LIGHT),
        ("LINEBEFORE",    (0, 0), (0, -1),  4, RED_WARN),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#e8c0bc")),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    return tbl


# ── PAGE TEMPLATE ─────────────────────────────────────────────
def _draw_page(canvas, doc):
    w, h = letter
    # Footer line
    canvas.saveState()
    canvas.setStrokeColor(MID_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 0.65 * inch, w - MARGIN, 0.65 * inch)
    # Footer text
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED_TEXT)
    canvas.drawString(MARGIN, 0.45 * inch, "MediScan AI  ·  Confidential — For Clinical Review Only")
    canvas.drawRightString(w - MARGIN, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


# ── MAIN FUNCTION ─────────────────────────────────────────────
def generate_pdf(findings, explanation, image_path):

    file_name = "ultrasound_report.pdf"
    styles = _styles()

    doc = SimpleDocTemplate(
        file_name,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.5 * inch,
        bottomMargin=0.9 * inch,
    )

    date_str  = datetime.now().strftime("%B %d, %Y  –  %H:%M")
    report_id = datetime.now().strftime("MS-%Y%m%d-%H%M%S")
    els = []

    # ── Header ──────────────────────────────────────────────────
    els.append(_header(styles, date_str, report_id))
    els.append(_accent_bar())
    els.append(Spacer(1, 10))
    els.append(_meta_bar(styles))
    els.append(Spacer(1, 22))

    # ── Findings ────────────────────────────────────────────────
    findings_lines = [l for l in findings.strip().split("\n") if l.strip()]
    els.append(KeepTogether([
        _section_header("CLINICAL FINDINGS", styles),
        Spacer(1, 8),
        _findings_table(findings_lines, styles),
    ]))
    els.append(Spacer(1, 22))

    # ── AI Explanation ──────────────────────────────────────────
    explanation_paras = [p.strip() for p in explanation.split("\n") if p.strip()]
    explanation_block = [
        _section_header("AI EXPLANATION", styles),
        Spacer(1, 12),
    ]
    for p in explanation_paras:
        explanation_block.append(Paragraph(p, styles["body"]))

    els.append(KeepTogether(explanation_block[:3]))  # keep header + first para together
    for p in explanation_block[3:]:
        els.append(p)
    els.append(Spacer(1, 22))

    # ── Annotated Image ─────────────────────────────────────────
    if image_path and os.path.exists(image_path):
        img = Image(image_path, width=3.6 * inch, height=3.6 * inch)
        img.hAlign = "CENTER"

        img_tbl = Table(
            [[img], [Paragraph("Figure 1. AI-annotated ultrasound scan", styles["caption"])]],
            colWidths=[CONTENT_W]
        )
        img_tbl.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND",    (0, 0), (0, 0),   LIGHT_GREY),
            ("TOPPADDING",    (0, 0), (0, 0),   16),
            ("BOTTOMPADDING", (0, 0), (0, 0),   16),
            ("TOPPADDING",    (0, 1), (0, 1),   6),
            ("BOTTOMPADDING", (0, 1), (0, 1),   6),
            ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ]))

        els.append(KeepTogether([
            _section_header("ANNOTATED SCAN", styles),
            Spacer(1, 12),
            img_tbl,
        ]))
        els.append(Spacer(1, 22))

    # ── Disclaimer ──────────────────────────────────────────────
    els.append(_disclaimer(styles))

    # ── Build ────────────────────────────────────────────────────
    doc.build(els, onFirstPage=_draw_page, onLaterPages=_draw_page)
    return file_name# ==========================================
# PDF REPORT GENERATOR — MediScan AI
# ==========================================

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.platypus import Flowable
from reportlab.lib.styles import ParagraphStyle
import os
import re
from datetime import datetime


def _md(text):
    """Convert markdown to ReportLab XML so bold/italic render properly in the PDF."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)           # **bold**
    text = re.sub(r'__(.+?)__',     r'<b>\1</b>', text)            # __bold__
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text)            # *italic*
    text = re.sub(r'_(.+?)_',       r'<i>\1</i>', text)            # _italic_
    text = re.sub(r'`(.+?)`',
                  r'<font name="Courier" size="9">\1</font>', text) # `code`
    text = re.sub(r'^#{1,6}\s*',    '', text, flags=re.MULTILINE)  # headings: drop # keep text
    return text.strip()

# ── PALETTE ───────────────────────────────────────────────────
TEAL        = colors.HexColor("#00b8a9")
TEAL_LIGHT  = colors.HexColor("#e6f9f7")
TEAL_MID    = colors.HexColor("#b2ede8")
NAVY        = colors.HexColor("#0a1628")
NAVY_MID    = colors.HexColor("#1a3a5c")
SLATE       = colors.HexColor("#4a6580")
LIGHT_GREY  = colors.HexColor("#f4f7f9")
MID_GREY    = colors.HexColor("#dde5ec")
DARK_TEXT   = colors.HexColor("#1a2633")
BODY_TEXT   = colors.HexColor("#2d3f50")
MUTED_TEXT  = colors.HexColor("#7a94aa")
RED_WARN    = colors.HexColor("#c0392b")
RED_LIGHT   = colors.HexColor("#fdf0ee")
WHITE       = colors.white

PAGE_W, PAGE_H = letter
MARGIN = 0.7 * inch
CONTENT_W = PAGE_W - 2 * MARGIN


# ── CUSTOM FLOWABLE: Colored Rule ─────────────────────────────
class ColorRule(Flowable):
    def __init__(self, color, height=2, width=None):
        Flowable.__init__(self)
        self.color = color
        self.rule_height = height
        self.rule_width = width
    def draw(self):
        w = self.rule_width or CONTENT_W
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, w, self.rule_height, fill=1, stroke=0)
    def wrap(self, *args):
        return (CONTENT_W, self.rule_height)


# ── STYLES ────────────────────────────────────────────────────
def _styles():
    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "title": S("title",
            fontName="Helvetica-Bold", fontSize=24, leading=30,
            textColor=WHITE, alignment=TA_LEFT),

        "subtitle": S("subtitle",
            fontName="Helvetica", fontSize=10, leading=14,
            textColor=colors.HexColor("#a0cfc9"), alignment=TA_LEFT),

        "meta_label": S("meta_label",
            fontName="Helvetica-Bold", fontSize=7.5, leading=11,
            textColor=MUTED_TEXT, spaceAfter=1),

        "meta_value": S("meta_value",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=DARK_TEXT),

        "section_title": S("section_title",
            fontName="Helvetica-Bold", fontSize=10, leading=14,
            textColor=TEAL, spaceBefore=0, spaceAfter=0),

        "finding_key": S("finding_key",
            fontName="Helvetica-Bold", fontSize=9.5, leading=14,
            textColor=DARK_TEXT),

        "finding_val": S("finding_val",
            fontName="Helvetica", fontSize=9.5, leading=14,
            textColor=BODY_TEXT),

        "body": S("body",
            fontName="Helvetica", fontSize=10, leading=16,
            textColor=BODY_TEXT, alignment=TA_JUSTIFY,
            spaceAfter=8),

        "caption": S("caption",
            fontName="Helvetica-Oblique", fontSize=8, leading=12,
            textColor=MUTED_TEXT, alignment=TA_CENTER),

        "disclaimer_head": S("disclaimer_head",
            fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=RED_WARN),

        "disclaimer_body": S("disclaimer_body",
            fontName="Helvetica", fontSize=8.5, leading=13,
            textColor=colors.HexColor("#7a2020")),

        "footer": S("footer",
            fontName="Helvetica", fontSize=7.5, leading=11,
            textColor=MUTED_TEXT, alignment=TA_CENTER),
    }


# ── HEADER BANNER ─────────────────────────────────────────────
def _header(styles, date_str, report_id):
    # Left: branding
    left_cell = [
        Paragraph("MediScan AI", styles["title"]),
        Spacer(1, 3),
        Paragraph("Breast Ultrasound Diagnostic Report", styles["subtitle"]),
    ]

    # Right: report meta
    meta = (
        f'<font name="Helvetica-Bold" size="7" color="#7ab8b0">REPORT ID</font><br/>'
        f'<font name="Helvetica" size="9" color="#ffffff">{report_id}</font><br/><br/>'
        f'<font name="Helvetica-Bold" size="7" color="#7ab8b0">DATE GENERATED</font><br/>'
        f'<font name="Helvetica" size="9" color="#ffffff">{date_str}</font><br/><br/>'
        f'<font name="Helvetica-Bold" size="7" color="#7ab8b0">DOCUMENT TYPE</font><br/>'
        f'<font name="Helvetica" size="9" color="#00b8a9">AI Diagnostic Report</font>'
    )
    right_cell = Paragraph(meta, ParagraphStyle("hdr_r",
        fontName="Helvetica", fontSize=9, leading=13,
        textColor=WHITE, alignment=TA_RIGHT))

    tbl = Table([[left_cell, right_cell]],
                colWidths=[CONTENT_W * 0.58, CONTENT_W * 0.42])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), NAVY),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 22),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 22),
        ("LEFTPADDING",   (0, 0), (0, -1),  22),
        ("RIGHTPADDING",  (1, 0), (1, -1),  22),
    ]))
    return tbl


# ── TEAL ACCENT BAR below header ──────────────────────────────
def _accent_bar():
    tbl = Table([[""]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), TEAL),
        ("ROWPADDING",    (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return tbl


# ── META INFO BAR ─────────────────────────────────────────────
def _meta_bar(styles):
    cells = [
        [Paragraph("PATIENT", styles["meta_label"]),
         Paragraph("—", styles["meta_value"])],
        [Paragraph("REFERRING PHYSICIAN", styles["meta_label"]),
         Paragraph("—", styles["meta_value"])],
        [Paragraph("MODALITY", styles["meta_label"]),
         Paragraph("Breast Ultrasound", styles["meta_value"])],
        [Paragraph("AI MODEL", styles["meta_label"]),
         Paragraph("MediScan CNN v2", styles["meta_value"])],
    ]
    col_w = CONTENT_W / len(cells)
    tbl = Table([cells], colWidths=[col_w] * len(cells))
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), LIGHT_GREY),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("LINEAFTER",     (0, 0), (-2, -1), 0.5, MID_GREY),
        ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
    ]))
    return tbl


# ── SECTION HEADER ────────────────────────────────────────────
def _section_header(title, styles):
    tbl = Table([[Paragraph(title, styles["section_title"])]],
                colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), TEAL_LIGHT),
        ("LINEBEFORE",    (0, 0), (0, -1),  3.5, TEAL),
        ("TOPPADDING",    (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("BOX",           (0, 0), (-1, -1), 0.5, TEAL_MID),
    ]))
    return tbl


# ── FINDINGS TABLE ────────────────────────────────────────────
def _findings_table(findings_lines, styles):
    rows = []
    for i, line in enumerate(findings_lines):
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
        else:
            key, val = "", line

        row_bg = WHITE if i % 2 == 0 else LIGHT_GREY
        rows.append((
            Paragraph(key, styles["finding_key"]),
            Paragraph(val, styles["finding_val"]),
            row_bg
        ))

    if not rows:
        return Paragraph("No findings recorded.", styles["body"])

    table_data = [[r[0], r[1]] for r in rows]
    col_w = [CONTENT_W * 0.32, CONTENT_W * 0.68]
    tbl = Table(table_data, colWidths=col_w)

    style_cmds = [
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",   (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 9),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("LINEBELOW",    (0, 0), (-1, -2), 0.5, MID_GREY),
        ("BOX",          (0, 0), (-1, -1), 0.5, MID_GREY),
    ]
    for i, (_, _, bg) in enumerate(rows):
        style_cmds.append(("BACKGROUND", (0, i), (-1, i), bg))

    tbl.setStyle(TableStyle(style_cmds))
    return tbl


# ── DISCLAIMER BOX ────────────────────────────────────────────
def _disclaimer(styles):
    content = [
        Paragraph("⚠  IMPORTANT DISCLAIMER", styles["disclaimer_head"]),
        Spacer(1, 4),
        Paragraph(
            "This report is generated by an artificial intelligence system and does not "
            "constitute a medical diagnosis. It is intended solely for informational and "
            "research purposes. Always consult a certified radiologist or licensed physician "
            "before making any clinical or treatment decisions.",
            styles["disclaimer_body"]
        ),
    ]
    tbl = Table([[content]], colWidths=[CONTENT_W])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), RED_LIGHT),
        ("LINEBEFORE",    (0, 0), (0, -1),  4, RED_WARN),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#e8c0bc")),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 14),
    ]))
    return tbl


# ── PAGE TEMPLATE ─────────────────────────────────────────────
def _draw_page(canvas, doc):
    w, h = letter
    # Footer line
    canvas.saveState()
    canvas.setStrokeColor(MID_GREY)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 0.65 * inch, w - MARGIN, 0.65 * inch)
    # Footer text
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED_TEXT)
    canvas.drawString(MARGIN, 0.45 * inch, "MediScan AI  ·  Confidential — For Clinical Review Only")
    canvas.drawRightString(w - MARGIN, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


# ── MAIN FUNCTION ─────────────────────────────────────────────
def generate_pdf(findings, explanation, image_path):

    file_name = "ultrasound_report.pdf"
    styles = _styles()

    doc = SimpleDocTemplate(
        file_name,
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.5 * inch,
        bottomMargin=0.9 * inch,
    )

    findings    = _md(findings)
    explanation = _md(explanation)

    date_str  = datetime.now().strftime("%B %d, %Y  –  %H:%M")
    report_id = datetime.now().strftime("MS-%Y%m%d-%H%M%S")
    els = []

    # ── Header ──────────────────────────────────────────────────
    els.append(_header(styles, date_str, report_id))
    els.append(_accent_bar())
    els.append(Spacer(1, 10))
    els.append(_meta_bar(styles))
    els.append(Spacer(1, 22))

    # ── Findings ────────────────────────────────────────────────
    findings_lines = [l for l in findings.strip().split("\n") if l.strip()]
    els.append(KeepTogether([
        _section_header("CLINICAL FINDINGS", styles),
        Spacer(1, 8),
        _findings_table(findings_lines, styles),
    ]))
    els.append(Spacer(1, 22))

    # ── AI Explanation ──────────────────────────────────────────
    explanation_paras = [p.strip() for p in explanation.split("\n") if p.strip()]
    explanation_block = [
        _section_header("AI EXPLANATION", styles),
        Spacer(1, 12),
    ]
    for p in explanation_paras:
        explanation_block.append(Paragraph(p, styles["body"]))

    els.append(KeepTogether(explanation_block[:3]))  # keep header + first para together
    for p in explanation_block[3:]:
        els.append(p)
    els.append(Spacer(1, 22))

    # ── Annotated Image ─────────────────────────────────────────
    if image_path and os.path.exists(image_path):
        img = Image(image_path, width=3.6 * inch, height=3.6 * inch)
        img.hAlign = "CENTER"

        img_tbl = Table(
            [[img], [Paragraph("Figure 1. AI-annotated ultrasound scan", styles["caption"])]],
            colWidths=[CONTENT_W]
        )
        img_tbl.setStyle(TableStyle([
            ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND",    (0, 0), (0, 0),   LIGHT_GREY),
            ("TOPPADDING",    (0, 0), (0, 0),   16),
            ("BOTTOMPADDING", (0, 0), (0, 0),   16),
            ("TOPPADDING",    (0, 1), (0, 1),   6),
            ("BOTTOMPADDING", (0, 1), (0, 1),   6),
            ("BOX",           (0, 0), (-1, -1), 0.5, MID_GREY),
        ]))

        els.append(KeepTogether([
            _section_header("ANNOTATED SCAN", styles),
            Spacer(1, 12),
            img_tbl,
        ]))
        els.append(Spacer(1, 22))

    # ── Disclaimer ──────────────────────────────────────────────
    els.append(_disclaimer(styles))

    # ── Build ────────────────────────────────────────────────────
    doc.build(els, onFirstPage=_draw_page, onLaterPages=_draw_page)
    return file_name