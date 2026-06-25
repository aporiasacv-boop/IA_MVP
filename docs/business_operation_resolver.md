# Business Operation Resolver

## Objetivo

Primera pieza del futuro **Semantic Router Empresarial** del Asistente de Inteligencia Empresarial Olnatura.

Detecta de forma **100% determinística** qué operación analítica subyace en una pregunta empresarial (`COUNT`, `SUM`, `AVG`, `MAX`, `MIN`, `TOP`, `TREND`, `COMPARE`, `LOOKUP`) sin utilizar Ollama, LLMs, embeddings ni bases vectoriales.

Este sprint es **aditivo**: no modifica el Intent Router, el chat ni la Executive Summary Layer.

## Arquitectura

```
Pregunta (texto)
      │
      ▼
OperationResolver
      │
      ├─ Normalización (minúsculas, acentos, espacios)
      ├─ Catálogo OPERATION_SYNONYMS (domain)
      └─ Scoring determinístico
      │
      ▼
OperationResolution
  • operation
  • confidence
  • matched_terms
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Dominio | `app/domain/operations.py` | Enum `BusinessOperation` |
| Dominio | `app/domain/operation_catalog.py` | Sinónimos por operación |
| Servicio | `app/services/operation_resolver.py` | Resolución determinística |
| Schema | `app/schemas/operation.py` | Contrato `OperationResolution` |
| API | `app/api/routes/semantic.py` | Endpoint de prueba |

## Flujo de resolución

1. Normalizar la pregunta (mismo criterio que otras capas NLP del proyecto).
2. Recorrer el catálogo de sinónimos ordenado por longitud descendente.
3. Registrar coincidencias por operación evitando solapamientos de texto.
4. Calcular:

```
confidence = coincidencias_operacion_ganadora / coincidencias_totales
```

5. Devolver la operación con mayor número de coincidencias.

Si no hay coincidencias:

```json
{
  "operation": null,
  "confidence": 0.0,
  "matched_terms": []
}
```

## Endpoint de prueba

```
GET /api/semantic/operation?question=¿Cuántos clientes existen?
```

Respuesta ejemplo:

```json
{
  "operation": "COUNT",
  "confidence": 1.0,
  "matched_terms": ["cuántos", "existen"]
}
```

## Ejemplos

| Pregunta | Operación |
|----------|-----------|
| ¿Cuántos clientes existen? | `COUNT` |
| ¿Qué proveedor tuvo mayor movimiento? | `MAX` |
| Muéstrame los principales clientes | `TOP` |
| ¿Cuál es el volumen total? | `SUM` |
| ¿Cuál es el promedio mensual? | `AVG` |

## Limitaciones actuales

- No identifica entidades de negocio (cliente, proveedor, mes); eso corresponde a capas posteriores del Semantic Router.
- No resuelve ambigüedad semántica profunda; depende del catálogo de sinónimos.
- Términos compartidos entre operaciones (p. ej. `total`) pueden repartir coincidencias; se priorizan frases más largas (`volumen total` → `SUM`).
- No ejecuta consultas SQL ni accede a PostgreSQL; solo clasifica la operación.
- Cobertura limitada a las operaciones del catálogo inicial del MVP.

## Próximos pasos sugeridos

1. Combinar `OperationResolver` + entidades + Intent Router en un pipeline unificado.
2. Enriquecer catálogo con sinónimos empresariales reales del dominio Olnatura.
3. Agregar reglas de desempate por contexto (`TOP` vs `MAX` en rankings).
4. Persistir telemetría de resolución para medir cobertura en producción.

## Pruebas

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_operation_resolver.py -v
```

Cobertura mínima del sprint: **5 casos obligatorios** + endpoint + caso sin coincidencias.
