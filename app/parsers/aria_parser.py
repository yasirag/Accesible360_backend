from playwright.async_api import async_playwright
from typing import Dict, List, Any


async def parse_aria(html_content: str) -> Dict[str, Any]:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.set_content(html_content, wait_until='networkidle')


        await page.add_script_tag(
            url='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js'
        )


        results = await page.evaluate('() => axe.run()')

        await browser.close()


        aria_rules = [
            'aria-valid-attr',
            'aria-valid-attr-value',
            'button-name',
            'link-name',
            'aria-role',
            'aria-hidden-focus'
        ]
        violations = [
            v for v in results['violations']
            if v['id'] in aria_rules
        ]

        return {
            'violations': len(violations),
            'elements': violations,
            'description': 'ARIA attributes validity and proper usage'
        }


if __name__ == '__main__':
    import asyncio

    html_good = """
    <html>
        <body>
            <button aria-label="Cerrar menú">×</button>
            <div role="navigation" aria-label="Principal">
                <a href="#home">Home</a>
            </div>
            <div role="alert" aria-live="polite">
                Acción completada
            </div>
        </body>
    </html>
    """
    result = asyncio.run(parse_aria(html_good))
    print("✅ Test ARIA correcto:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "No debería haber violations de ARIA"

    html_typo = """
    <html>
        <body>
            <button aria-labeel="Botón">Cerrar</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_aria(html_typo))
    print("Test typo en ARIA:")
    print(f"   Violations: {result['violations']}")
    assert any('aria-valid-attr' in v['id'] for v in result['elements']), \
        "Debería detectar typo en aria"

    html_bad_value = """
    <html>
        <body>
            <button aria-expanded="maybe">Menú</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_aria(html_bad_value))
    print(" Test valor ARIA inválido:")
    print(f"   Violations: {result['violations']}")

    html_no_name = """
    <html>
        <body>
            <button>×</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_aria(html_no_name))
    print("Test botón sin nombre:")
    print(f"   Violations: {result['violations']}")

    html_bad_role = """
    <html>
        <body>
            <div role="btn">Botón</div>
        </body>
    </html>
    """
    result = asyncio.run(parse_aria(html_bad_role))
    print(" Test rol ARIA inválido:")
    print(f"   Violations: {result['violations']}")

    html_modal = """
    <html>
        <body>
            <div role="dialog" aria-labelledby="modalTitle" aria-modal="true">
                <h2 id="modalTitle">Confirmar acción</h2>
                <button aria-label="Cerrar">×</button>
            </div>
        </body>
    </html>
    """
    result = asyncio.run(parse_aria(html_modal))
    print(" Test modal con ARIA:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Modal debe tener ARIA correcto"

    print("\n✅ Todos los tests de aria_parser pasaron!")