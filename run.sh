#!/bin/bash
# Ejecutar migraciones primero
alembic upgrade head

# Luego iniciar app
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
