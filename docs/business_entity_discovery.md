# Business Entity Discovery — Diario General Olnatura

**Fecha de análisis:** 2026-06-23  
**Alcance:** Exploración de solo lectura sobre PostgreSQL (`ia_mvp`)  
**Restricciones respetadas:** Sin `UPDATE`, `DELETE`, migraciones, cambios de ETL ni de código de aplicación.

---

## 1. Resumen ejecutivo

El Data Mart de Olnatura **no es un maestro de clientes/proveedores**. Es un **Diario General (GL)** exportado desde **Microsoft Dynamics 365 Finance & Operations**, cargado desde Excel a la tabla `movimientos_diario` (386.480 líneas, ejercicio 2025 completo).

### Hallazgo principal

La hipótesis del equipo es **correcta y está respaldada por los datos**:

| Evidencia | Detalle |
|-----------|---------|
| Código `20401001` en dimensión proveedor | Aparece como `cuenta_proveedor` con nombre `20401001 NOMINA POR PAGAR` |
| Movimientos | 15.639 líneas, ~370 M MXN (volumen absoluto) |
| Naturaleza contable | La misma cuenta existe en `account_display_value` como `PASIVO NOMINA POR PAGAR` |
| Códigos proveedor numéricos | Solo **3 de 938** códigos distintos en `cuenta_proveedor` inician con dígito; el resto son alfanuméricos tipo RFC/cuenta de mayor |

**Conclusión:** Las columnas `cuenta_proveedor` / `nombre_proveedor` y `cuenta_cliente` / `nombre_cliente` en D365 **no representan exclusivamente contrapartes comerciales**. Son **dimensiones financieras del asiento** que el ERP rellena según el `tipo_registro` (p. ej. *Saldo del proveedor*, *Saldo del cliente*, *Diario contable*, *Banco*, *Impuesto sobre las ventas*).

### Magnitud del universo

| Rol en el modelo actual | Entidades distintas (códigos) | Observación |
|-------------------------|-------------------------------|-------------|
| Cuenta contable (`account_display_value`) | 1.962 | Eje real del diario |
| Nombre de cuenta (`nombre_cuenta`) | 425 | Muchos códigos comparten etiqueta genérica (p. ej. *PRODUCCION EN PROCESO*) |
| “Proveedor” (`cuenta_proveedor`) | 938 | Mezcla RFC/vendors + cuentas de pasivo mal ubicadas |
| “Cliente” (`cuenta_cliente`) | 53 | Patrón `C###`; incluye *PUBLICO EN GENERAL* (57.730 mov.) |
| Catálogo unificado explorado | 2.778 | Unión de las tres dimensiones (puede haber duplicación conceptual) |

### Implicación para IA

Antes de ampliar reglas conversacionales o LLM, el sistema necesita un **catálogo maestro de entidades** (`dim_entidad`) que distinga:

1. Cuenta del catálogo contable  
2. Cliente comercial (maestro AR)  
3. Proveedor comercial (maestro AP)  
4. Banco / caja  
5. Pasivos laborales y fiscales  
6. Conceptos puente / genéricos  

El archivo [`entity_catalog_candidate.csv`](entity_catalog_candidate.csv) contiene **2.778 entidades** con clasificación preliminar para revisión manual.

---

## 2. Fase 1 — Inventario del modelo

### 2.1 Tabla origen (fuente de verdad operativa)

| Tabla | Filas | Origen | Descripción |
|-------|------:|--------|-------------|
| `movimientos_diario` | 386.480 | Excel → ETL de carga | Líneas del diario general D365 |

**Periodo cubierto:** 2025-01-01 a 2025-12-31 (12 meses).  
**Capa de registro:** única valor `Actual` (386.480 movimientos).  
**Hojas Excel de origen:** 12 (`ENERO` … `DICIEMBRE`; mayor volumen en `JUNIO`: 37.482 líneas).

### 2.2 Tablas de hechos (agregadas desde `movimientos_diario`)

