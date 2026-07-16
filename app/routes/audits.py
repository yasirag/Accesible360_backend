
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.validations import URLValidator, URLValidationError
from app.urls import extract_domain
from app.auditor import auditor


class AuditRequest(BaseModel):
    domain: str


url_validator = URLValidator()

router = APIRouter()


@router.post("/audits")
async def create_audit(request: AuditRequest):

    try:
        clean_url = url_validator.validate(request.domain)

        domain = extract_domain(clean_url)

        result = await auditor.audit(clean_url)

        return {
            "domain": domain,
            "url": clean_url,
            "indicators": result["indicators"],
            "score_overall": result["score_overall"]
        }

    except URLValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")