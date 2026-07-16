from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.auditor import auditor


class AuditRequest(BaseModel):
    domain: str


router = APIRouter()


@router.post("/audits")
async def create_audit(request: AuditRequest):

    try:
        if not request.domain:
            raise HTTPException(status_code=400, detail=f"Error: {request.domain}")

        domain = request.domain.strip()
        if not domain.startswith(("http://", "https://")):
            domain = f"https://{domain}"

        result = await auditor.audit(domain)

        return {
            "domain": domain,
            "indicators": result["indicators"],
            "score_overall": result["score_overall"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")