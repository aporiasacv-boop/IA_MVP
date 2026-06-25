from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCEL = PROJECT_ROOT / "data" / "raw" / "Movimiento de diario general_2025.xlsx"
OUTPUT_MD = PROJECT_ROOT / "docs" / "excel_analysis.md"
SAMPLE_ROWS = 5
EXAMPLE_VALUES = 5


def infer_type(series: pd.Series) -> str:
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if pd.api.types.is_bool_dtype(series):
        return "boolean"
    if pd.api.types.is_integer_dtype(series):
        return "integer"
    if pd.api.types.is_float_dtype(series):
        non_null = series.dropna()
        if len(non_null) > 0 and np.all(np.equal(non_null, non_null.astype(int))):
            return "numeric (entero aparente)"
        return "numeric (decimal)"
    non_null = series.dropna().astype(str).str.strip()
    if len(non_null) == 0:
        return "text"
    if non_null.str.fullmatch(r"-?\d+").all():
        return "text (codigo numerico)"
    if non_null.str.fullmatch(r"-?\d+\.\d+").all():
        return "text (numero como texto)"
    return "text"


def example_values(series: pd.Series, limit: int = EXAMPLE_VALUES) -> list[str]:
    values: list[str] = []
    for value in series.dropna().astype(str).unique()[:limit]:
        values.append(value[:120])
    return values


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def dataframe_preview_markdown(df: pd.DataFrame) -> str:
    headers = [str(col) for col in df.columns]
    rows = [[str(value)[:80] for value in row] for row in df.values.tolist()]
    return markdown_table(headers, rows)


def analyze_sheet(sheet_name: str, df: pd.DataFrame) -> dict:
    preview = df.head(SAMPLE_ROWS).fillna("").astype(str)
    preview_md = dataframe_preview_markdown(preview)
    return {
        "name": sheet_name,
        "rows": len(df),
        "columns": len(df.columns),
        "preview_md": preview_md,
        "df": df,
    }


def analyze_quality(combined: pd.DataFrame, sheets: dict[str, pd.DataFrame]) -> dict:
    amount_columns = [
        "Monto en divisa de transacción",
        "Monto",
        "Monto en divisa de reporte",
    ]
    date_columns = ["Fecha"]

    null_counts = combined.isnull().sum()
    null_pct = (null_counts / len(combined) * 100).round(2)

    empty_columns: list[str] = []
    for column in combined.columns:
        if column == "_hoja_origen":
            continue
        series = combined[column]
        if series.isna().all():
            empty_columns.append(column)
            continue
        if series.dtype == object:
            stripped = series.astype(str).str.strip()
            if ((series.isna()) | (stripped == "") | (stripped.str.lower() == "nan")).all():
                empty_columns.append(column)

    duplicate_rows = int(combined.drop(columns=["_hoja_origen"]).duplicated().sum())

    invalid_dates: dict[str, int] = {}
    for column in date_columns:
        if column in combined.columns:
            invalid_dates[column] = int(combined[column].isna().sum())

    invalid_amounts: dict[str, dict[str, int]] = {}
    for column in amount_columns:
        if column not in combined.columns:
            continue
        series = pd.to_numeric(combined[column], errors="coerce")
        invalid_amounts[column] = {
            "nulos": int(series.isna().sum()),
            "ceros": int((series == 0).sum()),
            "negativos": int((series < 0).sum()),
            "positivos": int((series > 0).sum()),
            "no_numericos": int(
                combined[column].notna().sum() - series.notna().sum()
            ),
        }

    per_sheet_duplicates: list[tuple[str, int]] = []
    for sheet_name, df in sheets.items():
        per_sheet_duplicates.append((sheet_name, int(df.duplicated().sum())))

    return {
        "null_counts": null_counts,
        "null_pct": null_pct,
        "empty_columns": empty_columns,
        "duplicate_rows": duplicate_rows,
        "invalid_dates": invalid_dates,
        "invalid_amounts": invalid_amounts,
        "per_sheet_duplicates": per_sheet_duplicates,
    }


