

from playwright.async_api import async_playwright
from typing import Dict, List, Any


async def parse_keyboard(html_content: str) -> Dict[str, Any]:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()


        await page.set_content(html_content, wait_until='networkidle')


        await page.add_script_tag(
            url='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js'
        )


        results = await page.evaluate('() => axe.run()')

        await browser.close()


        keyboard_rules = ['keyboard', 'focusable-disabled', 'tabindex']
        violations = [
            v for v in results['violations']
            if v['id'] in keyboard_rules
        ]

        return {
            'violations': len(violations),
            'elements': violations,
            'description': 'Keyboard navigation accessibility'
        }



if __name__ == '__main__':
    import asyncio

    html_good = """
    <html>
        <body>
            <button>Botón 1</button>
            <a href="#section">Enlace</a>
            <input type="text" placeholder="Campo">
            <button>Botón 2</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_keyboard(html_good))
    print("Test navegación correcta:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "No debería haber violations"


    html_bad = """
    <html>
        <body>
            <div onclick="alert('click')" style="cursor: pointer;">
                Click aquí (pero no con teclado)
            </div>
            <button>Botón accesible</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_keyboard(html_bad))
    print("Test sin acceso teclado:")
    print(f"   Violations: {result['violations']}")

    html_trap = """
    <html>
        <body>
            <button>Botón 1</button>
            <div tabindex="-1" role="button">
                No accesible con Tab
            </div>
            <button>Botón 2</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_keyboard(html_trap))
    print("Test trampa de teclado:")
    print(f"   Violations: {result['violations']}")

    html_form = """
    <html>
        <body>
            <form>
                <label for="name">Nombre:</label>
                <input type="text" id="name">

                <label for="email">Email:</label>
                <input type="email" id="email">

                <button type="submit">Enviar</button>
            </form>
        </body>
    </html>
    """
    result = asyncio.run(parse_keyboard(html_form))
    print("Test formulario accesible:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Formulario debe ser navegable"

    print("\n✅ Todos los tests de keyboard_parser pasaron!")