from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

app = FastAPI(
    title="Accesible360",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audits.router, prefix="/api/v1", tags=["audits"])


@app.get("/health")
async def health():
    return {"status": "ok"}


# Servir frontend estático
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    app.mount("/favicon.svg", StaticFiles(directory=static_dir), name="favicon")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        return FileResponse(os.path.join(static_dir, "index.html"))