def build_data_dictionary(combined: pd.DataFrame) -> list[dict]:
    dictionary: list[dict] = []
    for column in combined.columns:
        if column == "_hoja_origen":
            continue
        series = combined[column]
        dictionary.append(
            {
                "column": column,
                "type": infer_type(series),
                "null_pct": float((series.isnull().sum() / len(combined) * 100).round(2)),
                "unique": int(series.nunique(dropna=True)),
                "examples": example_values(series),
            }
        )
    return dictionary


def build_index_candidates(combined: pd.DataFrame) -> list[dict]:
    candidates = [
        {
            "column": "Fecha",
            "use": "filtros temporales, particionado, agregaciones mensuales",
            "reason": "Todas las consultas analiticas dependen del periodo contable.",
        },
        {
            "column": "Account display value",
            "use": "filtros, joins dimensionales, agrupaciones por cuenta",
            "reason": "Identificador contable principal para balances y mayor.",
        },
        {
            "column": "Nombre de la cuenta",
            "use": "busquedas textuales, reportes legibles",
            "reason": "Etiqueta humana asociada al codigo contable.",
        },
        {
            "column": "Número de diario",
            "use": "trazabilidad, deduplicacion, auditoria",
            "reason": "Agrupa movimientos pertenecientes al mismo asiento contable.",
        },
        {
            "column": "Asiento",
            "use": "joins intra-asiento, validacion de partida doble",
            "reason": "Subdivision del diario para reconstruir asientos completos.",
        },
        {
            "column": "Cuenta de proveedor",
            "use": "filtros, joins, ranking de proveedores",
            "reason": "Clave analitica para cuentas por pagar y gasto con terceros.",
        },
        {
            "column": "Nombre del proveedor",
            "use": "busquedas frecuentes, dashboards",
            "reason": "Dimension de negocio mas consultada en analisis de compras.",
        },
        {
            "column": "Cuenta de cliente",
            "use": "filtros, joins, ranking de clientes",
            "reason": "Clave analitica para cuentas por cobrar e ingresos.",
        },
        {
            "column": "Nombre del cliente",
            "use": "busquedas frecuentes, dashboards",
            "reason": "Dimension comercial para ventas y cartera.",
        },
        {
            "column": "Divisa",
            "use": "filtros, agregaciones multimoneda",
            "reason": "Segmentacion de montos por moneda operativa.",
        },
        {
            "column": "Tipo de registro",
            "use": "filtros de calidad, exclusion de ajustes",
            "reason": "Distingue movimientos operativos versus tecnicos.",
        },
        {
            "column": "Capa de registro",
            "use": "filtros contables, conciliacion",
            "reason": "Permite separar capas contables o de consolidacion.",
        },
        {
            "column": "Creado por",
            "use": "auditoria, control interno",
            "reason": "Trazabilidad del origen operativo del movimiento.",
        },
    ]
    present = set(combined.columns)
    return [item for item in candidates if item["column"] in present]


