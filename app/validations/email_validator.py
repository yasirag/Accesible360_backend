import re


class EmailValidationError(Exception):
    pass


class EmailValidator:

    def validate(self, email: str) -> str:

        if not email:
            raise EmailValidationError("El email no puede estar vacío.")

        email = email.strip().lower()

        if " " in email:
            raise EmailValidationError("El email no puede contener espacios.")

        if not self._is_valid_email(email):
            raise EmailValidationError(
                f"Email inválido: {email}. Usa formato: usuario@dominio.com"
            )

        return email

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
        return bool(re.match(pattern, email))