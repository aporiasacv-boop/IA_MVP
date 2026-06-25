CONCEPT_IDENTITY = "identity"
CONCEPT_ROLE = "role"
CONCEPT_NATURE = "nature"
CONCEPT_BEHAVIOR = "behavior"

CONCEPT_CATEGORIES = frozenset({CONCEPT_IDENTITY, CONCEPT_ROLE, CONCEPT_NATURE, CONCEPT_BEHAVIOR})

STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

MIN_SUGGESTION_SCORE = 0.55

# Cuentas contables mexicanas — prefijos para naturaleza
NATURE_ACCOUNT_PREFIXES: dict[str, tuple[str, ...]] = {
    "ACTIVO": ("1",),
    "PASIVO": ("2",),
    "CAPITAL": ("3",),
    "INGRESO": ("4",),
    "GASTO": ("5",),
    "COSTO": ("6",),
    "IMPUESTO": ("11", "21", "54", "55"),
    "PATRIMONIO": ("31", "32"),
    "AJUSTE": ("8", "9"),
}

# Palabras clave en nombre de cuenta para rol (evidencia secundaria, no primaria)
BANK_ACCOUNT_KEYWORDS = frozenset({"BANCO", "BANCARIA", "BANCARIO", "CAJA", "INVERSION"})
EMPLOYEE_ACCOUNT_KEYWORDS = frozenset({"NOMINA", "SUELDO", "SALARIO", "EMPLEADO"})
GOVERNMENT_ACCOUNT_KEYWORDS = frozenset({"SAT", "IMSS", "INFONAVIT", "HACIENDA", "IMPUESTO", "IVA", "ISR"})
COST_CENTER_KEYWORDS = frozenset({"CENTRO", "DEPARTAMENTO", "CC-"})

COMMERCIAL_DIMENSIONS = frozenset({"cuenta_cliente", "cuenta_proveedor"})
GL_DIMENSION = "account_display_value"
