
import re
from urllib.parse import urlparse


class URLValidationError(Exception):

    pass


class URLValidator:


    def validate(self, domain: str) -> str:
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
                "La URL debe tener un dominio válido. Usa: https://ejemplo.com"
            )

        if not self._is_valid_domain(parsed.netloc):
            raise URLValidationError(
                f"Dominio inválido: {parsed.netloc}. Usa: https://ejemplo.com"
            )

        return domain

    @staticmethod
    def _is_valid_domain(domain: str) -> bool:
        """Valida dominio según RFC 1123."""
        if not domain or len(domain) < 4:
            return False

        if ":" in domain:
            domain = domain.split(":")[0]

        domain_pattern = (
            r"^(?!-)[a-z0-9-]{1,63}(?<!-)"
            r"(\.(?!-)[a-z0-9-]{1,63}(?<!-))*"
            r"\.[a-z]{2,}$"
        )

        return bool(re.match(domain_pattern, domain.lower()))