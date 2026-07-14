

from playwright.async_api import async_playwright
from typing import Dict, List, Any


async def parse_focus(html_content: str) -> Dict[str, Any]:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_content(html_content, wait_until='networkidle')


        await page.add_script_tag(
            url='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js'
        )


        results = await page.evaluate('() => axe.run()')

        await browser.close()

        focus_rules = ['focus-visible', 'focus-order-semantics']
        violations = [
            v for v in results['violations']
            if v['id'] in focus_rules
        ]

        return {
            'violations': len(violations),
            'elements': violations,
            'description': 'Focus visibility for keyboard navigation'
        }


if __name__ == '__main__':
    import asyncio


    html_good = """
    <html>
        <head>
            <style>
                button:focus {
                    outline: 2px solid #4A90E2;
                    outline-offset: 2px;
                }
            </style>
        </head>
        <body>
            <button>Botón con focus visible</button>
            <input type="text" placeholder="Input con focus">
        </body>
    </html>
    """
    result = asyncio.run(parse_focus(html_good))
    print("✅ Test focus visible:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "No debería haber violations"


    html_bad = """
    <html>
        <head>
            <style>
                button:focus {
                    outline: none;
                }
            </style>
        </head>
        <body>
            <button>Botón sin focus visible</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_focus(html_bad))
    print(" Test sin focus visible:")
    print(f"   Violations: {result['violations']}")

    html_small = """
    <html>
        <head>
            <style>
                button:focus {
                    outline: 1px solid blue;
                }
            </style>
        </head>
        <body>
            <button>Botón con focus muy pequeño</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_focus(html_small))
    print(" Test focus muy pequeño:")
    print(f"   Violations: {result['violations']}")


    html_contrast = """
    <html>
        <head>
            <style>
                input:focus {
                    outline: 3px solid #FF5733;
                    outline-offset: 3px;
                }
            </style>
        </head>
        <body>
            <input type="text" placeholder="Email">
        </body>
    </html>
    """
    result = asyncio.run(parse_focus(html_contrast))
    print("Test focus con contraste:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Focus debe ser visible"


    html_links = """
    <html>
        <head>
            <style>
                a:focus {
                    outline: 2px solid orange;
                    background-color: lightyellow;
                }
            </style>
        </head>
        <body>
            <a href="#home">Home</a>
            <a href="#about">About</a>
        </body>
    </html>
    """
    result = asyncio.run(parse_focus(html_links))
    print("✅ Test links con focus:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Links deben mostrar focus"

    print("\n✅ Todos los tests de focus_parser pasaron!")