from app.domain.entities import BusinessEntity
from app.domain.operations import BusinessOperation


class TargetEntityResolver:
    """Reglas v1 para determinar target_entity y source_entity."""

    def resolve(
        self,
        operation: BusinessOperation | None,
        entities: list[BusinessEntity],
    ) -> tuple[BusinessEntity | None, BusinessEntity | None]:
        if not entities:
            return None, None

        entity_set = set(entities)

        # Regla 1: COUNT + CLIENTE -> target = CLIENTE
        if operation == BusinessOperation.COUNT and BusinessEntity.CLIENTE in entity_set:
            return BusinessEntity.CLIENTE, None

        # Regla 2: COUNT + PROVEEDOR -> target = PROVEEDOR
        if operation == BusinessOperation.COUNT and BusinessEntity.PROVEEDOR in entity_set:
            return BusinessEntity.PROVEEDOR, None

        # Regla 3: MAX + TRANSACCION -> target = TRANSACCION; source = CLIENTE si existe
        if operation == BusinessOperation.MAX and BusinessEntity.TRANSACCION in entity_set:
            source = (
                BusinessEntity.CLIENTE
                if BusinessEntity.CLIENTE in entity_set
                else None
            )
            return BusinessEntity.TRANSACCION, source

        # Regla 4: MAX + PROVEEDOR -> target = PROVEEDOR
        if operation == BusinessOperation.MAX and BusinessEntity.PROVEEDOR in entity_set:
            return BusinessEntity.PROVEEDOR, None

        # Regla 5: LOOKUP + CLIENTE + CUENTA -> target = CLIENTE, source = CUENTA
        if (
            operation == BusinessOperation.LOOKUP
            and BusinessEntity.CLIENTE in entity_set
            and BusinessEntity.CUENTA in entity_set
        ):
            return BusinessEntity.CLIENTE, BusinessEntity.CUENTA

        # Regla 6: LOOKUP + PROVEEDOR + CUENTA -> target = PROVEEDOR, source = CUENTA
        if (
            operation == BusinessOperation.LOOKUP
            and BusinessEntity.PROVEEDOR in entity_set
            and BusinessEntity.CUENTA in entity_set
        ):
            return BusinessEntity.PROVEEDOR, BusinessEntity.CUENTA

        # Regla 7: Fallback — primera entidad detectada como target
        return entities[0], None
