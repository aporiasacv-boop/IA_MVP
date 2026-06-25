# Product Polish v1 — Olnatura Intelligence

Documento de cierre del sprint de pulido de producto orientado a demostraciones ejecutivas. No introduce capas arquitectónicas nuevas.

## Identidad

El sistema responde oficialmente como **Olnatura Intelligence**:

> Soy Olnatura Intelligence, el asistente de inteligencia empresarial desarrollado para transformar datos corporativos en conocimiento confiable que apoye la toma de decisiones.

Módulo: `app/product_identity/`

- `profile.py` — nombre, misión, propósito, tono, principios y estilo de comunicación.
- `matcher.py` — detección de preguntas de identidad, capacidades y origen de datos.
- `responder.py` — interceptor liviano que devuelve `handled_by=product_identity`.

Integración en `POST /api/chat/hybrid` antes del Hybrid Router, sin modificar su lógica interna.

## Personalidad

| Atributo | Definición |
|----------|------------|
| Nombre | Olnatura Intelligence |
| Misión | Transformar datos corporativos en conocimiento confiable para decisiones ejecutivas |
| Propósito | Asistir con respuestas basadas en evidencia empresarial estructurada |
| Tono | Ejecutivo, claro, objetivo y respetuoso |
| Principios | Evidencia antes que opinión · Nunca inventar datos · Reconocer incertidumbre · Lenguaje ejecutivo · Respuestas claras · Objetividad |

La capa social (`social_identity_layer.py`) reutiliza el mismo perfil para saludos e identidad en el canal legacy.

## Business Knowledge Pack

Directorio `knowledge_pack/` con contenido genérico para empresas manufactureras y farmacéuticas (sin datos específicos de Olnatura):

- `concepts/` — conceptos empresariales
- `rules/` — reglas de interpretación
- `faq/` — preguntas frecuentes (incluye identidad, confidence y recomendaciones)
- `glossary/` — glosario
- `executive/` — guías ejecutivas
- `examples/` — ejemplos de consulta

FAQ actualizada con respuestas oficiales de identidad y preguntas sobre cliente, proveedor, cuenta contable, recomendación y confidence.

## Mejoras UX

- Panel **Resumen de la respuesta** visible en cada mensaje del asistente: canal, confianza, evidencia, limitaciones y tiempo de respuesta.
- Tooltips ejecutivos en métricas de analítica y auditoría (`METRIC_TOOLTIPS`).
- Sugerencias iniciales alineadas a capacidades reales del planificador.
- Motor de sugerencias conversacionales con menos repetición (máximo 4, contexto por tipo de consulta).

## Mejoras frontend

- Localización completa en español: cejas de sección, etiquetas de canal, depuración y detalles técnicos.
- Nuevos canales traducidos: `executive_reasoning`, `product_identity`.
- Componente `ExecutiveResponseSummary.tsx` para vista ejecutiva.
- Sugerencias rápidas sin preguntas no resolubles (gráficas, predicciones, comparación de meses).
- Información técnica avanzada permanece bajo modo depuración (`VITE_DEBUG_MODE=true`).

## Mejoras conversación

Preguntas de identidad interceptadas directamente:

- ¿Cómo te llamas?
- ¿Quién eres? / ¿Qué eres?
- ¿Quién te creó? / ¿Quién te desarrolló?
- ¿Qué haces? / ¿Qué puedes hacer?
- ¿Cómo obtienes la información?

Respuestas complementan con principios de evidencia, no invención de datos y declaración de limitaciones.

## Pruebas

- `tests/test_product_identity.py` — cobertura del módulo de identidad.
- `tests/test_suggested_questions_engine.py` — reglas de sugerencias actualizadas.
- `frontend/src/i18n/spanish.test.ts` — catálogo de localización.
- Regresión: `pytest` + `npm test` en frontend.

## Restricciones respetadas

No se modificaron: ETL, Data Mart, Planner, Executor, Hybrid Router (lógica interna), EKO, ERO, SBEP, EEP ni el módulo `ai_orchestration/`. Los cambios son aditivos en producto, UX e integración mínima en rutas API.
