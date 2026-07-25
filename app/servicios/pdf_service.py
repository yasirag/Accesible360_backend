import logging
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, PageBreak
from reportlab.lib.units import inch

from app.servicios.pdf_builders import SummaryPageBuilder, FailuresPageBuilder

logger = logging.getLogger(__name__)


class PDFService:

    def generate_audit_pdf(self, domain: str, score: int, indicators: dict, action_plan: list, timestamp: str) -> bytes:
        try:
            logger.info(f"[PDF] Generando PDF para {domain}")
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=0.5*inch, leftMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch)

            styles = getSampleStyleSheet()
            elements = []

            summary_builder = SummaryPageBuilder(styles)
            elements.extend(summary_builder.build(domain, score, indicators, timestamp))
            elements.append(PageBreak())

            failures_builder = FailuresPageBuilder(styles)
            elements.extend(failures_builder.build(action_plan))

            doc.build(elements)
            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"[PDF] PDF generado: {len(pdf_bytes)} bytes")
            return pdf_bytes
        except Exception as e:
            logger.error(f"[PDF] Error: {str(e)}")
            raise