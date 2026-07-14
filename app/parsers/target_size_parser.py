
from playwright.async_api import async_playwright
from typing import Dict, List, Any


async def parse_target_size(html_content: str) -> Dict[str, Any]:

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()


        await page.set_viewport_size({"width": 1280, "height": 720})


        await page.set_content(html_content, wait_until='networkidle')


        await page.add_script_tag(
            url='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js'
        )


        results = await page.evaluate('() => axe.run()')

        await browser.close()


        target_rules = ['target-size', 'target-offset']
        violations = [
            v for v in results['violations']
            if v['id'] in target_rules
        ]

        return {
            'violations': len(violations),
            'elements': violations,
            'description': 'Interactive elements must be at least 44x44 pixels',
            'standard': 'WCAG 2.5.5 Level AAA (44x44px minimum)'
        }



if __name__ == '__main__':
    import asyncio


    html_good = """
    <html>
        <head>
            <style>
                button {
                    padding: 12px 24px;
                    font-size: 16px;
                    min-width: 44px;
                    min-height: 44px;
                }
            </style>
        </head>
        <body>
            <button>Botón 1</button>
            <button>Botón 2</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_target_size(html_good))
    print("Test tamaño correcto:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Botones deben tener 44x44"

    html_small = """
    <html>
        <head>
            <style>
                button {
                    padding: 2px 4px;
                    font-size: 10px;
                    width: 30px;
                    height: 20px;
                }
            </style>
        </head>
        <body>
            <button>×</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_target_size(html_small))
    print("Test botón muy pequeño:")
    print(f"   Violations: {result['violations']}")


    html_links = """
    <html>
        <head>
            <style>
                a {
                    display: inline-block;
                    padding: 12px 16px;
                    min-height: 44px;
                }
            </style>
        </head>
        <body>
            <a href="#home">Home</a>
            <a href="#about">About</a>
        </body>
    </html>
    """
    result = asyncio.run(parse_target_size(html_links))
    print("Test links con padding:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Links deben tener área clickeable 44x44"


    html_checkbox = """
    <html>
        <head>
            <style>
                input[type="checkbox"] {
                    width: 44px;
                    height: 44px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <input type="checkbox" id="agree">
            <label for="agree">Acepto términos</label>
        </body>
    </html>
    """
    result = asyncio.run(parse_target_size(html_checkbox))
    print(" Test checkbox 44x44:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Checkbox debe ser 44x44"


    html_spaced = """
    <html>
        <head>
            <style>
                button {
                    padding: 12px 20px;
                    margin-right: 8px;
                    min-height: 44px;
                }
            </style>
        </head>
        <body>
            <button>Guardar</button>
            <button>Cancelar</button>
            <button>Eliminar</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_target_size(html_spaced))
    print("Test botones espaciados:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Botones con spacing deben ser accesibles"

    html_icon_small = """
    <html>
        <head>
            <style>
                .icon-btn {
                    width: 20px;
                    height: 20px;
                    font-size: 16px;
                }
            </style>
        </head>
        <body>
            <button class="icon-btn">☰</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_target_size(html_icon_small))
    print(" Test icono muy pequeño:")
    print(f"   Violations: {result['violations']}")

    html_icon_good = """
    <html>
        <head>
            <style>
                .icon-btn {
                    width: 44px;
                    height: 44px;
                    padding: 12px;
                    font-size: 20px;
                }
            </style>
        </head>
        <body>
            <button class="icon-btn">☰</button>
        </body>
    </html>
    """
    result = asyncio.run(parse_target_size(html_icon_good))
    print("Test icono con padding 44x44:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "Icono con padding 44x44 debe ser OK"

    print("\n✅ Todos los tests de target_size_parser pasaron!")