
import asyncio
from typing import Dict, Any

from app.parsers.form_parser import FormParser
from app.servicios.beautifulsoup_scraper import BeautifulSoupScraper
from app.scoring import calculate_score
from app.config import get_settings


class Auditor:
    """
    Orquestador de auditorías WCAG.

    Solo FormParser (WCAG 3.3.2 - Labels)
    """

    async def audit(self, url: str) -> Dict[str, Any]:
        """
        Auditar URL.

        Args:
            url: URL ya validada

        Returns:
            {
                "forms": {...}
            }
        """
        settings = get_settings()

        # Crear scraper BeautifulSoup
        bs_scraper = BeautifulSoupScraper(timeout=settings.playwright_timeout)

        try:
            # Inyectar scraper a parser
            form_parser = FormParser(bs_scraper)

            # Ejecutar parser
            result = await form_parser.parse(url)

            # Calcular score
            indicators = {"forms": result}
            score = calculate_score(indicators)

            return {
                "indicators": indicators,
                "score_overall": score
            }

        finally:
            # Limpiar recursos
            await bs_scraper.close()


auditor = Auditor()