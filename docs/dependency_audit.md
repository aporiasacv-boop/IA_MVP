# Dependency Audit — Asistente de Inteligencia Empresarial Olnatura

**Fecha:** 2026-06-23  
**Alcance:** Backend (`requirements.txt`) y Frontend (`package.json`)  
**Modo:** Solo lectura — sin cambios en código ni dependencias.

---

## Resumen ejecutivo

| Área | Dependencias declaradas | Sin uso en código de aplicación | Mal segmentadas |
|------|-------------------------|----------------------------------|-----------------|
| Backend | 11 | 3 (`pandas`, `openpyxl`, `pytest`) | `pytest` en prod |
| Frontend | 22 (3 prod + 19 dev) | 0 confirmadas | — |

No existe `pyproject.toml` en la raíz del proyecto; la fuente de verdad backend es `requirements.txt`.

---

## Backend — `requirements.txt`

| Paquete | Versión mínima | Uso en `app/` | Uso fuera de `app/` | Evidencia |
|---------|----------------|---------------|---------------------|-----------|
| `fastapi` | 0.115.0 | **Sí** | — | Routers, `deps.py`, `upload_service.py` |
| `uvicorn` | 0.32.0 | No (runtime) | Arranque del servidor | CLI / despliegue |
| `sqlalchemy` | 2.0.36 | **Sí** | `alembic/` | Modelos, repos, observability |
| `alembic` | 1.14.0 | No | `alembic/` | Migraciones |
| `psycopg2-binary` | 2.9.10 | Indirecto | — | DSN en `app/core/settings.py` |
| `pydantic-settings` | 2.6.0 | **Sí** | — | `app/core/settings.py` |
| `pandas` | 2.2.0 | **No** | `scripts/import_excel.py`, `scripts/explore_excel.py` | 0 imports en `app/` |
| `openpyxl` | 3.1.5 | **No** | Scripts Excel | Implícito en importación |
| `python-multipart` | 0.0.17 | Implícito | — | `UploadFile` en `upload.py` |
| `pytest` | 8.3.0 | **No** | `tests/` | Debería estar en `requirements-dev.txt` |
| `httpx` | 0.28.0 | **Sí** | Tests, scripts | `app/services/ollama_client.py` |

### Dependencias transitivas relevantes (no pinneadas)

| Paquete | Uso |
|---------|-----|
| `pydantic` | ~30 schemas en `app/schemas/` |
| `starlette` | Vía FastAPI (TestClient en tests) |

### Imports Python no utilizados (muestra estática)

La detección automática de imports no usados no se ejecutó con herramienta dedicada (`ruff`, `vulture`). Hallazgos manuales de alto valor:

| Módulo | Observación |
|--------|-------------|
| `app/services/executive_summary_service.py` | Solo consumido por `scripts/build_executive_summaries.py`, no por runtime FastAPI |
| Subpaquetes `v2/` | Activos en runtime; no son dependencias externas sino duplicación interna |

### Librerías duplicadas / solapamiento funcional

| Duplicación | Descripción |
|-------------|-------------|
| Dos `DeterministicResponseEngine` | `app/services/deterministic_response_engine.py` (legacy) vs `app/response_engine/deterministic_response_engine.py` (pipeline nuevo) |
| Dos familias analytics API | `/api/kpis*` (datamart) vs `/api/analytics/*` (observabilidad híbrida) |
| Dos endpoints chat | `POST /api/chat` vs `POST /api/chat/hybrid` |
| Dos sistemas de intent | `IntentRouter` (regex) vs `SemanticIntentBuilder` (operation/entity resolver) |

---

## Frontend — `package.json`

### Dependencies (producción)

| Paquete | Versión | Uso verificado |
|---------|---------|----------------|
| `react` | ^19.2.6 | Todos los componentes y hooks |
| `react-dom` | ^19.2.6 | `main.tsx` |
| `react-router-dom` | ^7.18.0 | `App.tsx`, `Sidebar`, tests |

### DevDependencies

| Paquete | Uso verificado |
|---------|----------------|
| `vite`, `@vitejs/plugin-react` | Build y dev server |
| `@tailwindcss/vite`, `tailwindcss` | Estilos (`index.css`) |
| `typescript`, `@types/*` | Compilación |
| `vitest`, `@vitest/coverage-v8`, `jsdom` | Tests (`vite.config.ts`) |
| `@testing-library/*` | Tests de componentes |
| `eslint`, `typescript-eslint`, plugins React | `eslint.config.js` |

**Resultado:** Todas las dependencias npm declaradas tienen referencia identificable en código o configuración.

### Paquetes instalados pero no referenciados en `src/`

| Artefacto | Estado |
|-----------|--------|
| `src/assets/vite.svg` | Asset sin referencia en `src/` |
| `public/icons.svg` | Sin referencia en componentes |

---

## Recomendaciones (solo documentación — no aplicadas)

1. Separar `requirements.txt` en `requirements.txt` + `requirements-dev.txt` (`pytest`, opcionalmente herramientas de scripts).
2. Mover `pandas`/`openpyxl` a dependencias de scripts o grupo opcional `excel`.
3. Ejecutar `ruff check --select F401` en CI para imports no usados.
4. Documentar explícitamente que `pydantic` es dependencia transitiva requerida.

---

## Métricas

| Métrica | Valor |
|---------|-------|
| Paquetes backend declarados | 11 |
| Paquetes backend sin uso en `app/` | 3 |
| Paquetes frontend declarados | 22 |
| Paquetes frontend sin uso | 0 |
| Duplicaciones arquitectónicas detectadas | 4 |
