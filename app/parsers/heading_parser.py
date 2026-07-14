
from bs4 import BeautifulSoup
from typing import Dict, List, Any


async def parse_headings(html_content: str) -> Dict[str, Any]:

    soup = BeautifulSoup(html_content, 'html.parser')
    violations = []
    structure = []


    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])


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
            'issue': 'Falta H1 - La página debe tener un título principal único',
            'heading': 'N/A',
            'level': 1
        })


    if h1_count > 1:
        violations.append({
            'issue': f'Múltiples H1 encontrados ({h1_count}) - Solo debe haber uno',
            'heading': 'Múltiples',
            'level': 1
        })


    for i in range(1, len(levels)):
        current_level = levels[i]
        previous_level = levels[i - 1]

        if current_level > previous_level:
            jump = current_level - previous_level
            if jump > 1:
                violations.append({
                    'issue': f'Salto de nivel: H{previous_level} → H{current_level} (solo +1 permitido)',
                    'heading': str(headings[i])[:150],
                    'level': current_level
                })

    return {
        'violations': len(violations),
        'elements': violations,
        'structure': structure,
        'h1_count': h1_count,
        'total_headings': len(headings)
    }



if __name__ == '__main__':

    html_good = """
    <html>
        <h1>Título Principal</h1>
        <h2>Sección 1</h2>
        <h3>Subsección 1.1</h3>
        <h2>Sección 2</h2>
        <h3>Subsección 2.1</h3>
    </html>
    """
    result = __import__('asyncio').run(parse_headings(html_good))
    print("Test jerarquía correcta:")
    print(f"   Violations: {result['violations']}")
    print(f"   H1 count: {result['h1_count']}")
    print(f"   Total headings: {result['total_headings']}")
    assert result['violations'] == 0, "No debería haber violations"
    assert result['h1_count'] == 1, "Debería haber 1 H1"
    assert result['total_headings'] == 5, "Debería haber 5 headings totales"


    html_no_h1 = """
    <html>
        <h2>Sección sin H1</h2>
        <h3>Subsección</h3>
    </html>
    """
    result = __import__('asyncio').run(parse_headings(html_no_h1))
    print("Test falta H1:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] >= 1, "Debería detectar falta de H1"
    assert result['h1_count'] == 0, "No debería haber H1"


    html_multiple_h1 = """
    <html>
        <h1>Título 1</h1>
        <h2>Sección</h2>
        <h1>Título 2</h1>
    </html>
    """
    result = __import__('asyncio').run(parse_headings(html_multiple_h1))
    print("Test múltiples H1:")
    print(f"   Violations: {result['violations']}")
    print(f"   H1 count: {result['h1_count']}")
    assert result['h1_count'] == 2, "Debería contar 2 H1s"
    assert any('Múltiples H1' in v['issue'] for v in result['elements']), "Debería alertar sobre múltiples H1"


    html_jump = """
    <html>
        <h1>Título</h1>
        <h3>Subsección sin H2</h3>
    </html>
    """
    result = __import__('asyncio').run(parse_headings(html_jump))
    print("Test salto de nivel (H1 → H3):")
    print(f"   Violations: {result['violations']}")
    assert any('Salto de nivel' in v['issue'] for v in result['elements']), "Debería detectar salto H1→H3"


    html_empty = """
    <html>
        <h1>Título</h1>
        <h2></h2>
        <h3>Subsección</h3>
    </html>
    """
    result = __import__('asyncio').run(parse_headings(html_empty))
    print("Test heading vacío:")
    print(f"   Violations: {result['violations']}")
    print(f"   Total headings: {result['total_headings']}")
    assert result['total_headings'] == 3, "Debería contar headings vacíos también"

    print("\n✅ Todos los tests de heading_parser pasaron!")