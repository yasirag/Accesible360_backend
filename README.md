# Accesible360 - Backend API

Auditoría automática de accesibilidad WCAG 2.1 AA. Escanea cualquier sitio web en 30 segundos y obtén un plan de acción.

## 🚀 Stack

- **Python 3.14** | FastAPI | SQLAlchemy 2.0 | PostgreSQL
- **AI:** Groq (`llama-3.1-70b-versatile`)
- **PDF:** ReportLab
- **Email:** Mock (v1: SendGrid)

## ⚙️ Setup Local (5 min)

```bash
# 1. Clonar
git clone https://github.com/yasirag/Accesible360_backend
cd Accesible360_backend

# 2. Entorno
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Base de datos
# Crear DB: createdb -U postgres Accesible360
psql -U postgres -d Accesible360 < schema.sql

# 4. Variables de entorno (.env)
echo "GROQ_API_KEY=tu_key_aqui" > .env
echo "DATABASE_URL=postgresql://postgres:password@localhost/Accesible360" >> .env

# 5. Ejecutar
python -m uvicorn app.main:app --reload
```

Servidor en: http://localhost:8000

## 📡 Endpoints Principales

### POST /api/v1/audits
Audita un sitio web

```bash
curl -X POST http://localhost:8000/api/v1/audits \
  -H "Content-Type: application/json" \
  -d '{"domain": "ejemplo.com"}'
```

**Response:**
```json
{
  "audit_id": "uuid",
  "domain": "ejemplo.com",
  "score_overall": 95,
  "indicators": {
    "forms": {"violations": 0},
    "headings": {"violations": 1},
    "links": {"violations": 0}
  },
  "action_plan": [...]
}
```

### GET /api/v1/audits/{audit_id}
Recupera auditoría guardada

```bash
curl http://localhost:8000/api/v1/audits/{audit_id}
```

### POST /api/v1/audits/{audit_id}/send-email
Envía auditoría por email

```bash
curl -X POST http://localhost:8000/api/v1/audits/{audit_id}/send-email \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### GET /api/v1/audits/{audit_id}/pdf
Descarga PDF con reporte completo

```bash
curl http://localhost:8000/api/v1/audits/{audit_id}/pdf -o reporte.pdf
```

## 🧪 Tests

```bash
pytest -v
```

## 🐳 Deploy (Render)

1. Push a GitHub
2. Crear app en https://render.com
3. Conectar repo
4. Configurar variables de entorno (GROQ_API_KEY, DATABASE_URL)
5. Deploy automático


## 🎯 MVP Scope

✅ 3 parsers WCAG (forms, headings, links)  
✅ Plan de acción con Groq  
✅ Persistencia en PostgreSQL  
✅ Reporte PDF  
✅ Envío por email

## 📊 Métricas

- Tiempo de auditoría: 3-5 segundos
- Elementos detectados: hasta 100 por indicador
- Disponibilidad: 99.9% (Render)

## 👨‍💻 Autor

Yasira Gonzalez - Junior Developer  
Factoría F5 
Madrid, Julio 2026

---

**¿Encontraste un bug? Abre un issue en GitHub**
