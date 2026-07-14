
from bs4 import BeautifulSoup
from typing import Dict, List, Any


async def parse_form_labels(html_content: str) -> Dict[str, Any]:

    soup = BeautifulSoup(html_content, 'html.parser')
    violations = []


    inputs = soup.find_all('input')

    for input_elem in inputs:

        input_type = input_elem.get('type', '').lower()
        if input_type in ['hidden', 'submit', 'button', 'reset', 'file', 'image']:
            continue


        if input_elem.get('aria-hidden') == 'true':
            continue

        input_id = input_elem.get('id')
        has_aria_label = input_elem.get('aria-label')
        has_aria_labelledby = input_elem.get('aria-labelledby')
        has_title = input_elem.get('title')


        has_label = False
        if input_id:
            label = soup.find('label', {'for': input_id})
            if label and label.get_text(strip=True):
                has_label = True

        is_labeled = has_label or has_aria_label or has_aria_labelledby or has_title

        if not is_labeled:
            violations.append({
                'type': 'input',
                'tag': str(input_elem)[:150],
                'input_type': input_type,
                'issue': 'Sin label accesible (falta <label>, aria-label, aria-labelledby o title)'
            })

    return {
        'violations': len(violations),
        'elements': violations
    }



if __name__ == '__main__':

    html_bad = """
    <form>
        <input type="text" id="name" placeholder="Tu nombre">
        <input type="email" id="email">
    </form>
    """
    result = __import__('asyncio').run(parse_form_labels(html_bad))
    print("❌ Test SIN labels:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 2, "Debería encontrar 2 inputs sin label"


    html_good = """
    <form>
        <label for="name">Nombre:</label>
        <input type="text" id="name">

        <input type="email" aria-label="Tu email">

        <input type="password" title="Contraseña">
    </form>
    """
    result = __import__('asyncio').run(parse_form_labels(html_good))
    print("✅ Test CON labels:")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 0, "No debería encontrar violations"


    html_hidden = """
    <form>
        <input type="hidden" id="csrf">
        <input type="submit" value="Enviar">
        <input type="text" id="real">
    </form>
    """
    result = __import__('asyncio').run(parse_form_labels(html_hidden))
    print("✅ Test CON hidden/submit (ignorar):")
    print(f"   Violations: {result['violations']}")
    assert result['violations'] == 1, "Solo debería contar el input type='text'"

    print("\n✅ Todos los tests de form_parser pasaron!")