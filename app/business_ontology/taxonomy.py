from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.business_ontology.constants import (
    CONCEPT_BEHAVIOR,
    CONCEPT_IDENTITY,
    CONCEPT_NATURE,
    CONCEPT_ROLE,
)


@dataclass(frozen=True)
class TaxonomyTypeSeed:
    concept_category: str
    type_code: str
    type_label: str
    description: str
    sort_order: int


INITIAL_TAXONOMY: tuple[TaxonomyTypeSeed, ...] = (
    # Identity — ¿Quién es?
    TaxonomyTypeSeed(CONCEPT_IDENTITY, "ORGANIZATION", "Organización", "Entidad empresarial con identidad canónica", 10),
    TaxonomyTypeSeed(CONCEPT_IDENTITY, "COMMERCIAL_PARTY", "Parte comercial", "Participante en dimensiones cliente o proveedor", 20),
    TaxonomyTypeSeed(CONCEPT_IDENTITY, "GL_ACCOUNT", "Cuenta contable", "Representación de cuenta del catálogo contable", 30),
    TaxonomyTypeSeed(CONCEPT_IDENTITY, "FINANCIAL_INSTITUTION", "Institución financiera", "Banco o entidad financiera identificada por comportamiento", 40),
    # Role — ¿Qué función?
    TaxonomyTypeSeed(CONCEPT_ROLE, "CLIENTE", "Cliente", "Dimensión cuenta_cliente predominante", 10),
    TaxonomyTypeSeed(CONCEPT_ROLE, "PROVEEDOR", "Proveedor", "Dimensión cuenta_proveedor predominante", 20),
    TaxonomyTypeSeed(CONCEPT_ROLE, "BANCO", "Banco", "Cuentas de tesorería o institución financiera", 30),
    TaxonomyTypeSeed(CONCEPT_ROLE, "EMPLEADO", "Empleado", "Relacionado con nómina o sueldos", 40),
    TaxonomyTypeSeed(CONCEPT_ROLE, "ENTIDAD_COMERCIAL", "Entidad comercial", "Cliente y proveedor simultáneamente", 50),
    TaxonomyTypeSeed(CONCEPT_ROLE, "GOBIERNO", "Gobierno", "Autoridad fiscal o gubernamental", 60),
    TaxonomyTypeSeed(CONCEPT_ROLE, "CUENTA_CONTABLE", "Cuenta contable", "Rol de cuenta del plan contable", 70),
    TaxonomyTypeSeed(CONCEPT_ROLE, "CENTRO_COSTO", "Centro de costo", "Dimensión de agrupación de costos", 80),
    TaxonomyTypeSeed(CONCEPT_ROLE, "OTRO", "Otro", "Rol no determinado con evidencia suficiente", 90),
    # Nature — ¿Qué representa contablemente?
    TaxonomyTypeSeed(CONCEPT_NATURE, "ACTIVO", "Activo", "Cuentas con prefijo 1xx", 10),
    TaxonomyTypeSeed(CONCEPT_NATURE, "PASIVO", "Pasivo", "Cuentas con prefijo 2xx", 20),
    TaxonomyTypeSeed(CONCEPT_NATURE, "CAPITAL", "Capital", "Cuentas con prefijo 3xx", 30),
    TaxonomyTypeSeed(CONCEPT_NATURE, "INGRESO", "Ingreso", "Cuentas con prefijo 4xx", 40),
    TaxonomyTypeSeed(CONCEPT_NATURE, "GASTO", "Gasto", "Cuentas con prefijo 5xx", 50),
    TaxonomyTypeSeed(CONCEPT_NATURE, "COSTO", "Costo", "Cuentas con prefijo 6xx", 60),
    TaxonomyTypeSeed(CONCEPT_NATURE, "IMPUESTO", "Impuesto", "Cuentas fiscales o de impuestos", 70),
    TaxonomyTypeSeed(CONCEPT_NATURE, "PATRIMONIO", "Patrimonio", "Cuentas de patrimonio", 80),
    TaxonomyTypeSeed(CONCEPT_NATURE, "AJUSTE", "Ajuste", "Cuentas de ajuste o cierre", 90),
    TaxonomyTypeSeed(CONCEPT_NATURE, "OTRO", "Otro", "Naturaleza contable indeterminada", 100),
    # Behavior — ¿Cómo participa?
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "COMPRA", "Compra", "Flujo de adquisición / débito en proveedor", 10),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "VENTA", "Venta", "Flujo de ingreso comercial", 20),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "COBRO", "Cobro", "Recuperación de cartera — crédito dominante en cliente", 30),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "PAGO", "Pago", "Desembolso a proveedores", 40),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "TRANSFERENCIA", "Transferencia", "Movimiento entre cuentas sin contraparte comercial", 50),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "NOMINA", "Nómina", "Movimientos de sueldos y salarios", 60),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "IMPUESTO", "Impuesto", "Movimientos fiscales", 70),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "INVENTARIO", "Inventario", "Movimientos de existencias", 80),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "PRODUCCION", "Producción", "Movimientos de producción / WIP", 90),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "FINANCIERO", "Financiero", "Tesorería, bancos, intereses", 100),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "ADMINISTRATIVO", "Administrativo", "Gastos administrativos recurrentes", 110),
    TaxonomyTypeSeed(CONCEPT_BEHAVIOR, "MIXTO", "Mixto", "Múltiples patrones de participación", 120),
)


