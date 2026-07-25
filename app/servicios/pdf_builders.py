from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors


class SummaryPageBuilder:


    def __init__(self, styles):
        self.styles = styles

    def build(self, domain, score, indicators, timestamp):
        elements = []

        title = Paragraph("<font size=20 color='#004ac6'><b>Accesible360</b></font>", self.styles['Heading1'])
        elements.append(title)
        elements.append(Paragraph("<font size=12 color='#666'>Auditoría de Accesibilidad Web WCAG 2.1 AA</font>",
                                  self.styles['Normal']))
        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph(f"<font size=14><b>Dominio:</b> {domain}</font>", self.styles['Normal']))
        elements.append(Spacer(1, 0.3 * inch))

        score_color = '#10b981' if score >= 80 else '#f59e0b' if score >= 60 else '#ef4444'
        score_status = 'EXCELENTE' if score >= 80 else 'MEJORABLE' if score >= 60 else 'CRÍTICO'

        center_style = ParagraphStyle('center', parent=self.styles['Normal'], alignment=1, fontSize=48,
                                      textColor=colors.HexColor(score_color), fontName='Helvetica-Bold')
        elements.append(Paragraph(f"{score}/100", center_style))
        elements.append(Spacer(1, 0.5 * inch))

        center_status_style = ParagraphStyle('center_status', parent=self.styles['Normal'], alignment=1, fontSize=14,
                                             textColor=colors.HexColor(score_color), fontName='Helvetica-Bold')
        elements.append(Paragraph(score_status, center_status_style))
        elements.append(Spacer(1, 0.4 * inch))

        elements.append(Paragraph("<font size=12><b>Resumen de Indicadores</b></font>", self.styles['Heading3']))
        elements.append(Spacer(1, 0.15 * inch))

        table_data = [['Indicador', 'Problemas', 'Estado']]
        if isinstance(indicators, dict):
            for name, data in indicators.items():
                if name == 'action_plan' or not isinstance(data, dict):
                    continue
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

        elements.append(
            Paragraph(f"<font size=9 color='#999'>Auditoría realizada: {timestamp}</font>", self.styles['Normal']))
        return elements


class FailuresPageBuilder:
    """Construye página 2 del PDF (fallos detallados con TODOS los elementos)."""

    def __init__(self, styles):
        self.styles = styles

    def build(self, action_plan):
        elements = []

        elements.append(Paragraph("<font size=18 color='#004ac6'><b>Fallos Detectados y Soluciones</b></font>",
                                  self.styles['Heading2']))
        elements.append(Spacer(1, 0.3 * inch))

        if not isinstance(action_plan, list) or len(action_plan) == 0:
            elements.append(Paragraph("<font size=12 color='#10b981'><b>✅ No hay fallos detectados.</b></font>",
                                      self.styles['Normal']))
            return elements

        fallo_count = 0
        for action in action_plan:
            if not isinstance(action, dict) or action.get('violations', 0) == 0:
                continue

            fallo_count += 1
            indicator = action.get('indicator', 'Fallo').upper()

            elements.append(Paragraph(f"<font size=12 color='#ef4444'><b>Fallo {fallo_count}: {indicator}</b></font>",
                                      self.styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))

            # Template genérico (si existe)
            action_elements = action.get('elements', [])
            if isinstance(action_elements, list) and len(action_elements) > 0:
                elem = action_elements[0]
                if isinstance(elem, dict):
                    what = elem.get('what', '')
                    why = elem.get('why', '')
                    how = elem.get('how', '')

                    if what:
                        elements.append(
                            Paragraph(f"<font size=10><b>• Problema:</b> {what}</font>", self.styles['Normal']))
                        elements.append(Spacer(1, 0.08 * inch))
                    if why:
                        elements.append(
                            Paragraph(f"<font size=10><b>• Impacto:</b> {why}</font>", self.styles['Normal']))
                        elements.append(Spacer(1, 0.08 * inch))
                    if how:
                        elements.append(Paragraph(f"<font size=10 color='#10b981'><b>• Solución:</b> {how}</font>",
                                                  self.styles['Normal']))
                        elements.append(Spacer(1, 0.08 * inch))

            # MOSTRAR TODOS LOS ELEMENTOS (no solo el 1ero)
            if isinstance(action_elements, list) and len(action_elements) > 0:
                elements.append(Paragraph(
                    f"<font size=9 color='#666'><b>Ubicaciones detectadas ({len(action_elements)}):</b></font>",
                    self.styles['Normal']))
                elements.append(Spacer(1, 0.08 * inch))

                for idx, elem in enumerate(action_elements[:10], 1):  # Máx 10 por rendimiento
                    if isinstance(elem, dict):
                        element_data = elem.get('element', {})
                        if isinstance(element_data, dict):
                            location_str = f"{idx}. "
                            if element_data.get('type'):
                                location_str += f"[{element_data.get('type')}] "
                            if element_data.get('id') and element_data.get('id') != 'sin-id':
                                location_str += f"ID: {element_data.get('id')} "
                            if element_data.get('href'):
                                location_str += f"URL: {element_data.get('href')[:40]}... "
                            if element_data.get('name'):
                                location_str += f"Name: {element_data.get('name')}"

                            elements.append(
                                Paragraph(f"<font size=8 color='#999'>{location_str}</font>", self.styles['Normal']))

                if len(action_elements) > 10:
                    elements.append(
                        Paragraph(f"<font size=8 color='#999'>+{len(action_elements) - 10} ubicaciones más...</font>",
                                  self.styles['Normal']))

                elements.append(Spacer(1, 0.15 * inch))

            elements.append(Spacer(1, 0.15 * inch))

        return elements