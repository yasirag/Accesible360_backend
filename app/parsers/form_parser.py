from typing import Dict, Any
from app.servicios.beautifulsoup_scraper import BeautifulSoupScraper


class FormParser:
    """Parser para WCAG 3.3.2 - Labels accesibles en formularios"""

    def __init__(self, scraper: BeautifulSoupScraper):
        self.scraper = scraper

    async def parse(self, url: str) -> Dict[str, Any]:
        await self.scraper.fetch(url)
        soup = self.scraper.get_soup()

        inputs = soup.find_all(["input", "textarea", "select"])

        violations = []

        for inp in inputs:
            input_id = inp.get("id", "").strip()
            aria_label = inp.get("aria-label", "").strip()
            input_type = inp.get("type", "").lower()

            if input_type in ["hidden", "submit", "button", "reset", "file"]:
                continue

            has_label = False
            if input_id:
                label = soup.find("label", {"for": input_id})
                if label and label.get_text(strip=True):
                    has_label = True

            if aria_label:
                has_label = True

            if not has_label:
                violations.append({
                    "type": inp.name,
                    "id": input_id or "sin-id",
                    "name": inp.get("name", ""),
                    "html": str(inp)[:100]
                })

        return {
            "indicator": "forms",
            "violations": len(violations),
            "elements": violations,
            "wcag_criterion": "3.3.2"
        }