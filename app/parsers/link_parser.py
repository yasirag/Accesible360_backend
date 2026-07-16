from typing import Dict, List, Any
from app.servicios.beautifulsoup_scraper import BeautifulSoupScraper


class LinkParser:
    """Validar que enlaces tengan texto descriptivo (WCAG 2.4.4)"""
    def __init__(self, scraper: BeautifulSoupScraper):
        self.scraper = scraper

    async def parse(self, url: str) -> Dict[str, Any]:
        await self.scraper.fetch(url)
        soup = self.scraper.get_soup()

        links = soup.find_all('a', href=True)

        generic_texts = ['click aquí', 'leer más', 'enlace', 'pulsa', '...']

        violations = []
        for link in links:
            text = link.get_text(strip=True).lower()
            if text in generic_texts or len(text) < 3:
                violations.append({
                    'type': 'generic_link_text',
                    'text': link.get_text(strip=True),
                    'href': link.get('href'),
                    'issue': f'Texto genérico: "{text}"'
                })

        return {
            'indicator': 'links',
            'violations': len(violations),
            'elements': violations,
            'wcag_criterion': '2.4.4',
            'severity': 'serio' if violations else 'ok'
        }
