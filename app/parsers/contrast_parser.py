from typing import Dict, Any

from app.servicios.playwright_scraper import PlaywrightScraper


class ContrastParser:
    """Parser para WCAG 1.4.3 - Contraste mínimo 4.5:1"""

    def __init__(self, scraper: PlaywrightScraper):
        self.scraper = scraper

    async def parse(self, url: str) -> Dict[str, Any]:

        await self.scraper.fetch(url)
        axe_results = await self.scraper.inject_axe_core()

        violations = axe_results.get("violations", [])
        contrast_violations = [
            v for v in violations if v.get("id") == "color-contrast"
        ]

        elements = []
        for violation in contrast_violations:
            for node in violation.get("nodes", []):
                elements.append({
                    "selector": node.get("target", ["unknown"])[0],
                    "html": node.get("html", "")[:100],
                    "message": node.get("message", "Contraste bajo")
                })

        return {
            "indicator": "contrast",
            "violations": len(elements),
            "elements": elements,
            "wcag_criterion": "1.4.3"
        }