| Tabla | Filas | Origen | Granularidad |
|-------|------:|--------|--------------|
| `fact_mes` | 12 | Script `build_datamart.py` | Año × mes |
| `fact_cuenta` | 1.962 | idem | Cuenta contable |
| `fact_cliente` | 50 | idem | Dimensión cliente D365 |
| `fact_proveedor` | 766 | idem | Dimensión proveedor D365 |
| `fact_divisa` | 3 | idem | Divisa |
| `fact_cliente_mes` | 292 | idem | Cliente × mes |
| `fact_proveedor_mes` | 3.700 | idem | Proveedor × mes |
| `fact_cuenta_mes` | 10.807 | idem | Cuenta × mes |

### 2.3 Tablas resumen ejecutivo

| Tabla | Filas | Origen |
|-------|------:|--------|
| `cliente_resumen` | 50 | `executive_summary_service` |
| `proveedor_resumen` | 766 | idem |
| `cuenta_resumen` | 1.962 | idem |
| `mes_resumen` | 12 | idem |

### 2.4 Vistas materializadas

| Vista | Origen | Uso |
|-------|--------|-----|
| `mv_resumen_mensual` | Migración Alembic 002/003 | KPIs mensuales |
| `mv_top_clientes` | idem | Rankings cliente |
| `mv_top_proveedores` | idem | Rankings proveedor |
| `mv_top_cuentas` | idem | Rankings cuenta |
| `mv_cliente_evolucion` | idem | Series temporales cliente |
| `mv_proveedor_evolucion` | idem | Series temporales proveedor |
| `mv_cuenta_evolucion` | idem | Series temporales cuenta |

### 2.5 Otras tablas

| Tabla | Filas | Origen |
|-------|------:|--------|
| `performance_metrics` | 359 | Telemetría del asistente |
| `alembic_version` | 1 | Control de migraciones |

### 2.6 Columnas de `movimientos_diario` relevantes para entidades

| Columna | Tipo semántico D365 | Distintos |
|---------|---------------------|----------:|
| `account_display_value` | Cuenta mayor (Main Account) | 1.962 |
| `nombre_cuenta` | Nombre de cuenta | 425 |
| `cuenta_proveedor` | Dimensión proveedor / acreedor | 938 |
| `nombre_proveedor` | Nombre dimensión proveedor | 766 |
| `cuenta_cliente` | Dimensión cliente | 53 |
| `nombre_cliente` | Nombre dimensión cliente | 50 |
| `tipo_registro` | Subledger posting type | 56 |
| `numero_diario` | Voucher / diario | 70.168 |
| `asiento` | Línea de asiento | 69.382 |
| `divisa` | Moneda transacción | 3 |

---

## 3. Fase 2 — Descubrimiento de entidades

### 3.1 Cobertura dimensional por movimiento

| Condición | Movimientos | % del total |
|-----------|------------:|------------:|
| Con cliente (`cuenta_cliente` + `nombre_cliente`) | 120.724 | 31,2% |
| Con proveedor (`cuenta_proveedor` + `nombre_proveedor`) | 121.554 | 31,5% |
| Sin ninguna contraparte | 140.202 | 36,3% |
| Con cliente **y** proveedor simultáneos | 181 | 0,05% |

**Interpretación:** Un tercio de las líneas son asientos puramente contables (inventario, producción, IVA, tipo de cambio) sin cliente ni proveedor en las dimensiones del export.

### 3.2 Signo y cuadre del diario

| Signo de `monto` | Líneas | Volumen absoluto acumulado |
|------------------|-------:|---------------------------:|
| Positivo | 153.966 | 15.759.270.309,91 |
| Negativo | 153.511 | 15.759.270.309,91 |
| Cero | 79.003 | 0,00 |

El balance positivo/negativo simétrico confirma naturaleza de **partida doble**. El 20,4% de líneas con monto cero corresponde principalmente a movimientos de ajuste, WIP o redondeo (`tipo_registro`).

### 3.3 Tipos de registro dominantes (actores del negocio)

