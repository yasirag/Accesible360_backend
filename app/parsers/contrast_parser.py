"""
contrast_parser.py

Detecta violaciones de contraste (WCAG 1.4.3) usando axe-core.
"""

from typing import Dict, Any
from playwright.async_api import async_playwright, Page
import json


async def run_axe_contrast(page: Page) -> Dict[str, Any]:
    """
    Ejecuta axe-core en la página y retorna violaciones de contraste.
    """

    axe_script = """
    (async () => {
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js';
        document.head.appendChild(script);

        await new Promise(resolve => {
            script.onload = resolve;
        });

        const results = await axe.run({
            runOnly: {
                type: 'rule',
                values: ['color-contrast']
            }
        });

        return results;
    })()
    """

    try:
        results = await page.evaluate(axe_script)
        return results
    except Exception as e:
        raise Exception(f"Error ejecutando axe-core: {str(e)}")


async def parse_contrast(url: str, timeout_seconds: int = 30) -> Dict[str, Any]:
    """
    Audita contraste en una URL.
    """

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=timeout_seconds * 1000, wait_until="networkidle")

            axe_results = await run_axe_contrast(page)

            violations = axe_results.get("violations", [])
            contrast_violations = [v for v in violations if v.get("id") == "color-contrast"]

            violation_count = sum(len(v.get("nodes", [])) for v in contrast_violations)

            elements = []
            for violation in contrast_violations:
                for node in violation.get("nodes", []):
                    elements.append({
                        "selector": node.get("target", ["unknown"])[0],
                        "html": node.get("html", "")[:100],
                        "issue": node.get("message", "Contraste bajo")
                    })

            return {
                "indicator": "contrast",
                "violations": violation_count,
                "severity": "critical" if violation_count > 0 else "none",
                "elements": elements[:10],
                "wcag_criterion": "1.4.3",
                "description": "Contraste insuficiente entre texto y fondo"
            }

        except Exception as e:
            raise Exception(f"Error en parse_contrast: {str(e)}")
        finally:
            await browser.close()


if __name__ == "__main__":
    import asyncio


    async def test():
        url = "https://example.com"
        result = await parse_contrast(url)
        print(json.dumps(result, indent=2))


    asyncio.run(test())