def business_questions() -> list[str]:
    return [
        "¿Que proveedor concentra el mayor importe absoluto en el ejercicio?",
        "¿Que proveedor tiene mas movimientos registrados?",
        "¿Que cliente genera mayor facturacion acumulada?",
        "¿Que cliente tiene mas transacciones contables?",
        "¿Cual es la cuenta contable con mayor saldo neto?",
        "¿Que cuenta presenta la mayor cantidad de apuntes?",
        "¿Que mes tuvo mayor volumen de movimientos?",
        "¿Que mes concentro el mayor importe absoluto?",
        "¿Como evoluciona el gasto total mes a mes?",
        "¿Como evolucionan los ingresos mes a mes?",
        "¿Que divisas intervienen y cual domina en numero de operaciones?",
        "¿Existen diferencias relevantes entre monto transaccional y monto en divisa de reporte?",
        "¿Que usuarios crean mas asientos contables?",
        "¿Que tipos de registro son los mas frecuentes?",
        "¿Que capa de registro concentra mas actividad?",
        "¿Que cuentas de proveedor tienen saldo negativo acumulado?",
        "¿Que cuentas de cliente tienen saldo positivo acumulado?",
        "¿Que descripciones se repiten con mayor frecuencia?",
        "¿Que diarios contienen asientos desbalanceados?",
        "¿Que proveedores operan en mas de una divisa?",
        "¿Que clientes operan en mas de una divisa?",
        "¿Que cuentas contables se movieron todos los meses del año?",
        "¿Que meses presentan caida abrupta de actividad frente al promedio?",
        "¿Que combinacion cuenta-proveedor concentra mas gasto?",
        "¿Que combinacion cuenta-cliente concentra mas ingreso?",
    ]