| `tipo_registro` | Movimientos | Volumen abs. (MXN) |
|-----------------|------------:|-------------------:|
| Impuesto sobre las ventas | 107.144 | 401 M |
| Saldo del proveedor | 38.707 | 1.132 M |
| Diario contable | 32.202 | 1.907 M |
| Pérdida / ganancia tipo de cambio | 50.412 | ~16 M |
| Costos de producción / inventario (varios) | ~80.000+ | Miles de millones |
| Saldo del cliente | 17.387 | 943 M |
| Banco | 8.650 | 7.337 M |
| Ingresos de orden de venta | 2.933 | 389 M |
| Transferencia apertura/cierre | 2.273 | 8.401 M |

Estos tipos son la **clave semántica** que D365 usa para decidir qué dimensión poblar — no el texto de la pregunta del usuario.

---

## 4. Fase 3 — Agrupamiento automático (hipótesis por similitud)

Método: clasificación por **patrones textuales y estructurales** (prefijos, sufijos societarios, RFC, palabras clave contables). **No se aplicaron reglas de negocio de Olnatura.**

| Grupo sugerido | Entidades | Movimientos | % volumen | Justificación |
|----------------|----------:|------------:|----------:|---------------|
| `cuenta_contable` | 1.623 | 257.560 | 61,4% | Código numérico tipo catálogo + descripción de mayor |
| `banco` | 21 | 9.348 | 13,6% | Nombres de instituciones financieras |
| `empresa` | 386 | 74.241 | 9,6% | Sufijos SA DE CV, S DE RL, SC, etc. en dimensión proveedor |
| `cliente_comercial` | 48 | 62.970 | 7,2% | Código `C###` en dimensión cliente |
| `impuesto_o_gobierno` | 76 | 111.561 | 2,9% | IVA, ISR, retenciones, impuestos |
| `nomina_o_pasivo_laboral` | 248 | 24.819 | 2,3% | NOMINA, PTU, IMSS, cargas sociales |
| `contraparte_comercial` | 357 | 27.857 | 1,9% | Dimensión proveedor sin patrón contable claro |
| `persona_moral_o_fisica` | 18 | 2.672 | 0,9% | Patrón RFC en código o nombre |
| `concepto_interno_o_puente` | 1 | 57.730 | 0,1% | *PUBLICO EN GENERAL* (cliente genérico D365) |

> **Nota:** Los porcentajes de volumen se calculan sobre la suma de montos absolutos por entidad en el catálogo unificado; una misma línea del diario puede contribuir a cuenta y a dimensión simultáneamente, por lo que el total supera el 100% a nivel de línea.

---

## 5. Fase 4 — Inventario de entidades (Top 20 global)

| Entidad | Movimientos | Monto total (abs.) | Clasificación | Confianza |
|---------|------------:|-------------------:|---------------|-----------|
| PUBLICO EN GENERAL (`C0003`) | 57.730 | 47,6 M | concepto_interno_o_puente | media |
| IVA TRASLADABLE POR COBRAR (`20603001`) | 39.448 | 143,7 M | impuesto_o_gobierno | media-alta |
| IVA TRASLADABLE COBRADO (`20604001`) | 36.766 | 113,3 M | impuesto_o_gobierno | media-alta |
| PROVEEDORES NACIONALES TASA 16% (`20101001`) | 20.867 | 2.227 M | cuenta_contable | media |
| PRODUCTO TERMINADO (`10702004`) | 19.471 | 1.286 M | cuenta_contable | media |
| NUEVA WAL MART DE MEXICO (`C0027`) | 19.004 | 361,4 M | cliente_comercial | media |
| **NOMINA POR PAGAR (`20401001` en proveedor)** | **15.639** | **370,4 M** | **nomina_o_pasivo_laboral** | **alta** |
| IVA ACRED. GASTOS… (`10602001`) | 14.420 | 40,5 M | impuesto_o_gobierno | media-alta |
| PERDIDA CAMBIARIA REALIZADA (`80010002`) | 14.311 | 3,6 M | cuenta_contable | media |
| ACREEDORES DIVERSOS… (`20301101`) | 13.239 | 374,7 M | cuenta_contable | media |
| COSTCO DE MEXICO (`C0026`) | 9.421 | 698,2 M | cliente_comercial | media |
| GENOMMA LABORATORIES (`C0004`) | 5.936 | 613,9 M | cliente_comercial | media |

