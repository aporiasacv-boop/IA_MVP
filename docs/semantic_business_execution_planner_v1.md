# Semantic Business Execution Planner v1

## Objetivo

Interpretar preguntas empresariales en lenguaje natural y generar un **BusinessExecutionPlan** que decide qué conocimiento (EKO) y razonamiento (ERO) se requiere — **sin LLM, sin SQL, sin ejecución**.

## Arquitectura

```
Pregunta del usuario
        ↓
Semantic Parser (determinístico)
        ↓
Business Execution Planner
        ↓
BusinessExecutionPlan
        ↓
(futuro) Consumo EKO / ERO / Evidence Package
```

## Parser semántico

Identifica:

| Dimensión | Descripción |
|-----------|-------------|
| Business Verb | Acción solicitada (catálogo JSON) |
| Business Object | Entidades de negocio (cliente, proveedor, riesgo…) |
| Business Context | Dominio (ventas, compras, finanzas…) |
| Business Scope | Alcance (top, principales, todos…) |
| Business Time | Marco temporal (este mes, 2024…) |
| Business Constraints | Restricciones (sin movimientos, con riesgo…) |

## Catálogo de verbos

Editable en `app/semantic_intent/catalog/verbs.json`:

| Categoría | Verbos |
|-----------|--------|
| Informativos | mostrar, listar, obtener, consultar |
| Analíticos | analizar, comparar, describir, explicar, resumir, identificar |
| Ejecutivos | evaluar, diagnosticar, justificar, recomendar, priorizar, interpretar |
| Conversacionales | qué sabes, quién es, cómo funciona, por qué |
| Futuros (disabled) | proyectar, simular, estimar, pronosticar |

## BusinessExecutionPlan

```json
{
  "detected_verb": "evaluar",
  "detected_objects": ["entidad", "riesgo"],
  "detected_context": ["finanzas"],
  "detected_timeframe": ["este mes"],
  "required_knowledge": ["identity", "facts", "alerts"],
  "required_reasoning": ["risks", "recommendations"],
  "required_evidence": ["eko_evidence", "ero_evidence"],
  "execution_strategy": "ero_risk_assessment",
  "confidence": "0.8500"
}
```

## Estrategias de ejecución

| Estrategia | Uso |
|------------|-----|
| `eko_identity_lookup` | Consultas informativas simples |
| `eko_profile_summary` | Perfil y hechos de entidad |
| `eko_full_analysis` | Análisis comportamental |
| `ero_risk_assessment` | Evaluación de riesgos |
| `ero_recommendation_review` | Recomendaciones ejecutivas |
| `eko_ero_combined` | Preguntas ejecutivas complejas |
| `ontology_exploration` | Preguntas conversacionales |
| `capability_discovery` | Qué sabes / cómo funciona |

## API

```
GET  /api/semantic-intent/verbs
POST /api/semantic-intent/parse
POST /api/semantic-intent/plan
GET  /api/semantic-intent/statistics
```

## Extensibilidad

1. Añadir verbos en `catalog/verbs.json` (sin tocar el motor)
2. Añadir objetos de negocio en `catalog/objects.json` con secciones EKO/ERO requeridas
3. El planner combina automáticamente requisitos por categoría de verbo + objetos detectados

## Observabilidad

- `semantic_parses`, `execution_plans`, `verb_distribution`
- `average_semantic_confidence`, `planner_success_rate`, `unknown_verbs`

## UI

Ruta `/intencion-semantica` — exploración interactiva de parseo y planificación.

## Garantías

- `metadata.deterministic = true`
- `metadata.contains_sql = false`
- `metadata.contains_llm_output = false`
- No integrado con Hybrid Router (sprint futuro)