@dataclass(frozen=True)
class RuleSeed:
    rule_code: str
    concept_category: str
    target_type_code: str
    priority: int
    score_weight: Decimal
    description: str
    conditions_json: dict


def build_rule_seeds() -> tuple[RuleSeed, ...]:
    return (
        # Identity rules
        RuleSeed("identity_commercial_party", CONCEPT_IDENTITY, "COMMERCIAL_PARTY", 10, Decimal("0.9000"),
                 "Dimensiones comerciales presentes", {"requires_any_dimension": list({"cuenta_cliente", "cuenta_proveedor"})}),
        RuleSeed("identity_gl_account", CONCEPT_IDENTITY, "GL_ACCOUNT", 20, Decimal("0.9200"),
                 "Solo dimensión cuenta contable", {"requires_only_dimension": "account_display_value"}),
        RuleSeed("identity_organization", CONCEPT_IDENTITY, "ORGANIZATION", 30, Decimal("0.8500"),
                 "Organización con movimientos comerciales", {"min_movements": 1, "requires_any_dimension": list({"cuenta_cliente", "cuenta_proveedor"})}),
        RuleSeed("identity_financial_institution", CONCEPT_IDENTITY, "FINANCIAL_INSTITUTION", 40, Decimal("0.8800"),
                 "Cuentas de banco en top_accounts", {"account_keywords": list({"BANCO", "BANCARIA", "CAJA"})}),
        # Role rules — profile dimensions primary
        RuleSeed("role_client_dimension", CONCEPT_ROLE, "CLIENTE", 10, Decimal("0.9200"),
                 "Solo dimensión cliente", {"requires_only_dimension": "cuenta_cliente"}),
        RuleSeed("role_vendor_dimension", CONCEPT_ROLE, "PROVEEDOR", 20, Decimal("0.9200"),
                 "Solo dimensión proveedor", {"requires_only_dimension": "cuenta_proveedor"}),
        RuleSeed("role_dual_commercial", CONCEPT_ROLE, "ENTIDAD_COMERCIAL", 30, Decimal("0.9000"),
                 "Cliente y proveedor", {"requires_all_dimensions": ["cuenta_cliente", "cuenta_proveedor"]}),
        RuleSeed("role_gl_account", CONCEPT_ROLE, "CUENTA_CONTABLE", 40, Decimal("0.9000"),
                 "Rol de cuenta contable", {"requires_dimension": "account_display_value", "excludes_commercial": True}),
        RuleSeed("role_bank_accounts", CONCEPT_ROLE, "BANCO", 50, Decimal("0.8800"),
                 "Cuentas de tesorería", {"account_keywords": list({"BANCO", "BANCARIA", "CAJA", "INVERSION"})}),
        RuleSeed("role_payroll", CONCEPT_ROLE, "EMPLEADO", 60, Decimal("0.8500"),
                 "Cuentas de nómina", {"account_keywords": list({"NOMINA", "SUELDO", "SALARIO"})}),
        RuleSeed("role_government", CONCEPT_ROLE, "GOBIERNO", 70, Decimal("0.8700"),
                 "Cuentas gubernamentales/fiscales", {"account_keywords": list({"SAT", "IMSS", "IVA", "ISR", "HACIENDA"})}),
        RuleSeed("role_cost_center", CONCEPT_ROLE, "CENTRO_COSTO", 80, Decimal("0.8000"),
                 "Centro de costo", {"account_keywords": list({"CENTRO", "DEPARTAMENTO"})}),
        # Nature rules — from top_accounts prefix
        RuleSeed("nature_asset_prefix", CONCEPT_NATURE, "ACTIVO", 10, Decimal("0.9000"),
                 "Mayoría cuentas 1xx", {"account_prefix": "1", "min_share": 0.5}),
        RuleSeed("nature_liability_prefix", CONCEPT_NATURE, "PASIVO", 20, Decimal("0.9000"),
                 "Mayoría cuentas 2xx", {"account_prefix": "2", "min_share": 0.5}),
        RuleSeed("nature_capital_prefix", CONCEPT_NATURE, "CAPITAL", 30, Decimal("0.9000"),
                 "Mayoría cuentas 3xx", {"account_prefix": "3", "min_share": 0.5}),
        RuleSeed("nature_income_prefix", CONCEPT_NATURE, "INGRESO", 40, Decimal("0.9000"),
                 "Mayoría cuentas 4xx", {"account_prefix": "4", "min_share": 0.5}),
        RuleSeed("nature_expense_prefix", CONCEPT_NATURE, "GASTO", 50, Decimal("0.9000"),
                 "Mayoría cuentas 5xx", {"account_prefix": "5", "min_share": 0.5}),
        RuleSeed("nature_cost_prefix", CONCEPT_NATURE, "COSTO", 60, Decimal("0.9000"),
                 "Mayoría cuentas 6xx", {"account_prefix": "6", "min_share": 0.5}),
        RuleSeed("nature_tax_accounts", CONCEPT_NATURE, "IMPUESTO", 70, Decimal("0.8800"),
                 "Cuentas fiscales", {"account_keywords": list({"IVA", "ISR", "IMPUESTO", "RETENCION"})}),
        RuleSeed("nature_adjustment_prefix", CONCEPT_NATURE, "AJUSTE", 80, Decimal("0.8500"),
                 "Cuentas 8xx/9xx", {"account_prefix_any": ["8", "9"], "min_share": 0.3}),
        # Behavior rules — profile metrics
        RuleSeed("behavior_purchase", CONCEPT_BEHAVIOR, "COMPRA", 10, Decimal("0.8800"),
                 "Proveedor con débito dominante", {"requires_dimension": "cuenta_proveedor", "debit_ratio_min": 1.2}),
        RuleSeed("behavior_sale", CONCEPT_BEHAVIOR, "VENTA", 20, Decimal("0.8800"),
                 "Cliente con crédito dominante", {"requires_dimension": "cuenta_cliente", "credit_ratio_min": 1.2}),
        RuleSeed("behavior_collection", CONCEPT_BEHAVIOR, "COBRO", 30, Decimal("0.8500"),
                 "Cliente con crédito > débito", {"requires_dimension": "cuenta_cliente", "credit_exceeds_debit": True}),
        RuleSeed("behavior_payment", CONCEPT_BEHAVIOR, "PAGO", 40, Decimal("0.8500"),
                 "Proveedor con débito > crédito", {"requires_dimension": "cuenta_proveedor", "debit_exceeds_credit": True}),
        RuleSeed("behavior_transfer", CONCEPT_BEHAVIOR, "TRANSFERENCIA", 50, Decimal("0.8200"),
                 "Sin contrapartes comerciales", {"max_counterparties": 0, "min_movements": 1}),
        RuleSeed("behavior_payroll", CONCEPT_BEHAVIOR, "NOMINA", 60, Decimal("0.8700"),
                 "Cuentas de nómina en movimientos", {"account_keywords": list({"NOMINA", "SUELDO", "SALARIO"})}),
        RuleSeed("behavior_tax", CONCEPT_BEHAVIOR, "IMPUESTO", 70, Decimal("0.8700"),
                 "Movimientos fiscales", {"account_keywords": list({"IVA", "ISR", "IMPUESTO"})}),
        RuleSeed("behavior_inventory", CONCEPT_BEHAVIOR, "INVENTARIO", 80, Decimal("0.8500"),
                 "Cuentas de inventario", {"account_keywords": list({"INVENTARIO", "ALMACEN", "EXISTENCIA"})}),
        RuleSeed("behavior_production", CONCEPT_BEHAVIOR, "PRODUCCION", 90, Decimal("0.8400"),
                 "Producción / WIP", {"account_keywords": list({"PRODUCCION", "WIP", "ORDEN"})}),
        RuleSeed("behavior_financial", CONCEPT_BEHAVIOR, "FINANCIERO", 100, Decimal("0.8600"),
                 "Tesorería / bancos", {"account_keywords": list({"BANCO", "INTERES", "FINANCIAMIENTO"})}),
        RuleSeed("behavior_administrative", CONCEPT_BEHAVIOR, "ADMINISTRATIVO", 110, Decimal("0.8000"),
                 "Gastos admin recurrentes", {"account_prefix": "5", "min_active_months": 3}),
        RuleSeed("behavior_mixed", CONCEPT_BEHAVIOR, "MIXTO", 120, Decimal("0.7500"),
                 "Dual comercial con actividad balanceada", {"requires_all_dimensions": ["cuenta_cliente", "cuenta_proveedor"], "balanced_debit_credit": True}),
    )