Inventario completo: **2.778 filas** en [`entity_catalog_candidate.csv`](entity_catalog_candidate.csv).

---

## 6. Fase 5 — Patrones detectados

### 6.1 ¿Nombres que claramente son cuentas contables?

**Sí, abundantes.** Ejemplos en `nombre_cuenta` / `account_display_value`:

- `PROVEEDORES NACIONALES TASA 16%`
- `PRODUCTO TERMINADO` / `PRODUCCION EN PROCESO` / `MATERIAS PRIMAS`
- `IVA TRASLADABLE POR COBRAR`
- `PASIVO NOMINA POR PAGAR`
- `PERDIDA CAMBIARIA REALIZADA`

1.962 códigos de cuenta con solo 425 nombres distintos → **alta reutilización de etiquetas** por subcuenta/analítica.

### 6.2 ¿Nombres que claramente son empresas?

**Sí, principalmente en dimensión proveedor** (códigos alfanuméricos tipo RFC):

- `DEREMATE COM DE MEXICO S DE RL DE CV` (`M991109KR2`)
- `SG FLEXO SA DE CV` (`25NC3290`)
- `EFECTIVALE S RL DE CV` (`EFE8908015`)

386 entidades clasificadas como `empresa` por sufijo societario.

### 6.3 ¿Patrones de RFC?

**Sí, limitados pero presentes:** 18 entidades con patrón RFC mexicano en código o nombre. La mayoría de proveedores usan códigos internos D365 de 10+ caracteres que **resembling** RFC pero no siempre válidos al 100%.

### 6.4 ¿Códigos repetidos entre roles?

| Patrón | Evidencia |
|--------|-----------|
| Mismo nombre en cuenta y proveedor | **0 coincidencias exactas** (UPPER trim) entre `nombre_proveedor` y `nombre_cuenta` |
| Misma entidad como cliente y proveedor | **2 nombres:** `GENOMMA LABORATORIES MEXICO`, `PHARMA PLUS` |
| Cuenta GL en campo proveedor | **3 códigos numéricos** en `cuenta_proveedor`; el principal es `20401001` NOMINA |

### 6.5 ¿Prefijos?

| Dimensión | Prefijo dominante | Entidades |
|-----------|-------------------|----------:|
| Cliente | `C` | 53 (100%) |
| Cuenta contable | `6` (gastos/costos) | 755 |
| Cuenta contable | `1` (activo circulante) | 282 |
| Cuenta contable | `2` (pasivo) | 221 |
| Proveedor | Letras A–Z dispersas | 935 códigos alfanuméricos |

### 6.6 ¿Cuentas internas / puentes?

- `PUBLICO EN GENERAL` (`C0003`): 57.730 movimientos — cliente genérico de facturación masiva.
- Cuentas de resultado financiero (`700xx`, `800xx`) para tipo de cambio.
- `Transferencia de transacciones de apertura y cierre`: 2.273 movimientos, 8.401 M MXN.

### 6.7 ¿Entidades en entrada y salida?

En un GL, **todas las cuentas participan en débito y crédito**. A nivel de dimensión comercial:

- Clientes aparecen en `tipo_registro = Saldo del cliente` e `Ingresos de orden de venta`.
- Proveedores en `Saldo del proveedor` y compras/gastos.
- La dimensión **no indica dirección**; el signo de `monto` sí.

---

## 7. Fase 6 — Análisis estadístico por grupo

### 7.1 Resumen agregado

| Grupo | Entidades | Movimientos | Volumen (MXN abs.) | % participación |
|-------|----------:|------------:|-------------------:|----------------:|
| cuenta_contable | 1.623 | 257.560 | 22.506 M | 61,4% |
| banco | 21 | 9.348 | 4.994 M | 13,6% |
| empresa | 386 | 74.241 | 3.501 M | 9,6% |
| cliente_comercial | 48 | 62.970 | 2.642 M | 7,2% |
| impuesto_o_gobierno | 76 | 111.561 | 1.076 M | 2,9% |
| nomina_o_pasivo_laboral | 248 | 24.819 | 851 M | 2,3% |
| contraparte_comercial | 357 | 27.857 | 640 M | 1,9% |
| persona_moral_o_fisica | 18 | 2.672 | 297 M | 0,9% |
| concepto_interno_o_puente | 1 | 57.730 | 48 M | 0,1% |

