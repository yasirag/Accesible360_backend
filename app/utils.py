import re
from urllib.parse import urlparse


class URLValidationError(Exception):
    pass

def validate_url(domain: str) -> str:

    if not domain:
        raise URLValidationError("La URL no puede estar vacía.")

    domain = domain.strip()

    if " " in domain:
        raise URLValidationError("La URL no puede contener espacios.")

    if not domain.startswith(("http://", "https://")):
        domain = f"https://{domain}"

    try:
        parsed = urlparse(domain)
    except Exception as e:
        raise URLValidationError(f"URL inválida: {str(e)}")

    if parsed.scheme not in ("http", "https"):
        raise URLValidationError(
            f"Solo soportamos http:// o https://. Recibido: {parsed.scheme}://"
        )

    if not parsed.netloc:
        raise URLValidationError(
            "La URL debe tener un dominio válido. "
            "Usa: https://ejemplo.com"
        )

    if not _is_valid_domain(parsed.netloc):
        raise URLValidationError(
            f"Dominio inválido: {parsed.netloc}. "
            f"Usa: https://ejemplo.com"
        )

    return domain


def _is_valid_domain(domain: str) -> bool:

    if not domain or len(domain) < 4:
        return False

    if ":" in domain:
        domain = domain.split(":")[0]

    if "@" in domain:
        domain = domain.split("@")[1]

    domain_pattern = r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*\.[a-z]{2,}$"

    return bool(re.match(domain_pattern, domain.lower()))


def extract_domain(url: str) -> str:

    try:
        parsed = urlparse(url)
        netloc = parsed.netloc

        if ":" in netloc:
            netloc = netloc.split(":")[0]

        if netloc.startswith("www."):
            netloc = netloc[4:]

        return netloc
    except Exception:
        return url


if __name__ == "__main__":
    print("=== TESTS UTILS ===\n")

    test_urls = [
        "ejemplo.com",
        "https://www.ejemplo.com",
        "http://example.com/page",
    ]

    print("Test validate_url:")
    for url in test_urls:
        try:
            result = validate_url(url)
            print(f"  '{url}' → '{result}'")
        except URLValidationError as e:
            print(f"   '{url}' → Error: {e}")

    print("\nTest extract_domain:")
    for url in ["https://www.ejemplo.com/page", "http://subdomain.google.com"]:
        result = extract_domain(url)
        print(f"  '{url}' → '{result}'")