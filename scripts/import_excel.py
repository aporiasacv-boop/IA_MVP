from __future__ import annotations

import hashlib
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
from sqlalchemy import insert, select, func

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.settings import settings
from app.database.database import SessionLocal
from app.models.movimiento_diario import MovimientoDiario

DEFAULT_EXCEL = settings.DATA_RAW_DIR / "Movimiento de diario general_2025.xlsx"
BATCH_SIZE = 5000

EXCEL_COLUMNS = [
    "Número de diario",
    "Asiento",
    "Fecha",
    "Año cerrado",
    "Account display value",
    "Nombre de la cuenta",
    "Descripción",
    "Divisa",
    "Monto en divisa de transacción",
    "Monto",
    "Monto en divisa de reporte",
    "Tipo de registro",
    "Capa de registro",
    "Cuenta de proveedor",
    "Nombre del proveedor",
    "Cuenta de cliente",
    "Nombre del cliente",
    "Creado por",
    "Creado por2",
]

HASH_COLUMNS = EXCEL_COLUMNS + ["hoja_origen"]


def to_decimal(value: object) -> Decimal:
    if value is None or pd.isna(value):
        return Decimal("0")
    return Decimal(str(value))


def normalize_optional_text(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").str.strip()
    return normalized.where(normalized.notna() & (normalized != "") & (normalized.str.lower() != "nan"), None)


def normalize_required_text(series: pd.Series) -> pd.Series:
    normalized = series.astype("string").fillna("").str.strip()
    return normalized.replace("nan", "")


def compute_hash(row: pd.Series) -> str:
    parts: list[str] = []
    for column in HASH_COLUMNS:
        value = row[column]
        if pd.isna(value):
            parts.append("")
        elif isinstance(value, (pd.Timestamp, datetime, date)):
            parts.append(pd.Timestamp(value).strftime("%Y-%m-%d"))
        else:
            parts.append(str(value).strip())
    payload = "|".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def transform_dataframe(df: pd.DataFrame, fecha_carga: datetime) -> pd.DataFrame:
    transformed = pd.DataFrame()
    fecha_series = pd.to_datetime(df["Fecha"])

    transformed["hoja_origen"] = normalize_required_text(df["hoja_origen"])
    transformed["numero_diario"] = normalize_required_text(df["Número de diario"])
    transformed["asiento"] = normalize_required_text(df["Asiento"])
    transformed["fecha"] = fecha_series.dt.date
    transformed["mes"] = fecha_series.dt.month.astype(int)
    transformed["anio"] = fecha_series.dt.year.astype(int)
    transformed["anio_cerrado"] = normalize_required_text(df["Año cerrado"])
    transformed["account_display_value"] = normalize_required_text(df["Account display value"])
    transformed["nombre_cuenta"] = normalize_required_text(df["Nombre de la cuenta"])
    transformed["descripcion"] = normalize_optional_text(df["Descripción"])
    transformed["divisa"] = normalize_required_text(df["Divisa"])
    transformed["monto_divisa_transaccion"] = df["Monto en divisa de transacción"].map(to_decimal)
    transformed["monto"] = df["Monto"].map(to_decimal)
    transformed["monto_divisa_reporte"] = df["Monto en divisa de reporte"].map(to_decimal)
    transformed["tipo_registro"] = normalize_optional_text(df["Tipo de registro"])
    transformed["capa_registro"] = normalize_required_text(df["Capa de registro"])
    transformed["cuenta_proveedor"] = normalize_optional_text(df["Cuenta de proveedor"])
    transformed["nombre_proveedor"] = normalize_optional_text(df["Nombre del proveedor"])
    transformed["cuenta_cliente"] = normalize_optional_text(df["Cuenta de cliente"])
    transformed["nombre_cliente"] = normalize_optional_text(df["Nombre del cliente"])
    transformed["creado_por"] = normalize_required_text(df["Creado por"])
    transformed["creado_por2"] = normalize_required_text(df["Creado por2"])
    transformed["fecha_carga"] = fecha_carga
    transformed["hash_fuente"] = df.apply(compute_hash, axis=1)
    return transformed


def load_excel(excel_path: Path) -> pd.DataFrame:
    workbook = pd.ExcelFile(excel_path)
    frames: list[pd.DataFrame] = []
    for sheet_name in workbook.sheet_names:
        print(f"Procesando hoja {sheet_name}...")
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        df["hoja_origen"] = sheet_name
        print(f"{len(df)} registros")
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def table_has_rows() -> bool:
    with SessionLocal() as session:
        count = session.scalar(select(func.count()).select_from(MovimientoDiario))
        return bool(count and count > 0)


def insert_batches(records: list[dict]) -> int:
    total_inserted = 0
    batch_number = 0

    with SessionLocal() as session:
        for start in range(0, len(records), BATCH_SIZE):
            batch_number += 1
            batch = records[start : start + BATCH_SIZE]
            print(f"Insertando lote {batch_number}...")
            session.execute(insert(MovimientoDiario), batch)
            session.commit()
            total_inserted += len(batch)

    return total_inserted


def main() -> int:
    excel_path = DEFAULT_EXCEL
    if len(sys.argv) > 1:
        excel_path = Path(sys.argv[1]).resolve()

    if not excel_path.exists():
        print(f"No se encontro el archivo: {excel_path}", file=sys.stderr)
        return 1

    if table_has_rows():
        print("La tabla movimientos_diario ya contiene registros. Abortando carga.", file=sys.stderr)
        return 1

    print(f"Leyendo archivo: {excel_path.name}")
    raw_df = load_excel(excel_path)
    print(f"Total registros a insertar: {len(raw_df):,}")

    fecha_carga = datetime.now()
    print("Transformando y calculando hash_fuente...")
    transformed = transform_dataframe(raw_df, fecha_carga)
    records = transformed.to_dict(orient="records")
    inserted = insert_batches(records)
    print(f"Carga completada: {inserted:,} registros insertados")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
