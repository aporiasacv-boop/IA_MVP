# Olnatura Intelligence

**Versión:** v1.0.0 Release Candidate (RC1)  
**Estado:** Listo para piloto empresarial

---

## Qué es

Olnatura Intelligence es una plataforma de inteligencia empresarial orientada al Director General. Permite consultar el negocio en lenguaje natural, obtener análisis accionables y visualizar indicadores clave en un entorno unificado en español.

La plataforma combina datos operativos, conocimiento institucional y asistencia conversacional para responder preguntas de negocio con evidencia y contexto ejecutivo.

---

## Capacidades

| Módulo | Descripción |
|--------|-------------|
| **Enterprise AI** | Asistente principal: conversación híbrida, memoria de sesión y respuestas empresariales en lenguaje natural. |
| **Executive Insight** | Capa de análisis IA que enriquece cada respuesta con hallazgos ejecutivos. |
| **Business Copilot** | Sugerencias de próximos análisis según la consulta y el contexto. |
| **Executive Advisor** | Agenda Ejecutiva con recomendaciones priorizadas del día y actualización tras cada conversación. |
| **Executive Dashboard** | Panel ejecutivo con KPIs, agenda compacta y acceso directo al asistente. |
| **Financial Simulator** | Simulación de escenarios financieros y evaluación de decisiones. |

---

## Arquitectura

```
Usuario (navegador)
        ↓
   Frontend React + Vite
        ↓
   API FastAPI (app/)
        ↓
   Canal híbrido de conversación
        ↓
   ┌─────┴─────┬─────────────┬──────────────────┐
   Datos      Conocimiento   Análisis ejecutivo  Simulación
   empresariales institucional  (Insight, Copilot,  y decisiones
                               Advisor)
```

- **Backend:** Python 3.12+, FastAPI, PostgreSQL, Alembic.
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS.
- **IA:** proveedores configurables (Ollama local, OpenAI, Anthropic) con modo mock para desarrollo.

---

## Cómo ejecutar

### Requisitos

- Python 3.12+
- Node.js 20+
- PostgreSQL
- Ollama (opcional, para modelos locales)

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
# Editar .env con credenciales de base de datos

.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
```

API disponible en: http://localhost:8001

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Aplicación en: http://localhost:5173

El proxy de desarrollo redirige las peticiones `/api` al backend en el puerto 8001.

### Tests

```powershell
# Backend
.\.venv\Scripts\python.exe -m pytest -q

# Frontend
cd frontend
npm run test
npx tsc -b
npm run build
```

---

## Variables de entorno

### Backend (`.env`)

| Variable | Descripción |
|----------|-------------|
| `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME` | Conexión PostgreSQL |
| `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Modelo local vía Ollama |
| `LLM_PROVIDER` | Proveedor principal (`mock`, `ollama`, `openai`, `anthropic`) |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | OpenAI (si aplica) |
| `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` | Anthropic (si aplica) |
| `EXECUTIVE_INSIGHT_ENABLED` | Habilita análisis IA en respuestas |
| `BUSINESS_COPILOT_ENABLED` | Habilita sugerencias de próximos análisis |
| `EXECUTIVE_ADVISOR_ENABLED` | Habilita Agenda Ejecutiva |
| `DEBUG` | Modo depuración del backend |

### Frontend (`frontend/.env`)

| Variable | Descripción |
|----------|-------------|
| `VITE_API_BASE_URL` | URL del API (vacío en dev usa proxy a `:8001`) |
| `VITE_USE_HYBRID_CHAT` | Usar canal híbrido (`true` por defecto) |
| `VITE_DEBUG_MODE` | Muestra paneles técnicos de depuración (`false` en producción) |

---

## Roadmap

El roadmap de ingeniería queda **cerrado** con esta release candidate. Las siguientes iteraciones surgirán exclusivamente de:

- uso real durante el piloto empresarial
- métricas y datos de producción
- feedback del Director General
- necesidades operativas del negocio

No se planifican sprints de arquitectura ni de construcción de producto hasta contar con evidencia del piloto.

---

## Licencia

Uso interno — Olnatura, S.A. de C.V.
