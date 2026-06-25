# Auditoría de Seguridad — RC1

**Alcance:** Revisión documental sin implementar autenticación  
**Fecha:** 2026-06-23

---

## 1. Credenciales de ejemplo

| Ubicación | Hallazgo | Riesgo |
|-----------|----------|--------|
| `.env.example` | `DATABASE_PASSWORD=Olnatura.25` | **Medio** — password real de ejemplo |
| `app/core/settings.py` | Defaults `ia_mvp`/`ia_mvp` para BD local | Bajo (dev) |
| `settings.py` | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` vacíos por defecto | OK |

**Recomendación:** Rotar password en cualquier despliegue. Usar placeholders en `.env.example` (`changeme`).

---

## 2. Variables de entorno

| Variable | Sensibilidad | Expuesta en frontend |
|----------|--------------|---------------------|
| `DATABASE_*` | Alta | No |
| `OPENAI_API_KEY` | Alta | No |
| `ANTHROPIC_API_KEY` | Alta | No |
| `VITE_API_BASE_URL` | Baja | Sí (solo URL) |

No se detectaron API keys en código fuente ni en frontend.

---

## 3. CORS

**Hallazgo:** No hay `CORSMiddleware` configurado en `app/main.py`.

| Entorno | Impacto |
|---------|---------|
| Desarrollo (Vite proxy) | Sin impacto — proxy same-origin |
| Producción (dominios distintos) | **Bloqueo o comportamiento browser-dependent** |

**Recomendación pre-producción:** Configurar CORS con lista blanca de orígenes.

---

## 4. Logs y PII

| Fuente | Riesgo PII |
|--------|------------|
| `hybrid_chat` | Mensajes de usuario en `performance_metrics` / operational records |
| Chat session debug panel | Session IDs en frontend (solo dev) |
| Logs uvicorn | Posible exposición de query strings |

**Recomendación:** Política de retención; enmascarar mensajes en logs de producción.

---

## 5. Tokens LLM

| Aspecto | Estado |
|---------|--------|
| Keys en servidor | Solo vía env vars |
| Keys en respuestas API | No expuestas |
| Tokens de usuario en respuestas | Metadatos de conteo sí; contenido no |

---

## 6. Uploads

| Endpoint | `POST /upload` |
|----------|----------------|
| Autenticación | Ninguna |
| Validación tipo archivo | Básica (upload service) |
| Tamaño máximo | Revisar en `upload_service.py` |

**Riesgo:** Upload abierto en red pública. Restringir en reverse proxy o deshabilitar en producción si no se usa.

---

## 7. Resumen de riesgos

| # | Riesgo | Severidad | Bloquea producción |
|---|--------|-----------|-------------------|
| 1 | Sin autenticación en API | **Alta** | Sí |
| 2 | Sin CORS configurado | Media | Parcial |
| 3 | Password en `.env.example` | Media | No (si se rota) |
| 4 | PII en métricas BD | Media | Parcial (compliance) |
| 5 | Upload sin auth | Media | Parcial |
| 6 | Sin rate limiting | Media | Parcial |
| 7 | Sin TLS en app (delegar a proxy) | Baja | No (si hay proxy) |

---

## 8. Aceptable para piloto interno

Con las siguientes condiciones:

- Red corporativa / VPN
- Cohortes pequeñas (< 20 usuarios)
- Sin datos personales reales de clientes externos
- Rotación de credenciales de BD
- Reverse proxy con TLS

**No aceptable para internet público sin mitigaciones de la sección 7.**
