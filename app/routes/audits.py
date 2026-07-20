
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.validations import URLValidator, URLValidationError
from app.urls import extract_domain
from app.orchestrators.auditor import auditor
import logging

class AuditRequest(BaseModel):
    domain: str


url_validator = URLValidator()

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/audits")
async def create_audit(request: AuditRequest):
    logger.info(f"[AUDITS] Iniciando auditoría para {request.domain}")

    try:
        clean_url = url_validator.validate(request.domain)
        domain = extract_domain(clean_url)

        logger.info(f"[AUDITS] URL válida: {clean_url}")
        result = await auditor.audit(clean_url)
        logger.info(f"[AUDITS] Auditoría completada, retornando...")

        return {
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
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")