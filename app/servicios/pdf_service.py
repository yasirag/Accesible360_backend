import logging
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors

logger = logging.getLogger(__name__)


class PDFService:
    """Servicio para generar PDFs de auditoría con ReportLab."""

    def __init__(self):
        self.page_size = A4

    def generate_audit_pdf(self, domain: str, score: int, indicators: dict, action_plan: list, timestamp: str) -> bytes:
        try:
            logger.info(f"[PDF] Generando PDF para {domain} (score: {score})")
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=self.page_size, rightMargin=0.5 * inch, leftMargin=0.5 * inch,
                                    topMargin=0.5 * inch, bottomMargin=0.5 * inch)

            elements = []
            styles = getSampleStyleSheet()

            # Página 1: Resumen
            elements.extend(self._build_summary_page(domain, score, indicators, timestamp, styles))
            elements.append(PageBreak())

            # Página 2: Fallos detallados
            elements.extend(self._build_failures_page(action_plan, styles))

            doc.build(elements)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"[PDF] PDF generado exitosamente para {domain}")
            return pdf_bytes
        except Exception as e:
            logger.error(f"[PDF] Error generando PDF: {str(e)}")
            raise

    def _build_summary_page(self, domain, score, indicators, timestamp, styles):
        elements = []

        # Header
        title = Paragraph("<font size=20 color='#004ac6'><b>Accesible360</b></font>", styles['Heading1'])
        elements.append(title)
        subtitle = Paragraph("<font size=12 color='#666'>Auditoría de Accesibilidad Web WCAG 2.1 AA</font>",
                             styles['Normal'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.4 * inch))

        domain_para = Paragraph(f"<font size=14><b>Dominio:</b> {domain}</font>", styles['Normal'])
        elements.append(domain_para)
        elements.append(Spacer(1, 0.3 * inch))

        score_color = '#10b981' if score >= 80 else '#f59e0b' if score >= 60 else '#ef4444'
        score_status = 'EXCELENTE' if score >= 80 else 'MEJORABLE' if score >= 60 else 'CRÍTICO'

        center_style = ParagraphStyle(
            'center',
            parent=styles['Normal'],
            alignment=1,
            fontSize=48,
            textColor=colors.HexColor(score_color),
            fontName='Helvetica-Bold'
        )
        score_para = Paragraph(f"{score}/100", center_style)
        elements.append(score_para)
        elements.append(Spacer(1, 0.25 * inch))

        center_status_style = ParagraphStyle(
            'center_status',
            parent=styles['Normal'],
            alignment=1,
            fontSize=14,
            textColor=colors.HexColor(score_color),
            fontName='Helvetica-Bold'
        )
        status_para = Paragraph(score_status, center_status_style)
        elements.append(status_para)
        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph("<font size=12><b>Resumen de Indicadores</b></font>", styles['Heading3']))
        elements.append(Spacer(1, 0.15 * inch))

        table_data = [['Indicador', 'Problemas', 'Estado']]
        for name, data in indicators.items():
            violations = data.get('violations', 0)
            icon = '✅' if violations == 0 else '⚠️'
            status = 'OK' if violations == 0 else 'FALLOS'
            table_data.append([name.upper(), str(violations), f"{icon} {status}"])

        table = Table(table_data, colWidths=[2 * inch, 1.2 * inch, 1.3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004ac6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))

        footer_text = Paragraph(f"<font size=9 color='#999'>Auditoría realizada: {timestamp}</font>", styles['Normal'])
        elements.append(footer_text)

        return elements

    def _build_failures_page(self, action_plan, styles):
        elements = []

        elements.append(Paragraph("<font size=18 color='#004ac6'><b>Fallos Detectados</b></font>", styles['Heading2']))
        elements.append(Spacer(1, 0.3 * inch))

        # Mostrar solo fallos (violations > 0)
        fallo_count = 0
        for action in action_plan:
            violations = action.get('violations', 0)
            if violations == 0:
                continue  # Saltar si no hay fallos

            fallo_count += 1
            indicator = action.get('indicator', 'Fallo').upper()

            # Título del fallo
            fallo_title = Paragraph(
                f"<font size=12 color='#ef4444'><b>Fallo {fallo_count}: {indicator}</b></font>",
                styles['Normal']
            )
            elements.append(fallo_title)
            elements.append(Spacer(1, 0.1 * inch))

            # Detalles (what, why, how)
            action_elements = action.get('elements', [])
            if action_elements:
                elem = action_elements[0]

                what = elem.get('what', '')
                why = elem.get('why', '')
                how = elem.get('how', '')

                if what:
                    what_para = Paragraph(
                        f"<font size=10><b>• Problema:</b> {what}</font>",
                        styles['Normal']
                    )
                    elements.append(what_para)
                    elements.append(Spacer(1, 0.08 * inch))

                if why:
                    why_para = Paragraph(
                        f"<font size=10><b>• Impacto:</b> {why}</font>",
                        styles['Normal']
                    )
                    elements.append(why_para)
                    elements.append(Spacer(1, 0.08 * inch))

                if how:
                    how_para = Paragraph(
                        f"<font size=10 color='#10b981'><b>• Solución:</b> {how}</font>",
                        styles['Normal']
                    )
                    elements.append(how_para)
                    elements.append(Spacer(1, 0.08 * inch))

            elements.append(Spacer(1, 0.2 * inch))

        if fallo_count == 0:
            ok_para = Paragraph(
                f"<font size=12 color='#10b981'><b>✅ No hay fallos detectados. El sitio cumple con WCAG 2.1 AA.</b></font>",
                styles['Normal']
            )
            elements.append(ok_para)

        return elements