from app.slot_clarification.slots import ClarificationSlot

SLOT_CLARIFICATION_TEMPLATES: dict[ClarificationSlot, str] = {
    ClarificationSlot.CLIENTE_CODIGO: (
        "¿De qué cliente deseas consultar la información?"
    ),
    ClarificationSlot.MES: "¿De qué mes deseas realizar la consulta?",
    ClarificationSlot.CUENTA_CODIGO: "¿Cuál es el código de cuenta?",
    ClarificationSlot.PROVEEDOR_CODIGO: (
        "¿De qué proveedor deseas consultar la información?"
    ),
    ClarificationSlot.ANIO: "¿De qué año deseas realizar la consulta?",
}
