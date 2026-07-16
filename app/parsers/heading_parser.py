from typing import Dict, List, Any
from app.servicios.beautifulsoup_scraper import BeautifulSoupScraper


class HeadingParser:
    """
    Parser para validar estructura de headings (WCAG 1.3.1).
    """
    def __init__(self, scraper: BeautifulSoupScraper):
        self.scraper = scraper

    async def parse(self, url: str) -> Dict[str, Any]:

        await self.scraper.fetch(url)
        soup = self.scraper.get_soup()

        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

        violations = []
        structure = []
        levels = []
        h1_count = 0

        for heading in headings:
            tag_name = heading.name
            level = int(tag_name[1])
            text = heading.get_text(strip=True)[:100]

            if level == 1:
                h1_count += 1

            levels.append(level)

            structure.append({
                'tag': tag_name,
                'text': text if text else '(vacío)',
                'level': level
            })

        if h1_count == 0:
            violations.append({
                'type': 'missing_h1',
                'issue': 'Falta H1 - La página debe tener un título principal único',
                'severity': 'crítico',
                'level': 1
            })
        elif h1_count > 1:
            violations.append({
                'type': 'multiple_h1',
                'issue': f'Múltiples H1 encontrados ({h1_count}) - Solo debe haber uno',
                'severity': 'crítico',
                'level': 1
            })

        for i in range(1, len(levels)):
            current_level = levels[i]
            previous_level = levels[i - 1]

            if current_level <= previous_level:
                continue

            jump = current_level - previous_level
            if jump > 1:
                violations.append({
                    'type': 'hierarchy_jump',
                    'issue': f'Salto de nivel: H{previous_level} → H{current_level} (solo +1 permitido)',
                    'severity': 'serio',
                    'level': current_level,
                    'from_level': previous_level,
                    'text': structure[i]['text']
                })

        return {
            'indicator': 'headings',
            'violations': len(violations),
            'elements': violations,
            'wcag_criterion': '1.3.1',
            'severity': 'serio' if violations else 'ok',
            'structure': structure,
            'h1_count': h1_count,
            'total_headings': len(headings)
        }