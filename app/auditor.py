
import asyncio
from typing import Dict, Any

from app.parsers.form_parser import FormParser
from app.servicios.beautifulsoup_scraper import BeautifulSoupScraper
from app.parsers.heading_parser import HeadingParser
from app.parsers.link_parser import LinkParser
from app.scoring import calculate_score
from app.config import get_settings


class Auditor:

    async def audit(self, url: str) -> Dict[str, Any]:

        settings = get_settings()

        bs_scraper = BeautifulSoupScraper(timeout=settings.playwright_timeout)

        try:

            form_parser = FormParser(bs_scraper)
            heading_parser = HeadingParser(bs_scraper)
            link_parser = LinkParser(bs_scraper)

            results = await asyncio.gather(
                form_parser.parse(url),
                heading_parser.parse(url),
                link_parser.parse(url),
            )
            indicators = {"forms": results[0],
                          "headings": results[1],
                          "links": results[2],
                          }
            score = calculate_score(indicators)

            return {
                "indicators": indicators,
                "score_overall": score
            }

        finally:
            await bs_scraper.close()


auditor = Auditor()