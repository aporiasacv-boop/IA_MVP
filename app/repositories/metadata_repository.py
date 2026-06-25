from sqlalchemy import text
from sqlalchemy.orm import Session


class MetadataRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def fetch_dataset_metadata(self) -> dict:
        row = self.session.execute(
            text(
                """
                WITH resumen AS (
                    SELECT
                        COALESCE(SUM(movimientos), 0) AS total_registros,
                        MIN(anio * 100 + mes) AS periodo_min,
                        MAX(anio * 100 + mes) AS periodo_max,
                        COUNT(*) AS total_meses
                    FROM mv_resumen_mensual
                ),
                anios AS (
                    SELECT COALESCE(
                        ARRAY_AGG(DISTINCT anio ORDER BY anio),
                        ARRAY[]::integer[]
                    ) AS anios_disponibles
                    FROM mv_resumen_mensual
                ),
                meses AS (
                    SELECT COALESCE(
                        ARRAY_AGG(
                            anio * 100 + mes ORDER BY anio, mes
                        ),
                        ARRAY[]::integer[]
                    ) AS meses_disponibles
                    FROM mv_resumen_mensual
                )
                SELECT
                    resumen.total_registros,
                    resumen.periodo_min,
                    resumen.periodo_max,
                    resumen.total_meses,
                    (SELECT COUNT(*) FROM fact_cliente) AS total_clientes,
                    (SELECT COUNT(*) FROM fact_proveedor) AS total_proveedores,
                    (SELECT COUNT(*) FROM fact_cuenta) AS total_cuentas,
                    anios.anios_disponibles,
                    meses.meses_disponibles
                FROM resumen
                CROSS JOIN anios
                CROSS JOIN meses
                """
            )
        ).mappings().one()
        return dict(row)
