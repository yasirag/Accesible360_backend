import logging

logger = logging.getLogger(__name__)


class SendGridService:

    def send_audit_summary(
        self,
        customer_email: str,
        domain: str,
        score: int,
        action_plan: list
    ) -> bool:

        logger.info(
            f"[EMAIL-MOCK] Email enviado a {customer_email}\n"
            f"[EMAIL-MOCK] Dominio: {domain}\n"
            f"[EMAIL-MOCK] Score: {score}/100\n"
            f"[EMAIL-MOCK] Problemas: {len(action_plan)}"
        )
        return True