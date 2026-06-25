# Olnatura Intelligence — Plataforma de Inteligencia Empresarial

**Versión:** Release Candidate 1 (RC1)  
**Estado:** Listo para pruebas funcionales con usuarios

---

## Descripción

Olnatura Intelligence es una plataforma de asistencia empresarial que combina:

- **Canal híbrido determinístico + IA** — Business Pipeline, conocimiento institucional, memoria conversacional y razonamiento ejecutivo
- **Capa de datos empresariales** — entidades, ontología, perfiles canónicos
- **Observabilidad y FinOps** — costos reales por consulta, ahorro por canal
- **Simulación y decisiones ejecutivas** — escenarios, recomendaciones con evidencia

---

## Arquitectura (resumen)

```
Usuario → Frontend React (español)
              ↓
         FastAPI (app/main.py)
              ↓
    ┌─────────┴─────────┐
    │   Hybrid Chat     │ ← canal principal
    └─────────┬─────────┘
              ↓
 Pipeline │ Knowledge │ Memory │ Reasoning │ Legacy
              ↓
    Operational Metrics / FinOps
              ↓
    Simulation Engine → Enterprise Decision Engine
```

Documentación detallada: [`docs/architecture_rc1.md`](docs/architecture_rc1.md)

---

## Inicio rápido

### Requisitos

- Python 3.12+
- Node.js 20+
- PostgreSQL (puerto 5432/5433 según `.env`)
- Ollama (opcional, para LLM local)

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
copy .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Abrir: http://localhost:5173

### Tests

```powershell
python -m pytest -q
```

**Última ejecución RC1:** 740 tests passed · cobertura backend ~87%

---

## Estructura del proyecto

```
IA_MVP/
├── app/                    # Backend FastAPI
│   ├── api/routes/         # Routers HTTP
│   ├── services/           # Chat híbrido, NLP, generación
│   ├── enterprise_knowledge_service/  # EKS (conocimiento canónico)
│   ├── operational_metrics/           # FinOps canónico
│   ├── simulation_engine/
│   ├── enterprise_decision/
│   └── ...
├── frontend/               # React + Vite + Tailwind
├── tests/                  # Pytest
├── docs/                   # Documentación técnica
├── alembic/                # Migraciones BD
└── scripts/                # ETL y utilidades
```

---

## APIs principales

| Dominio | Prefijo | Documentación |
|---------|---------|---------------|
| Chat híbrido | `POST /api/chat/hybrid` | `docs/hybrid_chat_router_v1.md` |
| FinOps | `/api/finops/*` | `docs/operational_metrics_finops_v2.md` |
| Conocimiento | `/api/enterprise-knowledge/*` | `docs/enterprise_knowledge_service_v1.md` |
| Simulación | `/api/simulation/*` | `docs/simulation_decision_engine_v1.md` |
| Decisiones | `/api/decision/*` | `docs/enterprise_decision_engine_v1.md` |
| Métricas | `/api/metrics/*` | `docs/observability_v1.md` |

Catálogo completo: [`docs/api_catalog_rc1.md`](docs/api_catalog_rc1.md)

---

## Frontend — pantallas activas

| Ruta | Pantalla |
|------|----------|
| `/` | Asistente IA |
| `/rendimiento` | Rendimiento |
| `/analytics` | Analítica Empresarial |
| `/audit` | Auditoría Operacional |
| `/entidades` | Entidades Empresariales |
| `/canonicas` | Identidad Canónica |
| `/perfiles` | Perfiles de Comportamiento |
| `/ontologia` | Ontología Empresarial |
| `/conocimiento` | Servicio de Conocimiento |
| `/objetos-conocimiento` | Objetos EKO |
| `/razonamiento` | Razonamiento Empresarial |
| `/intencion-semantica` | Intención Semántica |
| `/evidencia` | Paquete de Evidencia |
| `/simulador` | Simulador |
| `/centro-decisiones` | Centro de Decisiones |
| `/finops` | FinOps |

---

## Release Candidate 1

Ver [`docs/release_candidate_1.md`](docs/release_candidate_1.md) para arquitectura final, checklists, riesgos y limitaciones.

---

## Roadmap post-RC1

1. Pruebas funcionales con usuarios piloto
2. Autenticación y autorización (RBAC)
3. Deprecación progresiva de APIs legacy (`/api/chat`, `/api/kpis`, `/api/ai-costs`)
4. Persistencia de métricas in-memory en BD
5. Consolidación de motores `DeterministicResponseEngine` duplicados
6. CORS y hardening de seguridad para producción

---

## Licencia y propiedad

Uso interno Olnatura, S.A. de C.V.
