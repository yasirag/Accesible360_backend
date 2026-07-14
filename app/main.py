from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings

from app.models import AuditRequest, AuditResponse

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Accesible360 inicializada")
    yield
    print("⏹️ App cerrando...")



app = FastAPI(
    title="Accesible360 API",
    description="API de auditoría WCAG 2.1 AA",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejo general de errores no controlados."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Error interno del servidor",
            "detail": str(exc) if settings.environment == "development" else None
        }
    )

@app.get("/health")
async def health_check():

    return {
            "status": "ok",
            "version": "1.0.0",
            "environment": settings.environment,
        }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Accesible360 API",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/api/v1/audits")
async def create_audit(request: AuditRequest):

    return {"message": f"Audit endpoint for {request.domain} - coming soon"}


@app.get("/api/v1/audits/{audit_id}")
async def get_audit(audit_id: str):

    return {"message": f"Get audit {audit_id} - coming soon"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info",
    )
