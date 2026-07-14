from typing import Dict, Any
from bs4 import BeautifulSoup
import httpx


async def parse_images(url: str, timeout_seconds: int = 30) -> Dict[str, Any]:

    try:

        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            html_content = response.text


        soup = BeautifulSoup(html_content, "html.parser")

        all_images = soup.find_all("img")

        images_without_alt = []
        for img in all_images:
            src = img.get("src", "")
            alt = img.get("alt", "")

            if not alt or alt.strip() == "":
                full_src = src if src.startswith("http") else url.rstrip("/") + "/" + src.lstrip("/")

                images_without_alt.append({
                    "src": full_src[:200],
                    "alt": alt if alt else None,
                    "issue": "Imagen sin descripción (atributo alt vacío)"
                })

        violation_count = len(images_without_alt)

        return {
            "indicator": "images",
            "violations": violation_count,
            "severity": "critical" if violation_count > 0 else "none",
            "elements": images_without_alt[:10],
            "wcag_criterion": "1.1.1",
            "description": "Imágenes sin texto alternativo"
        }

    except httpx.RequestError as e:
        raise Exception(f"Error descargando URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Error en parse_images: {str(e)}")


if __name__ == "__main__":
    import asyncio
    import json


    async def test():
        url = "https://example.com"
        result = await parse_images(url)
        print(json.dumps(result, indent=2))


    asyncio.run(test())