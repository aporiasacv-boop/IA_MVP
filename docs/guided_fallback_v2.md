# Guided Fallback v2

Fallback contextual determinístico que **reconoce el dominio empresarial** mencionado en la consulta, aunque el pipeline no pueda ejecutarla.

## Problema (v1)

Consultas como *¿Cómo van las ventas?* recibían una respuesta genérica (*"Actualmente puedo ayudarte con..."*) sin reflejar que el sistema detectó palabras clave del dominio.

## Objetivo UX

Que el usuario perciba **comprensión parcial** del tema, sin inventar datos ni respuestas de negocio.

> La meta **no** es responder la consulta. Es comunicar claramente qué dominio se detectó y qué sí está disponible hoy.

## Fallback contextual

Cuando:

1. La consulta termina en `guided_fallback`
2. Se detecta un dominio en `DOMAIN_HINTS`
3. El tipo de fallback **no** es `OUT_OF_DOMAIN`

Se responde:

```
Detecté una consulta relacionada con ventas.

Actualmente no dispongo de información de ventas.

Puedo ayudarte con información sobre:

• Clientes
• Proveedores
• KPIs
• Actividad mensual
```

Si **no** hay dominio detectado → se mantiene el comportamiento v1.

## Dominios detectados

| Dominio | Palabras clave (ejemplos) |
|---------|---------------------------|
| VENTAS | ventas, venta, vender |
| COMPRAS | compras, compra, compradores |
| INVENTARIO | inventario, existencias, stock |
| FACTURACION | factura, facturación, facturacion |
| FINANZAS | finanzas, financiero, financiera |
| LOGISTICA | logística, envíos, distribución |
| PRODUCCION | producción, manufactura, fabricación |

Detección 100% determinística vía `normalize_for_matching` + coincidencia por término (prioridad por longitud).

## Reglas de visualización

- Máximo **4** capacidades visibles (sin catálogo completo)
- Sin *¿Qué puedes hacer?*
- Sin terminología técnica (query types, dataset, rankings)
- Sin datos inventados

## Módulo

```
app/guided_fallback/v2/
  domains.py    → DOMAIN_HINTS, BusinessDomain
  detector.py   → detect_domain()
  formatter.py  → build_domain_contextual_answer()
  metrics.py    → observabilidad in-process
```

Integración en `app/guided_fallback/engine.py` sin modificar planner, executor, memory ni capability discovery.

## Observabilidad

| Métrica | Descripción |
|---------|-------------|
| `domain_detected` | Último dominio detectado en fallback contextual |
| `domain_fallback_hits` | Fallbacks con respuesta contextual v2 |
| `domain_fallback_misses` | Fallbacks sin dominio detectado |
| `top_domains` | Ranking de dominios por frecuencia |

Expuesto en:

- Metadata de `POST /api/chat/hybrid`
- `GET /api/metrics/summary`
- `GET /api/audit/report`

## Limitaciones

- No agrega dominios de datos reales al pipeline
- No crea query types ni respuestas inventadas
- No usa LLM ni embeddings
- `OUT_OF_DOMAIN` conserva respuesta v1 aunque haya palabras clave
- Dominios `LOGISTICA` y `PRODUCCION` están catalogados pero sin datos empresariales aún

## Pruebas

```bash
pytest tests/test_guided_fallback_v2.py \
  tests/integration/test_guided_fallback_v2_integration.py -q
```

## Ejemplos

| Consulta | Dominio | Respuesta |
|----------|---------|-----------|
| ¿Cómo van las ventas? | VENTAS | ... relacionada con ventas |
| ¿Cómo está el inventario? | INVENTARIO | ... relacionada con inventario |
| ¿Cómo van las compras? | COMPRAS | ... relacionada con compras |
| ¿Qué información financiera tienes? | FINANZAS | ... relacionada con finanzas |
| ¿Cómo va el negocio? | — | Fallback v1 (ambiguo) |
