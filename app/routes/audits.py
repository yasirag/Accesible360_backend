from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator
import logging

from app.validations import URLValidator, URLValidationError, EmailValidator, EmailValidationError
from app.urls import extract_domain
from app.orchestrators.auditor import auditor
from app.database import get_db
from app.models import Audit, EmailSubmission

class AuditRequest(BaseModel):
    domain: str


class SendEmailRequest(BaseModel):
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_validator.validate(v)
        return v.lower()


url_validator = URLValidator()
email_validator = EmailValidator()
router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/audits")
async def create_audit(
        request: AuditRequest,
        session: Session = Depends(get_db)
):

    logger.info(f"[AUDITS] Iniciando auditoría para {request.domain}")

    try:
        clean_url = url_validator.validate(request.domain)
        domain = extract_domain(clean_url)
        logger.info(f"[AUDITS] URL válida: {clean_url}")

        result = await auditor.audit(clean_url)
        logger.info(f"[AUDITS] Auditoría completada")

        audit_id = uuid4()

        audit = Audit(
            id=audit_id,
            domain=domain,
            score_overall=result["score_overall"],
            results=result["indicators"],
            screenshot_url=None,
            customer_email=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

        session.add(audit)
        session.commit()
        session.refresh(audit)

        logger.info(f"[AUDITS] Guardado en BD con ID: {audit_id}")

        return {
            "audit_id": str(audit_id),
            "domain": domain,
            "url": clean_url,
            "score_overall": result["score_overall"],
            "indicators": result["indicators"],
            "action_plan": result["action_plan"]
        }

    except URLValidationError as e:
        logger.error(f"[AUDITS] Error validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"[AUDITS] Error general: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/audits/{audit_id}")
async def get_audit(
        audit_id: str,
        session: Session = Depends(get_db)
):

    logger.info(f"[AUDITS] Recuperando audit {audit_id}")

    try:
        audit = session.query(Audit).filter(Audit.id == audit_id).first()

        if not audit:
            logger.warning(f"[AUDITS] Audit {audit_id} no encontrado")
            raise HTTPException(status_code=404, detail=f"Auditoría {audit_id} no encontrada")

        logger.info(f"[AUDITS] Audit recuperado: {audit.domain}")

        return {
            "audit_id": str(audit.id),
            "domain": audit.domain,
            "score_overall": audit.score_overall,
            "results": audit.results,
            "screenshot_url": audit.screenshot_url,
            "customer_email": audit.customer_email,
            "created_at": audit.created_at,
            "updated_at": audit.updated_at
        }

    except Exception as e:
        logger.error(f"[AUDITS] Error recuperando: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/audits/{audit_id}/send-email")
async def send_audit_email(
        audit_id: str,
        request: SendEmailRequest,
        session: Session = Depends(get_db)
):

    logger.info(f"[EMAIL] Enviando auditoría {audit_id} a {request.email}")

    try:
        email = request.email
        audit = session.query(Audit).filter(Audit.id == audit_id).first()

        if not audit:
            logger.warning(f"[EMAIL] Audit {audit_id} no encontrado")
            raise HTTPException(status_code=404, detail=f"Auditoría {audit_id} no encontrada")

        email_submission = EmailSubmission(
            id=uuid4(),
            audit_id=audit_id,
            email=email,
            status='pending'
        )

        session.add(email_submission)
        session.commit()
        session.refresh(email_submission)

        logger.info(f"[EMAIL] Email guardado: {email} para audit {audit_id}")

        return {
            "success": True,
            "message": f"Email guardado: {email}",
            "email_id": str(email_submission.id),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except EmailValidationError as e:
        logger.error(f"[EMAIL] Error validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"[EMAIL] Error: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")