### 7.2 Caso NOMINA POR PAGAR (evidencia detallada)

La entidad `20401001` aparece **simultáneamente**:

| Campo | Valor en distintos movimientos |
|-------|-------------------------------|
| `cuenta_proveedor` / `nombre_proveedor` | `20401001` / `20401001 NOMINA POR PAGAR` |
| `account_display_value` / `nombre_cuenta` | `20401001` / `PASIVO NOMINA POR PAGAR` |
| Contrapartidas frecuentes | `80010002` pérdida cambiaria, `70001005` utilidad cambiaria, `20602001` ISR retenido nómina |

**Confianza alta:** es una **cuenta de pasivo laboral**, no un proveedor comercial.

---

## 8. Fase 7 — Clasificación sugerida (preliminar)

| Tipo propuesto | Descripción | Ejemplos | Confianza | Regla / evidencia |
|----------------|-------------|----------|-----------|-------------------|
| `GL_ACCOUNT` | Cuenta del catálogo contable | `20101001`, `10702004` | Alta | `account_display_value` numérico + nombre de mayor |
| `AR_CUSTOMER` | Cliente cuentas por cobrar | `C0026` COSTCO, `C0027` WALMART | Media | Prefijo `C` + maestro cliente D365 |
| `AP_VENDOR` | Proveedor cuentas por pagar | `M991109KR2` DEREMATE | Media-alta | Código alfanumérico + razón social en dimensión proveedor, sin patrón GL |
| `GL_MISPOSTED_AS_VENDOR` | Cuenta contable en campo proveedor | `20401001` NOMINA | Alta | Código numérico 8 dígitos en `cuenta_proveedor` |
| `BANK` | Institución financiera | Movimientos `tipo_registro = Banco` | Alta | Palabras clave + tipo de registro |
| `TAX_AUTHORITY` | Impuestos / retenciones | `20603001` IVA trasladable | Media-alta | Palabras IVA, ISR, IMPTOS |
| `PAYROLL_LIABILITY` | Pasivos de nómina | `20401001`, `20401008` PTU | Alta | NOMINA, PTU en nombre |
| `GENERIC_COUNTERPARTY` | Cliente catch-all | `C0003` PUBLICO EN GENERAL | Media | Nombre genérico + volumen masivo |
| `INTERNAL_FINANCIAL` | Resultado financiero / FX | `80010002`, `70001005` | Media | Series 7xx/8xx + tipo de cambio |

**Nunca asumir sin evidencia:** entidades `contraparte_comercial` con confianza baja-media requieren validación con catálogo maestro D365 (`CustTable`, `VendTable`, `MainAccount`).

---

## 9. Fase 8 — Mapa del negocio (solo datos)

### 9.1 ¿Qué representa este diario?

Un **libro mayor de manufactura / consumo masivo** (Olnatura) con:

- **Inventarios y costos de producción** (cuentas 107xx, 5xx, tipos WIP, emisión/recepción inventario).
- **Compras y proveedores** (20101001 proveedores nacionales, saldos AP).
- **Ventas y clientes** (10201004 clientes nacionales, ingresos OV, retailers C00xx).
- **IVA y retenciones** (106xx, 206xx — ~28% de líneas).
- **Nómina y pasivos laborales** (20401xxx).
- **Banca y tesorería** (8.650 movimientos bancarios, mayor volumen financiero).
- **Tipo de cambio y cierre** (series 7xx/8xx, transferencias apertura/cierre).

### 9.2 Actores que participan

