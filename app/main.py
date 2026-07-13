from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()
    print("✅ BD inicializada")
    yield

    print("⏹️ App cerrando...")



app = FastAPI(
    title="Accesible360 API",
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

@app.get("/health")
async def health_check():

    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "version": "1.0.0",
            "environment": settings.environment,
        }
    )


@app.post("/api/v1/audits")
async def create_audit(domain: str):

    return {"message": f"Audit endpoint for {domain} - coming soon"}


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