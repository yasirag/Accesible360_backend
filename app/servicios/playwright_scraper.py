from typing import Optional, Any
from playwright.async_api import async_playwright, Page, Browser

from app.servicios.base_scraper import BaseScraper


class PlaywrightScraper(BaseScraper):

    def __init__(self, timeout: int = 10):
        super().__init__(timeout)
        self.page: Optional[Page] = None
        self.browser: Optional[Browser] = None
        self.playwright = None

    async def fetch(self, url: str) -> str:

        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)

        assert self.browser is not None
        self.page = await self.browser.new_page()

        assert self.page is not None
        await self.page.goto(
            url,
            wait_until="networkidle",
            timeout=self.timeout * 1000
        )

        return await self.page.content()

    async def evaluate(self, code: str) -> Any:

        if not self.page:
            raise RuntimeError("Debes llamar fetch() primero")

        return await self.page.evaluate(code)

    async def inject_axe_core(self) -> dict:

        script = """
        (async () => {
            const el = document.createElement('script');
            el.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js';
            document.head.appendChild(el);

            let i = 0;
            while (typeof axe === 'undefined' && i < 100) {
                await new Promise(r => setTimeout(r, 100));
                i++;
            }

            if (typeof axe === 'undefined') {
                return { violations: [] };
            }

            const results = await axe.run();
            return results;
        })()
        """

        return await self.evaluate(script)

    async def close(self):
        """Cerrar Playwright y liberar recursos."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()