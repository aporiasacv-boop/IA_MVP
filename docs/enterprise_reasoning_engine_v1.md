# Enterprise Reasoning Engine v1

## Objetivo

Motor de razonamiento empresarial determinístico y explicable (XAI) que produce conclusiones verificables a partir del **Enterprise Knowledge Object (EKO)** — sin LLM, sin SQL, sin narrativa.

## Arquitectura

```
Enterprise Knowledge Object (EKO)
        ↓
Rule Packs (JSON configurables)
        ↓
Rule Evaluator (condiciones genéricas)
        ↓
Reasoning Builder
        ↓
Enterprise Reasoning Object (ERO) → PostgreSQL JSONB
```

## Flujo de construcción

1. `ReasoningBuildEngine` lee todos los EKO persistidos.
2. `load_enabled_rules()` carga reglas desde `app/enterprise_reasoning/rules/*.json`.
3. Para cada regla habilitada, `evaluate_rule()` evalúa condiciones contra el contexto EKO.
4. Las conclusiones se agrupan en `findings`, `signals`, `alerts`, `risks`, `opportunities`, `recommendations`.
5. Se filtran reglas incompatibles (`incompatible_with`).
6. Se persiste el ERO con métricas denormalizadas.

## Contrato ERO v1

| Sección | Contenido |
|---------|-----------|
| `findings` | Hallazgos verificables (ej. rol clasificado) |
| `signals` | Señales de comportamiento derivadas |
| `alerts` | Alertas que requieren atención |
| `risks` | Riesgos empresariales detectados |
| `opportunities` | Oportunidades comerciales |
| `recommendations` | Acciones recomendadas (estructuradas) |
| `evidence` | Índice de reglas disparadas |
| `confidence` | Agregado de confianza y contadores |
| `metadata` | Versión, flags determinísticos |

### ReasoningConclusion (elemento atómico)

- `key` — identificador de la conclusión
- `value` — dato estructurado (nunca narrativa)
- `rule_code` — regla que produjo la conclusión
- `evidence` — evidencia del EKO utilizada
- `confidence` — 0.0 a 1.0
- `severity` — low | medium | high | critical
- `computed_at` — timestamp de cálculo

## Ciclo de vida de una conclusión

```
EKO actualizado → Build ERO → Regla evaluada → Conclusión generada
→ Evidencia adjunta → Persistencia → API / UI → Health check
```

Re-ejecutar `scripts/build_enterprise_reasoning.py` recalcula todas las conclusiones de forma idempotente.

## Cómo añadir nuevas reglas

1. Crear o editar un archivo JSON en `app/enterprise_reasoning/rules/`.
2. Definir el pack y las reglas con el esquema:

```json
{
  "pack_id": "mi_pack",
  "version": "1.0.0",
  "rules": [
    {
      "rule_code": "mi_regla",
      "conclusion_type": "risk",
      "key": "clave_conclusion",
      "value": {"tipo": "estructurado"},
      "conditions": {"eko_alert_present": "missing_profile"},
      "severity": "high",
      "confidence": "0.9000",
      "enabled": true,
      "description": "Descripción de la regla"
    }
  ]
}
```

3. Operadores de condición disponibles:
   - `eko_alert_present`, `eko_signal_present`, `eko_alert_any`, `eko_signal_any`
   - `eko_fact_min`, `eko_fact_max`, `eko_fact_equals`
   - `eko_quality_min_completeness`, `eko_quality_has_profile`, `eko_quality_has_ontology`
   - `eko_roles_include`, `eko_nature_include`, `eko_roles_count_min`, `eko_relationships_min`
   - `all_of`, `any_of`, `not`

4. Ejecutar build: `python scripts/build_enterprise_reasoning.py`
5. Consultar reglas: `GET /api/reasoning/rules`

**No es necesario modificar el motor** — solo añadir archivos JSON.

## API

```
GET /api/reasoning/entities
GET /api/reasoning/entities/{canonical_id}
GET /api/reasoning/statistics
GET /api/reasoning/rules
```

## Observabilidad

- `reasoning_objects_total`
- `reasoning_rules_executed`
- `average_reasoning_confidence`
- `average_findings`
- `average_alerts`
- `average_recommendations`
- `last_reasoning_refresh`

## Health checks

- Razonamientos sin evidencia
- Confidence fuera de rango
- Hallazgos duplicados
- Reglas contradictorias (mismo key en risk y opportunity)
- Recomendaciones incompatibles (rule_code duplicado)
- ERO incompletos (informativo)

## UI

Ruta `/razonamiento` — exploración de hallazgos, riesgos, oportunidades y evidencia.

## Garantías

- `metadata.deterministic = true`
- `metadata.contains_sql = false`
- `metadata.contains_llm_output = false`
