# Business Entity Resolver

## Objetivo

Segunda pieza del futuro **Semantic Router Empresarial** del Asistente de Inteligencia Empresarial Olnatura.

Detecta de forma **100% determinística** qué entidades de negocio aparecen en una pregunta empresarial (`CLIENTE`, `PROVEEDOR`, `CUENTA`, `TRANSACCION`, `MOVIMIENTO`, `MES`, `ANIO`) y extrae parámetros asociados (`mes`, `anio`, `codigo`) sin utilizar Ollama, LLMs, embeddings ni bases vectoriales.

Este sprint es **aditivo**: no modifica el Intent Router, el Operation Resolver, el chat ni la Executive Summary Layer.

## Arquitectura

```
Pregunta (texto)
      │
      ▼
EntityResolver
      │
      ├─ Normalización (app/utils/text_normalizer.py)
      ├─ Catálogo ENTITY_SYNONYMS (domain)
      ├─ Extracción de parámetros (mes, anio, codigo)
      └─ Scoring determinístico
      │
      ▼
EntityResolution
  • entities
  • parameters
  • confidence
  • matched_terms
```

### Componentes

| Capa | Archivo | Responsabilidad |
|------|---------|-----------------|
| Dominio | `app/domain/entities.py` | Enum `BusinessEntity` |
| Dominio | `app/domain/entity_catalog.py` | Sinónimos por entidad |
| Utilidad | `app/utils/text_normalizer.py` | Normalización reutilizable |
| Servicio | `app/services/entity_resolver.py` | Resolución determinística |
| Schema | `app/schemas/entity.py` | Contrato `EntityResolution` |
| API | `app/api/routes/semantic.py` | Endpoint de prueba |

## Flujo de resolución

1. Normalizar la pregunta (minúsculas, acentos, espacios duplicados).
2. Recorrer el catálogo de sinónimos ordenado por longitud descendente.
3. Registrar coincidencias por entidad evitando solapamientos de texto.
4. Extraer parámetros del texto original:
   - **Mes**: nombres de mes (`junio` → `{"mes": "junio"}`).
   - **Año**: años de cuatro dígitos (`2025` → `{"anio": 2025}`).
   - **Código**: patrones `C\d+`, `P\d+` o alfanumérico mixto de longitud ≥ 5 con letras y dígitos.
5. Construir la lista final de entidades:
   - Los nombres de mes se registran como parámetro `mes` pero no agregan la entidad `MES`.
   - Los años numéricos agregan la entidad `ANIO` además del parámetro `anio`.
6. Calcular:

```
confidence = entidades_en_resultado / entidades_posibles_detectadas
```

Donde `entidades_posibles_detectadas` incluye todas las entidades con al menos una coincidencia en el catálogo, más `ANIO` si se detectó un año numérico.

Si no hay coincidencias:

```json
{
  "entities": [],
  "parameters": {},
  "confidence": 0.0,
  "matched_terms": []
}
```

## Endpoint de prueba

```
GET /api/semantic/entity?question=¿De qué cliente es la cuenta IMA0709183?
```

Respuesta ejemplo:

```json
{
  "entities": ["CLIENTE", "CUENTA"],
  "parameters": {
    "codigo": "IMA0709183"
  },
  "confidence": 1.0,
  "matched_terms": ["cliente", "cuenta"]
}
```

## Ejemplos

| Pregunta | Entidades | Parámetros |
|----------|-----------|------------|
| ¿Cuántos clientes existen? | `CLIENTE` | — |
| ¿Qué proveedor tuvo más movimiento en junio? | `PROVEEDOR`, `MOVIMIENTO` | `mes=junio` |
| ¿De qué cliente es la cuenta IMA0709183? | `CLIENTE`, `CUENTA` | `codigo=IMA0709183` |
| ¿Cuál fue la transacción más alta del cliente C001? | `TRANSACCION`, `CLIENTE` | `codigo=C001` |
| ¿Cuál fue la actividad de proveedores en 2025? | `PROVEEDOR`, `ANIO` | `anio=2025` |

## Limitaciones actuales

- No identifica la operación analítica (`COUNT`, `SUM`, etc.); eso corresponde al Operation Resolver.
- No resuelve ambigüedad semántica profunda; depende del catálogo de sinónimos.
- Términos compartidos entre entidades pueden generar coincidencias múltiples; se priorizan frases más largas (`movimiento individual` → `TRANSACCION` antes que `movimiento` → `MOVIMIENTO`).
- El sinónimo `actividad` está en el catálogo de `MOVIMIENTO` pero no etiqueta esa entidad por sí solo; se requiere `movimiento` o `movimientos` para incluirla en el resultado.
- Los códigos alfanuméricos requieren al menos una letra y un dígito para evitar falsos positivos con palabras comunes.
- No ejecuta consultas SQL ni accede a PostgreSQL; solo clasifica entidades y parámetros.
- No está integrado aún con el Query Engine ni con el Semantic Router unificado.

## Evolución futura

1. Combinar `EntityResolver` + `OperationResolver` + Intent Router en un **Semantic Router** unificado.
2. Conectar con **Business Query Engine** para traducir entidades y parámetros a consultas estructuradas.
3. Agregar **Context Resolver** para desambiguar referencias pronominales y filtros implícitos.
4. Enriquecer el catálogo con sinónimos empresariales reales del dominio Olnatura.
5. Persistir telemetría de resolución para medir cobertura en producción.

## Pruebas

```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\python.exe -m pytest tests/test_entity_resolver.py -v
```

Cobertura mínima del sprint: **5 casos obligatorios** + endpoint + caso sin coincidencias.
