import os
import logging
from datetime import datetime, timezone
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

from app.schemas.report import FullReportResponse
from app.services.export.pdf_styles import (
    get_report_styles, COLOR_PRIMARY, COLOR_SECONDARY, COLOR_MUTED,
    COLOR_LIGHT_BG, COLOR_BORDER, COLOR_ACCENT, COLOR_POS, COLOR_NEU, COLOR_NEG
)
from app.config import settings

logger = logging.getLogger(__name__)

class NumberedCanvas(canvas.Canvas):
    """Adds professional running headers and page numbers to every page."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(COLOR_MUTED)
        
        # Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, 750, "AI-Powered Opinion Intelligence Platform — Analytical Report")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer (all pages)
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Automated Intelligence Report")
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

class PDFReportBuilder:
    def __init__(self):
        self.styles = get_report_styles()
        os.makedirs(settings.STORAGE_DIR, exist_ok=True)

    def generate_pdf(self, report_data: FullReportResponse) -> str:
        """Builds a multi-page PDF report document and returns the absolute file path."""
        file_name = f"report_{report_data.id}.pdf"
        output_path = os.path.abspath(os.path.join(settings.STORAGE_DIR, file_name))

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        story = []
        r = report_data.report
        m = report_data.metrics
        sources = report_data.sources

        # 1. Header Banner
        report_title = r.report_title if r else f"Opinion Intelligence Report: {report_data.target_entity or report_data.original_prompt}"
        story.append(Paragraph(report_title, self.styles["DocTitle"]))
        
        date_str = report_data.created_at.strftime("%B %d, %Y at %H:%M UTC") if report_data.created_at else datetime.now(timezone.utc).strftime("%B %d, %Y")
        meta_line = f"Request: \"{report_data.original_prompt}\" | Generated: {date_str} | Scope: {report_data.location_scope or 'Global'} | Category: {report_data.category}"
        story.append(Paragraph(meta_line, self.styles["DocSubtitle"]))
        story.append(Spacer(1, 10))

        # 2. Executive Summary Callout Box
        if r and r.executive_summary:
            story.append(Paragraph("1. Executive Summary", self.styles["SectionHeader"]))
            callout_data = [[Paragraph(r.executive_summary, self.styles["CalloutText"])]]
            callout_table = Table(callout_data, colWidths=[504])
            callout_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), COLOR_LIGHT_BG),
                ('BOX', (0, 0), (-1, -1), 1, COLOR_BORDER),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ]))
            story.append(callout_table)
            story.append(Spacer(1, 14))

        # 3. Scorecard KPI Metrics Table
        if m:
            story.append(Paragraph("2. Quantitative Scorecard", self.styles["SectionHeader"]))
            sent = m.sentiment_distribution
            kpi_data = [
                [
                    Paragraph("<b>Total Records</b>", self.styles["TableCell"]),
                    Paragraph("<b>Overall Sentiment</b>", self.styles["TableCell"]),
                    Paragraph("<b>Net Polarity Score</b>", self.styles["TableCell"]),
                    Paragraph("<b>Primary Emotion</b>", self.styles["TableCell"])
                ],
                [
                    Paragraph(f"<font size=12><b>{m.total_records_analyzed}</b></font>", self.styles["TableHeader"]),
                    Paragraph(f"<font size=12><b>{sent.label}</b></font>", self.styles["TableHeader"]),
                    Paragraph(f"<font size=12><b>{sent.average_compound_score:+.2f}</b></font>", self.styles["TableHeader"]),
                    Paragraph(f"<font size=12><b>{max(m.emotion_scores.model_dump().items(), key=lambda x: x[1])[0].title()}</b></font>", self.styles["TableHeader"])
                ]
            ]
            kpi_table = Table(kpi_data, colWidths=[126, 126, 126, 126])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLOR_LIGHT_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(kpi_table)
            story.append(Spacer(1, 8))

            # Sentiment Breakdown Bar
            sent_bar_data = [[
                Paragraph(f"<b>Positive:</b> {sent.positive:.1f}%", self.styles["TableCell"]),
                Paragraph(f"<b>Neutral:</b> {sent.neutral:.1f}%", self.styles["TableCell"]),
                Paragraph(f"<b>Negative:</b> {sent.negative:.1f}%", self.styles["TableCell"])
            ]]
            sent_bar_table = Table(sent_bar_data, colWidths=[168, 168, 168])
            sent_bar_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), COLOR_LIGHT_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(sent_bar_table)
            story.append(Spacer(1, 14))

        # 4. Key Findings
        if r and r.key_findings:
            story.append(Paragraph("3. Key Takeaway Findings", self.styles["SectionHeader"]))
            for finding in r.key_findings:
                finding_block = [
                    Paragraph(f"• <b>{finding.title}</b>", self.styles["FindingTitle"]),
                    Paragraph(finding.description, self.styles["BodyRegular"])
                ]
                story.append(KeepTogether(finding_block))
            story.append(Spacer(1, 10))

        # 5. Major Topics & Thematic Breakdown
        if m and m.topic_clusters:
            story.append(Paragraph("4. Thematic Clusters & Discussion Themes", self.styles["SectionHeader"]))
            topic_rows = [
                [
                    Paragraph("<b>Topic / Theme</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Keywords</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Volume Share</b>", self.styles["TableHeader"]),
                    Paragraph("<b>Sentiment</b>", self.styles["TableHeader"])
                ]
            ]
            for t in m.topic_clusters[:5]:
                topic_rows.append([
                    Paragraph(t.name, self.styles["TableCell"]),
                    Paragraph(", ".join(t.keywords[:4]), self.styles["TableCell"]),
                    Paragraph(f"{t.share_percentage:.1f}%", self.styles["TableCell"]),
                    Paragraph(f"{t.sentiment_score:+.2f}", self.styles["TableCell"])
                ])
            topic_table = Table(topic_rows, colWidths=[140, 214, 75, 75])
            topic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLOR_LIGHT_BG),
                ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(topic_table)
            story.append(Spacer(1, 14))

        # 6. Trends & Predictive Forecast Narrative
        if r and (r.trend_narrative or r.forecast_interpretation):
            story.append(Paragraph("5. Temporal Trends & Predictive Forecast", self.styles["SectionHeader"]))
            if r.trend_narrative:
                story.append(Paragraph(r.trend_narrative, self.styles["BodyRegular"]))
            if r.forecast_interpretation:
                story.append(Paragraph(f"<b>Forecasting Analysis:</b> {r.forecast_interpretation}", self.styles["BodyRegular"]))
            story.append(Spacer(1, 10))

        # 7. Verified Sources & Attribution Table
        story.append(Paragraph("6. Source Attribution & Data Origin", self.styles["SectionHeader"]))
        source_rows = [
            [
                Paragraph("<b>Platform</b>", self.styles["TableHeader"]),
                Paragraph("<b>Query / URL</b>", self.styles["TableHeader"]),
                Paragraph("<b>Records Harvested</b>", self.styles["TableHeader"]),
                Paragraph("<b>Status</b>", self.styles["TableHeader"])
            ]
        ]
        if sources:
            for s in sources:
                query_display = s.query_used or s.source_url or "Direct Query"
                if len(query_display) > 45:
                    query_display = query_display[:42] + "..."
                source_rows.append([
                    Paragraph(s.platform, self.styles["TableCell"]),
                    Paragraph(query_display, self.styles["TableCell"]),
                    Paragraph(str(s.records_collected), self.styles["TableCell"]),
                    Paragraph(s.status, self.styles["TableCell"])
                ])
        else:
            source_rows.append([Paragraph("Direct Upload / Query", self.styles["TableCell"]), Paragraph("-", self.styles["TableCell"]), Paragraph(str(report_data.records_found), self.styles["TableCell"]), Paragraph("COMPLETED", self.styles["TableCell"])])

        source_table = Table(source_rows, colWidths=[90, 254, 100, 60])
        source_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_LIGHT_BG),
            ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(source_table)
        story.append(Spacer(1, 14))

        # 8. Methodological Disclaimers
        if r and r.caveats_and_disclaimers:
            story.append(Paragraph(f"<b>Methodological & Neutrality Notice:</b> {r.caveats_and_disclaimers}", self.styles["DisclaimerText"]))

        # Build document
        doc.build(story, canvasmaker=NumberedCanvas)
        logger.info(f"ReportLab generated PDF successfully at {output_path}")
        return output_path

pdf_builder = PDFReportBuilder()
