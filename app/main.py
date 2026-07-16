from fastapi import FastAPI
from app.routes import audits
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Accesible360",
    version="0.1.0"
)

app.include_router(audits.router, prefix="/api/v1", tags=["audits"])


@app.get("/health")
async def health():
    return {"status": "ok"}