| Actor | Rol en datos |
|-------|--------------|
| Catálogo de cuentas (1.962) | Eje central — siempre presente |
| Clientes comerciales (~50) | Retailers, distribuidores, público general |
| Proveedores comerciales (~760 nombres útiles) | Materias primas, servicios, logística |
| Estado / impuestos | IVA trasladado/acreditable, ISR, nómina estatal |
| Bancos | Movimientos de tesorería |
| Empleados (implícito) | Vía cuentas de nómina, no como dimensión directa |
| Sistema / cierre | Asientos de apertura, redondeo, WIP |

### 9.3 Tipos de movimiento

56 `tipo_registro` D365 — desde impuestos automáticos hasta costos estimados de producción. La semántica operativa está en este campo más que en cliente/proveedor.

### 9.4 Dimensiones empresariales recomendadas (propuesta)

| Dimensión | Propósito |
|-----------|-----------|
| `dim_entidad` | Maestro unificado con `entity_id`, `entity_type`, códigos fuente |
| `dim_tipo_entidad` | GL_ACCOUNT, AR_CUSTOMER, AP_VENDOR, BANK, TAX, PAYROLL, GENERIC |
| `dim_cuenta_contable` | Jerarquía de mayor (naturaleza, clase 1-8) |
| `dim_movimiento` | Mapeo de `tipo_registro` D365 a categoría de negocio |
| `dim_documento` | `numero_diario` + `asiento` + fecha |
| `dim_contraparte` | Solo entidades comerciales validadas (excluir GL mal ubicadas) |
| `dim_tiempo` | Ya existe vía `fact_mes` / `mes_resumen` |
| `dim_divisa` | Ya existe vía `fact_divisa` |
| `dim_centro_costo` | **No presente en export actual** — gap |

### 9.5 Nuevas tablas sugeridas (sin implementar)

```
dim_entidad          -- catálogo maestro curado
dim_tipo_entidad     -- taxonomía
bridge_movimiento_entidad  -- rol por línea: MAIN_ACCOUNT | CUSTOMER | VENDOR | NONE
dim_main_account     -- plan de cuentas con naturaleza débito/crédito
dim_posting_type     -- los 56 tipo_registro normalizados
```

---

## 10. Fase 9 — Preparación para IA

### 10.1 Metadatos que la IA necesita

| Metadato | Por qué |
|----------|---------|
| Tipo de entidad por código | Evitar tratar NOMINA como proveedor |
| Naturaleza de cuenta (activo/pasivo/ingreso/costo) | Responder “aumentó o disminuyó” correctamente |
| `tipo_registro` → categoría de negocio | Disambiguar compra vs pago vs ajuste |
| Relación cuenta ↔ dimensión permitida | Saber cuándo cliente/proveedor aplica |
| Periodo fiscal y moneda de reporte | Contexto de magnitudes |
| Glosario de abreviaturas (WIP, PTU, MOI, MOD) | Manufactura D365 |
| Lista curada de clientes/proveedores reales | Preguntas de ranking comercial |

### 10.2 Información que falta hoy

- Plan de cuentas jerárquico (solo código plano + nombre).
- Centro de costo / sitio / unidad de negocio (no exportados).
- Tabla maestra `CustTable` / `VendTable` / `MainAccount` de D365 para validación.
- Relación documento origen (factura, pago, nómina).
- Flag explícito débito/crédito (solo signo de `monto`).
- Catálogo de productos / familias (solo cuentas de inventario).

### 10.3 Qué construir antes de reglas o LLM

1. **Catálogo maestro de entidades** (revisión de `entity_catalog_candidate.csv`).
2. **Taxonomía de `tipo_registro`** (56 valores → ~10 categorías de negocio).
3. **Reglas de validez dimensional** (qué combinaciones cuenta+cliente+proveedor son legítimas).
4. **Separación semántica en el asistente:** consultas de **contabilidad** vs **comercio** vs **fiscal**.
5. **No expandir** `fact_proveedor` / `fact_cliente` sin depurar entidades GL mal clasificadas.

---

## 11. Consultas SQL utilizadas

Todas son de **solo lectura** (`SELECT`).

### Inventario de esquema

```sql
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_type, table_name;

SELECT matviewname FROM pg_matviews WHERE schemaname = 'public';
```

