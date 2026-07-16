from typing import Optional
from bs4 import BeautifulSoup
import httpx
from app.servicios.base_scraper import BaseScraper


class BeautifulSoupScraper(BaseScraper):

    def __init__(self, timeout: int = 10):
        super().__init__(timeout)
        self.client: Optional[httpx.AsyncClient] = None
        self.soup: Optional[BeautifulSoup] = None

    async def fetch(self, url: str) -> str:

        if not self.client:
            self.client = httpx.AsyncClient(timeout=self.timeout)

        response = await self.client.get(url, follow_redirects=True)
        response.raise_for_status()

        html = response.text
        self.soup = BeautifulSoup(html, "html.parser")

        return html

    def get_soup(self) -> BeautifulSoup:
        if not self.soup:
            raise RuntimeError("Llamar fetch() primero")
        return self.soup

    async def close(self):

        if self.client:
            await self.client.aclose()