from app.query_engine.query_types import BusinessQueryType
from app.slot_clarification.slots import ClarificationSlot

REQUIRED_SLOTS_BY_QUERY_TYPE: dict[BusinessQueryType, tuple[ClarificationSlot, ...]] = {
    BusinessQueryType.MAX_TRANSACCION_CLIENTE: (ClarificationSlot.CLIENTE_CODIGO,),
    BusinessQueryType.MAX_PROVEEDOR_MES: (ClarificationSlot.MES,),
    BusinessQueryType.LOOKUP_CLIENTE_BY_CUENTA: (ClarificationSlot.CUENTA_CODIGO,),
}

FILTER_KEY_BY_SLOT: dict[ClarificationSlot, str] = {
    ClarificationSlot.CLIENTE_CODIGO: "cliente_codigo",
    ClarificationSlot.PROVEEDOR_CODIGO: "proveedor_codigo",
    ClarificationSlot.CUENTA_CODIGO: "cuenta_codigo",
    ClarificationSlot.MES: "mes",
    ClarificationSlot.ANIO: "anio",
}