### Conteos y cardinalidad

```sql
SELECT COUNT(*) FROM movimientos_diario;

SELECT
    COUNT(DISTINCT account_display_value) AS dist_cuenta_cod,
    COUNT(DISTINCT nombre_cuenta) AS dist_nombre_cuenta,
    COUNT(DISTINCT cuenta_proveedor) FILTER (WHERE cuenta_proveedor IS NOT NULL) AS dist_prov_cod,
    COUNT(DISTINCT nombre_proveedor) FILTER (WHERE nombre_proveedor IS NOT NULL) AS dist_prov_nom,
    COUNT(DISTINCT cuenta_cliente) FILTER (WHERE cuenta_cliente IS NOT NULL) AS dist_cli_cod,
    COUNT(DISTINCT nombre_cliente) FILTER (WHERE nombre_cliente IS NOT NULL) AS dist_cli_nom,
    COUNT(DISTINCT tipo_registro) FILTER (WHERE tipo_registro IS NOT NULL) AS dist_tipo_reg,
    MIN(fecha) AS fecha_min,
    MAX(fecha) AS fecha_max
FROM movimientos_diario;
```

### Cobertura dimensional

```sql
SELECT
    COUNT(*) FILTER (WHERE cuenta_cliente IS NOT NULL AND nombre_cliente IS NOT NULL) AS con_cliente,
    COUNT(*) FILTER (WHERE cuenta_proveedor IS NOT NULL AND nombre_proveedor IS NOT NULL) AS con_proveedor,
    COUNT(*) FILTER (WHERE cuenta_cliente IS NULL AND cuenta_proveedor IS NULL) AS sin_contraparte,
    COUNT(*) FILTER (WHERE cuenta_cliente IS NOT NULL AND cuenta_proveedor IS NOT NULL) AS ambas_contrapartes
FROM movimientos_diario;
```

### Tipos de registro

```sql
SELECT COALESCE(tipo_registro, '(null)') AS tipo_registro,
       COUNT(*) AS movimientos,
       SUM(ABS(monto)) AS monto_total
FROM movimientos_diario
GROUP BY 1 ORDER BY movimientos DESC;
```

### Proveedores con apariencia de cuenta contable

```sql
SELECT cuenta_proveedor, nombre_proveedor,
       COUNT(*) AS movimientos, SUM(ABS(monto)) AS monto_total
FROM movimientos_diario
WHERE cuenta_proveedor IS NOT NULL
GROUP BY 1, 2
HAVING nombre_proveedor ~* '(POR PAGAR|NOMINA|IVA|ISR|GASTO|INGRESO|PROVISION|DEPRECIACION|ACTIVO|PASIVO)'
    OR cuenta_proveedor ~ '^[0-9]{4,}'
ORDER BY movimientos DESC
LIMIT 50;
```

### Caso NOMINA

```sql
SELECT cuenta_proveedor, nombre_proveedor, account_display_value, nombre_cuenta,
       COUNT(*) AS mov, SUM(ABS(monto)) AS monto
FROM movimientos_diario
WHERE UPPER(nombre_proveedor) LIKE '%NOMINA%'
   OR UPPER(nombre_cuenta) LIKE '%NOMINA%'
GROUP BY 1, 2, 3, 4
ORDER BY mov DESC
LIMIT 20;
```

### Catálogo unificado (base del CSV)

```sql
-- Cuentas
SELECT account_display_value AS codigo, MAX(nombre_cuenta) AS nombre,
       COUNT(*) AS mov, SUM(ABS(monto)) AS monto
FROM movimientos_diario GROUP BY account_display_value;

-- Proveedores
SELECT cuenta_proveedor, MAX(nombre_proveedor), COUNT(*), SUM(ABS(monto))
FROM movimientos_diario
WHERE cuenta_proveedor IS NOT NULL AND nombre_proveedor IS NOT NULL
GROUP BY cuenta_proveedor;

-- Clientes
SELECT cuenta_cliente, MAX(nombre_cliente), COUNT(*), SUM(ABS(monto))
FROM movimientos_diario
WHERE cuenta_cliente IS NOT NULL AND nombre_cliente IS NOT NULL
GROUP BY cuenta_cliente;
```

