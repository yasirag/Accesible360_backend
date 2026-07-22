
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from app.validations import URLValidator, URLValidationError
from app.urls import extract_domain
from app.orchestrators.auditor import auditor
from app.models import SendEmailRequest
from app.servicios.sendgrid_service import SendGridService
import logging

# Almacenamiento en memoria (temporal)
audits_memory = {}

class AuditRequest(BaseModel):
    domain: str

url_validator = URLValidator()
router = APIRouter()
logger = logging.getLogger(__name__)
sendgrid_service = SendGridService()

@router.post("/audits")
async def create_audit(request: AuditRequest):
    """Inicia auditoría WCAG 2.1 AA."""
    logger.info(f"[AUDITS] Iniciando auditoría para {request.domain}")
    try:
        clean_url = url_validator.validate(request.domain)
        domain = extract_domain(clean_url)
        logger.info(f"[AUDITS] URL válida: {clean_url}")

        result = await auditor.audit(clean_url)
        logger.info(f"[AUDITS] Auditoría completada")

        # Guardar en memoria
        audit_id = str(uuid4())
        audits_memory[audit_id] = {
            "domain": domain,
            "score_overall": result["score_overall"],
            "indicators": result["indicators"],
            "action_plan": result["action_plan"]
        }
        logger.info(f"[AUDITS] Guardado en memoria con ID: {audit_id}")

        return {
            "audit_id": audit_id,
            "domain": domain,
            "url": clean_url,
            "indicators": result["indicators"],
            "score_overall": result["score_overall"],
            "action_plan": result["action_plan"]
        }

    except URLValidationError as e:
        logger.error(f"[AUDITS] Error validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[AUDITS] Error general: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/audits/{audit_id}/send-email")
async def send_audit_email(
    audit_id: str,
    request: SendEmailRequest
):
    """Envía resumen de auditoría por email."""
    logger.info(f"[EMAIL] Enviando auditoría {audit_id} a {request.email}")
    try:
        audit = audits_memory.get(audit_id)
        if not audit:
            logger.error(f"[EMAIL] Auditoría {audit_id} no encontrada")
            raise HTTPException(status_code=404, detail="Auditoría no encontrada")

        audit["customer_email"] = request.email
        logger.info(f"[EMAIL] Email guardado: {request.email}")

        success = sendgrid_service.send_audit_summary(
            customer_email=request.email,
            domain=audit["domain"],
            score=audit["score_overall"],
            action_plan=audit["action_plan"]
        )

        if not success:
            raise HTTPException(status_code=500, detail="Error enviando email")

        logger.info(f"[EMAIL] Email enviado exitosamente")
        return {
            "success": True,
            "message": f"Email enviado a {request.email}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[EMAIL] Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error enviando email")
