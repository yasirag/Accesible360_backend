
import asyncio
from typing import Dict, Any
from datetime import datetime, timezone
from playwright.async_api import async_playwright, Page
from app.utils import validate_url, extract_domain, URLValidationError
from app.parsers.contrast_parser import parse_contrast
from app.parsers.aria_parser import parse_aria


async def audit_website(domain: str, timeout_seconds: int = 30) -> Dict[str, Any]:


    try:

        validated_url = validate_url(domain)
        clean_domain = extract_domain(validated_url)


        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            page = await browser.new_page()

            try:
                max_retries = 2

                for attempt in range(1, max_retries + 1):
                    try:
                        print(f"Navegando a {validated_url} (Intento {attempt}/{max_retries})...")
                        await page.goto(
                            validated_url,
                            timeout=timeout_seconds * 1000,
                            wait_until="networkidle"
                        )

                        print(f"🔍 Ejecutando 10 parsers en paralelo...")

                        results = await asyncio.gather(

                            _call_parser("contrast", parse_contrast(page)),
                            _call_parser("aria", parse_aria(page)),
                            return_exceptions=True
                        )

                        indicators = _consolidate_results(results)

                        return {
                            "domain": clean_domain,
                            "indicators": indicators,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "status": "success"
                        }

                    except asyncio.TimeoutError:
                        if attempt < max_retries:
                            print(f"Timeout en intento {attempt}. Reintentando...")
                            await asyncio.sleep(1)
                            continue
                        else:
                            raise asyncio.TimeoutError(
                                f"El sitio no responde después de {max_retries} intentos. "
                                f"Intenta más tarde."
                            )

                    except Exception as e:
                        raise Exception(f"Error durante auditoría: {str(e)}")

            finally:
                await browser.close()

    except URLValidationError as e:
        raise URLValidationError(str(e))

    except Exception as e:
        raise Exception(f"Error inesperado en auditoría: {str(e)}")


def _consolidate_results(results) -> Dict[str, Any]:

    consolidated = {}

    for result in results:
        if isinstance(result, Exception):
            print(f"⚠️ Error en parser: {result}")
            continue

        if result is None:
            continue

        indicator_name = result.get("indicator", "unknown")

        consolidated[indicator_name] = result

    return consolidated


async def _call_parser(name: str, parser_coro):

    try:
        result = await parser_coro
        return result
    except Exception as e:
        print(f"Parser '{name}' falló: {e}")

        return {
            "indicator": name,
            "violations": 0,
            "severity": "error",
            "error": str(e),
            "elements": [],
            "wcag_criterion": "N/A",
            "description": f"Error ejecutando auditoría"
        }

if __name__ == "__main__":

    async def test_audit():

        print("="*60)
        print("TEST LOCAL: app/auditor.py")
        print("="*60 + "\n")
        print("Test 1: Auditar example.com")
        print("-" * 60)
        try:
            result = await audit_website("https://example.com", timeout_seconds=30)
            print(f"✅ Auditoría exitosa")
            print(f"   Domain: {result['domain']}")
            print(f"   Indicadores encontrados: {list(result['indicators'].keys())}")
            print(f"   Timestamp: {result['timestamp']}")
            print(f"\n   Resultados de parsers:")
            for indicator, data in result["indicators"].items():
                violations = data.get("violations", 0)
                print(f"   - {indicator}: {violations} violations")
        except Exception as e:
            print(f"Error: {e}")

        print("\n" + "="*60 + "\n")
        print("Test 2: URL inválida")
        print("-" * 60)
        try:
            await audit_website("not a valid url!!!", timeout_seconds=30)
            print(f"Debería haber lanzado error")
        except Exception as e:
            print(f"Error esperado: {e}")

        print("\n" + "="*60)

    asyncio.run(test_audit())