### Prefijos de código

```sql
SELECT LEFT(cuenta_proveedor, 1) AS pref,
       COUNT(DISTINCT cuenta_proveedor) AS entidades,
       COUNT(*) AS movimientos
FROM movimientos_diario
WHERE cuenta_proveedor IS NOT NULL
GROUP BY 1 ORDER BY entidades DESC;
```

---

## 12. Riesgos

| Riesgo | Impacto | Severidad |
|--------|---------|-----------|
| Tratar `fact_proveedor` como maestro AP | Respuestas incorrectas en IA (“proveedor con más movimiento” = cuenta de nómina) | **Alta** |
| Rankings de cliente dominados por `PUBLICO EN GENERAL` | Distorsión de análisis comercial | **Alta** |
| 425 nombres vs 1.962 códigos | Ambigüedad en preguntas por nombre de cuenta | **Media** |
| 20% movimientos con monto cero | KPIs de volumen inflados si se cuentan líneas | **Media** |
| Sin centro de costo en export | Imposible responder por área/planta | **Media** |
| Clasificación automática del CSV | Falsos positivos en `empresa` / `contraparte` | **Media** — requiere curación manual |
| Doble conteo en catálogo unificado | Una línea aporta a cuenta y a dimensión | **Baja** (documentado) |

---

## 13. Recomendaciones

### Inmediatas (sin tocar datos)

1. Revisar manualmente [`entity_catalog_candidate.csv`](entity_catalog_candidate.csv) con Finanzas.
2. Marcar las **3 cuentas numéricas en dimensión proveedor** como `GL_MISPOSTED`.
3. Documentar para el equipo de IA que **“proveedor” en el asistente ≠ proveedor comercial**.
4. Usar `tipo_registro` en análisis exploratorios posteriores.

### Corto plazo (diseño, no implementado aquí)

1. Crear `dim_entidad` curada desde D365 (MainAccount, CustTable, VendTable).
2. Separar métricas: **ranking comercial** vs **ranking contable**.
3. Excluir `C0003` PUBLICO EN GENERAL de rankings comerciales o tratarlo como bucket especial.
4. Enriquecer export Excel con: `MainAccountType`, `PostingType`, dimensiones financieras D365.

### Mediano plazo

1. Rediseñar `fact_proveedor` / `fact_cliente` como vistas sobre `dim_entidad` filtradas por tipo.
2. Añadir `bridge_movimiento_entidad` con rol por línea.
3. Incorporar jerarquía del plan de cuentas para drill-down.

---

## 14. Propuesta de evolución del modelo de datos

```
                    ┌─────────────────────┐
                    │  movimientos_diario │  (hecho granular — sin cambios)
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
     ┌────────────────┐ ┌───────────┐ ┌──────────────────┐
     │ dim_main_account│ │dim_entidad│ │ dim_posting_type │
     │  (plan cuentas) │ │ (maestro) │ │ (tipo_registro)  │
     └────────────────┘ └─────┬─────┘ └──────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
           ┌────────────────┐   ┌────────────────┐
           │ fact_movimiento│   │ agg por tipo   │
           │   (opcional)   │   │ AR/AP/GL/Bank  │
           └────────────────┘   └────────────────┘
```

**Principio rector:** El diario general es la verdad operativa; clientes y proveedores son **roles opcionales** de cada línea, no el modelo entero.

---

## 15. Entregables

| Archivo | Descripción |
|---------|-------------|
| [`docs/business_entity_discovery.md`](business_entity_discovery.md) | Este documento |
| [`docs/entity_catalog_candidate.csv`](entity_catalog_candidate.csv) | 2.778 entidades con clasificación preliminar |

---

*Análisis realizado sobre PostgreSQL `ia_mvp` en entorno local. Volúmenes en MXN (moneda de reporte del diario). Clasificaciones del CSV son hipótesis para curación — no deben usarse en producción sin validación de negocio.*
