from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

# Professional Corporate Neutral Palette
COLOR_PRIMARY = HexColor("#0f172a")      # Slate 900
COLOR_SECONDARY = HexColor("#334155")    # Slate 700
COLOR_MUTED = HexColor("#64748b")        # Slate 500
COLOR_LIGHT_BG = HexColor("#f8fafc")     # Slate 50
COLOR_BORDER = HexColor("#e2e8f0")       # Slate 200
COLOR_ACCENT = HexColor("#0d9488")       # Teal 600

# Sentiment Colors
COLOR_POS = HexColor("#10b981")          # Emerald 500
COLOR_NEU = HexColor("#f59e0b")          # Amber 500
COLOR_NEG = HexColor("#f43f5e")          # Rose 500

def get_report_styles():
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=COLOR_PRIMARY,
        spaceAfter=6
    ))
    
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=COLOR_MUTED,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=COLOR_PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="BodyRegular",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=COLOR_SECONDARY,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="CalloutText",
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=COLOR_PRIMARY
    ))

    styles.add(ParagraphStyle(
        name="FindingTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=COLOR_PRIMARY
    ))

    styles.add(ParagraphStyle(
        name="DisclaimerText",
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=11,
        textColor=COLOR_MUTED,
        spaceBefore=10
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=COLOR_PRIMARY
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=COLOR_SECONDARY
    ))

    return styles
