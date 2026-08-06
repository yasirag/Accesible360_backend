from fastapi import FastAPI
from app.routes import audits
from app.config import get_settings
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
settings = get_settings()

FRONTEND_URL = os.getenv(
    "CORS_FRONTEND_URL",
    "http://localhost:5173"
)

app = FastAPI(
    title="Accesible360",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(audits.router, prefix="/api/v1", tags=["audits"])


@app.get("/health")
async def health():
    return {"status": "ok"}