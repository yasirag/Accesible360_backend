"""
link_parser.py

Detecta enlaces genéricos (WCAG 2.4.4).
Ref: https://www.w3.org/WAI/WCAG21/Understanding/link-purpose-in-context.html

Enlaces genéricos como "click aquí", "leer más", "aquí" son problemas.
Usa BeautifulSoup para parsear HTML.
"""

from typing import Dict, Any
from bs4 import BeautifulSoup
import httpx
import re

# Palabras genéricas en español e inglés
GENERIC_LINK_PATTERNS = [
    r"^click\s+(here|aquí|ahora)$",
    r"^leer\s+más$",
    r"^más$",
    r"^aquí$",
    r"^here$",
    r"^link$",
    r"^go$",
    r"^ir$",
    r"^ver$",
    r"^view$",
    r"^enter$",
    r"^\.$",  # Solo un punto
    r"^>\s*$",  # Solo símbolo
]


def is_generic_link(text: str) -> bool:
    """Verifica si el texto del link es genérico."""
    if not text or text.strip() == "":
        return True

    text_lower = text.lower().strip()

    for pattern in GENERIC_LINK_PATTERNS:
        if re.match(pattern, text_lower):
            return True

    return False


async def parse_links(url: str, timeout_seconds: int = 30) -> Dict[str, Any]:
    """
    Audita enlaces en una URL.

    Args:
        url: URL a auditar
        timeout_seconds: Timeout máximo

    Returns:
        Dict con enlaces genéricos
    """

    try:
        # 1. Descargar HTML
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            html_content = response.text

        # 2. Parsear con BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # 3. Encontrar todos los enlaces
        all_links = soup.find_all("a")

        # 4. Filtrar: enlaces genéricos
        generic_links = []
        for link in all_links:
            text = link.get_text(strip=True)
            href = link.get("href", "")

            # También considerar atributos aria-label
            aria_label = link.get("aria-label", "")
            accessible_name = aria_label or text

            if is_generic_link(accessible_name):
                generic_links.append({
                    "href": href[:200] if href else "#",
                    "text": text[:100] if text else "(sin texto)",
                    "issue": f"Enlace genérico: '{text}' - debe tener texto descriptivo"
                })

        violation_count = len(generic_links)

        return {
            "indicator": "links",
            "violations": violation_count,
            "severity": "serious" if violation_count > 0 else "none",
            "elements": generic_links[:10],
            "wcag_criterion": "2.4.4",
            "description": "Enlaces sin propósito claro (texto genérico)"
        }

    except httpx.RequestError as e:
        raise Exception(f"Error descargando URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Error en parse_links: {str(e)}")


if __name__ == "__main__":
    import asyncio
    import json


    async def test():
        url = "https://example.com"
        result = await parse_links(url)
        print(json.dumps(result, indent=2))


    asyncio.run(test())