def build_markdown(
    excel_path: Path,
    sheet_analysis: list[dict],
    combined: pd.DataFrame,
    dictionary: list[dict],
    quality: dict,
    index_candidates: list[dict],
) -> str:
    total_rows = len(combined)
    total_columns = len([c for c in combined.columns if c != "_hoja_origen"])
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sections = [
        "# Analisis del Excel de Movimientos Contables",
        "",
        f"Generado automaticamente el {generated_at}.",
        "",
        "# 1. Resumen General",
        "",
        f"- Nombre del archivo: `{excel_path.name}`",
        f"- Ruta analizada: `data/raw/{excel_path.name}`",
        f"- Numero de hojas: {len(sheet_analysis)}",
        f"- Numero total de registros: {total_rows:,}",
        f"- Numero total de columnas: {total_columns}",
        "",
        "# 2. Analisis por Hoja",
        "",
    ]

    for sheet in sheet_analysis:
        sections.extend(
            [
                f"## Hoja: {sheet['name']}",
                "",
                f"- Nombre: `{sheet['name']}`",
                f"- Numero de filas: {sheet['rows']:,}",
                f"- Numero de columnas: {sheet['columns']}",
                "",
                "### Muestra de las primeras filas",
                "",
                sheet["preview_md"],
                "",
            ]
        )

    sections.extend(["# 3. Diccionario de Datos", ""])
    dict_rows = [
        [
            item["column"],
            item["type"],
            f"{item['null_pct']:.2f}%",
            str(item["unique"]),
            "; ".join(item["examples"]) if item["examples"] else "Sin ejemplos",
        ]
        for item in dictionary
    ]
    sections.append(
        markdown_table(
            ["Columna", "Tipo inferido", "% nulos", "Valores unicos", "Ejemplos"],
            dict_rows,
        )
    )
    sections.append("")

    sections.extend(["# 4. Calidad de Datos", ""])
    null_rows = []
    for column, pct in quality["null_pct"].items():
        if column == "_hoja_origen":
            continue
        null_rows.append([column, str(int(quality["null_counts"][column])), f"{pct:.2f}%"])
    sections.append("## Valores nulos")
    sections.append("")
    sections.append(markdown_table(["Columna", "Nulos", "% nulos"], null_rows))
    sections.append("")

    sections.append("## Columnas vacias")
    sections.append("")
    if quality["empty_columns"]:
        for column in quality["empty_columns"]:
            sections.append(f"- `{column}`")
    else:
        sections.append("- No se detectaron columnas completamente vacias.")
    sections.append("")

    sections.append("## Duplicados")
    sections.append("")
    sections.append(f"- Duplicados exactos en dataset consolidado: **{quality['duplicate_rows']:,}**")
    sections.append("")
    sections.append("Duplicados por hoja:")
    sections.append("")
    dup_rows = [[name, str(count)] for name, count in quality["per_sheet_duplicates"]]
    sections.append(markdown_table(["Hoja", "Duplicados exactos"], dup_rows))
    sections.append("")

    sections.append("## Fechas invalidas o ausentes")
    sections.append("")
    for column, count in quality["invalid_dates"].items():
        sections.append(f"- `{column}`: {count:,} valores nulos o invalidos")
    if combined["Fecha"].notna().any():
        sections.append(
            f"- Rango observado en `Fecha`: {combined['Fecha'].min()} a {combined['Fecha'].max()}"
        )
    sections.append("")

    sections.append("## Montos invalidos o atipicos")
    sections.append("")
    amount_rows = []
    for column, stats in quality["invalid_amounts"].items():
        amount_rows.append(
            [
                column,
                str(stats["nulos"]),
                str(stats["no_numericos"]),
                str(stats["ceros"]),
                str(stats["negativos"]),
                str(stats["positivos"]),
            ]
        )
    sections.append(
        markdown_table(
            ["Columna", "Nulos", "No numericos", "Ceros", "Negativos", "Positivos"],
            amount_rows,
        )
    )
    sections.append("")

    sections.extend(["# 5. Candidatos para Indices SQL", ""])
    index_rows = [
        [item["column"], item["use"], item["reason"]] for item in index_candidates
    ]
    sections.append(markdown_table(["Columna", "Uso analitico", "Justificacion"], index_rows))
    sections.append("")

    sections.extend(
        [
            "# 6. Modelo Analitico Propuesto",
            "",
            "## Tabla detalle: `movimientos_diario`",
            "",
            "Tabla unificada con una fila por apunte contable exportado desde el diario general.",
            "",
            markdown_table(
                ["Columna SQL", "Tipo sugerido", "Origen Excel", "Justificacion"],
                [
                    ["id", "BIGSERIAL PK", "generado", "Identificador interno estable para joins y auditoria."],
                    ["hoja_origen", "VARCHAR(20)", "_hoja_origen", "Trazabilidad del mes exportado en Excel."],
                    ["numero_diario", "VARCHAR(50)", "Número de diario", "Agrupa lineas del mismo asiento contable."],
                    ["asiento", "VARCHAR(50)", "Asiento", "Subidentificador del asiento dentro del diario."],
                    ["fecha", "DATE", "Fecha", "Dimension temporal principal para BI y particionado."],
                    ["anio_cerrado", "VARCHAR(10)", "Año cerrado", "Permite filtrar periodos cerrados o abiertos."],
                    ["cuenta_codigo", "VARCHAR(50)", "Account display value", "Clave contable para balances y mayor."],
                    ["cuenta_nombre", "VARCHAR(255)", "Nombre de la cuenta", "Etiqueta legible para reportes."],
                    ["descripcion", "TEXT", "Descripción", "Contexto operativo del movimiento."],
                    ["divisa", "VARCHAR(10)", "Divisa", "Segmentacion multimoneda."],
                    ["monto_divisa_transaccion", "NUMERIC(18,4)", "Monto en divisa de transacción", "Importe en moneda original."],
                    ["monto", "NUMERIC(18,4)", "Monto", "Importe funcional principal."],
                    ["monto_divisa_reporte", "NUMERIC(18,4)", "Monto en divisa de reporte", "Importe para reportes consolidados."],
                    ["tipo_registro", "VARCHAR(50)", "Tipo de registro", "Clasificacion operativa del apunte."],
                    ["capa_registro", "VARCHAR(50)", "Capa de registro", "Separacion de capas contables."],
                    ["cuenta_proveedor", "VARCHAR(50)", "Cuenta de proveedor", "Clave de tercero proveedor."],
                    ["nombre_proveedor", "VARCHAR(255)", "Nombre del proveedor", "Dimension analitica de compras."],
                    ["cuenta_cliente", "VARCHAR(50)", "Cuenta de cliente", "Clave de tercero cliente."],
                    ["nombre_cliente", "VARCHAR(255)", "Nombre del cliente", "Dimension analitica de ventas."],
                    ["creado_por", "VARCHAR(100)", "Creado por", "Auditoria de origen."],
                    ["creado_por2", "VARCHAR(100)", "Creado por2", "Campo auxiliar de trazabilidad; evaluar si aporta valor o puede omitirse."],
                    ["hash_fuente", "VARCHAR(64)", "calculado", "Control de duplicados en cargas incrementales."],
                    ["created_at", "TIMESTAMPTZ", "generado", "Fecha de ingesta al MVP."],
                ],
            ),
            "",
            "## Tablas agregadas propuestas",
            "",
            "### `fact_mes`",
            "",
            "Agregacion mensual para dashboards ejecutivos.",
            "",
            "- `anio`, `mes`",
            "- `total_movimientos`",
            "- `total_debe`, `total_haber`, `importe_absoluto`",
            "- `proveedores_activos`, `clientes_activos`, `cuentas_activas`",
            "",
            "### `fact_cuenta`",
            "",
            "Saldo y actividad por cuenta contable.",
            "",
            "- `cuenta_codigo`, `cuenta_nombre`",
            "- `anio`, `mes`",
            "- `total_movimientos`, `saldo_neto`, `importe_absoluto`",
            "",
            "### `fact_proveedor`",
            "",
            "Analitica de compras y cuentas por pagar.",
            "",
            "- `cuenta_proveedor`, `nombre_proveedor`",
            "- `anio`, `mes`",
            "- `total_movimientos`, `importe_neto`, `importe_absoluto`",
            "",
            "### `fact_cliente`",
            "",
            "Analitica comercial y cuentas por cobrar.",
            "",
            "- `cuenta_cliente`, `nombre_cliente`",
            "- `anio`, `mes`",
            "- `total_movimientos`, `importe_neto`, `importe_absoluto`",
            "",
            "### `fact_divisa`",
            "",
            "Resumen multimoneda cuando el negocio opere en mas de una divisa.",
            "",
            "- `divisa`, `anio`, `mes`",
            "- `total_movimientos`, `monto_transaccion`, `monto_reporte`",
            "",
            "# 7. Estrategia de Rendimiento",
            "",
            "## Indices recomendados",
            "",
            "- `btree (fecha)` para filtros temporales.",
            "- `btree (numero_diario, asiento)` para reconstruccion de asientos.",
            "- `btree (cuenta_codigo, fecha)` para mayor analitico.",
            "- `btree (cuenta_proveedor, fecha)` y `btree (cuenta_cliente, fecha)` para analitica de terceros.",
            "- `btree (divisa, fecha)` para reportes multimoneda.",
            "- Indice hash o unico sobre `hash_fuente` para evitar cargas duplicadas.",
            "",
            "## Particionado",
            "",
            "Con ~386k filas anuales y crecimiento esperado, conviene particionar `movimientos_diario` por rango mensual o anual usando `fecha`.",
            "El Excel ya viene segmentado por mes, lo que valida un particionado temporal natural.",
            "",
            "## Vistas materializadas recomendadas",
            "",
            "- `mv_resumen_mes` equivalente a `fact_mes`.",
            "- `mv_top_proveedores` con ranking por importe absoluto y numero de movimientos.",
            "- `mv_top_clientes` con ranking comercial.",
            "- `mv_saldos_cuenta` para consultas de balance frecuentes.",
            "",
            "Refresco sugerido: post-carga del Excel o incremental diario.",
            "",
            "## Agregaciones recomendadas",
            "",
            "- Precomputar totales mensuales por cuenta, proveedor, cliente y divisa.",
            "- Mantener metricas de conteo y suma absoluta para preguntas de ranking.",
            "- Conservar saldo neto y saldo absoluto por separado para no distorsionar analisis de volumen.",
            "",
            "# 8. Consultas de Negocio Esperadas",
            "",
        ]
    )

    for index, question in enumerate(business_questions(), start=1):
        sections.append(f"{index}. {question}")

    sections.extend(
        [
            "",
            "# 9. Recomendacion Final",
            "",
            "Para este MVP la estructura SQL definitiva debe ser hibrida:",
            "",
            "1. Una tabla detalle unificada `movimientos_diario` con todas las columnas operativas del Excel mas metadatos de ingesta.",
            "2. Tablas agregadas por mes, cuenta, proveedor, cliente y divisa para responder consultas frecuentes sin escanear 386k+ filas.",
            "3. Indices orientados a `fecha`, `cuenta_codigo`, terceros y trazabilidad de asientos.",
            "4. Particionado por `fecha` si el volumen crece a multi-anio.",
            "5. Vistas materializadas para rankings y dashboards ejecutivos.",
            "",
            "No se recomienda normalizar en multiples tablas transaccionales en la primera iteracion porque el Excel ya trae dimensiones desnormalizadas y el MVP prioriza velocidad de consulta sobre pureza relacional.",
            "Si mas adelante se integran maestros de cuentas, clientes y proveedores desde ERP, entonces convendra separar dimensiones y mantener `movimientos_diario` como hecho central.",
            "",
        ]
    )

    return "\n".join(sections)


