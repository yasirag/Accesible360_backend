from bs4 import BeautifulSoup
from typing import Dict, List, Any


async def parse_tables(html_content: str) -> Dict[str, Any]:

    soup = BeautifulSoup(html_content, 'html.parser')
    violations = []
    tables_found = soup.find_all('table')

    for table_idx, table in enumerate(tables_found):
        thead = table.find('thead')
        tbody = table.find('tbody')

        if not thead:
            violations.append({
                'issue': f'Tabla {table_idx + 1}: Falta <thead> - Necesita encabezados estructurados',
                'table': str(table)[:200],
                'table_index': table_idx
            })

        if not tbody:
            violations.append({
                'issue': f'Tabla {table_idx + 1}: Falta <tbody> - El contenido debe estar en <tbody>',
                'table': str(table)[:200],
                'table_index': table_idx
            })


        th_elements = table.find_all('th')

        if not th_elements:
            violations.append({
                'issue': f'Tabla {table_idx + 1}: No tiene <th> - Los encabezados deben usar <th>',
                'table': str(table)[:200],
                'table_index': table_idx
            })
        else:
            for th in th_elements:
                scope = th.get('scope')
                if not scope:
                    violations.append({
                        'issue': f'Tabla {table_idx + 1}: <th> sin scope - Agrega scope="col" o scope="row"',
                        'table': str(th)[:150],
                        'table_index': table_idx
                    })
                    break

        caption = table.find('caption')
        summary = table.get('summary')

        if not caption and not summary:
            violations.append({
                'issue': f'Tabla {table_idx + 1}: Sin descripción - Agrega <caption> o atributo summary',
                'table': str(table)[:200],
                'table_index': table_idx
            })


        rows = table.find_all('tr')
        if rows and len(rows) <= 2:
            pass

    return {
        'violations': len(violations),
        'elements': violations,
        'tables_found': len(tables_found)
    }



if __name__ == '__main__':

    html_good = """
    <table>
        <caption>Ventas mensuales</caption>
        <thead>
            <tr>
                <th scope="col">Mes</th>
                <th scope="col">Ventas</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Enero</td>
                <td>$1000</td>
            </tr>
            <tr>
                <td>Febrero</td>
                <td>$1500</td>
            </tr>
        </tbody>
    </table>
    """
    result = __import__('asyncio').run(parse_tables(html_good))
    print("Test tabla correcta:")
    print(f"   Violations: {result['violations']}")
    print(f"   Tables found: {result['tables_found']}")
    assert result['violations'] == 0, "No debería haber violations"
    assert result['tables_found'] == 1, "Debería encontrar 1 tabla"

    html_no_thead = """
    <table>
        <tr>
            <th>Mes</th>
            <th>Ventas</th>
        </tr>
        <tr>
            <td>Enero</td>
            <td>$1000</td>
        </tr>
    </table>
    """
    result = __import__('asyncio').run(parse_tables(html_no_thead))
    print("Test sin <thead>:")
    print(f"   Violations: {result['violations']}")
    assert any('Falta <thead>' in v['issue'] for v in result['elements']), "Debería detectar falta de thead"

    html_no_tbody = """
    <table>
        <thead>
            <tr><th scope="col">Mes</th></tr>
        </thead>
        <tr>
            <td>Enero</td>
        </tr>
    </table>
    """
    result = __import__('asyncio').run(parse_tables(html_no_tbody))
    print("Test sin <tbody>:")
    print(f"   Violations: {result['violations']}")
    assert any('Falta <tbody>' in v['issue'] for v in result['elements']), "Debería detectar falta de tbody"

    html_no_th = """
    <table>
        <thead>
            <tr>
                <td>Mes</td>
                <td>Ventas</td>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Enero</td>
                <td>$1000</td>
            </tr>
        </tbody>
    </table>
    """
    result = __import__('asyncio').run(parse_tables(html_no_th))
    print("Test sin <th>:")
    print(f"   Violations: {result['violations']}")
    assert any('No tiene <th>' in v['issue'] for v in result['elements']), "Debería detectar falta de th"

    html_no_scope = """
    <table>
        <caption>Datos</caption>
        <thead>
            <tr>
                <th>Mes</th>
                <th>Ventas</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Enero</td>
                <td>$1000</td>
            </tr>
        </tbody>
    </table>
    """
    result = __import__('asyncio').run(parse_tables(html_no_scope))
    print("Test <th> sin scope:")
    print(f"   Violations: {result['violations']}")
    assert any('sin scope' in v['issue'] for v in result['elements']), "Debería detectar th sin scope"


    html_no_caption = """
    <table>
        <thead>
            <tr>
                <th scope="col">Mes</th>
                <th scope="col">Ventas</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Enero</td>
                <td>$1000</td>
            </tr>
        </tbody>
    </table>
    """
    result = __import__('asyncio').run(parse_tables(html_no_caption))
    print("Test sin caption:")
    print(f"   Violations: {result['violations']}")
    assert any('Sin descripción' in v['issue'] for v in result['elements']), "Debería detectar falta de caption"


    html_multiple = """
    <table>
        <caption>Tabla 1</caption>
        <thead>
            <tr><th scope="col">A</th></tr>
        </thead>
        <tbody>
            <tr><td>1</td></tr>
        </tbody>
    </table>
    <table>
        <caption>Tabla 2</caption>
        <thead>
            <tr><th scope="col">B</th></tr>
        </thead>
        <tbody>
            <tr><td>2</td></tr>
        </tbody>
    </table>
    """
    result = __import__('asyncio').run(parse_tables(html_multiple))
    print("Test múltiples tablas:")
    print(f"   Violations: {result['violations']}")
    print(f"   Tables found: {result['tables_found']}")
    assert result['violations'] == 0, "Ambas tablas están bien"
    assert result['tables_found'] == 2, "Debería encontrar 2 tablas"

    print("\n✅ Todos los tests de table_parser pasaron!")