def print_executive_summary(
    excel_path: Path,
    sheet_analysis: list[dict],
    combined: pd.DataFrame,
    quality: dict,
    output_md: Path,
) -> None:
    total_rows = len(combined)
    total_columns = len([c for c in combined.columns if c != "_hoja_origen"])
    top_null = (
        quality["null_pct"]
        .drop(labels=["_hoja_origen"], errors="ignore")
        .sort_values(ascending=False)
        .head(5)
    )

    print("=" * 72)
    print("RESUMEN EJECUTIVO - ANALISIS EXCEL MOVIMIENTOS CONTABLES")
    print("=" * 72)
    print(f"Archivo: {excel_path.name}")
    print(f"Hojas: {len(sheet_analysis)}")
    print(f"Registros totales: {total_rows:,}")
    print(f"Columnas: {total_columns}")
    print(f"Duplicados exactos: {quality['duplicate_rows']:,}")
    print(f"Documento generado: {output_md}")
    print("")
    print("Registros por hoja:")
    for sheet in sheet_analysis:
        print(f"  - {sheet['name']}: {sheet['rows']:,}")
    print("")
    print("Columnas con mayor % de nulos:")
    for column, pct in top_null.items():
        print(f"  - {column}: {pct:.2f}%")
    print("")
    if "Fecha" in combined.columns and combined["Fecha"].notna().any():
        print(
            f"Rango de fechas: {combined['Fecha'].min()} -> {combined['Fecha'].max()}"
        )
    print("=" * 72)


def main() -> int:
    excel_path = DEFAULT_EXCEL
    if len(sys.argv) > 1:
        excel_path = Path(sys.argv[1]).resolve()

    if not excel_path.exists():
        print(f"No se encontro el archivo: {excel_path}", file=sys.stderr)
        return 1

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)

    workbook = pd.ExcelFile(excel_path)
    sheet_analysis: list[dict] = []
    frames: list[pd.DataFrame] = []
    sheets: dict[str, pd.DataFrame] = {}

    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        sheet_analysis.append(analyze_sheet(sheet_name, df))
        df["_hoja_origen"] = sheet_name
        sheets[sheet_name] = df
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    dictionary = build_data_dictionary(combined)
    quality = analyze_quality(combined, sheets)
    index_candidates = build_index_candidates(combined)
    markdown = build_markdown(
        excel_path=excel_path,
        sheet_analysis=sheet_analysis,
        combined=combined,
        dictionary=dictionary,
        quality=quality,
        index_candidates=index_candidates,
    )
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    print_executive_summary(
        excel_path=excel_path,
        sheet_analysis=sheet_analysis,
        combined=combined,
        quality=quality,
        output_md=OUTPUT_MD,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
